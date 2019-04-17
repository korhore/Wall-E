'''
Created on Feb 24, 2013
Updated on Mar 8, 2014

@author: reijo
'''

import os
import sys
import signal
import getopt
from threading import Thread
from threading import Timer
import socket
import math
import time
import configparser

import daemon
import lockfile

from Axon import Axon
from TCPServer import TCPServer
from SocketClient import SocketClient
from Sensation import Sensation
from Romeo import Romeo
from ManualRomeo import ManualRomeo
from dbus.mainloop.glib import threads_init
from xdg.IconTheme import theme_cache
if 'Hearing.Hear' not in sys.modules:
    from Hearing.Hear import Hear
#from Config import CONFIG_FILE_PATH
#if 'Config' not in sys.modules:
from Config import Config

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
    
    Walle emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.
    External Sensorys are handled using sockets.
    """
    
    TURN_ACCURACYFACTOR = math.pi * 10.0/180.0
    FULL_TURN_FACTOR = math.pi * 45.0/180.0
    
    DEFAULT_OBSERVATION_DISTANCE = 3.0
    
    ACTION_TIME=1.0

    # Configuratioon Section and Option names
    DEFAULT_SECTION="DEFAULT"
    DIRECTION_SECTIION="Direction"
    IN_SECTION="In"
    OUT_SECTION="Out"
    MEMORY_SECTION="Memory"
    SENSORY_SECTION="Sensory"
    WORKING_SECTION="Working"
    LONG_TERM_SECTION="LongTerm"
    DRIVE_CAPABILITY_OPTION="Drive"
    STOP_CAPABILITY_OPTION="Stop"
    TRUE_VALUE="True"
    FALSE_VALUE="False"
  

    def __init__(self):
        Thread.__init__(self)
        self.name = "WalleServer"
        
        Capabilities = 'Capabilities' 
        Memory =        'Memory'

       
        self.number=0
        self.azimuth=0.0                # position sense, azimuth from north
        self.turning_to_object = False  # Are we turning to see an object
        self.hearing_angle = 0.0        # device hears sound from this angle, device looks to its front
                                        # to the azimuth direction
        self.observation_angle = 0.0           # turn until azimuth is this angle
        
        self.leftPower = 0.0            # moving
        self.rightPower = 0.0
        
        self.number = 0
        self.in_axon = Axon()       # global queue for senses to put sensations to walle
        self.out_axon = Axon()      # global queue for walle to put sensations to external senses

        self.config = Config()

        # starting build in capabilities/senses
        # we have capability to move
        if self.config.canMove():
            if MANUAL:
                self.romeo = ManualRomeo()
            else:
                self.romeo = Romeo()
            # we have hearing (positioning of object using sounds)
        if self.config.canHear():
            self.hearing=Hear(self.in_axon)
        
        # starting tcp server as nerve pathway to external senses to connect
        # we have azimuth sense (our own position detection)
        self.tcpServer=TCPServer(out_axon = self.in_axon, in_axon = self.out_axon, server_address=(HOST,PORT))

        
        self.running=False
        self.turnTimer = Timer(WalleServer.ACTION_TIME, self.stopTurn)
        
        self.calibrating=False              # are we calibrating
        self.calibrating_angle = 0.0        # calibrate device hears sound from this angle, device looks to its front
        #self.calibratingTimer = Timer(WalleServer.ACTION_TIME, self.stopCalibrating)
        print ("WalleServer: Calibrate version")
        
        # finally remember instance
        WalleServer.walle = self
        
    '''
    Configuration look like this
    [DEFAULT]
        [Direction]
            [In]
                [Memory]
                    [Sensory]
                         Drive=False
                         Stop=False}
                    [Working]
                        Drive=False
                        Stop=False}
                    [LongTerm]
                        Drive=False
                        Stop=False}
            [Out]
                [Memory]
                    [Sensory]
                         Drive=False
                         Stop=False}
                    [Working]
                        Drive=False
                        Stop=False}
                    [LongTerm]
                        Drive=False
                        Stop=False}
 
    Make dicts with keys, values of Drextions, Memory, Capabilities
    so we get this kind one level section,
    Sections will be  hosts available, but will we need more than localhost,
    Other hosts can be got by Sensations.
    
    In_Sensory_Drive=False
    In_Sensory_Stop=False

    In_Working_Drive=False
    In_Working_Stop=False
   
    In_LongTerm_Drive=False
    In_LongTerm_Stop=False
    
    [Microphones]
    left = Set
    right = Set_1
    calibrating_zero = 0.131151809437
    calibrating_factor = 3.54444800648
    
    
    '''


    def configure(self):
        cwd = os.getcwd()
        print("cwd " + cwd)
#        self.config = configparser.RawConfigParser()
        self.config = configparser.ConfigParser()
        # read our capabilities about sensation
        try:
            config_file=open(CONFIG_FILE_PATH,"a+")
            self.config.read(config_file)
            
            if not self.config.has_section(WalleServer.DEFAULT_SECTION):
                self.createDefaultSection(config=self.config, config_file=config_file)
                
            left_card = self.config.get(WalleServer.Capabilities, WalleServer.Memory)
            
            left_card = self.config.get(Hear.Microphones, Hear.left)
            if left_card == None:
                print('left_card == None')
                self.canRun = False
            right_card = self.config.get(Hear.Microphones, Hear.right)
            if right_card == None:
                print('right_card == None')
                self.canRun = False
            try:
                self.calibrating_zero = self.config.getfloat(Hear.Microphones, Hear.calibrating_zero)
            except configparser.NoOptionError:
                self.calibrating_zero = 0.0
            try:
                self.calibrating_factor = self.config.getfloat(Hear.Microphones, Hear.calibrating_factor)
            except configparser.NoOptionError:
                self.calibrating_factor = 1.0
 
        # TODO make autoconfig here               
        except configparser.MissingSectionHeaderError as e:
                print('ConfigParser.MissingSectionHeaderError ' + str(e))
                self.canRun = False
        except configparser.NoSectionError as e:
                print('ConfigParser.NoSectionError ' + str(e))
                self.canRun = False
        except configparser.NoOptionError as e:
                print('ConfigParser.NoOptionError ' + str(e))
                self.canRun = False
        except Exception as e:
                print('ConfigParser exception ' + str(e))
                self.canRun = False

    def createDefaultSection(self, config, config_file):
        try:
            config.add_section(WalleServer.DEFAULT_SECTION)
            config.write(config_file)   
        except Exception as e:
                print('onfig.add_secction exception ' + str(e))
        
    def run(self):
        print ("Starting " + self.name)
        
        # starting other threads/senders/capabilities
        
        self.running=True
        if self.config.canHear():
            self.hearing.start()
        print ("WalleServer: starting TCPServer")
        self.tcpServer.start()

        while self.running:
            sensation=self.in_axon.get()
            print ("WalleServer: got sensation from queue " + str(sensation))
            self.process(sensation)
            # as a test, echo everything to external device
            #self.out_axon.put(sensation)
 
        print ('Walle:run shutting down ...')

        print ('Walle:run shutting down TcpServer ...')
        self.tcpServer.stop()
        
        if self.config.canHear():
            print ('Walle:run shutting down hearing ...')
            self.hearing.stop()
        
        print ('Walle:run ALL SHUT DOWN')


    def stop(self):
        self.running = False

    '''
    DoStop is used to stop server process and its sobprocesses (threads)
    Technique is just give Stop Sewnsation oto process.
    With same tecnique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        self.in_axon.put(Sensation(number=++self.number,
                                   sensationType = Sensation.SensationType.Stop))

            
            
    def process(self, sensation):
        print ("WalleServer.process: " + time.ctime(sensation.getTime()) + ' ' + str(sensation))
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            print ("Walleserver.process Sensation.SensationType.Drive")
        elif sensation.getSensationType() == Sensation.SensationType.Stop:
            print ("Walleserver.process Sensation.SensationType.Stop")
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Who:
            print ("Walleserver.process Sensation.SensationType.Who")
        elif self.config.canHear() and sensation.getSensationType() == Sensation.SensationType.HearDirection:
            print ("Walleserver.process Sensation.SensationType.HearDirection")
            #inform external senses that we remember now hearing          
            self.out_axon.put(sensation)
            self.hearing_angle = sensation.getHearDirection()
            if self.calibrating:
                print ("Walleserver.process Calibrating hearing_angle " + str(self.hearing_angle) + " calibrating_angle " + str(self.calibrating_angle))
            else:
                self.observation_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
                print ("Walleserver.process create Sensation.SensationType.Observation")
                self.in_axon.put(Sensation(number=++self.number,
                                           sensationType = Sensation.SensationType.Observation,
                                           observationDirection= self.observation_angle,
                                           observationDistance=WalleServer.DEFAULT_OBSERVATION_DISTANCE))
                # mark hearing sensation to be processed to set direction out of memory, we forget it
                sensation.setDirection(Sensation.Direction.Out)
                #inform external senses that we don't remember hearing any more           
                self.out_axon.put(sensation)
        elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
            if not self.calibrating:
                print ("Walleserver.process Sensation.SensationType.Azimuth")
                #inform external senses that we remember now azimuth          
                #self.out_axon.put(sensation)
                self.azimuth = sensation.getAzimuth()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Observation:
            if not self.calibrating:
                print ("Walleserver.process Sensation.SensationType.Observation")
                #inform external senses that we remember now observation          
                self.out_axon.put(sensation)
                self.observation_angle = sensation.getObservationDirection()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Picture:
            print ("Walleserver.process Sensation.SensationType.Picture")
        elif sensation.getSensationType() == Sensation.SensationType.Calibrate:
            print ("Walleserver.process Sensation.SensationType.Calibrate")
            if sensation.getMemory() == Sensation.Memory.Working:
                if sensation.getDirection() == Sensation.Direction.In:
                    print ("Walleserver.process asked to start calibrating mode")
                    self.calibrating = True
                else:
                    print ("Walleserver.process asked to stop calibrating mode")
                    self.calibrating = False
                # ask external senses to to set same calibrating mode          
                self.out_axon.put(sensation)
            elif sensation.getMemory() == Sensation.Memory.Sensory:
                if self.config.canHear() and self.calibrating:
                    if self.turning_to_object:
                        print ("Walleserver.process turning_to_object, can't start calibrate activity yet")
                    else:
                        # allow requester to start calibration activaties
                        if sensation.getDirection() == Sensation.Direction.In:
                            print ("Walleserver.process asked to start calibrating activity")
                            self.calibrating_angle = sensation.getHearDirection()
                            self.hearing.setCalibrating(calibrating=True, calibrating_angle=self.calibrating_angle)
                            sensation.setDirection(Sensation.Direction.In)
                            self.out_axon.put(sensation)
                            #self.calibratingTimer = Timer(WalleServer.ACTION_TIME, self.stopCalibrating)
                            #self.calibratingTimer.start()
                        else:
                            print ("Walleserver.process asked to stop calibrating activity")
                            self.hearing.setCalibrating(calibrating=False, calibrating_angle=self.calibrating_angle)
                            #self.calibratingTimer.cancel()
                else:
                    print ("Walleserver.process asked calibrating activity WITHOUT calibrate mode, IGNORED")


        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            print ("Walleserver.process Sensation.SensationType.Capability")
        elif sensation.getSensationType() == Sensation.SensationType.Unknown:
            print ("Walleserver.process Sensation.SensationType.Unknown")
  
    def turn(self):
        # calculate new power to turn or continue turning
        if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
            self.leftPower, self.rightPower = self.getPower()
            if self.turning_to_object:
                print ("WalleServer.turn: self.hearing_angle " + str(self.hearing_angle) + " self.azimuth " + str(self.azimuth))
                print ("WalleServer.turn: turn to " + str(self.observation_angle))
                if math.fabs(self.leftPower) < Romeo.MINPOWER or math.fabs(self.rightPower) < Romeo.MINPOWER:
                    self.stopTurn()
                    print ("WalleServer.turn: Turn is ended")
                    self.turnTimer.cancel()
                else:
                    print ("WalleServer.turn: powers adjusted to " + str(self.leftPower) + ' ' + str(self.rightPower))
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
                    if self.config.canHear():
                        self.hearing.setOn(not self.turning_to_object)
                    print ("WalleServer.turn: powers initial to " + str(self.leftPower) + ' ' + str(self.rightPower))
                    self.number = self.number + 1
                    sensation, picture = self.romeo.processSensation(Sensation(number=self.number, sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
                    self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
                    self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
                    self.turnTimer = Timer(WalleServer.ACTION_TIME, self.stopTurn)
                    self.turnTimer.start()

            
    def stopTurn(self):
        if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
            self.turning_to_object = False
            self.leftPower = 0.0           # set motors in opposite power to turn in place
            self.rightPower = 0.0
            print ("WalleServer.stopTurn: Turn is stopped/cancelled")
                
            print ("WalleServer.stopTurn: powers to " + str(self.leftPower) + ' ' + str(self.rightPower))
                
            if self.config.canHear():
                self.hearing.setOn(not self.turning_to_object)
                
            self.number = self.number + 1
            #test=Sensation.SensationType.Drive
            sensation, picture = self.romeo.processSensation(Sensation(number=self.number, sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
            self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
            self.rightPower = sensation.getRightPower()
            print ("WalleServer.stopTurn: powers set to " + str(self.leftPower) + ' ' + str(self.rightPower))


 #   def stopCalibrating(self):
 #       self.calibrating=False
 #       print "WalleServer.stopCalibrating: Calibrating mode is stopped/cancelled"


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
        
        if math.fabs(self.observation_angle - self.azimuth) > WalleServer.TURN_ACCURACYFACTOR:
            power = (self.observation_angle - self.azimuth)/WalleServer.FULL_TURN_FACTOR
            if power > 1.0:
                power = 1.0
            if power < -1.0:
                power = -1.0
            if math.fabs(power) < Romeo.MINPOWER:
                power = 0.0
            leftPower = power           # set motor in opposite power to turn in place
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
    print ("threaded_server: starting server")
    arg.serve_forever()
    print ("threaded_server: arg.serve_forever() ended")

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    print ("do_server: create WalleServer")
    walle = WalleServer()

    succeeded=True
    try:
        walle.start()
        
    except Exception: 
        print ("do_server: socket error, exiting")
        succeeded=False

    if succeeded:
        print ('do_server: Press Ctrl+C to Stop')

        WalleServer.walle = walle   # remember walle so
                                    # we can stop it in ignal_handler   
        walle.join()
        
    print ("do_server exit")
    
def signal_handler(signal, frame):
    print ('signal_handler: You pressed Ctrl+C!')
    
    WalleServer.walle.doStop()
    
#     print ('signal_handler: Shutting down sensation server ...')
#     WalleRequestHandler.server.serving =False
#     print ('signal_handler: sensation server is down OK')
#     
#     print ('signal_handler: Shutting down picture server...')
#     WalleRequestHandler.pictureServer.serving =False
#     print ('signal_handler: picture server is down OK')



    
def start(is_daemon):
        if is_daemon:
            print ("start: daemon.__file__ " +  daemon.__file__)
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
    
    print ("stop: socket.socket(socket.AF_INET, socket.SOCK_STREAM)")
    # Create a socket (SOCK_STREAM means a TCP socket)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            print ('stop: sock.connect((localhost, PORT))')
            address=('localhost', PORT)
            sock.connect(address)
            print ("stop: connected")
            print ("stop: SocketClient.stop")
            ok = SocketClient.stop(socket = sock, address=address)
            if ok:
                # Receive data from the server
                print ("stop: sock.recv(1024)")
                received = sock.recv(1024)
                print ('stop: received answer ' + received)
        except Exception as err: 
            print ("stop: socket connect, cannot stop localhost, error " + str(err))
            return
    except Exception as err: 
        print ("stop: socket error, cannot stop localhost , error " + str(err))
        return

    finally:
        print ('stop: sock.close()')
        sock.close()
    print ("stop: end")

 


if __name__ == "__main__":
    #WalleRequestHandler.romeo = None    # no romeo device connection yet

    print ('Number of arguments:', len(sys.argv), 'arguments.')
    print ('Argument List:', str(sys.argv))
    try:
        opts, args = getopt.getopt(sys.argv[1:],"",["start","stop","restart","daemon","manual"])
    except getopt.GetoptError:
      print (sys.argv[0] + '[--start] [--stop] [--restart] [--daemon] [--manual]')
      sys.exit(2)
    print ('opts '+ str(opts))
    for opt, arg in opts:
        print ('opt '+ opt)
        if opt == '--start':
            print (sys.argv[0] + ' start')
            START=True
        elif opt == '--stop':
            print (sys.argv[0] + ' stop')
            STOP=True
        elif opt == '--restart':
            print (sys.argv[0] + ' restart')
            STOP=True
            START=True
        elif opt == '--daemon':
            print (sys.argv[0] + ' daemon')
            DAEMON=True
        elif opt == '--manual':
            print (sys.argv[0] + ' manual')
            MANUAL=True
           
    if not START and not STOP:
        START=True
    
    if (STOP):
        stop()
    if (START): 
        start(DAEMON)   
             
    print ("__main__ exit")
    exit()



