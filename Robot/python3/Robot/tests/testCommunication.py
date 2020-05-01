'''
Created on 21.06.2019
Updated on 13.02.2020
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

class CommunicationTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
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
    def getId(self):
        return 1.1
    def getWho(self):
        return "CommunicationTestCase"

    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        self.axon = Axon(robot=self)
        self.communication = Communication(parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        # define time in history, that is different than in all tests
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      direction=Sensation.Direction.Out,
                                                      name=CommunicationTestCase.NAME,
                                                      score=CommunicationTestCase.SCORE_1)
        # Image is in LongTerm memoryType, it comes from TensorflowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       direction=Sensation.Direction.Out)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       direction=Sensation.Direction.Out,
                                                       data="1")
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
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
        print('\ntearDown')       
        del self.communication
        del self.Wall_E_voice_sensation
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
        
    def re_test_Presense(self):
        print('\ntest_Presense')
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Presense')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # Not sure do we always get a voice
        self.assertEqual(self.getAxon().empty(), True, 'Axon should  be empty')
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
      
        print('\n current Entering')
        # make potential response
        #systemTime.sleep(0.1)  # wait to get really even id
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  direction=Sensation.Direction.Out,
                                                  data="22")
        #systemTime.sleep(0.1)  # wait to get really even id
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)

        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        #self.assertEqual(len(self.communication.getMemory().presentItemSensations[Wall_E_item_sensation.getName()].getAssociations()), 1)
        
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty when name entering')

#         tranferDirection, sensation, association = self.getAxon().get()
#         #Feeling
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Feeling, 'should get Feeling')
        
        tranferDirection, sensation, association = self.getAxon().get()
        #Voice
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
        # to be spoken
        self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
        print('\n current Present')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

        # process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should be empty when present, because only Voice is used')
# no voice given so we don't get a voice back
#         tranferDirection, sensation = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')

        print('\n current Present again')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

        #process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty when entering again because only Voice is used')
# no voice given so we don't get a voice back
#         tranferDirection, sensation = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
        print('\n current Absent')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 0, 'len(self.communication.getMemory().presentItemSensations after Absent Item Sensation should be 0')

        #process              
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 0, 'len(self.communication.getMemory().presentItemSensations should be 0')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should be empty')
        
    # #NAME2
        print("test is sleeping " + str(Communication.COMMUNICATION_INTERVAL+ 1.0) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(Communication.COMMUNICATION_INTERVAL+ 2.0)
    
        print('\n current Entering')
        # make potential response
        #systemTime.sleep(0.1)  # wait to get really even id
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  direction=Sensation.Direction.Out,
                                                  data="333")
        #systemTime.sleep(0.1)  # wait to get really even id
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)
        
        # make entering item and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations after Entering Item Sensation should be 1')

        #process                      
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty, when entering')
        
        tranferDirection, sensation, association = self.getAxon().get()
        #Feeling
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Feeling, 'should get Feeling')
        
        tranferDirection, sensation, association = self.getAxon().get()
        #Voice
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
        # to be spoken
        self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')

        print('\n current Entering')
        # make potential response
        #systemTime.sleep(0.1)  # wait to get really even id
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  direction=Sensation.Direction.Out,
                                                  data="4444")
        #systemTime.sleep(0.1)  # wait to get really even id
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_2,
                                                 presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations after Entering Item Sensation should NAME2 be 2')

        # make entering and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_2,
                                                 presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations after Entering Item NAME2 Sensation should NAME2 be 2')

        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual((self.getAxon().empty()), True,  'Axon should be empty when entered and present')
        
# no voice given so we don't get a voice back
#         tranferDirection, sensation = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
        print('\n current Present')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
         #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations should be 2')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty')
# no voice given so we don't get a voice back
#         tranferDirection, sensation = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')

        print('\n current Present again')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
         #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations should be 2')
# no voice given so we don't get a voice back
#         tranferDirection, sensation = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
        print('\n current Absent')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
       
         #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence

        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(self.getAxon().empty(), True, 'Axon should  be empty')
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
    
        print('\n current Absent')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
         #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(self.getAxon().empty(), True, 'Axon should  be empty')
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 0, 'len(self.communication.getMemory().presentItemSensations should be 0')
        
    '''
    1) item.name
    2) process(item) should get old self.Wall_E_voice_sensation, that will be
       spoken out
    3) parent Axon should get self.Wall_E_voice_sensation
    4) parent Axon should get Sensation.SensationType.Feeling
    '''

    def test_ProcessItemVoice(self):
        print('\ntest_ProcessItemVoice')
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        print('\n current Present')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

#         #process       
#         self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
#         # at this point we have Voice in Axon
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty when entering again because only Voice is used')
        
        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # nope, Memory.Sensory is not ment to work
#         print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Sensory)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        #self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Sensory)
        
        # test again

        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # nope, Memory.Sensory is not ment to work
#         print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Sensory)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Sensory)

        # and test again once more 

        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # nope, Memory.Sensory is not ment to work
#         print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Sensory)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Sensory)

       
    '''
    prepare: create 3 voices into  memory, associated to self.Wall_E_item_sensation
    test:
    1) create item Sensation
    2) create image.sensation
    3) associate item Sensation and image.sensation
    4) C0mmunication.process(item)
    5) should get old self.Wall_E_voice_sensation, that will be
       spoken out
    6) parent Axon should get self.Wall_E_voice_sensation
    7) parent Axon should get Sensation.SensationType.Feeling
    '''

    def do_test_ProcessItemVoice(self, memoryType):
        print('\ndo_test_ProcessItemVoice')
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        # Make Voice to the history by parameter Memory type       
        # simulate Association has connected an voice to Item and Image 
        # Voice is in Sensory Memory, it is not used in Communication yet or
        # it can be in n LongTerm memoryType, classified to be a good Voice
        # Make two test of these 
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)

        # response # 1
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_sensation_1 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    direction=Sensation.Direction.Out,                                                   
                                                    data="55555")
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 0)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation)
                                                                     
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_item_sensation)
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        
        # response # 2
        #systemTime.sleep(0.1)  # wait to get really even id        
        Wall_E_voice_sensation_2 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    direction=Sensation.Direction.Out,                                                   
                                                    data="666666")
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_image_sensation)
        self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_item_sensation)
        self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())

        # response # 3
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_sensation_3 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    direction=Sensation.Direction.Out,
                                                    data="7777777")
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_image_sensation)
        self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_item_sensation)
        self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())

        
        
        

        ## test part
                
        #image and Item
        # simulate item and image are connected each other with TensorflowClassifivation
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 direction=Sensation.Direction.Out,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 associations=[],
                                                 presence=Sensation.Presence.Entering)
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_image_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Image,
                                                  direction=Sensation.Direction.Out)
        
        Wall_E_image_sensation.associate(sensation=Wall_E_item_sensation)
        # these connected each other
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        # TODO this verifies test, but not implementation
        '''
        Commented out, so we can  correct implementation
        # simulate Association has connected an voice to Item and Image 
        Wall_E_voice_sensation_1 = self.communication.createSensation(sensationType=Sensation.SensationType.Voice, 
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

         #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

        #process
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
        # We have Voice to be spoken out
        
        # minimum is that we get something
        self.assertNotEqual(self.getAxon().empty(), True, 'Axon should not be empty')        
        #Voice and possible Feeling
        while(not self.getAxon().empty()):
            tranferDirection, sensation, association = self.getAxon().get()
            self.assertTrue(sensation.getSensationType() == Sensation.SensationType.Voice or\
                            sensation.getSensationType() == Sensation.SensationType.Feeling, 'should get Voice or Feeling')
            if sensation.getSensationType() == Sensation.SensationType.Feeling:
                self.communication.getMemory().process(sensation = sensation)   # let Memoru process Feeling as MainRobot would let it to do
                print('\ndo_test_ProcessItemVoice got Feeling ' + sensation.toDebugStr())

            elif sensation.getSensationType() == Sensation.SensationType.Voice:
                print('\ndo_test_ProcessItemVoice got Voice ' + sensation.toDebugStr())
                # check Voice is to be spoken
                self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        
        # should get also feeling
#         self.assertNotEqual(self.getAxon().empty(), True, 'Axon should not be empty')        
#         #Feeling
#         tranferDirection, sensation, association = self.getAxon().get()
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Feeling, 'should get Feeling')
        
        # score or importance TODO check this
        # this is hard to implement, because used voiced get higher importance, so lower score voices can get higher importance
        # than higher score Voices,
        # When test begibs, we get Voices with score CORE_2, but after that we cab get also SCORE_1
        # Soooo seems that there is nothing wrong with algorithm, but hard to test
        #self.assertEqual(sensation.getScore(),self.SCORE_2, 'should get Voice scored ' + str(self.SCORE_2))

        Wall_E_voice_sensation_1.delete()
        Wall_E_voice_sensation_2.delete()
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        # now we respond
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_response_sensation = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    direction=Sensation.Direction.Out,
                                                    data="88888888")
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation.setTime(systemTime.time())
       
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_image_sensation)
        self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_item_sensation)
        self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_response_sensation, association=None)

        # We should have a Voice to be spoken out again 
        # minimum is that we get something

        # wait some time        
        #systemTime.sleep(5)
        # OOPS Why we don't get response, but getMostImportantSensation did not find any 
        
        self.assertEqual(self.getAxon().empty(), False, 'Axon should not be empty')
        
        tranferDirection, sensation, association = self.getAxon().get()
        #Feeling
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Feeling, 'should get Feeling')

#         tranferDirection, sensation, association = self.getAxon().get()
#         #Feeling
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Feeling, 'should get Feeling')
        
        tranferDirection, sensation, association = self.getAxon().get()
        #Voice
        self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
        # to be spoken
        self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
        

        # we son't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
        print("test is sleeping " + str(Communication.COMMUNICATION_INTERVAL+ 1.0) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(Communication.COMMUNICATION_INTERVAL+ 2.0)
        # no communicationItems should be left in 
        #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
        print("test continues, should got  stopWaitingResponse")       

        
if __name__ == '__main__':
    unittest.main()

 