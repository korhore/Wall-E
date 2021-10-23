'''
Created on 13.02.2020
Updated on 14.05.2021
@author: reijo.korhonen@gmail.com

test Robot class

Tests basic functionality of Robot class
Most important is to test Sensation Routing functionality
We create one MainRobot level Robot and sense and muscle Robots
to study functionality.

python3 -m unittest tests/testRobot.py

TODO Robot does not yet have selfLocationSensation.
When implemented, update test

TODO Tests work now with Robot star routing, meaning that
Sensations are always routed directly from Robot to Robot
and all subRobots are mentioned in MainRobots configuration.

Routing is done default Robot.process, but that can be changed and
then test should be changed. Anyway 

Robot.process(self, transferDirection, sensation)
parameters should be changed 
Robot.process(self, sensation)
default functionality handles Main Robot feeling and stop-sensation,
and finally but detach sensation
transferDirection is not yest removed, but it is igneroed in implementation.

and routing
Robot.route(self, sensation)
does what Robot.process did before.

and changes shouls (are now) done in subRobots and tested



'''
import time as time
import os

import unittest
from Sensation import Sensation
#from Robot import Robot, TCPServer, HOST,PORT
#cannot import HOST,PORT
from Robot import Robot, TCPServer
from Axon import Axon

class RobotTestCase(unittest.TestCase):
    '''
    
    We should play as sense robot and muscle Robot
        - Wall_E_item
        - Image
        - voice
        - location
    '''
    
    MAINNAMES_1 =          ['Wall-E_MainName']
    MAINNAMES_2 =          ['Eva_MainName']
