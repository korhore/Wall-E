'''
Created on Feb 24, 2013
Updated on 15.04.2020
@author: reijo.korhonen@gmail.com
'''

import os
import shutil
from threading import Thread, Timer
import time
from enum import Enum
import sys
import signal
import getopt
import daemon
import lockfile
import socket
from PIL import Image as PIL_Image
import importlib
import traceback

from PIL import Image as PIL_Image

from Axon import Axon
from Config import Config, Capabilities
from Sensation import Sensation
from Memory import Memory
from AlsaAudio import Settings as AudioSettings

#from VirtualRobot import VirtualRobot
# from Romeo import Romeo
# from ManualRomeo import ManualRomeo
# from dbus.mainloop.glib import threads_init
# from xdg.IconTheme import theme_cache
# from _ast import Or
# if 'Hearing.Hear' not in sys.modules:
#     from Hearing.Hear import Hear
# if 'Seeing.See' not in sys.modules:
#     from Seeing.See import See

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

HOST = ''
PORT = 2000
ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM

DAEMON=False
START=False
STOP=False
MANUAL=False


class Robot(Thread):
    """
    Base class of Robot.
    
    Robot contzains Robots. Robot is very simple implementation that can handle Sensations and tranfers
    these Sensations to other Robots that ptocess them with their very special skill. Idea is minic a human that has
    organs with ans senses with their dedidicated functionality. Human and Robot have Axons that transfers Sensation
    from Senses to our brain and from our brain to muscles thich will make some functionality.
    
    AlsaMicrophone is an example of Sense-type Robot. AlsaPlöayback is an example of muscle-type Robot.
    
    Organising Robot to contain only  subrobots we produce very flexible architecture
    how we can build different kind functionality to our Robot. Robot6 can work inside one computer
    as a thread. But we have also implemented networking-type Robot, so Robot can work connected together
    with axons also on different sites in different computers and in different virtualized computers etc.
    
    Robot skills are defined as Capabilities. Examples of Capability are Voice and Image. Capability is used with a Direction.
    Direction is related to Main Robot, which is model of pur brain. If Capability 'Voice' Direction is 'In', we are hearing
    and if Direction is 'Out', we are speaking.
    
    All Robot has defined set of Capabilities, skills what it can do. Sense-type Robots produced Sensations that are transferred by
    Axons to MainRobot(brain) -direction our muscle-type Robots that have Cabibilities to make functions like speaking.
    For that we must have another direction concept, Transfer-direction, that tells in what direction Sensation is going
    
    Robot knows its subRobots and it can communicate with its parentRobot with Axon. Subrobots always tell their Capabilities
    to their parent. Now we have an architecture where each Robot knows their subRobots Capabilitys and can transfer sensation to
    all subRobot-direction if some of its sub, sub-sub etc. Robot has a Capabitity to process a Sensation with Capability asked.
    Each Sensations has a Capability, meaning of Sensation and Robot has Capability to process its, so we just check al all subRobot-levels
    which subRobot has Capability and transfer Sensation to that one, which makes same decision, processes Sensation itself
    and/or gives Sensation to its child.
    
    Sensations have Memory-level, Sensory or Long-Term. This mimics our Memory-functions. At sensory level Sansation processing is very fast,
    but Sensations can't have high-level meanings. Robot can have meanings of sensed things like Images or Voices, when we connect those
    little memories together, like out brains do. Meaning in a special SensationType Item, that has on ly oner attribyr, name.
    This is lowest level mean tu give names of thing Robots detects.
    
    Out Brain main physical functionality is process what we see. We borrow this to our Robot. We use Tensorflow to classify what out Robot sees.
    This way we can give names  of thing what Robots has seen, crob subImagesof big Images and find out that Robot has seen for instance 'human' 'table'
    and 'chair' and heard certain voice at that moment.
    
    This a point, where we can start to build intelligence to our Robot. subRobot can be build to process Sensations likke Items, sunImages and Voices.
    WE have made Association-naming subrobot, that connects together Sensations that happen at same moment. For example we have Item named 'Human'
    and Voice-sensation at same moment. We have build also Communnication-naming subRobot that can process Item-Sensations and if it finds one,
    it tries to find out association to a Voice. If it finds out this knd association made before, it speaks it out and listens.
    If it hears a voice as a response, it remembers this and will be very, very happy (Sense a sensationtype 'feeling')
    
    This is a moment we have implemented a Robot that can feel and communicate.
    
    Real examples of Robot-devices.
    - RaspberryPI: we use raspberryPI Camere, mictophone nad playback-devices. RaspberryPi is networkingCapable device so its is connected
      with other Robot-devices
    - Linux-deskstops: we use microphone and coukld use also webcam or other camere devices, but there is not yet camera used but is is easy to do.
      These are devices with powefull processors and a lot of memory, so we run Tensorflow at linux.devices. In prionciple eapberry PI is linux-decioce also
      and in principlr Raspberry PI 3 can run Tensorflow and it does it in practice also, but we have found, that it boots itself if we do so.
      So in out tests we use RsapberryPi and linux-device networked together and having common mind, meaning that all senses arfe shared by
      subRobot-Capability-principle across device border.
    - virtual servers. Thse cand act as Sense-robot or Muscle-level, because they don't have real devices like cameras or licrohones or playback-devices,
      but they casn run Tensorflow and brain-level subRobots like Vonnections and Communication explained above.
    
    
    
    Controls Robot-robot. Robot has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Robot emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.
    External Sensorys are handled using sockets.
    """

    # Robot settings"
    LogLevel = enum(Critical='a', Error='b', Normal='c', Detailed='d', Verbose='e')
    CRITICAL =  'Critical'
    ERROR =     'Error'
    NORMAL =    'Normal'
    DETAILED =  'Detailed'
    VERBOSE =   'Verbose'

    LogLevels={LogLevel.Critical: CRITICAL,
               LogLevel.Error: ERROR,
               LogLevel.Normal: NORMAL,
               LogLevel.Detailed: DETAILED,
               LogLevel.Verbose: VERBOSE}
    LogLevelsOrdered=(
               LogLevel.Critical,
               LogLevel.Error,
               LogLevel.Normal,
               LogLevel.Detailed,
               LogLevel.Verbose)
    
# these should be mentioned first in MainRobot-level
    #presence variables
#     presentItemSensations={}
#     
#     # (Main) Robots identity. All running Robot treads share these
#     #idexes used in communication
#     imageind=0
#     voiceind=0
#     # Features of Robot identity we can show and speak to
#     images=[]
#     voices=[]
#     
    SOCKET_ERROR_WAIT_TIME  =   60.0
    HOST_RECONNECT_MAX_TRIES =  10
    IS_SOCKET_ERROR_TEST =      False
    SOCKET_ERROR_TEST_RATE =    10
    SOCKET_ERROR_TEST_NUMBER =  0
    
