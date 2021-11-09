'''
Created on 12.03.2020
Updated on 25.03.2021
@author: reijo.korhonen@gmail.com

test Visual class
python3 -m unittest tests/testVisual.py


'''
import time as systemTime
import os
import shutil
from PIL import Image as PIL_Image

import unittest
from Sensation import Sensation
from Robot import Robot
from Visual.Visual import Visual
from Association.Association import Association
from Communication.Communication import Communication
from Axon import Axon

class VisualTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    TEST_RUNS=5
    #TEST_RUNS=1
    ASSOCIATION_INTERVAL=3.0
    #TEST_TIME=300 # 5 min, when debugging
    TEST_TIME=30 # 30s when normal test

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
    
    MAINNAMES = ["VisualTestCaseMainName"]
    OTHERMAINNAMES = ["OTHER_VisualTestCaseMainName"]

    LOCATIONS_1 = ["location1"]
    LOCATIONS_2 = ["OtherLocation"]
    LOCATIONS_1_2 = ["location1","OtherLocation"]
    ALL_LOCATIONS = [LOCATIONS_1,LOCATIONS_2,LOCATIONS_1_2]
    locationsInd = 0
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getName(self):
        return VisualTestCase.NAME
    def setMainNames(self, mainNames):
        self.mainNames = mainNames
    def getMainNames(self):
        return self.mainNames
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
    def getParent(self):
        return None
    def log(self, logStr, logLevel=None):
        if logLevel == None:
            logLevel = self.visual.LogLevel.Normal
        if logLevel <= self.visual.getLogLevel():
             print(self.visual.getName() + ":" + str( self.visual.config.level) + ":" + Sensation.Modes[self.visual.mode] + ": " + logStr)

    '''
    Testing    
    '''
    

    '''
    Testing    
    '''
    
    def setUp(self):
        self.mainNames = self.MAINNAMES
        self.axon = Axon(robot=self) # parent axon
        self.visual = Visual(mainRobot=self,
                             parent=self,
                             instanceName='Visual',
                             instanceType= Sensation.InstanceType.SubInstance,
                             level=2)
        self.visual.locations=self.LOCATIONS_1_2

        # define time in history, that is different than in all tests
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*max(VisualTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.stopSensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Working,
                                            sensationType=Sensation.SensationType.Stop,
                                            robotType=Sensation.RobotType.Sense,
                                            locations=self.getLocations())

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.visual.createSensation(time=self.history_sensationTime,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VisualTestCase.NAME,
                                                      score=VisualTestCase.SCORE_1,
                                                      presence = Sensation.Presence.Present,
                                                      locations=self.LOCATIONS_1_2)
        # Image is in LongTerm memoryType, it comes from TensorFlowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = self.visual.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       locations=self.LOCATIONS_1_2)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = self.visual.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data="1",
                                                       locations=self.LOCATIONS_1_2)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)

       
         
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)
#         
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())

        # get identity for self.visual as MainRobot does it (for images only)        
        self.studyOwnIdentity(robot=self.visual)
       
    def getSensations(self):

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        locations=self.getLocations()
        self.Wall_E_item_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VisualTestCase.NAME,
                                                      score=VisualTestCase.SCORE_1,
                                                      presence = Sensation.Presence.Present,
                                                      locations=locations)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
        image = self.visual.selfImage
        self.assertNotEqual(image, None, "image should not be None in this test")

        self.Wall_E_image_sensation = self.visual.createSensation( memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       image=image,
                                                       locations=locations)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
#         if len(self.visual.getMemory().getRobot().images) > 1:
#             image=self.visual.getMemory().getRobot().images[1]
        if len(self.visual.imageSensations) > 1:
           image = self.visual.imageSensations[1].getImage()
        else:
            image=None
        self.assertNotEqual(image, None, "image should not be None in this test")
        self.Wall_E_image_sensation_2 = self.visual.createSensation( memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       image=image,
                                                       locations=locations)
        
        
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation_2)

        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        #self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 4)# 4/3
        self.assertTrue(len(self.Wall_E_item_sensation.getAssociations()) == 3 or len(self.Wall_E_item_sensation.getAssociations()) == 4)# 3/4
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)#/1/2
        self.assertTrue(len(self.Wall_E_image_sensation.getAssociations()) == 1 or len(self.Wall_E_image_sensation.getAssociations()) == 2)#/1/2
        self.assertTrue(len(self.Wall_E_image_sensation_2.getAssociations()) == 1 or len(self.Wall_E_image_sensation_2.getAssociations()) == 2)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data="1",
                                                       locations=locations)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
        # these connected each other
        self.assertTrue(len(self.Wall_E_item_sensation.getAssociations()) == 4 or len(self.Wall_E_item_sensation.getAssociations()) ==  5)
        self.assertTrue(len(self.Wall_E_image_sensation.getAssociations()) == 2 or len(self.Wall_E_image_sensation.getAssociations()) == 3) 
        self.assertTrue(len(self.Wall_E_voice_sensation.getAssociations()) == 2 or len(self.Wall_E_voice_sensation.getAssociations()) == 3)

        self.assertTrue(len(self.Wall_E_item_sensation.getAssociations()) == 4 or len(self.Wall_E_item_sensation.getAssociations()) == 5)
        self.assertTrue(len(self.Wall_E_image_sensation.getAssociations()) == 2 or len(self.Wall_E_image_sensation.getAssociations()) == 3)
        self.assertTrue(len(self.Wall_E_voice_sensation.getAssociations()) == 2 or len(self.Wall_E_voice_sensation.getAssociations()) == 3)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())
        
        # communication
        self.communication_CommunicationNotStarted_sensation = self.visual.createSensation(
                                                      memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.RobotState,
                                                      robotState=Sensation.RobotState.CommunicationNotStarted,
                                                      locations=self.LOCATIONS_1_2)
        self.communication_CommunicationOn_sensation = self.visual.createSensation(
                                                      memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.RobotState,
                                                      robotState=Sensation.RobotState.CommunicationOn,
                                                      locations=self.LOCATIONS_1_2)
        self.communication_CommunicationWaiting_sensation = self.visual.createSensation(
                                                      memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.RobotState,
                                                      robotState=Sensation.RobotState.CommunicationWaiting,
                                                      locations=self.LOCATIONS_1_2)
        self.communication_CommunicationEnded_sensation = self.visual.createSensation(
                                                      memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.RobotState,
                                                      robotState=Sensation.RobotState.CommunicationEnded,
                                                      locations=self.LOCATIONS_1_2)
        
        self.communication_item_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Muscle,
                                                      name=VisualTestCase.NAME,
                                                      presence = Sensation.Presence.Present,
                                                      locations=self.LOCATIONS_1_2)

        image = self.visual.selfImage
        self.assertNotEqual(image, None, "image should not be None in this test")
        self.communication_image_sensation = self.visual.createSensation( memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       image=image,
                                                       locations=locations)
        
        self.communication_voice_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       data="1",
                                                       locations=locations)
        
        self.communication_positive_feeling_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Feeling,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       firstAssociateSensation=self.communication_item_sensation,
                                                       otherAssociateSensation=self.communication_voice_sensation,
             #         self.communication_CommunicationNotStarted_sensation = self.visual.createSensation(
