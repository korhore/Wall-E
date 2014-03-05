'''
Created on Feb 24, 2013
Updated on Feb 3, 2014

@author: reijo
'''

import SocketServer
from Sensation import Sensation
from Romeo import Romeo
from ManualRomeo import ManualRomeo
from Hearing import Hearing
from threading import Thread
import signal
import sys
import getopt
import socket
from Queue import Queue
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
    
    sensation_queue = Queue()       # global queue for senses to put sensations

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
 
        # starting build in capabilities/senses
        # we have capability to move
        if MANUAL:
            self.romeo = ManualRomeo()
        else:
            self.romeo = Romeo()
        # we have hearing (positioning of object using sounds)
        self.hearing=Hearing(WalleServer.sensation_queue)
        
        # starting tcp server as nerve pathway to external senses to connect
        # we have azimuth sense (our own position detection)
        self.tcpServer=WalleTCPServer(WalleServer.sensation_queue, (HOST,PORT))
        
        self.running=False



    def run(self):
        print "Starting " + self.name
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.hearing.start()
        print "WalleServer: starting WalleTCPServer"
        self.tcpServer.start()

        while self.running:
            sensation=WalleServer.sensation_queue.get()
            print "WalleServer: got sensation from queue " + str(sensation)
            self.process(sensation)

        self.tcpServer.stop()
        self.hearing.stop()

    def stop():
        self.running = False
            
            
    def process(self, sensation):
        print "WalleServer.process: " + time.ctime(sensation.getTime()) + ' ' + str(sensation)
        if sensation.getSensationType() == Sensation.SensationTypes.Drive:
            print "Walleserver.process Sensation.SensationTypes.Drive"
        elif sensation.getSensationType() == Sensation.SensationTypes.Stop:
            print "Walleserver.process Sensation.SensationTypes.Stop"
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationTypes.Who:
            print "Walleserver.process Sensation.SensationTypes.Who"
        elif sensation.getSensationType() == Sensation.SensationTypes.Hear:
            print "Walleserver.process Sensation.SensationTypes.Hear"
            self.hearing_angle = sensation.getHear()
            self.turn_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
            self.turning_to_object = True
            self.turn()
        elif sensation.getSensationType() == Sensation.SensationTypes.Azimuth:
            print "Walleserver.process Sensation.SensationTypes.Azimuth"
            self.azimuth = sensation.getAzimuth()
            self.turn()
        elif sensation.getSensationType() == Sensation.SensationTypes.Picture:
            print "Walleserver.process Sensation.SensationTypes.Picture"
        elif sensation.getSensationType() == Sensation.SensationTypes.Capability:
            print "Walleserver.process Sensation.SensationTypes.Capability"
        elif sensation.getSensationType() == Sensation.SensationTypes.Unknown:
            print "Walleserver.process Sensation.SensationTypes.Unknown"
  
    def turn(self):
        if self.turning_to_object:
            print "WalleServer.turn: self.hearing_angle " + str(self.hearing_angle) + " self.azimuth " + str(self.azimuth)
            print "WalleServer.turn: turn to " + str(self.turn_angle)
            self.leftPower, self.rightPower = self.getPower()
            if math.fabs(self.leftPower) < Romeo.MINPOWER or math.fabs(self.rightPower) < Romeo.MINPOWER:
                self.leftPower = 0.0           # set motors in opposite power to turn in place
                self.rightPower = 0.0
                print "WalleServer.turn: Turn is ended"
                self.turning_to_object = False
            
            print "WalleServer.turn: powers to " + str(self.leftPower) + ' ' + str(self.rightPower)
            
            self.number = self.number + 1
            #test=Sensation.SensationTypes.Drive
            sensation, picture = self.romeo.processSensation(Sensation(number=self.number, sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
            self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
            self.rightPower = sensation.getRightPower()
            print "WalleServer.turn: powers set to " + str(self.leftPower) + ' ' + str(self.rightPower)
          

    def add_radian(self, original_radian, added_radian):
        result = original_radian + added_radian
        if (result > math.pi):
            return -math.pi + (result - math.pi)
        if (result < -math.pi):
            return math.pi - (result - math.pi)
        return result


    def getPower(self):
        leftPower = 0.0           # set motorn in opposite pover to turn in place
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
        
        
class WalleTCPServer(Thread): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pause = 0.25
    allow_reuse_address = True
    
    # inhered
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    #allow_reuse_address = False


    def __init__(self, queue, server_address):
        Thread.__init__(self)
        self.name = "WalleTCPServer"
        self.queue = queue
        self.server_address = server_address
        print "WalleTCPServer: creating socket"
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
#        self.socket.settimeout(self.pause)
        self.socket.setblocking(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketServers = []
        self.running=False
       
    def run(self):
        print "Starting " + self.name
        
        # starting other threads/senders/capabilities
        
        self.running=True
#        if self.allow_reuse_address:
#            self.socket.setsockopt(socket.SOL_TCP, socket.SO_REUSEADDR, 1)
#            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          
        print self.name + "; bind " + str(self.server_address)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()
        self.socket.listen(self.request_queue_size)
 
        while self.running:
            print self.name + ": waiting self.socket.accept()"
            socket, address = self.socket.accept()
            print self.name + ": self.socket.accept() " + str(address)
            socketServer = self.createWalleSocketServer(queue=self.queue, socket=socket, address=address)
            socketServer.start()

    def stop():
        self.running = False
        
    def createWalleSocketServer(self, queue, socket, address):
        socketServer =  None
        for socketServerCandidate in self.socketServers:
            if not socketServerCandidate.running:
                socketServer = socketServerCandidate
                print self.name + ":createWalleSocketServer: found WalleSocketServer not running"
                socketServer.__init__(queue, socket, address)
                break
        if not socketServer:
            print self.name + ":createWalleSocketServer: creating new WalleSocketServer"
            socketServer = WalleSocketServer(queue, socket, address)
            self.socketServers.append(socketServer)
        return socketServer



class WalleSocketServer(Thread): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):


    def __init__(self, queue, socket, address):
        Thread.__init__(self)
        self.queue=queue
        self.socket=socket
        self.address=address
        self.name = str(address)
        self.running=False
       
    def run(self):
        print "Starting " + self.name
        
        # starting other threads/senders/capabilities
        
        self.running=True
 
        while self.running:
            self.data = self.socket.recv(1024).strip()
            print "WalleSocketServer Client " + str(self.address) + " wrote " + self.data
            if len(self.data) == 0:
                self.running = False
            else:
                strings=self.data.split('|')
                for string in strings:
                    print "WalleSocketServer string " + string
                    if len(string) > 0:
                        sensation=Sensation(string)
                        print sensation
                        self.queue.put(sensation)

        self.socket.close()

    def stop():
        self.running = False


class WalleRequestHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    

    def handle(self):
        print "WalleRequestHandler.handle"
        # self.request is the TCP socket connected to the client
        print "WalleRequestHandler.handle lf.request.recv(1024).strip()"
        self.data = self.request.recv(1024).strip()
        #print "{} wrote:".format(self.client_address[0])
        print "WalleRequestHandler.handle Client wrote " + self.data
        # just send back the same data, but upper-cased
        print "WalleRequestHandler.handle self.request.sendall(self.data.upper())"
        strings=self.data.split('|')
        for string in strings:
            print "WalleRequestHandler.handle string " + string
            if len(string) > 0:
                sensation=Sensation(string)
                print sensation
                if sensation.getSensationType() == Sensation.SensationTypes.Stop:
                    self.request.sendall(str(sensation))
                    print "WalleRequestHandler.handle sensation " + str(sensation) + " Shutdown"
                    if not WalleRequestHandler.romeo is None:
                        print "_WalleRequestHandler.handle del WalleRequestHandler.romeo"
                        del WalleRequestHandler.romeo
                        WalleRequestHandler.romeo = None
                        
                    print "WalleRequestHandler.handle sensation pictureServer.shutdown()"
                    WalleRequestHandler.pictureServer.serving =False
                    
                    print "WalleRequestHandler.handle sensation " + str(sensation) + " server.shutdown()"
                    WalleRequestHandler.server.serving =False
                else:
                    sensation, imageData = self.processSensation(sensation)
                    
                    self.request.sendall(str(sensation))
                    print "WalleRequestHandler.handle sensation " + str(sensation)
                    if sensation.getSensationType() == Sensation.SensationTypes.Picture:
                        self.request.sendall(imageData)
                    print "WalleRequestHandler.handle sensation imagedata " + str(len(imageData))
           
    def processSensation(self, sensation):
        if sensation.getSensationType() == Sensation.SensationTypes.Picture:
            print "WalleSocketServer.processSensation Sensation.SensationTypes.Picture"
            # take a picture
            call(["raspistill", "-vf", "-ex", "night", "-o", "/tmp/image.jpg"])
            f = open("/tmp/image.jpg", 'r')
            imageData=f.read()
            sensation.setImageSize(len(imageData))
            return sensation, imageData
        else:
            if not WalleRequestHandler.romeo == None:
                return WalleRequestHandler.romeo.processSensation(sensation)
            else:
                return sensation, ""
           
        
#    def handle(self):
#        # self.rfile is a file-like object created by the handler;
#        # we can now use e.g. readline() instead of raw recv() calls
#        self.data = self.rfile.readline().strip()
#        print "{} wrote:".format(self.client_address[0])
#        print self.data
#        # Likewise, self.wfile is a file-like object used to write back
#        # to the client
#        self.wfile.write(self.data.upper())

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

# TODO remove # after test
#    print "do_server: create romeo"
#    try:
#        WalleRequestHandler.romeo = Romeo()
#    except AttributeError:
#        print "do_server: Romeo error, only tests wuthout it are possible"
#        WalleRequestHandler.romeo = None
 
    #romeo.test2()

    print "do_server: create WalleServer"
    walle = WalleServer()
    #server = WalleSocketServer((HOST, PORT), WalleRequestHandler)
    #WalleRequestHandler.server = server

    succeeded=True
    try:
        walle.start()
        
#        # TODO
#        
#        # Create the server, binding to localhost on port 2000
#        print "do_server: create SocketServer.TCPServer "
#        print "do_server: create SocketServer.TCPServer " + HOST + " " + str(PORT)
#        #server = SocketServer.TCPServer((HOST, PORT), WalleRequestHandler)
#        server = WalleSocketServer((HOST, PORT), WalleRequestHandler)
#        WalleRequestHandler.server = server
        
#        print "do_server: create SocketServer.TCPServer " + HOST + " " + str(PICTURE_PORT)
#        #pictureServer = SocketServer.TCPServer((HOST, PICTURE_PORT), WalleRequestHandler)
#        pictureServer = WalleSocketServer((HOST, PICTURE_PORT), WalleRequestHandler)
#        WalleRequestHandler.pictureServer = pictureServer
#
    except Exception: 
        print "do_server: socket error, exiting"
        succeeded=False
   # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    #threaded_server(pictureServer)
    #threaded_server(server)
    if succeeded:
        print 'do_server: Press Ctrl+C to Stop'
        
        walle.join()
        
 #       print 'do_server: Creating serverThread'
 #       serverThread = Thread(target = threaded_server, args = (server, ))
 #       print 'do_server: Starting  serverThread'
 #       serverThread.start()
        
  #      print 'do_server: Creating pictureServerThread'
  #      pictureServerThread = Thread(target = threaded_server, args = (pictureServer, ))
 #       print 'do_server: Starting  pictureServerThread'
 #       pictureServerThread.start()
          
 #       print 'do_server: Waiting pictureServerThread to stop'
 #       pictureServerThread.join()
#
#        print 'do_server: Waiting serverThread to stop'
#        serverThread.join()
        
        print 'do_server: Servers stoppped OK'
    
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
        received = sock.recv(1024)
        print 'stop: received answer ' + received
    except Exception: 
        print "stop: connect error"
    finally:
        print 'stop: sock.close()'
        sock.close()
    print "stop: end"

 
def main():
    signal.signal(signal.SIGINT, signal_handler)
     

    WalleRequestHandler.romeo = None    # no romeo device connection yet
#    print "main: create romeo"
#    romeo = Romeo()
    #romeo.test2()

    #HOST, PORT = "localhost", 2000

    # Create the server, binding to localhost on port 2000
    print "main: create SocketServer.TCPServer " + HOST + " " + str(PORT)
    server = SocketServer.TCPServer((HOST, PORT), WalleRequestHandler)
    
    print "main: create SocketServer.TCPServer " + HOST + " " + str(PICTURE_PORT)
    pictureServer = SocketServer.TCPServer((HOST, PICTURE_PORT), WalleRequestHandler)

 
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    #threaded_server(pictureServer)
    #threaded_server(server)
    
    print 'main: Press Ctrl+C to Stop'
    
    print 'main: Creating serverThread'
    serverThread = Thread(target = threaded_server, args = (server, ))
    print 'main: Starting  serverThread'
    serverThread.start()
    
    print 'main: Creating pictureServerThread'
    pictureServerThread = Thread(target = threaded_server, args = (pictureServer, ))
    print 'main: Starting  pictureServerThread'
    pictureServerThread.start()
    
    print 'main: Waiting serverThread to stop'
    serverThread.join()
    print 'main: Waiting pictureServerThread to stop'
    pictureServerThread.join()
    
    print 'main: Servers stoppped OK'
    
    sys.exit(0)



if __name__ == "__main__":
    WalleRequestHandler.romeo = None    # no romeo device connection yet

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
#        if DAEMON:
#            print "daemon.__file__ " +  daemon.__file__
#            stdout=open('/tmp/Wall-E_Server.stdout', 'w+')
#            stderr=open('/tmp/Wall-E_Server.stderr', 'w+')
#            #remove('/var/run/Wall-E_Server.pid.lock')
#            pidfile=lockfile.FileLock('/var/run/Wall-E_Server.pid')
#            with daemon.DaemonContext(stdout=stdout,
#                                      stderr=stderr,
#                                      pidfile=pidfile):
#                do_server()
#        else:
#           do_server()
    
    # if romeo device connection, then delete it as last thing
    if not WalleRequestHandler.romeo is None:
        print "_main__ del WalleRequestHandler.romeo"
        del WalleRequestHandler.romeo
        WalleRequestHandler.romeo = None
    print "__main__ exit"
    exit()



