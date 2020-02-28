'''
Created on 23.06.2019
Updated on 28.07.2019
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
    
    TEST_MODEL_DOWNLOAD_TIME = 240.0    # can take a long, long time
    if TensorFlow_LITE:
        TEST_CLASSIFICATION_TIME = 35.0      # can take a long time
    else:
        TEST_CLASSIFICATION_TIME = 40.0      # can take a long time
                                        # 7.0 was minimum for PC, but 35 is mininun fot raspspberry 3 Lite Tensory model
                                        # try 40 for Raspberry 3 normal model, when first wait i 2* longer then nest ones
                                        # tested in raspberry running also Robot service, to we have some tolerance
                                        # raspberry would need more time
    TEST_TIME = 60.0                    # how long we wait tearDown until delete test variables
    TEST_STOP_TIME = 5.0                # how long to wait Robot read stop from its Axon
    TESTSETUPMODEL=False                # Set this True only if problems to load model
                                        # models are big and this takes a log, log time and can fail
                                        # if we don't wait enough, even if it runs OK
    if TensorFlow_LITE:
        TEST_ITEM_NAMES_1=['Saint Bernard',
                           'basset',
                           'beagle']
        TEST_ITEM_NAMES_2=['parachute',
                           'nematode',
                           'balloon',
                           'sandbar',
                           'speedboat',
                           'bathing cap']
    else:
        TEST_ITEM_NAMES_1=['dog']
        TEST_ITEM_NAMES_2=['person',
                           'kite']
    
    
    def getAxon(self):
        return self.axon

    def setUp(self):
        self.isFirstSleep=True
        self.axon = Axon()

        self.tensorFlowClassification = TensorFlowClassification(parent=self,
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
#         print('sleep ' + str(TensorFlowClassificationTestCase.TEST_TIME) + ' to Stop Robot and test finishes')
#         systemTime.sleep(TensorFlowClassificationTestCase.TEST_TIME)       # give Robot some time to stop
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop), association=None)
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

            sensations.append(Sensation.create(associations=[], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, image=image, filePath=testImageFileName))

        # test Entering, Present and Absent so, then in next picture absent Item,names are from previous picture
        # removed as a test     
        self.doTestClassification(imageSensation=sensations[0], names=names[0])   
        self.doTestClassification(imageSensation=sensations[1], names=names[1], absent_names=names[0])   
        self.doTestClassification(imageSensation=sensations[0], names=names[0], absent_names=names[1])   
          
    def doTestClassification(self, imageSensation, names, absent_names=None):
        print('doTestClassification start')
        #entering ne ones
        #exiting old ones
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
        #self.tensorFlowClassification.process(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
        if self.isFirstSleep:
            print('sleep ' + str(2*TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to classify')
            systemTime.sleep(2*TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
            self.isFirstSleep=False
        else:
            print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to classify')
            systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
        print('1: test continues classify should be done')
        
        self.assertFalse(self.getAxon().empty(), 'self.getAxon().empty() should not be empty')
        itemnames = []
        found_names = []
        found_absent_names = []
        while not self.getAxon().empty():
            transferDirection, sensation, association = self.getAxon().get()
            print("1: got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            if sensation.getDirection() == Sensation.Direction.Out and \
                sensation.getSensationType() == Sensation.SensationType.Image:
                print("1: got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
            elif sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Entering:
                print("1: got item Entering " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getName() not in itemnames:
                    itemnames.append(sensation.getName())
                self.assertTrue(sensation.getName() in names, sensation.getName()+' should be in test names')
                found_names.append(sensation.getName())
            elif absent_names is not None and sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Exiting:
                print("1: got item Exiting " + str(transferDirection) + ' ' + sensation.toDebugStr())
                self.assertTrue(sensation.getName() in absent_names, 'should be in test exiting_names')
                found_absent_names.append(sensation.getName())
            else:
               print("1: got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        self.assertEqual(sorted(names), sorted(found_names), 'should get exactly entering items')
        if absent_names is not None:
            self.assertEqual(sorted(absent_names), sorted(found_absent_names), 'should get exactly exiting items')

        #present
        #absent
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
        #self.tensorFlowClassification.process(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to classify')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
        print('2: test continues classify should be done')
        
        self.assertFalse(self.getAxon().empty(), 'self.getAxon().empty() should not be empty')
        itemnames = []
        found_names = []
        found_absent_names = []
        while not self.getAxon().empty():
            transferDirection, sensation, association = self.getAxon().get()
            print("2: got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            if sensation.getDirection() == Sensation.Direction.Out and \
                sensation.getSensationType() == Sensation.SensationType.Image:
                print("2: got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
            elif sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Present:
                print("2: got item Present " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getName() not in itemnames:
                    itemnames.append(sensation.getName())
                self.assertTrue(sensation.getName() in names, 'should be in test names')
                found_names.append(sensation.getName())
            elif absent_names is not None and sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Absent:
                print("2: got item Absent " + str(transferDirection) + ' ' + sensation.toDebugStr())
                self.assertTrue(sensation.getName() in absent_names, 'should be in test absent_names')
                found_absent_names.append(sensation.getName())
            else:
               print("2: got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        self.assertEqual(sorted(names), sorted(found_names), 'should get exactly present items')
        if absent_names is not None:
            self.assertEqual(sorted(absent_names), sorted(found_absent_names), 'should get exactly absent items')
        
        #change, because present ones still present and they are reported by last logic, but absent ones are gone and should not come 
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
        #self.tensorFlowClassification.process(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation, association=None)
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to classify')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to classify
        print('3: test continues classify should be done')
        self.assertFalse(self.getAxon().empty(), 'self.getAxon().empty() should not be empty')
        itemnames = []
        found_names = []
        found_absent_names = []
        while not self.getAxon().empty():
            transferDirection, sensation, association = self.getAxon().get()
            print("3: got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            if sensation.getDirection() == Sensation.Direction.Out and \
                sensation.getSensationType() == Sensation.SensationType.Image:
                print("3: got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
            elif sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Present:
                print("3: got item Present " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getName() not in itemnames:
                    itemnames.append(sensation.getName())
                self.assertTrue(sensation.getName() in names, 'should be in test names')
                found_names.append(sensation.getName())
            elif absent_names is not None and sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Absent:
                print("3: got item Absent but SHOULD NOT " + str(transferDirection) + ' ' + sensation.toDebugStr())
                self.assertTrue(sensation.getName() in absent_names, 'should be in test absent_names')
                found_absent_names.append(sensation.getName())
            else:
               print("3: got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        self.assertEqual(sorted(names), sorted(found_names), 'should get exactly present items')
        if absent_names is not None:
            self.assertEqual(len(found_absent_names), 0, '3: should not get absent items')
        
        self.assertTrue(self.getAxon().empty(), 'self.getAxon().empty() should be empty')
        
        print('doTestClassification end')

if __name__ == '__main__':
    unittest.main()

 