#     MAINNAMES =            ["RobotTestCaseMainName"]
#     OTHERMAINNAMES =       ["OTHER_RobotTestCaseMainName"]

    LOCATIONS_1 =          ['testLocation']
    LOCATIONS_2 =          [                'Ubuntu']
    LOCATIONS_1_2 =        ['testLocation', 'Ubuntu']
    LOCATIONS_1_3 =        ['testLocation',           '3']
    LOCATIONS_2_3 =        [                'Ubuntu', '3']
    LOCATIONS_3_4 =        [                          '3','4']
    LOCATIONS_EMPTY =      []
    LOCATIONS_GLOBAL =     [                                  'global']
    LOCATIONS_1_GLOBAL =   ['testLocation',                   'global']
    
    LOCATIONS_1_NAME =     'testLocation'
    LOCATIONS_1_X =        1.0
    LOCATIONS_1_Y =        2.0
    LOCATIONS_1_Z =        3.0
    LOCATIONS_1_RADIUS =   4.0
    
    LOCATIONS_2_NAME =     'Ubuntu'
    LOCATIONS_2_X =        11.0
    LOCATIONS_2_Y =        12.0
    LOCATIONS_2_Z =        13.0
    LOCATIONS_2_RADIUS =   14.0

    ASSOCIATION_INTERVAL=3.0

    SCORE_1 = 0.1
    SCORE_2 = 0.2
    SCORE_3 = 0.3
    SCORE_4 = 0.4
    SCORE_5 = 0.5
    SCORE_6 = 0.6
    SCORE_7 = 0.7
    SCORE_8 = 0.8
    NAME='Wall-E'
    NAME2='Eva'
    
    LOCALHOST='127.0.0.1'
    REMOTE_LOCALHOST='127.0.0.2'
    FAKE_PORT = 2001
    
    SLEEPTIME=10.0
    WAIT_STEP = 1.0
    
   
    '''
    Test Robot 
    '''
    
    class TestRobot(Robot): 
        '''
        Must fake is_alive to True, so we could test Sensation routing
        '''
        def is_alive(self):
            return True
        
    '''
    Test Sense Robot 
    '''
    
    class TestSenseRobot(TestRobot): 
        '''
        We can sense
        We are Sense type Robot
        '''        
        def canSense(self):
            return True 
     
        '''
        We can sense
        We are Sense type Robot
        # Special case of sense for testing
        '''        
        def sense(self, transferDirection, sensation):
            self.route(transferDirection=transferDirection, sensation=sensation)
            

        
    '''
    Helper methods   
    '''
    def setRobotLocations(self, robot, locations):
        robot.locations = locations
        robot.uplocations = locations
        robot.downlocations = locations    
 
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
        
    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        self.CleanDataDirectory()
        
        
        # set robots to same location
        
        self.mainRobot = Robot(
                           mainRobot=None,
                           parent=None,
                           instanceName='TestMainRobot',
                           instanceType= Sensation.InstanceType.Real)
        # We should set this, because we don't run mainRobot, but call its methods
        #self.assertEqual(self.mainRobot, s.mainRobotInstance, "should have Robot.mainRobotInstance")
        #self.assertEqual(mainRobot, self.mainRobot.getMainRobot(), "should have Robot.mainRobotInstance")
        if self.mainRobot.level == 1:
            self.mainRobot.activityAverage = self.mainRobot.shortActivityAverage = self.mainRobot.config.getActivityAvegageLevel()
            self.mainRobot.activityNumber = 0
            self.mainRobot.activityPeriodStartTime = time.time()

        self.mainRobot.setMainNames(RobotTestCase.MAINNAMES_1)
        self.assertEqual(RobotTestCase.MAINNAMES_1, self.mainRobot.getMainNames())

        self.mainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        self.mainRobot.selfSensation=self.mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.mainRobot.getName(),
                                                          name = self.mainRobot.getName(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.mainRobot.getKind(),
                                                          feeling=self.mainRobot.getFeeling(),
                                                          locations=self.mainRobot.getLocations())
        
        
        self.sense = RobotTestCase.TestSenseRobot(
                           mainRobot = self.mainRobot,
                           parent=self.mainRobot,
                           instanceName='Sense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
#        self.assertEqual(self.mainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.sense.setMainNames(RobotTestCase.MAINNAMES_1)
        self.mainRobot.subInstances.append(self.sense)
#        self.assertEqual(RobotTestCase.MAINNAMES_1, self.sense.getMainNames())
        
        
        self.muscle = RobotTestCase.TestRobot(
                           mainRobot = self.mainRobot,
                           parent=self.mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
#        self.assertEqual(self.mainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setMainNames(RobotTestCase.MAINNAMES_1)
        self.mainRobot.subInstances.append(self.muscle)
 #       self.assertEqual(RobotTestCase.MAINNAMES_1, self.muscle.getMainNames())
                
        #set muscle capabilities  Item, Image, Voice
        self.setRobotCapabilities(robot=self.muscle, robotTypes=[Sensation.RobotType.Sense])
        #self.setRobotCapabilities(robot=self.muscle, robotType=Sensation.RobotType.Muscle, is_set=False)

    '''
    Clean data directory from bi9nary files files.
    Test needs this so known sensations are only created
    '''  
    def CleanDataDirectory(self):
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    if filename.endswith('.'+Sensation.BINARY_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print('os.remove(' + filepath + ') error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
            except Exception as e:
                    print('os.listdir error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
                    
    '''
    set up remote Tcp-connected Robot
    in this machine without real networking devices
    '''

    def setUpRemote(self, mainNames):
        print('\nsetUpRemote')
        
        
        # set robots to same location
        
        self.remoteMainRobot = Robot(
                           mainRobot = None,
                           parent=None,
                           instanceName='RemoteMainRobot',
                           instanceType= Sensation.InstanceType.Real)
        # correct address, to we don't use same localhost 127.0.0.1, but we still use ip-nmumbers in this single computer without real networking
        self.remoteMainRobot.tcpServer.address = (RobotTestCase.REMOTE_LOCALHOST, self.remoteMainRobot.tcpServer.address[1])
        remoteport = self.remoteMainRobot.tcpServer.address[1]
        print('1: remoteport '+  str(remoteport))
        self.remoteMainRobot.setMainNames(mainNames=mainNames)
        self.assertEqual(self.remoteMainRobot.getMainNames(),self.MAINNAMES_2, 'check 00 remote should know its own mainNames')
     
        # We should set this, because we don't run mainRobot, but call its methods
        #self.assertEqual(self.remoteMainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        #self.assertEqual(self.remoteMainRobot, self.getMainRobot(), "should have Robot.mainRobotInstance")
        # this can be problem if tested methods use Robot.mainRobotInstance, because this points to (self.remoteMainRobot
        if self.remoteMainRobot.level == 1:
            self.remoteMainRobot.activityAverage = self.remoteMainRobot.shortActivityAverage = self.remoteMainRobot.config.getActivityAvegageLevel()
            self.remoteMainRobot.activityNumber = 0
            self.remoteMainRobot.activityPeriodStartTime = time.time()

        self.remoteMainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMainRobot.selfSensation=self.remoteMainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.remoteMainRobot,
                                                          name = self.remoteMainRobot.getName(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.remoteMainRobot.getKind(),
                                                          feeling=self.remoteMainRobot.getFeeling(),
                                                          locations=self.remoteMainRobot.getLocations())
        
        
        self.remoteSense = RobotTestCase.TestRobot(
                           mainRobot=self.remoteMainRobot,
                           parent=self.remoteMainRobot,
                           instanceName='RemoteSense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
#        self.assertEqual(self.remoteMainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        self.remoteSense.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMainRobot.subInstances.append(self.remoteSense)
        self.assertEqual(RobotTestCase.MAINNAMES_2, self.remoteSense.getMainNames())
        
        
        self.remoteMuscle = RobotTestCase.TestRobot(
                           mainRobot=self.remoteMainRobot,
                           parent=self.remoteMainRobot,
                           instanceName='RemoteMuscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
#        self.assertEqual(self.remoteMainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        self.remoteMuscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMuscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMainRobot.subInstances.append(self.remoteMuscle)
        self.assertEqual(RobotTestCase.MAINNAMES_2, self.remoteMuscle.getMainNames())
                
        #set muscle capabilities  Item, Image, Voice
        self.setRobotCapabilities(robot=self.remoteMuscle, robotTypes=[Sensation.RobotType.Sense, Sensation.RobotType.Communication])
        #self.setCapabilities(robot=self.remoteMuscle, robotType=Sensation.RobotType.Muscle, is_set=False)
        
        self.assertTrue(self.remoteMuscle in self.remoteMainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Communication,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        self.assertTrue(self.remoteMuscle in self.remoteMainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Communication,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        self.assertTrue(self.remoteMuscle in self.remoteMainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Sense,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        
    '''
    set up virtual Robot
    '''

    def setUpVirtual(self, mainNames):
        print('\nsetUpVirtual')
        
        
        # set robots to same location
        
        self.virtualMainRobot = RobotTestCase.TestRobot(
                           level=2,
                           mainRobot = self.mainRobot,
                           parent= self.mainRobot,
                           instanceName='VirtualMainRobot',
                           instanceType= Sensation.InstanceType.Virtual)
        self.virtualMainRobot.setMainNames(mainNames=mainNames)
        self.assertEqual(self.virtualMainRobot.getMainNames(),self.MAINNAMES_2, 'check 00 virtual should know its own mainNames')
        self.virtualMainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        self.virtualMainRobot.setMainNames(mainNames)
        self.mainRobot.subInstances.append(self.virtualMainRobot)
    
        # We should set this, because we don't run mainRobot, but call its methods
        #self.assertEqual(self.virtualMainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        #self.assertEqual(self.virtualMainRobot, self.getMainRobot(), "should have Robot.mainRobotInstance")
        # this can be problem if tested methods use Robot.mainRobotInstance, because this points to (self.virtualMainRobot
        if self.virtualMainRobot.level == 1:
            self.virtualMainRobot.activityAverage = self.virtualMainRobot.shortActivityAverage = self.virtualMainRobot.config.getActivityAvegageLevel()
            self.virtualMainRobot.activityNumber = 0
            self.virtualMainRobot.activityPeriodStartTime = time.time()

        self.virtualMainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        self.virtualMainRobot.selfSensation=self.virtualMainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.virtualMainRobot,
                                                          name = self.virtualMainRobot.getName(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.virtualMainRobot.getKind(),
                                                          feeling=self.virtualMainRobot.getFeeling(),
                                                          locations=self.virtualMainRobot.getLocations())
        
        #self.mainRobot.subInstances.append(self.virtualMainRobot)
        
        self.virtualSense = RobotTestCase.TestSenseRobot(
                           mainRobot=self.virtualMainRobot,
                           parent=self.virtualMainRobot,
                           instanceName='VirtualSense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=3)
#        self.assertEqual(self.virtualMainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        self.virtualSense.setLocations(RobotTestCase.LOCATIONS_1)
        self.virtualMainRobot.subInstances.append(self.virtualSense)
        self.assertEqual(RobotTestCase.MAINNAMES_2, self.virtualSense.getMainNames())
        
        
        self.virtualMuscle = RobotTestCase.TestRobot(
                           mainRobot=self.virtualMainRobot,
                           parent=self.virtualMainRobot,
                           instanceName='VirtualMuscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=3)
#        self.assertEqual(self.virtualMainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        self.virtualMuscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.virtualMuscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        self.virtualMainRobot.subInstances.append(self.virtualMuscle)
        self.assertEqual(RobotTestCase.MAINNAMES_2, self.virtualMuscle.getMainNames())
                
        #set muscle capabilities  Item, Image, Voice
        self.setRobotCapabilities(robot=self.virtualMuscle, robotTypes=[Sensation.RobotType.Sense, Sensation.RobotType.Communication])
        #self.setCapabilities(robot=self.virtualMuscle, robotType=Sensation.RobotType.Muscle, is_set=False)
        
        self.assertTrue(self.virtualMuscle in self.virtualMainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Communication,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        self.assertTrue(self.virtualMuscle in self.mainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Communication,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        
        self.assertTrue(self.virtualMuscle in self.virtualMainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Communication,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        self.assertTrue(self.virtualMuscle in self.mainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Communication,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        
        self.assertTrue(self.virtualMuscle in self.virtualMainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Sense,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))
        self.assertTrue(self.virtualMuscle in self.mainRobot.getCapabilityInstances(robotType = Sensation.RobotType.Sense,
                                                                                         memoryType = Sensation.MemoryType.Working,
                                                                                         sensationType = Sensation.SensationType.Item,
                                                                                         locations = RobotTestCase.LOCATIONS_1,
                                                                                         mainNames = RobotTestCase.MAINNAMES_1))

    '''
    set capabilities  Item, Image, Voice
    '''
    def setRobotCapabilities(self, robot, robotTypes):
        capabilities  =  robot.getCapabilities()

        for robotType in Sensation.RobotTypesOrdered:
            is_set = robotType in robotTypes    
            #sensory
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice, is_set=is_set)   
            #Working
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice, is_set=is_set)   
            #LongTerm
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice, is_set=is_set)   

        robot.setCapabilities(capabilities)
        


    def tearDown(self):
        print('\ntearDown')       
        del self.muscle
        del self.sense
        del self.mainRobot
        
    def tearDownRemote(self):
        print('\ntearDownRemote')       
        del self.remoteMuscle
        del self.remoteSense
        del self.remoteMainRobot

    def tearDownVirtual(self):
        print('\ntearDownVirtual')       
        del self.virtualMuscle
        del self.virtualSense
        del self.virtualMainRobot
       
    '''
    TODO is this test valid or not?
    '''
        
    def test_Locations(self):
        print('\ntestLocations')
        
        
        # set robots to same location
        
        mainRobot = Robot( mainRobot=None, 
                           parent=None,
                           instanceName='TestLocationMainRobot',
                           instanceType= Sensation.InstanceType.Real)
        # We should set this, because we don't run mainRobot, but call its methods
        #self.assertEqual(mainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        #self.assertEqual(mainRobot, self.getMainRobot(), "should have Robot.mainRobotInstance")
        if mainRobot.level == 1:
            mainRobot.activityAverage = mainRobot.shortActivityAverage = mainRobot.config.getActivityAvegageLevel()
            mainRobot.activityNumber = 0
            mainRobot.activityPeriodStartTime = time.time()

        mainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        mainRobot.selfSensation=mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = mainRobot.getName(),
                                                          name = mainRobot.getName(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=mainRobot.getKind(),
                                                          feeling=mainRobot.getFeeling(),
                                                          locations=mainRobot.getLocations())
        
        
        sense = RobotTestCase.TestRobot(
                           mainRobot=mainRobot,
                           parent=mainRobot,
                           instanceName='Sense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
#        self.assertEqual(mainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        sense.setLocations(RobotTestCase.LOCATIONS_1_2)
        mainRobot.subInstances.append(sense)
        
        
        muscle = RobotTestCase.TestRobot(
                           mainRobot=mainRobot,
                           parent=mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
 #       self.assertEqual(mainRobot,self.getMainRobot(), "should have Robot.mainRobotInstance")
        muscle.setLocations(RobotTestCase.LOCATIONS_1_2)
        muscle.setDownLocations(RobotTestCase.LOCATIONS_1_2)
        mainRobot.subInstances.append(muscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  muscle.getCapabilities()
        # location, needed, because Robot delegates subrobot capability checking
        # in routing phase for Capabilities so also capabilities should have same Locations
        # in real application they are, because Robots Locations come from Capabilities
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_1)
         #Sensory
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item, is_set=True)   
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image, is_set=True)   
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice, is_set=True)   
        #Working
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item, is_set=True)   
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image, is_set=True)   
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice, is_set=True)   
        #LongTerm
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item, is_set=True)   
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image, is_set=True)   
        capabilities.setCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice, is_set=True)   

        muscle.setCapabilities(capabilities)
        
        # tearDown
        
        print('\ntearDown')       
        muscle.setLocations(RobotTestCase.LOCATIONS_1)
        muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        del muscle
        
        sense.setLocations(RobotTestCase.LOCATIONS_1)
        del sense

        del mainRobot
        
        

    def test_Routing(self):
        print('\ntest_Sensation Routing')
        #history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        
        ###########################################################################################################
        # sense       have LOCATIONS_EMPTY set
        # muscle      have LOCATIONS_EMPTY set
        # sensation   have LOCATIONS_EMPTY location set 
        # when we don't set locations in the Sensation, it gets local default location, which should be routed everywhere
        print('\n-sensation, none locations set, sense and muscle empty locations set match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
        # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True,
                            transferDirection=Sensation.TransferDirection.Up)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True,
                            transferDirection=Sensation.TransferDirection.Direct)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True,
                            transferDirection=Sensation.TransferDirection.Up)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True,
                            transferDirection=Sensation.TransferDirection.Direct)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False,
                            transferDirection=Sensation.TransferDirection.Up)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False,
                            transferDirection=Sensation.TransferDirection.Direct)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True,
                            transferDirection=Sensation.TransferDirection.Up)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True,
                            transferDirection=Sensation.TransferDirection.Direct)

        
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_2 set
        # sensation   does not set location
        # when we don't set locations in the Sensation, it gets local default location, which should be routed everywhere
        print('\n-sensation, none locations set, sense LOCATIONS_1 and muscle LOCATIONS_2 locations set match because Sensation location matters, but this is not realistic test')
        print('\n-sensation no locations set, sense don\'t match to muscle')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_2)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_2)
        #Locations don't match, but sensations don't have location so
        # same result than with previous case
        
        self.do_TestRouting(locations = None,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations = None,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations = None,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations = None,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)

        
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_2 set
        # sensation   have LOCATIONS_1 set
        # when senses locations does not match destination's locations, it is not routed
        print('\n-sensation, LOCATIONS_1 locations set, senseLOCATIONS_1 muscle  LOCATIONS_2 don\'t match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_2)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_2)
        # locations don't match so nothing is routed
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=False)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=False)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)

         
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_1 set
        # sensation   have LOCATIONS_1 set
        # when senses locations does not match destination's locations, it is  routed
        print('\n-sensation LOCATIONS_1 locations set, sense and muscle LOCATIONS_1 locations set match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
         
        ###########################################################################################################
        # sense       have LOCATIONS_GLOBAL set
        # muscle      have LOCATIONS_GLOBAL set
        # sensation   have LOCATIONS_GLOBAL set
        # when senses locations and sensation location match as global, it is  routed
        print('\n-sensation LOCATIONS_GLOBAL locations set, sense and muscle LOCATIONS_GLOBAL match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
        
        ###########################################################################################################
        # sense       have LOCATIONS_GLOBAL set
        # muscle      have LOCATIONS_EMPTY set
        # sensation   have LOCATIONS_EMPTY set
        # when senses locations and sensation location match as global, it is  routed
        print('\n-sensation LOCATIONS_GLOBAL locations set, sense and muscle LOCATIONS_EMPTY locations match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)

        ###########################################################################################################
        # sense       have LOCATIONS_EMPTY set
        # muscle      have LOCATIONS_GLOBAL set
        # sensation   have LOCATIONS_EMPTY set
        # when senses locations and sensation location match as global, it is  routed
        print('\n-sensation locations LOCATIONS_EMPTY set, sense LOCATIONS_EMPTY and muscle LOCATIONS_GLOBAL locations match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
       
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_GLOBAL set
        # sensation   have LOCATIONS_1 set
        # when senses locations and sensation location match as global, it is  routed
        print('\n-sensation LOCATIONS_1 locations set, sense LOCATIONS_1 and muscle LOCATIONS_GLOBAL locations match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
       
       
        ###########################################################################################################
        # sense       have LOCATIONS_GLOBAL set
        # muscle      have LOCATIONS_1 set
        # sensation   have LOCATIONS_GLOBAL set
        # when senses locations and sensation location match as global, it is  routed
        print('\n-Sensation LOCATIONS_GLOBAL locations set, sense LOCATIONS_GLOBAL and muscle LOCATIONS_1 match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
       
       
      # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_1_2 set
        # muscle      have LOCATIONS_1_2  set
        # sensation   have no locations set
        # when senses locations does not match destination's locations, it is  routed
        print('\n-sensation None locations set, sense LOCATIONS_1_2 and muscle LOCATIONS_1_2 locations set match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1_2)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1_2)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1_2)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_1_2 set
        # muscle      have LOCATIONS_1_2  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  routed
        print('\n-sensation LOCATIONS_1_2 locations set, sense LOCATIONS_1_2 and LOCATIONS_1_2 muscle locations set match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1_2)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1_2)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1_2)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_2_3 set
        # muscle      have LOCATIONS_2_3  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  routed
        print('\n-sensation LOCATIONS_1_2 locations set, sense LOCATIONS_2_3 and muscle .LOCATIONS_2_3y locations partial match, not realistic test')
        # if Sensation's and Robot's Locations partially match, sensation is routed
        self.sense.setLocations(RobotTestCase.LOCATIONS_2_3)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_2_3)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_2_3)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n-sensation LOCATIONS_1_2 locations set, sense LOCATIONS_3_4 and muscle LOCATIONS_3_4 locations set no match, not realistic test')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_3_4)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_3_4)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=False)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=False)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)

        # Many locations tests
        ###########################################################################################################
        # sense       have GLOBAL set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have GLOBAL  set
        # when senses GLOBA locations match all destination's locations, it is  routed
        print('\n-sensation LOCATIONS_GLOBAL locations set, sense LOCATIONS_GLOBAL and muscle LOCATIONS_3_4 locations set match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_3_4)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
        
        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_3_4  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n-sensation LOCATIONS_3_4 locations set, senseLOCATIONS_3_4 locations and muscle LOCATIONS_GLOBAL locations match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_3_4)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
        
        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_1_GLOBAL  set
        # sensation   have LOCATIONS_3_4  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n-sensation LOCATIONS_3_4 locations set, sense LOCATIONS_3_4 locations and muscle LOCATIONS_1_GLOBAL1 locations match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_3_4)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1_GLOBAL)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1_GLOBAL)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
        
        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_1_GLOBAL set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_GLOBAL  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n-sensation GLOBAL+1 locations set, sense GLOBAL+1 and muscle many locations match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
         # default case
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Sense,
                            shouldBeRouted=True)
        # capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Muscle,
                            shouldBeRouted=True)
        # no capability
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_1,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=False)
        
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_GLOBAL,
                            senseMainNames = self.MAINNAMES_1,
                            muscleMainNames = self.MAINNAMES_2,                          
                            robotType=Sensation.RobotType.Communication,
                            shouldBeRouted=True)
        
        
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after self.muscle.getAxon().get(robot=self)')
        
        # finally teardown
        # set locations as they were or other tests fail
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        
        
    '''
    helper for testing local routing     
    '''
    def do_TestRouting(self,
                       locations,
                       shouldBeRouted,
                       senseMainNames = MAINNAMES_1,
                       muscleMainNames = MAINNAMES_1,
                       robotType=Sensation.RobotType.Sense,
                       transferDirection=Sensation.TransferDirection.Up):
#                       isCommunication=False):
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.setRobotMainNames(robot=self.sense, mainNames=senseMainNames)
        self.setRobotMainNames(robot=self.muscle, mainNames=muscleMainNames)
        self.setRobotCapabilities(robot=self.muscle, robotTypes=[robotType])

        if locations == None:     
            Wall_E_item_sensation = self.sense.createSensation(
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=robotType,
                                                     name=RobotTestCase.NAME,
                                                     score=RobotTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Entering)
        else:
            Wall_E_item_sensation = self.sense.createSensation(
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=robotType,
                                                     name=RobotTestCase.NAME,
                                                     score=RobotTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Entering,
                                                     locations=locations)
# TODO tested somewhere else and this test is not valid
#         for location in Wall_E_item_sensation.getLocations():        
#             self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location)), 1, 'len(self.sense.getMemory().getPresentItemSensations({}))'.format(location))
#             print('len(self.sense.getMemory().getPresentItemSensations({})) == 1 OK'.format(location))
            
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty before we test')
        # test
#        self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)

#         self.sense.process(sensation=Wall_E_item_sensation, isRoutedToParent = False)
        # old routing
#         # should be routed to mainRobot
#         self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         # test routing to muscle
        # new star routing
        # should be routed to mainRobot
        self.assertTrue(self.mainRobot.getAxon().empty(),'mainRobot Axon should be empty')
        # test routing to muscle
        # should be routed to mainRobot
        if shouldBeRouted:
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#             sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
# TODO tested elswhere and this test is not valid
#             for location in sensation.getLocations():        
#                 self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location)), 1, 'len(self.sense.getMemory().getPresentItemSensations({}))'.format(location))
#                 self.assertEqual(len(self.muscle.getMemory().getPresentItemSensations(location)), 1, 'len(self.muscle.getMemory().getPresentItemSensations({}))'.format(location))
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')


    '''
    deprecated
    
    Same location test. but test cases where Robots, mainNames match and Not match
    If not match, the Different Robottype Sensation is routed, but not same
    Robottype sensation not
    '''            
    def re_test_MainNamesRouting(self):
        print('\ntest_Sensation Routing')
        #history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        
        ###########################################################################################################
        # sense       have LOCATIONS_EMPTY set
        # muscle      have LOCATIONS_EMPTY set
        # sensation   have None location set 
        # when we don't set locations in the Sensation, it gets local default location, which should be routed everywhere
        print('\n-sensation, none locations set, sense and muscle empty locations set match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Sense,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Sense,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Muscle,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Muscle,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Direct)
       
        # but if ensation.RobotType.Communication and MainNanes are same, it is not routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Communication,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Communication,
                                 shouldBeRouted=False,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Communication,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Communication,
                                 shouldBeRouted=False,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Muscle should NOT be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=False,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=False,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
        
        ### Now different MainnNames
        ### if Robottype != Communication, results are same
        ### but with Robottype == Communication we should success
        
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Sense,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Sense,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Muscle,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Muscle,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
        # but if ensation.RobotType.Communication and MainNanes are same, it is not routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Communication,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Communication,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Communication,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Communication,
                                 shouldBeRouted=True,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Muscle should NOT be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=False,
                                 transferDirection=Sensation.TransferDirection.Up)
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=False,
                                 transferDirection=Sensation.TransferDirection.Direct)
        
                
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after test')
#         
        # finally teardown
        # set locations as they were or other tests fail
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)

    '''
    helper for testing local routing with MainName   
    '''
    def do_MainNamesRouting(self,
                            locations,
                            senseMainNames,
                            senseRobotType,
                            muscleMainNames,
                            muscleRobotType,
                            shouldBeRouted,
                            transferDirection=Sensation.TransferDirection.Up):
        self.assertTrue(self.mainRobot.getAxon().empty(), 'mainRobot Axon should be empty at the beginning of do_MainNamesRoutin\nCannot test properly this!')
        self.assertTrue(self.sense.getAxon().empty(), 'sense Axon should be empty at the beginning of do_MainNamesRoutin\nCannot test properly this!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the beginning of do_MainNamesRoutin\nCannot test properly this!')

        self.sense.setMainNames(senseMainNames)
        self.muscle.setMainNames(muscleMainNames)
 
        # Clear sense capabilities so MainRobot does not route sensation back to it       
        self.setRobotCapabilities(robot=self.sense, robotTypes=[])

        self.setRobotCapabilities(robot=self.muscle, robotTypes=[muscleRobotType])
        
        
        if locations == None:     
            sense_sensation = self.sense.createSensation(
                                                     memoryType=Sensation.MemoryType.Sensory,
                                                     sensationType=Sensation.SensationType.Voice,
                                                     robotType=senseRobotType
                                                     )
        else:
            sense_sensation = self.sense.createSensation(
                                                     memoryType=Sensation.MemoryType.Sensory,
                                                     sensationType=Sensation.SensationType.Voice,
                                                     robotType=senseRobotType,
                                                     locations=locations)
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty before we test')
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=sense_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=sense_sensation)
#         self.sense.process(sensation=sense_sensation, isRoutedToParent=True)
        
        # old Up/down routing
