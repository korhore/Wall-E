'''
Created on 23.06.2019
Updated on 31.12.2020
@author: reijo.korhonen@gmail.com

test TensorFlowClassification class
you must provide models/research
PYTHONPATH=/<here it is>/models/research python3 -m unittest tests/testTensorFlowClassification.py

Testing is complicated, because we must test TensorFlowClassification thread
and unittest goes to tearDown while we are in the middle of testing.
so we must set sleep in teadDown


'''
import time as systemTime
import os
import io
import shutil
import ntpath


import unittest
from Sensation import Sensation
from TensorFlowClassification.TensorFlowClassification import TensorFlowClassification, TensorFlow_LITE
from Axon import Axon

from PIL import Image as PIL_Image


class TensorFlowClassificationTestCase(unittest.TestCase):
    
                                # with original 1000xY pictures raspberry pi average 32.8s
    TEST_RESOLUTION_640 = True  # raspberry pi average 25.3s
    TEST_RESOLUTION_320 = False # raspberry pi average 22.4s
    TEST_RESOLUTION_160 = False # raspberry pi average 21.7s
    
    TEST_MODEL_DOWNLOAD_TIME = 240.0    # can take a long, long time
    if TensorFlow_LITE:
        TEST_CLASSIFICATION_TIME = 35.0      # can take a long time
    else:
        TEST_CLASSIFICATION_TIME = 40.0      # can take a long time
                                        # 7.0 was minimum for PC, but 35 is mininun fot raspspberry 3 Lite Tensory model
                                        # try 40 for Raspberry 3 normal model, when first wait i 2* longer then nest ones
                                        # tested in raspberry running also Robot service, to we have some tolerance
                                        # raspberry would need more time
    TEST_STOP_TIME = 5.0                # how long to wait Robot read stop from its Axon
    TESTSETUPMODEL=False                # Set this True only if problems to load model
                                        # models are big and this takes a log, log time and can fail
                                        # if we don't wait enough, even if it runs OK
    if TensorFlow_LITE:
        TEST_ITEM_NAMES_1=['dog',
                           'person',
                           'chair']
        TEST_ITEM_NAMES_2=['person',
                           'kite']
    else:
        TEST_ITEM_NAMES_1=['dog']
        TEST_ITEM_NAMES_2=['person',
                           'kite']
    
    MAINNAMES = ["TensorFlowClassificationTestCaseMainName"]
    OTHERMAINNAMES = ["OTHER_TensorFlowClassificationTestCaseMainName"]
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def setMainNames(self, mainNames):
        self.mainNames = mainNames
    def getMainNames(self):
        return self.mainNames
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
    def getName(self):
        return "TensorFlowClassificationTestCase"
    def getParent(self):
        return None
    def log(self, logStr, logLevel=None):
        #print('CommunicationTestCase log')
        if hasattr(self, 'tensorFlowClassification'):
            if self.tensorFlowClassification:
                if logLevel == None:
                    logLevel = self.tensorFlowClassification.LogLevel.Normal
                if logLevel <= self.tensorFlowClassification.getLogLevel():
                     print(self.tensorFlowClassification.getName() + ":" + str( self.tensorFlowClassification.config.level) + ":" + Sensation.Modes[self.tensorFlowClassification.mode] + ": " + logStr)
    
    '''
    Testing    
    '''
    
    def setUp(self):
        self.mainNames = self.MAINNAMES
        self.isFirstSleep=True
        self.processTimeSum = 0.0
        self.processNumber = 0

        self.axon = Axon(robot=self)

        self.tensorFlowClassification = TensorFlowClassification(
                                       mainRobot=self,
                                       parent=self,
                                       instanceName='TensorFlowClassification',
                                       instanceType= Sensation.InstanceType.SubInstance,
                                       level=2)

        # run doTestSetupMobel in setup so its is run first and we test model
        # creation and Robot is running now 
        if TensorFlowClassificationTestCase.TESTSETUPMODEL:
            self.doTestSetupMobel()
