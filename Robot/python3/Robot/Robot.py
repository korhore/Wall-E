'''
Created on Feb 24, 2013
Updated on 14.12.2021
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
import random
import tempfile

from PIL import Image as PIL_Image

from Axon import Axon
from Config import Config, Capabilities
from Sensation import Sensation
from Memory import Memory
from AlsaAudio import Settings as AudioSettings
#from syntaxnet.tensorflow.tensorflow.python.ops.linalg_ops import self_adjoint_eig

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Robot(Thread):
    """
    Base class of Robot.
    
    Robot contains Robots. Robot is very simple implementation that can handle Sensations and transfers
    these Sensations to other Robots that process them with their very special skill. Idea is mimic a human that has
    organs, muscles  and senses with their dedicated functionality. Human and Robot have Axons that transfers Sensation
    from Senses to our brain and from our brain to muscles which will make some functionality.
    
    AlsaMicrophone is an example of Sense-type Robot. AlsaPlöayback is an example of muscle-type Robot.
    
    Organising Robot to contain only  subrobots we produce very flexible architecture
    how we can build different kind functionality to our Robot. Robot6 can work inside one computer
    as a thread. But we have also implemented networking-type Robot, so Robot can work connected together
    with axons also on different sites in different computers and in different virtualized computers etc.
    
    Robot skills are defined as Capabilities. Examples of Capability are Voice and Image. Capability is used with a Robot Type.
    Robot Type is related to Main Robot, which is model of pour brain. If Capability 'Voice' Direction is 'Sense', we are hearing
    and if Robot Type  'Muscle', we are speaking.
    
    All Robot has defined set of Capabilities, skills what it can do. Sense-type Robots produced Sensations that are transferred by
    Axons to MainRobot(brain) -robotType our muscle-type Robots that have Capabilities to make functions like speaking.
    For that we must have another robotType concept, Transfer-robotType, that tells in what robotType Sensation is going
    
    Robot knows its subRobots and it can communicate with its parentRobot with Axon. Subrobots always tell their Capabilities
    to their parent. Now we have an architecture where each Robot knows their subRobots Capabilitys and can transfer sensation to
    all subRobot-robotType if some of its sub, sub-sub etc. Robot has a Capability to process a Sensation with Capability asked.
    Each Sensations has a Capability, meaning of Sensation and Robot has Capability to process its, so we just check al all subRobot-levels
    which subRobot has Capability and transfer Sensation to that one, which makes same decision, processes Sensation itself
    and/or gives Sensation to its child.
    
    Sensations have Memory-level, Sensory or Long-Term. This mimics our Memory-functions. At sensory level Sensation processing is very fast,
    but Sensations can't have high-level meanings. Robot can have meanings of sensed things like Images or Voices, when we connect those
    little memories together, like out brains do. Meaning in a special SensationType Item, that has only oner attribute, name.
    This is lowest level mean to give names of thing Robots detects.
    
    Out Brain main physical functionality is process what we see. We borrow this to our Robot. We use Tensorflow to classify what out Robot sees.
    This way we can give names  of thing what Robots has seen, crop subImagesof big Images and find out that Robot has seen for instance 'human' 'table'
    and 'chair' and heard certain voice at that moment.
    
    This a point, where we can start to build intelligence to our Robot. subRobot can be build to process Sensations likke Items, sunImages and Voices.
    WE have made Association-naming subrobot, that connects together Sensations that happen at same moment. For example we have Item named 'Human'
    and Voice-sensation at same moment. We have build also Communication-naming subRobot that can process Item-Sensations and if it finds one,
    it tries to find out association to a Voice. If it finds out this kind association made before, it speaks it out and listens.
    If it hears a voice as a response, it remembers this and will be very, very happy (Sense a SensationYype 'feeling')
    
    This is a moment we have implemented a Robot that can feel and communicate.
    
    Real examples of Robot-devices.
    - RaspberryPI: we use raspberryPI Camers, microphone and playback-devices. RaspberryPi is networkingCapable device so its is connected
      with other Robot-devices
    - Linux-desktops: we use microphone and could use also webcam or other camera devices, but there is not yet camera used but is is easy to do.
      These are devices with powerful processors and a lot of memory, so we run Tensorflow at linux.devices. In principle raspberry PI is linux-device also
      and in principle Raspberry PI 3 can run Tensorflow and it does it in practice it runs LITE version, but we have found, that it boots itself if we do so
      with non LITE Tendorflow. But Tensorflow LITE is enough for deteecting objects like 'person'.
      Non LITE Tensorfloflow could be teached to lean detecting new kind objects like Voices, but Robot is not yet ready to do so.
      
      So in out tests we use RsapberryPi and linux-device networked together and having common mind, meaning that all senses are shared by
      subRobot-Capability-principle across device border.
    - virtual servers. These can act as Sense-robot or Muscle-level, because they don't have real devices like cameras or microphones or playback-devices,
      but they can run Tensorflow and brain-level subRobots like Communication explained above.
    
    
    
    Controls Robot-robot. Robot has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Robot emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.
    External Sensorys are handled using sockets.
    """

    # Main Robot settings
    HOST = ''
    PORT = 2000
    ADDRESS_FAMILY = socket.AF_INET
    SOCKET_TYPE = socket.SOCK_STREAM
    
    DAEMON=False
    START=False
    STOP=False
    MANUAL=False
    
    # Robot settings"
    LogLevel = enum(No=-1, Critical=0, Error=1, Normal=2, Detailed=3, Verbose=4)
    NO =        'No'
    CRITICAL =  'Critical'
    ERROR =     'Error'
    NORMAL =    'Normal'
    DETAILED =  'Detailed'
    VERBOSE =   'Verbose'
    
    GLOBAL_LOCATION =   'global'
    GLOBAL_LOCATIONS =  [GLOBAL_LOCATION]
    PAST_LOCATION =   'past'
    PAST_LOCATIONS =  [PAST_LOCATION]
    

    LogLevels={LogLevel.No: NO,
               LogLevel.Critical: CRITICAL,
               LogLevel.Error: ERROR,
               LogLevel.Normal: NORMAL,
               LogLevel.Detailed: DETAILED,
               LogLevel.Verbose: VERBOSE}
    LogLevelsOrdered=(
               LogLevel.No,
               LogLevel.Critical,
               LogLevel.Error,
               LogLevel.Normal,
               LogLevel.Detailed,
               LogLevel.Verbose)
    
    SOCKET_ERROR_WAIT_TIME  =   60.0
    HOST_RECONNECT_MAX_TRIES =  10
    IS_SOCKET_ERROR_TEST =      False
    SOCKET_ERROR_TEST_RATE =    10
    SOCKET_ERROR_TEST_NUMBER =  0
    SOCKETCLIENT_MAX_QUEUE_LENGTH = 512
    STOPWAIT = 5                    # Tries to Stop subRobots and Wait Time
    
    
    ACTIVITE_LOGGING_AVERAGE_PERIOD =       3000.0     # used as period in seconds
    ACTIVITE_LOGGING_SHORT_AVERAGE_PERIOD = 3.0       # used as period in seconds
    ACTIVITE_LOGGING_INTERVAL =             60
    
    FEELING_LOGGING_SHORT_AVERAGE_PERIOD =  5.0      # used as period in feeling times , this is not time dependent
    
    IMAGE_FILENAME_TYPE = ".jpg"
    VOICE_FILENAME_TYPE = ".wav"
   
    def __init__(self,
                 mainRobot,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,             # TODO this is config section for configuration, NOT location
                                            # terminology should be clarified
                                            # and even if this is given, it is always
                                            # overridded first be default value and then by config value if found
                                            # maybe original idea was allow many instances of this Robot with many configurations
                                            # or run same configuration in many locations (inside mainRobot)
                                            # but ideas are confused and mixed
                 config=None):
        print("Robot 1")
        Thread.__init__(self)
        self.logLevel= Robot.LogLevel.No    # We can't log yet
        self.robotState = Sensation.RobotState.RobotStateInitiating
        
        self.daemon = True      # if daemon, all sub Robots are killed, when this one dies.
        
        self.time = time.time()
        
        self.mode = Sensation.Mode.Starting
        self.mainRobot = mainRobot
        self.parent = parent
        self.instanceName=instanceName
        if  self.instanceName is None:
            self.instanceName = Config.DEFAULT_INSTANCE
        self.instanceType=instanceType
        self.level=level+1
        self.location=location
        self.config=config
        # Features of Robot identity we can show and speak to
        self.imageSensations =   None
        self.voiceSensations =   None
        self.locationSensation = None
                                      # Robot has only one location, but it includes radius
                                      # so many Robots can be near each other and see and hear same things
        self.selfImage = None
        
        
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
        self.activityNumber = 0

        print("Robot 2")
        if self.config == None:
            self.config = Config(instanceName=self.instanceName,
                                 instanceType=self.instanceType,
                                 level=level)   # don't increase level, it has increased yet and Config has its own levels (that are same)
            # TODO self.location is marked to default value, so Init_parameter was meaningless
            self.location = Config.DEFAULT_LOCATION
        print("Robot 3")
        # TODO we get configuration always from default section Config.DEFAULT_LOCATIO == 'localhost' 
        # other section in config are meaningless, except 'DEFAULT' because we get default from there, if they are not overridden in 'localhost'
        self.id = self.config.getRobotId(section=self.location)
        self.capabilities = Capabilities(config=self.config, location=self.location)
        print("Robot 4")
        self.setName(self.config.getName(section=self.location))
        
        # self.activityLevel is property of every Robot
        # TODO this variable is not used, but other
        # self.activity* variables

        # self.feeling and self.feelingLevel are propertys of MainRobot and Virtual Robot but how ti doit is TODO
        #
#         self.activityLevel = Sensation.ActivityLevel.Normal
       
        if self.level == 1:                        
            self.mainRobot = self
            self._isMainRobot = True
            self.feeling = Sensation.Feeling.Neutral
            self.feelingLevel = float(Sensation.Feeling.Neutral)
#             self.activityLevel = Sensation.ActivityLevel.Normal
            
            self.getMemory().setMaxRss(self.config.getMaxRss())
            self.getMemory().setMinAvailMem (self.config.getMinAvailMem())
        elif self.getInstanceType() == Sensation.InstanceType.Virtual:#
            # also virtual instance has feeling and activity
            self.feeling = Sensation.Feeling.Neutral
            self.feelingLevel = float(Sensation.Feeling.Neutral)
#             self.activityLevel = Sensation.ActivityLevel.Normal
            
            self._isMainRobot = False
        else:
            self._isMainRobot = False
        self.mainNames = self.config.getMainNames()
        
        
        self.selfSensation=self.createSensation(log=False,
                                                sensationType=Sensation.SensationType.Robot,
                                                memoryType=Sensation.MemoryType.LongTerm,
                                                robotType=Sensation.RobotType.Sense,# We have found this
                                                name = self.getName(),
                                                presence = Sensation.Presence.Present,
                                                kind=self.getKind(),
                                                feeling=self.getFeeling(),
                                                locations=self.config.getLocations())


        # create locationSensation
        self.locationSensation = self.createSensation(log=False,
                                                 memoryType=Sensation.MemoryType.Sensory,
                                                 sensationType=Sensation.SensationType.Location,
                                                 robotType=Sensation.RobotType.Sense,
                                                 locations=self.config.getLocations())
        if not self._isMainRobot:
            parent = self.parent
            # if we don't have mainNames, try to get  one not next of our oarent up
            while (self.mainNames == None or len(self.mainNames) == 0) and\
                  parent != None:
                self.mainNames = parent.getMainNames()
                parent = parent.getParent()
            # TODO We ignore self.selfSensation.locationSensation to avoid infinite loop in logging.
        self.locations = self.config.getLocations()
        self.selfSensation.associate(sensation=self.locationSensation)
        #self.setLocations(self.config.getLocations())
        self.sublocations = self.config.getSubLocations()
        self.uplocations = self.config.getUpLocations()
        self.downlocations = self.config.getDownLocations()

        # at this point we can log
        self.logLevel=self.config.getLogLevel(section=self.location)

        self.log(logLevel=Robot.LogLevel.Normal, logStr="init robot name: " + self.getName() + " location: " + self.getLocationsStr() + " kind: " + self.getKind() + " instanceType: " + self.getInstanceType() + " capabilities: " + self.capabilities.toDebugString(self.getName()))
        # global queue for senses and other robots to put sensations to robot
        self.axon = Axon(robot=self)
        #and create subinstances
        for subInstanceName in self.config.getSubInstanceNames():
            self.log(logLevel=Robot.LogLevel.Normal, logStr="init robot sub instanceName " + subInstanceName)
            robot = self.loadSubRobot(subInstanceName=subInstanceName, level=self.level)
            if robot is not None:
                self.subInstances.append(robot)
            else:
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="init robot sub instanceName " + subInstanceName + " is None")

        for instanceName in self.config.getVirtualInstanceNames():
            robot = Robot(parent=self,
                          instanceName=instanceName,
                          instanceType=Sensation.InstanceType.Virtual,
                          level=self.level)
            if robot is not None:
                self.subInstances.append(robot)
            else:
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="init robot virtual instanceName " + instanceName + " is None")
 
        # create subinstance per location if this is subiinstabce wich has read its condif from file
        # is it has got ins config as parameter, then this is started subinstance, so son't load anything
        # to avoid infinite loop
        if location == None and config == None and self.level > 1 and len(self.sublocations) > 1:
            for location  in self.sublocations:
                self.log(logLevel=Robot.LogLevel.Normal, logStr="init robot sub instanceName " + instanceName + ' location ' + location)
                robot = self.loadSubRobot(subInstanceName=instanceName, level=self.level+1, config=self.config, location=location)
                if robot is not None:
                    self.subInstances.append(robot)
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="init robot sub instanceName " + instanceName + ' location ' + location + " is None")
                       
        # in main robot, set up LongTerm Memory and set up TCPServer
        if self.level == 1:                                                            
            self.getMemory().loadLongTermMemoryFromBinaryFiles()# loadLongTermMemory()
            self.getMemory().CleanDataDirectory()
            
            self.tcpServer=TCPServer(mainRobot=self.getMainRobot(),
                                     parent=self,
                                     memory=self.getMemory(),
                                     hostNames=self.config.getHostNames(),
                                     instanceName='TCPServer',
                                     instanceType=Sensation.InstanceType.Remote,
                                     level=self.level,
                                     address=(Robot.HOST,Robot.PORT))
            self.identity=Identity(mainRobot=self.getMainRobot(),
                                   parent=self,
                                   memory=self.getMemory(),  # use same memory than self
                                   instanceName='Identity',
                                   instanceType= Sensation.InstanceType.SubInstance,
                                   level=level)
            
        elif self.getInstanceType() == Sensation.InstanceType.Virtual:#
            # also virtual instance has identity as level 1 mainrobot
            self.identity=Identity(mainRobot=self.getMainRobot(),
                                   parent=self,
                                   memory=self.getMemory(),  # use same memory than self
                                   instanceName='Identity',
                                   instanceType= Sensation.InstanceType.SubInstance,
                                   level=level)

    '''
    When subInstance is ens, its's last method is to call it's mainRobot this method.
    We cam release its resources, when it is stopped
    '''            
    def subInstanceEnded(self, robot):
        if robot in self.subInstances:
            del self.subInstances[robot]
            
    def getMainRobot(self):
        return self.mainRobot
 
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
        
    def loadSubRobot(self, subInstanceName, level,
                     location=None,
                     config=None):
        robot = None
        try:
            module = subInstanceName+ '.' + subInstanceName
            imported_module = importlib.import_module(module)
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='init ' + subInstanceName)
            robot = getattr(imported_module, subInstanceName)(
                                                              mainRobot=self.getMainRobot(),
                                                              parent=self,
                                                              memory=self.getMemory(),  # use same memory than self
                                                              instanceName=subInstanceName,
                                                              instanceType= Sensation.InstanceType.SubInstance,
                                                              level=level,
                                                              location=location,
                                                              config=config)
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
    def getLogLevelString(logLevel):
        return Robot.LogLevels.get(logLevel)
    def getLogLevelStrings():
        return Robot.LogLevels.values()

    def setLogLevel(self, logLevel):
        self.logLevel = logLevel

    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name
    
    def setMainNames(self, mainNames):
#         if self.getInstanceType() == Sensation.InstanceType.SubInstance:
        self.mainNames = mainNames
        self.config.setMainNames(mainNames = mainNames)
    def getMainNames(self):
        return self.mainNames
    def getMainNamesString(self):
        return Sensation.strArrayToStr(self.mainNames)
    
    def setLocations(self, locations):
#         if self.getInstanceType() == Sensation.InstanceType.SubInstance:
        self.locations = locations
        # TODOP test this
        # seems, that there is no sense change locations, but in Robot Yes
        # used in Identification to set TensorflowClassification locations to past, so
        # is does not set any real Item sensations in current time and placed, but in past
        #self.config.setLocations(locations = locations)
    def getLocations(self):
        return self.locations
    def getLocationsStr(self):
        return Sensation.strArrayToStr(self.locations)
 
    def setSubLocations(self, sublocations):
        if self.getInstanceType() == Sensation.InstanceType.SubInstance:
            self.sublocations = sublocations
            self.config.setSubLocations(sublocations = sublocations)
    def getSubLocations(self):
        return self.sublocations
    def getSubLocationsStr(self):
        return Sensation.strArrayToStr(self.sublocations)
    
    def setUpLocations(self, uplocations):
        if self.getInstanceType() == Sensation.InstanceType.SubInstance:
            self.uplocations = uplocations
    def getUpLocations(self):
        return self.uplocations
    def getUpLocationsStr(self):
        return Sensation.strArrayToStr(self.uplocations)
    
    def setDownLocations(self, downlocations):
        if self.getInstanceType() == Sensation.InstanceType.SubInstance:
            self.downlocations = downlocations
    def getDownLocations(self):
        if self.getInstanceType() == Sensation.InstanceType.Remote:
            return self.locations
        return self.downlocations
    def getDownLocationsStr(self):
        return Sensation.strArrayToStr(self.downlocations)
    
    '''
    Is one or more location in one of this Robots set location
    '''
    def isInLocations(self, locations):
        # is no location requirement or Capabilities accepts all, return True
        # in other case test if at least one location match

        # local global is empty locations and it matches if Robots or its MainRobots instancetype is not Remote of Virtual
        # meaning local
        if len(locations) == 0 or len(self.getDownLocations()) == 0:
            if self.getMainRobot() != None and\
               self.getMainRobot().getInstanceType() != Sensation.InstanceType.Remote and\
               self.getMainRobot().getInstanceType() != Sensation.InstanceType.Virtual and\
               self.getInstanceType() != Sensation.InstanceType.Remote and\
               self.getInstanceType() != Sensation.InstanceType.Virtual:
                return True
        
        # global location matches fron Robot or fron Sensation        
        if Robot.GLOBAL_LOCATION in self.getDownLocations() or\
           Robot.GLOBAL_LOCATION in locations:            
            return True

        # Normal case is to check if at least one Robots down location matches        
        for location in locations:
            if location in self.getDownLocations():
                return True
        return False
   
    def getKind(self):
        return self.config.getKind(section=self.location)
    
    def getExposures(self):
        return self.config.getExposures(section=self.location)

    
    '''
    get Feeling of MainRobot
    
    Deprecated, Moving feeling handling To Communication
    '''   
    def getFeeling(self):
        if self.isMainRobot():
            if self.feelingLevel > (Sensation.Feeling.InLove + Sensation.Feeling.Happy)/2.0:
                return Sensation.Feeling.InLove
            elif self.feelingLevel > (Sensation.Feeling.Happy + Sensation.Feeling.Good)/2.0:
                return Sensation.Feeling.Happy
            elif self.feelingLevel > (Sensation.Feeling.Good + Sensation.Feeling.Normal)/2.0:
                return Sensation.Feeling.Good
            elif self.feelingLevel > (Sensation.Feeling.Normal + Sensation.Feeling.Neutral)/2.0:
                return Sensation.Feeling.Normal
            
            elif self.feelingLevel < (Sensation.Feeling.Terrified + Sensation.Feeling.Afraid)/2.0:
                return Sensation.Feeling.Terrified
            elif self.feelingLevel < (Sensation.Feeling.Afraid + Sensation.Feeling.Disappointed)/2.0:
                return Sensation.Feeling.Afraid
            elif self.feelingLevel < (Sensation.Feeling.Disappointed + Sensation.Feeling.Worried)/2.0:
                return Sensation.Feeling.Disappointed
            elif self.feelingLevel < (Sensation.Feeling.Worried + Sensation.Feeling.Neutral)/2.0:
                return Sensation.Feeling.Worried
            
        return Sensation.Feeling.Neutral
    
    def getInstanceType(self):
        return self.instanceType

    def getAxon(self):
        return self.axon
       
    def getConfig(self):
        return self.config
    def setConfig(self, config):
        self.config = config
        
    def getConfigFilePath(self):
        return self.config.getConfigFilePath()

#     def getInstanceType(self):
#         return self.config.getInstanceType
        
    def getSubInstances(self):
        return self.subInstances

    def getCapabilities(self):
        return self.capabilities
    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
 
    '''
    get capabilities that main robot or all Sub,Virtual and Remote instances have
    We traverse to main robot and get orrred capabilities of all subinstances
    
    Method is used only for logging and debugging purposes
    '''
    def getMasterCapabilities(self):
        if self.getParent() is not None:
            capabilities =  self.getParent().getLocalMasterCapabilities()
        else:   # we are parent, get our and subcapalities orred
            capabilities = Capabilities(deepCopy=self.getCapabilities())
            for robot in self.getSubInstances():
                capabilities.Or(robot._getCapabilities())
                                    
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='getMasterCapabilities ' +capabilities.toDebugString(self.getName()))
        return capabilities
    
    def _getCapabilities(self):
        capabilities = Capabilities(deepCopy=self.getCapabilities(), config=self.getCapabilities().config)
        for robot in self.getSubInstances():
            capabilities.Or(robot._getLocalCapabilities())
                                   
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='_getCapabilities ' +capabilities.toDebugString(self.getName()))
        return capabilities
    '''
    get capabilities that main robot or all Sub and virtual instances have
    We traverse to main robot and get orrred capabilities of all subinstances not remote
    '''
    
    def getLocalMasterCapabilities(self):
        if self.getParent() is not None:
            capabilities =  self.getParent().getLocalMasterCapabilities()
        else:   # we are parent, get our and subcapalities orred
            capabilities = Capabilities(deepCopy = self.getCapabilities(), config = self.getCapabilities().config)
            for robot in self.getSubInstances():
                if robot.getInstanceType() != Sensation.InstanceType.Remote:
                    capabilities.Or(robot._getLocalCapabilities())
                                    
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='getLocalMasterCapabilities ' +capabilities.toDebugString(self.getName()))
        return capabilities

    def _getLocalCapabilities(self):
        capabilities = Capabilities(deepCopy = self.getCapabilities(), config = self.getCapabilities().config)
        for robot in self.getSubInstances():
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                capabilities.Or(robot._getLocalCapabilities())
                                    
        self.log(logLevel=Robot.LogLevel.Verbose, logStr='_getLocalCapabilities ' +capabilities.toDebugString(self.getName()))
        return capabilities
    
#############

    '''
    get locations that main robot or all Sub and Virtual instances have
    We traverse to main robot and get orrred locations of all subinstances
    
    TODO
    Remote robots are ignored, so we don't get double TCPServer location back,
    but in future, we should accept all other remotes,
    but caller remote SocketServer and SocketClient

    '''
    def getLocalMasterLocations(self):
        if self.getParent() is not None:
            locations =  self.getParent().getLocalMasterLocations()
        else:   # we are parent, get our and sublocations orred
            locations = self.getDownLocations()
            for robot in self.getSubInstances():
                if robot.getInstanceType() != Sensation.InstanceType.Remote:
                    for location in robot._getLocations():
                        if location not in locations:
                            locations.append(location)
                                    
#         self.log(logLevel=Robot.LogLevel.Verbose, logStr='getMasterLocations ' + str(locations))
        self.log(logLevel=Robot.LogLevel.Normal, logStr='getMasterLocations ' + str(locations))
        return locations
    
    def _getLocations(self):
        locations = self.getDownLocations()
        for robot in self.getSubInstances():
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                for location in robot._getLocations():
                    if location not in locations:
                        locations.append(location)
                                  
#         self.log(logLevel=Robot.LogLevel.Verbose, logStr='_getLocations ' + str(locations))
        self.log(logLevel=Robot.LogLevel.Normal, logStr='_getLocations ' + str(locations))
        return locations
    
       
    '''
    Has this instance this capability
    ''' 
#    def hasCapability(self, isCommunication, robotType, memoryType, sensationType, locations, mainNames):
    def hasCapability(self, robotType, memoryType, sensationType, locations, mainNames):
        hasCapalility = False
        if self.is_alive() and self.getCapabilities() is not None and\
           self.isInLocations(locations):
#             testRobotType = self.getMainNamesRobotType(isCommunication=isCommunication, robotType=robotType, mainNames=mainNames)
            self.log(logLevel=Robot.LogLevel.Detailed, logStr="hasCapability isInLocations locations " + str(locations) + " self.getDownLocations " + str(self.getDownLocations()))      
            hasCapalility = self.getCapabilities().hasCapability(robotType=robotType, memoryType=memoryType, sensationType=sensationType, acceptAll=self.getInstanceType() != Sensation.InstanceType.Remote)
            # If checked capability RobotType is Communication
            # is exists only if mainNames is nit this Robots MaionNanes
            # meaning that communication goes between Robots, not inside one (Main)Robot
            if robotType == Sensation.RobotType.Communication and self.isInMainNames(mainNames):
                hasCapalility = False
            else:
                hasCapalility = self.getCapabilities().hasCapability(robotType=robotType, memoryType=memoryType, sensationType=sensationType, acceptAll=self.getInstanceType() != Sensation.InstanceType.Remote)                
            if hasCapalility:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr="hasCapability robotType " + str(robotType) + " memoryType " + str(memoryType) + " sensationType " + str(sensationType) + " locations " + str(locations) + ' ' + str(hasCapalility))      
        return hasCapalility
    
    '''
    Reverse robotType in foreign mainName
    if isCommunication
    '''
#     def getMainNamesRobotType(self, isCommunication, robotType, mainNames=None):
#         if isCommunication:
#             if mainNames == None:
#                 mainNames = self.getMainNames()
#             if self.isInMainNames(mainNames):
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr="getMainNamesRobotType {} -> {}".format(robotType,robotType))      
#                 return robotType
#             if robotType == Sensation.RobotType.Muscle:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr="getMainNamesRobotType {} -> {}".format(robotType,Sensation.RobotType.Sense))      
#                 return Sensation.RobotType.Sense
#             self.log(logLevel=Robot.LogLevel.Normal, logStr="getMainNamesRobotType {} -> {}".format(robotType,Sensation.RobotType.Muscle))      
#             return Sensation.RobotType.Muscle
#         return robotType
    
    '''
    Is this Robot at least in one of mainNames
    '''
    def isInMainNames(self, mainNames):
        if mainNames is None:
            self.log(logLevel=Robot.LogLevel.Normal, logStr="isInMainNames mainNames None: True")      
            return True
        for mainName in mainNames:
            if mainName in self.getMainNames():
                self.log(logLevel=Robot.LogLevel.Normal, logStr="isInMainNames {} in {}: True".format(mainName, self.getMainNames()))      
                return True            
        self.log(logLevel=Robot.LogLevel.Normal, logStr="isInMainNames {} not in {}: False".format(mainNames, self.getMainNames()))      
        return False
    
    '''
    Has this instance or at least one of its subinstances this capability
    ''' 
#    def hasSubCapability(self, isCommunication, robotType, memoryType, sensationType, locations, mainNames):
    def hasSubCapability(self, robotType, memoryType, sensationType, locations, mainNames):
        #self.log(logLevel=Robot.LogLevel.Verbose, logStr="hasSubCapability robotType " + str(robotType) + " memoryType " + str(memoryType) + " sensationType " + str(sensationType))
#        if self.hasCapability(isCommunication, robotType, memoryType, sensationType, locations, mainNames):
        if self.hasCapability(robotType, memoryType, sensationType, locations, mainNames):
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability self has robotType ' + str(robotType) + ' memoryType ' + str(memoryType) + ' sensationType ' + str(sensationType) + ' True')      
            return True    
        for robot in self.getSubInstances():
#            if robot.isInLocations(locations) and robot.getCapabilities().hasCapability(isCommunication, robotType, memoryType, sensationType) or \
            if robot.isInLocations(locations) and robot.getCapabilities().hasCapability(robotType, memoryType, sensationType) or \
                robot.hasSubCapability(robotType, memoryType, sensationType, locations, mainNames):
#               robot.hasSubCapability(isCommunication, robotType, memoryType, sensationType, locations, mainNames):
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability subInstance ' + robot.getName() + ' at ' + robot.getLocationsStr() + ' has robotType ' + str(robotType) + ' memoryType ' + str(memoryType) + ' sensationType ' + str(sensationType) + ' True')      
                return True
        #self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability robotType ' + str(robotType) + ' memoryType ' + str(memoryType) + ' sensationType ' + str(sensationType) + ' False')      
        return False

    '''
    return subrobots that have themselves or their subrobots have capabilities requires
    '''   
    def getSubCapabilityInstances(self, robotType, memoryType, sensationType, locations, mainNames):
        robots=[]
        for robot in self.getSubInstances():
            if robot.hasCapability(robotType, memoryType, sensationType, locations, mainNames) or \
               robot.hasSubCapability(robotType, memoryType, sensationType, locations, mainNames): # or \
               #robot.getInstanceType() == Sensation.InstanceType.Remote:       # append all Remotes so it gets same Memory NOPE Bad idea, Robot will process this, not just put to memory
                robots.append(robot)
        return robots

    '''
    return subrobots that have themselves have capabilities requires.
    Owner Robots are not mentioned
    This method is used in star routing
    '''   
    def getCapabilityInstances(self, robotType, memoryType, sensationType, locations, mainNames):
        robots=[]
        if self.hasCapability(robotType, memoryType, sensationType, locations, mainNames):
            robots.append(self)
        for robot in self.getSubInstances():
            if robot.getInstanceType() == Sensation.InstanceType.Virtual:
                virtualSubRobots = robot.getCapabilityInstances(robotType=robotType,
                                                                memoryType=memoryType,
                                                                sensationType=sensationType,
                                                                locations=locations,
                                                                mainNames=mainNames)
                for virtualSubRobot in virtualSubRobots:
                    robots.append(virtualSubRobot)

            else:
                if robot.hasCapability(robotType, memoryType, sensationType, locations, mainNames):
                    robots.append(robot)
        return robots

    def run(self):
        self.running=True
        self.robotState = Sensation.RobotState.RobotStateRunning

        self.log(logLevel=Robot.LogLevel.Normal, logStr="run: Starting robot name " + self.getName() + " kind " + self.getKind() + " instanceType " + self.getInstanceType())      
        
        # study own identity
        # starting point of robot is always to study what it knows himself
        if self.isMainRobot() or self.getInstanceType() == Sensation.InstanceType.Virtual:# or\
            self.studyOwnIdentity()
            self.mode = Sensation.Mode.Starting


        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()

        if self.isMainRobot():
            # main robot starts tcpServer first so clients gets association
            self.tcpServer.start()
            self.identity.start()
        elif self.getInstanceType() == Sensation.InstanceType.Virtual:
            self.identity.start()
            
#         if self.level == 1:
        # activity start values
        self.activityAverage = self.shortActivityAverage = self.config.getActivityAvegageLevel()
        self.activityPeriodStartTime = time.time()

        # and start for MainRobot and VirtualRobot
        if self.isMainRobot() or self.getInstanceType() == Sensation.InstanceType.Virtual:
            self.activityNumber = 0
            self.timer = Timer(interval=Robot.ACTIVITE_LOGGING_INTERVAL, function=self.logActivity)
            self.timer.start()
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        
        self.initRobot()
        while self.running:
            # if we can't sense, the we wait until we get something into Axon
            # or if we can sense, but there is something in our xon, process it
            if not self.getAxon().empty() or not self.canSense():
                transferDirection, sensation = self.getAxon().get(robot=self)
                # when we get a sensation it is attached to us.
                self.log(logLevel=Robot.LogLevel.Normal, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
                
                # We are main Robot, keep track of presence
#                 if self.isMainRobot():
#                     if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemoryType() == Sensation.MemoryType.Working and\
#                        sensation.getRobotType() == Sensation.RobotType.Sense:
#                        self.tracePresents(sensation)
#     
                self.process(transferDirection=transferDirection, sensation=sensation)
                sensation.detach(robot=self) # to be sure, MainRobot is not attached to this sensation
                self.log("done sensation.detach(robot=self)")
            else:
                self.sense()
        self.deInitRobot()
 
        self.mode = Sensation.Mode.Stopping
        self.robotState = Sensation.RobotState.RobotStateStopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")
        if self.isMainRobot() or self.getInstanceType() == Sensation.InstanceType.Virtual:
            self.timer.cancel()
        

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        # main robot starts tcpServer first so clients gets association
        if self.isMainRobot():
            self.log("MainRobot Stopping self.tcpServer " + self.tcpServer.getName())      
            self.tcpServer.stop()
            self.log("MainRobot Stopping self.identity " + self.identity.getName())      
            self.identity.stop()
        elif self.getInstanceType() == Sensation.InstanceType.Virtual:
            self.log("VirtualRobot Stopping self.identity " + self.identity.getName())      
            self.identity.stop()

        someRunning = False
        for robot in self.subInstances:
            if robot.isAlive():
                self.log("Robot waits " + robot.getName() + " stopping")      
                someRunning = True
                break 
        i=0
        while i < Robot.STOPWAIT and someRunning:
            time.sleep(Robot.STOPWAIT)
            someRunning = False
            for robot in self.subInstances:
                if robot.isAlive():
                    self.log("Robot waits " + robot.getName() + " stopping")      
                    someRunning = True
                    break 
            i = i+1    

        if self.isMainRobot():
            i=0
            while i < Robot.STOPWAIT and self.identity.isAlive():
                self.log("MainRobot waiting self.identity Stopping " + self.identity.getName())
                time.sleep(Robot.STOPWAIT)
                i = i+1    
            while i < Robot.STOPWAIT and self.tcpServer.isAlive():
                self.log("MainRobot waiting self.tcpServer Stopping " + self.tcpServer.getName())
                time.sleep(Robot.STOPWAIT)
                i = i+1    
            # finally save memories
            self.getMemory().saveLongTermMemoryToBinaryFiles()#saveLongTermMemory()
        elif self.getInstanceType() == Sensation.InstanceType.Virtual:
            i=0
            while i < Robot.STOPWAIT and self.identity.isAlive():
                self.log("VirtualRobot waiting self.identity Stopping " + self.identity.getName())
                time.sleep(Robot.STOPWAIT)
                i = i+1
            # TODO we have common data directory, but we should have one per Memory
            # Now we can't save virtual Robots memory

        self.log("run ALL SHUT DOWN")      
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run ALL SHUT DOWN")
        self.robotState = Sensation.RobotState.RobotStateStopped
        
    '''
    Overridable method to be run just before
    while self.running:
    loop
    '''
        
    def initRobot(self):
        pass

    '''
    Overridable method to be run just after
    while self.running:
    loop
    '''
        
    def deInitRobot(self):
        pass
        
    '''
    logging activity
    '''
        
    def logActivity(self):
        activityNumber = self.activityNumber 
        for robot in self.getSubInstances():
            activityNumber += robot.getActivityNumber()

        activityLevel = float(activityNumber)/(time.time() - self.activityPeriodStartTime)
        self.log("logActivity activityLevel {} ".format(activityLevel))
        self.activityAverage = ((self.activityAverage * (Robot.ACTIVITE_LOGGING_AVERAGE_PERIOD - 1.0))  + activityLevel)/Robot.ACTIVITE_LOGGING_AVERAGE_PERIOD
        self.log("logActivity activityAverage {} ".format(self.activityAverage))
        self.shortActivityAverage = ((self.activityAverage * (Robot.ACTIVITE_LOGGING_SHORT_AVERAGE_PERIOD - 1.0))  + activityLevel)/Robot.ACTIVITE_LOGGING_SHORT_AVERAGE_PERIOD
        self.log("logActivity shortActivityAverage {} ".format(self.shortActivityAverage))
        self.activityNumber = 0
       # normal
        #self.config.setActivityAvegageLevel(activityLevelAverage = self.activityAverage)
        # to define default level
        self.config.setActivityAvegageLevel(activityLevelAverage = self.activityAverage)
        
        if self.running and self.mode == Sensation.Mode.Normal:
            self.activityPeriodStartTime = time.time()
            self.timer = Timer(interval=Robot.ACTIVITE_LOGGING_INTERVAL, function=self.logActivity)
            self.timer.start()

    '''
    get activityNumber for Robot
    '''
        
    def getActivityNumber(self):
        
        # ignore virtual, it calculates its activity independently by its subRobots
        # ignore Robots that are not running
        if self.getInstanceType() != Sensation.InstanceType.Virtual and\
           self.running and self.mode == Sensation.Mode.Normal:
            activityNumber = self.activityNumber
            for robot in self.getSubInstances():
                    activityNumber = activityNumber + robot.getActivityNumber()
            self.activityNumber = 0
    
            return activityNumber
        
        return 0
        
        
    '''
    get Feeling of MainRobot
    '''   
    def getActivityLevel(self):
        if self.level == 1 and\
           self.activityAverage > 0.0 and\
           self.shortActivityAverage > 0.0:
            # 9 level
            # 1/4 of activity too low, 1/4 too far
            # so we take base = 1/4, which means self.activityAverage/2
            # because self.activityAverage is middle
            base = self.activityAverage/2
            activityLevel = self.activityAverage/9.0 #self.activityAverage/float(len(Sensation.ActivityLevel))
            
            if self.shortActivityAverage < base + 0.5 * activityLevel:
                return Sensation.ActivityLevel.Sleeping
            if self.shortActivityAverage < base + 1.5 * activityLevel:
                return Sensation.ActivityLevel.Dreaming
            if self.shortActivityAverage < base + 2.5 * activityLevel:
                return Sensation.ActivityLevel.Lazy
            if self.shortActivityAverage < base + 3.5 * activityLevel:
                return Sensation.ActivityLevel.Relaxed
            if self.shortActivityAverage > base + 8.5 * activityLevel:
                return Sensation.ActivityLevel.Breaking
            if self.shortActivityAverage > base + 7.5 * activityLevel:
                return Sensation.ActivityLevel.Tired
            if self.shortActivityAverage > base + 6.5 * activityLevel:
                return Sensation.ActivityLevel.Hurry
            if self.shortActivityAverage > base + 5.5 * activityLevel:
                return Sensation.ActivityLevel.Busy
            
        return Sensation.ActivityLevel.Normal

        

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
             print("{}:{}:{}:{}:{}:{}:{}".format(time.ctime(time.time()), self.getMainNamesString(),self.getName(),self.config.level,Sensation.Modes[self.mode],self.getLocationsStr(),logStr), flush=True)

    def stop(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")
        self.robotState = Sensation.RobotState.RobotStateStopping

        if self.running:
             # stop sub instances here, when main instance is not running any more
            for robot in self.subInstances:
                robot.stop()
#             if not self.isMainRobot():
#                 self.getMainRobot().stop()
            self.log(logLevel=Robot.LogLevel.Verbose, logStr="self.running = False")      
            self.running = False    # this in not real, but we wait for Sensation,
                                # so give  us one stop sensation
        # TODO removed temporarely
        # do not stop with sensation
        self.log(logLevel=Robot.LogLevel.Verbose, logStr="self.routet(transferDirection=Sensation.TransferDirection.Up, sensation=self.createSensation(sensationType = Sensation.SensationType.Stop))") 
        # stop sensation
        sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)
        # us,but maybe not send up
        self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        # to the parent also
        if self.getParent() is not None:
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        #self.route(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)

    '''
    doStop is used to stop server process and its subprocesses (threads)
    Technique is just give Stop Sensation to process.
    With same technique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        # stop sensation
        sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)
        # us,but maybe not send up
        self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        # to the parent also
        if self.getParent() is not None:
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        
    def studyOwnIdentity(self):
        self.mode = Sensation.Mode.StudyOwnIdentity
        self.log(logLevel=Robot.LogLevel.Normal, logStr="My name is " + self.getName())
        # What kind we are
        self.log(logLevel=Robot.LogLevel.Detailed, logStr="My kind is " + str(self.getKind()))   

        if self.isMainRobot() or self.getInstanceType() == Sensation.InstanceType.Virtual:
            self.imageSensations, self.voiceSensations = self.getIdentitySensations(name=self.getName())
            if len(self.imageSensations) > 0:
                self.selfImage = self.imageSensations[0].getImage()
            else:
                self.selfImage = None

    def getIdentitySensations(self, name):
        imageSensations=[]
        voiceSensations=[]
        identitypath = self.config.getIdentityDirPath(name)
        self.log('Identitypath for {} is {}'.format(name, identitypath))
        for dirName, subdirList, fileList in os.walk(identitypath):
            self.log('Found directory: %s' % dirName)      
            image_file_names=[]
            voice_file_names=[]
            for fname in fileList:
                self.log('\t%s' % fname)
                if fname.endswith(Robot.IMAGE_FILENAME_TYPE):# or\
                    # png do not work yet
                    #fname.endswith(".png"):
                    image_file_names.append(fname)
                elif fname.endswith(Robot.VOICE_FILENAME_TYPE):
                    voice_file_names.append(fname)
            # images
            for fname in image_file_names:
                image_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join(tempfile.gettempdir(),fname)
                shutil.copyfile(image_path, sensation_filepath)
                image = PIL_Image.open(sensation_filepath)
                image.load()
                # imageSensation memoryType = Sensation.MemoryType.Sensory, because it is needed to process it later, but this can change in future, so maybe it can be given as parameter
                imageSensation = self.createSensation( sensationType = Sensation.SensationType.Image,
                                                       memoryType = Sensation.MemoryType.Sensory,
                                                       robotType = Sensation.RobotType.Sense,
                                                       image=image,
                                                       locations=Robot.PAST_LOCATIONS)
                imageSensations.append(imageSensation)
            # voices
            for fname in voice_file_names:
                voice_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join(tempfile.gettempdir(),fname)
                shutil.copyfile(voice_path, sensation_filepath)
                with open(sensation_filepath, 'rb') as f:
                    data = f.read()
                            
                    # length must be AudioSettings.AUDIO_PERIOD_SIZE
                    remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                    if remainder != 0:
                        self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) + " correcting " )
                        len_zerobytes = AudioSettings.AUDIO_PERIOD_SIZE - remainder
                        ba = bytearray(data)
                        for i in range(len_zerobytes):
                            ba.append(0)
                        data = bytes(ba)
                        remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                        if remainder != 0:
                            self.log("Did not succeed to fix!")
                            self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) )
                    # voiceSensation memoryType = Sensation.MemoryType.LongTerm, because we wan't to remember voice and it is not needed to process it later, but this can change in future, so maybe it can be given as parameter
                    voiceSensation = self.createSensation( associations=[],
                                                           sensationType = Sensation.SensationType.Voice,
                                                           memoryType = Sensation.MemoryType.LongTerm,
                                                           robotType = Sensation.RobotType.Sense,
                                                           data=data,
                                                           locations=Robot.PAST_LOCATIONS)
                    voiceSensations.append(voiceSensation)
                    
        return imageSensations, voiceSensations


                
    

    '''
    #process
    
    Every Robot processes Sensations it gets from its Axon.
    Here, in basic class method are basic processing,
    meaning statistical processing, how hurry this Robots is
    ans handling globals Snsasations, meaning now Stop. When Robot gets
    a Stop-sensatgions, it stops recursively its subRobots and itself.
    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on Sensation.MemoryType
    level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    Typical example is detscting what Items are in a Image. Image-SEnsation
    is Sensory-leval and Item-Sensations are Work level, information that
    is output from Sosory-Sensations.
    
    If there are many assignments to other Sensations with high meaning level,
    also this Sensation is meaningful.
    
    This method rarely gets Sensation.MemoryType.LongTerm Sensation
    to process, but processing itself can create this kiund Sensation as a copy
    which Robot wants to remember.
    
    Processing a Sensation can produce new Sensations that are routed
    to other Robots. It is also possible to create new Sensation, which is
    not routed anywhere now, but further processing of some Robot can find it
    from Memory, when it processes some other Sensation.
    Robots can create momories.When in Longterm level, we process memories.
    Which memories are still important and which memories we should forget.
    
    Finally, this basic implementation is called from this method overridded
    by subRobots.
    
    
    In basic class Sensation processing in not implemented, but this the place
    for derived classes to process Sensations and then call this basic
    implementation.
    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on Sensation.MemoryType
    level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    After processing this basic implementation transfers sensation forward.
    If out Direction, then we put Sensation to our parent Axon.
    If in robotType, sensation is put to all subinstances Axon that has capability
    to process it.
    
    Parameters
    
    transferDirection is sensation going up to MainBobot or down so leaf Robots
    sensation         Sensation to process

        
    '''
            
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())

        # log MainRobot activity
        # log Robot activity
        #if self.level == 1:
        self.activityNumber += 1

         # MainRobot and Virtual robot have Memory
