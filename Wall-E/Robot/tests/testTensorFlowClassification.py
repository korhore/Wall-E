'''
Created on 23.06.2019
Updated on 23.07.2019
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
    TEST_CLASSIFICATION_TIME = 15.0     # can take a long time
    TEST_STOP_TIME = 5.0                # how long to wait Robot read stop from its Axon
    TESTSETUPMODEL=False                # Set this True only if problems to load model
                                        # models are big and this takes a log, log time and can fail
                                        # if we don't wait enough, even if it runs OK
    TEST_ITEM_NAMES=['dog',
                     'person',
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
        
        for image_path in TensorFlowClassification.TEST_IMAGE_PATHS:
            testImageFileName = '/tmp/'+ntpath.basename(image_path)
            shutil.copyfile(image_path, testImageFileName)
            image = PIL_Image.open(testImageFileName)
            image.load()
            print('image filename ' + testImageFileName)
            print('image.size) ' + str(image.size))


            sensation = Sensation.create(associations=[], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, image=image, filePath=testImageFileName)
            self.tensorFlowClassification.getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        print('sleep ' + str(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME) + ' to to classify')
        systemTime.sleep(TensorFlowClassificationTestCase.TEST_CLASSIFICATION_TIME)       # give Robot some time to stop
        itemnames = []
        while not self.getAxon().empty():
            transferDirection, sensation = self.getAxon().get()
            print("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            if sensation.getDirection() == Sensation.Direction.Out and \
                sensation.getSensationType() == Sensation.SensationType.Image:
                print("got crop image of item " + str(transferDirection) + ' ' + sensation.toDebugStr())
            elif sensation.getSensationType() == Sensation.SensationType.Item:
                print("got item " + str(transferDirection) + ' ' + sensation.toDebugStr())
                if sensation.getName() not in itemnames:
                    itemnames.append(sensation.getName())
                self.assertTrue(sensation.getName() in TensorFlowClassificationTestCase.TEST_ITEM_NAMES, 'should be in test names')      
            else:
               print("got something else" + str(transferDirection) + ' ' + sensation.toDebugStr())
        
        print ("found " + str(len(itemnames)) + ' ' + str(itemnames))
        print ("should found " + str(len(TensorFlowClassificationTestCase.TEST_ITEM_NAMES)) + ' ' + str(TensorFlowClassificationTestCase.TEST_ITEM_NAMES))
        self.assertTrue(len(TensorFlowClassificationTestCase.TEST_ITEM_NAMES) == len(itemnames), 'exact test names should be found')      
          

if __name__ == '__main__':
    unittest.main()

 