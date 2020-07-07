'''
Created on 14.02.2020
Updated on 04.07.2020
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
    
    LOCATION_1 = ['testLocation']
    LOCATION_2 = ['Ubuntu']
    SET_1_2_LOCATIONS =   ['testLocation', 'Ubuntu']
    EMPTY_LOCATION = ''
    
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

        self.mainRobot.setLocations(RobotTestCase.LOCATION_1)
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
        self.sense.setLocations(RobotTestCase.LOCATION_1)
        self.mainRobot.subInstances.append(self.sense)
        
        
        self.muscle = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.mainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.muscle.setLocations(RobotTestCase.LOCATION_1)
        self.mainRobot.subInstances.append(self.muscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.muscle.getCapabilities()
        # location, needed, because Robot delegates subrobot capability checking
        # in routing phase for Capabilities so also capabilities should have same Locations
        # in real application they are, because Robots Locations come from Capabilities
        # deprecated capabilities.setLocations(RobotTestCase.LOCATION_1)
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

        self.remoteMainRobot.setLocations(RobotTestCase.LOCATION_1)
        self.remoteMainRobot.selfSensation=self.remoteMainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
                                                          memoryType=Sensation.MemoryType.LongTerm,
                                                          robotType=Sensation.RobotType.Sense,# We have found this
                                                          robot = self.remoteMainRobot.getWho(),
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
        self.remoteSense.setLocations(RobotTestCase.LOCATION_1)
        self.remoteMainRobot.subInstances.append(self.remoteSense)
        
        
        self.remoteMuscle = RobotTestCase.TestRobot(parent=self.remoteMainRobot,
                           instanceName='RemoteMuscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.assertEqual(self.remoteMainRobot,Robot.getMainRobotInstance(), "should have Robot.mainRobotInstance")
        self.remoteMuscle.setLocations(RobotTestCase.LOCATION_1)
        self.remoteMainRobot.subInstances.append(self.remoteMuscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.remoteMuscle.getCapabilities()
        # location, needed, because Robot delegates subrobot capability checking
        # in routing phase for Capabilities so also capabilities should have same Locations
        # in real application they are, because Robots Locations come from Capabilities
        # deprecated capabilities.setLocations(RobotTestCase.LOCATION_1)
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
        self.sense.setLocations(RobotTestCase.LOCATION_1)
        Wall_E_item_sensation.setLocations(RobotTestCase.LOCATION_1)
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocations(RobotTestCase.LOCATION_2)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATION_2)
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
        
        # TODO now we use one location, not many
        # set sensation contain one Location and muscle to contain many locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocations(RobotTestCase.LOCATION_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATION_1)
        #self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation= self.mainRobot.getAxon().get()

       # test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()

        # set sensation contain many Locations and muscle to contain one locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocations(RobotTestCase.LOCATION_1)
        Wall_E_item_sensation.setLocations(RobotTestCase.LOCATION_1)
       
        self.muscle.setLocations(RobotTestCase.LOCATION_1)
        
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
        
        self.sense.setLocations(RobotTestCase.EMPTY_LOCATION)
        Wall_E_item_sensation.setLocations(RobotTestCase.EMPTY_LOCATION)
       
        self.muscle.setLocations(RobotTestCase.LOCATION_1)
        
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
        
        self.sense.setLocations(RobotTestCase.LOCATION_1)
        Wall_E_item_sensation.setLocations(RobotTestCase.LOCATION_1)
       
        self.muscle.setLocations(RobotTestCase.EMPTY_LOCATION)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation = self.mainRobot.getAxon().get()
       #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation = self.muscle.getAxon().get()
     
        # set both sensation not  Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocations(RobotTestCase.EMPTY_LOCATION)
        Wall_E_item_sensation.setLocations(RobotTestCase.EMPTY_LOCATION)
       
        self.muscle.setLocations(RobotTestCase.EMPTY_LOCATION)
        
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
        # global sensation, that goes every location, this should success
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_no_location)
       

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
         
        # global sensation, that goes every location
        Wall_E_item_sensation_no_location = self.sense.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.NAME,
                                                 score=RobotTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)

        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should be empty BEFORE we test')
        self.assertEqual(Wall_E_item_sensation.getLocations(), RobotTestCase.LOCATION_1, 'sensation should have location {} BEFORE we test'.format(RobotTestCase.LOCATION_1))
        # set locations
        self.localSocketServer.setLocations(RobotTestCase.LOCATION_2)
        
        
        # with different location we should fail
        self.do_tcp_negative_case_sensation(sensationToSend = Wall_E_item_sensation)

        # with global sensation, that goes every location, we should success        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_no_location)
        
        # set receiving robot as global setting its location empty
        # set locations
        self.localSocketServer.setLocations(RobotTestCase.EMPTY_LOCATION)
        self.remoteMuscle.setLocations(RobotTestCase.EMPTY_LOCATION)
        
        # with sensation with different location we should success, because receiver accepts all        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation)
        # with global sensation, that goes every location, we should success        
        self.do_tcp_positive_case_sensation(sensationToSend = Wall_E_item_sensation_no_location)
        
        # set locations back
        self.localSocketServer.setLocations(RobotTestCase.LOCATION_1)
        self.remoteMuscle.setLocations(RobotTestCase.LOCATION_1)
        #localSocketClient.setLocations(RobotTestCase.LOCATION_1)
        
        
        
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
        while not self.remoteMainRobot.getAxon().empty() and time.time() < endTime:
            time.sleep(RobotTestCase.WAIT_STEP)
        
        self.assertTrue(self.remoteMainRobot.getAxon().empty(),'remoteMainRobote Axon should be empty')
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
      
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
        self.sense.setLocations(RobotTestCase.LOCATION_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATION_1)
        self.sense.associate(sensation=Wall_E_location_sensation)
        # now sense and Item are in RobotTestCase.LOCATION_1_NAME location
        
        
        # in muscle we should set also capabilities, look SetUp
        #self.muscle.setLocations(RobotTestCase.LOCATION_2)
        muscle_location_sensation = self.sense.createSensation(
                                                 memoryType=Sensation.MemoryType.Sensory,
                                                 sensationType=Sensation.SensationType.Location,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=RobotTestCase.LOCATION_2)
        self.muscle.associate(sensation=muscle_location_sensation)
        # now muscle is in RobotTestCase.LOCATION_2
        
       #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATION_2)
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
        self.muscle.setLocations(RobotTestCase.LOCATION_1)
        #capabilities  =  self.muscle.getCapabilities()
        #capabilities.setLocations(RobotTestCase.LOCATION_1)
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
        
#         self.sense.setLocations(RobotTestCase.LOCATION_1)
#         #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATION_1)
#         Wall_E_location_sensation = self.sense.createSensation(
#                                                  memoryType=Sensation.MemoryType.Sensory,
#                                                  sensationType=Sensation.SensationType.Location,
#                                                  robotType=Sensation.RobotType.Sense,
#                                                  name=RobotTestCase.LOCATION_1_NAME)
#         Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
#        
#         self.muscle.setLocations(RobotTestCase.LOCATION_1)
#         capabilities  =  self.muscle.getCapabilities()
#         capabilities.setLocations(RobotTestCase.LOCATION_1)
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
       
        
        self.sense.setLocations(RobotTestCase.EMPTY_LOCATION)
        #Wall_E_item_sensation.setLocations(RobotTestCase.EMPTY_LOCATION)
       
        self.muscle.setLocations(RobotTestCase.LOCATION_1)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.LOCATION_1)
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
        
        self.sense.setLocations(RobotTestCase.LOCATION_1)
        #Wall_E_item_sensation.setLocations(RobotTestCase.LOCATION_1)
        Wall_E_item_sensation.associate(sensation=Wall_E_location_sensation)
       
        self.muscle.setLocations(RobotTestCase.EMPTY_LOCATION)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.EMPTY_LOCATION)
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
        
        self.sense.setLocations(RobotTestCase.EMPTY_LOCATION)
        #Wall_E_item_sensation.setLocations(RobotTestCase.EMPTY_LOCATION)
       
        self.muscle.setLocations(RobotTestCase.EMPTY_LOCATION)
        #capabilities  =  self.muscle.getCapabilities()
        # deprecated capabilities.setLocations(RobotTestCase.EMPTY_LOCATION)
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

 