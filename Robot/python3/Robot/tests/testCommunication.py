'''
Created on 21.06.2019
Updated on 14.04.2021
@author: reijo.korhonen@gmail.com

test Association class
python3 -m unittest tests/testCommunication.py


'''
import time as systemTime
import os

import unittest
from Sensation import Sensation
# import Communication, but
# set Communication.COMMUNICATION_INTERVAL smaller,
# so test runs faster, when no waits normal time 30s, when we don't get
# response from person
TEST_COMMUNICATION_INTERVAL=1.0 
from Communication.Communication import Communication
Communication.COMMUNICATION_INTERVAL = TEST_COMMUNICATION_INTERVAL

from Association.Association import Association
from Axon import Axon
from Robot import Robot

from CommunicationTest import CommunicationTest

class CommunicationTestCase(unittest.TestCase, CommunicationTest):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    


    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        
#         Robot.mainRobotInstance = self
        self.mainNames = self.MAINNAMES

        # Robot to test        
        self.communication = Communication(mainRobot=self,
                                           parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.setRobotMainNames(self.communication, self.MAINNAMES)
        self.setRobotLocations(self.communication, self.getLocations())
            
        # should get Identity for proper functionality. Use Wall-E Identity in test
        self.communication.imageSensations, self.communication.voiceSensations = \
            self.communication.getIdentitySensations(name=CommunicationTestCase.NAME)
        self.assertTrue(len(self.communication.getMemory().getRobot().voiceSensations) > 0, "should have identity for testing")
        
        self.doSetUp(robot=self.communication, communication=self.communication)
        

    def tearDown(self):
        print('\ntearDown')       
        self.doTearDown()

        del self.communication
        
    '''
    TensorfloClassafication produces
    Item.name Working Out
    
   '''    
    def test_PresenseItemPresentRobot(self):
        self.doTest_PresenseItemPresentRobot(robot=self.communication, isWait=False)
       
            
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def test_PresenseItemAbsentRobot(self):
        self.doTest_PresenseItemAbsentRobot(robot=self.communication, isWait=False)
        

    '''
    TensorfloClassification produces
    Item.name Working Out
    Sensations outside Robot are in same Robot.mainNames and robotType=Sensation.RobotType.Sense
    so this test is same than without paramweters
    '''    
    def test_2_Presense(self):
        #self.do_test_Presense(mainNames=self.MAINNAMES, robotType=Sensation.RobotType.Sense)
        self.doTest_2_Presense(robot=self.communication, isWait=False)
        
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in other Robot.mainNames and robotType=Sensation.RobotType.Communication
    so this test result should  same than with test where robotType=Sensation.RobotType.Sense,
    because Communication should handle those sensation equally, when Robot.mainNames differ
    '''    
    def test_3_Presense(self):
        #self.do_test_Presense(mainNames=self.OTHERMAINNAMES, robotType=Sensation.RobotType.Communication)
        self.doTest_3_Presense(robot=self.communication, isWait=False)

        
        
    def test_ProcessItemImageVoiceFromSameRobotSenses(self):
        #responses
        # - come from mainNames=self.OTHERMAINNAMES
        # - are marked as robotType=Sensation.RobotType.Muscle
        #
        # but Communication should handle these responses as person said,
        # Microphone detects as Sense type Voices in same mainNames
        print('\ntest_ProcessItemImageVoiceFromSameRobotSenses\n')
        self.doTest_ProcessItemImageVoiceFromSameRobotSenses(robot = self.communication, isWait = True)
        
        
if __name__ == '__main__':
    unittest.main()

 