#         if ((sensation.sensationType is Sensation.SensationType.Feeling) and (self.isMainRobot())) or\
#              ((sensation.sensationType is Sensation.SensationType.Feeling) and (self.getInstanceType() == Sensation.InstanceType.Virtual)):

        # TODO FeelingHandling is Deprecated hee and all functionality will be moved to Cpommuninication.
        if sensation.sensationType is Sensation.SensationType.Feeling:
            feeling = self.getMemory().process(sensation=sensation)# process locally
            if feeling is not None:
                self.feelingLevel = ((Robot.FEELING_LOGGING_SHORT_AVERAGE_PERIOD-1.0)/Robot.FEELING_LOGGING_SHORT_AVERAGE_PERIOD) * self.feeling +\
                                    (1.0/Robot.FEELING_LOGGING_SHORT_AVERAGE_PERIOD) * feeling
                newMainRobotFeeling = self.getFeeling()
                if newMainRobotFeeling != self.feeling:
                    self.feeling = newMainRobotFeeling
                    # create plain feeling to all others know this does not assigned to for instance certain Item.name
                    # TODO Study, do we find out, that we feel like something (Sense) or do we wan't to tell that feel something  (Muscle) or both
                    # We choose both now
                    feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                            robotType=Sensation.RobotType.Sense, feeling = self.feeling, locations=self.getUpLocations()) # valid in this location