#         # should be routed to mainRobot
#         self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         # test routing to muscle
#         self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # new Star routing
        self.assertTrue(self.mainRobot.getAxon().empty(),'mainRobot Axon should be empty')

        # test routing to the muscle
        if shouldBeRouted:
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#             sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
            
#         # new start routing    
#         # should NOT be routed to mainRobot
#         self.assertTrue(self.mainRobot.getAxon().empty(),'mainRobot Axon should be empty')
#         # test routing to muscle
#         # should be routed to mainRobot
#         if shouldBeRouted:
#             self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
#             tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#             self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
#         else:
#             self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')

# should not use tricks like this            
#     def reverserRobotType(self, robotType):
#         if robotType == Sensation.RobotType.Sense:
#             return Sensation.RobotType.Muscle
#         return Sensation.RobotType.Sense

       
    '''
    Tcp connection and routing. We test inside localhost SocketServer and SocketClient
    TODO This test is impossible to do with one MainRobot, because one MainRobot is not
    initiated to respond until it has send request to and we don't have mainRobot
    running to get its tested properly
    '''

    # re-enable this, when all other works
    # TODO if we run this test alone, it works, nut if we enable other test, we fail
    # other test ler local mainrebot keep running
    def test_Tcp(self):
        print('\n--test_Sensation Routing with TCP SocketServer and SocketClient')
        
        # set first remote mainRobot
        
        # set log level Detailed, so we know what is happening
        self.setUpRemote(mainNames=self.MAINNAMES_2)
        self.assertEqual(self.remoteMainRobot.getMainNames(),self.MAINNAMES_2, 'check 0 remote should know its own mainNames')
        
        self.remoteMainRobot.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        # create tcpServer same way as MainRpbot does it, but no hosts to connect, this is server only
        self.remoteMainRobot.tcpServer=TCPServer(
                                           mainRobot=self.remoteMainRobot,
                                           parent=self.remoteMainRobot,
                                           memory=self.remoteMainRobot.getMemory(),
                                           hostNames=[], # no hostnames to connect, we are server side
                                           instanceName='remoteTCPServer',
                                           instanceType=Sensation.InstanceType.Remote,
                                           level=self.remoteMainRobot.level,
                                           address=(Robot.HOST,Robot.PORT))
        
        # this is hard to test
        # we could also start self.remoteMainRobot 
        # but for test step by step, it is easier make only self.remoteMainRobot.tcpServer as running process 

        self.remoteMainRobot.tcpServer.start()        
        
        # set then local mainRobot
        
        # set log level Detailed, so we know what is happening
        self.mainRobot.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        
        # create tcpServe same way as MainRpbot does it, but connecting to localhost
        # but fake self.mainRobot server port, nobody will connect to it, we are connecting side
        
