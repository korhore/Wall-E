'''
Created on 13.02.2020
Updated on 13.07.2020
@author: reijo.korhonen@gmail.com

test Robot class

Tests basic functionality of Robot class
Most important is to test Sensation Routing functionality
We create one MainRobot level Robot and sense and muscle Robots
to study functionality.

python3 -m unittest tests/testRobot.py

TODO Robot does not yet have selLocationSensation.
When implemented, update test


'''
import time as time

import unittest
from Sensation import Sensation
from Robot import Robot, TCPServer, HOST,PORT
from Axon import Axon

class RobotTestCase(unittest.TestCase):
    '''
    
    We should play as sense robot and muscle Robot
        - Wall_E_item
        - Image
        - voice
        - location
    '''
    
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
    SHORT_SLEEPTIME=15-0
    LONG_SLEEPTIME=20.0
    WAIT_STEP = 1.0
    
    '''
    Robot modeling
    Don't know yet if this is needed
    '''
 
    
#     def getAxon(self):
#         return self.axon
#     def getId(self):
#         return 1.1
#     def getWho(self):
#         return "RobotTestCase"
#     
#     def setLocation(self, location):
#         self.location = location
#     def getLocation(self):
#         return self.location
#     
#     def log(self, logStr, logLevel=None):
#         if logLevel == None:
#             logLevel = Robot.LogLevel.Normal
#         if logLevel <= self.sense.getLogLevel():
#             print(self.sense.getWho() + ":" + str( self.sense.config.level) + ":" + Sensation.Modes[self.sense.mode] + ": " + logStr)
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
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        
        
        # set robots to same location
        
        self.mainRobot = Robot(parent=None,
                           instanceName='TestMainRobot',
                           instanceType= Sensation.InstanceType.Real)
        # We should set this, because we don't run mainRobot, but call its methods
        self.assertEqual(self.mainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        self.assertEqual(self.mainRobot, Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        if self.mainRobot.level == 1:
            self.mainRobot.activityAverage = self.mainRobot.shortActivityAverage = self.mainRobot.config.getActivityAvegageLevel()
            self.mainRobot.activityNumber = 0
            self.mainRobot.activityPeriodStartTime = time.time()

        self.mainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        self.mainRobot.selfSensation=self.mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.mainRobot.getWho(),
                                                          name = self.mainRobot.getWho(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.mainRobot.getKind(),
                                                          feeling=self.mainRobot.getFeeling(),
                                                          locations=self.mainRobot.getLocations())
        
        
        self.sense = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Sense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.mainRobot.subInstances.append(self.sense)
        
        
        self.muscle = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.mainRobot.subInstances.append(self.muscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.muscle.getCapabilities()
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

        self.muscle.setCapabilities(capabilities)      


    def setUpRemote(self):
        print('\nsetUpRemote')
        
        
        # set robots to same location
        
        self.remoteMainRobot = Robot(parent=None,
                           instanceName='RemoteMainRobot',
                           instanceType= Sensation.InstanceType.Real)
        # correct address, to we don't use same localhost 127.0.0.1, but we still use ip-nmumbers in this single computer without real networking
        self.remoteMainRobot.tcpServer.address = (RobotTestCase.REMOTE_LOCALHOST, self.remoteMainRobot.tcpServer.address[1])
        remoteport = self.remoteMainRobot.tcpServer.address[1]
        print('1: remoteport '+  str(remoteport))
     
        # We should set this, because we don't run mainRobot, but call its methods
        self.assertEqual(self.remoteMainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        self.assertEqual(self.remoteMainRobot, Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
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
                                                          name = self.remoteMainRobot.getWho(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.remoteMainRobot.getKind(),
                                                          feeling=self.remoteMainRobot.getFeeling(),
                                                          locations=self.remoteMainRobot.getLocations())
        
        
        self.remoteSense = RobotTestCase.TestRobot(parent=self.remoteMainRobot,
                           instanceName='RemoteSense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.remoteMainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.remoteSense.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMainRobot.subInstances.append(self.remoteSense)
        
        
        self.remoteMuscle = RobotTestCase.TestRobot(parent=self.remoteMainRobot,
                           instanceName='RemoteMuscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.remoteMainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.remoteMuscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMainRobot.subInstances.append(self.remoteMuscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.remoteMuscle.getCapabilities()
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

        self.remoteMuscle.setCapabilities(capabilities)
        


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
        
    def testLocations(self):
        print('\ntestLocations')
        
        
        # set robots to same location
        
        mainRobot = Robot(parent=None,
                           instanceName='TestLocationMainRobot',
                           instanceType= Sensation.InstanceType.Real)
        # We should set this, because we don't run mainRobot, but call its methods
        self.assertEqual(mainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        self.assertEqual(mainRobot, Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        if mainRobot.level == 1:
            mainRobot.activityAverage = mainRobot.shortActivityAverage = mainRobot.config.getActivityAvegageLevel()
            mainRobot.activityNumber = 0
            mainRobot.activityPeriodStartTime = time.time()

        mainRobot.setLocations(RobotTestCase.LOCATIONS_1)
        mainRobot.selfSensation=mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = mainRobot.getWho(),
                                                          name = mainRobot.getWho(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=mainRobot.getKind(),
                                                          feeling=mainRobot.getFeeling(),
                                                          locations=mainRobot.getLocations())
        
        
        sense = RobotTestCase.TestRobot(parent=mainRobot,
                           instanceName='Sense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        sense.setLocations(RobotTestCase.LOCATIONS_1_2)
        mainRobot.subInstances.append(sense)
        
        
        muscle = RobotTestCase.TestRobot(parent=mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        muscle.setLocations(RobotTestCase.LOCATIONS_1_2)
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
        del muscle
        del sense
        del mainRobot
        
        

    def test_Routing(self):
        print('\ntest_Sensation Routing')
        #history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_1 set
        # sensation   does not set location
        # when we don't set locations in the Sensation, it gets local default location, which should be routed everywhere
        
        print('\n sensation, no locations set, Robot location match, Sensation locations match')
        self.do_TestRouting(locations=None, shouldBeRouted=True)

        
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_2 set
        # sensation   does not set location
        # when we don't set locations in the Sensation, it gets local default location, which should be routed everywhere
        print('\n sensation no locations set, sense don\'t match to muscle')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_2)
        self.do_TestRouting(locations=None, shouldBeRouted=True)
        
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_2 set
        # sensation   have LOCATIONS_1 set
        # when senses locations does not match destination's locations, it is not routed
        print('\n sensation, no locations set, sense don\'t match to muscle')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_2)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1, shouldBeRouted=False)
        
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_1 set
        # sensation   have LOCATIONS_1 set
        # when senses locations does not match destination's locations, it is  routed
        print('\n sensation locations set, sense and muscle match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1, shouldBeRouted=True)
        
        ###########################################################################################################
        # sense       have LOCATIONS_GLOBAL set
        # muscle      have LOCATIONS_GLOBAL set
        # sensation   have LOCATIONS_GLOBAL set
        # when senses locations and sensation location match as global, it is  routed
        print('\n sensation locations set, sense and muscle match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL, shouldBeRouted=True)
        
        ###########################################################################################################
        # sense       have LOCATIONS_GLOBAL set
        # muscle      have LOCATIONS_EMPTY set
        # sensation   have LOCATIONS_EMPTY set
        # when senses locations and sensation location match as global, it is  routed
        print('\n sensation locations set, sense and muscle match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL, shouldBeRouted=True)

        ###########################################################################################################
        # sense       have LOCATIONS_EMPTY set
        # muscle      have LOCATIONS_GLOBAL set
        # sensation   have LOCATIONS_EMPTY set
        # when senses locations and sensation location match as global, it is  routed
        print('\n sensation locations set, sense and muscle match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_EMPTY, shouldBeRouted=True)
       
        ###########################################################################################################
        # sense       have LOCATIONS_1 set
        # muscle      have LOCATIONS_GLOBAL set
        # sensation   have LOCATIONS_1 set
        # when senses locations and sensation location match as global, it is  routed
        print('\n sensation locations set, sense and muscle match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1, shouldBeRouted=True)
       
       
        ###########################################################################################################
        # sense       have LOCATIONS_GLOBAL set
        # muscle      have LOCATIONS_1 set
        # sensation   have LOCATIONS_GLOBAL set
        # when senses locations and sensation location match as global, it is  routed
        print('\n sensation locations set, sense and muscle match')
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL, shouldBeRouted=True)
       
       
      # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_1_2 set
        # muscle      have LOCATIONS_1_2  set
        # sensation   have no locations set
        # when senses locations does not match destination's locations, it is  routed
        print('\n sensation No locations set, sense and muscle match many locations set')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1_2)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1_2)
        self.do_TestRouting(locations=None, shouldBeRouted=True)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_1_2 set
        # muscle      have LOCATIONS_1_2  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  routed
        print('\n sensation many locations set, sense and muscle match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1_2)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1_2)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2, shouldBeRouted=True)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_2_3 set
        # muscle      have LOCATIONS_2_3  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  routed
        print('\n sensation many locations set, sense and muscle many locations partial match')
        # if Sensation's and Robot's Locations partially match, sensation is routed
        self.sense.setLocations(RobotTestCase.LOCATIONS_2_3)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_2_3)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2, shouldBeRouted=True)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n sensation many locations set, sense and muscle many locations no match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_3_4)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_2, shouldBeRouted=False)

        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n sensation many locations set, sense and muscle many locations no match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_GLOBAL, shouldBeRouted=True)
        
        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n sensation many locations set, sense and muscle many locations no match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_3_4)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4, shouldBeRouted=True)
        
        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n sensation many locations set, sense and muscle many locations no match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_3_4)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1_GLOBAL)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_3_4, shouldBeRouted=True)
        
        # Many locations tests
        ###########################################################################################################
        # sense       have LOCATIONS_3_4 set
        # muscle      have LOCATIONS_3_4  set
        # sensation   have LOCATIONS_1_2  set
        # when senses locations does not match destination's locations, it is  not routed
        print('\n sensation many locations set, sense and muscle many locations no match')
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.LOCATIONS_1_GLOBAL)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_3_4)
        self.do_TestRouting(locations=RobotTestCase.LOCATIONS_1_GLOBAL, shouldBeRouted=True)
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after self.muscle.getAxon().get()')
        
    '''
    helper for testing local routing     
    '''
    def do_TestRouting(self, locations, shouldBeRouted):
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')

        if locations == None:     
            Wall_E_item_sensation = self.sense.createSensation(
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=Sensation.RobotType.Sense,
                                                     name=RobotTestCase.NAME,
                                                     score=RobotTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Entering)
        else:
             Wall_E_item_sensation = self.sense.createSensation(
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=Sensation.RobotType.Sense,
                                                     name=RobotTestCase.NAME,
                                                     score=RobotTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Entering,
                                                     locations=locations)
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        if shouldBeRouted:
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get()
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
    '''
    Tcp connection and routing. We test inside localhost SocketServer and SocketClient
    TODO This test is impossible to do with one MainRobot, because one MainRobot is not
    initiated to respond until it has send request to and we don't have mainRobot
    running to get its tested properly
    '''
        
    def test_Tcp(self):
        print('\ntest_Sensation Routing with TCP SocketServer and SocketClient')
        
        # set first remote mainRobot
        
        # set log level Detailed, so we know what is happening
        self.setUpRemote()
        
        self.remoteMainRobot.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        # create tcpServer same way as MainRpbot does it, but no hosts to connect, this is server only
        self.remoteMainRobot.tcpServer=TCPServer(parent=self.remoteMainRobot,
                                           memory=self.remoteMainRobot.getMemory(),
                                           hostNames=[], # no hostnames to connect, we are server side
                                           instanceName='remoteTCPServer',
                                           instanceType=Sensation.InstanceType.Remote,
                                           level=self.remoteMainRobot.level,
                                           address=(HOST,PORT))
        
        # this is hard to test
        # we could also start self.remoteMainRobot 
        # but for test step by step, it is easier make only self.remoteMainRobot.tcpServer as running process 

        self.remoteMainRobot.tcpServer.start()        
        
        # set then local mainRobot
        
        # set log level Detailed, so we know what is happening
        self.mainRobot.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        # create tcpServe same way as MainRpbot does it, but connecting to localhost
        # but fake self.mainRobot server port, nobody will connect to it, we are connecting side
        self.mainRobot.tcpServer=TCPServer(parent=self.mainRobot,
                                           memory=self.mainRobot.getMemory(),
                                           hostNames=[RobotTestCase.REMOTE_LOCALHOST],
                                           instanceName='localTCPServer',
                                           instanceType=Sensation.InstanceType.Remote,
                                           level=self.mainRobot.level,
                                           address=(HOST,RobotTestCase.FAKE_PORT)) # fake self.mainRobot server port, nobody will connect to it, we are connecting side
        # We try to connect running self.remoteMainRobot

        self.mainRobot.tcpServer.start()
        
        # after this we test live processes, to we use WithWait -test6 methods
        print ('Wait tcpServer runs')
        # manual conditional wait
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while len(self.mainRobot.tcpServer.socketClients) == 0 and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)

        self.assertTrue(len(self.mainRobot.tcpServer.socketClients) > 0, 'should have socketClient')        
        self.localSocketClient = self.mainRobot.tcpServer.socketClients[0]
        
        self.assertTrue(len(self.mainRobot.tcpServer.socketServers) > 0, 'should have socketServer')        
        self.localSocketServer = self.mainRobot.tcpServer.socketServers[0]
        
        # test configuration
        self.assertEqual(self.mainRobot.tcpServer.getInstanceType(),Sensation.InstanceType.Remote)                
        self.assertEqual(self.localSocketClient.getInstanceType(),Sensation.InstanceType.Remote)
        # conditional wait
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while self.localSocketClient.getLocations() != RobotTestCase.LOCATIONS_1 and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)

        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
        # unit tests
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
        
        # test full functionality of isInLocations with other option of Robot location
        # test local global location as Robot location
        # SocketClient gets location from SocketServer, so we must change that
        # if remote is local Global it should not accept anything from local
        # except global location, because global goes everywhere
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_EMPTY)
        # unit tests
        self.assertFalse(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))
        
        # test  global location as Robot location
        # SocketClient gets location from SocketServer, so we must change that
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_GLOBAL)
        # unit tests
        # if remote is global it should accept everything from local
        self.assertTrue(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))
        # set all as it was to continue test
        # SocketClient gets location from SocketServer, so we must change that
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_1)
       

        # test location routing
        
        # set log level Detailed, so we know what is happening
        self.localSocketClient.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        self.assertTrue(len(self.mainRobot.tcpServer.socketServers) > 0,'should have socketServer')        
        self.localSocketServer = self.mainRobot.tcpServer.socketServers[0]
 
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) == 1,'should have socketClient')        
        self.remoteSocketClient = self.remoteMainRobot.tcpServer.socketClients[0]
        # set log level Detailed, so we know what is happening
        self.remoteSocketClient.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 1,'should have socketServer')        
        self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
        
        self.assertTrue(self.localSocketClient in self.mainRobot.subInstances,'mainRobot should know localSocketClient')        
        self.assertTrue(self.remoteSocketClient in self.remoteMainRobot.subInstances,'mainRobot should know remoteSocketClient')        
        self.assertFalse(self.localSocketServer in self.mainRobot.subInstances,'mainRobot should know localSocketServer')        
        self.assertFalse(self.remoteSocketServer in self.remoteMainRobot.subInstances,'mainRobot should know self.remoteSocketServer')
        
        self.assertEqual(len(self.mainRobot.subInstances),3, 'mainRobot should know 3 subInstances')
               
        
        
        # conditional wait for first assert for capabilities
        print ('Wait self.remoteMainRobot and SocketServers runs')
        
        capabilities  =  self.localSocketClient.getCapabilities()
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while not capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item) and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)
            capabilities  =  self.localSocketClient.getCapabilities()
       
        
        # at this point we should have got back Robot sensation from self.remoteMainRobot
        # as well as capabilities
        
        # check Capabilities
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.localSocketClient.getCapabilities()
         #Sensory
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
        
        # local and remote capabilities should be equal        
        self.assertEqual(self.localSocketClient.getCapabilities(),self.localSocketServer.getCapabilities(), 'should have equal local capabilities')        
        self.assertEqual(self.remoteSocketClient.getCapabilities(),self.remoteSocketServer.getCapabilities(), 'should have equal remote capabilities')        
        self.assertEqual(self.localSocketClient.getCapabilities().toString(),self.remoteSocketClient.getCapabilities().toString(), 'should have equal local and remote capabilities')        
        self.assertEqual(self.localSocketServer.getCapabilities().toString(),self.remoteSocketServer.getCapabilities().toString(), 'should have equal local and remote capabilities')        
        # location should be equal now
        self.assertEqual(self.localSocketClient.getLocations(),self.localSocketServer.getLocations(), 'should have equal local location')        
        self.assertEqual(self.remoteSocketClient.getLocations(),self.remoteSocketServer.getLocations(), 'should have equal remote location')        
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')        
        self.assertEqual(self.localSocketServer.getLocations(),self.remoteSocketServer.getLocations(), 'should have equal local and remote location')        

        # Ready to test routing a sensation.
        # test both positive and negative cases
        self.do_tcp_positive_case()
        self.do_tcp_negative_case()
        self.do_tcp_positive_case()

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
        
    def do_tcp_positive_case(self):
        print('\n test tcp positive case')
        history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL
        
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Presense')
        # normal sensation with location, this should success
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.sense.getLocations())
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation)
        
        #  global sensation, that goes every location, this should success
        Wall_E_item_sensation_global_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=RobotTestCase.LOCATIONS_GLOBAL)
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_global_location)
        
        # local global sensation, that goes every location in local robot, but should not be sent to REmote Robot
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        # test test
        self.assertEqual(Wall_E_item_sensation_no_location.getLocations(), RobotTestCase.LOCATIONS_EMPTY)
        # test
        self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation_no_location)
       

    def do_tcp_positive_case_sensation(self, sensationToSend):
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
       
        self.assertEqual(sensationToSend.getReceivedFrom(), [], 'local sensation should not have receivedFrom information at the beginning of test')
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensationToSend)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
        
        # test routing to remote muscle from local sense 
        print ('Wait Sensation is transferred by tcp')
 
        # conditional wait              
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while self.remoteMainRobot.getAxon().empty() and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)

        # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
        self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
        tranferDirection, sensation = self.remoteMainRobot.getAxon().get()

        # test routing to remoteMuscle
        self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
        tranferDirection, sensation = self.remoteMuscle.getAxon().get()
        
        # test, that sensation is same than transferred
        self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
        
        # test, that local sensation to be transferred does not contain  receicedFrom information
        self.assertEqual(sensationToSend.getReceivedFrom(), [], 'local sensation should not have receivedFrom information')

        # test, that remote sensation transferred does contain  receicedFron information
        self.assertEqual(sensation.getReceivedFrom(), [RobotTestCase.LOCALHOST], 'remote sensation should have receivedFrom information')

        # now muscle should not have more sensations
        self.assertTrue(self.remoteMuscle.getAxon().empty(),'muscle Axon should be empty')
        
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')

        # test routing remote got sensation back from remote to local
    
        self.remoteSense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
        self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
        tranferDirection, sensation = self.remoteMainRobot.getAxon().get()

        # test routing to remoteMuscle
        self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
        tranferDirection, sensation = self.remoteMuscle.getAxon().get()
        
        # but routing to local should fail. because we have got this sensation from local and receivedFron contains that information
        print ('Wait Sensation is transferred by tcp')

        # conditional wait               
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while not self.mainRobot.getAxon().empty() and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)

        # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
        self.assertTrue(self.mainRobot.getAxon().empty(),'localMainRobote Axon should be empty')
   
           
    '''
    tcp negative case
    '''
    def do_tcp_negative_case(self):
        ###################################################################################################################################################
        # tcp negative case
        # localSocketServer has different location
        #
        print('\n test tcp negative case, localSocketServer has different location')
        history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL
        
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        
        ################ test same location sense, muscle ####################
        ################ test same location localSocket , remoteSocket ####################
        ################ but location localSocket , remoteSocket differs ####################
        
        ################ change local localSocketServer location, so localSocketClient should not capability to handle this message ####################        
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.sense.getLocations())
        # with sensation, that has different location the srcSocker we should fail       
         
        # local global sensation, that goes every location in local robot, but not with remote and local Robots
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)

        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should be empty BEFORE we test')
        self.assertEqual(Wall_E_item_sensation.getLocations(), RobotTestCase.LOCATIONS_1, 'sensation should have location {} BEFORE we test'.format(RobotTestCase.LOCATIONS_1))
        # set locations
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_2)
        
        
        # with different location we should fail
        self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation)

        # with local global sensation should fail       
        self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation_no_location)
        
        # set receiving robot as global setting its location empty these
        # set locations
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.remoteMuscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        
        # with sensation with different location we should success, because receiver accepts all        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation)
        # with global sensation, that goes every location, we should success        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_no_location)
        
        # set locations back
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMuscle.setLocations(RobotTestCase.LOCATIONS_1)
        #localSocketClient.setLocations(RobotTestCase.LOCATIONS_1)
        
        
        
    def do_tcp_negative_case_sensation(self, sensationToSend):
        
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensationToSend)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
        
        # remote SocketServer should have NOT got it and when it is living process, it has NOT put it to remoteMainRobot
        print ('Wait Sensation is transferred by tcp')

        # conditional wait               
        endTime = time.time() + RobotTestCase.SLEEPTIME
        # wait ere this time if we will bet something routes even if positive case is that should be self.remoteMainRobot.getAxon().empty()
        while self.remoteMainRobot.getAxon().empty() and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)
        
        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should be empty')
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
      
    '''
    TODO These tests fail.
    Sensation based location processing is not implemented
    So these tests can't work and it is not even sure
    what kind of tests ere needrd, if and when Sensation based Location logic
    is implemented.
    '''

    def future_test_Routing_LocationSensation(self):
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
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
        
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
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should not be routed to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
        
        # set sensation contain  one Location and muscle to contain many locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        #capabilities.setLocations(RobotTestCase.LOCATIONS_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation= self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()

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
#         self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
#         # should be routed to mainRobot
#         self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get()
#         #  test routing to muscle
#         self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
#         # should be routed to mainRobot
#         self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
#         tranferDirection, sensation = self.muscle.getAxon().get()
       
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
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensationn = self.mainRobot.getAxon().get()
       #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
 
        # set sensation Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        # this is valid test, if we now associate Location sensation
        
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATIONS_1)
        Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
       
        self.muscle.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
     
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
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATIONS_EMPTY)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       #  test routing to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty before self.mainRobot.process')        
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')        
        tranferDirection, sensation = self.muscle.getAxon().get()
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after self.muscle.getAxon().get()')        
       
if __name__ == '__main__':
    unittest.main()

 