#                     self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                    self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=feelingSensation)
                    feelingSensation2 = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                            robotType=Sensation.RobotType.Muscle, feeling = self.feeling, locations=self.getUpLocations()) # valid in this location
#                     self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation2)
                    self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=feelingSensation2)
            sensation.detachAll()
                                                           
            # send it to us
            # we should also process this in tcp-connection and Virtual Robots.
            # it is done below by normal route rules
            
        # TODO Stop
        # How to stop

        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: SensationSensationType.Stop')      
            sensation.detachAll()
            self.stop()
            # TODO Robot.LogLevel.Detailed
        elif sensation.getSensationType() == Sensation.SensationType.Capability:
#             self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: sensation.getSensationType() == Sensation.SensationType.Capability')      
#             self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: self.setCapabilities(Capabilities(capabilities=sensation.getCapabilities() ' + sensation.getCapabilities().toDebugString(self.getName()))      
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: sensation.getSensationType() == Sensation.SensationType.Capability')      
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: self.setCapabilities(Capabilities(capabilities=sensation.getCapabilities() ' + sensation.getCapabilities().toDebugString(self.getName()))      
            self.setCapabilities(Capabilities(deepCopy=sensation.getCapabilities()))#, config=sensation.getCapabilities().config))
#             self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: capabilities: ' + self.getCapabilities().toDebugString('saved capabilities'))
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: setCapabilities: ' + self.getCapabilities().toDebugString('saved capabilities'))
            self.setLocations(locations=sensation.getLocations())
#             self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: setLocations: ' + self.getLocationsStr())
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: setLocations: ' + self.getLocationsStr())
            sensation.detachAll()
            
            
        # route to subRobot.process
            
#         self.route(transferDirection=transferDirection, sensation=sensation)

#         # sensation going up
# #         elif transferDirection == Sensation.TransferDirection.Up:
#         elif True:
#             # if sensation is going up  and we have a parent
# #             if self.getParent() is None:
#             if True:
#                 # check if we have subRobot that has capability to process this sensation
#                 #needToDetach=True
#                 self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: self.getSubCapabilityInstances')
# #                robots = self.getSubCapabilityInstances(isCommunication = sensation.getIsCommunication(),
#                 selfSubrobots = self.getCapabilityInstances(robotType=sensation.getRobotType(),
#                                                         memoryType=sensation.getMemoryType(),
#                                                         sensationType=sensation.getSensationType(),
#                                                         locations=sensation.getLocations(),
#                                                         mainNames=sensation.getMainNames())
#                 mainSubrobots = self.getMainRobot().getCapabilityInstances(robotType=sensation.getRobotType(),
#                                                         memoryType=sensation.getMemoryType(),
#                                                         sensationType=sensation.getSensationType(),
#                                                         locations=sensation.getLocations(),
#                                                         mainNames=sensation.getMainNames())
#                 robots = []
#                 for subrobot in selfSubrobots + mainSubrobots:
#                     if not subrobot is self and not subrobot in robots:
#                         robots.append(subrobot)
#                 self.log(logLevel=Robot.LogLevel.Verbose, logStr='process for ' + sensation.toDebugStr() + ' robots ' + str(robots))
#                 if len(robots) == 0:
#                      self.log(logLevel=Robot.LogLevel.Normal, logStr='None robot has capability for this sensation= {})'.format(sensation.toDebugStr()))
#                 # TODO getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation, detach=False)
#                 # logic does not work, so it is removed and we don't keep Sensations ownership, but let all subRobot to get ownership evwn if same
#                 # sensation is sent to many subRobots
#                 for robot in robots:
#                     if robot.getInstanceType() == Sensation.InstanceType.Remote:
#                         # if this sensation comes from sockrServers host
#                         if sensation.isReceivedFrom(robot.getHost()) or \
#                             sensation.isReceivedFrom(robot.getSocketServer().getHost()):
#                             self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getName() + ' has capability for this, but sensation comes from it self. Don\'t recycle it {}'.format(sensation.toDebugStr()))
#                         else:
#                             self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getName() + ' has capability for this, robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation= {})'.format(sensation.toDebugStr()))
#                             robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)#, detach=False) # keep ownerdhip untill sent to all sub Robots
#                             #needToDetach=False
#                     else:
#                         self.log(logLevel=Robot.LogLevel.Detailed, logStr='Local robot ' + robot.getName() + ' has capability for this, robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation= {})'.format(sensation.toDebugStr()))
#                         # new instance or sensation for process
#                         robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)#, detach=False) # keep ownerdhip untill sent to all sub Robots
#                         #needToDetach=False
# #                 if needToDetach:
# #                     sensation.detach(robot=self) # detach if no subRobot found
#             else: # we are subRobot
#                 self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation= {})'.format(sensation.toDebugStr()))      
#                 self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
#         # sensation going down
#         else:
#             # which subRobot can process this
#             #needToDetach=True
#             self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getSubCapabilityInstances')
# #            robots = self.getSubCapabilityInstances(isCommunication = sensation.getIsCommunication(),
#             robots = self.getSubCapabilityInstances(robotType=sensation.getRobotType(),
#                                                     memoryType=sensation.getMemoryType(),
#                                                     sensationType=sensation.getSensationType(),
#                                                     locations=sensation.getLocations(),
#                                                     mainNames=sensation.getMainNames())
#             self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getSubCapabilityInstances' + str(robots))
#             if len(robots) == 0:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='None robot has capability for this sensation= {})'.format(sensation.toDebugStr()))
#             for robot in robots:
#                 if robot.getInstanceType() == Sensation.InstanceType.Remote:
#                     # if this sensation comes from sockrServers host
#                     if sensation.isReceivedFrom(robot.getHost()) or \
#                        sensation.isReceivedFrom(robot.getSocketServer().getHost()):
#                         self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getName() + 'has capability for this, but sensation comes from it self. Don\'t recycle sensation {})'.format(sensation.toDebugStr()))
#                     else:
#                         self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getName() + ' has capability for this, robot.getAxon().put(robot=self, {})'.format(sensation.toDebugStr()))
#                         robot.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)#, detach=False) # keep ownerdhip untill sent to all sub Robots
#                         #needToDetach=False
#                 else:
#                     self.log(logLevel=Robot.LogLevel.Verbose, logStr='Local robot ' + robot.getName() + ' has capability for this, robot.getAxon().put(robot=self, {})'.format(sensation.toDebugStr()))
#                     robot.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)#, detach=False) # keep ownerdhip untill sent to all sub Robots
#                     #needToDetach=False
# #             if needToDetach:
# #                 sensation.detach(robot=self) # detach if no subRobot found
        sensation.detach(robot=self)         # finally detach sensation
 
    '''
    Sensation routing from one Robot to others
    Routing is based on
    - capabilities
    - locations
    - MainNames
    
    Sensation has capability as well Robots has set of capabilities. If Robot has
    asked capability asked be Sensation, it is routed, if also
    locations has match.
    
    MainNames define logcal Robot si if capabilitys and
    location match and also MainNames match, then Sensation is routed also by networ,
    because this is logical Robot working is different computers.
    If SensationType is Communication and MainNames don't mach, this is communication between
    different Robots, so Sensation is routed even if Locations don't match.
    
    In a computer, meaning in one run, there one Robots has stated its subrobots,
    all (sub)Robots route Sensations directly to each other. We get list of (sub)Robots
    from MainRobot which can have its own functionality or it can be just host
    for networking subRobots. Networking subRobots get their copabilities for
    foreign Robots fron network and give their own copabilitis - logical add
    of all SubRobots capabilities - to opposite partt of the connection.
    
    There is also virtualRobot-robottype and it acts as networking Robot. Its
    routing is handled by transferDirection-parameter, so VirtualRobots subRobots
    route their Sensations only to that VirtualRobot. VirtualRobot itself is
    subRobot to MainRobot so their can communicate with each other. Anyway
    virtualRobot is a demo efect,
    

    
    Parameters
    
    sensation         Sensation to route
    isRoutedToParent     True if sensation will be routed only to parent

        
    '''
            
    def route(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Detailed, logStr='route: ' + time.ctime(sensation.getTime()) + ' ' + sensation.toDebugStr())
        self.log(logLevel=Robot.LogLevel.Detailed, logStr='route: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        
        robots = []
        # Route up
        # this version routes directly to this Robots MainRobot and call same method with  Sensation.TransferDirection.Down parameter
        if transferDirection == Sensation.TransferDirection.Up:
            self.getMainRobot().route(transferDirection = Sensation.TransferDirection.Down, sensation=sensation)
            return
        else:
            if transferDirection == Sensation.TransferDirection.Down:
            # transferDirection == Sensation.TransferDirection.Direct
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='route: self.getSubCapabilityInstances')
                robots = self.getCapabilityInstances(robotType=sensation.getRobotType(),
                                                            memoryType=sensation.getMemoryType(),
                                                            sensationType=sensation.getSensationType(),
                                                            locations=sensation.getLocations(),
                                                            mainNames=sensation.getMainNames())
            else:
                # check if we have subRobot that has capability to process this sensation
                #needToDetach=True
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='route: self.getSubCapabilityInstances')
                selfSubrobots = self.getCapabilityInstances(robotType=sensation.getRobotType(),
                                                            memoryType=sensation.getMemoryType(),
                                                            sensationType=sensation.getSensationType(),
                                                            locations=sensation.getLocations(),
                                                            mainNames=sensation.getMainNames())
                mainSubrobots = self.getMainRobot().getCapabilityInstances(robotType=sensation.getRobotType(),
                                                            memoryType=sensation.getMemoryType(),
                                                            sensationType=sensation.getSensationType(),
                                                            locations=sensation.getLocations(),
                                                            mainNames=sensation.getMainNames())
                for subrobot in selfSubrobots + mainSubrobots:
                    if not subrobot is self and not subrobot in robots:
                        robots.append(subrobot)
                        
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='process for ' + sensation.toDebugStr() + ' robots ' + str(robots))
               
            if len(robots) == 0:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr='None robot has capability for this sensation= {})'.format(sensation.toDebugStr()))
            for robot in robots:
                if robot.getInstanceType() == Sensation.InstanceType.Remote:
                    # if this sensation comes from sockrServers host
                    if sensation.isReceivedFrom(robot.getHost()) or \
                        sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getName() + ' has capability for this, but sensation comes from it self. Don\'t recycle it {}'.format(sensation.toDebugStr()))
                    else:
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getName() + ' has capability for this, robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation= {})'.format(sensation.toDebugStr()))
                        robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)#, detach=False) # keep ownerdhip untill sent to all sub Robots
                else:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr='Local robot ' + robot.getName() + ' has capability for this, robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation= {})'.format(sensation.toDebugStr()))
                    # new instance or sensation for process
                    robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)#, detach=False) # keep ownerdhip untill sent to all sub Robots
   
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
                 log=True,
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 
                  # base field are by default None, so we know what fields are given and what not
                 sensationType = None,
                 memoryType = None,
                 robotType = None,
                 robot = None,
