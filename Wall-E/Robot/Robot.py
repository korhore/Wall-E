'''
Created on Feb 24, 2013
Updated on 15.05.2019
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
import importlib

from Axon import Axon
from Config import Config, Capabilities
from Sensation import Sensation
# if 'Sensation' not in sys.modules:
#     from Sensation import Sensation
from Romeo import Romeo
from ManualRomeo import ManualRomeo
from dbus.mainloop.glib import threads_init
from xdg.IconTheme import theme_cache
from _ast import Or
if 'Hearing.Hear' not in sys.modules:
    from Hearing.Hear import Hear
if 'Seeing.See' not in sys.modules:
    from Seeing.See import See


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
    
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("Robot 1")
        Thread.__init__(self)
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
        self.name = self.getWho()
        self.log("init robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + self.config.getInstanceType() + self.capabilities.toDebugString())
        # global queue for senses and other robots to put sensations to robot
        self.axon = Axon(config=self.config)
        #a nd create virtual instances
        for subInstanceName in self.config.getSubInstanceNames():
            try:
                module = subInstanceName+ '.' + subInstanceName
                imported_module = importlib.import_module(module)
                print('init ' + subInstanceName)
                robot = getattr(imported_module, subInstanceName)(parent=self,
                                                                  instanceName=subInstanceName,
                                                                  instanceType= Sensation.InstanceType.SubInstance,
                                                                  level=self.level)
            except ImportError as e:
                print("Import error, using default Robot for " + module + ' fix this ' + str(e))

                robot = Robot(configFilePath=self.config.getSubinstanceConfigFilePath(subInstanceName),
                              parent=self)
                              #outAxon=self.inAxon)
            if robot is not None:
                self.subInstances.append(robot)
            else:
                self.log("init robot sub instanceName " + subInstanceName + " is None")

        for instanceName in self.config.getVirtualInstanceNames():
            robot = Robot(parent=self,
                          instanceName=instanceName,
                          instanceType=Sensation.InstanceType.Virtual,
                          level=self.level)
            if robot is not None:
                self.subInstances.append(robot)
            else:
                self.log("init robot virtual instanceName " + instanceName + " is None")
        

            
    def getParent(self):
        return self.parent

    def getLevel(self):
        return self.level
    
    def getWho(self):
        return self.config.getWho()
    
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
                                    
        self.log('getMasterCapabilities ' +capabilities.toDebugString())
        return capabilities
    
    def _getCapabilities(self):
        capabilities = Capabilities(deepCopy=self.getCapabilities())
        for robot in self.getSubInstances():
            capabilities.Or(robot._getLocalCapabilities())
                                   
        self.log('_getCapabilities ' +capabilities.toDebugString())
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
                                    
        self.log('getLocalMasterCapabilities ' +capabilities.toDebugString())
        return capabilities

    def _getLocalCapabilities(self):
        capabilities = Capabilities(deepCopy=self.getCapabilities())
        for robot in self.getSubInstances():
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                capabilities.Or(robot._getLocalCapabilities())
                                    
        self.log('_getLocalCapabilities ' +capabilities.toDebugString())
        return capabilities
       
    '''
    Has this instance this capability
    ''' 
    def hasCapanility(self, direction, memory, sensationType):
        hasCapalility = False
        if self.getCapabilities() is not None:
            hasCapalility = self.getCapabilities().hasCapanility(direction, memory, sensationType)
            self.log("hasCapanility direction " + str(direction) + " memory " + str(memory) + " sensationType " + str(sensationType) + ' ' + str(hasCapalility))      
        return hasCapalility
    '''
    Has this instance or at least one of its subinstabces this capability
    ''' 
    def hasSubCapanility(self, direction, memory, sensationType):
        #self.log("hasSubCapanility direction " + str(direction) + " memory " + str(memory) + " sensationType " + str(sensationType))
        if self.hasCapanility(direction, memory, sensationType):
            self.log('hasSubCapanility self has direction ' + str(direction) + ' memory ' + str(memory) + ' sensationType ' + str(sensationType) + ' True')      
            return True    
        for robot in self.getSubInstances():
            if robot.getCapabilities().hasCapanility(direction, memory, sensationType) or \
               robot.hasSubCapanility(direction, memory, sensationType):
                self.log('hasSubCapanility subInstance ' + robot.getWho() + ' direction ' + str(direction) + ' memory ' + str(memory) + ' sensationType ' + str(sensationType) + ' True')      
                return True
        #self.log('hasSubCapanility direction ' + str(direction) + ' memory ' + str(memory) + ' sensationType ' + str(sensationType) + ' False')      
        return False
   
    def getSubCapabiliyInstances(self, direction, memory, sensationType):
        robots=[]
        for robot in self.getSubInstances():
            if robot.hasCapanility(direction, memory, sensationType) or \
                robot.hasSubCapanility(direction, memory, sensationType):
                robots.append(robot)
        return robots


    def run(self):
        self.running=True
        self.log("run: Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()
#         # main robot starts tcpServer first so clients gets connection
#         if self.level == 1:
#             self.tcpServer.start()
           
        # study own identity
        # starting point of robot is always to study what it knows himself
        self.studyOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            sensation=self.axon.get()
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
        
    def log(self, logStr):
         print(self.name + ":" + str( self.config.level) + ":" + Sensation.Modes[self.mode] + ": " + logStr)

    def stop(self):
        self.log("Stopping robot")      
        if self.level == 1:
            self.tcpServer.stop()

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
        self.running = False    # this in not real, but we wait for Sensation,
                                # so give  us one stop sensation
        self.axon.put(Sensation(sensationType = Sensation.SensationType.Stop))


    '''
    DoStop is used to stop server process and its subprocesses (threads)
    Technique is just give Stop Sensation to process.
    With same technique remote machines can stop us and we scan stop them
    '''
            
    def doStop(self):
        self.axon.put(Sensation(sensationType = Sensation.SensationType.Stop))
        
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
    In basic class Sensation processing in not implemented, but this the place
    for derives classes to process Sensations and then call this basic
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

        
    '''
            
    def process(self, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')      
            self.stop()
        # sensation going up
        elif sensation.getDirection() == Sensation.Direction.Out:
            if sensation.getSensationType() == Sensation.SensationType.Capability:
                self.log('process: sensation.getSensationType() == Sensation.SensationType.Capability')      
                self.log('process: self.setCapabilities(Capabilities(capabilities=sensation.getCapabilities() ' + sensation.getCapabilities().toDebugString('capabilities'))      
                self.setCapabilities(Capabilities(deepCopy=sensation.getCapabilities()))
                self.log('process: capabilities: ' + self.getCapabilities().toDebugString('saved capabilities'))      
            elif self.getParent() is not None: # if sensation is going up  and we have a parent
                self.log('process: self.getParent().getAxon().put(sensation)')      
                self.getParent().getAxon().put(sensation)
            # finally check, if we con process this sensation as in-direction sensation
            # maybe this is not a good idea, b ecause  MainRobot will send this sensation to us anyway
            robots = self.getSubCapabiliyInstances(direction=Sensation.Direction.In, memory=sensation.getMemory(), sensationType=sensation.getSensationType())
            self.log('Sensation.Direction.In self.getSubCapabiliyInstances' + str(robots))
        # sensation going in
        else:
            # which subinstances can process this
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