#         # We should sleep some time, because SockerServer and SocketClient read same config file
#         # and change it also. This would be a problem with many connections
        print("sleep {}".format(RobotTestCase.WAIT_STEP))
        time.sleep(RobotTestCase.WAIT_STEP)
        
        
        self.mainRobot.tcpServer=TCPServer(
                                           mainRobot=self.mainRobot,
                                           parent=self.mainRobot,
                                           memory=self.mainRobot.getMemory(),
                                           hostNames=[RobotTestCase.REMOTE_LOCALHOST],
                                           instanceName='localTCPServer',
                                           instanceType=Sensation.InstanceType.Remote,
                                           level=self.mainRobot.level,
                                           address=(Robot.HOST,RobotTestCase.FAKE_PORT)) # fake self.mainRobot server port, nobody will connect to it, we are connecting side
        # We try to connect running self.remoteMainRobot

        # added this to avoid other test setting failure
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)

        self.mainRobot.tcpServer.start()
        # We should sleep some time, because SockerServer and SocketClient read same config file
        # and change it also. This would be a problem with many connections
        print("sleep {}".format(RobotTestCase.WAIT_STEP))
        time.sleep(RobotTestCase.WAIT_STEP)

        
        # after this we test live processes, to we use WithWait -test6 methods
        print ('Wait tcpServer runs')
        # manual conditional wait
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while len(self.mainRobot.tcpServer.socketClients) == 0 \
              and len(self.remoteMainRobot.tcpServer.socketClients) == 0 \
              and time.time() < endTime:
            print ('Wait tcpServer runs time.sleep({} < {}'.format(time.time(), endTime))
            time.sleep(RobotTestCase.WAIT_STEP)
        
        # local 
        self.assertTrue(len(self.mainRobot.tcpServer.socketClients) > 0, 'should have local socketClient')        
        self.localSocketClient = self.mainRobot.tcpServer.socketClients[0]
        
        self.assertTrue(len(self.mainRobot.tcpServer.socketServers) > 0, 'should have local socketServer')        
        self.localSocketServer = self.mainRobot.tcpServer.socketServers[0]
        
        # test configuration
        self.assertEqual(self.mainRobot.tcpServer.getInstanceType(),Sensation.InstanceType.Remote)                
        self.assertEqual(self.localSocketClient.getInstanceType(),Sensation.InstanceType.Remote)
        
        # remote
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) > 0, 'should have remote socketClient')        
        self.remoteSocketClient = self.remoteMainRobot.tcpServer.socketClients[0]
        
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) > 0, 'should have remote socketServer')        
        self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
        
        # test configuration
        self.assertEqual(self.remoteMainRobot.tcpServer.getInstanceType(),Sensation.InstanceType.Remote)                
        self.assertEqual(self.remoteSocketClient.getInstanceType(),Sensation.InstanceType.Remote)
        
        # conditional wait for locations set
        endTime = time.time() + RobotTestCase.SLEEPTIME
#         print ("before while self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
#         print ("before while self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
        while (self.localSocketClient.getLocations() != RobotTestCase.LOCATIONS_1 or\
               self.remoteSocketClient.getLocations() != RobotTestCase.LOCATIONS_1 or\
               self.localSocketServer.getLocations() != RobotTestCase.LOCATIONS_1 or\
               self.remoteSocketServer.getLocations() != RobotTestCase.LOCATIONS_1) and\
              time.time() < endTime:
#             print ("while self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
#             print ("while self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
            print ('Wait LOCATIONS_1 time.sleep({} < {}'.format(time.time(), endTime))
            time.sleep(RobotTestCase.WAIT_STEP)