#     sharedSensationHosts = []               # hosts with we have already shared our sensations
#     mainRobotInstance = None                # singleton instance
        
   
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT):
        print("Robot 1")
        Thread.__init__(self)
        
        self.time = time.time()
        
        self.mode = Sensation.Mode.Starting
        self.parent = parent
        self.instanceName=instanceName
        if  self.instanceName is None:
            self.instanceName = Config.DEFAULT_INSTANCE
        self.instanceType=instanceType
        self.level=level+1
        
        #idexes used in communication
        self.imageind=0
        self.voiceind=0
        # Features of Robot identity we can show and speak to
        self.images=[]
        self.voices=[]
        
        
        if memory is None:
            self.memory = Memory(robot = self,
                                 maxRss = maxRss,
                                 minAvailMem = minAvailMem)
        else:
            self.memory = memory
        
        self.subInstances = []  # subInstance contain a outAxon we write muscle sensations
                                # for subrobot this axon in inAxon
                                # We ask subInstance to report its Sensations to
                                # inAxon, so our live is reading inAxon
                                # and writing to outAxon, which is created by us
                                # or give in this method
        self.running=False

        print("Robot 2")
        self.config = Config(instanceName=self.instanceName,
                             instanceType=self.instanceType,
                             level=level)   # don't increase level, it has increased yet and Config has its own levels (that are same)
        print("Robot 3")
        self.id = self.config.getRobotId()
        self.capabilities = Capabilities(config=self.config)
        print("Robot 4")
        self.logLevel=self.config.getLogLevel()
        self.setWho(self.config.getWho())
        self.log(logLevel=Robot.LogLevel.Normal, logStr="init robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType() + self.capabilities.toDebugString())
        # global queue for senses and other robots to put sensations to robot
        self.axon = Axon(robot=self)
        #and create subinstances
        for subInstanceName in self.config.getSubInstanceNames():
            self.log(logLevel=Robot.LogLevel.Verbose, logStr="init robot sub instanceName " + subInstanceName)
            robot = self.loadSubRobot(subInstanceName=subInstanceName, level=self.level)
            if robot is not None:
                self.subInstances.append(robot)
            else:
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="init robot sub instanceName " + subInstanceName + " is None")

        for instanceName in self.config.getVirtualInstanceNames():
            robot = VirtualRobot(parent=self,
                          instanceName=instanceName,
                          instanceType=Sensation.InstanceType.Virtual,
                          level=self.level)
            if robot is not None:
                self.subInstances.append(robot)
            else:
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="init robot virtual instanceName " + instanceName + " is None")
                
        # in main robot, set up Long_tem Memory and set up TCPServer
        if self.level == 1:                        
            Robot.mainRobotInstance = self
            self._isMainRobot = True
            
            
            # Robot-level variables are instantiated here
            # (Main) Robots identity. All running Robot treads share these
            #indexes used in communication
            #self.getMemory().presentItemSensations={}
            self.imageind=0
            self.voiceind=0
            # Features of Robot identity we can show and speak to
#             Robot.images=[]
#             Robot.voices=[]
#              
#             Robot.sharedSensationHosts = []         # hosts with we have already shared our sensations
#             
#             Robot.mainRobotInstance = self          # singleton instance
            
            self.getMemory().setMaxRss(self.config.getMaxRss())
            self.getMemory().setMinAvailMem (self.config.getMinAvailMem())
            
            self.getMemory().loadLongTermMemory()
            self.getMemory().CleanDataDirectory()
            
            self.tcpServer=TCPServer(parent=self,
                                     memory=self.getMemory(),
                                     hostNames=self.config.getHostNames(),
                                     instanceName='TCPServer',
                                     instanceType=Sensation.InstanceType.Remote,
                                     level=self.level,
                                     address=(HOST,PORT))
        else:
            self._isMainRobot = False

            
    def getMainRobotInstance():
        return Robot.mainRobotInstance
 
    def isMainRobot (self):
        return self._isMainRobot
 
    def setId(self, id):
        self.id = id
    def getId(self):
        return self.id
    
    def getTime(self):
        return self.time                
                
    def isRunning(self):
        return self.running
        
    def loadSubRobot(self, subInstanceName, level):
        robot = None
        try:
            module = subInstanceName+ '.' + subInstanceName
            imported_module = importlib.import_module(module)
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='init ' + subInstanceName)
#            self.log(logLevel=Robot.LogLevel.Normal, logStr='init ' + subInstanceName)
            robot = getattr(imported_module, subInstanceName)(parent=self,
                                                              memory=self.getMemory(),  # use same memory than self
                                                              instanceName=subInstanceName,
                                                              instanceType= Sensation.InstanceType.SubInstance,
                                                              level=level)
        except ImportError as e:
             self.log(logLevel=Robot.LogLevel.Critical, logStr="Import error, implement " + module + ' to fix this ' + str(e) + ' ' + str(traceback.format_exc()))
             self.log(logLevel=Robot.LogLevel.Critical, logStr="Import error, implement " + module + ' ignored, not initiated or not will be started until corrected!')
        return robot
            
    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent

    def getLevel(self):
        return self.level
    
    def getLogLevel(self):
        return self.logLevel

    def setLogLevel(self, logLevel):
        self.logLevel = logLevel
