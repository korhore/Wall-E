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
if 'Seeing.See' not in sys.modules:
    from Seeing.See import See
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


class RobotServer(Thread):
    """
    Controls Robot-robot. Robot has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Robot emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.
    External Sensorys are handled using sockets.
    """
    
    TURN_ACCURACYFACTOR = math.pi * 10.0/180.0
    FULL_TURN_FACTOR = math.pi * 45.0/180.0
    
    DEFAULT_OBSERVATION_DISTANCE = 3.0
    
    ACTION_TIME=1.0

#     TRUE_VALUE="True"
#    FALSE_VALUE="False"
  

    def __init__(self, configFilePath=Config.CONFIG_FILE_PATH,
                 in_axon=None,
                 out_axon=None):
        Thread.__init__(self)
        self.name = "RobotServer"
        
        Capabilities = 'Capabilities' 
        Memory =        'Memory'

       
        self.azimuth=0.0                # position sense, azimuth from north
        self.turning_to_object = False  # Are we turning to see an object
        self.hearing_angle = 0.0        # device hears sound from this angle, device looks to its front
                                        # to the azimuth direction
        self.observation_angle = 0.0           # turn until azimuth is this angle
        
        self.leftPower = 0.0            # moving
        self.rightPower = 0.0
        
         # TODO Identity from configuration
 
        self.config = Config(config_file_path=configFilePath)
        print(self.name + ": init robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())
        self.name = self.config.getWho()
          # global queue for senses and other robots to put sensations to robot
        if in_axon is None:
            self.in_axon = Axon(Config.LOCALHOST) 
        else:
            self.in_axon = in_axon
             
        # global queue for this robot to put sensations to external senses  (muscles) or robots
        if out_axon is None:
            self.out_axon = Axon(Config.LOCALHOST)
        else:
            self.out_axon = out_axon
        # starting build in capabilities/senses
        # we have capability to move
        if self.config.canMove():
            if MANUAL:
                self.romeo = ManualRomeo()
            else:
                self.romeo = Romeo()
            # we have hearing (positioning of object using sounds)
            self.turnTimer = Timer(RobotServer.ACTION_TIME, self.stopTurn)
            
        if self.config.canHear():
            self.hearing=Hear(self.in_axon)
        
        if self.config.canSee():
            self.seeing=See(self.in_axon)

        # Real instances can have sockets to other robots
        # starting tcp server as nerve pathway to external senses to connect
        # we have azimuth sense (our own position detection)
        if self.config.getInstance() == Sensation.Instance.Real:
            self.tcpServer=TCPServer(out_axon = self.in_axon, in_axon = self.out_axon, server_address=(HOST,PORT))

        
        self.running=False
        
        self.calibrating=False              # are we calibrating
        self.calibrating_angle = 0.0        # calibrate device hears sound from this angle, device looks to its front
        #self.calibratingTimer = Timer(RobotServer.ACTION_TIME, self.stopCalibrating)
        print(self.name + ": Calibrate version")
        
        # finally remember instance
        RobotServer.robot = self
        #and create virtual instances
        self.virtualInstances = []
        for virtualInstance in self.config.getVirtualInstances():
            robot = RobotServer(configFilePath=self.config.getVirtualinstanceConfigFilePath(virtualInstance))
            self.virtualInstances.append(robot)

       
    def run(self):
        print(self.name + ": Starting " + self.name)
        print(self.name + ": Starting robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())
        
        # starting other threads/senders/capabilities
        
        self.running=True
        
        if self.config.canHear():
            self.hearing.start()
        if self.config.canSee():
            self.seeing.start()
        if self.config.getInstance() == Sensation.Instance.Real:
            print(self.name + ": RobotServer: starting TCPServer")
            self.tcpServer.start()
        
        # start virtual instances here
        for robot in self.virtualInstances:
            robot.start()


        while self.running:
            sensation=self.in_axon.get()
            print (self.name + ": got sensation from queue " + str(sensation))
            self.process(sensation)
            # as a test, echo everything to external device
            #self.out_axon.put(sensation)
 
        print(self.name + ": Stopping robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())

         # stop virtual instances here, when main instance is not running any more
        for robot in self.virtualInstances:
            robot.stop()

        print (self.name + ": Robot:run shutting down ...")

        if self.config.getInstance() == Sensation.Instance.Real:
            print (self.name + ": Robot:run shutting down TcpServer ...")
            self.tcpServer.stop()
        
        if self.config.canHear():
            print (self.name + ": Robot:run shutting down hearing ...")
            self.hearing.stop()
        if self.config.canSee():
            print (self.name + ": Robot:run shutting down seeing ...")
            self.seeing.stop()
       
        print (self.name + " :Robot:run ALL SHUT DOWN")


    def stop(self):
        self.running = False
        for virtailInstace in self.GetVirtailInstaces():
            virtailInstace.stop()


    '''
    DoStop is used to stop server process and its sobprocesses (threads)
    Technique is just give Stop Sewnsation oto process.
    With same tecnique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        self.in_axon.put(Sensation(sensationType = Sensation.SensationType.Stop))

            
            
    def process(self, sensation):
        print (self.name + "; RobotServer.process: " + time.ctime(sensation.getTime()) + ' ' + str(sensation))
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            print (self.name + ": Robotserver.process Sensation.SensationType.Drive")
        elif sensation.getSensationType() == Sensation.SensationType.Stop:
            print (self.name + ": Robotserver.process Sensation.SensationType.Stop")
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Who:
            print (self.name + ": Robotserver.process Sensation.SensationType.Who")
        elif self.config.canHear() and sensation.getSensationType() == Sensation.SensationType.HearDirection:
            print (self.name + ": Robotserver.process Sensation.SensationType.HearDirection")
            #inform external senses that we remember now hearing          
            self.out_axon.put(sensation)
            self.hearing_angle = sensation.getHearDirection()
            if self.calibrating:
                print (self.name + ": Robotserver.process Calibrating hearing_angle " + str(self.hearing_angle) + " calibrating_angle " + str(self.calibrating_angle))
            else:
                self.observation_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
                print (self.name + ": Robotserver.process create Sensation.SensationType.Observation")
                self.in_axon.put(Sensation(sensationType = Sensation.SensationType.Observation,
                                           observationDirection= self.observation_angle,
                                           observationDistance=RobotServer.DEFAULT_OBSERVATION_DISTANCE))
                # mark hearing sensation to be processed to set direction out of memory, we forget it
                sensation.setDirection(Sensation.Direction.Out)
                #inform external senses that we don't remember hearing any more           
                self.out_axon.put(sensation)
        elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
            if not self.calibrating:
                print (self.name + ": Robotserver.process Sensation.SensationType.Azimuth")
                #inform external senses that we remember now azimuth          
                #self.out_axon.put(sensation)
                self.azimuth = sensation.getAzimuth()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Observation:
            if not self.calibrating:
                print (self.name + ": Robotserver.process Sensation.SensationType.Observation")
                #inform external senses that we remember now observation          
                self.out_axon.put(sensation)
                self.observation_angle = sensation.getObservationDirection()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.ImageFilePath:
            print (self.name + ": Robotserver.process Sensation.SensationType.ImageFilePath")
        elif sensation.getSensationType() == Sensation.SensationType.Calibrate:
            print (self.name + ": Robotserver.process Sensation.SensationType.Calibrate")
            if sensation.getMemory() == Sensation.Memory.Working:
                if sensation.getDirection() == Sensation.Direction.In:
                    print (self.name + ": Robotserver.process asked to start calibrating mode")
                    self.calibrating = True
                else:
                    print (self.name + ": Robotserver.process asked to stop calibrating mode")
                    self.calibrating = False
                # ask external senses to to set same calibrating mode          
                self.out_axon.put(sensation)
            elif sensation.getMemory() == Sensation.Memory.Sensory:
                if self.config.canHear() and self.calibrating:
                    if self.turning_to_object:
                        print (self.name + ": Robotserver.process turning_to_object, can't start calibrate activity yet")
                    else:
                        # allow requester to start calibration activaties
                        if sensation.getDirection() == Sensation.Direction.In:
                            print (self.name + ": Robotserver.process asked to start calibrating activity")
                            self.calibrating_angle = sensation.getHearDirection()
                            self.hearing.setCalibrating(calibrating=True, calibrating_angle=self.calibrating_angle)
                            sensation.setDirection(Sensation.Direction.In)
                            self.out_axon.put(sensation)
                            #self.calibratingTimer = Timer(RobotServer.ACTION_TIME, self.stopCalibrating)
                            #self.calibratingTimer.start()
                        else:
                            print (self.name + ": Robotserver.process asked to stop calibrating activity")
                            self.hearing.setCalibrating(calibrating=False, calibrating_angle=self.calibrating_angle)
                            #self.calibratingTimer.cancel()
                else:
                    print (self.name + ": Robotserver.process asked calibrating activity WITHOUT calibrate mode, IGNORED")


        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            print (self.name + ": Robotserver.process Sensation.SensationType.Capability")
        elif sensation.getSensationType() == Sensation.SensationType.Unknown:
            print (self.name + ": Robotserver.process Sensation.SensationType.Unknown")
  
    def turn(self):
        # calculate new power to turn or continue turning
        if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
            self.leftPower, self.rightPower = self.getPower()
            if self.turning_to_object:
                print (self.name + ": RobotServer.turn: self.hearing_angle " + str(self.hearing_angle) + " self.azimuth " + str(self.azimuth))
                print (self.name + ": RobotServer.turn: turn to " + str(self.observation_angle))
                if math.fabs(self.leftPower) < Romeo.MINPOWER or math.fabs(self.rightPower) < Romeo.MINPOWER:
                    self.stopTurn()
                    print (self.name + ": RobotServer.turn: Turn is ended")
                    self.turnTimer.cancel()
                else:
                    print (self.name + ": RobotServer.turn: powers adjusted to " + str(self.leftPower) + ' ' + str(self.rightPower))
                    sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
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
                    print (self.name + ": RobotServer.turn: powers initial to " + str(self.leftPower) + ' ' + str(self.rightPower))
                    sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
                    self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
                    self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
                    self.turnTimer = Timer(RobotServer.ACTION_TIME, self.stopTurn)
                    self.turnTimer.start()

            
    def stopTurn(self):
        if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
            self.turning_to_object = False
            self.leftPower = 0.0           # set motors in opposite power to turn in place
            self.rightPower = 0.0
            print (self.name + ": RobotServer.stopTurn: Turn is stopped/cancelled")
                
            print (self.name + ": RobotServer.stopTurn: powers to " + str(self.leftPower) + ' ' + str(self.rightPower))
                
            if self.config.canHear():
                self.hearing.setOn(not self.turning_to_object)
                
            #test=Sensation.SensationType.Drive
            sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
            self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
            self.rightPower = sensation.getRightPower()
            print (self.name + ": RobotServer.stopTurn: powers set to " + str(self.leftPower) + ' ' + str(self.rightPower))


 #   def stopCalibrating(self):
 #       self.calibrating=False
 #       print( self.name + ": RobotServer.stopCalibrating: Calibrating mode is stopped/cancelled")


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
        
        if math.fabs(self.observation_angle - self.azimuth) > RobotServer.TURN_ACCURACYFACTOR:
            power = (self.observation_angle - self.azimuth)/RobotServer.FULL_TURN_FACTOR
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

    print ("do_server: create RobotServer")
    robot = RobotServer()

    succeeded=True
    try:
        robot.start()
        for virtailInstace in robot.GetVirtailInstaces():
            virtailInstace.start()
        
    except Exception: 
        print ("do_server: socket error, exiting")
        succeeded=False

    if succeeded:
        print ('do_server: Press Ctrl+C to Stop')

        RobotServer.robot = robot   # remember robot so
                                    # we can stop it in ignal_handler   
        robot.join()
        
    print ("do_server exit")
    
def signal_handler(signal, frame):
    print ('signal_handler: You pressed Ctrl+C!')
    
    RobotServer.robot.doStop()
    
#     print ('signal_handler: Shutting down sensation server ...')
#     RobotRequestHandler.server.serving =False
#     print ('signal_handler: sensation server is down OK')
#     
#     print ('signal_handler: Shutting down picture server...')
#     RobotRequestHandler.pictureServer.serving =False
#     print ('signal_handler: picture server is down OK')



    
def start(is_daemon):
        if is_daemon:
            print ("start: daemon.__file__ " +  daemon.__file__)
            stdout=open('/tmp/Robot_Server.stdout', 'w+')
            stderr=open('/tmp/Robot_Server.stderr', 'w+')
            #remove('/var/run/Robot_Server.pid.lock')
            pidfile=lockfile.FileLock('/var/run/Robot_Server.pid')
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
    #RobotRequestHandler.romeo = None    # no romeo device connection yet
    cwd = os.getcwd()
    print("cwd " + cwd)


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



