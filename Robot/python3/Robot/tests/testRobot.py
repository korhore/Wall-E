'''
Created on 14.02.2020
Updated on 14.02.2020
@author: reijo.korhonen@gmail.com

test Robot class

Tests basic functionality of Robot class
Mosts importantis to test Sensation Routing functionality
We cleare one ;ainRobot level Robot and sense and muscle Robots
to study functionality.

python3 -m unittest tests/testRobot.py


'''
import time as systemTime

import unittest
from Sensation import Sensation
from Robot import Robot
from Axon import Axon

class RobotTestCase(unittest.TestCase):
    '''
    
    We should play as sense robot and muacle Robot
        - Wall_E_item
        - Image
        - voice
    '''
    
    SET_1_1_LOCATIONS_1 = ['testLocation']
    SET_1_1_LOCATIONS_2 = ['Ubuntu']
    SET_1_2_LOCATIONS =   ['testLocation', 'Ubuntu']
    SET_EMPTY_LOCATIONS = []

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
#     def setLocations(self, locations):
#         self.locations = locations
#     def getLocations(self):
#         return self.locations
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
        self.mainRobot.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
        
        self.sense = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Sense',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.sense.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
        self.mainRobot.subInstances.append(self.sense)
        
        
        self.muscle = RobotTestCase.TestRobot(parent=self.mainRobot,
                           instanceName='Muscle',
                           instanceType= Sensation.InstanceType.SubInstance,
                           level=2)
        self.muscle.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
        self.mainRobot.subInstances.append(self.muscle)
                
        #set muscle capabilities  Item, Image, Voice
        capabilities  =  self.muscle.getCapabilities()
        # locations, needed, because Robot delegates subrobot capability checking
        # in routing phase for Capabilities so also capabilities should have same Locations
        # in real application they are, because Robots Locations come from Capabilities
        capabilities.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
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
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation, association = self.muscle.getAxon().get()
        
        self.assertEqual(len(self.sense.getMemory().presentItemSensations), 1, 'len(self.sense.getMemory().presentItemSensations should be 1')
        
        # same routing should fail. if Sensation's and Robot's Locations don't match
        self.sense.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocations(RobotTestCase.SET_1_1_LOCATIONS_2)
        capabilities  =  self.muscle.getCapabilities()
        capabilities.setLocations(RobotTestCase.SET_1_1_LOCATIONS_2)
        self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should not be routed to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty')
        
        # set sensation contain  one Location and muscle to contain many locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        self.muscle.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
        capabilities  =  self.muscle.getCapabilities()
        capabilities.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
        self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation, association = self.muscle.getAxon().get()

        # set sensation contain many Locations and muscle to contain one locations and one match, routing should succeed again
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
        Wall_E_item_sensation.setLocations(RobotTestCase.SET_1_2_LOCATIONS)
       
        self.muscle.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        capabilities  =  self.muscle.getCapabilities()
        capabilities.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
        #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation, association = self.muscle.getAxon().get()
       
        # set sensation no Locations and muscle to contain one locations and one match, routing should succeed again
        # because Sensation does not give location requirement, where to go
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
        Wall_E_item_sensation.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        capabilities  =  self.muscle.getCapabilities()
        capabilities.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
       #  test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation, association = self.muscle.getAxon().get()
 
        # set sensation Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
        Wall_E_item_sensation.setLocations(RobotTestCase.SET_1_1_LOCATIONS_1)
       
        self.muscle.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
        capabilities  =  self.muscle.getCapabilities()
        capabilities.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
        self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
       # TODO test routing to muscle
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')
        tranferDirection, sensation, association = self.muscle.getAxon().get()
     
        # set both sensation not  Locations and muscle not Location , routing should succeed again
        # because Robot does not give location requirement, what to accept
        # in muscle we should set also capabilities, look SetUp
        
        self.sense.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
        Wall_E_item_sensation.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
       
        self.muscle.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
        capabilities  =  self.muscle.getCapabilities()
        capabilities.setLocations(RobotTestCase.SET_EMPTY_LOCATIONS)
        self.muscle.setCapabilities(capabilities)
        
        # test
        self.sense.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # should be routed to mainRobot
        self.assertFalse(self.mainRobot.getAxon().empty(),'mainRobot Axon should not be empty')
        tranferDirection, sensation, association = self.mainRobot.getAxon().get()
       #  test routing to muscle
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty before self.mainRobot.process')        
        self.mainRobot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation, association=association)
        # should be routed to mainRobot
        self.assertFalse(self.muscle.getAxon().empty(),'muscle Axon should not be empty')        
        tranferDirection, sensation, association = self.muscle.getAxon().get()
        self.assertTrue(self.muscle.getAxon().empty(),'muscle Axon should be empty after self.muscle.getAxon().get()')        
     
       
if __name__ == '__main__':
    unittest.main()

 