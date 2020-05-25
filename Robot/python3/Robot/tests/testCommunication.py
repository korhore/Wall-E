'''
Created on 21.06.2019
Updated on 24.05.2020
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
    VOICEDATA1=b'0x000x00'
    VOICEDATA2=b'0x000x000x01'
    VOICEDATA3=b'0x000x00x01x01'
    VOICEDATA4=b'0x000x00x01x01x01'
    VOICEDATA5=b'0x000x00x01x01x01x01'
    VOICEDATA6=b'0x000x00x01x01x01x01x01'
    VOICEDATA7=b'0x000x00x01x01x01x01x01x01'
    VOICEDATA8=b'0x000x00x01x01x01x01x01x01x01'
    
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
    def test_Presense(self):
        print('\ntest_Presense')
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Presense')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        # We get Voice, if Communication can respond but it cant
        self.expect(name='Entering, Too old response', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)        # Not sure do we always get a voice
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
      
        print('\n current Entering')
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
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        #self.assertEqual(len(self.communication.getMemory().presentItemSensations[Wall_E_item_sensation.getName()].getAssociations()), 1)
        
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        # now we should get Voice, Robot is presenting itself
        self.expect(name='Entering, response', isEmpty=False, isSpokenVoice=True, isHeardVoice=False, isFeeling=False)
        
        print('\n current Present')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

        # process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        self.expect(name='Present, used response', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)

        print('\n current Present again')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

        #process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        self.expect(name='Present again, used response', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)
        
        print('\n current Absent')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 0, 'len(self.communication.getMemory().presentItemSensations after Absent Item Sensation should be 0')

        #process              
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 0, 'len(self.communication.getMemory().presentItemSensations should be 0')
        self.expect(name='Absent', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)
 
    # #NAME2
        
        print('\n NAME2 current Entering')
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
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations after Entering Item Sensation should be 1')

        #process                      
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        #self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty, when entering')
        self.expect(name='Present Name 2, Conversation continues', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=True, isPositiveFeeling=True)
        
        print('\n NAME2 current Entering')
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
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations after Entering Item Sensation should NAME2 be 2')

        # make entering and process
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_2,
                                                 presence=Sensation.Presence.Entering)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations after Entering Item NAME2 Sensation should NAME2 be 2')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.expect(name='Entering Name 2, No basic change in presentation', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)
        
        print('\n NAME2 current Present')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations should be 2')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty')
        self.expect(name='Present Name 2, No basic change in presentation', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)

        print('\n NAME2 current Present again')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 2, 'len(self.communication.getMemory().presentItemSensations should be 2')
        self.expect(name='Present NAME2 again No basic change in presentation', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)
        
        print('\n NAME2 current Absent')
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
       
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        self.expect(name='Absent NAME2', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)
    
        print('\n NAME2 current Absent')
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 0, 'len(self.communication.getMemory().presentItemSensations should be 0')
        self.expect(name='Absent NAME', isEmpty=True, isSpokenVoice=False, isHeardVoice=False, isFeeling=False)
        
        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")  
        #self.logAxon()     
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='NO response', isEmpty=False, isSpokenVoice=False, isHeardVoice=False,  isFeeling=True, isNegativeFeeling=True)
        # no communicationItems should be left in 
        #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
        print("test continues, should have got Feeling from stopWaitingResponse")

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
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #simulate TensorflowClassification send presence item to MainBobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().presentItemSensations (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
        
        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # Note, Memory.Sensory is not ment to work
        # test again

        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
        
        # and test again once more 

        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)

       
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
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation)
                                                                     
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)# sometime 1, sometimes 2
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        
        Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_item_sensation)
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
        
        Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_item_sensation)
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
        
        Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_item_sensation)
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
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')

        #Item is entering, process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation, association=None)
        # should get just Voice as introducing Robot
        self.expect(name='introducing self', isEmpty=False, isSpokenVoice=True, isHeardVoice=False, isFeeling=False)


        Wall_E_voice_sensation_1.delete()
        Wall_E_voice_sensation_2.delete()
        
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
        
        self.assertEqual(len(self.communication.getMemory().presentItemSensations), 1, 'len(self.communication.getMemory().presentItemSensations should be 1')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation, association=None)

        # should get Voice and a Feeling between Voice and Item
        self.expect(name='response', isEmpty=False, isSpokenVoice=True, isHeardVoice=False,  isFeeling=True, isPositiveFeeling=True)
        

        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")       
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='NO response', isEmpty=False, isSpokenVoice=False, isHeardVoice=False,  isFeeling=True, isNegativeFeeling=True)
        # no communicationItems should be left in 
        #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
        print("test continues, should have got Feeling from stopWaitingResponse")
        
    '''
    How we expect tested Robot responses
    
    parameters
    name           name of the tested case
    isEmpty        do we expect a response at all
    isSpokenVoice  do we expect to get Voice to be spoken
    isHeardVoice   do we expect to get Voice heard
    isFeeling      do we expect to get Feeling
    '''
        
    def expect(self, name, isEmpty, isSpokenVoice, isHeardVoice, isFeeling, isPositiveFeeling=False, isNegativeFeeling=False):
        print("Now expect")       
        errortext = '{}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        self.assertEqual(self.getAxon().empty(), isEmpty, errortext)
        if not isEmpty:   
        #Voice and possible Feeling
            isSpokenVoiceStillExpected = isSpokenVoice
            isHeardVoiceStillExpected = isHeardVoice
            isFeelingStillExpected = isFeeling
            while(not self.getAxon().empty()):
                tranferDirection, sensation, association = self.getAxon().get()
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if isSpokenVoiceStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Muscle:
                            isSpokenVoiceStillExpected = False # got it
                    elif isHeardVoiceStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Sense:
                            isHeardVoiceStillExpected = False # got it
                    else: # got something unexpected Voice
                        errortext = '{}: Got unexpected Voice'.format(name)
                        self.assertTrue(False, errortext)
                if sensation.getSensationType() == Sensation.SensationType.Feeling:
                    errortext =  '{}: got unexpected Feeling Another Feeling {}'.format(name, str(not isFeelingStillExpected))
                    self.assertTrue(isFeelingStillExpected, errortext)
                    isFeelingStillExpected = False
                    self.assertEqual(sensation.getPositiveFeeling(), isPositiveFeeling)
                    self.assertEqual(sensation.getNegativeFeeling(), isNegativeFeeling)
                  
            # check that we got all
            self.assertFalse(isSpokenVoiceStillExpected, 'Did not get expected voice to be Spoken')                   
            self.assertFalse(isHeardVoiceStillExpected, 'Did not get expected  voice to be Heard')                   
            self.assertFalse(isFeelingStillExpected, 'Did not get feeling')                   
                
    '''
    Log how it would have happened, if we had expected this
    
    parameters
    name           name of the tested case
    isEmpty        do we expect a response at all
    isSpokenVoice  do we expect to get Voice to be spoken
    isHeardVoice   do we expect to get Voice heard
    isFeeling      do we expect to get Feeling
    '''
        
    def logExpect(self, name, isEmpty, isSpokenVoice, isHeardVoice, isFeeling):
        print("Now logExpect")       
        errortext = 'Log {}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        if self.getAxon().empty() != isEmpty:
            print(errortext)
            return
        if not isEmpty:   
        #Voice and possible Feeling
            isSpokenVoiceStillExpected = isSpokenVoice
            isHeardVoiceStillExpected = isHeardVoice
            isFeelingStillExpected = isFeeling
            while(not self.getAxon().empty()):
                tranferDirection, sensation, association = self.getAxon().get()
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if isSpokenVoiceStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Muscle:
                            isSpokenVoiceStillExpected = False # got it
                    elif isHeardVoiceStillExpected:
                        if sensation.getRobotType() == Sensation.RobotType.Sense:
                            isHeardVoiceStillExpected = False # got it
                    else: # got something unexpected Voice
                        errortext = '{}: Got unexpected Voice'.format(name)
                        print(errortext)
                        return
                if sensation.getSensationType() == Sensation.SensationType.Feeling:
                    errortext =  '{}: got unexpected Feeling Another Feeling {}'.format(name, str(not isFeelingStillExpected))
                    if not isFeelingStillExpected:
                        print(errortext)
                        return
                    isFeelingStillExpected = False
            # check that we got all
            if isSpokenVoiceStillExpected:
                print('Did not get expected voice to be Spoken')                   
            if isHeardVoiceStillExpected:
                print('Did not get expected  voice to be Heard')
            if isFeelingStillExpected:
                print('Did not get feeling')                   

        
if __name__ == '__main__':
    unittest.main()

 