#         print ("self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
#         print ("self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
            
        # check    
        self.assertTrue(time.time() < endTime, 'check 1 should have got location '+ str(RobotTestCase.LOCATIONS_1) + ' but it is missing')
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 1 should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        # why (self.localSocketClient.getLocations() ['testLocation'] !=  self.remoteSocketClient.getLocations() ['testLocation', 'global']
        # this is first place when rhis check fails, but it variates


        #test getLocations
        # test test        
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1, 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketClient.getDownLocations(),self.remoteSocketClient.getDownLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketClient.getDownLocations(),RobotTestCase.LOCATIONS_1, 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        # test       
        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.remoteSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.localSocketServer.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.remoteSocketServer.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')

        # test isInLocations        
        self.assertTrue(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))
        
        
        # check    

        # test test        
        # set log level Detailed, so we know what is happening
        self.remoteSocketClient.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 1,'should have socketServer')        
        self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
        
        self.assertTrue(self.localSocketClient in self.mainRobot.subInstances,'mainRobot should know localSocketClient')        
        self.assertTrue(self.remoteSocketClient in self.remoteMainRobot.subInstances,'remoteMainRobot should know remoteSocketClient')        
        self.assertFalse(self.localSocketServer in self.mainRobot.subInstances,'mainRobot should know localSocketServer')        
        self.assertFalse(self.remoteSocketServer in self.remoteMainRobot.subInstances,'remoteMainRobot should know self.remoteSocketServer')
        self.assertEqual(len(self.mainRobot.subInstances),3, 'mainRobot should know 3 subInstances')
               
        
        
        # conditional wait for first assert for capabilities
        print ('Wait self.remoteMainRobot and SocketServers runs')
        
        # check
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 3 should have equal local and remote location')

        capabilities  =  self.localSocketClient.getCapabilities()
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while not capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item) and time.time() < endTime:
            print ('Wait localSocketClient capabilities time.sleep({} < {}'.format(time.time(), endTime))
            time.sleep(RobotTestCase.WAIT_STEP)
            capabilities  =  self.localSocketClient.getCapabilities()
        # check
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 4 should have equal local and remote location')
 
        capabilities  =  self.remoteSocketClient.getCapabilities()
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while not capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item) and time.time() < endTime:
            print ('Wait remoteSocketClient capabilities time.sleep({} < {}'.format(time.time(), endTime))
            time.sleep(RobotTestCase.WAIT_STEP)
            capabilities  =  self.remoteSocketClient.getCapabilities()

        # check
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 5 should have equal local and remote location')
        # check
        #self.assertEqual(self.localSocketClient.getMainNames(),self.MAINNAMES_2, 'check 6 local should know remote mainNames')
        # check
        self.assertEqual(self.remoteSocketClient.getMainNames(),self.MAINNAMES_1, 'check 7 remoteSocketClient should know local mainNames')
        self.assertEqual(self.remoteMainRobot.getMainNames(),self.MAINNAMES_2, 'check 8 remoteMainRobot should know its own remote mainNames')
        self.assertEqual(self.localSocketClient.getMainNames(),self.MAINNAMES_2, 'check 9 localSocketClient should know remote mainNames')
        self.assertEqual(self.mainRobot.getMainNames(),self.MAINNAMES_1, 'check 10 local mainRobot should know its own local mainNames')
        # why (self.localSocketClient.getLocations() ['testLocation'] !=  self.remoteSocketClient.getLocations() ['testLocation', 'global']
        # remotes location has been changed
       
        
        # at this point we should have got back Robot sensation from self.remoteMainRobot
        # as well as capabilities
        
        # check Local Capabilities
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.localSocketClient.getCapabilities()
        # Sense
        # Sensory
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
        #Working
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
        #LongTerm
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
        
        # Communication
        # Sensory
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
        # Working
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
        #LongTerm
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     

       # local and remote capabilities should be equal        
        self.assertEqual(self.localSocketClient.getCapabilities(),self.localSocketServer.getCapabilities(), 'should have equal local capabilities')        
        self.assertEqual(self.remoteSocketClient.getCapabilities(),self.remoteSocketServer.getCapabilities(), 'should have equal remote capabilities')        
        #self.assertEqual(self.localSocketClient.getCapabilities().toString(),self.remoteSocketClient.getCapabilities().toString(), 'should have equal local and remote capabilities')        
        #self.assertEqual(self.localSocketServer.getCapabilities().toString(),self.remoteSocketServer.getCapabilities().toString(), 'should have equal local and remote capabilities')        
        # location should be equal now
        self.assertEqual(self.localSocketClient.getLocations(),self.localSocketServer.getLocations(), 'should have equal local location')        
        self.assertEqual(self.remoteSocketClient.getDownLocations(),self.remoteSocketServer.getDownLocations(), 'should have equal remote down location')        
        #self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketServer.getDownLocations(),self.remoteSocketServer.getDownLocations(), 'should have equal local and remote down location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']      
        self.assertEqual(self.localSocketServer.getLocations(),self.remoteSocketServer.getLocations(), 'should have equal local and remote location')
        

        # remote muscle should have it's capabilities
        capabilities  =  self.remoteMuscle.getCapabilities()
        # Sense
        # Sensory
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
        # Working
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
        # LongTerm
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
        
        # Communication
        # Sensory
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
        #Working
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
        #LongTerm
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
        
        
        # Finally we have tested that capabilities and locations are OK for testing
        # Ready to test routing a sensation.
        # test both positive and negative cases
        
        self.do_remote_positive_case(remoteMainRobot = self.remoteMainRobot,
                                  remoteSense = self.remoteSense,
                                  remoteMuscle = self.remoteMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp = True,
                                  transferDirection=Sensation.TransferDirection.Up)
        self.do_remote_positive_case(remoteMainRobot = self.remoteMainRobot,
                                  remoteSense = self.remoteSense,
                                  remoteMuscle = self.remoteMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp = True,
                                  transferDirection=Sensation.TransferDirection.Direct)
       # negative case
        self.do_remote_negative_case(remoteMainRobot = self.remoteMainRobot,
                                  remoteSense = self.remoteSense,
                                  remoteMuscle = self.remoteMuscle,
                                  robotType=Sensation.RobotType.Sense,
                                  isSentLocal = True,
                                  isSentRemote = True,
                                  isTcp = True,
                                  transferDirection=Sensation.TransferDirection.Up)
        self.do_remote_negative_case(remoteMainRobot = self.remoteMainRobot,
                                  remoteSense = self.remoteSense,
                                  remoteMuscle = self.remoteMuscle,
                                  robotType=Sensation.RobotType.Sense,
                                  isSentLocal = True,
                                  isSentRemote = True,
                                  isTcp = True,
                                  transferDirection=Sensation.TransferDirection.Direct)
        #self.do_remote_negative_case(robotType=Sensation.RobotType.Muscle,
        self.do_remote_negative_case(remoteMainRobot = self.remoteMainRobot,
                                  remoteSense = self.remoteSense,
                                  remoteMuscle = self.remoteMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp = True,
                                  transferDirection=Sensation.TransferDirection.Up)
        self.do_remote_negative_case(remoteMainRobot = self.remoteMainRobot,
                                  remoteSense = self.remoteSense,
                                  remoteMuscle = self.remoteMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp = True,
                                  transferDirection=Sensation.TransferDirection.Direct)


        # done
        # local should be stopped manually
        self.mainRobot.tcpServer.stop()
        self.localSocketClient.stop()        
        self.localSocketServer.stop()
        
        # remote should be stopped manually
        self.remoteMainRobot.tcpServer.stop()
        self.remoteSocketClient.stop()        
        self.remoteSocketServer.stop()
        
       
        print ('Sleep {}s to wait self.remoteMainRobot and self.mainRobot.tcpServer, localSocketServer and localSocketClient to stop'.format(RobotTestCase.SLEEPTIME))

        time.sleep(RobotTestCase.SLEEPTIME)
        
        self.tearDownRemote()
        
        # del all
        del self.mainRobot.tcpServer
        # remote should be deletes in self.tearDownRemote
        #del self.remoteMainRobot.tcpServer       
    '''
    tcp positive case
    test same location localSocket , remoteSocket, sense, muscle
    '''    
        
