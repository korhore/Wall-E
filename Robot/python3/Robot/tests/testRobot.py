'''
Created on 13.02.2020
Updated on 10.01.2021
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
    Robot modeling
    Don't know yet if this is needed
    '''
 
    
#     def getAxon(self):
#         return self.axon
#     def getId(self):
#         return 1.1
#     def getName(self):
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
#             print(self.sense.getName() + ":" + str( self.sense.config.level) + ":" + Sensation.Modes[self.sense.mode] + ": " + logStr)
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
        
        
        self.sense = RobotTestCase.TestRobot(
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
        self.setCapabilities(robot=self.muscle, robotTypes=[Sensation.RobotType.Sense])
        #self.setCapabilities(robot=self.muscle, robotType=Sensation.RobotType.Muscle, is_set=False)


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
        self.setCapabilities(robot=self.remoteMuscle, robotTypes=[Sensation.RobotType.Sense, Sensation.RobotType.Communication])
        #self.setCapabilities(robot=self.remoteMuscle, robotType=Sensation.RobotType.Muscle, is_set=False)
        
    '''
    set capabilities  Item, Image, Voice
    '''
    def setCapabilities(self, robot, robotTypes):
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
        
    '''
    
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
                            shouldBeRouted=True)
        # no capability
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
        # locations donn't match so nothing is routed
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
        
        
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after self.muscle.getAxon().get()')
        
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
                       robotType=Sensation.RobotType.Sense):
#                       isCommunication=False):
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.setRobotMainNames(robot=self.sense, mainNames=senseMainNames)
        self.setRobotMainNames(robot=self.muscle, mainNames=muscleMainNames)
        self.setCapabilities(robot=self.muscle, robotTypes=[robotType])

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
                                                     #isCommunication=isCommunication,
                                                     name=RobotTestCase.NAME,
                                                     score=RobotTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Entering,
                                                     locations=locations)
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty before we test')
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

        # same logic than in Memory
        if locations == None or len(locations) == 0:
            locations = [''] 
        for location in locations:        
            self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location)), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')

    '''
    deprecated
    
    Same location test. but test cases where Robots, mainNames match and Not match
    If not match, the Different Robottype Sensation is routed, but not same
    Robottype sensation not
    '''            
    def test_MainNamesRouting(self):
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
                                 shouldBeRouted=True)
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Muscle,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=True)
        # but if ensation.RobotType.Communication and MainNanes are same, it is not routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Communication,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Communication,
                                 shouldBeRouted=False)
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Muscle should NOT be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_1,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=False)
        
        ### Now different MainnNames
        ### if Robottype != Communication, results are same
        ### but with Robottype == Communication we should success
        
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Sense,
                                 shouldBeRouted=True)
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Sense should be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Muscle,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=True)
        # but if ensation.RobotType.Communication and MainNanes are same, it is not routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Communication,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Communication,
                                 shouldBeRouted=True)
        # when MAINNAMES_1,Sensation.RobotType.Sense; MAINNAMES_1,Sensation.RobotType.Muscle should NOT be routed
        self.do_MainNamesRouting(locations=None,
                                 senseMainNames=RobotTestCase.MAINNAMES_1,
                                 senseRobotType=Sensation.RobotType.Sense,
                                 muscleMainNames=RobotTestCase.MAINNAMES_2,
                                 muscleRobotType=Sensation.RobotType.Muscle,
                                 shouldBeRouted=False)
                
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
                            shouldBeRouted):
        self.assertTrue(self.mainRobot.getAxon().empty(), 'mainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.assertTrue(self.sense.getAxon().empty(), 'sense Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')

        self.sense.setMainNames(senseMainNames)
        self.muscle.setMainNames(muscleMainNames)
 
        # Clear sense capabilities so MainRobot does not route sensation back to it       
        self.setCapabilities(robot=self.sense, robotTypes=[])

        self.setCapabilities(robot=self.muscle, robotTypes=[muscleRobotType])
        
        
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
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sense_sensation)
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
        self.mainRobot.tcpServer=TCPServer(
                                           mainRobot=self.mainRobot,
                                           parent=self.mainRobot,
                                           memory=self.mainRobot.getMemory(),
                                           hostNames=[RobotTestCase.REMOTE_LOCALHOST],
                                           instanceName='localTCPServer',
                                           instanceType=Sensation.InstanceType.Remote,
                                           level=self.mainRobot.level,
                                           address=(HOST,RobotTestCase.FAKE_PORT)) # fake self.mainRobot server port, nobody will connect to it, we are connecting side
        # We try to connect running self.remoteMainRobot

        # added this to avoid other test setting failure
        self.sense.setLocations(RobotTestCase.LOCATIONS_1)
        self.muscle.setLocations(RobotTestCase.LOCATIONS_1)

        self.mainRobot.tcpServer.start()
        
        # after this we test live processes, to we use WithWait -test6 methods
        print ('Wait tcpServer runs')
        # manual conditional wait
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while len(self.mainRobot.tcpServer.socketClients) == 0 \
              and len(self.remoteMainRobot.tcpServer.socketClients) == 0 \
              and time.time() < endTime:
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
            time.sleep(RobotTestCase.WAIT_STEP)
#         print ("self.localSocketClient.getLocations() {} self.remoteSocketServer.getLocations() {}".format(self.localSocketClient.getLocations(), self.remoteSocketServer.getLocations()))
#         print ("self.remoteSocketClient.getLocations() {} self.localSocketServer.getLocations() {}".format(self.remoteSocketClient.getLocations(), self.localSocketServer.getLocations()))
            
        # check    
        self.assertTrue(time.time() < endTime, 'check 1 should have got location '+ str(RobotTestCase.LOCATIONS_1) + ' but it is missing')
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 1 should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        # why (self.localSocketClient.getLocations() ['testLocation'] !=  self.remoteSocketClient.getLocations() ['testLocation', 'global']
        # this is first place when rhis check fails, but it variates


        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.remoteSocketClient.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.localSocketServer.getLocations(),RobotTestCase.LOCATIONS_1)
        self.assertEqual(self.remoteSocketServer.getLocations(),RobotTestCase.LOCATIONS_1)
        
        # unit tests
        self.assertTrue(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1))
        # TODO re-enable
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3)) # ['testLocation'] [                'Ubuntu', '3']
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
        self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
        # test if this affects
        self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))
        
        # test full functionality of isInLocations with other option of Robot location
        # test local global location as Robot location
        # SocketClient gets location from SocketServer, so we must change that
        # if remote is local Global it should not accept anything from local
        # except global location, because global goes everywhere
        # TODO What is this?
        # We can't change location in local and expect that remote changes it back, because it is set only once and it is already set
        # so next code is commented out        
#         self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_EMPTY)
#         self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_EMPTY)
#         self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
#         self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_EMPTY)
#        # unit tests
#         self.assertFalse(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1)) # [] ['testLocation']
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
#         self.assertFalse(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))

        # TODO What is this?
        # We can't change location in local and expect that remote changes it back, because it is set only once and it is already set
        # so next code is commented out        
#         # test  global location as Robot location
#         # SocketClient gets location from SocketServer, so we must change that
#         self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
#         self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_GLOBAL)
#         self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
#         self.assertEqual(self.localSocketClient.getDownLocations(),RobotTestCase.LOCATIONS_GLOBAL)
#        # unit tests
#         # if remote is global it should accept everything from local
#         self.assertTrue(self.localSocketClient.isInLocations(self.localSocketClient.getLocations()))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_2))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_3))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_2_3))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_3_4))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_EMPTY))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_GLOBAL))
#         self.assertTrue(self.localSocketClient.isInLocations(RobotTestCase.LOCATIONS_1_GLOBAL))
#         # set all as it was to continue test
#         # SocketClient gets location from SocketServer, so we must change that
#         self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_1)
#         self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_1)
        
        # check    
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 2 should have equal local and remote location')
 #         # added set
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 1,'should have socketServer')        
#         self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
        
#         self.remoteSocketServer.setLocations(RobotTestCase.LOCATIONS_1)
#         self.remoteSocketServer.setDownLocations(RobotTestCase.LOCATIONS_1)
 #       self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
       

        # test location routing
        
        # set log level Detailed, so we know what is happening
#         self.localSocketClient.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
#         self.assertTrue(len(self.mainRobot.tcpServer.socketServers) > 0,'should have socketServer')        
#         self.localSocketServer = self.mainRobot.tcpServer.socketServers[0]
#  
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) == 1,'should have socketClient')        
#         self.remoteSocketClient = self.remoteMainRobot.tcpServer.socketClients[0]
        
#         # check    
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 2 should have equal local and remote location')
#         self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']

        # test test        
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketClient.getLocations(),RobotTestCase.LOCATIONS_1, 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketClient.getDownLocations(),self.remoteSocketClient.getDownLocations(), 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        self.assertEqual(self.localSocketClient.getDownLocations(),RobotTestCase.LOCATIONS_1, 'should have equal local and remote location')  # will get ['testLocation'] != ['testLocation', 'Ubuntu']
        # set log level Detailed, so we know what is happening
        self.remoteSocketClient.setLogLevel(Robot.LogLevel.Normal) # TODO Normal Detailed
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 1,'should have socketServer')        
#         self.remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
        
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
            time.sleep(RobotTestCase.WAIT_STEP)
            capabilities  =  self.localSocketClient.getCapabilities()
        # check
        self.assertEqual(self.localSocketClient.getLocations(),self.remoteSocketClient.getLocations(), 'check 4 should have equal local and remote location')
 
        capabilities  =  self.remoteSocketClient.getCapabilities()
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while not capabilities.hasCapability(robotType=Sensation.RobotType.Sense, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Item) and time.time() < endTime:
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
        
        # check Capabilities
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.localSocketClient.getCapabilities()
        # Sense
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
        
        #Communication
        #Sensory
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

        # Ready to test routing a sensation.
        # test both positive and negative cases
#         self.do_tcp_positive_case(robotType=Sensation.RobotType.Sense,
#                                   isCommunication=False,
#                                   isSentLocal = True,
#                                   isSentRemote = False)
        # We set muscle mainNames different than sense and after that capabilities should match      
#        self.do_tcp_positive_case(robotType=Sensation.RobotType.Muscle,
        self.do_tcp_positive_case(robotType=Sensation.RobotType.Communication,
                                  #isCommunication =True,
                                  isSentLocal = False,
                                  isSentRemote = True)
        # negative case
        self.do_tcp_negative_case(robotType=Sensation.RobotType.Sense,
                                  #isCommunication=False,
                                  isSentLocal = True,
                                  isSentRemote = True)# TODO False)
        #self.do_tcp_negative_case(robotType=Sensation.RobotType.Muscle,
        self.do_tcp_negative_case(robotType=Sensation.RobotType.Communication,
                                  #isCommunication=True,
                                  isSentLocal = False,
                                  isSentRemote = True)


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
        
#    def do_tcp_positive_case(self, robotType, isCommunication, isSentLocal, isSentRemote):
    def do_tcp_positive_case(self, robotType, isSentLocal, isSentRemote):
        print('\n-test tcp positive case')
        history_sensationTime = time.time() -2*RobotTestCase.ASSOCIATION_INTERVAL
        
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'mainRobotAxon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        if True:#isSentRemote:
            self.assertTrue(self.remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
            self.assertTrue(self.remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n--too old_Presense')
        # normal sensation with location, this should success
        Wall_E_item_sensation = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 #isCommunication=isCommunication,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.sense.getLocations())
        self.assertEqual(Wall_E_item_sensation.getMainNames(), self.MAINNAMES_1, 'Sensation to send should be created with local mainnames')
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation,
                                            isSentLocal = isSentLocal,
                                            isSentRemote = isSentRemote)
        
        #  global sensation, that goes every location, this should success
        Wall_E_item_sensation_global_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 #isCommunication=isCommunication,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=RobotTestCase.LOCATIONS_GLOBAL)
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_global_location,
                                            isSentLocal = isSentLocal,
                                            isSentRemote = isSentRemote)
        
        # local global sensation, that goes every location in local robot, but should not be sent to Remote Robot
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 #isCommunication=isCommunication,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_no_location,
                                            isSentLocal = isSentLocal,
                                            isSentRemote = False)
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'mainRobotAxon should be empty at the end of test!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the end of test!')
        if True:#isSentRemote:
            self.assertTrue(self.remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the end of test!')
            self.assertTrue(self.remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the should be empty at the end of test!')
#         # test test
#         self.assertEqual(Wall_E_item_sensation_no_location.getLocations(), RobotTestCase.LOCATIONS_EMPTY)
#         # test
#         self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation_no_location,
#                                             isSentLocal = True)
       

    def do_tcp_positive_case_sensation(self, sensationToSend, isSentLocal, isSentRemote):
        self.assertTrue(self.mainRobot.getAxon().empty(), 'mainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        if True:#isSentRemote:
            self.assertTrue(self.remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
            print("1. self.remoteMainRobot.getAxon().empty()")
            self.assertTrue(self.remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
       
        self.assertEqual(sensationToSend.getReceivedFrom(), [], 'local sensation should not have receivedFrom information at the beginning of test')
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensationToSend)
            # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(), 'local mainRobot Axon should be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
        self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
       
        # process   
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        if isSentLocal:
            # test routing to muscle
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get()
            self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
            self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
            
            for location in sensationToSend.getLocations():       
                self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location=location)), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should  be empty')

        # test routing to remote muscle from local sense 
        print ('Wait Sensation is transferred by tcp')
     
        # conditional wait              
        endTime = time.time() + RobotTestCase.SLEEPTIME
        while self.remoteMainRobot.getAxon().empty() and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)
    
        if isSentRemote:    
            # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
            self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobot Axon should not be empty')
            tranferDirection, sensation = self.remoteMainRobot.getAxon().get()
            self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
            self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')
    
            # test routing to remoteMuscle
            self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
            self.assertFalse(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
            tranferDirection, sensation = self.remoteMuscle.getAxon().get()
            
            # test, that sensation is same than transferred
            self.assertEqual(sensationToSend.getId(), sensation.getId(), 'send and received sensations ids should be equal')
            self.assertEqual(sensationToSend, sensation, 'send and received sensations should be equal')           
            # test, that local sensation to be transferred does not contain  receicedFrom information
            self.assertEqual(sensationToSend.getReceivedFrom(), [], 'local sensation should not have receivedFrom information')
    
            # test, that remote sensation transferred does contain  receicedFron information
            self.assertEqual(sensation.getReceivedFrom(), [RobotTestCase.LOCALHOST], 'remote sensation should have receivedFrom information')
    
            # now muscle should not have more sensations
            self.assertTrue(self.remoteMuscle.getAxon().empty(),'remote muscle Axon should be empty')
        

            # test routing remote got sensation back from remote to local
        
            self.remoteSense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
            # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
            self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
            tranferDirection, sensation = self.remoteMainRobot.getAxon().get()

            # test routing to remoteMuscle
            self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
            self.assertFalse(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
            tranferDirection, sensation = self.remoteMuscle.getAxon().get()
            self.assertTrue(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should be empty')
        
            # but routing to local should fail. because we have got this sensation from local and receivedFrom contains that information
            print ('Wait Sensation is transferred by tcp')
    
            # conditional wait               
            endTime = time.time() + RobotTestCase.SLEEPTIME
            while not self.mainRobot.getAxon().empty() and time.time() < endTime:
                time.sleep(RobotTestCase.WAIT_STEP)
            self.assertTrue(self.remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty!')
    
            # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
            self.assertTrue(self.mainRobot.getAxon().empty(),'localMainRobote Axon should be empty')
        else:
            # remote SocketServer should not have got it and when it is living process, it has not put it to remoteMainRobot
            #self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobot Axon should be empty')
            self.assertTrue(self.remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty')
            self.assertTrue(self.remoteSense.getAxon().empty(), 'remoteMuscle Axon should be empty')

       
        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'mainRobotAxon should be empty at the end of test!')
        self.assertTrue(self.muscle.getAxon().empty(), 'muscle Axon should be empty at the end of test!')
        self.assertTrue(self.sense.getAxon().empty(), 'sense Axon should be empty at the end of test!')

        self.assertTrue(self.remoteMainRobot.getAxon().empty(), 'remoteMainRobot Axon should be empty at the end of test!')
        self.assertTrue(self.remoteMuscle.getAxon().empty(), 'remoteMuscle Axon should be empty at the end of test!')
        self.assertTrue(self.remoteSense.getAxon().empty(), 'remoteSense Axon should be empty at the end of test!')
           
    '''
    tcp negative case
    '''
    def do_tcp_negative_case(self,
                             robotType,
                             #isCommunication,
                             isSentLocal,
                             isSentRemote):
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
                                                 #isCommunication=isCommunication,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.sense.getLocations())
        # with sensation, that has different location the srcSocker we should fail       
         
        # local global sensation, that goes every location in local robot, but not with remote and local Robots
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,
                                                 #isCommunication=isCommunication,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)

        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should be empty BEFORE we test')
        self.assertEqual(Wall_E_item_sensation.getLocations(), RobotTestCase.LOCATIONS_1, 'sensation should have location {} BEFORE we test'.format(RobotTestCase.LOCATIONS_1))
        # set locations
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_2)
        self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_2)
        
        
        # with different location we should fail
        self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation,
                                            isSentLocal = isSentLocal)

        # with local global sensation should fail       
        self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation_no_location,
                                            isSentLocal = isSentLocal)
        
        # set receiving robot as global setting its location empty these
        # set locations
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.remoteMuscle.setLocations(RobotTestCase.LOCATIONS_GLOBAL)
        self.remoteMuscle.setDownLocations(RobotTestCase.LOCATIONS_GLOBAL)
        
        # with sensation with different location we should success, because receiver accepts all        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation,
                                            isSentLocal=isSentLocal,
                                            isSentRemote=isSentRemote)
        # with global sensation, that goes every location, we should success        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_no_location,
                                            isSentLocal=isSentLocal,
                                            isSentRemote=isSentRemote)
        
        # set locations back
        self.localSocketServer.setLocations(RobotTestCase.LOCATIONS_1)
        self.localSocketServer.setDownLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMuscle.setLocations(RobotTestCase.LOCATIONS_1)
        self.remoteMuscle.setDownLocations(RobotTestCase.LOCATIONS_1)
        #localSocketClient.setLocations(RobotTestCase.LOCATIONS_1)
        
        
        
    def do_tcp_negative_case_sensation(self,sensationToSend,
                                       isSentLocal):
        
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensationToSend)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        if isSentLocal:
            # should be routed to mainRobot
            self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
            tranferDirection, sensation = self.muscle.getAxon().get()
        else:
            self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')

            
        # remote SocketServer should have NOT got it and when it is living process, it has NOT put it to remoteMainRobot
        print ('Wait Sensation is transferred by tcp')

        # conditional wait               
        endTime = time.time() + RobotTestCase.SLEEPTIME
        # wait ere this time if we will bet something routes even if positive case is that should be self.remoteMainRobot.getAxon().empty()
        while self.remoteMainRobot.getAxon().empty() and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)
        
        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobot Axon should be empty')
        
        if isSentLocal:
            for location in sensationToSend.getLocations():        
                self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location = location)), 1, 'len(self.sense.getMemory().presentItemSensations(location = {}) should be 1'.format(location))
        else:
             for location in sensationToSend.getLocations():
                # TODO check this
                self.assertEqual(len(self.sense.getMemory().getPresentItemSensations(location = location)), 1, 'len(self.sense.getMemory().presentItemSensations(location = {}) should be 0'.format(location))
     
    '''
    TODO These tests fail.
    Sensation based location processing is not implemented
    So these tests can't work and it is not even sure
    what kind of tests are needed, if and when Sensation based Location logic
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
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
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
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_1)
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
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
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
        self.muscle.setDownLocations(RobotTestCase.LOCATIONS_EMPTY)
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

 