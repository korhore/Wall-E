'''
Created on Feb 24, 2013
Updated on 17.08.2019
@author: reijo.korhonen@gmail.com
'''

import os
import shutil
from threading import Thread, Timer
import time
from enum import Enum

#import daemon
#import lockfile
import importlib
import traceback

from PIL import Image as PIL_Image


from Axon import Axon
from Config import Config, Capabilities
from Sensation import Sensation
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
    #presence variables
    presentItemSensations={}
    
    # (Main) Robots identity. All running Robot treads share these
    #idexes used in communication
    imageind=0
    voiceind=0
    # Features of Robot identity we can show and speak to
    images=[]
    voices=[]
    
        
   
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("Robot 1")
        Thread.__init__(self)
        
        self.time = time.time()
        self.id = Sensation.getNextId()
        
        self.mode = Sensation.Mode.Starting
        self.parent = parent
        self.instanceName=instanceName
        if  self.instanceName is None:
            self.instanceName = Config.DEFAULT_INSTANCE
        self.instanceType=instanceType
        self.level=level+1
        
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
        self.capabilities = Capabilities(config=self.config)
        print("Robot 4")
        self.logLevel=self.config.getLogLevel()
        self.setWho(self.config.getWho())
        self.log(logLevel=Robot.LogLevel.Normal, logStr="init robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType() + self.capabilities.toDebugString())
        # global queue for senses and other robots to put sensations to robot
        self.axon = Axon()
        #and create subinstances
        for subInstanceName in self.config.getSubInstanceNames():
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
    def hasCapability(self, direction, memory, sensationType):
        hasCapalility = False
        if self.isRunning() and self.getCapabilities() is not None:
            hasCapalility = self.getCapabilities().hasCapability(direction, memory, sensationType)
            if hasCapalility:
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="hasCapability direction " + str(direction) + " memory " + str(memory) + " sensationType " + str(sensationType) + ' ' + str(hasCapalility))      
        return hasCapalility
    '''
    Has this instance or at least one of its subinstabces this capability
    ''' 
    def hasSubCapability(self, direction, memory, sensationType):
        #self.log(logLevel=Robot.LogLevel.Verbose, logStr="hasSubCapability direction " + str(direction) + " memory " + str(memory) + " sensationType " + str(sensationType))
        if self.hasCapability(direction, memory, sensationType):
            self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability self has direction ' + str(direction) + ' memory ' + str(memory) + ' sensationType ' + str(sensationType) + ' True')      
            return True    
        for robot in self.getSubInstances():
            if robot.getCapabilities().hasCapability(direction, memory, sensationType) or \
               robot.hasSubCapability(direction, memory, sensationType):
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability subInstance ' + robot.getWho() + ' has direction ' + str(direction) + ' memory ' + str(memory) + ' sensationType ' + str(sensationType) + ' True')      
                return True
        #self.log(logLevel=Robot.LogLevel.Verbose, logStr='hasSubCapability direction ' + str(direction) + ' memory ' + str(memory) + ' sensationType ' + str(sensationType) + ' False')      
        return False
   
    def getSubCapabilityInstances(self, direction, memory, sensationType):
        robots=[]
        for robot in self.getSubInstances():
            if robot.hasCapability(direction, memory, sensationType) or \
                robot.hasSubCapability(direction, memory, sensationType):
                robots.append(robot)
        return robots


    def run(self):
        self.running=True
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run: Starting robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()
        # study own identity
        # starting point of robot is always to study what it knows himself
        self.studyOwnIdentity()
        self.getOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            # if we can't sense, the we wait until we get something into Axon
            # or if we can sense, but there is something in our xon, process it
            if not self.getAxon().empty() or not self.canSense():
                transferDirection, sensation, association = self.getAxon().get()
                self.log(logLevel=Robot.LogLevel.Normal, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
                self.process(transferDirection=transferDirection, sensation=sensation, association=association)
                # as a test, echo everything to external device
                #self.out_axon.put(sensation)
            else:
                self.sense()
 
        self.mode = Sensation.Mode.Stopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
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
        self.log(logLevel=Robot.LogLevel.Verbose, logStr="self.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=Sensation(sensationType = Sensation.SensationType.Stop))")      
        self.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop), association=None)


    '''
    DoStop is used to stop server process and its subprocesses (threads)
    Technique is just give Stop Sensation to process.
    With same technique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        self.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop), association=None)
        
    def studyOwnIdentity(self):
        self.mode = Sensation.Mode.StudyOwnIdentity
        self.log(logLevel=Robot.LogLevel.Normal, logStr="My name is " + self.getWho())      
        self.log(logLevel=Robot.LogLevel.Detailed, logStr="My kind is " + str(self.getKind()))      
#        self.identitypath = self.config.getIdentityDirPath(self.getKind())
#         self.log(logLevel=Robot.LogLevel.Detailed, logStr='My identitypath is ' + self.identitypath)      
#         for dirName, subdirList, fileList in os.walk(self.identitypath):
#             self.log(logLevel=Robot.LogLevel.Verbose, logStr='Found directory: %s' % dirName)      
#             for fname in fileList:
#                 self.log(logLevel=Robot.LogLevel.Verbose, logStr='\t%s' % fname)
                
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
                Robot.images.append(image)
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
                    Robot.voices.append(data)
    

    '''
    In basic class Sensation processing in not implemented, but this the place
    for derived classes to process Sensations and then call this basic
    implementation.
    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
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
                self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation))')      
                self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation, association=None)
            else: # we are main Robot
                # check if we have subrobot that has capability to process this sensation
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: self.getSubCapabilityInstances')      
                robots = self.getSubCapabilityInstances(direction=sensation.getDirection(), memory=sensation.getMemory(), sensationType=sensation.getSensationType())
                self.log(logLevel=Robot.LogLevel.Verbose, logStr='process for ' + sensation.toDebugStr() + ' robots ' + str(robots))
                for robot in robots:
                    if robot.getInstanceType() == Sensation.InstanceType.Remote:
                        # if this sensation comes from sockrServers host
                        if sensation.isReceivedFrom(robot.getHost()) or \
                            sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                            self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getWho() + 'has capability for this, but sensation comes from it self. Don\'t recycle it')
                        else:
                            self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)')
                            robot.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=None)
                    else:
                        self.log(logLevel=Robot.LogLevel.Verbose, logStr='Local robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)')
                        # new instance or sensation for process
                        robot.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=None)
        # sensation going down
        else:
            # which subinstances can process this
            robots = self.getSubCapabilityInstances(direction=sensation.getDirection(), memory=sensation.getMemory(), sensationType=sensation.getSensationType())
            self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getSubCapabilityInstances' + str(robots))
            for robot in robots:
                if robot.getInstanceType() == Sensation.InstanceType.Remote:
                    # if this sensation comes from sockrServers host
                    if sensation.isReceivedFrom(robot.getHost()) or \
                       sensation.isReceivedFrom(robot.getSocketServer().getHost()):
                        self.log(logLevel=Robot.LogLevel.Verbose, logStr='Remote robot ' + robot.getWho() + 'has capability for this, but sensation comes from it self. Don\'t recycle it')
                    else:
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='Remote robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(sensation)')
                        robot.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=None)
                else:
                    self.log(logLevel=Robot.LogLevel.Verbose, logStr='Local robot ' + robot.getWho() + ' has capability for this, robot.getAxon().put(sensation)')
                    robot.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=None)
                    