#    def do_remote_positive_case(self, robotType, isCommunication, isSentLocal, isSentRemote):
    def do_remote_positive_case(self,
                             remoteMainRobot,
                             remoteSense,
                             remoteMuscle,
                             robotType,
                             isSentLocal,
                             isSentRemote,
                             isTcp,
                             transferDirection=Sensation.TransferDirection.Up):
        print('\n-test tcp positive case')
        history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL
        
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'mainRobotAxon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        if True:#isSentRemote:
            self.assertTrue(remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
            self.assertTrue(remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n--too old_Presense')
        # normal sensation with location, this should success
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.sense.getLocations())
        self.assertEqual(Wall_E_item_sensation.getMainNames(), self.MAINNAMES_1, 'Sensation to send should be created with local mainnames')
        self.assertEqual(remoteMuscle.getMainNames(), self.MAINNAMES_2, 'remoteMuscle should be created with remote mainnames')
        self.do_remote_positive_case_sensation(remoteMainRobot = remoteMainRobot,
                                            remoteSense = remoteSense,
                                            remoteMuscle = remoteMuscle,
                                            sensationToSend = Wall_E_item_sensation,
                                            isSentLocal = isSentLocal,
                                            isSentRemote = isSentRemote,
                                            isTcp=isTcp,
                                            transferDirection=transferDirection)
        
        #  global sensation, that goes every location, this should success
        Wall_E_item_sensation_global_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=RobotTestCase.LOCATIONS_GLOBAL)
        self.do_remote_positive_case_sensation(remoteMainRobot = remoteMainRobot,
                                            remoteSense = remoteSense,
                                            remoteMuscle = remoteMuscle,
                                            sensationToSend = Wall_E_item_sensation_global_location,
                                            isSentLocal = isSentLocal,
                                            isSentRemote = isSentRemote,
                                            isTcp=isTcp,
                                            transferDirection=transferDirection)
        
        # local global sensation, that goes every location in local robot, but should not be sent to Remote Robot
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=[])
        self.do_remote_positive_case_sensation(remoteMainRobot = remoteMainRobot,
                                                remoteSense = remoteSense,
                                                remoteMuscle = remoteMuscle,
                                                sensationToSend = Wall_E_item_sensation_no_location,
                                                isSentLocal = isSentLocal,
                                                isSentRemote = False,
                                                isTcp=isTcp,
                                                transferDirection=transferDirection)

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'mainRobotAxon should be empty at the end of test!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the end of test!')
        if True:#isSentRemote:
            self.assertTrue(remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the end of test!')
            self.assertTrue(remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the should be empty at the end of test!')
#         # test test
#         self.assertEqual(Wall_E_item_sensation_no_location.getLocations(), RobotTestCase.LOCATIONS_EMPTY)
#         # test
#         self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation_no_location,
#                                             isSentLocal = True)
       

    def do_remote_positive_case_sensation(self,
                                       remoteMainRobot,
                                       remoteSense,
                                       remoteMuscle,
                                       sensationToSend,
                                       isSentLocal,
                                       isSentRemote,
                                       isTcp,
                                       transferDirection=Sensation.TransferDirection.Up):
        self.assertTrue(self.mainRobot.getAxon().empty(), 'mainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        if True:#isSentRemote:
            self.assertTrue(remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
            print("1. remoteMainRobot.getAxon().empty()")
            self.assertTrue(remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
       
        self.assertEqual(sensationToSend.getReceivedFrom(), [], 'local sensation should not have receivedFrom information at the beginning of test')
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
#         self.sense.process(transferDirection=transferDirection, sensation=sensationToSend)
        self.sense.sense(transferDirection=transferDirection, sensation=sensationToSend)
#         self.sense.process(sensation=sensationToSend,isRoutedToParent=False)
        # old Up/down routing
#             # should be routed to mainRobot
#         self.assertFalse(self.mainRobot.getAxon().empty(), 'local mainRobot Axon should be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
#         self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
#         self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)

        # new star routing       
        # process   
        self.assertTrue(self.mainRobot.getAxon().empty(), 'local mainRobot Axon should be empty')
        if isSentLocal:
             # test test here
            self.assertTrue(self.muscle in self.mainRobot.getCapabilityInstances(robotType = sensationToSend.getRobotType(),
                                                                                 memoryType = sensationToSend.getMemoryType(),
                                                                                 sensationType = sensationToSend.getSensationType(),
                                                                                 locations = sensationToSend.getLocations(),
                                                                                 mainNames = sensationToSend.getMainNames()))
           # test routing to muscle
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#             sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
            self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
            self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
            
            for location in sensationToSend.getLocations():       
                self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location=location)), 1, 'len(self.sense.getMemory().getPresentItemSensations({}) should be 1'.format(location))
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')

        # test routing to remote muscle from local sense 
        if isTcp:
            print ('Wait Sensation is transferred by remote')
         
            # conditional wait              
            endTime = time.time() + RobotTestCase.SLEEPTIME
            
    #         while remoteMainRobot.getAxon().empty() and time.time() < endTime:
            while remoteMuscle.getAxon().empty() and time.time() < endTime:
                print ('Wait Sensation is transferred by remote time.sleep({} < {}'.format(time.time(), endTime))
                time.sleep(RobotTestCase.WAIT_STEP)
    
        if isSentRemote:
            
            # test test here TODO Cant test like this,
            # because we test also no location and then there are no getCapabilityInstances
#             self.assertTrue(remoteMuscle in remoteMainRobot.getCapabilityInstances(robotType = sensationToSend.getRobotType(),
#                                                                                              memoryType = sensationToSend.getMemoryType(),
#                                                                                              sensationType = sensationToSend.getSensationType(),
#                                                                                              locations = sensationToSend.getLocations(),
#                                                                                              mainNames = sensationToSend.getMainNames()))
            
            
            # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
#             self.assertFalse(remoteMainRobot.getAxon().empty(),'remoteMainRobot Axon should not be empty')
#             tranferDirection, sensation = remoteMainRobot.getAxon().get(robot=self)
# #             sensation, isRoutedToParent = remoteMainRobot.getAxon().get(robot=self)
#             
#             self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
#             self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
#     
#             # test routing to remoteMuscle
#             remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
            self.assertFalse(remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
            tranferDirection, sensation = remoteMuscle.getAxon().get(robot=self)
#             sensation, isRoutedToParent = remoteMuscle.getAxon().get(robot=self)
            
            # test, that sensation is same than transferred
            self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
            self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')           
            # test, that local sensation to be transferred does not contain  receicedFrom information
            self.assertEqual(sensationToSend.getReceivedFrom(), [], 'local sensation should not have receivedFrom information')
    
            # test, that remote sensation transferred does contain  receicedFron information
            if isTcp:
                self.assertEqual(sensation.getReceivedFrom(), [RobotTestCase.LOCALHOST], 'remote sensation should have receivedFrom information')
    
            # now muscle should not have more sensations
            self.assertTrue(remoteMuscle.getAxon().empty(),'remote muscle Axon should be empty')
        

            # test routing remote got sensation back from remote to local
        
            remoteSense.process(transferDirection=transferDirection, sensation=sensation)
            remoteSense.route(transferDirection=transferDirection, sensation=sensation)
            # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
            # old routing
#             self.assertFalse(remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
#             tranferDirection, sensation = remoteMainRobot.getAxon().get(robot=self)
# 
#             # test routing to remoteMuscle
#             remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)

            self.assertFalse(remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
            tranferDirection, sensation = remoteMuscle.getAxon().get(robot=self)
#             sensation, isRoutedToParent = remoteMuscle.getAxon().get(robot=self)
            self.assertTrue(remoteMuscle.getAxon().empty(),'remoteMuscle Axon should be empty')
        
            # but routing to local should fail. because we have got this sensation from local and receivedFrom contains that information
        if isSentRemote:
            if isTcp:
                print ('Wait Sensation is transferred by remote')
        
                # conditional wait               
                endTime = time.time() + RobotTestCase.SLEEPTIME
                while not self.mainRobot.getAxon().empty() and time.time() < endTime:
                    time.sleep(RobotTestCase.WAIT_STEP)
            self.assertTrue(remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty!')
    
            # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
            self.assertTrue(self.mainRobot.getAxon().empty(),'localMainRobot Axon should be empty')
        else:
            # remote SocketServer should not have got it and when it is living process, it has not put it to remoteMainRobot
            #self.assertTrue(remoteMainRobot.getAxon().empty(),'remoteMainRobot Axon should be empty')
            self.assertTrue(remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty')
            self.assertTrue(remoteSense.getAxon().empty(), 'remoteMuscle Axon should be empty')

       
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'mainRobotAxon should be empty at the end of test!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the end of test!')
        self.assertTrue(self.sense.getAxon().empty(), 'sense Axon should be empty at the end of test!')

        self.assertTrue(remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the end of test!')
        self.assertTrue(remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the end of test!')
        self.assertTrue(remoteSense.getAxon().empty(), 'remoteSense Axon should be empty at the end of test!')
           
    '''
    tcp negative case
    '''
    def do_remote_negative_case(self,
                             remoteMainRobot,
                             remoteSense,
                             remoteMuscle,
                             robotType,
                             isSentLocal,
                             isSentRemote,
                             isTcp,
                             transferDirection=Sensation.TransferDirection.Direct):
        ###################################################################################################################################################
        # tcp negative case
        # localSocketServer has different location
        #
        print('\n-test tcp negative case, localSocketServer has different location')
        history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL
        
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        
        ################ test same location sense, muscle ####################
        ################ test same location localSocket , remoteSocket ####################
        ################ but location localSocket , remoteSocket differs ####################
        
        ################ change local localSocketServer location, so localSocketClient should not capability to handle this message ####################        
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.sense.getLocations())
        for location in Wall_E_item_sensation.getLocations():       
            self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location=location)), 1, 'len(self.sense.getMemory().getPresentItemSensations({}) should be 1'.format(location))
        # with sensation, that has different location the srcSocker we should fail       
         
        # local global sensation, that goes every location in local robot, but not with remote robots
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=[])

        for location in Wall_E_item_sensation_no_location.getLocations():       
            self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location=location)), 1, 'len(self.sense.getMemory().getPresentItemSensations({}) should be 1'.format(location))

        self.assertTrue(remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should be empty BEFORE we test')
        self.assertEqual(Wall_E_item_sensation.getLocations(), RobotTestCase.LOCATIONS_1, 'sensation should have location {} BEFORE we test'.format(RobotTestCase.LOCATIONS_1))
        if isTcp:
        # set locations
            self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_2)
            self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_2)
        else:
            remoteMuscle.setLocations(RobotTestCase.LOCATIONS_2)
            remoteMuscle.setDownLocations(RobotTestCase.LOCATIONS_2)
       
        
        # with different location we should fail
        self.do_tcp_negative_case_sensation(remoteMainRobot,
                                            remoteSense,
                                            remoteMuscle,
                                            sensationToSend = Wall_E_item_sensation,
                                            isSentLocal = isSentLocal,
                                            isTcp = isTcp,
                                            transferDirection = transferDirection)

        # with local global sensation should fail
        self.do_tcp_negative_case_sensation(remoteMainRobot,
                                                remoteSense,
                                                remoteMuscle,
                                                sensationToSend = Wall_E_item_sensation_no_location,
                                                isSentLocal = isSentLocal,
                                                isTcp = isTcp,
                                                transferDirection = transferDirection)
        
        # set receiving robot as global setting its location empty these
        # set locations
        if isTcp:       
            self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
            self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
        remoteMuscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        remoteMuscle.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
        
        # with sensation with different location we should success, because receiver accepts all        
        self.do_remote_positive_case_sensation(remoteMainRobot,
                                            remoteSense,
                                            remoteMuscle,
                                            sensationToSend = Wall_E_item_sensation,
                                            isSentLocal=isSentLocal,
                                            isSentRemote=isSentRemote,
                                            isTcp = isTcp,
                                            transferDirection=transferDirection)
        # with global sensation, that goes every location, we should success        
        self.do_remote_positive_case_sensation(remoteMainRobot,
                                            remoteSense,
                                            remoteMuscle,
                                            sensationToSend = Wall_E_item_sensation_no_location,
                                            isSentLocal=isSentLocal,
                                            isSentRemote=isSentRemote,
                                            isTcp = isTcp,
                                            transferDirection=transferDirection)
        
        # set locations back
        if isTcp:       
            self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_1)
            self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_1)
        remoteMuscle.setLocations(RobotTestCase.LOCATIONS_1)
        remoteMuscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        #localSocketClient.setLocations(RobotTestCase.LOCATIONS_1)
        
        
    '''
    do_tcp_negative_case_sensation
    '''    
       
    def do_tcp_negative_case_sensation(self,
                                       remoteMainRobot,
                                       remoteSense,
                                       remoteMuscle,                                       
                                       sensationToSend,
                                       isSentLocal,
                                       isTcp,
                                       transferDirection=Sensation.TransferDirection.Up):
        
#         self.sense.process(transferDirection=transferDirection, sensation=sensationToSend)
        self.sense.sense(transferDirection=transferDirection, sensation=sensationToSend)
        # old routing
        # should be routed to mainRobot
