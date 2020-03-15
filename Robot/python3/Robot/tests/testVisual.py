'''
Created on 12.03.2020
Updated on 12.03.2020
@author: reijo.korhonen@gmail.com

test Association class
python3 -m unittest tests/testVisual.py


'''
import time as systemTime

import unittest
from Sensation import Sensation
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
    ASSOCIATION_INTERVAL=3.0

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
    
    def getAxon(self):
        return self.axon

    '''
    Testing    
    '''
    
    def setUp(self):
        self.axon = Axon() # parent axon

        # define time in history, that is different than in all tests
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*max(VisualTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.stopSensation = Sensation.create(memory=Sensation.Memory.Working,
                                              sensationType=Sensation.SensationType.Stop,
                                            direction=Sensation.Direction.Out)

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memory
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = Sensation.create(time=self.history_sensationTime,
                                                      memory=Sensation.Memory.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      direction=Sensation.Direction.Out,
                                                      name=VisualTestCase.NAME,
                                                      presence = Sensation.Presence.Present)
        # Image is in LongTerm memory, it comes from TensorflowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = Sensation.create(time=self.history_sensationTime,
                                                       memory=Sensation.Memory.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       direction=Sensation.Direction.Out)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation,
                                             score=VisualTestCase.SCORE_1)
        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = Sensation.create(time=self.history_sensationTime,
                                                       memory=Sensation.Memory.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       direction=Sensation.Direction.Out,
                                                       data="1")
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation,
                                             score=VisualTestCase.SCORE_1)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation,
                                             score=VisualTestCase.SCORE_1)
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)

       
         
        self.visual = Visual(parent=self,
                            instanceName='Visual',
                            instanceType= Sensation.InstanceType.SubInstance,
                            level=2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())
       
    def getSenasations(self):

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memory
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      direction=Sensation.Direction.Out,
                                                      name=VisualTestCase.NAME,
                                                      presence = Sensation.Presence.Present)
        # Image is in LongTerm memory, it comes from TensorflowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = Sensation.create( memory=Sensation.Memory.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       direction=Sensation.Direction.Out)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation,
                                             score=VisualTestCase.SCORE_1)
        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = Sensation.create(memory=Sensation.Memory.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       direction=Sensation.Direction.Out,
                                                       data="1")
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation,
                                             score=VisualTestCase.SCORE_1)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation,
                                             score=VisualTestCase.SCORE_1)
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)

        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())


    def tearDown(self):
        self.visual.stop()
        while self.visual.running:
            systemTime.sleep(1)
         
        del self.visual
        del self.Wall_E_voice_sensation
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
        del self.axon
        
    def test_Visual(self):
        self.assertEqual(self.visual.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Visual\nCannot test properly this!')
        self.visual.start()
        
        for i in range(VisualTestCase.TEST_RUNS):
            self.getSenasations()
            
            self.visual.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_voice_sensation)
            self.visual.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation)
            self.visual.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_item_sensation)
            systemTime.sleep(3) # let Visual start before waiting it to stops           
            self.assertEqual(self.visual.getAxon().empty(), True, 'Axon should be empty again at the end of test_Visual!')
        
        self.visual.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        
        systemTime.sleep(3) # let result UI be shown until cleared           
        

 
        
if __name__ == '__main__':
    unittest.main()

 