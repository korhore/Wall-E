'''
Created on Feb 24, 2013
Updated on Mar 8, 2014

@author: reijo
'''

import SocketServer
from Axon import Axon
from TCPServer import TCPServer
from SocketServer import SocketServer
from Sensation import Sensation
from Romeo import Romeo
from ManualRomeo import ManualRomeo
from Hearing import Hearing
from threading import Thread
from threading import Timer
import signal
import sys
import getopt
import socket
import math
import time



import daemon
import lockfile



HOST = '0.0.0.0'
PORT = 2000
PICTURE_PORT = 2001

DAEMON=False
START=False
STOP=False
MANUAL=False

class WalleServer(Thread):
    """
    Controls Walle-robot. Walle has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Walle emulates senses (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (tecnically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Integraterd sensation are transferred in Queue, which is thread safe. Every SEnse runs in its own thread as real senses, independently.
    External Senses are handled using sockets.
    """
    
    TURN_ACCURACYFACTOR = math.pi * 10.0/180.0
    FULL_TURN_FACTOR = math.pi * 45.0/180.0
    

    def __init__(self):
        Thread.__init__(self)
        self.name = "WalleServer"
       
        self.azimuth=0.0                # position sense, azimuth from north
        self.turning_to_object = False  # Are we turning to see an object
        self.hearing_angle = 0.0        # device hears sound from this angle, device looks to its front
                                        # to the azimuth direction
        self.turn_angle = 0.0           # turn until azimuth is this angle
        
        self.leftPower = 0.0            # moving
        self.rightPower = 0.0
        
        self.number = 0
        self.in_axon = Axon()       # global queue for senses to put sensations
        self.out_axon = Axon()      # global queue for senses to put sensations

        # starting build in capabilities/senses
        # we have capability to move
        if MANUAL:
            self.romeo = ManualRomeo()
        else:
            self.romeo = Romeo()
        # we have hearing (positioning of object using sounds)
        self.hearing=Hearing(self.in_axon)
        
        # starting tcp server as nerve pathway to external senses to connect
        # we have azimuth sense (our own position detection)
        self.tcpServer=TCPServer(out_axon = self.in_axon, in_axon = self.out_axon, server_address=(HOST,PORT))

        
        self.running=False
        self.turnTimer = Timer(10.0, self.stopTurn)



    def run(self):
        print "Starting " + self.name
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.hearing.start()
        print "WalleServer: starting TCPServer"
        self.tcpServer.start()

        while self.running:
            sensation=self.in_axon.get()
            print "WalleServer: got sensation from queue " + str(sensation)
            self.process(sensation)
            # as a test, echo everything to external device
            self.out_axon.put(sensation)

        self.tcpServer.stop()
        self.hearing.stop()

    def stop(self):
        self.running = False
            
            
    def process(self, sensation):
        print "WalleServer.process: " + time.ctime(sensation.getTime()) + ' ' + str(sensation)
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            print "Walleserver.process Sensation.SensationType.Drive"
        elif sensation.getSensationType() == Sensation.SensationType.Stop:
            print "Walleserver.process Sensation.SensationType.Stop"
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Who:
            print "Walleserver.process Sensation.SensationType.Who"
        elif sensation.getSensationType() == Sensation.SensationType.HearDirection:
            print "Walleserver.process Sensation.SensationType.HearDirection"
            self.hearing_angle = sensation.getHearDirection()
            self.turn_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
            self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
            print "Walleserver.process Sensation.SensationType.Azimuth"
            self.azimuth = sensation.getAzimuth()
            self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Picture:
            print "Walleserver.process Sensation.SensationType.Picture"
        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            print "Walleserver.process Sensation.SensationType.Capability"
        elif sensation.getSensationType() == Sensation.SensationType.Unknown:
            print "Walleserver.process Sensation.SensationType.Unknown"
  
    def turn(self):
        # calculate new power to turn or continue turning
        self.leftPower, self.rightPower = self.getPower()
        if self.turning_to_object:
            print "WalleServer.turn: self.hearing_angle " + str(self.hearing_angle) + " self.azimuth " + str(self.azimuth)
            print "WalleServer.turn: turn to " + str(self.turn_angle)
            if math.fabs(self.leftPower) < Romeo.MINPOWER or math.fabs(self.rightPower) < Romeo.MINPOWER:
                self.leftPower = 0.0           # set motors in opposite power to turn in place
                self.rightPower = 0.0
                print "WalleServer.turn: Turn is ended"
                self.turning_to_object = False
                self.turnTimer.cancel()
            else:
                print "WalleServer.turn: powers adjusted to " + str(self.leftPower) + ' ' + str(self.rightPower)
                self.number = self.number + 1
                sensation, picture = self.romeo.processSensation(Sensation(number=self.number, sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
                self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
                self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
                
        else:
            if math.fabs(self.leftPower) >= Romeo.MINPOWER or math.fabs(self.rightPower) >= Romeo.MINPOWER:
                self.turning_to_object = True
                # adjust hearing
                # if turn, don't hear sound, because we are giving moving sound
                # we want hear only sounds from other objects
                self.hearing.setOn(not self.turning_to_object)
                print "WalleServer.turn: powers initial to " + str(self.leftPower) + ' ' + str(self.rightPower)
                self.number = self.number + 1
                sensation, picture = self.romeo.processSensation(Sensation(number=self.number, sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
                self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
                self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
                self.turnTimer = Timer(10.0, self.stopTurn)
                self.turnTimer.start()

            
    def stopTurn(self):
        self.turning_to_object = False
        self.leftPower = 0.0           # set motors in opposite power to turn in place
        self.rightPower = 0.0
        print "WalleServer.stopTurn: Turn is cancelled"
            
        print "WalleServer.stopTurn: powers to " + str(self.leftPower) + ' ' + str(self.rightPower)
            
        self.hearing.setOn(not self.turning_to_object)
            
        self.number = self.number + 1
        #test=Sensation.SensationType.Drive
        sensation, picture = self.romeo.processSensation(Sensation(number=self.number, sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
        self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
        self.rightPower = sensation.getRightPower()
        print "WalleServer.stopTurn: powers set to " + str(self.leftPower) + ' ' + str(self.rightPower)

          

    def add_radian(self, original_radian, added_radian):
        result = original_radian + added_radian
        if (result > math.pi):
            return -math.pi + (result - math.pi)
        if (result < -math.pi):
            return math.pi - (result - math.pi)
        return result


    def getPower(self):
        leftPower = 0.0           # set motor in opposite power to turn in place
        rightPower = 0.0
        
        if math.fabs(self.turn_angle - self.azimuth) > WalleServer.TURN_ACCURACYFACTOR:
            power = (self.turn_angle - self.azimuth)/WalleServer.FULL_TURN_FACTOR
            if power > 1.0:
                power = 1.0
            if power < -1.0:
                power = -1.0
            if math.fabs(power) < Romeo.MINPOWER:
                power = 0.0
            leftPower = power           # set motorn in opposite pover to turn in place
            rightPower = -power
        if math.fabs(leftPower) < Romeo.MINPOWER or math.fabs(rightPower) < Romeo.MINPOWER:
            leftPower = 0.0           # set motors in opposite power to turn in place
            rightPower = 0.0
 
        # test system has so little power, that we must run it at full speed           
 #       if leftPower > Romeo.MINPOWER:
 #           leftPower = 1.0           # set motorn in opposite pover to turn in place
 #           rightPower = -1.0
 #       elif leftPower < -Romeo.MINPOWER:
 #           leftPower = -1.0           # set motorn in opposite pover to turn in place
 #           rightPower = 1.0
            
            
        return leftPower, rightPower
        
        



def threaded_server(arg):
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "threaded_server: starting server"
    arg.serve_forever()
    print "threaded_server: arg.serve_forever() ended"

def signal_handler(signal, frame):
    print 'signal_handler: You pressed Ctrl+C!'
    
    print 'signal_handler: Shutting down sensation server ...'
    WalleRequestHandler.server.serving =False
    print 'signal_handler: sensation server is down OK'
    
    print 'signal_handler: Shutting down picture server...'
    WalleRequestHandler.pictureServer.serving =False
    print 'signal_handler: picture server is down OK'

  

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    print "do_server: create WalleServer"
    walle = WalleServer()
    #server = WalleSocketServer((HOST, PORT), WalleRequestHandler)
    #WalleRequestHandler.server = server

    succeeded=True
    try:
        walle.start()
        
    except Exception: 
        print "do_server: socket error, exiting"
        succeeded=False

    if succeeded:
        print 'do_server: Press Ctrl+C to Stop'
        
        walle.join()
        
    print "do_server exit"
    
def start(is_daemon):
        if is_daemon:
            print "start: daemon.__file__ " +  daemon.__file__
            stdout=open('/tmp/Wall-E_Server.stdout', 'w+')
            stderr=open('/tmp/Wall-E_Server.stderr', 'w+')
            #remove('/var/run/Wall-E_Server.pid.lock')
            pidfile=lockfile.FileLock('/var/run/Wall-E_Server.pid')
            with daemon.DaemonContext(stdout=stdout,
                                      stderr=stderr,
                                      pidfile=pidfile):
                do_server()
        else:
           do_server()

    
def stop():
    
    print "stop: socket.socket(socket.AF_INET, socket.SOCK_STREAM)"
    # Create a socket (SOCK_STREAM means a TCP socket)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception: 
        print "stop: socket error"

    
    try:
        # Connect to server and send data
        print 'stop: sock.connect((localhost, PORT))'
        sock.connect(('localhost', PORT))
        print "stop: sock.sendall STOP sensation"
        sock.sendall(str(Sensation(sensationType = 'S')))
    
        # Receive data from the server
        print "stop: sock.recv(1024)"
        received = sock.recv(1024)
        print 'stop: received answer ' + received
    except Exception: 
        print "stop: connect error"
    finally:
        print 'stop: sock.close()'
        sock.close()
    print "stop: end"

 


if __name__ == "__main__":
    #WalleRequestHandler.romeo = None    # no romeo device connection yet

    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)
    try:
        opts, args = getopt.getopt(sys.argv[1:],"",["start","stop","restart","daemon","manual"])
    except getopt.GetoptError:
      print sys.argv[0] + '[--start] [--stop] [--restart] [--daemon] [--manual]'
      sys.exit(2)
    print 'opts '+ str(opts)
    for opt, arg in opts:
        print 'opt '+ opt
        if opt == '--start':
            print sys.argv[0] + ' start'
            START=True
        elif opt == '--stop':
            print sys.argv[0] + ' stop'
            STOP=True
        elif opt == '--restart':
            print sys.argv[0] + ' restart'
            STOP=True
            START=True
        elif opt == '--daemon':
            print sys.argv[0] + ' daemon'
            DAEMON=True
        elif opt == '--manual':
            print sys.argv[0] + ' manual'
            MANUAL=True
           
    if not START and not STOP:
        START=True
    
    if (STOP):
        stop()
    if (START): 
        start(DAEMON)   
             
    print "__main__ exit"
    exit()



