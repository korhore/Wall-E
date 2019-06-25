'''
Created on 21.06.2019
Updated on 21.06.2019
@author: reijo.korhonen@gmail.com

test Connection class
python3 -m unittest tests/testConnection.py


'''
import time as systemTime

import unittest
from Sensation import Sensation
from Communication.Communication import Communication
from Connection.Connection import Connection
from Axon import Axon

from PIL import Image as PIL_Image

class CommunicationTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    SCORE=0.8
    NAME='Wall-E'
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon

    '''
    Testing    
    '''
    
    def setUp(self):
        self.axon = Axon()

        # define time in history, that is different than in all tests
        sensationTime = systemTime.time() -10*Connection.CONNECTION_INTERVAL

        # simulate item and image are connected each other with TensorflowClassifivation
        self.Wall_E_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name=CommunicationTestCase.NAME, connections=[])
        self.Wall_E_image_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Image, connections=[Sensation.Connection(sensation=self.Wall_E_item_sensation,
                                                                                         score=CommunicationTestCase.SCORE)])
        self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=self.Wall_E_image_sensation,
                                                                      score=CommunicationTestCase.SCORE))
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getConnections()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getConnections()), 1)
       
        # simulate Connection has connected an voice to Item and Image 
        self.Wall_E_voice_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Voice, 
                                                       connections=[Sensation.Connection(sensation=self.Wall_E_image_sensation,
                                                                                         score=CommunicationTestCase.SCORE),
                                                                    Sensation.Connection(sensation=self.Wall_E_item_sensation,
                                                                                         score=CommunicationTestCase.SCORE)])
         # test that all is OK for tests
        self.assertEqual(len(self.Wall_E_voice_sensation.getConnections()), 2)
        # add missing connections test that all is OK for tests
        self.Wall_E_image_sensation.addConnection(Sensation.Connection(sensation=self.Wall_E_voice_sensation,
                                                                       score=CommunicationTestCase.SCORE))
        self.assertEqual(len(self.Wall_E_image_sensation.getConnections()), 2)
        # add missing connections test that all is OK for tests
        self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=self.Wall_E_voice_sensation,
                                                                      score=CommunicationTestCase.SCORE))
        self.assertEqual(len(self.Wall_E_item_sensation.getConnections()), 2)
        
        self.communication = Communication(parent=self,
                                     instanceName='Communication',
                                     instanceType= Sensation.InstanceType.SubInstance,
                                     level=2)
        


    def tearDown(self):
        
        del self.communication
        del self.Wall_E_voice_sensation
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
       
#     def test_SensationCreate(self):
#         self.assertIsNot(self.Wall_E_item_sensation, None)
#         self.assertIsNot(self.Wall_E_image_sensation, None)

    '''
    1) item,name
    2) process(item) should get old self.Wall_E_voice_sensation,that will be
       spoken out
    3) parent Axon should get self.Wall_E_voice_sensation
    '''
       
    def test_ProcessItem(self):
        #image and Item
        # simulate item and image are connected each other with TensorflowClassifivation
        Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.LongTerm,
                                                 sensationType=Sensation.SensationType.Item,
                                                 name=CommunicationTestCase.NAME,
                                                 connections=[])
        Wall_E_image_sensation = Sensation.create(memory=Sensation.Memory.LongTerm,
                                                  sensationType=Sensation.SensationType.Image,
                                                  connections=[Sensation.Connection(sensation=Wall_E_item_sensation,
                                                                                    score=CommunicationTestCase.SCORE)])
        Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=Wall_E_image_sensation,
                                                                score=CommunicationTestCase.SCORE))
        # these connected each other
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 1)
        # TODO this verifies test, but not implementation
        '''
        Commented out, so we can  correct implementation
        # simulate Connection has connected an voice to Item and Image 
        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice, 
                                                       connections=[Sensation.Connection(sensation=Wall_E_image_sensation,
                                                                                         score=CommunicationTestCase.SCORE),
                                                                    Sensation.Connection(sensation=Wall_E_item_sensation,
                                                                                         score=CommunicationTestCase.SCORE)])
         # test that all is OK for tests
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 2)
        # add missing connections test that all is OK for tests
        Wall_E_image_sensation.addConnection(Sensation.Connection(sensation=Wall_E_voice_sensation,
                                                                       score=CommunicationTestCase.SCORE))
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 2)
        # add missing connections test that all is OK for tests
        Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=Wall_E_voice_sensation,
                                                                      score=CommunicationTestCase.SCORE))
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 2)

        
        #######################
        '''

        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # We have Voice to be spoken out
        # minimum is that we get something
        self.assertNotEqual(self.getAxon().empty(), True, 'Axon should not be empty')
        tranferDirection, sensation=self.getAxon().get()
        #Voice
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
        # to be spoken
        self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
if __name__ == '__main__':
    unittest.main()

 