#     def getLogLevel(self):
#         return self.config.getLogLevel()

    def setWho(self, name):
        self.name = name
    def getWho(self):
        return self.name
    
    def getKind(self):
        return self.config.getKind()

    def getAxon(self):
        return self.axon
       
    def getConfig(self):
        return self.config
    def setConfig(self, config):
        self.config = config
        
    def getConfigFilePath(self):
        return self.config.getConfigFilePath()

    def getInstanceType(self):
        return self.config.getInstanceType
        
    def getSubInstances(self):
        return self.subInstances

    def getCapabilities(self):
        return self.capabilities
    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
 
    '''
    get capabilities that main robot or all Sub,Virtual and Remote instances have
    We traverse to main robot and get orrred capabilities of all subinstances
    '''
    def getMasterCapabilities(self):
        if self.getParent() is not None:
            capabilities =  self.getParent().getLocalMasterCapabilities()
        else:   # we are parent, get our ans subcapalities orred
            capabilities = Capabilities(deepCopy=self.getCapabilities())
            for robot in self.getSubInstances():
                capabilities.Or(robot._getCapabilities())
                                    
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='getMasterCapabilities ' +capabilities.toDebugString())
        return capabilities
    
    def _getCapabilities(self):
        capabilities = Capabilities(deepCopy=self.getCapabilities())
        for robot in self.getSubInstances():
            capabilities.Or(robot._getLocalCapabilities())
                                   
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='_getCapabilities ' +capabilities.toDebugString())
        return capabilities
    '''
    get capabilities that main robot or all Sub and virtual instances have
    We traverse to main robot and get orrred capabilities of all subinstances not remote
    '''
    
    def getLocalMasterCapabilities(self):
        if self.getParent() is not None:
            capabilities =  self.getParent().getLocalMasterCapabilities()
        else:   # we are parent, get our and subcapalities orred
            capabilities = Capabilities(deepCopy=self.getCapabilities())
            for robot in self.getSubInstances():
                if robot.getInstanceType() != Sensation.InstanceType.Remote:
                    capabilities.Or(robot._getLocalCapabilities())
                                    
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='getLocalMasterCapabilities ' +capabilities.toDebugString())
        return capabilities

    def _getLocalCapabilities(self):
        capabilities = Capabilities(deepCopy=self.getCapabilities())
        for robot in self.getSubInstances():
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                capabilities.Or(robot._getLocalCapabilities())
                                    
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='_getLocalCapabilities ' +capabilities.toDebugString())
        return capabilities
       
    '''
    Has this instance this capability
    ''' 
    def hasCapability(self, direction, memoryType, sensationType):
        hasCapalility = False
        if self.is_alive() and self.getCapabilities() is not None:
            hasCapalility = self.getCapabilities().hasCapability(direction, memoryType, sensationType)
            if hasCapalility:
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="hasCapability direction " + str(direction) + " memoryType " + str(memoryType) + " sensationType " + str(sensationType) + ' ' + str(hasCapalility))      
        return hasCapalility
    '''
    Has this instance or at least one of its subinstabces this capability
    ''' 
    def hasSubCapability(self, direction, memoryType, sensationType):
        #self.log(logLevel=Robot.LogLevel.Verbose, logStr="hasSubCapability direction " + str(direction) + " memoryType " + str(memoryType) + " sensationType " + str(sensationType))
        if self.hasCapability(direction, memoryType, sensationType):
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability self has direction ' + str(direction) + ' memoryType ' + str(memoryType) + ' sensationType ' + str(sensationType) + ' True')      
            return True    
        for robot in self.getSubInstances():
            if robot.getCapabilities().hasCapability(direction, memoryType, sensationType) or \
               robot.hasSubCapability(direction, memoryType, sensationType):
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability subInstance ' + robot.getWho() + ' has direction ' + str(direction) + ' memoryType ' + str(memoryType) + ' sensationType ' + str(sensationType) + ' True')      
                return True
        #self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability direction ' + str(direction) + ' memoryType ' + str(memoryType) + ' sensationType ' + str(sensationType) + ' False')      
        return False
   
    def getSubCapabilityInstances(self, direction, memoryType, sensationType):
        robots=[]
        for robot in self.getSubInstances():
            if robot.hasCapability(direction, memoryType, sensationType) or \
                robot.hasSubCapability(direction, memoryType, sensationType) or \
                robot.getInstanceType() == Sensation.InstanceType.Remote:       # append all Remotes so it gets same Memory
                robots.append(robot)
        return robots


    def run(self):
        self.running=True
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run: Starting robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # study own identity
        # starting point of robot is always to study what it knows himself
        if self.isMainRobot():
            self.studyOwnIdentity()
            self.getOwnIdentity()
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()

        if self.isMainRobot():
            # main robot starts tcpServer first so clients gets association
            self.tcpServer.start()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            # if we can't sense, the we wait until we get something into Axon
            # or if we can sense, but there is something in our xon, process it
            if not self.getAxon().empty() or not self.canSense():
                transferDirection, sensation, association = self.getAxon().get()
                # when we get a sensation it is attached to us.
                self.log(logLevel=Robot.LogLevel.Normal, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
                
                # We are main Robot, keep track of presence
#                 if self.isMainRobot():
#                     if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemoryType() == Sensation.MemoryType.Working and\
#                        sensation.getDirection() == Sensation.Direction.Out:
#                        self.tracePresents(sensation)
#     
                self.process(transferDirection=transferDirection, sensation=sensation, association=association)
                sensation.detach(robot=self) # to be sure, MainRobot is not attached to this sensation
                self.log("done sensation.detach(robot=self)")
            else:
                self.sense()
 
        self.mode = Sensation.Mode.Stopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        # main robot starts tcpServer first so clients gets association
        if self.isMainRobot():
            self.log("MainRobot Stopping self.tcpServer " + self.tcpServer.getWho())      
            self.tcpServer.stop()
            
        someRunning = False
        for robot in self.subInstances:
            if robot.isAlive():
                self.log("Robot waits " + robot.getWho() + " stopping")      
                someRunning = True
                break 
        i=0
        while i < 20 and someRunning:
            time.sleep(10)
            someRunning = False
            for robot in self.subInstances:
                if robot.isAlive():
                    self.log("Robot waits " + robot.getWho() + " stopping")      
                    someRunning = True
                    break 
            i = i+1    

        if self.isMainRobot():
            i=0
            while i < 20 and self.tcpServer.isAlive():
                self.log("MainRobot waiting self.tcpServer Stopping " + self.tcpServer.getWho())
                time.sleep(10)
                i = i+1    
            # finally save memories
            self.getMemory().saveLongTermMemory()

        self.log("run ALL SHUT DOWN")      
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run ALL SHUT DOWN")

    '''
    Default implementation can not sense
    Override this when derived into Sense type Robot
    '''        
    def canSense(self):
        return False  
        '''
    Default implementation can not sense
    Override this when derived into Sense type Robot
    '''        
    def sense(self):
        pass    
  
        
    def log(self, logStr, logLevel=LogLevel.Normal):
         if logLevel <= self.getLogLevel():
             print(self.getWho() + ":" + str( self.config.level) + ":" + Sensation.Modes[self.mode] + ": " + logStr)

    def stop(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
        self.log(logLevel=Robot.LogLevel.Verbose, logStr="self.running = False")      
        self.running = False    # this in not real, but we wait for Sensation,
                                # so give  us one stop sensation
        self.log(logLevel=Robot.LogLevel.Verbose, logStr="self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.createSensation(sensationType = Sensation.SensationType.Stop))") 
        # stop sensation
        sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)
        # us,but maybe not send up
        self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None)
        # to the parent also
        if self.getParent() is not None:
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None)


    '''
    DoStop is used to stop server process and its subprocesses (threads)
    Technique is just give Stop Sensation to process.
    With same technique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        # stop sensation
        sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)
        # us,but maybe not send up
        self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None)
        # to the parent also
        if self.getParent() is not None:
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None)
        
    def studyOwnIdentity(self):
        self.mode = Sensation.Mode.StudyOwnIdentity
        self.log(logLevel=Robot.LogLevel.Normal, logStr="My name is " + self.getWho())      
        self.log(logLevel=Robot.LogLevel.Detailed, logStr="My kind is " + str(self.getKind()))      
        if self.isMainRobot():
            self.identitypath = self.config.getIdentityDirPath(self.getKind())
            self.log('My identitypath is ' + self.identitypath)      
            for dirName, subdirList, fileList in os.walk(self.identitypath):
                self.log('Found directory: %s' % dirName)      
                image_file_names=[]
                voice_file_names=[]
                for fname in fileList:
                    self.log('\t%s' % fname)
                    if fname.endswith(".jpg"):# or\
                    # png dows not work yet
                    #fname.endswith(".png"):
                        image_file_names.append(fname)
                    elif fname.endswith(".wav"):
                        voice_file_names.append(fname)
                # images
                for fname in image_file_names:
                    image_path=os.path.join(dirName,fname)
                    sensation_filepath = os.path.join('/tmp/',fname)
                    shutil.copyfile(image_path, sensation_filepath)
                    image = PIL_Image.open(sensation_filepath)
                    image.load()
                    self.images.append(image)
                 # voices
                for fname in voice_file_names:
                    image_path=os.path.join(dirName,fname)
                    sensation_filepath = os.path.join('/tmp/',fname)
                    shutil.copyfile(image_path, sensation_filepath)
                    with open(sensation_filepath, 'rb') as f:
                        data = f.read()
                            
                        # length must be AudioSettings.AUDIO_PERIOD_SIZE
                        remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                        if remainder is not 0:
                            self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) + " correcting " )
                            len_zerobytes = AudioSettings.AUDIO_PERIOD_SIZE - remainder
                            ba = bytearray(data)
                            for i in range(len_zerobytes):
                                ba.append(0)
                            data = bytes(ba)
                            remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                            if remainder is not 0:
                                self.log("Did not succeed to fix!")
                                self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) )
                        self.voices.append(data)
                
    '''
    get our identity
    '''   
    def getOwnIdentity(self):
        self.identitypath = self.config.getIdentityDirPath(self.getKind())
        for dirName, subdirList, fileList in os.walk(self.identitypath):
            self.log('Found directory: %s' % dirName)      
            image_file_names=[]
            voice_file_names=[]
            for fname in fileList:
                self.log('\t%s' % fname)
                if fname.endswith(".jpg"):# or\
                   #fname.endswith(".png"):
                    image_file_names.append(fname)
                elif fname.endswith(".wav"):
                    voice_file_names.append(fname)
            # images
            for fname in image_file_names:
                image_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join('/tmp/',fname)
                shutil.copyfile(image_path, sensation_filepath)
                image = PIL_Image.open(sensation_filepath)
                image.load()
                self.images.append(image)
             # voices
            for fname in voice_file_names:
                image_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join('/tmp/',fname)
                shutil.copyfile(image_path, sensation_filepath)
                with open(sensation_filepath, 'rb') as f:
                    data = f.read()
                        
                    # length must be AudioSettings.AUDIO_PERIOD_SIZE
                    remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                    if remainder is not 0:
                        self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) + " correcting " )
                        len_zerobytes = AudioSettings.AUDIO_PERIOD_SIZE - remainder
                        ba = bytearray(data)
                        for i in range(len_zerobytes):
                            ba.append(0)
                        data = bytes(ba)
                        remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                        if remainder is not 0:
                            self.log("Did not succeed to fix!")
                            self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) )
                    self.voices.append(data)
    

    '''
    In basic class Sensation processing in not implemented, but this the place
    for derived classes to process Sensations and then call this basic
    implementation.
    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memoryType level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    After processing this basic implementation transfers sensation forward.
    If out Direction, then we put Sensation to our parent Axon.
    If in direction, sensation is put to all subinstances Axon that has capability
    to process it.
    
    Parameters
    
    transferDirection is sensation going up to MainBobot or down so leaf Robots
    sensation         Sensation to process
    association       Association - more information how processing should be done
                      optional

        
    '''
            
    def process(self,transferDirection, sensation,  association=None):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: SensationSensationType.Stop')      
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: sensation.getSensationType() == Sensation.SensationType.Capability')      
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: self.setCapabilities(Capabilities(capabilities=sensation.getCapabilities() ' + sensation.getCapabilities().toDebugString('capabilities'))      
            self.setCapabilities(Capabilities(deepCopy=sensation.getCapabilities()))
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: capabilities: ' + self.getCapabilities().toDebugString('saved capabilities'))      
        # sensation going up
        elif transferDirection == Sensation.TransferDirection.Up:
            if self.getParent() is not None: # if sensation is going up  and we have a parent
                self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation))')      
                self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation, association=None)
            else: # we are main Robot
                # check if we have subrobot that has capability to process this sensation
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: self.getSubCapabilityInstances')      
                robots = self.getSubCapabilityInstances(direction=sensation.getDirection(), memoryType=sensation.getMemoryType(), sensationType=sensation.getSensationType())
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='process for ' + sensation.toDebugStr() + ' robots ' + str(robots))
                for robot in robots:
                    if robot.getInstanceType() == Sensation.InstanceType.Remote:
                        # if this sensation comes from sockrServers host
                        if sensation.isReceivedFrom(robot.getHost()) or \
                            sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                            self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getWho() + 'has capability for this, but sensation comes from it self. Don\'t recycle it')
                        else:
                            self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)')
                            robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=None, detach=False) # keep ownerdhip untill sent to all sub Robots
                    else:
                        self.log(logLevel=Robot.LogLevel.Verbose, logStr='Local robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)')
                        # new instance or sensation for process
                        robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=None, detach=False) # keep ownerdhip untill sent to all sub Robots
                #sensation.detach(robot=self) # when sent to subrobots, detach
        # sensation going down
        else:
            # which subinstances can process this
            robots = self.getSubCapabilityInstances(direction=sensation.getDirection(), memoryType=sensation.getMemoryType(), sensationType=sensation.getSensationType())
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getSubCapabilityInstances' + str(robots))
            for robot in robots:
                if robot.getInstanceType() == Sensation.InstanceType.Remote:
                    # if this sensation comes from sockrServers host
                    if sensation.isReceivedFrom(robot.getHost()) or \
                       sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                        self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getWho() + 'has capability for this, but sensation comes from it self. Don\'t recycle it')
                    else:
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(robot=self, sensation)')
                        robot.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation, association=None, detach=False) # keep ownerdhip untill sent to all sub Robots
                else:
                    self.log(logLevel=Robot.LogLevel.Verbose, logStr='Local robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(robot=self, sensation)')
                    robot.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation, association=None, detach=False) # keep ownerdhip untill sent to all sub Robots

        sensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes
# Utilities
#presence in Memory now
#     def tracePresents(self, sensation):
#         # present means pure Present, all other if handled not present
#         # if present sensations must come in order
#         if sensation.getName() in self.getMemory().presentItemSensations and\
#            sensation.getTime() > self.getMemory().presentItemSensations[sensation.getName()].getTime(): 
# 
#             if sensation.getPresence() == Sensation.Presence.Entering or\
#                sensation.getPresence() == Sensation.Presence.Present or\
#                sensation.getPresence() == Sensation.Presence.Exiting:
#                 self.getMemory().presentItemSensations[sensation.getName()] = sensation
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())
#             else:
#                 del self.getMemory().presentItemSensations[sensation.getName()]
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr="Absent " + sensation.getName())
#         # accept only sensation items that are not prensent, but not not in order ones
#         # absetnt sensations don't have any mean at this case
#         elif (sensation.getName() not in self.getMemory().presentItemSensations) and\
#              (sensation.getPresence() == Sensation.Presence.Entering or\
#                sensation.getPresence() == Sensation.Presence.Present or\
#                sensation.getPresence() == Sensation.Presence.Exiting):
#                 self.getMemory().presentItemSensations[sensation.getName()] = sensation
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())
# 
#     def presenceToStr(self):
#         namesStr=''
#         for name, sensation in self.getMemory().presentItemSensations.items():
#             namesStr = namesStr + ' ' + name
#         return namesStr
            
    '''
    Memory functionality
    '''      
    '''
    getters, setters
    '''
        
    def getMemory(self):
        return self.memory
    def setMemory(self, memory):
        self.memory = memory
   
    def getMaxRss(self):
        return self.getMemory.getMaxRss()
    def setMaxRss(self, maxRss):
        self.getMemory.setMaxRss(maxRss)
   
    def getMinAvailMem(self):
        return self.getMemory.getMinAvailMem()
    def setMinAvailMem(self, minAvailMem):
        self.getMemory.setMinAvailMem(minAvailMem)
           
    '''
    Sensation constructor that takes care, that we have only one instance
    per Sensation per number
    
    This is needed if we want handle associations properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constructor
    '''
       
    def createSensation(self,
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = Sensation.SensationType.Unknown,
                 memoryType=Sensation.MemoryType.Sensory,
                 direction=Sensation.Direction.In,
                 who=None,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 filePath='',
                 data=b'',
                 image=None,
                 calibrateSensationType = Sensation.SensationType.Unknown,
                 capabilities = None,                                       # capabilities of sensorys, direction what way sensation go
                 name='',                                                   # name of Item
                 presence=Sensation.Presence.Unknown,                       # presence of Item
                 kind=Sensation.Kind.Normal):                               # Normal kind
        
        return self.getMemory().create(
                 robot=self,
                 associations = associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 direction=direction,
                 who=who,
                 leftPower = leftPower, rightPower = rightPower,
                 azimuth = azimuth,
                 accelerationX=accelerationX, accelerationY = accelerationY, accelerationZ = accelerationZ,
                 hearDirection = hearDirection,
                 observationDirection = observationDirection, observationDistance = observationDistance,
                 filePath = filePath,
                 data = data,
                 image = image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name = name,
                 presence =presence,
                 kind = kind )            
                        
 
# VirtualRobot

# from Robot import Robot
# from Config import Config, Capabilities
# from Sensation import Sensation


class VirtualRobot(Robot):
    from threading import Timer

    SLEEPTIME = 60.0
    SLEEP_BETWEEN_IMAGES = 20.0
    SLEEP_BETWEEN_VOICES = 10.0
    VOICES_PER_CONVERSATION = 4
    COMMUNICATION_INTERVAL=600       # continue 10 mins and then stop
   
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0):
        Robot.__init__(self,
                       memory=None,             # use own memory
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        print("We are in VirtualRobot, not Robot")
        self.identitypath = self.config.getIdentityDirPath(self.getKind())
        self.imageind=0
        self.voiceind=0
        self.images=[]
        self.voices=[]
        

    def run(self):
        self.running=True
        self.log("run: Starting Virtual Robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType())      
        
           
        # study own identity
        # starting point of robot is always to study what it knows himself
        self.studyOwnIdentity()
        self.getOwnIdentity()
        
        
#         # starting other threads/senders/capabilities
#         for robot in self.subInstances:
#             if robot.getInstanceType() != Sensation.InstanceType.Remote:
#                 robot.start()
        
        self.timer = Timer(interval=VirtualRobot.COMMUNICATION_INTERVAL, function=self.stopRunning)
        self.timer.start()
        
        Robot.run(self) #normal Robot run


#         # live until stopped
#         self.mode = Sensation.Mode.Normal
#         while self.running:
#             # as a leaf sensor robot default processing for sensation we have got
#             # in practice we can get stop sensation
#             if not self.getAxon().empty():  
#                 transferDirection, sensation, association = self.getAxon().get()
#                 self.process(transferDirection=transferDirection, sensation=sensation, association=association)
#             else:
#                 self.sense()
# 
#         self.log("run ALL SHUT DOWN")  
#         
    def stopRunning(self):
        self.running = False   
         
    '''
    get your identity
    '''   
    def getOwnIdentity(self):
        for dirName, subdirList, fileList in os.walk(self.identitypath):
            self.log('Found directory: %s' % dirName)      
            image_file_names=[]
            voice_file_names=[]
            for fname in fileList:
                self.log('\t%s' % fname)
                if fname.endswith(".jpg"):# or\
                   #fname.endswith(".png"):
                    image_file_names.append(fname)
                elif fname.endswith(".wav"):
                    voice_file_names.append(fname)
            # images
            for fname in image_file_names:
                image_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join('/tmp/',fname)
                shutil.copyfile(image_path, sensation_filepath)
                image = PIL_Image.open(sensation_filepath)
                image.load()
                self.images.append(image)

                imageSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, image=image, filePath=sensation_filepath)
                self.log("getOwnIdentity: self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=" + imageSensation.toDebugStr())      
                self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
                imageSensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes
             # voices
            for fname in voice_file_names:
                image_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join('/tmp/',fname)
                shutil.copyfile(image_path, sensation_filepath)
                with open(sensation_filepath, 'rb') as f:
                    data = f.read()
                    
                    # add missing 0 bytes for 
                    # length must be AudioSettings.AUDIO_PERIOD_SIZE
                    remainder = len(data) % (AudioSettings.AUDIO_PERIOD_SIZE*AudioSettings.AUDIO_CHANNELS)
                    if remainder is not 0:
                        self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) + " correcting " )
                        len_zerobytes = (AudioSettings.AUDIO_PERIOD_SIZE*AudioSettings.AUDIO_CHANNELS - remainder)
                        ba = bytearray(data)
                        for i in range(len_zerobytes):
                            ba.append(0)
                        data = bytes(ba)
                        remainder = len(data) % (AudioSettings.AUDIO_PERIOD_SIZE*AudioSettings.AUDIO_CHANNELS)
                        if remainder is not 0:
                            self.log("Did not succeed to fix!")
                            self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE*AudioSettings.AUDIO_CHANNELS) )
                    
                    self.voices.append(data)
                    time.sleep(VirtualRobot.SLEEP_BETWEEN_VOICES)
                    sensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, data=data, filePath=sensation_filepath)
                    self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None) # or self.process
                    self.log("getOwnIdentity: self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=" + sensation.toDebugStr())      
                    sensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes
                 
    '''
    tell your identity
    '''   
    def tellOwnIdentity(self):
        
        image = self.images[self.imageind]
        imageSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, image=image)
        self.log('tellOwnIdentity: self.imageind  ' + str(self.imageind) + ' self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=' + imageSensation.toDebugStr())      
        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None) # or self.process
        self.imageind=self.imageind+1
        if self.imageind >= len(self.images):
            self.imageind = 0
        imageSensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes

        for i in range(VirtualRobot.VOICES_PER_CONVERSATION):          
            time.sleep(VirtualRobot.SLEEP_BETWEEN_VOICES)
            data = self.voices[self.voiceind]
            sensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, data=data)
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None) # or self.process
            self.log("tellOwnIdentity: " + str(self.voiceind) + " self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=" + sensation.toDebugStr())      
            self.voiceind=self.voiceind+1
            if self.voiceind >= len(self.voices):
               self.voiceind = 0
            sensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes

    '''
    We can sense
    We are Sense type Robot
    '''        
    def canSense(self):
        return True 
    
    '''
    sense
    '''
    
    def sense(self):
        if len(self.images) > 0 and len(self.voices) > 0:
            self.tellOwnIdentity()
            time.sleep(VirtualRobot.SLEEPTIME)
        else:
            self.running = False
            
'''
TCPServer functionality

