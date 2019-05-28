'''
Created on Feb 24, 2013
Updated on 19.05.2019
@author: reijo.korhonen@gmail.com

This class Main robot
that start and manages all subrobots

    Controls Robot-robot. Robot has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Robot emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.


'''

import os
import time
import sys
import signal
import getopt

from threading import Thread
from threading import Timer

import socket



from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

HOST = ''
PORT = 2000
ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM

DAEMON=False
START=False
STOP=False
MANUAL=False


class MainRobot(Robot):
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
    

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in MainRobot, not Robot")
 
        Robot.__init__(self,
                       parent = None,                            # Main robot can't have parent
                       instanceName=Config.MAIN_INSTANCE,        # instance name is main robot
                       instanceType=Sensation.InstanceType.Real, # Instancetype is real
                       level=level)
        print("We are in MainRobot, not Robot")
        
        # in main robot, set up TCPServer
        if self.level == 1:
            self.tcpServer=TCPServer(parent=self,
                                     hostNames=self.config.getHostNames(),
                                     instanceName='TCPServer',
                                     instanceType=Sensation.InstanceType.Remote,
                                     level=self.level,
                                     address=(HOST,PORT))


    def run(self):
        self.running=True
        self.log("run: Starting Main Robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()

        # main robot starts tcpServer first so clients gets connection
        if self.level == 1:
            self.tcpServer.start()
           
        # study own identity
        # starting point of robot is always to study what it knows himself
        self.studyOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            sensation=self.getAxon().get()
            self.log("got sensation from queue " + sensation.toDebugStr())      
            self.process(sensation)
            # as a test, echo everything to external device
            #self.out_axon.put(sensation)
 
        self.mode = Sensation.Mode.Stopping
        self.log("Stopping robot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log("run ALL SHUT DOWN")      
        
        
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

    '''    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    TODO above implementation is mostly for Hearing Sensory and
    Moving Sensory and should be move to those implementations.
    
    '''
            
            
    def process(self, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')      
            self.stop()

        elif sensation.getDirection() == Sensation.Direction.Out:
            if sensation.getSensationType() == Sensation.SensationType.Capability:
                self.log('process: sensation.getSensationType() == Sensation.SensationType.Capability')      
                self.log('process: self.setCapabilities(Capabilities(capabilities=sensation.getCapabilities() ' + sensation.getCapabilities().toDebugString('capabilities'))      
                self.setCapabilities(Capabilities(deepCopy=sensation.getCapabilities()))
                self.log('process: capabilities: ' + self.getCapabilities().toDebugString('saved capabilities'))      
            elif self.getParent() is not None: # if sensation is going up  and we have a parent
                self.log('process: self.getParent().getAxon().put(sensation)')      
                self.getParent().getAxon().put(sensation)
            else:
                # do some basic processing of main robot level and testing
                #Voicedata can be played back, if we have a subcapability for it
                if sensation.getSensationType() == Sensation.SensationType.Voice or \
                   sensation.getSensationType() == Sensation.SensationType.Image or \
                    sensation.getSensationType() == Sensation.SensationType.Item:
                    self.log('process: Main root Sensation.SensationType.Voice, Image or Item Out')
                    # basically we don't know how to handle going in sensation, but
                    # subInstances can know. Check which subinsces can process this and deliver sensation to them.
                    # Also subclasses can implement their own implementation for processing        
                    robots = self.getSubCapabiliyInstances(direction=Sensation.Direction.In, memory=sensation.getMemory(), sensationType=sensation.getSensationType())
                    self.log('Sensation.Direction.Out -> In self.getSubCapabiliyInstances' + str(robots))
                    for robot in robots:
                        sensation.setDirection(Sensation.Direction.In)# todo, we should create new in-direction instance and reference it
                        playbackSensation = Sensation.create(sensation=sensation, references=[sensation], direction=Sensation.Direction.In) # new instance or sensation for playback
                        
                        if robot.getInstanceType() == Sensation.InstanceType.Remote:
                            # if this sensation comes from sockrServers host
                            if sensation.isReceivedFrom(robot.getHost()) or \
                               sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                                self.log('Remote robot ' + robot.getWho() + 'has capability for this, but sensation comes from it self. Don\'t recycle it')
                            else:
                                self.log('Remote robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(sensation)')
                                robot.getAxon().put(playbackSensation)
                        else:
                            self.log('Local robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(sensation)')
                            robot.getAxon().put(playbackSensation)
                       
        else:
            # basically we don't know how to handle going in sensation, but
            # subInstances can know. Check which subinsces can process this and deliver sensation to them.
            # Also subclasses can implement their own implementation for processing        
            if sensation.getSensationType() == Sensation.SensationType.Voice:
                self.log('process: Main root Sensation.SensationType.Voice In')
            if sensation.getSensationType() == Sensation.SensationType.Image:
                self.log('process: Main root Sensation.SensationType.Image In')
            robots = self.getSubCapabiliyInstances(direction=Sensation.Direction.In, memory=sensation.getMemory(), sensationType=sensation.getSensationType())
            self.log('Sensation.Direction.In self.getSubCapabiliyInstances' + str(robots))
            for robot in robots:
                if robot.getInstanceType() == Sensation.InstanceType.Remote:
                    # if this sensation comes from sockrServers host
                    if sensation.isReceivedFrom(robot.getHost()) or \
                       sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                        self.log('Remote robot ' + robot.getWho() + 'has capability for this, but sensation comes from it self. Don\'t recycle it')
                    else:
                        self.log('Remote robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(sensation)')
                        robot.getAxon().put(sensation)
                else:
                    self.log('Local robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(sensation)')
                    robot.getAxon().put(sensation)
 #             # for testing purposes write this back to all out subInstances playback gets it
#             for robot in self.subInstances:
#                 if robot.getWho() == "Speaking":
#                     # TODO should we make a copy, because we should not change original sensation
#                     sensation.setDirection(Sensation.Direction.In)
#                     self.log('process: Sensation.SensationType.Voice Speaking robot.getInAxon().put(sensation)')
#                     robot.getInAxon().put(sensation)
#                     return  

        # TODO This old stuf is not needed   
#         if sensation.getSensationType() == Sensation.SensationType.Drive:
#             self.log('process: Sensation.SensationType.Drive')      
#         elif sensation.getSensationType() == Sensation.SensationType.Stop:
#             self.log('process: SensationSensationType.Stop')      
#             self.stop()
#         elif sensation.getSensationType() == Sensation.SensationType.Who:
#             print (self.name + ": Robotserver.process Sensation.SensationType.Who")
#             
#         # TODO study what capabilities out subrobots have ins put sensation to them
#         elif self.config.canHear() and sensation.getSensationType() == Sensation.SensationType.HearDirection:
#             self.log('process: SensationType.HearDirection')      
#              #inform external senses that we remember now hearing          
#             self.out_axon.put(sensation)
#             self.hearing_angle = sensation.getHearDirection()
#             if self.calibrating:
#                 self.log("process: Calibrating hearing_angle " + str(self.hearing_angle) + " calibrating_angle " + str(self.calibrating_angle))      
#             else:
#                 self.observation_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
#                 self.log("process: create Sensation.SensationType.Observation")
#                 observation = Sensation(sensationType = Sensation.SensationType.Observation,
#                                         memory=Memory.Work,
#                                         observationDirection= self.observation_angle,
#                                         observationDistance=Robot.DEFAULT_OBSERVATION_DISTANCE,
#                                         reference=sensation)
#                 # process internally
#                 self.log("process: put Observation to in_axon")
#                 self.inAxon.put(observation)
#                 
#                 #process by remote robotes
#                 # mark hearing sensation to be processed to set direction out of memory, we forget it
#                 sensation.setDirection(Sensation.Direction.Out)
#                 observation.setDirection(Sensation.Direction.Out)
#                 #inform external senses that we don't remember hearing any more           
#                 self.log("process: put HearDirection to out_axon")
#                 self.out_axon.put(sensation)
#                 # seems that out_axon is handled when observation is processed internally here
#                 #self.log("process: put Observation to out_axon")
#                 #self.out_axon.put(observation)
#         elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
#             if not self.calibrating:
#                 self.log('process: Sensation.SensationType.Azimuth')      
#                 #inform external senses that we remember now azimuth          
#                 #self.out_axon.put(sensation)
#                 self.azimuth = sensation.getAzimuth()
#                 self.turn()
#         elif sensation.getSensationType() == Sensation.SensationType.Observation:
#             if not self.calibrating:
#                 self.log('process: Sensation.SensationType.Observation')      
#                 #inform external senses that we remember now observation          
#                 self.observation_angle = sensation.getObservationDirection()
#                 self.turn()
#                 self.log("process: put Observation to out_axon")
#                 sensation.setDirection(Sensation.Direction.Out)
#                 self.out_axon.put(sensation)
#         elif sensation.getSensationType() == Sensation.SensationType.ImageFilePath:
#             self.log('process: Sensation.SensationType.ImageFilePath')      
#         elif sensation.getSensationType() == Sensation.SensationType.Calibrate:
#             self.log('process: Sensation.SensationType.Calibrate')      
#             if sensation.getMemory() == Sensation.Memory.Working:
#                 if sensation.getDirection() == Sensation.Direction.In:
#                     self.log('process: asked to start calibrating mode')      
#                     self.calibrating = True
#                 else:
#                     self.log('process: asked to stop calibrating mode')      
#                     self.calibrating = False
#                 # ask external senses to to set same calibrating mode          
#                 self.out_axon.put(sensation)
#             elif sensation.getMemory() == Sensation.Memory.Sensory:
#                 if self.config.canHear() and self.calibrating:
#                     if self.turning_to_object:
#                         print (self.name + ": Robotserver.process turning_to_object, can't start calibrate activity yet")
#                     else:
#                         # allow requester to start calibration activaties
#                         if sensation.getDirection() == Sensation.Direction.In:
#                             self.log('process: asked to start calibrating activity')      
#                             self.calibrating_angle = sensation.getHearDirection()
#                             self.hearing.setCalibrating(calibrating=True, calibrating_angle=self.calibrating_angle)
#                             sensation.setDirection(Sensation.Direction.In)
#                             self.log('process: calibrating put HearDirection to out_axon')      
#                             self.out_axon.put(sensation)
#                             #self.calibratingTimer = Timer(Robot.ACTION_TIME, self.stopCalibrating)
#                             #self.calibratingTimer.start()
#                         else:
#                             self.log('process: asked to stop calibrating activity')      
#                             self.hearing.setCalibrating(calibrating=False, calibrating_angle=self.calibrating_angle)
#                             #self.calibratingTimer.cancel()
#                 else:
#                     self.log('process: asked calibrating activity WITHOUT calibrate mode, IGNORED')      
# 
# 
#         elif sensation.getSensationType() == Sensation.SensationType.Capability:
#             self.log('process: Sensation.SensationType.Capability')      
#         elif sensation.getSensationType() == Sensation.SensationType.Unknown:
#             self.log('process: Sensation.SensationType.Unknown')
 
        # Finally just put sensation to our parent (if we have one)
#         if self.getLevel() > 1:
#             self.outAxon.put(sensation)
  
#     def turn(self):
#         # calculate new power to turn or continue turning
#         if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
#             self.leftPower, self.rightPower = self.getPower()
#             if self.turning_to_object:
#                 self.log("turn: self.hearing_angle " + str(self.hearing_angle) + " self.azimuth " + str(self.azimuth))      
#                 self.log("turn: turn to " + str(self.observation_angle))      
#                 if math.fabs(self.leftPower) < Romeo.MINPOWER or math.fabs(self.rightPower) < Romeo.MINPOWER:
#                     self.stopTurn()
#                     self.log("turn: Turn is ended")      
#                     self.turnTimer.cancel()
#                 else:
#                     self.log("turn: powers adjusted to " + str(self.leftPower) + ' ' + str(self.rightPower))      
#                     sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
#                     self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
#                     self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
#                     
#             else:
#                 if math.fabs(self.leftPower) >= Romeo.MINPOWER or math.fabs(self.rightPower) >= Romeo.MINPOWER:
#                     self.turning_to_object = True
#                     # adjust hearing
#                     # if turn, don't hear sound, because we are giving moving sound
#                     # we want hear only sounds from other objects
#                     if self.config.canHear():
#                         self.hearing.setOn(not self.turning_to_object)
#                     self.log("turn: powers initial to " + str(self.leftPower) + ' ' + str(self.rightPower))      
#                     sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
#                     self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
#                     self.rightPower = sensation.getRightPower()           # set motors in opposite power to turn in place
#                     self.turnTimer = Timer(Robot.ACTION_TIME, self.stopTurn)
#                     self.turnTimer.start()
# 
#             
#     def stopTurn(self):
#         if self.config.canMove() and self.romeo.exitst(): # if we have moving capability
#             self.turning_to_object = False
#             self.leftPower = 0.0           # set motors in opposite power to turn in place
#             self.rightPower = 0.0
#             self.log("stopTurn: Turn is stopped/cancelled")      
#             self.log("stopTurn: powers to " + str(self.leftPower) + ' ' + str(self.rightPower))      
#                 
#             if self.config.canHear():
#                 self.hearing.setOn(not self.turning_to_object)
#                 
#             #test=Sensation.SensationType.Drive
#             sensation, picture = self.romeo.processSensation(Sensation(sensationType='D', leftPower = self.leftPower, rightPower = self.rightPower))
#             self.leftPower = sensation.getLeftPower()           # set motors in opposite power to turn in place
#             self.rightPower = sensation.getRightPower()
#             self.log("stopTurn: powers set to " + str(self.leftPower) + ' ' + str(self.rightPower))      
# 
# 
#  #   def stopCalibrating(self):
#  #       self.calibrating=False
#  #       print( self.name + ": Robot.stopCalibrating: Calibrating mode is stopped/cancelled")
# 
# 
#     def add_radian(self, original_radian, added_radian):
#         result = original_radian + added_radian
#         if (result > math.pi):
#             return -math.pi + (result - math.pi)
#         if (result < -math.pi):
#             return math.pi - (result - math.pi)
#         return result
# 
# 
#     def getPower(self):
#         leftPower = 0.0           # set motor in opposite power to turn in place
#         rightPower = 0.0
#         
#         if math.fabs(self.observation_angle - self.azimuth) > Robot.TURN_ACCURACYFACTOR:
#             power = (self.observation_angle - self.azimuth)/Robot.FULL_TURN_FACTOR
#             if power > 1.0:
#                 power = 1.0
#             if power < -1.0:
#                 power = -1.0
#             if math.fabs(power) < Romeo.MINPOWER:
#                 power = 0.0
#             leftPower = power           # set motor in opposite power to turn in place
#             rightPower = -power
#         if math.fabs(leftPower) < Romeo.MINPOWER or math.fabs(rightPower) < Romeo.MINPOWER:
#             leftPower = 0.0           # set motors in opposite power to turn in place
#             rightPower = 0.0
#  
#         # test system has so little power, that we must run it at full speed           
#  #       if leftPower > Romeo.MINPOWER:
#  #           leftPower = 1.0           # set motorn in opposite pover to turn in place
#  #           rightPower = -1.0
#  #       elif leftPower < -Romeo.MINPOWER:
#  #           leftPower = -1.0           # set motorn in opposite pover to turn in place
#  #           rightPower = 1.0
#             
#             
#         return leftPower, rightPower
        
'''
TCPserver is a Robot that gets connections from other Robots behind network
and delivers them to main Robot. This is done as sensation, because main
robot is a robot that reads sensations.

Another possibility is handle these subrots locally here, but it may be better to
handle all sunrobot sensastion routing things in main robot
TODO Capabilities come from network

'''
        
class TCPServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    
    # inhered
#    address_family = socket.AF_INET
#    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    #allow_reuse_address = False


#    def __init__(self, out_axon, in_axon, server_address):
    def __init__(self,
                 address,
                 hostNames,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0):

        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in TCPServer, not Robot")
        self.address=address
        self.name = str(address)
        self.hostNames = hostNames

        Thread.__init__(self)
        self.name = "TCPServer"
        self.log('__init__: creating socket' )
        self.sock = socket.socket(family=ADDRESS_FAMILY,
                                  type=SOCKET_TYPE)
        self.sock.setblocking(1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketServers = []
        self.socketClients = []
        self.running=False
       
    def run(self):
        self.log('run: Starting')
               
        self.running=True
        self.mode = Sensation.Mode.Normal

#        if self.allow_reuse_address:
#            self.socket.setsockopt(socket.SOL_TCP, socket.SO_REUSEADDR, 1)
#            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          
        try:
            self.log('run: bind '+ str(self.address))
            self.sock.bind(self.address)
            self.server_address = self.sock.getsockname()
            self.sock.listen(self.request_queue_size)
            
            self.log("TCPServer for hostName in self.hostNames")
            for hostName in self.hostNames:
                self.log("TCPServer hostname " + hostName)
                address=(hostName, PORT)
                sock = socket.socket(family=ADDRESS_FAMILY,
                                     type=SOCKET_TYPE)
                
                connected=False
                try:
                    self.log('run: sock.connect('  + str(address) + ')')
                    sock.connect(address)
                    connected=True
                    self.log('run: done sock.connect('  + str(address) + ')')
                except Exception as e:
                    self.log("run: sock.connect(" + str(address) + ') exception ' + str(e))
                    connected = False
    
                if connected:
                    socketServer = self.createSocketServer(sock=sock, address=address)
                    socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer)
                    socketServer.setSocketClient(socketClient)
                    # add only socketClients to subInstances, because they give us capabilities
                    # but we give capabilities to thers with socketServer
                    #self.parent.subInstances.append(socketServer)
                    self.parent.subInstances.append(socketClient)  # Note to parent subInstances
                    socketServer.start()
                    time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
                    socketClient.start()
                    time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
        except Exception as e:
                self.log("run: sock.bind, listen exception " + str(e))
                self.running = False
        
 
        while self.running:
            self.log('run: waiting self.sock.accept()')
            sock, address = self.sock.accept()
            self.log('run: self.sock.accept() '+ str(address))
            socketServer = self.createSocketServer(sock=sock, address=address)
            socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer)
            socketServer.setSocketClient(socketClient)
            #self.parent.subInstances.append(socketServer)
            self.parent.subInstances.append(socketClient) # Note to parent subInstances


            if self.running:
                self.log('run: socketServer.start()')
                socketServer.start()
                time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
            if self.running:
                self.log('run: socketClient.start()')
                socketClient.start()
                time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything

    def stop(self):
        self.log('stop')
        print(self.name + ":stop") 
        self.running = False
        self.mode = Sensation.Mode.Stopping
        for socketServer in self.socketServers:
            if socketServer.running:
                socketServer.stop()
        for socketClient in self.socketClients:
            if socketClient.running:
                socketClient.stop()
        
    def createSocketServer(self, sock, address, socketClient=None):
        socketServer =  None
        for socketServerCandidate in self.socketServers:
            if not socketServerCandidate.running:
                socketServer = socketServerCandidate
                self.log('createSocketServer: found SocketServer not running')
                socketServer.__init__(parent=self,
                                      instanceName='SocketServer',
                                      instanceType=Sensation.InstanceType.Remote,
                                      level=self.level,
                                      address=address,
                                      sock=sock,
                                      socketClient=socketClient)
                break
        if not socketServer:
            self.log('createSocketServer: creating new SocketServer')
            socketServer = SocketServer(parent=self,
                                        instanceName='SocketServer',
                                        instanceType=Sensation.InstanceType.Remote,
                                        level=self.level,
                                        address=address,
                                        sock=sock,
                                        socketClient=socketClient)

            self.socketServers.append(socketServer)
        return socketServer

    def createSocketClient(self, sock, address, socketServer=None):
        socketClient =  None
        for socketClientCandidate in self.socketClients:
            if not socketClientCandidate.running:
                socketClient = socketClientCandidate
                self.log('createSocketClient: found SocketClient not running')
                socketClient.__init__(parent=self.parent,
                                      instanceName='SocketClient',
                                      instanceType=Sensation.InstanceType.Remote,
                                      level=self.level,
                                      address=address,
                                      sock=sock,
                                      socketServer=socketServer)
                break
        if not socketClient:
            self.log('createSocketClient: creating new SocketClient')
            socketClient = SocketClient(parent=self.parent,
                                        instanceName='SocketClient',
                                        instanceType=Sensation.InstanceType.Remote,
                                        level=self.level,
                                        address=address,
                                        sock=sock,
                                        socketServer=socketServer)
            self.socketClients.append(socketClient)
        return socketClient

class SocketClient(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 address = None,
                 remoteHost=None,
                 sock = None,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0,
                 socketServer=None):
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)

        print("We are in SocketClient, not Robot")
        self.sock = sock
        self.address = address
        self.remoteHost=remoteHost
        self.socketServer = socketServer
        if self.sock is None or self.address is None:       
            self.address=(self.remoteHost, PORT)
        self.name = 'SocketClient:'+str(address)
        self.running=False
        self.log("__init__ done")
        
    def getHost(self):
        return self.address[0]

    def setSocketServer(self, socketServer):
        self.socketServer = socketServer
    def getSocketServer(self):
        return self.socketServer

#         if self.sock is None:       
#             self.sock = socket.socket(family=ADDRESS_FAMILY,
#                                         type=SOCKET_TYPE)
#             try:
#                 self.log('self.sock.connect('  + str(self.address) + ')')
#                 self.sock.connect(self.address)
#                 self.log('sobe self.sock.connect('  + str(self.address) + ')')
#             except Exception as e:
#                 self.log("self.sock.connect(self.address) exception " + str(e))
 
    '''
    remove this test run implementation when connection is done OK
    '''               
    def run(self):
        self.running=True
        self.mode = Sensation.Mode.Normal
        self.log("run: Starting")
                 
        try:
            # tell who we are
            sensation=Sensation(direction=Sensation.Direction.Out, sensationType = Sensation.SensationType.Who, who=self.getWho())
            self.log('run: sendSensation(sensation=Sensation(sensationType = Sensation.SensationType.Who), sock=self.sock,'  + str(self.address) + ')')
            self.running =  self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
            self.log('run: done sendSensation(sensation=Sensation(sensationType = Sensation.SensationType.Who), sock=self.sock,'  + str(self.address) + ')')
            if self.running:
                 # tell our local capabilities
                 # it is important to deliver only local capabilities to the remote,
                 # because other way we would deliver back remote's own capabilities we don't have and
                 # remote would and we to do something that it only can do and
                 # we would route sensation back to remote, which routes it back to us
                 # in infinite loop
                capabilities=self.getLocalMasterCapabilities()
                self.log('run: self.getLocalMasterCapabilities() '  + capabilities.toString())
                self.log('run: self.getLocalMasterCapabilities() ' +capabilities.toDebugString())

                sensation=Sensation(direction=Sensation.Direction.Out, sensationType = Sensation.SensationType.Capability, capabilities=capabilities)
                self.log('run: Sensation(sensationType = Sensation.SensationType.Capability, capabilities=self.getLocalCapabilities()), sock=self.sock,'  + str(self.address) + ')')
                self.running = self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
                self.log('run: done ' + str(self.address) +  ' '  + sensation.getCapabilities().toDebugString('SocketClient'))
        except Exception as e:
            self.log("run: SocketClient.sendSensation exception " + str(e))
            self.running = False

        # Nope, can't do anything like below code
#         # finally normal run from Robot-class
        if self.running:
            super(SocketClient, self).run()

        
        # starting other threads/senders/capabilities

        
    def process(self, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + sensation.toDebugStr())
        # We can handle only sensation going in-direction
        if sensation.getDirection() == Sensation.Direction.In:
             self.running = self.sendSensation(sensation, self.sock, self.address) 
        # stop and stop remote also
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')
            self.getSocketServer().stop()   # stop SockerServer also  
            self.stop()


        #self.sock.close()

    '''
    Overwrite local method. This way we can use remote Robot
    same way than local ones.
    
    our server has got capabilities from remote host
    our own capabilities are meaningless
    '''
    def getCapabilities(self):
        if self.getSocketServer() is not None:
            self.log('getCapabilities: self.getSocketServer().getCapabilities() ' + self.getSocketServer().getCapabilities().toDebugString('SocketClient Capabilities'))
            return self.getSocketServer().getCapabilities()
        return None

    '''
    Create local method with different name
    We use this to send capabilities to remote
        '''
    def getLocalCapabilities(self):
        return self.capabilities

   
    '''
    ask capabilities from our remote host
    tell our capabilities to remote tells it's
    '''
        
#     def askCapabilities(self):
#         self.log('askCapabilities')
#         sensation=Sensation(sensationType=Sensation.SensationType.Capability, capabilities=self.getCapabilities())
#         SocketClient.sendSensation(sensation=sensation, sock=self.sock, address=self.address)

    '''
    method for sending a sensation
    '''
        
    def sendSensation(self, sensation, sock, address):
        self.log('SocketClient.sendSensation')
        ok = True
        
        if sensation.isReceivedFrom(self.getHost()) or \
          sensation.isReceivedFrom(self.getSocketServer().getHost()):
            self.log('socketClient.sendSensation asked to send sensation back to sensation original host. We Don\'t recycle it!')
        else:
            bytes = sensation.bytes()
            length =len(bytes)
            length_bytes = length.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
    
            try:
                l = sock.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
                if Sensation.SEPARATOR_SIZE == l:
                    print('SocketClient wrote separator to ' + str(address))
                else:
                    print("SocketClient length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
                    ok = False
            except Exception as err:
                self.log("SocketClient error writing Sensation.SEPARATOR to " + str(address)  + " error " + str(err))
                ok=False
            if ok:
                try:
                    l = sock.send(length_bytes)                            # message length section
                    print("SocketClient wrote length " + str(length) + " of Sensation to " + str(address))
                except Exception as err:
                    self.log("SocketClient error writing length of Sensation to " + str(address) + " error " + str(err))
                    ok = False
                if ok:
                    try:
                        l = sock.send(bytes)                              # message data section
                        self.log("SocketClient wrote Sensation to " + str(address))
                        if length != l:
                            print("SocketClient length " + str(l) + " != " + str(length) + " error writing to " + str(address))
                            ok = False
                    except Exception as err:
                        self.log("SocketClient error writing Sensation to " + str(address) + " error " + str(err))
                        ok = False
            if sensation.getSensationType() == Sensation.SensationType.Voice:
                self.log("run: SocketClient Voice sensation")
            else:
                self.log("run: SocketClient wrote sensation " + sensation.toDebugStr())
        return ok

    '''
    Method for stopping remote host
    and after that us
    '''
    def stop(self):
        self.log("stop") 
        self.sendSensation(sensation=Sensation(sensationType = Sensation.SensationType.Stop), sock=self.sock, address=self.address)
        self.running = False
        self.mode = Sensation.Mode.Stopping
        self.sock.close()
        
        super(SocketClient, self).stop()

    '''
    Global method for stopping remote host
    '''
    def sendStop(self, sock, address):
        self.log("stop") 
        print("SocketClient: stop(sock, address") 
        self.sendSensation(sensation=Sensation(sensationType = Sensation.SensationType.Stop), sock=sock, address=address)

class SocketServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 sock, 
                 address,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0,
                 socketClient = None):

        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in SocketServer, not Robot")
        self.sock=sock
        self.address=address
        self.socketClient = socketClient
        self.name = 'SocketServer:' + str(address)
        
    def getHost(self):
        return self.address[0]
       
    def setSocketClient(self, socketClient):
        self.socketClient = socketClient
    def getSocketClient(self):
        return self.socketClient
    
    def run(self):
        self.running=True
        self.mode = Sensation.Mode.Normal
        self.log("run: Starting")
        
        # starting other threads/senders/capabilities
        
        # if we don't know our capabilities, we should ask them
        # Wed can't talk to out  host direction, but client can,
        # so we ask it to do the job
#         if self.getCapabilities() is None and self.socketClient is not None:
#             self.socketClient.askCapabilities()
 
        while self.running:
            self.log("run: waiting next Sensation from" + str(self.address))
            synced = False
            self.data = self.sock.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
            if len(self.data) == 0:
                synced = True# Test
            while not synced and self.running:
                if len(self.data) == len(Sensation.SEPARATOR):
                    if self.data[0] is Sensation.SEPARATOR[0]:    # this also syncs to next message, if we get sock transmit errors
                        synced = True
                if not synced:
                    self.data = self.sock.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
                    #print "WalleSocketServer separator l " + str(len(self.data)) + ' ' + str(len(Sensation.SEPARATOR))
                    if len(self.data) == 0:
                        self.running = False               

            if synced and self.running:
                self.log("run: waiting size of next Sensation from " + str(self.address))
                self.data = self.sock.recv(Sensation.NUMBER_SIZE)                         # message length section
                if len(self.data) == 0:
                    self.running = False
                else:
                    length_ok = True
                    try:
                        sensation_length = int.from_bytes(self.data, Sensation.BYTEORDER)
                    except:
                        self.log("run: SocketServer Client protocol error, no valid length resyncing " + str(self.address) + " wrote " + self.data)
                        length_ok = False
                        
                    if length_ok:
                        self.log("run: SocketServer Client " + str(self.address) + " wrote " + str(sensation_length))
                        self.data=None
                        while sensation_length > 0:
                            data = self.sock.recv(sensation_length)                       # message data section
                            if len(data) == 0:
                                self.running = False
                            else:
                                if self.data is None:
                                    self.data = data
                                else:
                                    self.data = self.data+data
                                sensation_length = sensation_length - len(data)
                        if self.running:
                            sensation=Sensation(bytes=self.data)
                            sensation.addReceived(self.getHost())  # remember route
                            if sensation.getSensationType() == Sensation.SensationType.Capability:
                                self.log("run: SocketServer got Capability sensation " + sensation.getCapabilities().toDebugString('SocketServer'))
                                self.process(sensation)
                            else:
                                self.log("run: SocketServer got sensation " + sensation.toDebugStr())
                                if sensation.getSensationType() == Sensation.SensationType.Voice:
                                    self.log("run: SocketServer got Voice sensation")
                                self.getParent().getParent().getAxon().put(sensation) # write sensation to TCPServers Parent, because TCPServer does not read its Axon
                                if sensation.getSensationType() == Sensation.SensationType.Voice:
                                    self.log("run: SocketServer got Voice sensation")
            

        self.sock.close()

    def stop(self):
        self.log("stop")
        self.getSocketClient().sendStop(sock = self.sock, address=self.address)
        self.running = False
        self.mode = Sensation.Mode.Stopping
        self.sock.close()

        super(SocketServer, self).stop()


def threaded_server(arg):
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print ("threaded_server: starting server")
    arg.serve_forever()
    print ("threaded_server: arg.serve_forever() ended")

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    print ("do_server: create MainRobot")
    global mainRobot
    mainRobot = MainRobot()

    succeeded=True
    try:
        mainRobot.start()
#         for virtailInstace in mainRobot.GetVirtailInstaces():
#             virtailInstace.start()
        
    except Exception: 
        print ("do_server: sock error, " + str(e) + " exiting")
        succeeded=False

    if succeeded:
        print ('do_server: Press Ctrl+C to Stop')

        MainRobot.mainRobot = mainRobot   # remember mainRobot so
                              # we can stop it in signal_handler   
        mainRobot.join()
        
    print ("do_server exit")
    
def signal_handler(signal, frame):
    print ('signal_handler: You pressed Ctrl+C!')
    
    mainRobot.doStop()
    
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
    
    print ("stop: socket.socket(sock.AF_INET, socket.SOCK_STREAM)")
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
            ok = SocketClient.stop(sock = sock, address=address)
            if ok:
                # Receive data from the server
                print ("stop: sock.recv(1024)")
                received = sock.recv(1024)
                print ('stop: received answer ' + received)
        except Exception as err: 
            print ("stop: sock connect, cannot stop localhost, error " + str(err))
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



