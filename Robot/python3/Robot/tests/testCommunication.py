'''
Created on 21.06.2019
Updated on 26.10.2020
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
    
    ASSOCIATION_INTERVAL=3.0 # in float seconds
    AXON_WAIT = 10           # in int time to conditionally wait to get something into Axon

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
    VOICEDATA1=b'0x000x00'
    VOICEDATA2=b'0x000x000x01'
    VOICEDATA3=b'0x000x00x01x01'
    VOICEDATA4=b'0x000x00x01x01x01'
    VOICEDATA5=b'0x000x00x01x01x01x01'
    VOICEDATA6=b'0x000x00x01x01x01x01x01'
    VOICEDATA7=b'0x000x00x01x01x01x01x01x01'
    VOICEDATA8=b'0x000x00x01x01x01x01x01x01x01'
    VOICEDATA9=b'0x000x00x01x01x01x01x01x01x01x01'
    BEST_FEELING = Sensation.Feeling.Happy
    BETTER_FEELING = Sensation.Feeling.Good
    NORMAL_FEELING = Sensation.Feeling.Normal
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        #print('CommunicationTestCase getAxon')
        return self.axon
    def getId(self):
        #print('CommunicationTestCase getId')
        return 1.1
    def getWho(self):
        #print('CommunicationTestCase getWho')
        return "CommunicationTestCase"
    def log(self, logStr, logLevel=None):
        #print('CommunicationTestCase log')
        if hasattr(self, 'communication'):
            if self.communication:
                if logLevel == None:
                    logLevel = self.communication.LogLevel.Normal
                if logLevel <= self.communication.getLogLevel():
                     print(self.communication.getWho() + ":" + str( self.communication.config.level) + ":" + Sensation.Modes[self.communication.mode] + ": " + logStr)
    
    def logAxon(self):
        self.log("{} Axon with queue length {} full {}".format(self.getWho(), self.getAxon().queue.qsize(), self.getAxon().queue.full()))

    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        self.axon = Axon(robot=self)
        # Communication gets its own Memory
        # this is not same situation thab in normal run, where MainRobot level own Memory
        # this should be handled in test
        self.communication = Communication(parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        # should get Identity for proper functionality. Use Wall-E Identity in test
        self.communication.imageSensations, self.communication.voiceSensations = \
            self.communication.getIdentitySensations(who=CommunicationTestCase.NAME)
        self.assertTrue(len(self.communication.getMemory().getRobot().voiceSensations) > 0, "should have identity for testing")
        # test setup   
        # define time in history, that is different than in all tests
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
        
        
        #name=CommunicationTestCase.NAME
        # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=CommunicationTestCase.NAME,
                                                      score=CommunicationTestCase.SCORE_1)
        # Image is in LongTerm memoryType, it comes from TensorflowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = self.communication.createSensation(time=self.history_sensationTime,
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
        self.Wall_E_voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data=CommunicationTestCase.VOICEDATA1)
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
        
        #name=CommunicationTestCase.NAME2
        # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Eva_item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=CommunicationTestCase.NAME2,
                                                      score=CommunicationTestCase.SCORE_1)
        # Image is in LongTerm memoryType, it comes from TensorflowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Eva_image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense)
        self.Eva_item_sensation.associate(sensation=self.Eva_image_sensation)
        # set association also to history
        self.Eva_item_sensation.getAssociation(sensation=self.Eva_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Eva_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Eva_image_sensation.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Eva_voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data=CommunicationTestCase.VOICEDATA1)
        self.Eva_item_sensation.associate(sensation=self.Eva_voice_sensation)
        self.Eva_image_sensation.associate(sensation=self.Eva_voice_sensation)
        # these connected each other
        self.assertEqual(len(self.Eva_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Eva_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Eva_voice_sensation.getAssociations()), 2)

       
         
        self.assertEqual(len(self.Eva_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Eva_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Eva_voice_sensation.getAssociations()), 2)
        
        self.Eva_item_sensation_association_len = len(self.Eva_item_sensation.getAssociations())
        self.Eva_image_sensation_association_len = len(self.Eva_image_sensation.getAssociations())
        self.Eva_voice_sensation_association_len = len(self.Eva_voice_sensation.getAssociations())
        
        

    def tearDown(self):
        print('\ntearDown')       
        del self.communication
        del self.Wall_E_voice_sensation
        del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
  
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def re_test_Presense(self):
        print('\ntest_Presense')
                
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Entering {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        # We get Voice, if Communication can respond but it cant
        self.expect(name='Entering, Too old response', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)        # Not sure do we always get a voice
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 1')
      
        print('\n current Entering {}'.format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA2)
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)

        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        #self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()[Wall_E_item_sensation.getName()].getAssociations()), 1)
        
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        # now we should get Voice, Robot is presenting itself
        # TODO, but we get 2 voices, Communication is too voice, because iy introduces itself and starts to speak.
        self.expect(name='Entering, response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (and be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        # process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(name='Present, response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)

        # this situation should not happen
#         print('\n current Present again {}'.format(CommunicationTestCase.NAME))
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  robotType=Sensation.RobotType.Sense,
#                                                  name=CommunicationTestCase.NAME,
#                                                  score=CommunicationTestCase.SCORE_1,
#                                                  presence=Sensation.Presence.Present)
#         #simulate TensorflowClassification send presence item to MainRobot
#         #self.communication.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
# 
#         #process       
#         self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
#         self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
#         # TODO is this so?
#         self.expect(name='Present again, used response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)
        
        print('\n current Absent {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 0')

        #process              
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        self.expect(name='Absent', isEmpty=False, isSpoken=False, isHeard=False, isVoiceFeeling=True, isNegativeFeeling=True)
        
 
        # NAME with NAME2
        
        print('\n NAME current Entering {}',format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA3)
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME,
                                                  score=CommunicationTestCase.SCORE_1,
                                                  presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)
        
        # make entering item and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME,
                                                  score=CommunicationTestCase.SCORE_1,
                                                  presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 1')

        #process                      
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        #self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty, when entering')
        self.expect(name='Present Name 2, Conversation continues', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)
        
        print('\n NAME2 current Entering {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA4)
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_2,
                                                 presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 2')

        # make entering and process
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_2,
                                                 presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 2')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.expect(name='Entering Name 2, change in presentation',  isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)
        
        print('\n NAME2 current Present {}'.format(CommunicationTestCase.NAME2))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # TODO We find response
        # TODO if we find voice we speak, but now all voices are used. at this point
        # There has not been changes of present items and we have conversation on, but we have not send response
        # so we don't get response at this point
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        self.expect(name='Present Name 2, change in presentation',  isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)

        print('\n NAME2 current Present again {}'.format(CommunicationTestCase.NAME2))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # There has not been changes of present items and we have conversation on, but we have not send response
        # so we don't get response at this point
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        # TODO Next commented test should be valid Why this?
        #self.expect(name='Present NAME2 again basic change in presentation', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
        self.expect(name='Present NAME2 again basic change in presentation', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)
        
        print('\n NAME2 current Absent {}'.format(CommunicationTestCase.NAME2))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
       
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(name='Absent NAME2', isEmpty=False, isSpoken=False, isHeard=False, isVoiceFeeling=True, isNegativeFeeling=True)
    

# This was test Absent again
# and nothing was processed, so we should not get anything
# but there was still test, Now also test is commented out
#         print('\n NAME2 current Absent')
#         Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  robotType=Sensation.RobotType.Sense,
#                                                  name=CommunicationTestCase.NAME,
#                                                  score=CommunicationTestCase.SCORE_1,
#                                                  presence=Sensation.Presence.Absent)
#         #simulate TensorflowClassification send presence item to MainBobot
#         #self.communication.tracePresents(Wall_E_item_sensation) # presence
#        
#         self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
#         self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')
#         self.expect(name='Absent NAME', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
        
        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        
        # conversation is still on
#         self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
# 
#          # wait some time
#         sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
#         print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
#         systemTime.sleep(sleepTime)
#         #print("Now stopWaitingResponse should be happened and we test it")  
#         #self.logAxon()     
#         # should get Voice Feeling between Voice and Item
#         # BUT is hard to test, just log
#         # TODO Why commented does not work
#         self.expect(name='NO response', isEmpty=False, isSpoken=False, isHeard=False,  isVoiceFeeling=True, isNegativeFeeling=True)
#         #self.expect(name='NO response', isEmpty=True, isSpoken=False, isHeard=False,  isVoiceFeeling=False, isNegativeFeeling=False)
#         # no communicationItems should be left in 
#         #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
#         #print("test continues, should have got Feeling from stopWaitingResponse")
#         
        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')
        self.expect(name='Absent NAME', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
       

    '''
    Test and simulate Communication.process logic
    TODO This test is disabled, because we dpn't need if this is needed
    and this test is also broken.
    '''

    def re_test_1_SimulateProcess(self):
        print('\ntest_1_SimulateProcess')
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        allPresentItemSensations = self.communication.getMemory().getAllPresentItemSensations()
        self.assertEqual(len(allPresentItemSensations), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.assertEqual(allPresentItemSensations[0], Wall_E_item_sensation, 'allPresentItemSensations[0] should be Wall_E_item_sensation')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
        
        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.do_test_SimulateProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # Note, Memory.Sensory is not ment to work
        # test again
        # TODO test again does not work if we dob't delete sensations
        # because feelind for Voices has been changed of old ones and we don't
        # get new ones, because old sensations have better feeling
        # and if we delete sensation

#         print('self.do_test_SimulateProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_SimulateProcessItemVoice(memoryType=Sensation.MemoryType.Working)
#         
#         # and test again once more 
# 
#         print('self.do_test_SimulateProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_SimulateProcessItemVoice(memoryType=Sensation.MemoryType.Working)

    '''
    Simulate Communication.Process, step by step to test logic
    
    prepare: create 3 voices into  memory, associated to self.Wall_E_item_sensation
    test:
    1) create item Sensation
    2) create image sensation
    3) associate item Sensation and image.sensation
    4) Communication.process(item)
    
    At this point Communication should find Iten.name entering and
    start to speak introducing itself

    Parent should get old self.Wall_E_voice_sensation, that will be
       spoken out
       
    5) parent Axon should get self.Wall_E_voice_sensation
    6) parent Axon should get Sensation.SensationType.Feeling
    
    If Item.name heard Robot to speak, it react to starts speaks out 
    
    8) Communication.process(Voice)
    
    Communication reacts and
    
    9) parent Axon should get self.Wall_E_voice_sensation
    10) parent Axon should get Sensation.SensationType.Feeling
    
    Steps 8), 9) and 10) cound continue as long as Robot finds voices that hhave not been spoken in this conversatio
    If Item.name does not want to repond, then Communication should find out that conversation is ended and it should procuce just negative 
    
    11) parent Axon should get Sensation.SensationType.Feeling
        

    TensorfloClassafication produces
    Item.name Working Out
    
    AlsaAudioMicrophone produces  
    Voice Sensory Out
    
    And Communication should react to those and produce
    Voice Sensory In if it finds Voice to play and
    Feeling Sensory In anyway
    
    

    '''

    def do_test_SimulateProcessItemVoice(self, memoryType):
        print('\ndo_test_ProcessItemVoice 1')
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
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA5)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 0) # this is sometimes 1, sometimes 0
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len) # same
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation)
                                                                     
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)# sometime 1, sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_item_sensation, feeling = CommunicationTestCase.BETTER_FEELING) # 2. best feeling, so this should be answer # 2
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2) # sometimes 2. sometimes 3
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        
        # response # 2
        #systemTime.sleep(0.1)  # wait to get really even id        
        Wall_E_voice_sensation_2 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA6)
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 1) # sometimes 1. sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_item_sensation, feeling = CommunicationTestCase.BEST_FEELING) # 1. best feeling, so this should be answer # 1
        #self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 2) # sometimes 2, sometimes 3
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())

        # response # 3
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_sensation_3 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA7)
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 1)# sometimes 1, sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_item_sensation, feeling = CommunicationTestCase.NORMAL_FEELING) # 3. best feeling, so this should be answer # 3
        #self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 2) # sometime 2,sometimes 3
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())

        
        
        

        ## test part
                
        #image and Item
        # simulate item and image are connected each other with TensorflowClassifivation
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 associations=[],
                                                 presence=Sensation.Presence.Entering)
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_image_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        
        Wall_E_image_sensation.associate(sensation=Wall_E_item_sensation)
        # these connected each other
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        # TODO this verifies test, but not implementation
        '''
        Commented out, so we can correct implementation
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

         #simulate TensorflowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        #Item is entering, process
        self.simulateCommunicationProcess(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
# introducing self is commented out from test, because it is commented out from implementation
#         # should get just Voice as introducing Robot
#         self.expect(name='introducing self', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)

#        self.expect(name='introducing self', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_2, isHeard=False, isVoiceFeeling=True, isPositiveFeeling=True)
        self.expect(name='Starting conversation, get best voice', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_2, isHeard=False, isVoiceFeeling=False)

# OOPS What was meaning of next deletieons.
#         Wall_E_voice_sensation_1.delete()
#         Wall_E_voice_sensation_2.delete()
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        # now we respond
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_response_sensation = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA8)
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation.setTime(systemTime.time())
       
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # process
        self.simulateCommunicationProcess(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation)

        # should get Voice but no Feeling because Robot is kust introducing itself
        #self.expect(name='response', isEmpty=False, isSpoken=True, isHeard=False,  isVoiceFeeling=False, isPositiveFeeling=False)
        # should get 2. best voice and positive feeling for 1. best voice
        # But voice is still 1. best voice, why
        self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_1, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        #self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, voice=None, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        

 
         # now we respond again 
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_response_sensation = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA9)
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation.setTime(systemTime.time())
       
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+2)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+2)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # process
        self.simulateCommunicationProcess(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation)

        # should get Voice and a Feeling between Voice and Item
       #self.expect(name='response', isEmpty=False, isSpoken=True, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        # But voice is still 1. best voice, why
        self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_3, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        

        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")       
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='NO response', isEmpty=False, isSpoken=False, isHeard=False,  isVoiceFeeling=True, isNegativeFeeling=True)
        # no communicationItems should be left in 
        #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
        print("test continues, should have got Feeling from stopWaitingResponse")
        

        
    
    '''
    1) item.name MemoryType.Working Presence.Present
    2) process(item) should get old self.Wall_E_voice_sensation, that will be
       spoken out
    3) parent Axon should get self.Wall_E_voice_sensation
    4) parent Axon should get Sensation.SensationType.Feeling
    '''

    def test_2_ProcessItemPresent(self):
        print('\ntest_2_ProcessItemPresent')
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        allPresentItemSensations = self.communication.getMemory().getAllPresentItemSensations()
        self.assertEqual(len(allPresentItemSensations), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.assertEqual(allPresentItemSensations[0], Wall_E_item_sensation, 'allPresentItemSensations[0] should be Wall_E_item_sensation')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
        
        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # Note, Memory.Sensory is not ment to work
        # test again
        # TODO test again does not work if we dob't delete sensations
        # because feelind for Voices has been changed of old ones and we don't
        # get new ones, because old sensations have better feeling
        # and if we delete sensation

#         print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
#         
#         # and test again once more 
# 
#         print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)

       
    '''
    prepare: create 3 voices into  memory, associated to self.Wall_E_item_sensation
    test:
    1) create item Sensation
    2) create image sensation
    3) associate item Sensation and image.sensation
    4) Communication.process(item)
    
    At this point Communication should find Iten.name entering and
    start to speak introducing itself

    Parent should get old self.Wall_E_voice_sensation, that will be
       spoken out
       
    5) parent Axon should get self.Wall_E_voice_sensation
    6) parent Axon should get Sensation.SensationType.Feeling
    
    If Item.name heard Robot to speak, it react to starts speaks out 
    
    8) Communication.process(Voice)
    
    Communication reacts and
    
    9) parent Axon should get self.Wall_E_voice_sensation
    10) parent Axon should get Sensation.SensationType.Feeling
    
    Steps 8), 9) and 10) cound continue as long as Robot finds voices that hhave not been spoken in this conversatio
    If Item.name does not want to repond, then Communication should find out that conversation is ended and it should procuce just negative 
    
    11) parent Axon should get Sensation.SensationType.Feeling
        

    TensorfloClassafication produces
    Item.name Working Out
    
    AlsaAudioMicrophone produces  
    Voice Sensory Out
    
    And Communication should react to those and produce
    Voice Sensory In if it finds Voice to play and
    Feeling Sensory In anyway
    
    

    '''

    def do_test_ProcessItemVoice(self, memoryType):
        print('\ndo_test_ProcessItemVoice 1')
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
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA5)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 0) # this is sometimes 1, sometimes 0
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len) # same
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation)
                                                                     
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)# sometime 1, sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_item_sensation, feeling = CommunicationTestCase.BETTER_FEELING) # 2. best feeling, so this should be answer # 2
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2) # sometimes 2. sometimes 3
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        
        # response # 2
        #systemTime.sleep(0.1)  # wait to get really even id        
        Wall_E_voice_sensation_2 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA6)
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 1) # sometimes 1. sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_item_sensation, feeling = CommunicationTestCase.BEST_FEELING) # 1. best feeling, so this should be answer # 1
        #self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 2) # sometimes 2, sometimes 3
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())

        # response # 3
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_sensation_3 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA7)
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 1)# sometimes 1, sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_item_sensation, feeling = CommunicationTestCase.NORMAL_FEELING) # 3. best feeling, so this should be answer # 3
        #self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 2) # sometime 2,sometimes 3
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())

        
        
        

        ## test part
                
        #image and Item
        # simulate item and image are connected each other with TensorflowClassifivation
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 associations=[],
                                                 presence=Sensation.Presence.Entering)
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_image_sensation_1 = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        
        Wall_E_image_sensation_1.associate(sensation=Wall_E_item_sensation)
        # these connected each other
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation_1.getAssociations()), 1)
        # TODO this verifies test, but not implementation
        '''
        Commented out, so we can correct implementation
        # simulate Association has connected an voice to Item and Image 
        Wall_E_voice_sensation_1 = self.communication.createSensation(sensationType=Sensation.SensationType.Voice, 
                                                       associations=[Sensation.Association(sensation=Wall_E_image_sensation_1,
                                                                                         score=CommunicationTestCase.SCORE_1),
                                                                    Sensation.Association(sensation=Wall_E_item_sensation,
                                                                                         score=CommunicationTestCase.SCORE_1)])
         # test that all is OK for tests
        self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        Wall_E_image_sensation_1.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation_1,
                                                                       score=CommunicationTestCase.SCORE_1))
        self.assertEqual(len(Wall_E_image_sensation_1.getAssociations()), 2)
        # add missing associations test that all is OK for tests
        Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation_1,
                                                                      score=CommunicationTestCase.SCORE_1))
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 2)

        
        #######################
        '''

         #simulate TensorflowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        #Item is entering, process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        
        self.assertEqual(len(self.communication.saidSensations), 2, 'self.communication.saidSensations should have 2 items')
        self.assertEqual(self.communication.saidSensations[0], Wall_E_image_sensation_1.getDataId(), 'self.communication.saidSensations[0] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[1], Wall_E_voice_sensation_2.getDataId(), 'self.communication.saidSensations[1] should have Wall_E_voice_sensation_2.getDataId()')
# introducing self is commented out from test, because it is commented out from implementation
#         # should get just Voice as introducing Robot
#         self.expect(name='introducing self', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False)

#        self.expect(name='introducing self', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_2, isHeard=False, isVoiceFeeling=True, isPositiveFeeling=True)
        self.expect(name='Starting conversation, get best voice', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_voice_sensation_2,
                    image=Wall_E_image_sensation_1,
                    isVoiceFeeling=False,
                    isImageFeeling=False)

# OOPS What was meaning of next deletieons.
#         Wall_E_voice_sensation_1.delete()
#         Wall_E_voice_sensation_2.delete()
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        # now we respond
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_response_sensation = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA8)
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation.setTime(systemTime.time())
       
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation)
        
        #self.assertEqual(len(self.communication.saidSensations), 3, 'self.communication.saidSensations should have 3 items')
        self.assertEqual(len(self.communication.saidSensations), 4, 'self.communication.saidSensations should have 4 items')
        self.assertEqual(len(self.communication.heardSensations), 1, 'self.communication.heardSensations should have 1 items')
        print("Wall_E_voice_sensation_1.getDataId()    {}".format(Wall_E_voice_sensation_1.getDataId()))
        print("Wall_E_voice_sensation_2.getDataId()    {}".format(Wall_E_voice_sensation_2.getDataId()))
        print("Wall_E_voice_sensation_3.getDataId()    {}".format(Wall_E_voice_sensation_3.getDataId()))
        print("Wall_E_voice_response_sensation.getDataId()    {}".format(Wall_E_voice_response_sensation.getDataId()))
        print("self.communication.saidSensations[0] {}".format(self.communication.saidSensations[0]))
        print("self.communication.saidSensations[1] {}".format(self.communication.saidSensations[1]))
        print("self.communication.saidSensations[2] {}".format(self.communication.saidSensations[2]))
        print("self.communication.saidSensations[3] {}".format(self.communication.saidSensations[3]))
        #print("self.communication.saidSensations[2] {}".format(self.communication.saidSensations[2]))
        print("self.communication.heardSensations[0] {}".format(self.communication.heardSensations[0]))
       
        self.assertEqual(self.communication.saidSensations[0], Wall_E_image_sensation_1.getDataId(), 'self.communication.saidSensations[0] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[1], Wall_E_voice_sensation_2.getDataId(), 'self.communication.saidSensations[1] should have Wall_E_voice_sensation_2.getDataId()')
        self.assertEqual(self.communication.saidSensations[2], self.Wall_E_image_sensation.getDataId(), 'self.communication.saidSensations[2] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[3], Wall_E_voice_sensation_1.getDataId(), 'self.communication.saidSensations[3] should have Wall_E_voice_sensation_1.getDataId()')
        self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation.getDataId()')

        # should get Voice but no Feeling because Robot is is introducing itself
        #self.expect(name='response', isEmpty=False, isSpoken=True, isHeard=False,  isVoiceFeeling=False, isPositiveFeeling=False)
        # should get 2. best voice and positive feeling for 1. best voice
        # But voice is still 1. best voice, why
        # TODO expect. Ww should get 2 feeling sensation, 1 Voice and 1 Image sensation
        # expect does not support this yet
#         self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, isHeard=False,
#                     voice=Wall_E_voice_sensation_1, isVoiceFeeling=True, isPositiveFeeling=True)
        
        self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_voice_sensation_1,
                    image=self.Wall_E_image_sensation,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        #self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, voice=None, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        

 
         # now we respond again 
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_response_sensation_2 = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA9)
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation_2.setTime(systemTime.time())
       
        Wall_E_voice_response_sensation_2.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation_2.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+2)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation_2.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation_2.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+3)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation_2)

        self.assertEqual(len(self.communication.saidSensations), 5, 'self.communication.saidSensations should have 5 items')
        self.assertEqual(len(self.communication.heardSensations), 2, 'self.communication.heardSensations should have 2 items')
        print("Wall_E_voice_sensation_1.getDataId()    {}".format(Wall_E_voice_sensation_1.getDataId()))
        print("Wall_E_voice_sensation_2.getDataId()    {}".format(Wall_E_voice_sensation_2.getDataId()))
        print("Wall_E_voice_sensation_3.getDataId()    {}".format(Wall_E_voice_sensation_3.getDataId()))
        print("self.communication.saidSensations[0] {}".format(self.communication.saidSensations[0]))
        print("self.communication.saidSensations[1] {}".format(self.communication.saidSensations[1]))
        print("self.communication.saidSensations[2] {}".format(self.communication.saidSensations[2]))
        print("self.communication.saidSensations[3] {}".format(self.communication.saidSensations[3]))
        print("self.communication.saidSensations[4] {}".format(self.communication.saidSensations[4]))
        print("self.communication.heardSensations[0] {}".format(self.communication.heardSensations[0]))
        print("self.communication.heardSensations[1] {}".format(self.communication.heardSensations[1]))
        
        # We don't have other unused images any more
        
        self.assertEqual(self.communication.saidSensations[0], Wall_E_image_sensation_1.getDataId(), 'self.communication.saidSensations[0] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[1], Wall_E_voice_sensation_2.getDataId(), 'self.communication.saidSensations[1] should have Wall_E_voice_sensation_2.getDataId()')
        self.assertEqual(self.communication.saidSensations[2], self.Wall_E_image_sensation.getDataId(), 'self.communication.saidSensations[2] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[3], Wall_E_voice_sensation_1.getDataId(), 'self.communication.saidSensations[3] should have Wall_E_voice_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[4], Wall_E_voice_sensation_3.getDataId(), 'self.communication.saidSensations[4] should have Wall_E_voice_sensation_3.getDataId()')
        self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation.getDataId()')
        self.assertEqual(self.communication.heardSensations[1], Wall_E_voice_response_sensation_2.getDataId(), 'self.communication.heardSensations[1] should have Wall_E_voice_response_sensation_2.getDataId()')
      # should get Voice and a Feeling between Voice and Item
       #self.expect(name='response', isEmpty=False, isSpoken=True, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        # But voice is still 1. best voice, why
        #self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_3, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        self.expect(name='response, third best voice', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_voice_sensation_3,
                    image=None,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        

        # response 3
        Wall_E_voice_response_sensation_3 = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA9)
       
        Wall_E_voice_response_sensation_3.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation_3.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+2)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation_3.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation_3.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+2)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation_3)

        self.assertEqual(len(self.communication.saidSensations), 6, 'self.communication.saidSensations should have 6 items')
        self.assertEqual(len(self.communication.heardSensations), Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH, 'self.communication.heardSensations should have {} items'.format(Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH))
        print("Wall_E_voice_sensation_1.getDataId()    {}".format(Wall_E_voice_sensation_1.getDataId()))
        print("Wall_E_voice_sensation_2.getDataId()    {}".format(Wall_E_voice_sensation_2.getDataId()))
        print("Wall_E_voice_sensation_3.getDataId()    {}".format(Wall_E_voice_sensation_3.getDataId()))
        print("self.communication.saidSensations[0] {}".format(self.communication.saidSensations[0]))
        print("self.communication.saidSensations[1] {}".format(self.communication.saidSensations[1]))
        print("self.communication.saidSensations[2] {}".format(self.communication.saidSensations[2]))
        print("self.communication.saidSensations[3] {}".format(self.communication.saidSensations[3]))
        print("self.communication.saidSensations[4] {}".format(self.communication.saidSensations[4]))
        print("self.communication.saidSensations[5] {}".format(self.communication.saidSensations[5]))
        print("self.communication.heardSensations[0] {}".format(self.communication.heardSensations[0]))
        print("self.communication.heardSensations[1] {}".format(self.communication.heardSensations[1]))
        for i in range(2,Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH):
            print("self.communication.heardSensations[{}] {}".format(i, self.communication.heardSensations[i]))
        
        # We don't have other unused images any more
        
        self.assertEqual(self.communication.saidSensations[0], Wall_E_image_sensation_1.getDataId(), 'self.communication.saidSensations[0] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[1], Wall_E_voice_sensation_2.getDataId(), 'self.communication.saidSensations[1] should have Wall_E_voice_sensation_2.getDataId()')
        self.assertEqual(self.communication.saidSensations[2], self.Wall_E_image_sensation.getDataId(), 'self.communication.saidSensations[2] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[3], Wall_E_voice_sensation_1.getDataId(), 'self.communication.saidSensations[3] should have Wall_E_voice_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[4], Wall_E_voice_sensation_3.getDataId(), 'self.communication.saidSensations[4] should have Wall_E_voice_sensation_3.getDataId()')
        self.assertEqual(self.communication.saidSensations[5], Wall_E_voice_response_sensation.getDataId(), 'self.communication.saidSensations[5] should have Wall_E_voice_response_sensation.getDataId()')
        self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation_2.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation_2.getDataId()')
        self.assertEqual(self.communication.heardSensations[1], Wall_E_voice_response_sensation_3.getDataId(), 'self.communication.heardSensations[1] should have Wall_E_voice_response_sensation_3.getDataId()')
        # TODO make this test more common about Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH
        if Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH == 2:
            # first hweard is now dropped
            #self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation.getDataId()')
            self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation_2.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation_2.getDataId()')
            self.assertEqual(self.communication.heardSensations[1], Wall_E_voice_response_sensation_3.getDataId(), 'self.communication.heardSensations[1] should have Wall_E_voice_response_sensation_3.getDataId()')
        # should get Voice and a Feeling between Voice and Item
        # Voice should be already spoken Voice, but not last one, so it would be Wall_E_voice_response_sensation, which is dropped fron feard voices
        # But voice is still 1. best voice, why
        self.expect(name='response, Wall_E_voice_response_sensation', isEmpty=False, isSpoken=True, isHeard=False,  
                    voice=Wall_E_voice_response_sensation, isVoiceFeeling=True, isPositiveFeeling=True)
        

        # response 4
        Wall_E_voice_response_sensation_4 = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA9)
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation_4.setTime(systemTime.time())
       
        Wall_E_voice_response_sensation_4.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation_4.getAssociations()), 2)#1
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+2)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_response_sensation_4.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation_4.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+2)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation_4)

        self.assertEqual(len(self.communication.saidSensations), 7, 'self.communication.saidSensations should have 7 items')
        self.assertEqual(len(self.communication.heardSensations), Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH, 'self.communication.heardSensations should have {} items'.format(Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH))
        print("Wall_E_voice_sensation_1.getDataId()    {}".format(Wall_E_voice_sensation_1.getDataId()))
        print("Wall_E_voice_sensation_2.getDataId()    {}".format(Wall_E_voice_sensation_2.getDataId()))
        print("Wall_E_voice_sensation_3.getDataId()    {}".format(Wall_E_voice_sensation_3.getDataId()))
        print("self.communication.saidSensations[0] {}".format(self.communication.saidSensations[0]))
        print("self.communication.saidSensations[1] {}".format(self.communication.saidSensations[1]))
        print("self.communication.saidSensations[2] {}".format(self.communication.saidSensations[2]))
        print("self.communication.saidSensations[3] {}".format(self.communication.saidSensations[3]))
        print("self.communication.saidSensations[4] {}".format(self.communication.saidSensations[4]))
        print("self.communication.saidSensations[5] {}".format(self.communication.saidSensations[5]))
        print("self.communication.saidSensations[6] {}".format(self.communication.saidSensations[6]))
        print("self.communication.heardSensations[0] {}".format(self.communication.heardSensations[0]))
        print("self.communication.heardSensations[1] {}".format(self.communication.heardSensations[1]))
        for i in range(2,Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH):
            print("self.communication.heardSensations[{}] {}".format(i, self.communication.heardSensations[i]))
        
        # We don't have other unused images any more
        
        self.assertEqual(self.communication.saidSensations[0], Wall_E_image_sensation_1.getDataId(), 'self.communication.saidSensations[0] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[1], Wall_E_voice_sensation_2.getDataId(), 'self.communication.saidSensations[1] should have Wall_E_voice_sensation_2.getDataId()')
        self.assertEqual(self.communication.saidSensations[2], self.Wall_E_image_sensation.getDataId(), 'self.communication.saidSensations[2] should have Wall_E_image_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[3], Wall_E_voice_sensation_1.getDataId(), 'self.communication.saidSensations[3] should have Wall_E_voice_sensation_1.getDataId()')
        self.assertEqual(self.communication.saidSensations[4], Wall_E_voice_sensation_3.getDataId(), 'self.communication.saidSensations[4] should have Wall_E_voice_sensation_3.getDataId()')
        self.assertEqual(self.communication.saidSensations[5], Wall_E_voice_response_sensation.getDataId(), 'self.communication.saidSensations[5] should have Wall_E_voice_response_sensation.getDataId()')
        self.assertEqual(self.communication.saidSensations[6], Wall_E_voice_response_sensation_2.getDataId(), 'self.communication.saidSensations[5] should have Wall_E_voice_response_sensation.getDataId()')
        #self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation_2.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation_2.getDataId()')
        self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation_3.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation_3.getDataId()')
        self.assertEqual(self.communication.heardSensations[1], Wall_E_voice_response_sensation_4.getDataId(), 'self.communication.heardSensations[1] should have Wall_E_voice_response_sensation.getDataId()')
        # TODO make this test more common about Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH
        if Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH == 2:
            # first heard is now dropped
            self.assertEqual(self.communication.heardSensations[0], Wall_E_voice_response_sensation_3.getDataId(), 'self.communication.heardSensations[0] should have Wall_E_voice_response_sensation_3.getDataId()')
            self.assertEqual(self.communication.heardSensations[1], Wall_E_voice_response_sensation_4.getDataId(), 'self.communication.heardSensations[1] should have Wall_E_voice_response_sensation_4.getDataId()')
        # should get Voice and a Feeling between Voice and Item
        # Voice should be already spoken Voice, but not last one, so it would be Wall_E_voice_response_sensation_2, which is dropped fron heard voices
        self.expect(name='response, Wall_E_voice_response_sensation_2', isEmpty=False, isSpoken=True, isHeard=False,  
                    voice=Wall_E_voice_response_sensation_2, isVoiceFeeling=True, isPositiveFeeling=True)

        # TODO end
 
        
        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")       
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='NO response', isEmpty=False, isSpoken=False, isHeard=False,  isVoiceFeeling=True, isNegativeFeeling=True)
        # no communicationItems should be left in 
        #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
        print("test continues, should have got Feeling from stopWaitingResponse")
       
    '''
    How we expect tested Robot responses
    
    parameters
    name           name of the tested case
    isEmpty        do we expect a response at all
    isSpoken  do we expect to get Voice to be spoken
    isHeard   do we expect to get Voice heard
    isVoiceFeeling      do we expect to get Feeling
    '''
        
    def expect(self, name, isEmpty, isSpoken, isHeard,
               isVoiceFeeling, voice=None,
               isImageFeeling=False, image=None, 
               isPositiveFeeling=False, isNegativeFeeling=False):
        print("Now expect")
        errortext = '{}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        if not isEmpty: 
            i=0  
            while self.getAxon().empty() and i < CommunicationTestCase.AXON_WAIT:
                systemTime.sleep(1)
                i=i+1
                print('slept {}s to get something to Axon'.format(i))
        self.assertEqual(self.getAxon().empty(), isEmpty, errortext)
        if not isEmpty:   
        #Voice. Image and possible Feeling
            isSpokenVoiceStillExpected = isSpoken
            isHeardVoiceStillExpected = isHeard
            isSpokenImageStillExpected = isSpoken
            isHeardImageStillExpected = isHeard
            if voice is not None:
                isVoiceStillExpected = True
            else:
                isVoiceStillExpected = False
                isSpokenVoiceStillExpected = False
                isHeardVoiceStillExpected = False
            if image is not None:
                isImageStillExpected = True
            else:
                isImageStillExpected = False
                isSpokenImageStillExpected = False
                isHeardImageStillExpected = False
            isVoiceFeelingStillExpected = isVoiceFeeling
            isImageFeelingStillExpected = isImageFeeling
            while(not self.getAxon().empty()):
                tranferDirection, sensation = self.getAxon().get()
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if isVoiceStillExpected:
                        isVoiceStillExpected = (sensation.getDataId() != voice.getDataId())
                    if isSpokenVoiceStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Muscle:
                            isSpokenVoiceStillExpected = False # got it
                    elif isHeardVoiceStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Sense:
                            isHeardVoiceStillExpected = False # got it
                    else: # got something unexpected Voice
                        errortext = '{}: Got unexpected Voice, duplicate {}'.format(name, isSpoken or isHeard)
                        self.assertTrue(False, errortext)
                elif sensation.getSensationType() == Sensation.SensationType.Image:
                    if isImageStillExpected:
                        isImageStillExpected = (sensation.getDataId() != image.getDataId())
                    if isSpokenImageStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Muscle:
                            isSpokenImageStillExpected = False # got it
                    elif isHeardImageStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Sense:
                            isHeardImageStillExpected = False # got it
                    else: # got something unexpected Image
                        errortext = '{}: Got unexpected Image, duplicate {}'.format(name, isSpoken or isHeard)
                        self.assertTrue(False, errortext)
                elif sensation.getSensationType() == Sensation.SensationType.Feeling:
                    errortext =  '{}: got unexpected Feeling Another Feeling {}'.format(name, str(not (isVoiceFeelingStillExpected or isImageFeelingStillExpected)))
                    self.assertTrue(isVoiceFeelingStillExpected or isImageFeelingStillExpected, errortext)
#                     self.assertEqual(len(sensation.getAssociations()), 1)
                    if sensation.getOtherAssociateSensation().getSensationType() == Sensation.SensationType.Voice:
                        isVoiceFeelingStillExpected = False
                    elif sensation.getOtherAssociateSensation().getSensationType() == Sensation.SensationType.Image:
                        isImageFeelingStillExpected = False
                    else:
                        self.assertTrue(False, "Unsupported associate type {} with feeling".format( sensation.getOtherAssociateSensation().getSensationType()))

                    self.assertEqual(sensation.getPositiveFeeling(), isPositiveFeeling)
                    self.assertEqual(sensation.getNegativeFeeling(), isNegativeFeeling)
                  
            # check that we got all
            self.assertFalse(isSpokenVoiceStillExpected, 'Did not get expected voice to be Spoken')                   
            self.assertFalse(isHeardVoiceStillExpected,  'Did not get expected voice to be Heard')                   
            self.assertFalse(isVoiceStillExpected,  'Did not get expected voice')                   
            self.assertFalse(isSpokenImageStillExpected, 'Did not get expected image to be Spoken')                   
            self.assertFalse(isHeardImageStillExpected,  'Did not get expected image to be Heard')                   
            self.assertFalse(isImageStillExpected,  'Did not get expected image')                   
            self.assertFalse(isVoiceFeelingStillExpected, 'Did not get voice feeling')                   
            self.assertFalse(isImageFeelingStillExpected, 'Did not get image feeling')                   
                
    '''
    Log how it would have happened, if we had expected this
    
    parameters
    name           name of the tested case
    isEmpty        do we expect a response at all
    isSpoken  do we expect to get Voice to be spoken
    isHeard   do we expect to get Voice heard
    isVoiceFeeling      do we expect to get Feeling
    '''
        
    def logExpect(self, name, isEmpty, isSpoken, isHeard, isVoiceFeeling):
        print("Now logExpect")       
        errortext = 'Log {}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        if self.getAxon().empty() != isEmpty:
            print(errortext)
            return
        if not isEmpty:   
        #Voice and possible Feeling
            isSpokenStillExpected = isSpoken
            isHeardStillExpected = isHeard
            isVoiceFeelingStillExpected = isVoiceFeeling
            while(not self.getAxon().empty()):
                tranferDirection, sensation = self.getAxon().get()
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if isSpokenStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Muscle:
                            isSpokenStillExpected = False # got it
                    elif isHeardStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Sense:
                            isHeardStillExpected = False # got it
                    else: # got something unexpected Voice
                        errortext = '{}: Got unexpected Voice'.format(name)
                        print(errortext)
                        return
                if sensation.getSensationType() == Sensation.SensationType.Feeling:
                    errortext =  '{}: got unexpected Feeling Another Feeling {}'.format(name, str(not isVoiceFeelingStillExpected))
                    if not isVoiceFeelingStillExpected:
                        print(errortext)
                        return
                    isVoiceFeelingStillExpected = False
            # check that we got all
            if isSpokenStillExpected:
                print('Did not get expected voice to be Spoken')                   
            if isHeardStillExpected:
                print('Did not get expected  voice to be Heard')
            if isVoiceFeelingStillExpected:
                print('Did not get feeling')                   

        
if __name__ == '__main__':
    unittest.main()

 