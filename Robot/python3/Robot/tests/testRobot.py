'''
Created on 14.02.2020
Updated on 01.07.2020
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
    
    SET_1_1_LOCATIONS_1 = 'testLocation'
    SET_1_1_LOCATIONS_2 = 'Ubuntu'
    #SET_1_2_LOCATIONS =   ['testLocation', 'Ubuntu']
    SET_EMPTY_LOCATIONS = ''
    
    LOCATION_1_NAME =     'testLocation'
    LOCATION_1_X =        1.0
    LOCATION_1_Y =        2.0
    LOCATION_1_Z =        3.0
    LOCATION_1_RADIUS =   4.0
    
    LOCATION_2_NAME =     'Ubuntu'
    LOCATION_2_X =        11.0
    LOCATION_2_Y =        12.0
    LOCATION_2_Z =        13.0
    LOCATION_2_RADIUS =   14.0

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
    SHORT_SLEEPTIME=15
    LONG_SLEEPTIME=20
   
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

        self.mainRobot.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.mainRobot.selfSensation=self.mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.mainRobot.getWho(),
                                                          name = self.mainRobot.getWho(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.mainRobot.getKind(),
                                                          feeling=self.mainRobot.getFeeling(),
                                                          location=self.mainRobot.getLocation())
        
        
        self.sense = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Sense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.mainRobot.subInstances.append(self.sense)
        
        
        self.muscle = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.mainRobot.subInstances.append(self.muscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.muscle.getCapabilities()
        # location, needed, because Robot delegates subrobot capability checking
        # in routing phase for Capabilities so also capabilities should have same Locations
        # in real application they are, because Robots Locations come from Capabilities
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        # correct address, to we don't use ame locakpst 127.0.0.1, but we still use ip-nmumbers in this single computer without real networking
        self.remoteMainRobot.tcpServer.address = (RobotTestCase.REMOTE_LOCALHOST, self.remoteMainRobot.tcpServer.address[1])
        remoteport = self.remoteMainRobot.tcpServer.address[1]
        print('1: remoteport '+  str(remoteport))
     
        # We should set this, because we don't run mainRobot, but call its methods
        self.assertEqual(self.remoteMainRobot, Robot.mainRobotInstance, "should have Robot.mainRobotInstance")
        self.assertEqual(self.remoteMainRobot, Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        # this can be ptoblem if tested methods use Robot.mainRobotInstance, because this points to (self.remoteMainRobot
        if self.remoteMainRobot.level == 1:
            self.remoteMainRobot.activityAverage = self.remoteMainRobot.shortActivityAverage = self.remoteMainRobot.config.getActivityAvegageLevel()
            self.remoteMainRobot.activityNumber = 0
            self.remoteMainRobot.activityPeriodStartTime = time.time()

        self.remoteMainRobot.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.remoteMainRobot.selfSensation=self.remoteMainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.remoteMainRobot.getWho(),
                                                          name = self.remoteMainRobot.getWho(),
                                                          presence = Sensation.Presence.Present,
                                                          kind=self.remoteMainRobot.getKind(),
                                                          feeling=self.remoteMainRobot.getFeeling(),
                                                          location=self.remoteMainRobot.getLocation())
        
        
        self.remoteSense = RobotTestCase.TestRobot(parent=self.remoteMainRobot,
                           instanceName='RemoteSense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.remoteMainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.remoteSense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
# don't change selfSensation self, it messes logging
#         self.remoteSense.selfSensation=self.remoteMainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
#                                                           memoryType=Sensation.MemoryType.LongTerm,
#                                                           robotType=Sensation.RobotType.Sense,# We have found this
#                                                           robot = self.remoteSense.getWho(),
#                                                           name = self.remoteSense.getWho(),
#                                                           presence = Sensation.Presence.Present,
#                                                           kind=self.remoteSense.getKind(),
#                                                           feeling=self.remoteSense.getFeeling(),
#                                                           location=self.remoteSense.getLocation())
        self.remoteMainRobot.subInstances.append(self.remoteSense)
        
        
        self.remoteMuscle = RobotTestCase.TestRobot(parent=self.remoteMainRobot,
                           instanceName='RemoteMuscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.remoteMainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.remoteMuscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
# don't change selfSensation self, it messes logging
#         self.remoteMuscle.selfSensation=self.remoteMainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
#                                                           memoryType=Sensation.MemoryType.LongTerm,
#                                                           robotType=Sensation.RobotType.Sense,# We have found this
#                                                           robot = self.remoteMuscle.getWho(),
#                                                           name = self.remoteMuscle.getWho(),
#                                                           presence = Sensation.Presence.Present,
#                                                           kind=self.remoteMuscle.getKind(),
#                                                           feeling=self.remoteMuscle.getFeeling(),
#                                                           location=self.remoteMuscle.getLocation())
        self.remoteMainRobot.subInstances.append(self.remoteMuscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.remoteMuscle.getCapabilities()
        # location, needed, because Robot delegates subrobot capability checking
        # in routing phase for Capabilities so also capabilities should have same Locations
        # in real application they are, because Robots Locations come from Capabilities
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        print('\ntearDownRemore')       
        del self.remoteMuscle
        del self.remoteSense
        del self.remoteMainRobot

    def test_Routing(self):
        print('\ntest_Sensation Routing')
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
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
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
        
        # set sensation contain one Location and muscle to contain many locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
       
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
       
        # set sensation no Locations and muscle to contain one locations and one match, routing should succeed again
        # because Sensation does not give location requirement, where to go
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
       
        self.muscle.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
     
        # set both sensation not  Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
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
        
    '''
    Tcp connection and routing. We test inside localhost SocketServer and SocketClient
    TODO This test is impossible to do with one MainRobot, because one MainRobot is not
    initiated to respond until it has send request to and we don't have mainRobot
    running to get its tested propelly
    '''
        
    def test_Tcp(self):
        print('\ntest_Sensation Routing with TCP SocketServer and SocketClient')
        
        # set first remote mainRobot
        
        # set log level Detailed, so we know what is happening
        self.setUpRemote()
        
        self.remoteMainRobot.setLogLevel(Robot.LogLevel.Detailed)
        # create tcpServe same way as MainRpbot does it, but connecting to localhost
        self.remoteMainRobot.tcpServer=TCPServer(parent=self.remoteMainRobot,
                                           memory=self.remoteMainRobot.getMemory(),
                                           hostNames=[], # no hostnames to connect, we are server side
                                           instanceName='remoteTCPServer',
                                           instanceType=Sensation.InstanceType.Remote,
                                           level=self.remoteMainRobot.level,
                                           address=(HOST,PORT))
        
        # this is hard to test
        # we could also start self.remoteMainRobot   

        self.remoteMainRobot.tcpServer.start()
        #self.remoteMainRobot.start()
        

        #self.remoteMainRobot.start()        
        # server does not start SocketClients or SocketServer untill connected
#         print ('Sleep {}s to wait tcpServer runs'.format(RobotTestCase.SLEEPTIME))
#         time.sleep(RobotTestCase.SLEEPTIME)
#         
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) > 0,'should have socketClient')        
#         localSocketClient = self.remoteMainRobot.tcpServer.socketClients[0]
#         # set log level Detailed, so we know what is happening
#         localSocketClient.setLogLevel(Robot.LogLevel.Detailed)
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) > 0,'should have socketServer')        
#         localSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
#  
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) == 2,'should have socketClient')        
#         remoteSocketClient = self.remoteMainRobot.tcpServer.socketClients[1]
#         # set log level Detailed, so we know what is happening
#         remoteSocketClient.setLogLevel(Robot.LogLevel.Detailed)
#         self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 2,'should have socketServer')        
#         remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[1]
#         
#         self.assertTrue(localSocketClient in self.remoteMainRobot.subInstances,'mainRobot should know localSocketClient')        
#         self.assertTrue(remoteSocketClient in self.remoteMainRobot.subInstances,'mainRobot should know remoteSocketClient')        
#         self.assertFalse(localSocketServer in self.remoteMainRobot.subInstances,'mainRobot should know localSocketServer')        
#         self.assertFalse(remoteSocketServer in self.remoteMainRobot.subInstances,'mainRobot should know remoteSocketServer')
        
        print ('Sleep {}s to wait remote SocketServers runs'.format(RobotTestCase.SLEEPTIME))        
        
        
        # set then local mainRobot
        
        # set log level Detailed, so we know what is happening
        self.mainRobot.setLogLevel(Robot.LogLevel.Detailed)
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
        print ('Sleep {}s to wait tcpServer runs'.format(RobotTestCase.SLEEPTIME))
        time.sleep(RobotTestCase.SLEEPTIME)
        
        self.assertTrue(len(self.mainRobot.tcpServer.socketClients) > 0,'should have socketClient')        
        localSocketClient = self.mainRobot.tcpServer.socketClients[0]
        # set log level Detailed, so we know what is happening
        localSocketClient.setLogLevel(Robot.LogLevel.Detailed)
        self.assertTrue(len(self.mainRobot.tcpServer.socketServers) > 0,'should have socketServer')        
        localSocketServer = self.mainRobot.tcpServer.socketServers[0]
 
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketClients) == 1,'should have socketClient')        
        remoteSocketClient = self.remoteMainRobot.tcpServer.socketClients[0]
        # set log level Detailed, so we know what is happening
        remoteSocketClient.setLogLevel(Robot.LogLevel.Detailed)
        self.assertTrue(len(self.remoteMainRobot.tcpServer.socketServers) == 1,'should have socketServer')        
        remoteSocketServer = self.remoteMainRobot.tcpServer.socketServers[0]
        
        self.assertTrue(localSocketClient in self.mainRobot.subInstances,'mainRobot should know localSocketClient')        
        self.assertTrue(remoteSocketClient in self.remoteMainRobot.subInstances,'mainRobot should know remoteSocketClient')        
        self.assertFalse(localSocketServer in self.mainRobot.subInstances,'mainRobot should know localSocketServer')        
        self.assertFalse(remoteSocketServer in self.remoteMainRobot.subInstances,'mainRobot should know remoteSocketServer')
        
        print ('Sleep {}s to wait self.remoteMainRobot and SocketServers runs'.format(RobotTestCase.LONG_SLEEPTIME))
        time.sleep(RobotTestCase.LONG_SLEEPTIME)
        
        # at this point we should have got back Robot sensation from elf.remoteMainRobot
        # we run self.mainRobot manually, so we emulate hot it react and connects to remote
        
#         self.assertFalse(self.mainRobot.getAxon().empty(),'self.mainRobot Axon should not be empty')
#         tranferDirection, sensation = self.mainRobot.getAxon().get()
#         self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
# 
#         print ('Sleep {}s to wait self.remoteMainRobot SocketServers runs'.format(RobotTestCase.SLEEPTIME))
#         time.sleep(RobotTestCase.SLEEPTIME)
        # now connections should be finished
        
        # check Capabilities
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  localSocketClient.getCapabilities()
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
        
              
        self.assertEqual(len(self.mainRobot.subInstances),3, 'mainRobot should know 4 subInstances') # 3 id MainRobot runs, 4 if we have made Sochet-classes ourselves
        
        # TODO if we have both local and remote SocketClient are in self.mainRobot.subInstances  it is hard to test
        # because self.mainRobot should route sensatiself.mainRobot.tcpServer.start()ons to both, because they have same capabilities and
        # then both SocketketServers wound send sensations to self.mainRobot which send sensations to muscle.
        # so muscle should get at least 3 copies of Sensation.
       
        print ('Sleep {}s to wait socketServer and socketClient are initiated'.format(RobotTestCase.SLEEPTIME))
        time.sleep(RobotTestCase.SLEEPTIME)
        
#         # fake localSocketClient ip-address, to 127.0.0.2 
#         localSocketClient.address = (RobotTestCase.FAKE_LOCALHOST, localSocketServer.address[1])
#         remoteSocketClient.address = (RobotTestCase.FAKE_LOCALHOST, remoteSocketServer.address[1])

        
        # TODO Here we could test location, capabilities and routing
        # with local and remote
        #
        # ip-number is same with local and remote, but received Sensation should not be sent back,
        # as usual functionality is
        #self.mainRobot.tcpServer.start()
        
        ###################################################################################################################################################
        # capabilities should be equal now
        #
        print('\n test tcp Capabilities')
        self.assertEqual(localSocketClient.getCapabilities(),localSocketServer.getCapabilities(), 'should have equal local capabilities')        
        self.assertEqual(remoteSocketClient.getCapabilities(),remoteSocketServer.getCapabilities(), 'should have equal remote capabilities')        
        self.assertEqual(localSocketClient.getCapabilities().toString(),remoteSocketClient.getCapabilities().toString(), 'should have equal local and remote capabilities')        
        self.assertEqual(localSocketServer.getCapabilities().toString(),remoteSocketServer.getCapabilities().toString(), 'should have equal local and remote capabilities')        
        # location should be equal now
        self.assertEqual(localSocketClient.getLocation(),localSocketServer.getLocation(), 'should have equal local location')        
        self.assertEqual(remoteSocketClient.getLocation(),remoteSocketServer.getLocation(), 'should have equal remote location')        
        self.assertEqual(localSocketClient.getLocation(),remoteSocketClient.getLocation(), 'should have equal local and remote location')        
        self.assertEqual(localSocketServer.getLocation(),remoteSocketServer.getLocation(), 'should have equal local and remote location')        

        # to routing test and because we have local and remote, we should get sensation in muscle two times
        # get local routed version and version sent to  remote, which is us
        
        ###################################################################################################################################################
        # tcp positive case
        # test same location localSocket , remoteSocket, sense, muscle
        #
        print('\n test tcp positive case')
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
        
        self.assertEqual(Wall_E_item_sensation.getReceivedFrom(), [], 'local sensation should not have receivedFrom information at the beginning of test')
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
        
        # test routing to remote muscle from local sense 
        print ('Sleep {}s to wait Sensation is transferred by tcp'.format(RobotTestCase.SLEEPTIME))
        time.sleep(RobotTestCase.SLEEPTIME)

        # remote SocketServer should have got it abd when it is living process, it has put it to remoteMainRobot
        self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
        tranferDirection, sensation = self.remoteMainRobot.getAxon().get()

        # test routing to remoteMuscle
        self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
        tranferDirection, sensation = self.remoteMuscle.getAxon().get()
        
        # test, that sensation is same than transferred
        self.assertEqual(Wall_E_item_sensation, sensation, 'send and received sensations should be equal')
        
        # test, that local sensation to be transferred does not contain  receicedFrom information
        self.assertEqual(Wall_E_item_sensation.getReceivedFrom(), [], 'local sensation should not have receivedFrom information')

        # test, that remote sensation transferred does contain  rfeceicedFron information
        self.assertEqual(Wall_E_item_sensation.getReceivedFrom(), [RobotTestCase.LOCALHOST], 'remote sensation should have receivedFrom information')

        # now muscle should not have more sensations
        self.assertTrue(self.remoteMuscle.getAxon().empty(),'muscle Axon should be empty')
        
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
        
        
        ###################################################################################################################################################
        # tcp negative case
        # localSocketServer has different location
        #
        print('\n test tcp negative case, localSocketServer has different location')
        
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        
        ################ test same location sense, muscle ####################
        ################ test same location localSocket , remoteSocket ####################
        ################ but location localSocket , remoteSocket differs ####################
        
        ################ change local localSocketServer location, so localSocketClient should not capability to handle this message ####################        
        localSocketServer.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
        
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
        
      
        # remote SocketServer should have NOT got it and when it is living process, it has NOT put it to remoteMainRobot
        print ('Sleep {}s to wait Sensation is transferred by tcp'.format(RobotTestCase.SLEEPTIME))
        time.sleep(RobotTestCase.SLEEPTIME)
        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
        
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
        
        ###################################################################################################################################################
        # tcp positive case again
        # localSocketServer has same location again
        #
        print('\n tcp positive case again, localSocketServer has same location again')
        localSocketServer.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        
        ################ test same location localSocket , remoteSocket, sense, muscle ####################
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
        
        # test routing to remote muscle from local sense 
        print ('Sleep {}s to wait Sensation is transferred by tcp'.format(RobotTestCase.SLEEPTIME))
        time.sleep(RobotTestCase.SLEEPTIME)

        # TODO this fails OOPS, recycle case, STUDY
        # remote SocketServer should have got it and when it is living process, it has put it to remoteMainRobot
        self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should not be empty')
        tranferDirection, sensation = self.remoteMainRobot.getAxon().get()

        # test routing to remoteMuscle
        self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.remoteMuscle.getAxon().empty(),'remoteMuscle Axon should not be empty')
        tranferDirection, sensation = self.remoteMuscle.getAxon().get()
        
        # now muscle should not have more sensations
        self.assertTrue(self.remoteMuscle.getAxon().empty(),'muscle Axon should be empty')
        
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
        
        
        
        
        
        ################ test same location sense, muscle ####################
        ################ test same location localSocket , remoteSocket ####################
        ################ but location localSocket , remoteSocket differs ####################
        
        
        
        
        ###################################################################################################################################################
        # tcp negative case
        # muscle and remoteMuscle have different location than local sense
        #
        
        
        # same routing should fail. if Sensation's and Robot's Locations don't match
        # but SocketClients location is not changed, it still sends sensation to remote
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        localSocketServer.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)

        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
        self.remoteMuscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
        #self.muscle.setCapabilities(capabilities)
        
        # test local
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should not be routed to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
                
        # test remote
        print ('Sleep {}s to wait Sensation is transferred by tcp'.format(RobotTestCase.SLEEPTIME))
        time.sleep(RobotTestCase.SLEEPTIME)
        # should be routed to mainRobot
        self.assertFalse(self.remoteMainRobot.getAxon().empty(),'remoteMainRobot Axon should not be empty')
        tranferDirection, sensation = self.remoteMainRobot.getAxon().get()
        # test routing to muscle
        self.remoteMainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should not be routed to muscle
        self.assertTrue(self.remoteMuscle.getAxon().empty(),'remoteMuscle. Axon should be empty')
        
        
        ################
        # TODO not done
       
        # set sensation contain one Location and muscle to contain many locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
       
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
        #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
       
        # set sensation no Locations and muscle to contain one locations and one match, routing should succeed again
        # because Sensation does not give location requirement, where to go
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
       
        self.muscle.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
     
        # set both sensation not  Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        Wall_E_item_sensation.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
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
        
        # done
        self.remoteMainRobot.stop()
        self.mainRobot.tcpServer.stop()
        
        localSocketClient.stop()        
        localSocketServer.stop()

        remoteSocketClient.stop()        
        remoteSocketServer.stop()
       
        print ('Sleep {}s to wait self.remoteMainRobot and self.mainRobot.tcpServer, localSocketServer and localSocketClient to stop'.format(RobotTestCase.SLEEPTIME))

        time.sleep(RobotTestCase.SLEEPTIME)
        
        self.tearDownRemote()
        
        # del all
        del self.mainRobot.tcpServer

     
     
    '''
    These tests fail. because Location-Sensation routing is not implemented
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
                                                 name=RobotTestCase.LOCATION_1_NAME)
        Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.sense.associate(sensation=Wall_E_location_sensation)
        # now sense and Item are in RobotTestCase.LOCATION_1_NAME location
        
        
        # in muscle we should set also capabilities, look SetUp
        #self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
        muscle_location_sensation = self.sense.createSensation(
                                                 memoryType=Sensation.MemoryType.Sensory,
                                                 sensationType=Sensation.SensationType.Location,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.SET_1_1_LOCATIONS_2)
        self.muscle.associate(sensation=muscle_location_sensation)
        # now muscle is in RobotTestCase.SET_1_1_LOCATIONS_2
        
       #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_2)
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
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        #capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        
#         self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
#         #Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
#         Wall_E_location_sensation = self.sense.createSensation(
#                                                  memoryType=Sensation.MemoryType.Sensory,
#                                                  sensationType=Sensation.SensationType.Location,
#                                                  robotType=Sensation.RobotType.Sense,
#                                                  name=RobotTestCase.LOCATION_1_NAME)
#         Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
#        
#         self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
#         capabilities  =  self.muscle.getCapabilities()
#         capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
       
        
        self.sense.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #Wall_E_item_sensation.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
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
        
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        #Wall_E_item_sensation.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
       
        self.muscle.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
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
        
        self.sense.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #Wall_E_item_sensation.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocation(RobotTestCase.SET_EMPTY_LOCATIONS)
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

 