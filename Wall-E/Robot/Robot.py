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
from Config import Config, Capabilities

# HOST = '0.0.0.0'
# PORT = 2000
# PICTURE_PORT = 2001

DAEMON=False
START=False
STOP=False
MANUAL=False


class Robot(Thread):
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
  

    def __init__(self, workingDirectory=None,
                 configFilePath=Config.CONFIG_FILE_PATH,
                 inAxon=None, # we read this as muscle functionality and getting
                              # sensationsfron ot subInstances (Senses)
                              # write to this when submitting things to subInstances
                 outAxon=None):
        Thread.__init__(self)
        self.mode = Sensation.Mode.Starting
        self.inAxon = inAxon    # axon for up direction
        self.outAxon = outAxon
        self.subInstances = []     # subInstance contain a outAxon we write muscle sensations
                                # for subrobot this axon in inAxon
                                # We ask subInstance to report its Sensations to
                                # inAxon, so our live is reading inAxon
                                # and writing to outAxon, which is created by us
                                # or give in this method
        self.running=False

       
#         Capabilities = 'Capabilities' 
#         Memory =       'Memory'

       
 
        self.config = Config(config_file_path=configFilePath)
        self.capabilities = Capabilities(config=self.config)
        self.log("init robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())
        self.name = self.config.getWho()
        # global queue for senses and other robots to put sensations to robot
        if self.inAxon is None:
            self.inAxon = Axon(config=self.config) 
        if self.outAxon is None:
            self.outAxon = Axon(config=self.config) 
 
        # TODO           
        # Study our config. What subInstances we have.
             
                #and create virtual instances
        for subInstance in self.config.getSubInstances():
            robot = Robot(configFilePath=self.config.getSubinstanceConfigFilePath(subInstance),
                          outAxon=self.inAxon)
            self.subInstances.append(robot)

        for virtualInstance in self.config.getVirtualInstances():
            robot = Robot(configFilePath=self.config.getVirtualinstanceConfigFilePath(virtualInstance),
                          outAxon=self.inAxon)
            self.subInstances.append(robot)
            
    def getInAxon(self):
        return self.inAxon
    def setInAxon(self, inAxon):
        self.inAxon = inAxon

    def getOutAxon(self):
        return self.outAxon
    def setOutAxon(self, outAxon):
        self.outAxon = outAxon
       
    def getConfig(self):
        return self.config
    def setConfig(self, outAxon):
        self.config = config

    def getCapabilities(self):
        return self.capabilities
    def setCapabilities(self, capabilities):
        self.capabilities = capabilities

    def run(self):
        self.log(" Starting robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())      
        
        # starting other threads/senders/capabilities
        
        self.running=True
                
        # start subInstances and virtual instances here
        for robot in self.subInstances:
            robot.start()
            
        # study own identity
        # starting point of robot is always to study what it knows himself
        self.studyOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            sensation=self.inAxon.get()
            self.log("got sensation from queue " + str(sensation))      
            self.process(sensation)
            # as a test, echo everything to external device
            #self.out_axon.put(sensation)
 
        self.mode = Sensation.Mode.Stopping
        self.log("Stopping robot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log("run ALL SHUT DOWN")      
        
    def log(self, logStr):
         print(self.name + ":" + Sensation.Modes[self.mode] + ": " + logStr)

    def stop(self):
        self.log("Stopping robot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
        self.running = False    # this in not real, but we wait for Sensation,
                                # so give  us one stop sensation
        self.inAxon.put(Sensation(sensationType = Sensation.SensationType.Stop))


    '''
    DoStop is used to stop server process and its subprocesses (threads)
    Technique is just give Stop Sensation oto process.
    With same technique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        self.inAxon.put(Sensation(sensationType = Sensation.SensationType.Stop))
        
    def studyOwnIdentity(self):
        self.mode = Sensation.Mode.StudyOwnIdentity
        self.log("My name is " + self.name)      
        self.kind = self.config.getKind()
        self.log("My kind is " + str(self.kind))      
        self.identitypath = self.config.getIdentityDirPath(self.kind)
        self.log('My identitypath is ' + self.identitypath)      
        for dirName, subdirList, fileList in os.walk(self.identitypath):
            self.log('Found directory: %s' % dirName)      
            for fname in fileList:
                self.log('\t%s' % fname)      

            
            
    def process(self, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + str(sensation))      
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            self.log('process: Sensation.SensationType.Drive')      
        elif sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')      
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Who:
            print (self.name + ": Robotserver.process Sensation.SensationType.Who")
            
        # TODO study what capabilities out subrobots have ins put sensation to them
        elif self.config.canHear() and sensation.getSensationType() == Sensation.SensationType.HearDirection:
            self.log('process: SensationType.HearDirection')      
             #inform external senses that we remember now hearing          
            self.out_axon.put(sensation)
            self.hearing_angle = sensation.getHearDirection()
            if self.calibrating:
                self.log("process: Calibrating hearing_angle " + str(self.hearing_angle) + " calibrating_angle " + str(self.calibrating_angle))      
            else:
                self.observation_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
                self.log("process: create Sensation.SensationType.Observation")
                observation = Sensation(sensationType = Sensation.SensationType.Observation,
                                        memory=Memory.Work,
                                        observationDirection= self.observation_angle,
                                        observationDistance=Robot.DEFAULT_OBSERVATION_DISTANCE,
                                        reference=sensation)
                # process internally
                self.log("process: put Observation to in_axon")
                self.inAxon.put(observation)
                
                #process by remote robotes
                # mark hearing sensation to be processed to set direction out of memory, we forget it
                sensation.setDirection(Sensation.Direction.Out)
                observation.setDirection(Sensation.Direction.Out)
                #inform external senses that we don't remember hearing any more           
                self.log("process: put HearDirection to out_axon")
                self.out_axon.put(sensation)
                # seems that out_axon is handled when observation is processed internally here
                #self.log("process: put Observation to out_axon")
                #self.out_axon.put(observation)
        elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
            if not self.calibrating:
                self.log('process: Sensation.SensationType.Azimuth')      
                #inform external senses that we remember now azimuth          
                #self.out_axon.put(sensation)
                self.azimuth = sensation.getAzimuth()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Observation:
            if not self.calibrating:
                self.log('process: Sensation.SensationType.Observation')      
                #inform external senses that we remember now observation          
                self.observation_angle = sensation.getObservationDirection()
                self.turn()
                self.log("process: put Observation to out_axon")
                sensation.setDirection(Sensation.Direction.Out)
                self.out_axon.put(sensation)
        elif sensation.getSensationType() == Sensation.SensationType.ImageFilePath:
            self.log('process: Sensation.SensationType.ImageFilePath')      
        elif sensation.getSensationType() == Sensation.SensationType.Calibrate:
            self.log('process: Sensation.SensationType.Calibrate')      
            if sensation.getMemory() == Sensation.Memory.Working:
                if sensation.getDirection() == Sensation.Direction.In:
                    self.log('process: asked to start calibrating mode')      
                    self.calibrating = True
                else:
                    self.log('process: asked to stop calibrating mode')      
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
                            self.log('process: asked to start calibrating activity')      
                            self.calibrating_angle = sensation.getHearDirection()
                            self.hearing.setCalibrating(calibrating=True, calibrating_angle=self.calibrating_angle)
                            sensation.setDirection(Sensation.Direction.In)
                            self.log('process: calibrating put HearDirection to out_axon')      
                            self.out_axon.put(sensation)
                            #self.calibratingTimer = Timer(Robot.ACTION_TIME, self.stopCalibrating)
                            #self.calibratingTimer.start()
                        else:
                            self.log('process: asked to stop calibrating activity')      
                            self.hearing.setCalibrating(calibrating=False, calibrating_angle=self.calibrating_angle)
                            #self.calibratingTimer.cancel()
                else:
                    self.log('process: asked calibrating activity WITHOUT calibrate mode, IGNORED')      


        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            self.log('process: Sensation.SensationType.Capability')      
        elif sensation.getSensationType() == Sensation.SensationType.Unknown:
            self.log('process: Sensation.SensationType.Unknown')      
  
    def turn(self):
        # calculate new power to turn or continue turning
        if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
            self.leftPower, self.rightPower = self.getPower()
            if self.turning_to_object:
                self.log("turn: self.hearing_angle " + str(self.hearing_angle) + " self.azimuth " + str(self.azimuth))      
                self.log("turn: turn to " + str(self.observation_angle))      
                if math.fabs(self.leftPower) < Romeo.MINPOWER or math.fabs(self.rightPower) < Romeo.MINPOWER:
                    self.stopTurn()
                    self.log("turn: Turn is ended")      
                    self.turnTimer.cancel()
                else:
                    self.log("turn: powers adjusted to " + str(self.leftPower) + ' ' + str(self.rightPower))      
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
                    self.log("turn: powers initial to " + str(self.leftPower) + ' ' + str(self.rightPower))      
                    sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
                    self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
                    self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
                    self.turnTimer = Timer(Robot.ACTION_TIME, self.stopTurn)
                    self.turnTimer.start()

            
    def stopTurn(self):
        if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
            self.turning_to_object = False
            self.leftPower = 0.0           # set motors in opposite power to turn in place
            self.rightPower = 0.0
            self.log("stopTurn: Turn is stopped/cancelled")      
            self.log("stopTurn: powers to " + str(self.leftPower) + ' ' + str(self.rightPower))      
                
            if self.config.canHear():
                self.hearing.setOn(not self.turning_to_object)
                
            #test=Sensation.SensationType.Drive
            sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
            self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
            self.rightPower = sensation.getRightPower()
            self.log("stopTurn: powers set to " + str(self.leftPower) + ' ' + str(self.rightPower))      


 #   def stopCalibrating(self):
 #       self.calibrating=False
 #       print( self.name + ": Robot.stopCalibrating: Calibrating mode is stopped/cancelled")


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
        
        if math.fabs(self.observation_angle - self.azimuth) > Robot.TURN_ACCURACYFACTOR:
            power = (self.observation_angle - self.azimuth)/Robot.FULL_TURN_FACTOR
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

    print ("do_server: create Robot")
    global robot
    robot = Robot()

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

        Robot.robot = robot   # remember robot so
                                    # we can stop it in ignal_handler   
        robot.join()
        
    print ("do_server exit")
    
def signal_handler(signal, frame):
    print ('signal_handler: You pressed Ctrl+C!')
    
    robot.doStop()
    
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