#                 isCommunication=False,
                 mainNames = None,                 
                 locations =  None,
                 leftPower = None, rightPower = None,                        # Walle motors state
                 azimuth = None,                                             # Walle robotType relative to magnetic north pole
                 x=None, y=None, z=None, radius=None,                        # location and acceleration of Robot
                 hearDirection = None,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection = None,observationDistance = None,     # Walle's observation of something, relative to Walle
                 filePath = None,
                 data = None,                                                # ALSA voice is string (uncompressed voice information)
                 image = None,                                               # Image internal representation is PIl.Image 
                 calibrateSensationType = None,
                 capabilities = None,                                        # capabilitis of sensorys, robotType what way sensation go
                 name = None,                                                # name of Item
                 score = None,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence = None,                                            # presence of Item
                 kind = None,                                                # kind (for instance voice)
                 firstAssociateSensation = None,                             # associated sensation first side
                 otherAssociateSensation = None,                             # associated Sensation other side
                 feeling = None,                                             # feeling of sensation or association
                 positiveFeeling = None,                                     # change association feeling to more positive robotType if possible
                 negativeFeeling = None,
                 robotState = None):


        
        return self.getMemory().create(
                 log=log,
                 robot=self,
                 associations = associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 robotType=robotType,
                 #robot=robot,
#                 isCommunication=isCommunication,
                 mainNames=mainNames,
                 locations=locations,
                 leftPower = leftPower, rightPower = rightPower,
                 azimuth = azimuth,
                 x=x, y = y, z = z, radius=radius,
                 hearDirection = hearDirection,
                 observationDirection = observationDirection, observationDistance = observationDistance,
                 filePath = filePath,
                 data = data,
                 image = image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name = name,
                 score = score,
                 presence = presence,
                 kind = kind,
                 firstAssociateSensation = firstAssociateSensation,
                 otherAssociateSensation = otherAssociateSensation,
                 feeling = feeling,
                 positiveFeeling=positiveFeeling,
                 negativeFeeling=negativeFeeling,
                 robotState = robotState)

                        
    '''
    Sensation functionality start
    This is wrapper to Sensation provided by real Sensation self.selfSensation
    '''

    '''
    Helper function to update or create an Association
    We support only one Sensation by SensationType
    
    TODO Seems this meyhod is not in use
    '''
    def associate(self,
                  sensation,                                    # sensation to connect
                  time=None,                                    # last used
                  feeling = Sensation.Feeling.Neutral,          # feeling of association two sensations
                  positiveFeeling = False,                      # change association feeling to more positive robotType if possible
                  negativeFeeling = False):                     # change association feeling to more negativee robotType if possible
        selfSensationByType = self.getSelfSensation(sensationType=sensation.getSensationType())
        
        selfSensationByType.setTime(sensation.getTime())
        selfSensationByType.setSensationType(sensation.getSensationType())
        #selfSensationByType.setMemoryType(sensation.getMemoryType()) # setMemoryType is not implemented
        selfSensationByType.setRobotType(sensation.getRobotType())
        selfSensationByType.setFeeling(sensation.getFeeling())

        if sensation.getSensationType() is Sensation.SensationType.Drive:
            selfSensationByType.setLeftPower(sensation.getLeftPower())
            selfSensationByType.setRightPower(sensation.getRightPower())
        elif sensation.getSensationType() is Sensation.SensationType.HearDirection:
            selfSensationByType.setHearDirection(sensation.getHearDirection())
        elif sensation.getSensationType() is Sensation.SensationType.Azimuth:
            selfSensationByType.setAzimuth(sensation.getAzimuth())
        elif sensation.getSensationType() is Sensation.SensationType.Acceleration:
            selfSensationByType.setX(sensation.getX())
            selfSensationByType.setY(sensation.getY())
            selfSensationByType.setZ(sensation.getZ())
        elif sensation.getSensationType() is Sensation.SensationType.Location:
#             selfSensationByType.setX(sensation.getX())
#             selfSensationByType.setY(sensation.getY())
#             selfSensationByType.setZ(sensation.getZ())
#             selfSensationByType.setRadius(sensation.getRadius())
            selfSensationByType.setLocations(sensation.getLocations())
        elif sensation.getSensationType() is Sensation.SensationType.Observation:
            selfSensationByType.setObservationDirection(sensation.getObservationDirection())
            selfSensationByType.setObservationDistance(sensation.getObservationDistance())
        elif sensation.getSensationType() is Sensation.SensationType.Voice:
#             selfSensationByType.setFilePath(sensation.getFilePath())
            selfSensationByType.setData(sensation.getData())
            selfSensationByType.setKind(sensation.getKind())
        elif sensation.getSensationType() is Sensation.SensationType.Image:
#             selfSensationByType.setFilePath(sensation.getFilePath())
            selfSensationByType.setImage(sensation.getImage())
        elif sensation.getSensationType() is Sensation.SensationType.Calibrate:
            selfSensationByType.setHearDirection(sensation.getHearDirection())
            if sensation.getCalibrateSensationType() is Sensation.SensationType.HearDirection:
               selfSensationByType.setHearDirection(sensation.getHearDirection())
        elif sensation.getSensationType() is Sensation.SensationType.Capability:
            selfSensationByType.setCapabilities(sensation.getCapabilities())
            selfSensationByType.setLocations(sensation.getLocations())
        elif sensation.getSensationType() is Sensation.SensationType.Item:
            selfSensationByType.setName(sensation.getName())
            selfSensationByType.setScore(sensation.getScore())
            selfSensationByType.setPresence(sensation.getPresence())
        elif sensation.getSensationType() is Sensation.SensationType.Feeling:
            selfSensationByType.setFirstAssociateSensation(sensation.getFirstAssociateSensation())
            selfSensationByType.setOtherAssociateSensation(sensation.getOtherAssociateSensation())
            selfSensationByType.setPositiveFeeling(sensation.getPositiveFeeling())
            selfSensationByType.setNegativeFeeling(sensation.getNegativeFeeling())
            
        for assosiation in sensation.getAssociations():
            selfSensationByType.associate(sensation=assosiation.getSensation())
            
        selfSensationByType.receivedFrom = sensation.getReceivedFrom()
            
            
    '''
    Helper function to get selfSensation by certain SensationType
    '''
    def getSelfSensation(self, sensationType=None):
        if sensationType is None:
            return self.selfSensation
        for association in self.selfSensation.getAssociations():
            if association.getSensation().getSensationType() == sensationType:
                return association.getSensation()
        # not found, create one with defaults
        sensation = self.createSensation(memoryType=Sensation.MemoryType.Sensory, sensationType = sensationType)
        self.selfSensation.associate(sensation=sensation)
        return sensation
        
        
       
             
'''
Identity Robot 
This sends Our Identity Sensations to other
Robots connected and to Our Awareness also
So they know what kind of eperiences we have.
Experiences determine how we react to things (Item.names)
'''

class Identity(Robot):

    # test
    #SLEEPTIME = 10.0
    # normal
    SLEEPTIME = 60.0
    # test
    #CLASSIFICATION_TIME = 10.0      # can take a long time
    CLASSIFICATION_TIME = 40.0      # can take a long time
    #CLASSIFICATION_TIME = 80.0       # can take a long time