#         self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         
#         self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)

        # new star routing
        self.assertTrue(self.mainRobot.getAxon().empty(),'mainRobot Axon should be empty')
        
        # test routing to muscle
        if isSentLocal:
            # should be routed to mainRobot
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#             sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')

            
        # remote SocketServer should have NOT got it and when it is living process, it has NOT put it to remoteMainRobot
        if isTcp:       
            # conditional wait
            print ('Wait Sensation is transferred by remote')
            endTime = time.time() + RobotTestCase.SLEEPTIME
            while remoteMuscle.getAxon().empty() and time.time() < endTime:
                print ('Wait remoteMuscle.getAxon() time.sleep({} < {}'.format(time.time(), endTime))
                time.sleep(RobotTestCase.WAIT_STEP)
        
        self.assertTrue(remoteMuscle.getAxon().empty(),'remoteMuscle Axon should be empty')

        # TODO presence does not change in this test so this is basically obsolote test
        # but it should be true
        if isSentLocal:
            for location in sensationToSend.getLocations():        
                self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location = location)), 1, 'len(self.sense.getMemory().presentItemSensations(location = {}) should be 1'.format(location))
        else:
             for location in sensationToSend.getLocations():
                self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location = location)), 1, 'len(self.sense.getMemory().presentItemSensations(location = {}) should be 0'.format(location))


    '''
    Test Virtual Robot
    '''
    '''
    Tcp connection and routing. We test inside localhost SocketServer and SocketClient
    TODO This test is impossible to do with one MainRobot, because one MainRobot is not
    initiated to respond until it has send request to and we don't have mainRobot
    running to get its tested properly
    '''

    # re-enable this, when all other works
    # TODO if we run this test alone, it works, nut if we enable other test, we fail
    # other test ler local mainrebot keep running
    def test_Virtual(self):
        print('\n--test_Sensation Routing with Virtual Robot')
        
        # set first virtual mainRobot
        
        # set log level Detailed, so we know what is happening
        self.setUpVirtual(mainNames=self.MAINNAMES_2)
        self.assertEqual(self.virtualMainRobot.getMainNames(),self.MAINNAMES_2, 'check 0 virtual should know its own mainNames')
        
        self.virtualMainRobot.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        # create tcpServer same way as MainRpbot does it, but no hosts to connect, this is server only
#         self.remoteMainRobot.tcpServer=TCPServer(
#                                            mainRobot=self.remoteMainRobot,
#                                            parent=self.remoteMainRobot,
#                                            memory=self.remoteMainRobot.getMemory(),
#                                            hostNames=[], # no hostnames to connect, we are server side
#                                            instanceName='remoteTCPServer',
#                                            instanceType=Sensation.InstanceType.Remote,
#                                            level=self.remoteMainRobot.level,
#                                            address=(HOST,PORT))
#         
#         # this is hard to test
#         # we could also start self.remoteMainRobot 
#         # but for test step by step, it is easier make only self.remoteMainRobot.tcpServer as running process 
# 
#         self.remoteMainRobot.tcpServer.start()        
#         
#         # set then local mainRobot
#         
#         # set log level Detailed, so we know what is happening
#         self.mainRobot.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
#         
#         # create tcpServe same way as MainRpbot does it, but connecting to localhost
#         # but fake self.mainRobot server port, nobody will connect to it, we are connecting side
#         
# #         # We should sleep some time, because SockerServer and SocketClient read same config file
# #         # and change it also. This would be a problem with many connections
#         print("sleep {}".format(RobotTestCase.WAIT_STEP))
#         time.sleep(RobotTestCase.WAIT_STEP)
#         
#         
#         self.mainRobot.tcpServer=TCPServer(
#                                            mainRobot=self.mainRobot,
#                                            parent=self.mainRobot,
#                                            memory=self.mainRobot.getMemory(),
#                                            hostNames=[RobotTestCase.REMOTE_LOCALHOST],
#                                            instanceName='localTCPServer',
#                                            instanceType=Sensation.InstanceType.Remote,
#                                            level=self.mainRobot.level,
#                                            address=(HOST,RobotTestCase.FAKE_PORT)) # fake self.mainRobot server port, nobody will connect to it, we are connecting side
#         # We try to connect running self.remoteMainRobot
# 
#         # added this to avoid other test setting failure
#         self.sense.setLocations(RobotTestCase.LOCATIONS_1)
#         self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
# 
#         self.mainRobot.tcpServer.start()
#         # We should sleep some time, because SockerServer and SocketClient read same config file
#         # and change it also. This would be a problem with many connections
#         print("sleep {}".format(RobotTestCase.WAIT_STEP))
#         time.sleep(RobotTestCase.WAIT_STEP)
# 
#         
#         # after this we test live processes, to we use WithWait -test6 methods
#         print ('Wait tcpServer runs')
#         # manual conditional wait
#         endTime = time.time() + RobotTestCase.SLEEPTIME
#         while len(self.mainRobot.tcpServer.socketClients) == 0 \
#               and len(self.remoteMainRobot.tcpServer.socketClients) == 0 \
#               and time.time() < endTime:
#             print ('Wait tcpServer runs time.sleep({} < {}'.format(time.time(), endTime))
#             time.sleep(RobotTestCase.WAIT_STEP)
#         
#         # local 
#         self.assertTrue(len(self.mainRobot.tcpServer.socketClients) > 0, 'should have local socketClient')        
#         self.localSocketClient = self.mainRobot.tcpServer.socketClients[0]
#         
#         self.assertTrue(len(self.mainRobot.tcpServer.socketServers) > 0, 'should have local socketServer')        
#         self.localSocketServer = self.mainRobot.tcpServer.socketServers[0]
#         
#         # test configuration
#         self.assertEqual(self.mainRobot.tcpServer.getInstanceType(),Sensation.InstanceType.Remote)                
#         self.assertEqual(self.localSocketClient.getInstanceType(),Sensation.InstanceType.Remote)
#         
#         # remote
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) > 0, 'should have remote socketClient')        
#         self.remoteSocketClient = self.remoteMainRobot.tcpServer.socketClients[0]
#         
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) > 0, 'should have remote socketServer')        
#         self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
#         
        # test configuration
        self.assertEqual(self.virtualMainRobot.getInstanceType(),Sensation.InstanceType.Virtual)                
#         self.assertEqual(self.virtualMainRobot.tcpServer.getInstanceType(),Sensation.InstanceType.Virtual)                
#         self.assertEqual(self.remoteSocketClient.getInstanceType(),Sensation.InstanceType.Remote)
#         
#         # conditional wait for locations set
#         endTime = time.time() + RobotTestCase.SLEEPTIME
# #         print ("before while self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
# #         print ("before while self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
#         while (self.localSocketClient.getLocations() != RobotTestCase.LOCATIONS_1 or\
#                self.remoteSocketClient.getLocations() != RobotTestCase.LOCATIONS_1 or\
#                self.localSocketServer.getLocations() != RobotTestCase.LOCATIONS_1 or\
#                self.remoteSocketServer.getLocations() != RobotTestCase.LOCATIONS_1) and\
#               time.time() < endTime:
# #             print ("while self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
# #             print ("while self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
#             print ('Wait LOCATIONS_1 time.sleep({} < {}'.format(time.time(), endTime))
#             time.sleep(RobotTestCase.WAIT_STEP)
# #         print ("self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
# #         print ("self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
#             
#         # check    
#         self.assertTrue(time.time() < endTime, 'check 1 should have got location '+ str(RobotTestCase.LOCATIONS_1) + ' but it is missing')
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 1 should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
#         # why (self.localSocketClient.getLocations() ['testLocation'] !=  self.remoteSocketClient.getLocations() ['testLocation', 'global']
#         # this is first place when rhis check fails, but it variates
# 
# 
#         #test getLocations
#         # test test        
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
#         self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1, 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
#         self.assertEqual(self.localSocketClient.getDownLocations(),self.remoteSocketClient.getDownLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
#         self.assertEqual(self.localSocketClient.getDownLocations(),RobotTestCase.LOCATIONS_1, 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
#         # test       
#         self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
#         self.assertEqual(self.remoteSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
#         self.assertEqual(self.localSocketServer.getLocations(),RobotTestCase.LOCATIONS_1)
#         self.assertEqual(self.remoteSocketServer.getLocations(),RobotTestCase.LOCATIONS_1)
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')
# 
#         # test isInLocations        
#         self.assertTrue(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))
#         
#         
#         # check    
# 
#         # test test        
#         # set log level Detailed, so we know what is happening
#         self.remoteSocketClient.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 1,'should have socketServer')        
#         self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
#         
#         self.assertTrue(self.localSocketClient in self.mainRobot.subInstances,'mainRobot should know localSocketClient')        
#         self.assertTrue(self.remoteSocketClient in self.remoteMainRobot.subInstances,'remoteMainRobot should know remoteSocketClient')        
#         self.assertFalse(self.localSocketServer in self.mainRobot.subInstances,'mainRobot should know localSocketServer')        
#         self.assertFalse(self.remoteSocketServer in self.remoteMainRobot.subInstances,'remoteMainRobot should know self.remoteSocketServer')
#         self.assertEqual(len(self.mainRobot.subInstances),3, 'mainRobot should know 3 subInstances')
#                
#         
#         
#         # conditional wait for first assert for capabilities
#         print ('Wait self.remoteMainRobot and SocketServers runs')
#         
#         # check
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 3 should have equal local and remote location')
# 
#         capabilities  =  self.localSocketClient.getCapabilities()
#         endTime = time.time() + RobotTestCase.SLEEPTIME
#         while not capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item) and time.time() < endTime:
#             print ('Wait localSocketClient capabilities time.sleep({} < {}'.format(time.time(), endTime))
#             time.sleep(RobotTestCase.WAIT_STEP)
#             capabilities  =  self.localSocketClient.getCapabilities()
#         # check
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 4 should have equal local and remote location')
#  
#         capabilities  =  self.remoteSocketClient.getCapabilities()
#         endTime = time.time() + RobotTestCase.SLEEPTIME
#         while not capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item) and time.time() < endTime:
#             print ('Wait remoteSocketClient capabilities time.sleep({} < {}'.format(time.time(), endTime))
#             time.sleep(RobotTestCase.WAIT_STEP)
#             capabilities  =  self.remoteSocketClient.getCapabilities()
# 
#         # check
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 5 should have equal local and remote location')
#         # check
#         #self.assertEqual(self.localSocketClient.getMainNames(),self.MAINNAMES_2, 'check 6 local should know remote mainNames')
#         # check
#         self.assertEqual(self.remoteSocketClient.getMainNames(),self.MAINNAMES_1, 'check 7 remoteSocketClient should know local mainNames')
        self.assertEqual(self.virtualMainRobot.getMainNames(),self.MAINNAMES_2, 'check 8 virtualMainRobot should know its own remote mainNames')