# Utilities
    def tracePresents(self, sensation):
        # present means pure Present, all other if handled not present
        # if present sensations must come in order
        if sensation.getName() in Robot.presentItemSensations and\
           sensation.getTime() > Robot.presentItemSensations[sensation.getName()].getTime(): 

            if sensation.getPresence() == Sensation.Presence.Entering or\
               sensation.getPresence() == Sensation.Presence.Present or\
               sensation.getPresence() == Sensation.Presence.Exiting:
                Robot.presentItemSensations[sensation.getName()] = sensation
                self.log(logLevel=Robot.LogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())
            else:
                del Robot.presentItemSensations[sensation.getName()]
                self.log(logLevel=Robot.LogLevel.Normal, logStr="Absent " + sensation.getName())
        # accept only sensation items that are not prensent, but not not in order ones
        # absetnt sensations don't have any mean at this case
        elif (sensation.getName() not in Robot.presentItemSensations) and\
             (sensation.getPresence() == Sensation.Presence.Entering or\
               sensation.getPresence() == Sensation.Presence.Present or\
               sensation.getPresence() == Sensation.Presence.Exiting):
                Robot.presentItemSensations[sensation.getName()] = sensation
                self.log(logLevel=Robot.LogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())

    def presenceToStr(self):
        namesStr=''
        for name, sensation in Robot.presentItemSensations.items():
            namesStr = namesStr + ' ' + name
        return namesStr
 
# VirtualRobot

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation


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
        self.timer = Timer(interval=VirtualRobot.COMMUNICATION_INTERVAL, function=self.stopRunning)
        self.timer.start()


        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():  
                transferDirection, sensation, association = self.getAxon().get()
                self.process(transferDirection=transferDirection, sensation=sensation, association=association)
            else:
                self.sense()

        self.log("run ALL SHUT DOWN")  
        
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

                imageSensation = Sensation.create(associations=[], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, image=image, filePath=sensation_filepath)
                self.log("getOwnIdentity: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=" + imageSensation.toDebugStr())      
                self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
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
                    sensation = Sensation.create(associations=[], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, data=data, filePath=sensation_filepath)
                    self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None) # or self.process
                    self.log("getOwnIdentity: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=" + sensation.toDebugStr())      
                 
    '''
    tell your identity
    '''   
    def tellOwnIdentity(self):
        
        image = self.images[self.imageind]
        imageSensation = Sensation.create(associations=[], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, image=image)
        self.log('tellOwnIdentity: self.imageind  ' + str(self.imageind) + ' self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=' + imageSensation.toDebugStr())      
        self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None) # or self.process
        self.imageind=self.imageind+1
        if self.imageind >= len(self.images):
            self.imageind = 0

        for i in range(VirtualRobot.VOICES_PER_CONVERSATION):          
            time.sleep(VirtualRobot.SLEEP_BETWEEN_VOICES)
            data = self.voices[self.voiceind]
            sensation = Sensation.create(associations=[], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, data=data)
            self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation, association=None) # or self.process
            self.log("tellOwnIdentity: " + str(self.voiceind) + " self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=" + sensation.toDebugStr())      
            self.voiceind=self.voiceind+1
            if self.voiceind >= len(self.voices):
               self.voiceind = 0

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