#    SLEEPTIME = 5.0
    #SLEEP_BETWEEN_IMAGES = 20.0
    #SLEEP_BETWEEN_VOICES = 10.0
    SLEEP_BETWEEN_VOICES = 20.0
    VOICES_PER_CONVERSATION = 4
    
    IMAGE_FILENAME_TYPE = ".jpg"
    VOICE_FILENAME_TYPE = ".wav"
  
    def __init__(self,
                 mainRobot,
                 parent,
                 instanceName,
                 level,
                 memory,
                 instanceType = Sensation.InstanceType.SubInstance,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        level=level+1   # don' loop Identitys
        Robot.__init__(self,
                       mainRobot=mainRobot,
                       memory=memory,
#                        isForgettableMemory=False, # when we use other Robots Memory
#                                                   # we can't gorget sensations
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        print("We are in Identity, not Robot")
        
        self.selfImageSensation = None
        self.selfVoiceSensation = None

        self.identitypath = self.config.getIdentityDirPath(self.getParent().getName()) # parent's location, parent's Identity
        self.sleeptime = Identity.SLEEPTIME
        
        self.setLocations(locations=Robot.PAST_LOCATIONS)
        self.setUpLocations(uplocations=Robot.PAST_LOCATIONS)
        

    '''
    get identity sensations
    this handles also exposures
    
    deprecated
    '''

#     def getIdentityExposureSensations(self, name, exposures, feeling):
#         from TensorFlowClassification.TensorFlowClassification import TensorFlowClassification
#         
#         tensorFlowClassification = TensorFlowClassification(mainRobot=self.getMainRobot(),
#                                                             parent=self,
#                                                             privateParent=self,     # note, this guides TensorFlowClassification to send sensations direcly to us instead route
#                                                             memory=self.getMemory(),    # use same memory
#                                                             instanceName='TensorFlowClassification',
#                                                             instanceType= Sensation.InstanceType.SubInstance,
#                                                             level=self.level)
#         tensorFlowClassification.setLocations(Robot.PAST_LOCATIONS)
#         tensorFlowClassification.start()
# 
#         # TODO this way both exposures and local identity are equal, making
#         # equal mess of images and sounds
#         # to be more realistic, we should make real conversations like
#         # we see exposure Item.name assigned to its coice and we answer with our voice
#         # but our Item.names should not be assigned to anything.       
#         names = exposures
#         names.append(name)
#         
#         for name in names:
#             # if  stopped break
#             if not self.running:
#                 break
# 
#             imageSensations=[]
#             
#             identityItemSensations=[]
#             identityImageSensations=[]
#             identityVoiceSensations=[]
#         
#             identitypath = self.config.getIdentityDirPath(name)
#             self.log('{} Identitypath is {}'.format(name, identitypath))
#             for dirName, subdirList, fileList in os.walk(identitypath):
#                 # if  stopped break
#                 if not self.running:
#                     break
#                 self.log('Found directory: %s' % dirName)      
# #                image_file_names=[]
# #                voice_file_names=[]4
#                 for fname in fileList:
#                     # if  stopped break
#                     if not self.running:
#                         break
#                     self.log('\t%s' % fname)
#                     # We must copy original files to /tmp
#                     # because files in Sensation are temporary and
#                     # will be deleted in some point
#                     
#                     if fname.endswith(Robot.IMAGE_FILENAME_TYPE):# or\
#                         # png dows not work yet
#                         #fname.endswith(".png"):
#                         #image_file_names.append(fname)
#                         file_path=os.path.join(dirName,fname)
#                         sensation_filepath = os.path.join(tempfile.gettempdir(),fname)
#                         shutil.copyfile(file_path, sensation_filepath)
#                         image = PIL_Image.open(sensation_filepath)
#                         image.load()
#                         imageSensation = self.createSensation( sensationType = Sensation.SensationType.Image,
#                                                                memoryType = Sensation.MemoryType.Sensory,
#                                                                robotType = Sensation.RobotType.Sense,
#                                                                image = image,
#                                                                location = Robot.PAST_LOCATIONS)
#                         imageSensations.append(imageSensation)
#                         if fname == name + Robot.IMAGE_FILENAME_TYPE:
#                            self.selfImageSensation = imageSensation
#                         
#                         
#                     elif fname.endswith(Robot.VOICE_FILENAME_TYPE):
#  #                       voice_file_names.append(fname)
#                         file_path=os.path.join(dirName,fname)
#                         sensation_filepath = os.path.join(tempfile.gettempdir(),fname)
#                         shutil.copyfile(file_path, sensation_filepath)
#                         with open(sensation_filepath, 'rb') as f:
#                             data = f.read()
#                                     
#                             # length must be AudioSettings.AUDIO_PERIOD_SIZE
#                             remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
#                             if remainder != 0:
#                                 self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) + " correcting " )
#                                 len_zerobytes = AudioSettings.AUDIO_PERIOD_SIZE - remainder
#                                 ba = bytearray(data)
#                                 for i in range(len_zerobytes):
#                                     ba.append(0)
#                                 data = bytes(ba)
#                                 remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
#                                 if remainder != 0:
#                                     self.log("Did not succeed to fix!")
#                                     self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) )
#                             voiceSensation = self.createSensation( associations=[],
#                                                                    sensationType = Sensation.SensationType.Voice,
#                                                                    memoryType = Sensation.MemoryType.LongTerm,
#                                                                    robotType = Sensation.RobotType.Sense,
#                                                                    data=data,
#                                                                    location = Robot.PAST_LOCATIONS)
#                             identityVoiceSensations.append(voiceSensation)
#                             
#                             if fname == name + Robot.VOICE_FILENAME_TYPE:
#                                self.selfVoiceSensation = voiceSensation
#                            
#             # now we need help of TensrlFlowClassification to get subImages and Item.names it can detect
#             isFirstSleep = True
#             self.log('{} Identity imageSensations {}'.format(name, len(imageSensations)))
#             for imageSensation in imageSensations:
#                 # if  stopped break
#                 if not self.running:
#                     break
#                 self.log('{} Identity tensorFlowClassification {}'.format(name, imageSensation.toDebugStr()))
#                 tensorFlowClassification.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation)
#                 # give tensorFlowClassification                
#                 if isFirstSleep:
#                     waitTime =  2*Identity.CLASSIFICATION_TIME       # give Robot some time to process
#                     isFirstSleep=False
#                 else:
#                     waitTime =  Identity.CLASSIFICATION_TIME       # give Robot some time to process
#                 self.log('{} Identity time.sleep({})'.format(name, waitTime))
#                 time.sleep(waitTime)
#                    
#                 self.log('{} Identity slept time.sleep({}) self.getAxon().empty() {}'.format(name, waitTime, self.getAxon().empty()))
#                 while not self.getAxon().empty():
#                     transferDirection, sensation = self.getAxon().get(robot=self)
#                     self.log('{} Identity get from tensorFlowClassification {}'.format(name, sensation.toDebugStr()))
#                     if sensation.getSensationType() == Sensation.SensationType.Image:
#                         self.log('{} Identity get Image from tensorFlowClassification'.format(name))
#                         identityImageSensations.append(sensation)
#                     elif sensation.getSensationType() == Sensation.SensationType.Item and\
#                          sensation.getPresence() == Sensation.Presence.Entering:
#                         self.log('{} Identity get Item from tensorFlowClassification {}'.format(name, sensation.getName()))
#                         identityItemSensations.append(sensation)
#                             
#             for imageSensation in imageSensations:
#                 imageSensation.detach(robot=self)
#                 imageSensation.delete() # NOTE this is not enough, if reimplemented
#                 del imageSensation
#        
#             # now we have 
#             #identityItemSensations
#             #identityImageSensations
#             #identityVoiceSensations
#             # assign them with feeling given.
#                 
#             self.log('{} Identity identityItemSensations {}'.format(name, len(identityItemSensations)))
#             self.log('{} Identity identityImageSensations {}'.format(name, len(identityImageSensations)))
#             self.log('{} Identity identityVoiceSensations {}'.format(name, len(identityVoiceSensations)))
#             for identityItemSensation in identityItemSensations:
#                 self.getMemory().setMemoryType(sensation=identityItemSensation, memoryType=Sensation.MemoryType.LongTerm)
#                 for identityImageSensation in identityImageSensations:
#                     self.getMemory().setMemoryType(sensation=identityImageSensation, memoryType=Sensation.MemoryType.LongTerm)
#                     identityImageSensation.associate(sensation=identityItemSensation, 
#                                                      feeling = feeling)
#                 for identityVoiceSensation in identityVoiceSensations:
#                     identityVoiceSensation.associate(sensation=identityItemSensation, 
#                                                      feeling = feeling)
#             for identityImageSensation in identityImageSensations:
#                 for identityVoiceSensation in identityVoiceSensations:
#                         identityVoiceSensation.associate(sensation=identityImageSensation, 
#                                                          feeling = feeling)
#                         
#         # TODO we have associated each exposure and mainrobot.name, but we haven't associated anything with
#         # mainrobot.name sensations with exposure sensations so this is still
#         # setting identity and for main Robot and each exposure, but they don't communiocate with each other.
#         # should they?
# 
#         tensorFlowClassification.stop()
#         
#         # Finally detach created sensations, because they are memoryries, that can vanich, but are at first ih high priority
#         for sensation in identityItemSensations+identityImageSensations+identityVoiceSensations:
#             sensation.detach(robot=self)


    '''
    get item sensasions from imageSensations sensations
    '''

    def getItemSensations(self, tensorFlowClassification, name, imageSensations):
        itemSensations=[]
        itemImageSensations=[]
        names=[]
        isFirstSleep = True
        self.log('{} Identity imageSensations {}'.format(name, len(imageSensations)))
        for imageSensation in imageSensations:
            # if  stopped break
            if not self.running:
                break
            self.log('Identity tensorFlowClassification {}'.format(imageSensation.toDebugStr()))
            tensorFlowClassification.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation)
            # give tensorFlowClassification                
            if isFirstSleep:
                waitTime =  2*Identity.CLASSIFICATION_TIME       # give Robot some time to process
                isFirstSleep=False
            else:
                waitTime =  Identity.CLASSIFICATION_TIME       # give Robot some time to process
            self.log('{} Identity time.sleep({})'.format(name, waitTime))
            time.sleep(waitTime)
                   
            self.log('Identity slept time.sleep({}) self.getAxon().empty() {}'.format(waitTime, self.getAxon().empty()))
            while not self.getAxon().empty():
                transferDirection, sensation = self.getAxon().get(robot=self)
                self.log('{} Identity get from tensorFlowClassification {}'.format(name, sensation.toDebugStr()))
                if sensation.getSensationType() == Sensation.SensationType.Image:
                    self.log('{} Identity get Image from tensorFlowClassification'.format(name))
                    itemImageSensations.append(sensation)
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Entering:
                    self.log('{} Identity get Item from tensorFlowClassification {}'.format (name,sensation.getName()))
                    if sensation.getName() not in names:
                        names.append(sensation.getName())
                        itemSensations.append(sensation)

        return itemSensations, itemImageSensations


    '''
    Always get  from parent
    STUDY how Robot.PAST_LOCATIONS work
    '''        
    def getLocations(self):
#         return self.getParent().getLocations(self)
        return Robot.PAST_LOCATIONS

    '''
    Always get  from parent
    '''        
    def getUpLocations(self):
#         return self.getParent().getUpLocations(self)
        return Robot.PAST_LOCATIONS
    '''
    Always get  from parent
    '''        
    def getDownLocations(self):
#         return self.getParent().getDownLocations(self)
        return Robot.PAST_LOCATIONS

    def run(self):
        self.running=True
        self.mode = Sensation.Mode.Starting
        self.robotState = Sensation.RobotState.RobotStateRunning

        self.log("run: Starting Identity Robot for name " + self.getParent().getName() + " kind " + self.getKind() + " instanceType " + self.getInstanceType())      
                   
        # wait until started so all others can start first        
        time.sleep(self.sleeptime)
        # prepare Memory once
        # if not stopped
        self.mode = Sensation.Mode.Normal
        if self.running:
            while self.getParent().imageSensations is None or self.getParent().voiceSensations is None:
                self.log("run: Waiting Identity Robot main Robot\'s imaage and voice sensations")      
                time.sleep(self.sleeptime)
                
            # start TensorFlowClassification so we can get Item sensations from imageSensations 
            from TensorFlowClassification.TensorFlowClassification import TensorFlowClassification 
            tensorFlowClassification = TensorFlowClassification(mainRobot=self.getMainRobot(),
                                                                parent=self,
                                                                privateParent=self,         # note, this guides TensorFlowClassification to send sensations direcly to us instead route
                                                                memory=self.getMemory(),    # use same memory
                                                                instanceName='TensorFlowClassification',
                                                                instanceType= Sensation.InstanceType.SubInstance,
                                                                level=self.level)
            tensorFlowClassification.setLocations(Robot.PAST_LOCATIONS)
            tensorFlowClassification.setUpLocations(Robot.PAST_LOCATIONS)
            tensorFlowClassification.start()
            self.getParent().itemSensations, self.getParent().itemImageSensations = self.getItemSensations(tensorFlowClassification=tensorFlowClassification, name = self.getParent().getName(), imageSensations = self.getParent().imageSensations)
            

            # own identity 
            for itemSensation in self.getParent().itemSensations:
                for voiceSensation in self.getParent().voiceSensations:
                    itemSensation.associate(sensation=voiceSensation,feeling = Sensation.Feeling.Neutral)
            # exposures               
            for exposure in self.getParent().getExposures():
                # what images ans voices exposure has
                exposureImageSensations, exposureVoiceSensations = self.getIdentitySensations(name=exposure)
                # what are Item.names and little images for those
                exposureItemSensations, exposureItemImageSensations = self.getItemSensations(tensorFlowClassification=tensorFlowClassification, name = exposure, imageSensations = exposureImageSensations)
                # now mimic situation, where this robot sees exposute Item.name and its littele image and hears its all Voices
                # TODO Item now includes also litle Image, so it is not needed to use little Images.
                for itemSensation in self.getParent().itemSensations:
                    for exposureItemSensation in exposureItemSensations:
                        itemSensation.associate(sensation=exposureItemSensation,feeling = Sensation.Feeling.Neutral)
                        for exposureVoiceSensation in exposureVoiceSensations:
                            # we hear the at once, assign them
                            exposureItemSensation.associate(sensation=exposureVoiceSensation,feeling = Sensation.Feeling.Neutral)
                            itemSensation.associate(sensation=exposureVoiceSensation,feeling = Sensation.Feeling.Neutral)
                            # we answer with all our voices, meaning that we assign it to those
                            for voiceSensation in self.getParent().voiceSensations:
                                exposureItemSensation.associate(sensation=voiceSensation,feeling = Sensation.Feeling.Neutral)
                                exposureVoiceSensation.associate(sensation=voiceSensation,feeling = Sensation.Feeling.Neutral)
                # finally detach exposure sensations, because they are memories that can vanish
                for exposureItemSensation  in exposureItemSensations:
                    self.getMemory().setMemoryType(sensation=exposureItemSensation, memoryType=Sensation.MemoryType.LongTerm)
                    exposureItemSensation .detach(robot=self)
                for exposureVoiceSensation in exposureVoiceSensations:
                    self.getMemory().setMemoryType(sensation=exposureVoiceSensation, memoryType=Sensation.MemoryType.LongTerm)
                    exposureVoiceSensation.detach(robot=self)
                for exposureImageSensation in exposureImageSensations:
                    self.getMemory().setMemoryType(sensation=exposureImageSensation, memoryType=Sensation.MemoryType.LongTerm)
                    exposureImageSensation.detach(robot=self)

            # remember also this Robots identity
            # We will not detach identity, but this robot remembers it for ever
            for itemSensation  in self.getParent().itemSensations:
                self.getMemory().setMemoryType(sensation=itemSensation, memoryType=Sensation.MemoryType.LongTerm)
            for imageSensation in self.getParent().itemImageSensations:
                self.getMemory().setMemoryType(sensation=imageSensation, memoryType=Sensation.MemoryType.LongTerm)
               
            self.robotState = Sensation.RobotState.RobotStateStopping
            #self.getIdentitySensations(name=self.getParent().getName(), exposures=self.getParent().getExposures(), feeling = Sensation.Feeling.Neutral)
            tensorFlowClassification.stop()
            
        # all done        
        self.running=False
        self.mode = Sensation.Mode.Stopping
        self.robotState = Sensation.RobotState.RobotStateStopped


    def stopRunning(self):
        self.running = False   
        self.mode = Sensation.Mode.Stopping
        self.robotState = Sensation.RobotState.RobotStateStopping
       
                 
    '''
    tell your identity
    TODO newer called
         Identity is something that is in main Robots memory
         this is OK,
         but we should handle also exposures
         
    deprecated
    '''   
#     def tellOwnIdentity(self):
#         
#         selfSensation = self.createSensation( associations=[], sensation=self.getParent().selfSensation, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
#                                               locations='') # valid everywhere
#         self.log('tellOwnIdentity: selfSensation self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=' + selfSensation.toDebugStr())      
#         self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=selfSensation) # or self.process
#         selfSensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes
#        
#         imageind = random.randint(0, len(self.getParent().imageSensations)-1)
#         imageSensation = self.createSensation( associations=[], sensation=self.getParent().imageSensations[imageind], memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
#                                                locations='') # valid everywhere
#         self.log('tellOwnIdentity: imageind  ' + str(imageind) + ' self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=' + imageSensation.toDebugStr())      
#         self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation) # or self.process
#         imageSensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes
# 
#         for i in range(Identity.VOICES_PER_CONVERSATION):          
#             time.sleep(Identity.SLEEP_BETWEEN_VOICES)
#             
#             voiceind = random.randint(0, len(self.getParent().voiceSensations)-1)
#             voiceSensation = self.createSensation(associations=[], sensation=self.getParent().voiceSensations[voiceind], memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
#                                                   locations='') # valid everywhere
#             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation, association=None) # or self.process
#             self.log("tellOwnIdentity: " + str(voiceind) + " self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=" + voiceSensation.toDebugStr())      
#             voiceSensation.detach(robot=self) #to be sure all is deteched, TODO Study to remove other detachhes
# 
#     '''
#     We can sense
#     We are Sense type Robot
#     '''        
#     def canSense(self):
#         return False 
#     
#     '''
#     sense
#     '''
#     
#     def sense(self):
#         if len(self.getParent().imageSensations) > 0 and len(self.getParent().voiceSensations) > 0:
#             time.sleep(self.sleeptime)
#             self.tellOwnIdentity()
#             self.sleeptime = 2*self.sleeptime
#         else:
#             self.running = False
            
            

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
                 mainRobot,
                 memory,
                 address,
                 hostNames,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0):

        Robot.__init__(self,
                       mainRobot=mainRobot,
                       memory=memory,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in TCPServer, not Robot")
        self.address=address
        self.setName('TCPServer: ' + str(address))
        # convert hostnames to IP addresses so same thing has always same name
        self.hostNames = []
        for hostname in hostNames:
            self.hostNames.append(socket.gethostbyname(hostname))

        self.log('__init__: creating socket' )
        self.sock = socket.socket(family=Robot.ADDRESS_FAMILY,
                                  type=Robot.SOCKET_TYPE)
        self.sock.setblocking(True)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketServers = []
        self.socketClients = []
        self.running=False
        self.isStoppedByRemote=False
       
    def run(self):
        self.log('run: Starting')
               
        self.running=True
        self.mode = Sensation.Mode.Normal
        self.robotState = Sensation.RobotState.RobotStateRunning
          
        try:
            self.log('run: bind '+ str(self.address))
            self.sock.bind(self.address)
            self.server_address = self.sock.getsockname()
            self.sock.listen(self.request_queue_size)
            
            # TODO WE should connect to hostsnames that respond
            
            self.log("TCPServer for hostName in self.hostNames")
            for hostName in self.hostNames:
                connected = False
                tries=0
                while self.running and not connected and tries < Robot.HOST_RECONNECT_MAX_TRIES:
                    self.log('run: TCPServer.connectToHost ' + str(hostName))
                    connected, socketClient, socketServer = self.connectToHost(hostName)

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
            self.log("run: sock.bind, listen exception {}".format(str(e)))
            traceback = e.__traceback__
            while traceback:
                self.log("run: sock.bind, listen exception {}: line {}".format(traceback.tb_frame.f_code.co_filename,traceback.tb_lineno))
                traceback = traceback.tb_next
            self.running = False
        
 
        socketClient = None
        socketServer = None
        while self.running and not self.isStoppedByRemote:
            self.log('run: waiting self.sock.accept()')
            sock, address = self.sock.accept()
            self.log('run: self.sock.accept() '+ str(address))
            if self.running and not self.isStoppedByRemote:
                self.log('run: as server socketServer = self.createSocketServer'+ str(address))
                socketServer = self.createSocketServer(sock=sock, address=address, mainRobot=self.getMainRobot(), tcpServer=self)
                self.log('run: as server socketClient = self.createSocketClient'+ str(address))
                socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer, tcpServer=self)
                self.log('run: socketServer.setSocketClient(socketClient)'+ str(address))
                socketServer.setSocketClient(socketClient)
                self.parent.subInstances.append(socketClient) # Note to parent subInstances
    
    
                if self.running and not self.isStoppedByRemote:
                    self.log('run: socketServer.start()')
                    socketServer.start()
                    time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
                if self.running and not self.isStoppedByRemote:
                    self.log('run: socketClient.start()')
                    socketClient.start()
                    time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
        self.robotState = Sensation.RobotState.RobotStateStopping
        self.log('run: STOPPED')
        if socketClient and socketClient.running:
            self.log('run: socketClient.stop()')
            socketClient.stop()
        if socketServer and socketServer.running:
            self.log('run: socketServer.stop()')
            socketServer.stop()
        self.log('run: ENDED')
        self.robotState = Sensation.RobotState.RobotStateStopped
        
    '''
    Connect to host by creating SocketClient and SocketServer
    '''
        
    def connectToHost(self, hostName):
        self.log("connectToHost hostName " + hostName)
        address=(hostName, Robot.PORT)
        sock = socket.socket(family=Robot.ADDRESS_FAMILY,
                             type=Robot.SOCKET_TYPE)
                
        connected=False
        socketClient = None
        socketServer = None
        try:
            self.log('connectToHost: sock.connect('  + str(address) + ')')
            sock.connect(address)
            connected=True
            self.log('connectToHost: done sock.connect('  + str(address) + ')')
        except Exception as e:
            self.log("connectToHost: sock.connect(" + str(address) + ') exception ' + str(e))
            connected = False
    
        if connected:
            socketServer = self.createSocketServer(sock=sock, address=address, mainRobot=self.getMainRobot(), tcpServer=self)
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
        return connected, socketClient, socketServer
        

    def stop(self):
        self.log('stop')
        self.running = False
        self.mode = Sensation.Mode.Stopping
        self.robotState = Sensation.RobotState.RobotStateStopping
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
        address=('localhost', Robot.PORT)
        sock = socket.socket(family=Robot.ADDRESS_FAMILY,
                             type=Robot.SOCKET_TYPE)
        try:
            self.log('run: sock.connect('  + str(address) + ')')
            sock.connect(address)
            self.log('run: done sock.connect('  + str(address) + ')')
        except Exception as e:
            self.log("run: sock.connect(" + str(address) + ') exception ' + str(e))
 
                   
    def createSocketServer(self, sock, address,  mainRobot, tcpServer, socketClient=None):
        self.log('createSocketServer: creating new SocketServer')
        socketServer = SocketServer(mainRobot=mainRobot,
                                    parent=self,
                                    memory=self.getMemory(),    # use same memory
                                    instanceName='SocketServer',
                                    instanceType=Sensation.InstanceType.Remote,
                                    level=self.level,
                                    address=address,
                                    sock=sock,
                                    socketClient=socketClient,
                                    tcpServer=tcpServer)
        self.socketServers.append(socketServer)
        self.log('createSocketServer: return socketServer')
        return socketServer

    def createSocketClient(self, sock, address, tcpServer, socketServer=None):
        self.log('createSocketClient: creating new SocketClient')
        socketClient = SocketClient(mainRobot=self.parent,
                                    parent=self.parent,
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

class SocketClient(Robot): #, SocketServer.ThreadingMixIn, TCPServer):

    def __init__(self,
                 mainRobot,
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
        print("We are in SocketClient, not Robot")
        #set first variables we may need, when we create Robot
        # because we overwrite some methods rhat need these variables
 
        self.isStoppedByRemote = False       
        self.tcpServer = tcpServer
        self.sock = sock
        self.address = address
        self.remoteHost=remoteHost
        self.socketServer = socketServer
        if self.sock is None or self.address is None:       
            self.address=(self.remoteHost, Robot.PORT)
        
        #now we can init Robot class
        Robot.__init__(self,
                       mainRobot=mainRobot,
                       parent=parent,
                       memory=memory,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)

            
            
        self.setName('SocketClient: '+str(address))
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
        self.robotState = Sensation.RobotState.RobotStateRunning
        self.log("run: Starting")
                 
        try:
            # tell other side robot that we are present ion these location with MainNames
            sensation=self.getMainRobot().createSensation(associations=[],
                                                          robotType=Sensation.RobotType.Communication,
                                                          sensationType = Sensation.SensationType.Robot,
                                                          memoryType = Sensation.MemoryType.Working,
                                                          presence = Sensation.Presence.Present,
                                                          name = self.getName(),
                                                          locations = self.getLocations())
            self.log('run: sendSensation(sensation=Sensation(robot=self.getMainRobot(),sensationType = Sensation.SensationType.Robot), sock=self.sock,'  + str(self.address) + ')')
            self.running =  self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
            sensation.detach(robot=self.getMainRobot())
            self.log('run: done sendSensation(sensation=Sensation(robot=self.getMainRobot(), sensationType = Sensation.SensationType.Robot), sock=self.sock,'  + str(self.address) + ')')
            if self.running:
                 # tell our local capabilities
                 # it is important to deliver only local capabilities to the remote,
                 # because other way we would deliver back remote's own capabilities we don't have and
                 # remote would and we to do something that it only can do and
                 # we would route sensation back to remote, which routes it back to us
                 # in infinite loop
                capabilities=self.getLocalMasterCapabilities()
                self.log('run: self.getLocalMasterCapabilities() toString '  + capabilities.toString())
                self.log('run: self.getLocalMasterCapabilities() toDebugString '  + capabilities.toDebugString('SocketClient before send'))
                locations = self.getLocalMasterLocations();
                self.log('run: self.getLocalMasterLocations() ' + str(locations))
                sensation=self.getMainRobot().createSensation(associations=[], robotType=Sensation.RobotType.Muscle, sensationType = Sensation.SensationType.Capability,
                                                                       capabilities=capabilities,
                                                                       locations = locations,
                                                                       mainNames = self.getMainRobot().getMainNames()) # main Robots mainNames
                self.log('run: sendSensation(sensationType = Sensation.SensationType.Capability, capabilities=self.getLocalMasterCapabilities()), sock=self.sock {} mainNames {}'.format(self.address, self.getMainRobot().getMainNames()))
                self.running = self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
                sensation.detach(robot=self.getMainRobot())
                self.log('run: sendSensation Sensation.SensationType.Capability done ' + str(self.address) +  ' '  + sensation.getCapabilities().toDebugString('SocketClient'))
        except Exception as e:
            self.log("run: SocketClient.sendSensation exception {}".format(str(e)))
            traceback = e.__traceback__
            while traceback:
                self.log("run: SocketClient.sendSensation exception {}: line {}".format(traceback.tb_frame.f_code.co_filename,traceback.tb_lineno))
                traceback = traceback.tb_next
            self.running = False

        # finally normal run from Robot-class
        if self.running:
            super(SocketClient, self).run()        
        # If there has been problem in connections
        # at this point new SocketClient is running and it should have all Sensations from out Axon to send
        # but to be sure that no Sensations will be as unForgettable state
        # and memory can not be released, just try to empty out Axon
        self.robotState = Sensation.RobotState.RobotStateStopping
        while(not self.getAxon().empty()):        
            tranferDirection, sensation = self.getAxon().get(robot=self)
            sensation.detachAll()
        self.robotState = Sensation.RobotState.RobotStateStopped

        
    def process(self, transferDirection, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        # We can handle only sensation going down transfer-robotType
#         if transferDirection == Sensation.TransferDirection.Down:
        self.activityNumber += 1
        if not self.isStoppedByRemote:
            if self.getAxon().length() > Robot.SOCKETCLIENT_MAX_QUEUE_LENGTH:
                self.log('process: skipping too long Axon queue Sensation')
            else:
                self.running = self.sendSensation(sensation, self.sock, self.address)
                # if we have got broken pipe -error, meaning that socket writing does not work any more
                # then try to get new connection, meaning that ask TCPServer to give us a new open socket
                # TODO When stopping by remote Robot Stop-sensation this logic is broken
                # If we have got Remote Robots Stop-Sensation, then we should not try to connect again.
                # But in practice we have problem in TCPServer
                if not self.running and self.mode == Sensation.Mode.Interrupted:
                    self.log('process: interrupted')
                    connected = False
                    tries=0
                    while not connected and tries < Robot.HOST_RECONNECT_MAX_TRIES:
                        self.log('process: interrupted self.tcpServer.connectToHost ' + str(self.getHost()))
                        connected, socketClient, socketServer = self.tcpServer.connectToHost(self.getHost())
                        if not connected:
                            self.log('process: interrupted self.tcpServer.connectToHost did not succeed ' + str(self.getHost()) + ' time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)')
                            time.sleep(Robot.SOCKET_ERROR_WAIT_TIME)
                            tries=tries+1
                    if connected:
                        self.log('process: interrupted self.tcpServer.connectToHost SUCCEEDED to ' + str(self.getHost()))
                        # transfer sensation we could not send to the new SocketClient
                        socketClient.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
                        # transfer all sensation from out Axon to the new SocketClient
                        while(not self.getAxon().empty()):
                            tranferDirection, sensationToMove = self.getAxon().get(robot=self)
                            sensationToMove.detachAll()
                            socketClient.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensationToMove)
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
    Overwrite local method. This way we can use remote Robot
    same way than local ones.
    
    our server has got locations from remote host
    our own location are meaningless
    '''
    def getLocations(self):
        if self.getSocketServer() is not None:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='getLocations: self.getSocketServer().getLocations() ' + self.getSocketServer().getLocationsStr())
            return self.getSocketServer().getLocations()
        return None

    def getUpLocations(self):
        if self.getSocketServer() is not None:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='getLocations: self.getSocketServer().getUpLocations() ' + self.getSocketServer().getUpLocationsStr())
            return self.getSocketServer().getUpLocations()
        return None
   
    def getDownLocations(self):
        if self.getSocketServer() is not None:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='getLocations: self.getSocketServer().getDownLocations() ' + self.getSocketServer().getDownLocationsStr())
            return self.getSocketServer().getDownLocations()
        return None
    
    '''
    Overwrite local method. This way we can use remote Robot
    same way than local ones.
    
    our server has got mainNames from remote host
    our own mainNames are meaningless
    '''
    def getMainNames(self):
        if self.getSocketServer() is not None:
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='getMainNames: self.getSocketServer().getMainNames {}'.format(self.getSocketServer().getMainNames()))
            return self.getSocketServer().getMainNames()
        return None
    '''
    share out knowledge of sensation memory out client has capabilities
       
    This is happening when SocketServer is calling it and we don't know if
    SocketClient is running so best way can be just put all sensations into our Axon
    '''
#     def shareSensations(self, capabilities):
#         if self.getHost() not in self.getMemory().sharedSensationHosts:
#             for sensation in self.getMemory().getSensations(capabilities):
#                  self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
# 
#             self.getMemory().sharedSensationHosts.append(self.getHost())

    '''
    share Robot knowledge about items, voices and images.
    
    This is used, when two Robots connect using tcp/ip
    SocketServer asks SocketClient to share these Sensation to other mainRobot running in other computer.
    When this is done at the beginning of connection, mainRobots share each other what is happening.
    '''
    def shareSensations(self, capabilities):
        if self.getHost() not in self.getMemory().sharedSensationHosts:
            # choose what to share
            sensationtypes = [Sensation.SensationType.Item,
                              Sensation.SensationType.Image,
                              Sensation.SensationType.Voice]
            for sensation in self.getMemory().getSensations(capabilities = capabilities,
                                                            sensationtypes = sensationtypes):
                    self.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)

            self.getMemory().sharedSensationHosts.append(self.getHost())
    '''
    method for sending a sensation
    '''
        
    def sendSensation(self, sensation, sock, address):
        #self.log('SocketClient.sendSensation')
        ok = True
        
        if sensation.isReceivedFrom(self.getHost()) or \
           sensation.isReceivedFrom(self.getSocketServer().getHost()):
            #pass
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='socketClient.sendSensation asked to send sensation back to sensation original host. We Don\'t recycle it! receivedFrom:' + str(sensation.receivedFrom) + ': self.getHost(): ' + self.getHost() + ': self.getSocketServer().getHost(): ' + self.getSocketServer().getHost())
        else:
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='socketClient.sendSensation receivedFrom:' + str(sensation.receivedFrom) + ' self.getHost(): ' + self.getHost() + ': self.getSocketServer().getHost(): ' + self.getSocketServer().getHost())
            sensation.setRobotId(self.getMainRobot().getId()) # claim that
 
            # We need ead lock todiable some-one changes this sensation
            self.getMemory().acquireRead()                                                                # all sensation come from Robot
            bytes = sensation.bytes()
            self.getMemory().releaseRead()                                                                # all sensation come from Robot
            length =len (bytes)
            length_bytes = length.to_bytes(Sensation.ID_SIZE, byteorder=Sensation.BYTEORDER)
    
            try:
                l = sock.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
                if Sensation.SEPARATOR_SIZE == l:
                    pass
                    #self.log('SocketClient.sendSensation wrote separator to ' + str(address))
                else:
                    self.log(logLevel=Robot.LogLevel.Verbose, logStr="SocketClient.sendSensation length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
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
                        self.log(logLevel=Robot.LogLevel.Normal, logStr="SocketClient.sendSensation wrote sensation " + sensation.toDebugStr() + " to " + str(address))
                    except Exception as err:
                        self.log("SocketClient.sendSensation error writing Sensation to " + str(address) + " error " + str(err))
                        ok = False
                        self.mode = Sensation.Mode.Interrupted
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
        self.robotState = Sensation.RobotState.RobotStateStopping
        
        # socketserver can't close itself, just put it to closing mode
        self.getSocketServer().stop() # socketserver can't close itself, we must send a stop sensation to it
        # we must send a stop sensation to it
        
        # tell other side robot that we are absentt in these location with MainNames
        sensation=self.getMainRobot().createSensation(associations=[],
                                                      robotType=Sensation.RobotType.Communication,
                                                      sensationType = Sensation.SensationType.Robot,
                                                      memoryType = Sensation.MemoryType.Working,
                                                      presence = Sensation.Presence.Absent,
                                                      name = self.getName(),
                                                      locations = self.getLocations())
        self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
        sensation.detach(robot=self)
        
        # try to stop other side robot, it should decide itself, if it stops or not but that is not yet implemented        
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
                 mainRobot,
                 tcpServer,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0,
                 socketClient = None):

        Robot.__init__(self,
                       mainRobot=mainRobot,
                       memory=memory,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in SocketServer, not Robot")
        self.sock=sock
        self.address=address
        self.tcpServer=tcpServer
        self.socketClient = socketClient
        self.setName('SocketServer: ' + str(address))
    
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
        self.robotState = Sensation.RobotState.RobotStateRunning
        self.log("run: Starting")
        
        # starting other threads/senders/capabilities
        
        # if we don't know our capabilities, we should ask them
        # can't talk to out  host robotType, but client can,
        # so we ask it to do the job
#         if self.getCapabilities() is None and self.socketClient is not None:
#             self.socketClient.askCapabilities()
 
        while self.running:
            self.log(logLevel=Robot.LogLevel.Detailed, logStr="run: waiting next Sensation from " + str(self.address))
            synced = False
            ok = True
            while not synced and self.running:
                try:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr="self.sock.recv SEPARATOR from " + str(self.address))
                    self.data = self.sock.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
                    if len(self.data) == len(Sensation.SEPARATOR) and self.data[0] is Sensation.SEPARATOR[0]:
                        synced = True
                        ok = True
                    if len(self.data) == 0: # no hope to get something
                        self.running = False
                except Exception as err:
                    self.log("self.sock.recv SEPARATOR " + str(self.address) + " error " + str(err))
                    self.running = False
                    ok = False
                    self.mode = Sensation.Mode.Interrupted   
            if synced and self.running:
                # message length section
                self.log(logLevel=Robot.LogLevel.Detailed, logStr="run: waiting size of next Sensation from " + str(self.address))
                # we can get id of sensation in many pieces
                sensation_length_length = Sensation.ID_SIZE
                self.data = None
                while sensation_length_length > 0 and self.running and ok:
                    try:
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr="run: self.sock.recv(sensation_length_length) from " + str(self.address))
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
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr="run: SocketServer Client " + str(self.address) + " wrote " + str(sensation_length))
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
                                self.log("run: self.sock.recv({}) Interrupted error {} {}".format(sensation_length,str(self.address),str(err)))
                                self.running = False
                                ok = False
                                if self.mode == Sensation.Mode.Normal:  # interrupted (only if not stopping)
                                    self.mode = Sensation.Mode.Interrupted
                        if self.running and ok and sensation_length == 0:
                            sensation=self.createSensation(associations=[], bytes=self.data)
                            sensation.addReceived(self.getHost())  # remember route
                            if sensation.getSensationType() == Sensation.SensationType.Capability:
                                self.log('run: SocketServer got Capability sensation {} mainNames {}'.format(sensation.getCapabilities().toDebugString('SocketServer'), sensation.getMainNames()))
                                self.setMainNames(mainNames=sensation.getMainNames())
                                self.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
                                self.route(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
                                # share here sensations from our memory that this host has capabilities
                                # We wan't always share our all knowledge with all other robots
                                if self.getSocketClient() is not None:
                                    self.getSocketClient().shareSensations(self.getCapabilities())
                            elif sensation.getSensationType() == Sensation.SensationType.Robot:
                                self.log("run: SocketServer got Robot sensation " + sensation.toDebugStr())
                                # reply with Robot-sensation is done with self.getSocketClient().shareSensations(self.getCapabilities()
                            elif sensation.getSensationType() == Sensation.SensationType.Location:
                                self.log("run: SocketServer got Location sensation " + sensation.toDebugStr())
                                self.setLocations(locations=sensation.getLocations())
                                #self.setMainNames(mainNames=sensation.getMainNames())
                            else:
                                # check if we have got Stop and reject it to start again informing that remote has send us a stop
                                # This is a hack and we should handle this in TCPServer, but works
                                if sensation.getSensationType() == Sensation.SensationType.Stop:
                                    self.log("run: SocketServer got Stop sensation " + sensation.toDebugStr())
                                    self.tcpServer.isStoppedByRemote = True
                                    if self.getSocketClient() is not None:
                                        self.getSocketClient().isStoppedByRemote = True
                                    self.getMainRobot().stop()
                                self.log("run: SocketServer got sensation " + sensation.toDebugStr())
#                                 self.getParent().getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation) # write sensation to TCPServers Parent, because TCPServer does not read its Axon
                                self.route(transferDirection=Sensation.TransferDirection.Up, sensation=sensation) # write sensation to TCPServers Parent, because TCPServer does not read its Axon
                            sensation.detach(robot=self)
                            self.log("done sensation.detach(robot=self)")
                        else:
                            # TODO check logic
                            self.mode = Sensation.Mode.Interrupted # if we could not read all, then we are interrupted
                            synced = False
                        
        try:
            self.sock.close()
        except Exception as err:
            self.log("self.sock.close() " + str(self.address) + " error " + str(err))

    def stop(self):
        self.log("stop")
#         self.getSocketClient().sendStop(sock = self.sock, address=self.address)
        self.running = False
        self.mode = Sensation.Mode.Stopping
        self.robotState = Sensation.RobotState.RobotStateStopping
        


    global do_server   
    def do_server(mainRobot):
        signal.signal(signal.SIGINT, signal_handler)
        # commented only linux only signals
        # rest can be found in Windows also
        #signal.signal(signal.SIGHUP, signal_handler)
        #signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
        #print ("do_server: create Robot")
        #global mainRobot
        #mainRobot = Robot(mainRobot=None)
    
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
    
    global signal_handler   
    def signal_handler(signal, frame):
        print ('signal_handler: You pressed Ctrl+C!')
        
        mainRobot.doStop()
        print ('signal_handler: ended!')        
        #                                                 location=self.getLocations())


#     exit()
    
#     print ('signal_handler: Shutting down sensation server ...')
#     RobotRequestHandler.server.serving =False
#     print ('signal_handler: sensation server is down OK')
#     
#     print ('signal_handler: Shutting down picture server...')
#     RobotRequestHandler.pictureServer.serving =False
#     print ('signal_handler: picture server is down OK')



    global robotStart    
    def robotStart(is_daemon, mainRobot):
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
                    do_server(mainRobot=mainRobot)
            else:
                do_server(mainRobot=mainRobot)
                print ("start: stopped")

    
    global robotStop   
    def robotStop():
        
        print ("stop: socket.socket(sock.AF_INET, socket.SOCK_STREAM)")
        # Create a socket (SOCK_STREAM means a TCP socket)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # Connect to server and send data
                print ('stop: sock.connect((localhost, Robot.PORT))')
                address=('localhost', Robot.PORT)
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
            returnIdentitymainRobot
    
        finally:
            print ('stop: sock.close()')
            sock.close()
        print ("stop: end")

 

    # Main Robot starting code
    global doMainRobot
    def doMainRobot(mainRobot):
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
                Robot.STOP=True
            elif opt == '--stop':
                print (sys.argv[0] + ' stop')
                Robot.STOP=True
            elif opt == '--restart':
                print (sys.argv[0] + ' restart')
                Robot.STOP=True
                Robot.START=True
            elif opt == '--daemon':
                print (sys.argv[0] + ' daemon')
                Robot.DAEMON=True
            elif opt == '--manual':
                print (sys.argv[0] + ' manual')
                Robot.MANUAL=True
               
        if not Robot.START and not Robot.STOP:
            Robot.START=True
        
        if (Robot.STOP):
            robotStop()
        if (Robot.START): 
            robotStart(Robot.DAEMON, mainRobot=mainRobot)   
                 
        print ("__main__ exit")
        exit()
        print ("__main__ exit has been done so this should not be printed")

# add this code to your main Robot code    
# # Main Robot starting code
# if __name__ == "__main__":
#     print ("__main__: create Robot")
#     doMainRobot()
#     global mainRobot
#     mainRobot = Robot(mainRobot=None)
#     mainRobot.doMainRobot()
    