#         self.assertEqual(self.localSocketClient.getMainNames(),self.MAINNAMES_2, 'check 9 localSocketClient should know remote mainNames')
#         self.assertEqual(self.mainRobot.getMainNames(),self.MAINNAMES_1, 'check 10 local mainRobot should know its own local mainNames')
#         # why (self.localSocketClient.getLocations() ['testLocation'] !=  self.remoteSocketClient.getLocations() ['testLocation', 'global']
#         # remotes location has been changed
#        
#         
#         # at this point we should have got back Robot sensation from self.remoteMainRobot
#         # as well as capabilities
#         
#         # check Local Capabilities
#         #set muscle capabilities  Item, Image, Voice
#         capabilities  =  self.localSocketClient.getCapabilities()
#         # Sense
#         # Sensory
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
#         #Working
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
#         #LongTerm
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
#         
#         # Communication
#         # Sensory
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
#         # Working
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
#         #LongTerm
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
#         self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
# 
#        # local and remote capabilities should be equal        
#         self.assertEqual(self.localSocketClient.getCapabilities(),self.localSocketServer.getCapabilities(), 'should have equal local capabilities')        
#         self.assertEqual(self.remoteSocketClient.getCapabilities(),self.remoteSocketServer.getCapabilities(), 'should have equal remote capabilities')        
#         #self.assertEqual(self.localSocketClient.getCapabilities().toString(),self.remoteSocketClient.getCapabilities().toString(), 'should have equal local and remote capabilities')        
#         #self.assertEqual(self.localSocketServer.getCapabilities().toString(),self.remoteSocketServer.getCapabilities().toString(), 'should have equal local and remote capabilities')        
#         # location should be equal now
#         self.assertEqual(self.localSocketClient.getLocations(),self.localSocketServer.getLocations(), 'should have equal local location')        
#         self.assertEqual(self.remoteSocketClient.getDownLocations(),self.remoteSocketServer.getDownLocations(), 'should have equal remote down location')        
#         #self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
#         self.assertEqual(self.localSocketServer.getDownLocations(),self.remoteSocketServer.getDownLocations(), 'should have equal local and remote down location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']      
#         self.assertEqual(self.localSocketServer.getLocations(),self.remoteSocketServer.getLocations(), 'should have equal local and remote location')
#         
# 
        # virtual muscle should have it's capabilities
        capabilities  =  self.virtualMuscle.getCapabilities()
        # Sense
        # Sensory
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
        # Working
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
        # LongTerm
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
         
        # Communication
        # Sensory
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item))  
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice))    
        #Working
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.Working, sensationType=Sensation.SensationType.Voice))    
        #LongTerm
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Item))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Image))    
        self.assertTrue(capabilities.hasCapability(robotType=Sensation.RobotType.Communication, memoryType=Sensation.MemoryType.LongTerm, sensationType=Sensation.SensationType.Voice))     
#         
#         
#         # Finally we have tested that capabilities and locations are OK for testing
#         # Ready to test routing a sensation.
#         # test both positive and negative cases
#         
        self.do_remote_positive_case(remoteMainRobot = self.virtualMainRobot,
                                  remoteSense = self.virtualSense,
                                  remoteMuscle = self.virtualMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp=False,
                                  transferDirection=Sensation.TransferDirection.Up)
        self.do_remote_positive_case(remoteMainRobot = self.virtualMainRobot,
                                  remoteSense = self.virtualSense,
                                  remoteMuscle = self.virtualMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp=False,
                                  transferDirection=Sensation.TransferDirection.Direct)
#        # negative case
        self.do_remote_negative_case(remoteMainRobot = self.virtualMainRobot,
                                  remoteSense = self.virtualSense,
                                  remoteMuscle = self.virtualMuscle,
                                  robotType=Sensation.RobotType.Sense,
                                  isSentLocal = True,
                                  isSentRemote = True,
                                  isTcp=False,
                                  transferDirection=Sensation.TransferDirection.Up)
        self.do_remote_negative_case(remoteMainRobot = self.virtualMainRobot,
                                  remoteSense = self.virtualSense,
                                  remoteMuscle = self.virtualMuscle,
                                  robotType=Sensation.RobotType.Sense,
                                  isSentLocal = True,
                                  isSentRemote = True,
                                  isTcp=False,
                                  transferDirection=Sensation.TransferDirection.Direct)
        #self.do_remote_negative_case(robotType=Sensation.RobotType.Muscle,
        self.do_remote_negative_case(remoteMainRobot = self.virtualMainRobot,
                                  remoteSense = self.virtualSense,
                                  remoteMuscle = self.virtualMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp=False,
                                  transferDirection=Sensation.TransferDirection.Up)
        self.do_remote_negative_case(remoteMainRobot = self.virtualMainRobot,
                                  remoteSense = self.virtualSense,
                                  remoteMuscle = self.virtualMuscle,
                                  robotType=Sensation.RobotType.Communication,
                                  isSentLocal = False,
                                  isSentRemote = True,
                                  isTcp=False,
                                  transferDirection=Sensation.TransferDirection.Direct)
# 
# 
#         # done
#         # local should be stopped manually
#         self.mainRobot.tcpServer.stop()
#         self.localSocketClient.stop()        
#         self.localSocketServer.stop()
#         
#         # remote should be stopped manually
#         self.remoteMainRobot.tcpServer.stop()
#         self.remoteSocketClient.stop()        
#         self.remoteSocketServer.stop()
#         
#        
#         print ('Sleep {}s to wait self.remoteMainRobot and self.mainRobot.tcpServer, localSocketServer and localSocketClient to stop'.format(RobotTestCase.SLEEPTIME))
# 
#         time.sleep(RobotTestCase.SLEEPTIME)
        
        self.tearDownVirtual()
        
     
    '''
    TODO These tests fail.
    Sensation based location processing is not implemented
    So these tests can't work and it is not even sure
    what kind of tests are needed, if and when Sensation based Location logic
    is implemented.
    '''

    def future_test_Routing_LocationSensation(self,
                                              transferDirection=Sensation.TransferDirection.Up):
        print('\ntest_Sensation Routing with Location Sensation')
        history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Presense')
        #time.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
        # same routing should fail. if Sensation's and Robot's Locations don't match
        Wall_E_location_sensation = self.sense.createSensation(
                                                 memoryType=Sensation.MemoryType.Sensory,
                                                 sensationType=Sensation.SensationType.Location,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.LOCATIONS_1_NAME)
        Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.sense.associate(sensation=Wall_E_location_sensation)
        # now sense and Item are in RobotTestCase.LOCATIONS_1_NAME location
        
        
        # in muscle we should set also capabilities, look SetUp
        #self.muscle.setLocations(RobotTestCase.LOCATIONS_2)
        muscle_location_sensation = self.sense.createSensation(
                                                 memoryType=Sensation.MemoryType.Sensory,
                                                 sensationType=Sensation.SensationType.Location,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.LOCATIONS_2)
        self.muscle.associate(sensation=muscle_location_sensation)
        # now muscle is in RobotTestCase.LOCATIONS_2
        
       #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_2)
        #self.muscle.setCapabilities(capabilities)
        
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should not be routed to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
        
        # set sensation contain  one Location and muscle to contain many locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        #capabilities.setLocations(RobotTestCase.LOCATIONS_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
        

        # set sensation contain many Locations and muscle to contain one locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        
        # this as not test with Location sensation, because Robot can be onky in one last Location, but not in mane places
        
#         self.sense.setLocations(RobotTestCase.LOCATIONS_1)
#         #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
#         Wall_E_location_sensation = self.sense.createSensation(
#                                                  memoryType=Sensation.MemoryType.Sensory,
#                                                  sensationType=Sensation.SensationType.Location,
#                                                  robotType=Sensation.RobotType.Sense,
#                                                  name=RobotTestCase.LOCATIONS_1_NAME)
#         Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
#        
#         self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
#         capabilities  =  self.muscle.getCapabilities()
#         capabilities.setLocations(RobotTestCase.LOCATIONS_1)
#         self.muscle.setCapabilities(capabilities)
#         
#         # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
#         # should be routed to mainRobot
#         self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         #  test routing to muscle
#         self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
#         # should be routed to mainRobot
#         self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
#         tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
       
        # set sensation no Locations and muscle to contain one locations and one match, routing should succeed again
        # because Sensation does not give location requirement, where to go
        # in muscle we should set also capabilities, look SetUp
        
        # this is valid test, if we don't associate Location sensation, so we create new sensation without associations
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
       
        
        self.sense.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_EMPTY)
       
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
       #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#         sensation, isRoutedToParent  = self.muscle.getAxon().get(robot=self)
 
        # set sensation Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        # this is valid test, if we now associate Location sensation
        
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
       
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #self.muscle.setCapabilities(capabilities)
        
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
     
        # set both sensation not Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        # this is valid test, if we don't associate Location sensation, so we create new sensation without associations
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        
        self.sense.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_EMPTY)
       
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #self.muscle.setCapabilities(capabilities)
        
        # test
#         self.sense.process(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        self.sense.sense(transferDirection=transferDirection, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.mainRobot.getAxon().get(robot=self)
       #  test routing to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty before self.mainRobot.process')        
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')        
        tranferDirection, sensation = self.muscle.getAxon().get(robot=self)
#         sensation, isRoutedToParent = self.muscle.getAxon().get(robot=self)
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after self.muscle.getAxon().get(robot=self)')        
       
if __name__ == '__main__':
    unittest.main()

 