#                                                       memoryType=Sensation.MemoryType.Sensory,
#                                                       sensationType=Sensation.SensationType.RobotState,
#                                                       robotState=Sensation.RobotState.RobotState.CommunicationNotStarted,
#                                                       locations=self.LOCATIONS_1_2)
                                          positiveFeeling=True,
                                                       locations=locations)
    '''
    helper method to return different kind locations
    '''       
    def getLocations(self):    
        if self.locationsInd >= len(self.ALL_LOCATIONS):
            self.locationsInd=0
        locations = self.ALL_LOCATIONS[self.locationsInd]
        self.locationsInd = self.locationsInd+1
        return locations
        


    def tearDown(self):
        #self.visual.stop()
        #self.assertEqual(self.visual.getAxon().empty(), False, 'Axon should not be empty after self.visual.stop()')
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get(robot=self)
            self.assertTrue(sensation.getSensationType() == Sensation.SensationType.Stop or\
                            sensation.getSensationType() == Sensation.SensationType.Feeling,
                            'parent should get Stop or Feeling sensation type after test and self.visual.stop()')
        
        while self.visual.running:
            systemTime.sleep(1)
         
        del self.visual
        del self.Wall_E_voice_sensation
        del self.Wall_E_image_sensation_2
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
        del self.axon
        
    def test_Visual(self):
        self.assertEqual(self.visual.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Visual\nCannot test properly this!')
        self.visual.start()
        
        sleeptime = Visual.SLEEPTIME+Visual.SLEEPTIMERANDOM
        print("--- test sleeping " + str(sleeptime) + " second until starting to test")
        systemTime.sleep(sleeptime ) # let Visual start before waiting it to stops
        for i in range(VisualTestCase.TEST_RUNS):
            self.getSensations()
            
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_CommunicationNotStarted_sensation)
            
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_item_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_CommunicationOn_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_CommunicationWaiting_sensation)

            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_voice_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation_2)
 
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_item_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_image_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_voice_sensation)
 
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_positive_feeling_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_CommunicationEnded_sensation)
                       
            sleeptime = 3
            print("--- test sleeping " + str(sleeptime) + " second until test results")
            systemTime.sleep(sleeptime ) # let Visual start before waiting it to stops
            # OOps assertEqual removed, study
            self.assertEqual(self.visual.getAxon().empty(), True, 'Axon should be empty again at the end of test_Visual!')
            #self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_voice_sensation)

# TODO Reenable stop       
#         print("--- put stop-sensation for Visual")
#         self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        
        print("--- test sleeping " + str(VisualTestCase.TEST_TIME) + " second until stop should be done")
        systemTime.sleep(VisualTestCase.TEST_TIME) # let result UI be shown until cleared           
        print("--- Visual should disappear when you press Stop now")
        
    '''
    functionality from Robot
    '''
    def studyOwnIdentity(self, robot):
        print("My name is " + robot.getName())
        # What kind we are
        print("My kind is " + str(robot.getKind()))      
        robot.selfSensation=robot.createSensation(sensationType=Sensation.SensationType.Item,
                                                memoryType=Sensation.MemoryType.LongTerm,
                                                robotType=Sensation.RobotType.Sense,# We have found this
                                                robot = robot.getName(),
                                                name = robot.getName(),
                                                presence = Sensation.Presence.Present,
                                                kind=robot.getKind(),
                                                locations=self.LOCATIONS_1_2)
        robot.imageSensations, robot.voiceSensations = robot.getIdentitySensations(name=robot.getName())
        if len(robot.imageSensations) > 0:
            robot.selfImage = robot.imageSensations[0].getImage()
        else:
            robot.selfImage = None
 
        
if __name__ == '__main__':
    unittest.main()

 