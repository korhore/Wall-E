'''
Created on 17.04.2021
Updated on 25.04.2021
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
#TEST_COMMUNICATION_INTERVAL=5.0
TEST_SLEEPTIME = 3.0
TEST_SLEEPTIMERANDOM = 1.0

from VisualCommunication.VisualCommunication import VisualCommunication
from Communication.Communication import Communication
#Communication.COMMUNICATION_INTERVAL = TEST_COMMUNICATION_INTERVAL
VisualCommunication.SLEEPTIME = TEST_SLEEPTIME
VisualCommunication.SLEEPTIMERANDOM = TEST_SLEEPTIMERANDOM

from CommunicationTest import CommunicationTest

class VisualCommunicationTestCase(unittest.TestCase, CommunicationTest):

    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        
#         Robot.mainRobotInstance = self
        self.mainNames = self.MAINNAMES

        # Robot to test        
        self.visualCommunication = VisualCommunication(mainRobot=self,
                                           parent=self,
                                           instanceName='VisualCommunication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.setRobotMainNames(self.visualCommunication, self.MAINNAMES)
        self.setRobotLocations(self.visualCommunication, self.getLocations())
            
        # should get Identity for proper functionality. Use Wall-E Identity in test
        self.visualCommunication.imageSensations, self.visualCommunication.voiceSensations = \
            self.visualCommunication.getIdentitySensations(name=VisualCommunicationTestCase.NAME)
        self.assertTrue(len(self.visualCommunication.getMemory().getRobot().voiceSensations) > 0, "should have identity for testing")
        
        self.doSetUp(robot=self.visualCommunication)#, communication=self.visualCommunication)
        
       
        
 
        # start VisualCommunication       
        self.visualCommunication.start()
        
        sleeptime = VisualCommunication.SLEEPTIME+VisualCommunication.SLEEPTIMERANDOM
        #sleeptime = VisualCommunication.SLEEPTIMERANDOM
        print("--- test sleeping " + str(sleeptime) + " second until starting to test")
        systemTime.sleep(sleeptime ) # let VisualCommunication start before waiting it to stops
        self.communication=None
        for subRobot in self.visualCommunication.getSubInstances():
            if subRobot.getName() == 'Communication':
                self.communication = subRobot
        self.assertFalse(self.communication==None, "No Communication found")
        self.assertTrue(self.communication.running, "No Communication running'")
        self.doSetUpCommunication(communication=self.communication)
        #Forse same location
#         self.setRobotLocations(self.communication, self.getLocations())
#          # TODO should set these, deleting others missing
#         for location in self.communication.getLocations():
#             self.communication.itemConversations[location] =\
#                 Communication.ConversationWithItem(robot=self.communication, location=location)
#         self.communication.robotConversation =\
#                 Communication.ConversationWithRobot(robot=self)
#         
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get(robot=self)
            self.log(logStr='setUp self.getAxon().get(robot=self) sensation = {}'.format(sensation.toDebugStr()))
        

    def tearDown(self):
        print('\ntearDown\nPRESS STOP!\n')       
        while self.visualCommunication.running:
            print('\ntearDown\n still self.visualCommunication.running PRESS STOP! if you did not yet\n')       
            systemTime.sleep(1)

        self.doTearDown()
        del self.visualCommunication
        print('\ntearDown done')       
        
    '''
    TensorfloClassafication produces
    Item.name Working Out
    
   '''    
    def test_PresenseItemPresentRobot(self):
        print('\ntest_PresenseItemPresentRobot\n')       
        self.doTest_PresenseItemPresentRobot(robot=self.visualCommunication, isWait = True)
        print('\ndone test_PresenseItemPresentRobot\n')       
       
            
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def test_PresenseItemAbsentRobot(self):
        print('\ntest_PresenseItemAbsentRobot\n')       
        self.doTest_PresenseItemAbsentRobot(robot=self.visualCommunication, isWait = True)
        

    '''
    TensorfloClassification produces
    Item.name Working Out
    Sensations outside Robot are in same Robot.mainNames and robotType=Sensation.RobotType.Sense
    so this test is same than without parameters
    '''    
    def test_2_Presense(self):
        print('\ntest_2_Presense\n')       
        self.doTest_2_Presense(robot=self.visualCommunication, communication=self.communication, isWait = True)
        
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in other Robot.mainNames and robotType=Sensation.RobotType.Communication
    so this test result should  same than with test where robotType=Sensation.RobotType.Sense,
    because Communication should handle those sensation equally, when Robot.mainNames differ
    '''    
    def test_3_Presense(self):
        print('\ntest_3_Presense\n')       
        self.doTest_3_Presense(robot=self.visualCommunication, communication=self.communication, isWait = True)

        
    '''
    Voice comes from this Robots Sense-Robot (Microphone)
    '''    
        
    def test_ProcessItemImageVoiceFromSameRobotSenses(self):
        print('\ntest_ProcessItemImageVoiceFromSameRobotSenses\n')
        self.doTest_ProcessItemImageVoiceFromSameRobotSenses(robot = self.visualCommunication, isWait = True)
        
        
if __name__ == '__main__':
    unittest.main()

 