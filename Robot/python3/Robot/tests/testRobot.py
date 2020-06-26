'''
Created on 14.02.2020
Updated on 25.06.2020
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
import time as systemTime

import unittest
from Sensation import Sensation
from Robot import Robot
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
                           instanceType= Sensation.InstanceType.Real,
                           level=1)
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
        self.sense.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
# don't change selfSensation self, it messes logging
#         self.sense.selfSensation=self.mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
#                                                           memoryType=Sensation.MemoryType.LongTerm,
#                                                           robotType=Sensation.RobotType.Sense,# We have found this
#                                                           robot = self.sense.getWho(),
#                                                           name = self.sense.getWho(),
#                                                           presence = Sensation.Presence.Present,
#                                                           kind=self.sense.getKind(),
#                                                           feeling=self.sense.getFeeling(),
#                                                           location=self.sense.getLocation())
        self.mainRobot.subInstances.append(self.sense)
        
        
        self.muscle = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.muscle.setLocation(RobotTestCase.SET_1_1_LOCATIONS_1)
# don't change selfSensation self, it messes logging
#         self.muscle.selfSensation=self.mainRobot.createSensation(sensationType=Sensation.SensationType.Robot,
#                                                           memoryType=Sensation.MemoryType.LongTerm,
#                                                           robotType=Sensation.RobotType.Sense,# We have found this
#                                                           robot = self.muscle.getWho(),
#                                                           name = self.muscle.getWho(),
#                                                           presence = Sensation.Presence.Present,
#                                                           kind=self.muscle.getKind(),
#                                                           feeling=self.muscle.getFeeling(),
#                                                           location=self.muscle.getLocation())
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


    def tearDown(self):
        print('\ntearDown')       
        del self.muscle
        del self.sense
        del self.mainRobot
        
    def test_Routing(self):
        print('\ntest_Sensation Routing')
        history_sensationTime = systemTime.time() -2*RobotTestCase.ASSOCIATION_INTERVAL

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Presense')
        #systemTime.sleep(0.1)  # wait to get really even id
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
    These tests fail. because Location-Sensation routing is not implemented
    '''     
     
    def test_Routing_LocationSensation(self):
        print('\ntest_Sensation Routing with Location Sensation')
        history_sensationTime = systemTime.time() -2*RobotTestCase.ASSOCIATION_INTERVAL

        self.assertEqual(self.mainRobot.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Presense')
        #systemTime.sleep(0.1)  # wait to get really even id
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

 