# unit tests testing threads so we go to tearDown too early
        else:
            self.tensorFlowClassification.start()


    def tearDown(self):
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_STOP_TIME) + ' to Stop Robot and test finishes')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_STOP_TIME)       # give Robot some time to stop
        self.tensorFlowClassification.getAxon().put(robot=self,
                                                    transferDirection=Sensation.TransferDirection.Up,
                                                    sensation=self.tensorFlowClassification.createSensation(associations=[], sensationType = Sensation.SensationType.Stop))
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_STOP_TIME) + ' time for Robot to process Stop Sensation')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_STOP_TIME)       # give Robot some time to stop

        del self.tensorFlowClassification
        del self.axon
        
    '''
    Download model, if it is not downloaded yet
    '''
       
    def doTestSetupMobel(self):
        print('modelFilename ' + TensorFlowClassification.PATH_TO_FROZEN_GRAPH)
        if os.path.exists(TensorFlowClassification.PATH_TO_FROZEN_GRAPH):
            print('modelFilename exists ' + TensorFlowClassification.PATH_TO_FROZEN_GRAPH)
            PATH_TO_FROZEN_GRAPHbak = TensorFlowClassification.PATH_TO_FROZEN_GRAPH + '.bak'
            print('modelFilename rename to ' + PATH_TO_FROZEN_GRAPHbak)
            os.rename(TensorFlowClassification.PATH_TO_FROZEN_GRAPH, PATH_TO_FROZEN_GRAPHbak)
            self.assertFalse(os.path.exists(TensorFlowClassification.PATH_TO_FROZEN_GRAPH), 'modelFilename should not exist TEST implement error')      
        self.tensorFlowClassification.start()
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_MODEL_DOWNLOAD_TIME) + ' to download model')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_MODEL_DOWNLOAD_TIME) # give some time to download model
        self.assertTrue(os.path.exists(TensorFlowClassification.PATH_TO_FROZEN_GRAPH), TensorFlowClassification.PATH_TO_FROZEN_GRAPH + ' should exists')      
            
    def test_Classification(self):
        # Create Image sensation with a test image same way as
        # RaspberryPiCamera does it
        sensations=[]
        testImageFileNames=[]
        names=[TensorFlowClassificationTestCase.TEST_ITEM_NAMES_1, TensorFlowClassificationTestCase.TEST_ITEM_NAMES_2]
        
        for image_path in TensorFlowClassification.TEST_IMAGE_PATHS:
            testImageFileName = '/tmp/'+ntpath.basename(image_path)
            testImageFileNames.append(testImageFileName)
            shutil.copyfile(image_path, testImageFileName)
            image = PIL_Image.open(testImageFileName)
            image.load()
            print('image filename ' + testImageFileName)
            print('image.size) ' + str(image.size))
            if TensorFlowClassificationTestCase.TEST_RESOLUTION_640:
                if image.size[0]> image.size[1]:
                    image = image.resize((640, int(image.size[1]*640/image.size[0])))
                else:
                    image = image.resize((int(image.size[0]*640/image.size[1]), 640))
                print('resized image.size) ' + str(image.size))
            elif TensorFlowClassificationTestCase.TEST_RESOLUTION_320:
                if image.size[0]> image.size[1]:
                    image = image.resize((320, int(image.size[1]*320/image.size[0])))
                else:
                    image = image.resize((int(image.size[0]*320/image.size[1]), 320))
                print('resized image.size) ' + str(image.size))
            elif TensorFlowClassificationTestCase.TEST_RESOLUTION_160:
                if image.size[0]> image.size[1]:
                    image = image.resize((160, int(image.size[1]*160/image.size[0])))
                else:
                    image = image.resize((int(image.size[0]*160/image.size[1]), 160))
                print('resized image.size) ' + str(image.size))

            sensations.append(self.tensorFlowClassification.createSensation(associations=[], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, image=image, filePath=testImageFileName))

        # test Entering, Present and Absent so, then in next picture absent Item,names are from previous picture
        # removed as a test     
        self.doTestClassification(imageSensation=sensations[0], currentNames=names[0])   
        self.doTestClassification(imageSensation=sensations[1], currentNames=names[1], previousNames=names[0])   
        self.doTestClassification(imageSensation=sensations[0], currentNames=names[0], previousNames=names[1])   
          
    def doTestClassification(self, imageSensation, currentNames, previousNames=None):
        print('doTestClassification start')
        #entering new ones
        #exiting old ones
        enteringNames=currentNames
        presentNames=[]
        exitingNames = []
        absentNames = []
        if previousNames is not None:
            enteringNames = self.getDifferItems(firstPresent=currentNames, secondPresent=previousNames)
            exitingNames = self.getDifferItems(firstPresent=previousNames, secondPresent=currentNames)
            presentNames = self.getSameItems(firstPresent=previousNames, secondPresent=currentNames)
            
        self.doTestItemSensations(imageSensation=imageSensation,
                                  enteringNames=enteringNames,
                                  presentNames=presentNames,
                                  exitingNames=exitingNames,
                                  absentNames=absentNames)

        #present
        #absent
        enteringNames=[]
        presentNames=currentNames
        exitingNames = []
        absentNames = []
        if previousNames is not None:
            absentNames = self.getDifferItems(firstPresent=previousNames, secondPresent=currentNames)
         
        self.doTestItemSensations(imageSensation=imageSensation,
                                  enteringNames=enteringNames,
                                  presentNames=presentNames,
                                  exitingNames=exitingNames,
                                  absentNames=absentNames)
       
        #still present
        # no absent
        enteringNames=[]
        presentNames=currentNames
        exitingNames = []
        absentNames = []
         
        self.doTestItemSensations(imageSensation=imageSensation,
                                  enteringNames=enteringNames,
                                  presentNames=presentNames,
                                  exitingNames=exitingNames,
                                  absentNames=absentNames)
         
        # test removed temporarely
        #self.assertTrue(self.getAxon().empty(), 'self.getAxon().empty() should be empty')
        while not self.getAxon().empty():
                transferDirection, sensation = self.getAxon().get()
                print("external: got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getRobotType() == Sensation.RobotType.Sense and \
                    sensation.getSensationType() == Sensation.SensationType.Image:
                    print("external: got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Present:
                    print("external: got item Present " + str(transferDirection) + ' ' + sensation.toDebugStr())
                    if sensation.getName() not in itemnames:
                        itemnames.append(sensation.getName())
                    self.assertTrue(sensation.getName() in currentNames, 'should be in test names')
                    found_names.append(sensation.getName())
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Absent:
                    print("external: got item Absent but SHOULD NOT " + str(transferDirection) + ' ' + sensation.toDebugStr())
                    found_absent_names.append(sensation.getName())
                else:
                   print("external: got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        
        print('doTestClassification end')


    '''
    test that we get item sensations expected
    '''
    def doTestItemSensations(self, imageSensation, enteringNames, presentNames, exitingNames, absentNames):
        print('doTestItemSensations start')
        
        testStartTime = systemTime.time()
        self.tensorFlowClassification.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation)
        
        if self.isFirstSleep:
            waitTime =  2*TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME       # give Robot some time to stop
            self.isFirstSleep=False
        else:
            waitTime =  TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME       # give Robot some time to stop
        print('1: test gets process created exiting/absent itemsensation')
        
#         self.assertFalse(self.getAxon().empty(), 'self.getAxon().empty() should not be empty')
        foundEnteringNames = []
        foundPresentNames = []
        foundExitingNames = []
        foundAbsentNames = []
        while ((sorted(enteringNames) != sorted(foundEnteringNames)) or \
               (sorted(presentNames) != sorted(foundPresentNames)) or \
               (sorted(exitingNames) != sorted(foundExitingNames)) or \
               (sorted(absentNames) != sorted(foundAbsentNames))) \
               and \
              (systemTime.time() - testStartTime < waitTime):
            if not self.getAxon().empty():
                transferDirection, sensation = self.getAxon().get()
                print("1: got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getRobotType() == Sensation.RobotType.Sense and \
                    sensation.getSensationType() == Sensation.SensationType.Image:
                    print("1: got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Entering:
                    print("1: got item Entering " + str(transferDirection) + ' ' + sensation.toDebugStr())
                    self.assertTrue(sensation.getName() in enteringNames, sensation.getName()+' should be in test entering names')
                    foundEnteringNames.append(sensation.getName())
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Present:
                    print("2: got item Present " + str(transferDirection) + ' ' + sensation.toDebugStr())
                    self.assertTrue(sensation.getName() in presentNames, sensation.getName()+ ' should be in test still present names')
                    foundPresentNames.append(sensation.getName())
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Exiting:
                    print("1: got item Exiting " + str(transferDirection) + ' ' + sensation.toDebugStr())
                    self.assertTrue(sensation.getName() in exitingNames, 'should be in test exiting_names')
                    foundExitingNames.append(sensation.getName())
                elif sensation.getSensationType() == Sensation.SensationType.Item and\
                    sensation.getPresence() == Sensation.Presence.Absent:
                    print("1: got item Absent " + str(transferDirection) + ' ' + sensation.toDebugStr())
                    self.assertTrue(sensation.getName() in absentNames, 'should be in test absent_names')
                    foundAbsentNames.append(sensation.getName())
                else:
                   print("1: got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
            else:
                systemTime.sleep(1)
        processTime = systemTime.time() - testStartTime
        self.processTimeSum += processTime
        self.processNumber += 1
        print('1: TensorFlowClassification processed image {} seconds average {} seconds\n'.\
              format(processTime, self.processTimeSum/self.processNumber))
                
        self.assertEqual(sorted(foundEnteringNames), sorted(enteringNames), 'should get exactly entering items')
        self.assertEqual(sorted(foundPresentNames), sorted(presentNames), 'should get exactly present items')
        self.assertEqual(sorted(foundExitingNames), sorted(exitingNames), 'should get exactly exiting items')
        self.assertEqual(sorted(foundAbsentNames), sorted(absentNames), 'should get exactly entering items')

        
    '''
    which items will be absent when present one changes
    '''    
    def getDifferItems(self, firstPresent, secondPresent):
        differ=[]
        for name in firstPresent:
            if name not in secondPresent:
                differ.append(name)
        return differ
    
    def getSameItems(self, firstPresent, secondPresent):
        same=[]
        for name in firstPresent:
            if name in secondPresent:
                same.append(name)
        return same

if __name__ == '__main__':
    unittest.main()

 
