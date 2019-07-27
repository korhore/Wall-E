'''
Created on 23.06.2019
Updated on 28.07.2019
@author: reijo.korhonen@gmail.com

test TensorFlowClassification class
python3 -m unittest tests/testTensorFlowClassification.py


'''
import time as systemTime
import os
import io
import shutil
import ntpath


import unittest
from Sensation import Sensation
from TensorFlowClassification.TensorFlowClassification import TensorFlowClassification
from Axon import Axon

from PIL import Image as PIL_Image


class TensorFlowClassificationTestCase(unittest.TestCase):
    
    TEST_MODEL_DOWNLOAD_TIME = 240.0    # can take a long, long time
    TEST_CLASSIFICATION_TIME = 7.0     # can take a long time
    TEST_STOP_TIME = 5.0                # how long to wait Robot read stop from its Axon
    TESTSETUPMODEL=False                # Set this True only if problems to load model
                                        # models are big and this takes a log, log time and can fail
                                        # if we don't wait enough, even if it runs OK
    TEST_ITEM_NAMES_1=['dog']
    TEST_ITEM_NAMES_2=['person',
                       'kite']
    
    
    def getAxon(self):
        return self.axon

    def setUp(self):
        self.axon = Axon()

        self.tensorFlowClassification = TensorFlowClassification(parent=self,
                                       instanceName='TensorFlowClassification',
                                       instanceType= Sensation.InstanceType.SubInstance,
                                       level=2)

        # run doTestSetupMobel in setup so its is run first and we test model
        # creation and Robot is running now 
        if TensorFlowClassificationTestCase.TESTSETUPMODEL:
            self.doTestSetupMobel()
        else:
            self.tensorFlowClassification.start()


    def tearDown(self):
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop))
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_STOP_TIME) + ' to Stop Robot')
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
        self.doTestClassification(imageSensation=sensations[0], names=names[0])   
        self.doTestClassification(imageSensation=sensations[1], names=names[1], absent_names=names[0])   
        self.doTestClassification(imageSensation=sensations[0], names=names[0], absent_names=names[1])   
          
    def doTestClassification(self, imageSensation, names, absent_names=None):
        #entering
        #exiting TODO
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation)
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to to classify')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
        
        self.assertFalse(self.getAxon().empty(), 'self.getAxon().empty() should not be empty')
        itemnames = []
        found_names = []
        found_absent_names = []
        while not self.getAxon().empty():
            transferDirection, sensation = self.getAxon().get()
            print("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            if sensation.getDirection() == Sensation.Direction.Out and \
                sensation.getSensationType() == Sensation.SensationType.Image:
                print("got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
            elif sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Entering:
                print("got item Entering " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getName() not in itemnames:
                    itemnames.append(sensation.getName())
                self.assertTrue(sensation.getName() in names, 'should be in test names')
                found_names.append(sensation.getName())
            elif absent_names is not None and sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Exiting:
                print("got item Absent " + str(transferDirection) + ' ' + sensation.toDebugStr())
                self.assertTrue(sensation.getName() in absent_names, 'should be in test exiting_names')
                found_absent_names.append(sensation.getName())
            else:
               print("got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        self.assertEqual(sorted(names), sorted(found_names), 'should get exactly entering items')
        if absent_names is not None:
            self.assertEqual(sorted(absent_names), sorted(found_absent_names), 'should get exactly exiting items')

        #present
        #absent
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation)
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to to classify')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
        
        self.assertFalse(self.getAxon().empty(), 'self.getAxon().empty() should not be empty')
        itemnames = []
        found_names = []
        found_absent_names = []
        while not self.getAxon().empty():
            transferDirection, sensation = self.getAxon().get()
            print("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            if sensation.getDirection() == Sensation.Direction.Out and \
                sensation.getSensationType() == Sensation.SensationType.Image:
                print("got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
            elif sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Present:
                print("got item Present " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getName() not in itemnames:
                    itemnames.append(sensation.getName())
                self.assertTrue(sensation.getName() in names, 'should be in test names')
                found_names.append(sensation.getName())
            elif absent_names is not None and sensation.getSensationType() == Sensation.SensationType.Item and\
                sensation.getPresence() == Sensation.Presence.Absent:
                print("got item Absent " + str(transferDirection) + ' ' + sensation.toDebugStr())
                self.assertTrue(sensation.getName() in absent_names, 'should be in test absent_names')
                found_absent_names.append(sensation.getName())
            else:
               print("got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        self.assertEqual(sorted(names), sorted(found_names), 'should get exactly present items')
        if absent_names is not None:
            self.assertEqual(sorted(absent_names), sorted(found_absent_names), 'should get exactly absent items')
        
        #no change, because present ones still present and absent ones are gone
        self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=imageSensation)
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to to classify')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
        
        self.assertTrue(self.getAxon().empty(), 'self.getAxon().empty() should  be empty')

if __name__ == '__main__':
    unittest.main()

 