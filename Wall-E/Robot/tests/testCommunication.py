'''
Created on 21.06.2019
Updated on 21.06.2019
@author: reijo.korhonen@gmail.com

test Association class
python3 -m unittest tests/testCommunication.py


'''
import time as systemTime

import unittest
from Sensation import Sensation
from Communication.Communication import Communication
from Association.Association import Association
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
        self.history_sensationTime = systemTime.time() -10*Association.ASSOCIATION_INTERVAL

        # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memory
        self.Wall_E_item_sensation = Sensation.create(time=self.history_sensationTime,
                                                      memory=Sensation.Memory.LongTerm,
                                                      sensationType=Sensation.SensationType.Item,
                                                      direction=Sensation.Direction.Out,
                                                      name=CommunicationTestCase.NAME,
                                                      associations=[])
        # Image is in LongTerm memory, it comes from TensorflowCallification and is crop of original big image
        self.Wall_E_image_sensation = Sensation.create(time=self.history_sensationTime,
#                                                      memory=Sensation.Memory.LongTerm,
                                                       memory=Sensation.Memory.Sensory,
                                                       sensationType=Sensation.SensationType.Image,
                                                       direction=Sensation.Direction.Out,
                                                       associations=[Sensation.Association(sensation=self.Wall_E_item_sensation,
                                                                                           score=CommunicationTestCase.SCORE)])
        self.Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=self.Wall_E_image_sensation,
                                                                        score=CommunicationTestCase.SCORE))
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
       
         
        self.communication = Communication(parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        


    def tearDown(self):
        
        del self.communication
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
       
#     def test_SensationCreate(self):
#         self.assertIsNot(self.Wall_E_item_sensation, None)
#         self.assertIsNot(self.Wall_E_image_sensation, None)

    '''
    1) item.name
    2) process(item) should get old self.Wall_E_voice_sensation,that will be
       spoken out
    3) parent Axon should get self.Wall_E_voice_sensation
    '''

    def test_ProcessItemSensoryVoice(self):
        self.do_test_ProcessItemSensoryVoice(memory=Sensation.Memory.Sensory)
        self.do_test_ProcessItemSensoryVoice(memory=Sensation.Memory.LongTerm)

       
    def do_test_ProcessItemSensoryVoice(self, memory):
 # Make Voice to the history by parameter Memory type       
        # simulate Association has connected an voice to Item and Image 
        # Voice is in Sensory Memory, it is not used in Communication yet or
        # it can be in n LongTerm memory, classified ti be a good Voice
        # Make two test of these 
        Wall_E_voice_sensation = Sensation.create(time=self.history_sensationTime,
#                                                       memory=Sensation.Memory.LongTerm,
                                                       memory=memory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       direction=Sensation.Direction.Out, 
                                                       associations=[Sensation.Association(sensation=self.Wall_E_image_sensation,
                                                                                           score=CommunicationTestCase.SCORE),
                                                                     Sensation.Association(sensation=self.Wall_E_item_sensation,
                                                                                           score=CommunicationTestCase.SCORE)])
         # test that all is OK for tests
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        self.Wall_E_image_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation,
                                                                         score=CommunicationTestCase.SCORE))
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        self.Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation,
                                                                        score=CommunicationTestCase.SCORE))
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
       

        ## test part
                
        #image and Item
        # simulate item and image are connected each other with TensorflowClassifivation
        Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.LongTerm,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 associations=[])
        Wall_E_image_sensation = Sensation.create(memory=Sensation.Memory.LongTerm,
                                                  sensationType=Sensation.SensationType.Image,
                                                  direction=Sensation.Direction.Out, 
                                                  associations=[Sensation.Association(sensation=Wall_E_item_sensation,
                                                                                      score=CommunicationTestCase.SCORE)])
        Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=Wall_E_image_sensation,
                                                                   score=CommunicationTestCase.SCORE))
        # these connected each other
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        # TODO this verifies test, but not implementation
        '''
        Commented out, so we can  correct implementation
        # simulate Association has connected an voice to Item and Image 
        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice, 
                                                       associations=[Sensation.Association(sensation=Wall_E_image_sensation,
                                                                                         score=CommunicationTestCase.SCORE),
                                                                    Sensation.Association(sensation=Wall_E_item_sensation,
                                                                                         score=CommunicationTestCase.SCORE)])
         # test that all is OK for tests
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        Wall_E_image_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation,
                                                                       score=CommunicationTestCase.SCORE))
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation,
                                                                      score=CommunicationTestCase.SCORE))
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 2)

        
        #######################
        '''

        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # We have Voice to be spoken out
        # minimum is that we get something
        self.assertNotEqual(self.getAxon().empty(), True, 'Axon should not be empty')
        
        tranferDirection, sensation = self.getAxon().get()
        #Voice
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
        # to be spoken
        self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
        Wall_E_voice_sensation.delete()
        
if __name__ == '__main__':
    unittest.main()

 