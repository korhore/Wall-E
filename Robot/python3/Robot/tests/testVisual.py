'''
Created on 12.03.2020
Updated on 26.04.2020
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
    TEST_TIME=60 # 30s when normal test

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
    '''
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getName(self):
        return VisualTestCase.NAME
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
        self.axon = Axon(robot=self) # parent axon
        self.visual = Visual(parent=self,
                            instanceName='Visual',
                            instanceType= Sensation.InstanceType.SubInstance,
                            level=2)

        # define time in history, that is different than in all tests
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*max(VisualTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.stopSensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Working,
                                            sensationType=Sensation.SensationType.Stop,
                                            robotType=Sensation.RobotType.Sense)

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.visual.createSensation(time=self.history_sensationTime,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VisualTestCase.NAME,
                                                      score=VisualTestCase.SCORE_1,
                                                      presence = Sensation.Presence.Present)
        # Image is in LongTerm memoryType, it comes from TensorflowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = self.visual.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense)
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
                                                       data="1")
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation,)
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
       
    def getSenasations(self):

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VisualTestCase.NAME,
                                                      score=VisualTestCase.SCORE_1,
                                                      presence = Sensation.Presence.Present)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
        image = self.visual.selfImage
        self.assertNotEqual(image, None, "image should not be None in this test")

        self.Wall_E_image_sensation = self.visual.createSensation( memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       image=image)
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
                                                       image=image)
        
        
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation_2)

        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 3)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation_2.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data="1")
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 4)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)

        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 4)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())
        
        # communication
        self.communication_item_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Muscle,
                                                      name=VisualTestCase.NAME,
                                                      presence = Sensation.Presence.Present)

        image = self.visual.selfImage
        self.assertNotEqual(image, None, "image should not be None in this test")
        self.communication_image_sensation = self.visual.createSensation( memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       image=image)
        
        self.communication_voice_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       data="1")
        
        self.communication_positive_feeling_sensation = self.visual.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Feeling,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       firstAssociateSensation=self.communication_item_sensation,
                                                       otherAssociateSensation=self.communication_voice_sensation,
                                                       positiveFeeling=True)
        


    def tearDown(self):
        #self.visual.stop()
        #self.assertEqual(self.visual.getAxon().empty(), False, 'Axon should not be empty after self.visual.stop()')
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get()
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
            self.getSenasations()
            
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_item_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_voice_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation_2)
 
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_item_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_image_sensation)
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_voice_sensation)
 
            self.visual.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_positive_feeling_sensation)
                       
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
        print("--- Visual should be disappear when you press Stop now")
        
    '''
    functionality from Robot
    '''
    def studyOwnIdentity(self, robot):
#         kind = robot.config.getKind()
#         identitypath = robot.config.getIdentityDirPath(robot.getKind())
#         for dirName, subdirList, fileList in os.walk(identitypath):
#             image_file_names=[]
#             for fname in fileList:
#                 print('studyOwnIdentity \t%s' % fname)
#                 if fname.endswith(".jpg"):
#                     image_file_names.append(fname)
# # png is not working YET                    
# #                 if fname.endswith(".png"):
# #                     image_file_names.append(fname)
#             # images
#             for fname in image_file_names:
#                 image_path=os.path.join(dirName,fname)
#                 sensation_filepath = os.path.join('/tmp/',fname)
#                 shutil.copyfile(image_path, sensation_filepath)
#                 image = PIL_Image.open(sensation_filepath)
#                 image.load()
#                 robot.images.append(image)

        print("My name is " + robot.getName())
        # What kind we are
        print("My kind is " + str(robot.getKind()))      
        robot.selfSensation=robot.createSensation(sensationType=Sensation.SensationType.Item,
                                                memoryType=Sensation.MemoryType.LongTerm,
                                                robotType=Sensation.RobotType.Sense,# We have found this
                                                robot = robot.getName(),
                                                name = robot.getName(),
                                                presence = Sensation.Presence.Present,
                                                kind=robot.getKind())
        #if robot.isMainRobot() or robot.getInstanceType() == Sensation.InstanceType.Virtual:
        if True:
            robot.imageSensations, robot.voiceSensations = robot.getIdentitySensations(who=robot.getName())
            if len(robot.imageSensations) > 0:
                robot.selfImage = robot.imageSensations[0].getImage()
            else:
                robot.selfImage = None
 
        
if __name__ == '__main__':
    unittest.main()

 