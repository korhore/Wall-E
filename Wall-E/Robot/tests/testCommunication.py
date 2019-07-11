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
    
    SCORE_1 = 0.1
    SCORE_2 = 0.2
    SCORE_3 = 0.3
    SCORE_4 = 0.4
    SCORE_5 = 0.5
    SCORE_6 = 0.6
    SCORE_7 = 0.7
    SCORE_8 = 0.8
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
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*Association.ASSOCIATION_INTERVAL

        # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memory
        self.Wall_E_item_sensation = Sensation.create(time=self.history_sensationTime,
                                                      memory=Sensation.Memory.LongTerm,
                                                      sensationType=Sensation.SensationType.Item,
                                                      direction=Sensation.Direction.Out,
                                                      name=CommunicationTestCase.NAME)
        # Image is in LongTerm memory, it comes from TensorflowClassification and is crop of original big image
        self.Wall_E_image_sensation = Sensation.create(time=self.history_sensationTime,
                                                       memory=Sensation.Memory.LongTerm,
                                                       #memory=Sensation.Memory.Sensory,
                                                       sensationType=Sensation.SensationType.Image,
                                                       direction=Sensation.Direction.Out)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation,
                                             score=CommunicationTestCase.SCORE_1)
        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
       
         
        self.communication = Communication(parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
       


    def tearDown(self):
        
        del self.communication
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
       

    '''
    1) item.name
    2) process(item) should get old self.Wall_E_voice_sensation,that will be
       spoken out
    3) parent Axon should get self.Wall_E_voice_sensation
    '''

    def test_ProcessItemVoice(self):
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)

        print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.LongTerm)')
        self.do_test_ProcessItemVoice(memory=Sensation.Memory.LongTerm)
        print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)')
        self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)

       
    def do_test_ProcessItemVoice(self, memory):
        # Make Voice to the history by parameter Memory type       
        # simulate Association has connected an voice to Item and Image 
        # Voice is in Sensory Memory, it is not used in Communication yet or
        # it can be in n LongTerm memory, classified to be a good Voice
        # Make two test of these 
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)

        Wall_E_voice_sensation_1 = Sensation.create(time=self.history_sensationTime,
                                                    memory=memory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    direction=Sensation.Direction.Out)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 0)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation,
                                           score=CommunicationTestCase.SCORE_1)
                                                                     
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_item_sensation,
                                           score=CommunicationTestCase.SCORE_1)
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        
        Wall_E_voice_sensation_2 = Sensation.create(time=self.history_sensationTime,
                                                    memory=memory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    direction=Sensation.Direction.Out)
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_image_sensation,
                                           score=CommunicationTestCase.SCORE_2)
        self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_item_sensation,
                                           score=CommunicationTestCase.SCORE_2)
        self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        
        

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
                                                  direction=Sensation.Direction.Out)
        
        Wall_E_image_sensation.associate(sensation=Wall_E_item_sensation,
                                         score=CommunicationTestCase.SCORE_1)
        # these connected each other
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        # TODO this verifies test, but not implementation
        '''
        Commented out, so we can  correct implementation
        # simulate Association has connected an voice to Item and Image 
        Wall_E_voice_sensation_1 = Sensation.create(sensationType=Sensation.SensationType.Voice, 
                                                       associations=[Sensation.Association(sensation=Wall_E_image_sensation,
                                                                                         score=CommunicationTestCase.SCORE_1),
                                                                    Sensation.Association(sensation=Wall_E_item_sensation,
                                                                                         score=CommunicationTestCase.SCORE_1)])
         # test that all is OK for tests
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        Wall_E_image_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation_1,
                                                                       score=CommunicationTestCase.SCORE_1))
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation_1,
                                                                      score=CommunicationTestCase.SCORE_1))
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
        
        # to be spoken
        self.assertEqual(sensation.getScore(),self.SCORE_2, 'should get Voice scored ' + str(self.SCORE_2))
        
        Wall_E_voice_sensation_1.delete()
        Wall_E_voice_sensation_2.delete()
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())

        
if __name__ == '__main__':
    unittest.main()

 