TCPserver is a Robot that gets associations from other Robots behind network
and delivers them to main Robot. This is done as sensation, because main
robot is a robot that reads sensations.
'''
        
class TCPServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    request_queue_size = 5
    #allow_reuse_address = False

    def __init__(self,
                 memory,
                 address,
                 hostNames,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0):

        Robot.__init__(self,
                       memory=memory,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in TCPServer, not Robot")
        self.address=address
        self.setWho('TCPServer: ' + str(address))
        # convert hostnames to IP addresses so same thing has always same name
        self.hostNames = []
        for hostname in hostNames:
            self.hostNames.append(socket.gethostbyname(hostname))

        self.log('__init__: creating socket' )
        self.sock = socket.socket(family=ADDRESS_FAMILY,
                                  type=SOCKET_TYPE)
        self.sock.setblocking(True)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketServers = []
        self.socketClients = []
        self.running=False
       
    def run(self):
        self.log('run: Starting')
               
        self.running=True
        self.mode = Sensation.Mode.Normal
          
        try:
            self.log('run: bind '+ str(self.address))
            self.sock.bind(self.address)
            self.server_address = self.sock.getsockname()
            self.sock.listen(self.request_queue_size)
            
            self.log("TCPServer for hostName in self.hostNames")
            for hostName in self.hostNames:
                connected = False
                tries=0
                while self.running and not connected and tries < Robot.HOST_RECONNECT_MAX_TRIES:
                    self.log('run: TCPServer.connectToHost ' + str(hostName))
                    connected = self.connectToHost(hostName)

                    if self.running and not connected:
                        self.log('run: TCPServer.connectToHost did not succeed ' + str(hostName) + ' time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)')
                        time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)
                        tries=tries+1
                        
                if self.running:        
                    if connected:
                        self.log('run: self.tcpServer.connectToHost SUCCEEDED to ' + str(hostName))
                    else:
                        self.log('run: self.tcpServer.connectToHost did not succeed FINAL, no more tries to ' + str(hostName))
                else:
                    break
        except Exception as e:
                self.log("run: sock.bind, listen exception " + str(e))
                self.running = False
        
 
        while self.running:
            self.log('run: waiting self.sock.accept()')
            sock, address = self.sock.accept()
            self.log('run: self.sock.accept() '+ str(address))
            if self.running:
                self.log('run: socketServer = self.createSocketServer'+ str(address))
                socketServer = self.createSocketServer(sock=sock, address=address)
                self.log('run: socketClient = self.createSocketClient'+ str(address))
                socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer, tcpServer=self)
                self.log('run: socketServer.setSocketClient(socketClient)'+ str(address))
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
        self.log('run: STOPPED')
        
    '''
    Connect to host by creating SocketClient and SocketServer
    '''
        
    def connectToHost(self, hostName):
        self.log("connectToHost hostName " + hostName)
        address=(hostName, PORT)
        sock = socket.socket(family=ADDRESS_FAMILY,
                             type=SOCKET_TYPE)
                
        connected=False
        try:
            self.log('connectToHost: sock.connect('  + str(address) + ')')
            sock.connect(address)
            connected=True
            self.log('connectToHost: done sock.connect('  + str(address) + ')')
        except Exception as e:
            self.log("connectToHost: sock.connect(" + str(address) + ') exception ' + str(e))
            connected = False
    
        if connected:
            socketServer = self.createSocketServer(sock=sock, address=address)
            socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer, tcpServer=self)
            socketServer.setSocketClient(socketClient)
            # add only socketClients to subInstances, because they give us capabilities
            # but we give capabilities to others with socketServer
            #self.parent.subInstances.append(socketServer)
            self.parent.subInstances.append(socketClient)  # Note to parent subInstances
            socketServer.start()
            time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
            socketClient.start()
            time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
        return connected
        

    def stop(self):
        self.log('stop')
        self.running = False
        self.mode = Sensation.Mode.Stopping
        for socketServer in self.socketServers:
            if socketServer.running:
                self.log('stop: socketServer.stop()')
                socketServer.stop()
        for socketClient in self.socketClients:
            if socketClient.running:
                self.log('stop: socketClient.stop()')
                socketClient.stop()
        # Connect to ourselves as a fake client
        # so server gets association and closes it
        self.log('stop: s.connect(self.address)')
        # Connect to ourselves as a fake client.
        address=('localhost', PORT)
        sock = socket.socket(family=ADDRESS_FAMILY,
                             type=SOCKET_TYPE)
        try:
            self.log('run: sock.connect('  + str(address) + ')')
            sock.connect(address)
            self.log('run: done sock.connect('  + str(address) + ')')
        except Exception as e:
            self.log("run: sock.connect(" + str(address) + ') exception ' + str(e))
 
                   
    def createSocketServer(self, sock, address, socketClient=None):
        self.log('createSocketServer: creating new SocketServer')
        socketServer = SocketServer(parent=self,
                                    memory=self.getMemory(),    # use same memory
                                    instanceName='SocketServer',
                                    instanceType=Sensation.InstanceType.Remote,
                                    level=self.level,
                                    address=address,
                                    sock=sock,
                                    socketClient=socketClient)
        self.socketServers.append(socketServer)
        self.log('createSocketServer: return socketServer')
        return socketServer

    def createSocketClient(self, sock, address, tcpServer, socketServer=None):
        self.log('createSocketClient: creating new SocketClient')
        socketClient = SocketClient(parent=self.parent,
                                    memory=self.getMemory(),    # use same memory
                                    instanceName='SocketClient',
                                    instanceType=Sensation.InstanceType.Remote,
                                    level=self.level,
                                    address=address,
                                    sock=sock,
                                    socketServer=socketServer,
                                    tcpServer=tcpServer)
        self.socketClients.append(socketClient)
        return socketClient

class SocketClient(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 memory,
                 tcpServer,
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
                       memory=memory,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)

        print("We are in SocketClient, not Robot")
        self.tcpServer = tcpServer
        self.sock = sock
        self.address = address
        self.remoteHost=remoteHost
        self.socketServer = socketServer
        if self.sock is None or self.address is None:       
            self.address=(self.remoteHost, PORT)
        self.setWho('SocketClient: '+str(address))
        self.running=False
        self.log("__init__ done")
        
    def getHost(self):
        return self.address[0]

    def setSocketServer(self, socketServer):
        self.socketServer = socketServer
    def getSocketServer(self):
        return self.socketServer

    def run(self):
        self.running=True
        self.mode = Sensation.Mode.Normal
        self.log("run: Starting")
                 
        try:
            # tell who we are, speaking
            sensation=Robot.getMainRobotInstance().createSensation(associations=[], direction=Sensation.Direction.In, sensationType = Sensation.SensationType.Who, who=self.getWho())
            self.log('run: sendSensation(sensation=Sensation(robot=Robot.getMainRobotInstance(),sensationType = Sensation.SensationType.Who), sock=self.sock,'  + str(self.address) + ')')
            self.running =  self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
            sensation.detach(robot=Robot.getMainRobotInstance())
            self.log('run: done sendSensation(sensation=Sensation(robot=Robot.getMainRobotInstance(), sensationType = Sensation.SensationType.Who), sock=self.sock,'  + str(self.address) + ')')
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

                sensation=Robot.getMainRobotInstance().createSensation(associations=[], direction=Sensation.Direction.In, sensationType = Sensation.SensationType.Capability, capabilities=capabilities)
                self.log('run: sendSensation(sensationType = Sensation.SensationType.Capability, capabilities=self.getLocalCapabilities()), sock=self.sock,'  + str(self.address) + ')')
                self.running = self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
                sensation.detach(robot=Robot.getMainRobotInstance())
                self.log('run: sendSensation Sensation.SensationType.Capability done ' + str(self.address) +  ' '  + sensation.getCapabilities().toDebugString('SocketClient'))
        except Exception as e:
            self.log("run: SocketClient.sendSensation exception {}".format(str(e)))
            self.running = False

        # finally normal run from Robot-class
        if self.running:
            super(SocketClient, self).run()

        
        # starting other threads/senders/capabilities

        
    def process(self, transferDirection, sensation, association=None):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        # We can handle only sensation going down transfer-direction
        if transferDirection == Sensation.TransferDirection.Down:
            self.running = self.sendSensation(sensation, self.sock, self.address)
            # if we have got broken pipe -error, meaning that socket writing does not work any more
            # then try to get new association, meaning that ask TCPServer to give us a new open socket
            if not self.running and self.mode == Sensation.Mode.Interrupted:
                self.log('process: interrupted')
                connected = False
                tries=0
                while not connected and tries < Robot.HOST_RECONNECT_MAX_TRIES:
                    self.log('process: interrupted self.tcpServer.connectToHost ' + str(self.getHost()))
                    connected = self.tcpServer.connectToHost(self.getHost())
                    if not connected:
                        self.log('process: interrupted self.tcpServer.connectToHost did not succeed ' + str(self.getHost()) + ' time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)')
                        time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)
                        tries=tries+1
                if connected:
                    self.log('process: interrupted self.tcpServer.connectToHost SUCCEEDED to ' + str(self.getHost()))
                else:
                    self.log('process: interrupted self.tcpServer.connectToHost did not succeed FINAL, no more tries to ' + str(self.getHost()))
                # we are stopped anyway, if we are lucky we have new SocketServer and SocketClient now to our host
                # don't touch anything, if we are reused
        sensation.detach(robot=self) # finally release sent sensation


    '''
    Overwrite local method. This way we can use remote Robot
    same way than local ones.
    
    our server has got capabilities from remote host
    our own capabilities are meaningless
    '''
    def getCapabilities(self):
        if self.getSocketServer() is not None:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='getCapabilities: self.getSocketServer().getCapabilities() ' + self.getSocketServer().getCapabilities().toDebugString('SocketClient Capabilities'))
            return self.getSocketServer().getCapabilities()
        return None

    '''
    Create local method with different name
    We use this to send capabilities to remote
        '''
    def getLocalCapabilities(self):
        return self.capabilities

    '''
    share out knowledge of sensation memory out client has capabilities
       
    This is happening when SocketServer is calling it and we don't know if
    SocketClient is running so best way can be just put all sensations into our Axon
    '''
    def shareSensations(self, capabilities):
        if self.getHost() not in self.getMemory().sharedSensationHosts:
            for sensation in self.getMemory().getSensations(capabilities):
                 self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=None)

            self.getMemory().sharedSensationHosts.append(self.getHost())

    '''
    method for sending a sensation
    '''
        
    def sendSensation(self, sensation, sock, address):
        #self.log('SocketClient.sendSensation')
        ok = True
        
        if sensation.isReceivedFrom(self.getHost()) or \
           sensation.isReceivedFrom(self.getSocketServer().getHost()):
            pass
            #self.log('socketClient.sendSensation asked to send sensation back to sensation original host. We Don\'t recycle it!')
        else:
            sensation.setRobotId(Robot.getMainRobotInstance().getId()) # claim that
                                                                  # all sensation come from Robot
            bytes = sensation.bytes()
            length =len(bytes)
            length_bytes = length.to_bytes(Sensation.ID_SIZE, byteorder=Sensation.BYTEORDER)
    
            try:
                l = sock.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
                if Sensation.SEPARATOR_SIZE == l:
                    pass
                    #self.log('SocketClient.sendSensation wrote separator to ' + str(address))
                else:
                    self.log("SocketClient.sendSensation length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
                    ok = False
            except Exception as err:
                self.log("SocketClient.sendSensation error writing Sensation.SEPARATOR to " + str(address)  + " error " + str(err))
                ok=False
                if self.mode != Sensation.Mode.Normal:  # interrupted (only if not stopping)
                    self.mode = Sensation.Mode.Interrupted
                    self.log("SocketClient.sendSensation self.mode = Sensation.Mode.Interrupted " + str(address))
            ## if we test, then we cause error time by time by us
            if Robot.IS_SOCKET_ERROR_TEST and self.mode == Sensation.Mode.Normal and\
               self.getSocketServer().mode == Sensation.Mode.Normal:
                Robot.SOCKET_ERROR_TEST_NUMBER = Robot.SOCKET_ERROR_TEST_NUMBER+1
                self.log("SocketClient.sendSensation Robot.IS_SOCKET_ERROR_TEST Robot.SOCKET_ERROR_TEST_NUMBER % Robot.SOCKET_ERROR_TEST_RATE: " + str(Robot.SOCKET_ERROR_TEST_NUMBER % Robot.SOCKET_ERROR_TEST_RATE))
                if Robot.SOCKET_ERROR_TEST_NUMBER % Robot.SOCKET_ERROR_TEST_RATE == 0:
                    self.log("SocketClient.sendSensation Robot.IS_SOCKET_ERROR_TEST sock.close()")
                    sock.close()
            if ok:
                try:
                    l = sock.send(length_bytes)                            # message length section
                    #self.log("SocketClient wrote length " + str(length) + " of Sensation to " + str(address))
                except Exception as err:
                    self.log("SocketClient.sendSensation error writing length of Sensation to " + str(address) + " error " + str(err))
                    ok = False
                    if self.mode != Sensation.Mode.Normal:  # interrupted (only if not stopping)
                        self.mode = Sensation.Mode.Interrupted
                        self.log("SocketClient.sendSensation self.mode = Sensation.Mode.Interrupted " + str(address))
                if ok:
                    try:
                        sock.sendall(bytes)                              # message data section
                        #self.log("SocketClient wrote Sensation to " + str(address))
                        self.log("SocketClient.sendSensation wrote sensation " + sensation.toDebugStr() + " to " + str(address))
                        # try to send same sensation only once
                        # TODO maybe not a good idea, id sensation is changed by us
                        sensation.addReceived(self.getHost())
                        sensation.addReceived(self.getSocketServer().getHost())
                    except Exception as err:
                        self.log("SocketClient.sendSensation error writing Sensation to " + str(address) + " error " + str(err))
                        ok = False
                        self.mode = Sensation.Mode.Interrupted
#             if not ok:
#                 # TODO This logic does not work, because sock is bad file descriptor at this point
#                 self.log("send SocketClient error, try to reconnect after sleep ")
#                 time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)
#                 self.log("send: sock.connect(" + str(address) +")")
#                 try:
#                     sock.connect(address)
#                     self.log("send: sock.connect(" + str(address) +") succeeded")
#                     ok = True
#                 except Exception as err:
#                     self.log("SocketClient sock.connect(" + str(address) + ") error " + str(err))
#                     ok = False 
        return ok

    '''
    Method for stopping remote host
    and after that us
    '''
    def stop(self):
        # We should first stop or SocketServer because it is not in Robots subinstaves list
        self.log("stop")
        self.running = False
        self.mode = Sensation.Mode.Stopping
        
        # socketserver can't close itself, just put it to closing mode
        self.getSocketServer().stop() # socketserver can't close itself, we must send a stop sensation to it
        # we must send a stop sensation to it
        sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)
        self.sendSensation(sensation=sensation, sock=self.getSocketServer().getSocket(), address=self.getSocketServer().getAddress())
        # stop remote with same technique
        self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
        sensation.detach(robot=self)
        self.sock.close()
         
        super(SocketClient, self).stop()

    '''
    Global method for stopping remote host
    TODO this does not work, because we don't have self
    '''
    def sendStop(sock, address):
        print("SocketClient.sendStop(sock, address)") 
        sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)

        bytes = sensation.bytes()
        length =len(bytes)
        length_bytes = length.to_bytes(Sensation.ID_SIZE, byteorder=Sensation.BYTEORDER)
    
        ok = True
        try:
            l = sock.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
            if Sensation.SEPARATOR_SIZE == l:
                print('SocketClient.sendStop wrote separator to ' + str(address))
            else:
                print("SocketClient.sendStop length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
                ok = False
        except Exception as err:
            print("SocketClient.sendStop error writing Sensation.SEPARATOR to " + str(address)  + " error " + str(err))
            ok=False
            self.mode = Sensation.Mode.Interrupted
        if ok:
            try:
                l = sock.send(length_bytes)                            # message length section
                print("SocketClient.sendStop wrote length " + str(length) + " of Sensation to " + str(address))
            except Exception as err:
                self.log("SocketClient.sendStop error writing length of Sensation to " + str(address) + " error " + str(err))
                ok = False
            if ok:
                try:
                    l = sock.send(bytes)                              # message data section
                    print("SocketClient.sendStop wrote Sensation to " + str(address))
                    if length != l:
                        print("SocketClient.sendStop length " + str(l) + " != " + str(length) + " error writing to " + str(address))
                        ok = False
                except Exception as err:
                    print("SocketClient.sendStop error writing Sensation to " + str(address) + " error " + str(err))
                    ok = False
                    self.mode = Sensation.Mode.Interrupted
        return ok
        

class SocketServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 memory,
                 sock, 
                 address,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0,
                 socketClient = None):

        Robot.__init__(self,
                       memory=memory,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in SocketServer, not Robot")
        self.sock=sock
        self.address=address
        self.socketClient = socketClient
        self.setWho('SocketServer: ' + str(address))
    
    def getSocket(self):
        return self.sock
    def getAddress(self):
        return self.address
       
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
            ok = True
            while not synced and self.running:
                try:
                    self.data = self.sock.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
                    if len(self.data) == len(Sensation.SEPARATOR) and self.data[0] is Sensation.SEPARATOR[0]:
                        synced = True
                        ok = True
                except Exception as err:
                    self.log("self.sock.recv SEPARATOR " + str(self.address) + " error " + str(err))
                    self.running = False
                    ok = False
                    self.mode = Sensation.Mode.Interrupted   
            if synced and self.running:
                # message length section
                self.log("run: waiting size of next Sensation from " + str(self.address))
                # we can get id of sensation in many pieces
                sensation_length_length = Sensation.ID_SIZE
                self.data = None
                while sensation_length_length > 0 and self.running and ok:
                    try:
                        data = self.sock.recv(sensation_length_length)                       # message data section
                        if len(data) == 0:
                            self.running = False
                            ok = False
                        else:
                            if self.data is None:
                                self.data = data
                            else:
                                self.data = self.data+data
                        sensation_length_length = sensation_length_length - len(data)
                    except Exception as err:
                        self.log("run: self.sock.recv(sensation_length_length) Interrupted error " + str(self.address) + " " + str(err))
                        self.running = False
                        ok = False
                        if self.mode != Sensation.Mode.Normal:  # interrupted (only if not stopping)
                            self.mode = Sensation.Mode.Interrupted
                if ok:
                    length_ok = True
                    try:
                        sensation_length = int.from_bytes(self.data, Sensation.BYTEORDER)
                    except Exception as err:
                        self.log("run: SocketServer Client protocol error, no valid length resyncing " + str(self.address) + " wrote " + self.data)
                        length_ok = False
                        synced = False
                                
                    if length_ok:
                        self.log("run: SocketServer Client " + str(self.address) + " wrote " + str(sensation_length))
                        self.data=None
                        while self.running and ok and sensation_length > 0:
                            try:
                                data = self.sock.recv(sensation_length)                       # message data section
                                if len(data) == 0:
                                    self.running = False
                                    ok = False
                                else:
                                    if self.data is None:
                                        self.data = data
                                    else:
                                        self.data = self.data+data
                                sensation_length = sensation_length - len(data)
                            except Exception as err:
                                self.log("run: self.sock.recv(sensation_length) Interrupted error " + str(self.address) + " " + str(err))
                                self.running = False
                                ok = False
                                if self.mode != Sensation.Mode.Normal:  # interrupted (only if not stopping)
                                    self.mode = Sensation.Mode.Interrupted
                        if self.running and ok:
                            sensation=self.createSensation(associations=[], bytes=self.data)
                            sensation.addReceived(self.getHost())  # remember route
                            if sensation.getSensationType() == Sensation.SensationType.Capability:
                                self.log("run: SocketServer got Capability sensation " + sensation.getCapabilities().toDebugString('SocketServer'))
                                self.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None)
                                # share here sensations from our memory that this host has capabilities
                                # We wan't always share our all knowledge with all other robots
                                if self.getSocketClient() is not None:
                                    self.getSocketClient().shareSensations(self.getCapabilities())
                            else:
                                self.log("run: SocketServer got sensation " + sensation.toDebugStr())
                                self.getParent().getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None) # write sensation to TCPServers Parent, because TCPServer does not read its Axon

        try:
            self.sock.close()
        except Exception as err:
            self.log("self.sock.close() " + str(self.address) + " error " + str(err))

    def stop(self):
        self.log("stop")
#         self.getSocketClient().sendStop(sock = self.sock, address=self.address)
        self.running = False
        self.mode = Sensation.Mode.Stopping
        



def threaded_server(arg):
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print ("threaded_server: starting server")
    arg.serve_forever()
    print ("threaded_server: arg.serve_forever() ended")

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print ("do_server: create Robot")
    global mainRobot
    mainRobot = Robot()

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

        Robot.mainRobot = mainRobot   # remember mainRobot so
                              # we can stop it in signal_handler   
        mainRobot.join()
        
    print ("do_server exit")
    
def signal_handler(signal, frame):
    print ('signal_handler: You pressed Ctrl+C!')
    
    mainRobot.doStop()
    print ('signal_handler: ended!')
#     exit()
    
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
# try system default
#             stdout=open('/tmp/Robot_Server.stdout', 'w+')
#             stderr=open('/tmp/Robot_Server.stderr', 'w+')
            #remove('/var/run/Robot_Server.pid.lock')
            pidfile=lockfile.FileLock('/var/run/Robot.pid')
            cwd = os.getcwd()   #work at that directory we are when calling this
                                # We have data and config directories there
                                # so it is important where we are

            with daemon.DaemonContext(working_directory=cwd,
# try ststem default
#                                       stdout=stdout,
#                                       stderr=stderr,
                                      pidfile=pidfile):
                do_server()
        else:
            do_server()
            print ("start: stopped")

    
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
            print ("stop: SocketClient.stop(sock = sock, address=address)")
            # TODO This does not worn, because SocketClient.sendStop is broken, because it needs self and it is not global
            ok = SocketClient.sendStop(sock = sock, address=address)
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
    #RobotRequestHandler.romeo = None    # no romeo device association yet
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
    print ("__main__ exit has been done so this should not be printed")
                