'''
Created on 21.06.2019
Updated on 13.04.2021
@author: reijo.korhonen@gmail.com

test Association class
python3 -m unittest tests/testCommunication.py


'''
import time as systemTime
import os

import unittest
from Sensation import Sensation
# import Communication, but
# set Communication.COMMUNICATION_INTERVAL smaller,
# so test runs faster, when no waits normal time 30s, when we don't get
# response from person
TEST_COMMUNICATION_INTERVAL=1.0 
from Communication.Communication import Communication
Communication.COMMUNICATION_INTERVAL = TEST_COMMUNICATION_INTERVAL

from Association.Association import Association
from Axon import Axon
from Robot import Robot

from RobotTestCase import RobotTestCase

class CommunicationTestCase(unittest.TestCase, RobotTestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    


    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        
        self.CleanDataDirectory()

        Robot.mainRobotInstance = self
        self.mainNames = self.MAINNAMES
        self.axon = Axon(robot=self)

        # Robot to test        
        self.communication = Communication(mainRobot=self,
                                           parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.setRobotMainNames(self.communication, self.MAINNAMES)
        self.setRobotLocations(self.communication, self.getLocations())
        # should correct self.communication.itemConversations,
        # because it is crested in _init__ normal way with configuration settings
        self.communication.itemConversations={}
        self.communication.robotConversations={}
        if len(self.communication.getLocations()) > 0:
            for location in self.communication.getLocations():
                self.communication.itemConversations[location] =\
                    Communication.ConversationWithItem(robot=self.communication, location=location)
                self.communication.robotConversations[location] =\
                    Communication.ConversationWithRobot(robot=self.communication, location=location)
        else:
            self.communication.itemConversations['']=Communication.ConversationWithItem(robot=self.communication, location='')
            self.communication.robotConversations['']=Communication.ConversationWithRobot(robot=self.communication, location='')
            
        # should get Identity for proper functionality. Use Wall-E Identity in test
        self.communication.imageSensations, self.communication.voiceSensations = \
            self.communication.getIdentitySensations(name=CommunicationTestCase.NAME)
        self.assertTrue(len(self.communication.getMemory().getRobot().voiceSensations) > 0, "should have identity for testing")
        
        self.doSetUp(robot=self.communication)
        

    def tearDown(self):
        print('\ntearDown')       
        self.doTearDown()

        del self.communication
        
    '''
    TensorfloClassafication produces
    Item.name Working Out
    
   '''    
    def test_PresenseItemPresentRobot(self):
        self.doTest_PresenseItemPresentRobot(robot=self.communication, isWait=False)
        
    def doTest_PresenseItemPresentRobot(self, robot, isWait):
        # create Robot sensation
        self.assertFalse(len(robot.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertFalse(robot.getMemory().hasRobotsPresence())
        roboSensation=self.createSensation(associations=[],
                                           robotType=Sensation.RobotType.Communication,
                                           sensationName='roboSensation',
                                           robot=robot,
                                           sensationType = Sensation.SensationType.Robot,
                                           memoryType = Sensation.MemoryType.Working,
                                           name = robot.getName(),
                                           presence = Sensation.Presence.Present,
                                           locations = self.getLocations(),
                                           mainNames=self.OTHERMAINNAMES), # Should haver other mainnames than this Robot to get robot presence
        
        self.assertTrue(len(robot.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertTrue(robot.getMemory().hasRobotsPresence())

        self.do_test_PresenseItemRobot(robot=robot, isWait=isWait, isPresentRobot = True)
            
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def test_PresenseItemAbsentRobot(self):
        self.doTest_PresenseItemAbsentRobot(robot=self.communication, isWait=False)
        
    def doTest_PresenseItemAbsentRobot(self, robot, isWait):
        # create Robot sensation
        self.assertFalse(len(robot.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertFalse(robot.getMemory().hasRobotsPresence())
        roboSensation=self.createSensation(associations=[],
                                           robotType=Sensation.RobotType.Communication,
                                           sensationName='roboSensation',
                                           robot=robot,
                                           sensationType = Sensation.SensationType.Robot,
                                           memoryType = Sensation.MemoryType.Working,
                                           name = robot.getName(),
                                           presence = Sensation.Presence.Absent,
                                           locations = self.getLocations())
        
        self.assertFalse(len(robot.getMemory().getAllPresentRobotSensations()) > 0)

        self.do_test_PresenseItemRobot(robot=robot, isWait=isWait, isPresentRobot = False)
        self.assertFalse(robot.getMemory().hasRobotsPresence())
        

  
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def do_test_PresenseItemRobot(self, robot, isWait, isPresentRobot):
        print('\ntest_Presense')
                
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Entering {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation_entering = self.createSensation(
                                                 sensationName='Wall_E_item_sensation_entering',
                                                 robot=robot,
                                                 time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.getLocations())
        self.assertTrue(Wall_E_item_sensation_entering.isForgettable())
        self.printSensationNameById(note='Wall_E_item_sensation_entering test', dataId= Wall_E_item_sensation_entering.getDataId())
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering)
        # We get Voice, Image, if Communication can respond but it can't
        self.expect(isWait=isWait,
                    name='Entering, Too old response', isEmpty=True)
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 1, 'len(robot.getMemory()..getAllPresentItemSensations() should be 1')
      
        print('\n current Entering {}'.format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation1 = self.createSensation(
                                                sensationName='voice_sensation1',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTestCase.VOICEDATA2,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation1.isForgettable())
        self.printSensationNameById(note='voice_sensation1 test', dataId=voice_sensation1.getDataId())
        image_sensation1 = self.createSensation(
                                                sensationName='image_sensation1',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.assertTrue(image_sensation1.isForgettable())
        self.printSensationNameById(note='image_sensation1 test', dataId=image_sensation1.getDataId())
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(item_sensation1.isForgettable())
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        item_sensation1.associate(sensation=voice_sensation1)
        item_sensation1.associate(sensation=image_sensation1)
        voice_sensation1.associate(sensation=image_sensation1)

        Wall_E_item_sensation_entering2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering2',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(systemTime.time() - Wall_E_item_sensation_entering2.getTime() < Communication.COMMUNICATION_INTERVAL)
       
        self.assertTrue(Wall_E_item_sensation_entering2.isForgettable())
        self.printSensationNameById(note='Wall_E_item_sensation_entering2 test', dataId=Wall_E_item_sensation_entering2.getDataId())
         
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 1, 'len(robot.getMemory().getAllPresentItemSensations() should be 1')

        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering2)

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation1, isExactMuscleImage=True,
                        muscleVoice=voice_sensation1, isExactMuscleVoice=True,
                        communicationItem=Wall_E_item_sensation_entering2, isExactCommunicationItem=True)
            # To test other Communication Robots functionality we must make a trick and change this Sensation ocatio
            # so this Robot think that Sensation comes fromother Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, reply to communicationItem, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation1, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation1, isExactCommunicationVoice=True,
                        communicationItem=None)        # TODO remove this, it is not valid any more
        else:  
            self.expect(isWait=isWait,
                        name='Entering, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation1, isExactMuscleImage=True,
                        muscleVoice=voice_sensation1, isExactMuscleVoice=True)


       
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation_present = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present test', dataId=Wall_E_item_sensation_present.getDataId())
        # make potential response
        voice_sensation2 = self.createSensation(
                                                sensationName='voice_sensation2',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTestCase.VOICEDATA2,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation2.isForgettable())
        self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
        
        image_sensation2 = self.createSensation(
                                                sensationName='image_sensation2',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.assertTrue(image_sensation2.isForgettable())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        
        item_sensation2 = self.createSensation(
                                                sensationName='item_sensation2',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(item_sensation2.isForgettable())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        item_sensation2.associate(sensation=voice_sensation2)
        item_sensation2.associate(sensation=image_sensation2)
        voice_sensation2.associate(sensation=image_sensation2)

        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (and be assigned as self.association) with with  name and associations count
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 1, 'len(robot.getMemory().getAllPresentItemSensations() should be 1')
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present)
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 1, 'len(robot.getMemory().getAllPresentItemSensations() should be 1')

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            self.expect(isWait=isWait,
                        name='isPresentRobot Present, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation2, isExactMuscleImage=True,
                        muscleVoice=voice_sensation2, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_present, isExactCommunicationItem=True)
            # To test other Communication Robots functionality we must make a trick and change this Sensation ocatio
            # so this Robot think that Sensation comes fromother Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Present, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation2, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation2, isExactCommunicationVoice=True,
                        communicationItem=None)        # TODO remove this, it is not valid any more
        else:  
            self.expect(isWait=isWait,
                        name='Present, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation2, isExactMuscleImage=True,
                        muscleVoice=voice_sensation2, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)


        # We should remove remote Robot Item-presence to test this local Absent feature
        if isPresentRobot and Robot.GLOBAL_LOCATION in robot.getMemory()._presentItemSensations:
            del robot.getMemory()._presentItemSensations[Robot.GLOBAL_LOCATION]
        

        
        print('\n current Absent {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation_absent = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent test', dataId=Wall_E_item_sensation_absent.getDataId())
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 0, 'len(robot.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 0')

        #process              
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 0, 'len(robot.getMemory().getAllPresentItemSensations() should be 0')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        self.expect(isWait=isWait,
                    name='Absent', isEmpty=False, #isSpoken=False, isHeard=False,
                    isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
        
 
        # NAME with NAME2
        
        print('\n NAME current Entering {}',format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation3 = self.createSensation(
                                                sensationName='voice_sensation3',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTestCase.VOICEDATA3,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation3 test', dataId=voice_sensation3.getDataId())
        image_sensation3 = self.createSensation(
                                                sensationName='image_sensation3',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation3 test', dataId=image_sensation3.getDataId())
        item_sensation3 = self.createSensation(
                                                sensationName='item_sensation3',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation3 test', dataId=item_sensation3.getDataId())
        item_sensation3.associate(sensation=voice_sensation3)
        item_sensation3.associate(sensation=image_sensation3)
        voice_sensation3.associate(sensation=image_sensation3)
        
        # make entering item and process
        Wall_E_item_sensation_entering3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering3',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_entering3 test', dataId=Wall_E_item_sensation_entering3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 1, 'len(robot.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 1')

        #process                      
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering3)
                        
        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 3', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation3, isExactMuscleImage=True,
                        muscleVoice=voice_sensation3, isExactMuscleVoice=True,
                        communicationItem=Wall_E_item_sensation_entering3, isExactCommunicationItem=True)
            # To test other Communication Robots functionality we must make a trick and change this Sensation ocatio
            # so this Robot think that Sensation comes from other Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Present, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation3, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation3, isExactCommunicationVoice=True,
                        communicationItem=None)        # TODO remove this, it is not valid any more
        else:  
            self.expect(isWait=isWait,
                        name='Entering, response 3', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation3, isExactMuscleImage=True,
                        muscleVoice=voice_sensation3, isExactMuscleVoice=True,)
            

        
        print('\n NAME2 current Entering {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation4 = self.createSensation(
                                                sensationName='voice_sensation4',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation4 test', dataId=voice_sensation4.getDataId())
        image_sensation4 = self.createSensation(
                                                sensationName='image_sensation4',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation4 test', dataId=image_sensation4.getDataId())
        item_sensation4 = self.createSensation(
                                                sensationName='image_sensation4',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation4 test', dataId=item_sensation4.getDataId())
        item_sensation4.associate(sensation=voice_sensation4)
        item_sensation4.associate(sensation=image_sensation4)
        voice_sensation4.associate(sensation=image_sensation4)
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 2, 'len(robot.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 2')

        # make entering and process
        Wall_E_item_sensation_entering4 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering4',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_entering4 test', dataId=Wall_E_item_sensation_entering4.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        # other entering is handled as response
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 2, 'len(robot.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 2')


        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering4)
        
        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            self.expect(isWait=isWait,
                        name='isPresentRobot Name2 entering, response 4', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation4, isExactMuscleImage=True,
                        muscleVoice=voice_sensation4, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_entering4, isExactCommunicationItem=True)
            # To test other Communication Robots functionality we must make a trick and change this Sensation ocatio
            # so this Robot think that Sensation comes fromother Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Name2 enteringt, reply to communicationItem, response 4', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation4, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation4, isExactCommunicationVoice=True,
                        communicationItem=None)
        else:  
            self.expect(isWait=isWait,
                        name='Name2 entering , response 4', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation4, isExactMuscleImage=True,
                        muscleVoice=voice_sensation4, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)

        print('\n NAME2 current Present {}'.format(CommunicationTestCase.NAME2))
        # added make potential response
        voice_sensation5 = self.createSensation(
                                                sensationName='voice_sensation5',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation5 test', dataId=voice_sensation5.getDataId())
        image_sensation5 = self.createSensation(
                                                sensationName='image_sensation5',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation5 test', dataId=image_sensation5.getDataId())
        item_sensation5 = self.createSensation(
                                                sensationName='item_sensation5',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation5 test', dataId=item_sensation5.getDataId())
        item_sensation5.associate(sensation=voice_sensation5)
        item_sensation5.associate(sensation=image_sensation5)
        voice_sensation5.associate(sensation=image_sensation5)

        Wall_E_item_sensation_present2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present2',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present2 test', dataId=Wall_E_item_sensation_present2.getDataId())

        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present2)
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 2, 'len(robot.getMemory().getAllPresentItemSensations() should be 2')

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            self.expect(isWait=isWait,
                        name='isPresentRobot Name2 present, response 5', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation5, isExactMuscleImage=True,
                        muscleVoice=voice_sensation5, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_present2, isExactCommunicationItem=True)
            # To test other Communication Robots functionality we must make a trick and change this Sensation ocatio
            # so this Robot think that Sensation comes fromother Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Name2 enteringt, reply to communicationItem, response 5', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation5, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation5, isExactCommunicationVoice=True,
                        communicationItem=None)
        else:  
            self.expect(isWait=isWait,
                        name= "Name2 present, response 5", isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation5, isExactMuscleImage=True,
                        muscleVoice=voice_sensation5, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)
           

        print('\n NAME2 current Present again {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation6 = self.createSensation(
                                                sensationName='voice_sensation6',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation6 test', dataId=voice_sensation6.getDataId())
        image_sensation6 = self.createSensation(
                                                sensationName='image_sensation6',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation6 test', dataId=image_sensation6.getDataId())
        item_sensation6 = self.createSensation(
                                                sensationName='item_sensation6',
                                                robot=robot,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation6 test', dataId=item_sensation6.getDataId())
        item_sensation6.associate(sensation=voice_sensation6)
        item_sensation6.associate(sensation=image_sensation6)
        voice_sensation6.associate(sensation=image_sensation6)

        Wall_E_item_sensation_present3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present3',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present3 test', dataId=Wall_E_item_sensation_present3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot

        # do we have Robots present
        if isPresentRobot:
            communicationItem=Wall_E_item_sensation_present3
            isExactCommunicationItem=True
        else:
            communicationItem=None
            isExactCommunicationItem=False
       
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present3)
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 2, 'len(robot.getMemory().getAllPresentItemSensations() should be 2')

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            self.expect(isWait=isWait,
                        name='isPresentRobot Name2 present, response 6', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation6, isExactMuscleImage=True,
                        muscleVoice=voice_sensation6, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_present3, isExactCommunicationItem=True)
            # To test other Communication Robots functionality we must make a trick and change this Sensation ocatio
            # so this Robot think that Sensation comes fromother Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Name2 present, reply to communicationItem, response 6', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation6, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation6, isExactCommunicationVoice=True,
                        communicationItem=None)
        else:  
            self.expect(isWait=isWait,
                        name= "Name2 present, response 6", isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation6, isExactMuscleImage=True,
                        muscleVoice=voice_sensation6, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)
            
            

        # We should remove remote Robot Item-presence to test this local Absent feature
        if isPresentRobot and Robot.GLOBAL_LOCATION in robot.getMemory()._presentItemSensations:
            del robot.getMemory()._presentItemSensations[Robot.GLOBAL_LOCATION]
        
        print('\n NAME2 current Absent {}'.format(CommunicationTestCase.NAME2))
        Wall_E_item_sensation_absent2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent2',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent2 test', dataId=Wall_E_item_sensation_absent2.getDataId())
       
        #simulate TensorFlowClassification send presence item to MainRobot
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent2)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 1, 'len(robot.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(isWait=isWait,
                    name='Absent NAME2', isEmpty=False, #isSpoken=False, isHeard=False,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isNegativeFeeling=True)
    

        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation_absent3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent3',
                                                robot=robot,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent3 test', dataId=Wall_E_item_sensation_absent3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot       
        robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent3)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 0, 'len(robot.getMemory().getAllPresentItemSensations() should be 0')
        self.expect(isWait=isWait,
                    name='Absent NAME', isEmpty=True)#isSpoken=False, isHeard=False, isVoiceFeeling=False)
       

    '''
    TensorfloClassification produces
    Item.name Working Out
    Sensations outside Robot are in same Robot.mainNames and robotType=Sensation.RobotType.Sense
    so this test is same than without paramweters
    '''    
    def test_2_Presense(self):
        self.do_test_Presense(mainNames=self.MAINNAMES, robotType=Sensation.RobotType.Sense)
        
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in other Robot.mainNames and robotType=Sensation.RobotType.Communication
    so this test result should  same than with test where robotType=Sensation.RobotType.Sense,
    because Communication should handle those sensation equally, when Robot.mainNames differ
    '''    
    def test_3_Presense(self):
        self.do_test_Presense(mainNames=self.OTHERMAINNAMES, robotType=Sensation.RobotType.Communication)

    '''
    TensorfloClöassafication produces
    Item.name Working Out
    
    At his moment only TenserflowClassification creates SEnsationType.Item presense
    Sensations and RobotType is always Sense. Test same way
    
    TODO This test logic is obsolote, because we don't get Presence items repeated, but
    Present and the Absent and so on.
    
    '''    
    def do_test_Presense(self, mainNames, robotType):
        print('\ndo_test_Presense {} {}'.format(mainNames, robotType))

        # robot setup  
        # TODO is this needed, because we don't use to create Sensations
        for sensation in self.communication.getMemory().getAllPresentItemSensations():
            print("Present name {}".format(sensation.getName()))        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')
      
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Entering {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation1 = self.createSensation(
                                                sensationName='Wall_E_item_sensation1',
                                                robot=self.communication,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation1 test', dataId=Wall_E_item_sensation1.getDataId())
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation1)
        # We get Voice, if Communication can respond but it can't
        for sensation in self.communication.getMemory().getAllPresentItemSensations():
            print("Entering, Too old response after process, Present name {}".format(sensation.getName()))
        for location in self.communication.getMemory()._presentItemSensations.keys():
            for itemSensation in self.communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        self.expect(name='Entering, Too old response', isEmpty=True)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 1')

        # remove this one
        absent_item_sensation1 = self.createSensation(
                                                sensationName='absent_item_sensation1',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='absent_item_sensation1 test', dataId=absent_item_sensation1.getDataId())

        for sensation in self.communication.getMemory().getAllPresentItemSensations():
            print("absent1 after process, Present name {}".format(sensation.getName()))
        for location in self.communication.getMemory()._presentItemSensations.keys():
            for itemSensation in self.communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=absent_item_sensation1)

        # TODO enable and reimplement next line, because 
        # heardDataIds is location based now       
        #self.assertEqual(len(self.communication.heardDataIds), 0)
        # We get Voice, if Communication can respond but it can't
        self.expect(name='absent1', isEmpty=True)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 0')

        
              
        print('\n current Entering {}'.format(CommunicationTestCase.NAME))
        # make potential response
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        
        for sensation in self.communication.getMemory().getAllPresentItemSensations():
            print("absent1 after process, Present name {}".format(sensation.getName()))
        for location in self.communication.getMemory()._presentItemSensations.keys():
            for itemSensation in self.communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=item_sensation1)
        # We get Voice, if Communication can respond but it can't
        self.expect(name='current Entering', isEmpty=True)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 0')
       
         # We hear voice and see image
        voice_sensation1 = self.createSensation(
                                                sensationName='voice_sensation1',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTestCase.VOICEDATA2,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation1 test', dataId=voice_sensation1.getDataId())
        self.assertEqual(len(item_sensation1.getAssociations()), 2)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation1)
        # TODO enable and reimplement next 2 lines, because 
        # heardDataIds is location based now       
#         self.assertEqual(len(self.communication.heardDataIds), 1)
#         self.assertEqual(self.communication.heardDataIds[0], voice_sensation1.getDataId())
        # We get Voice, if Communication can respond but it can't, we hear it in this discussion
        self.expect(name='voice_sensation1', isEmpty=True)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 0')
        
 
        # TODO We don't get SensationType.Image from Item.name (==person)
        # so this test is very obsolete
        # remove test? 
        image_sensation1 = self.createSensation(
                                                sensationName='image_sensation1',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation1 test', dataId=image_sensation1.getDataId())
        self.assertEqual(len(item_sensation1.getAssociations()), 3)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=image_sensation1)
        # TODO enable and reimplement next 3 lines, because 
        # heardDataIds is location based now
        if robotType == Sensation.RobotType.Sense:   
            self.assertEqual(len(self.communication.itemConversations[self.getLocations()[0]].heardDataIds), 1, 'self.getLocations(self.communication.itemConversations[{}].heardDataIds)'.format(self.getLocations()))
            self.assertEqual(self.communication.itemConversations[self.getLocations()[0]].heardDataIds[0], voice_sensation1.getDataId())
        # We get Voice, if Communication can respond but it can't, we hear it in this discussion
        self.expect(name='image_sensation1', isEmpty=True)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 0')
 
        # Absent
        # remove this one
        absent_item_sensation2 = self.createSensation(
                                                sensationName='absent_item_sensation2',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='absent_item_sensation2 test', dataId=absent_item_sensation2.getDataId())

        for sensation in self.communication.getMemory().getAllPresentItemSensations():
            print("absent1 after process, Present name {}".format(sensation.getName()))
        for location in self.communication.getMemory()._presentItemSensations.keys():
            for itemSensation in self.communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))
        self.assertFalse(self.communication.getMemory().hasItemsPresence(), 'should not have presence')

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=absent_item_sensation2)
        # TODO enable and reimplement next line, because 
        # heardDataIds is location based now       
#         self.assertEqual(len(self.communication.heardDataIds), 0)
        
        # We get Voice, if Communication can respond but it can't
        self.expect(name='absent1', isEmpty=True)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 0')
        
        # Now we have heard something when CommunicationTestCase.NAME was present       
        # We have present item
        
        Wall_E_item_sensation2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation2',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation2 test', dataId=Wall_E_item_sensation2.getDataId())
        self.assertEqual(len(Wall_E_item_sensation1.getAssociations()), 1)
        self.assertEqual(len(item_sensation1.getAssociations()), 3) # 1
        self.assertEqual(len(Wall_E_item_sensation2.getAssociations()), 1)
        
        for sensation in self.communication.getMemory().getAllPresentItemSensations():
            print("Wall_E_item_sensation2 before process, Present name {}".format(sensation.getName()))
        for location in self.communication.getMemory()._presentItemSensations.keys():
            for itemSensation in self.communication.getMemory()._presentItemSensations[location].values():
                print("Wall_E_item_sensation2 before process present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        
        #simulate TensorFlowClassification send presence item to MainRobot
        # should still have only CommunicationTestCase.NAME present
        
        # process
        print("process Wall_E_item_sensation2")
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation2)
        #  we will get response and 4 associations are created more
        self.assertEqual(len(Wall_E_item_sensation1.getAssociations()), 1)
        print("\nitem_sensation1.getAssociations() {}\n".format(len(item_sensation1.getAssociations())))
        self.assertTrue(len(item_sensation1.getAssociations()) == 3 or\
                         len(item_sensation1.getAssociations()) == 5 or\
                         len(item_sensation1.getAssociations()) == 7 or\
                         len(item_sensation1.getAssociations()) == 11) #3/5/7/11
        self.assertTrue(len(Wall_E_item_sensation2.getAssociations()) == 1 or\
                        len(Wall_E_item_sensation2.getAssociations()) == 3 or\
                        len(Wall_E_item_sensation2.getAssociations()) == 5 or\
                        len(Wall_E_item_sensation2.getAssociations()) == 9) #1/3/5/9

        # We can use   image_sensation1,   voice_sensation1 after Absent   
        self.expect(name='Wall_E_item_sensation2', isEmpty=False,
                    muscleImage=image_sensation1, isExactMuscleImage=True,
                    muscleVoice=voice_sensation1, isExactMuscleVoice=True)
        # No communication robot
#                     communicationImage=image_sensation1, isExactCommunicationImage=True,
#                     communicationVoice=voice_sensation1, isExactCommunicationVoice=True)
        
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation3',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation3 test', dataId=Wall_E_item_sensation3.getDataId())

        self.assertEqual(len(Wall_E_item_sensation1.getAssociations()), 1) # present in location ''
        self.assertTrue(len(Wall_E_item_sensation2.getAssociations()) == 1 or\
                        len(Wall_E_item_sensation2.getAssociations()) == 3 or\
                        len(Wall_E_item_sensation2.getAssociations()) == 5)
        self.assertEqual(len(Wall_E_item_sensation3.getAssociations()), 1)
        self.assertTrue(len(item_sensation1.getAssociations()) == 3 or\
                        len(item_sensation1.getAssociations()) == 5 or\
                        len(item_sensation1.getAssociations()) == 7 )         # present in testlocation , added +1
        self.assertEqual(len(image_sensation1.getAssociations()), 2)
        self.assertEqual(len(voice_sensation1.getAssociations()), 2)
       
        #simulate TensorFlowClassification send presence item to MainRobot
        # should still have only CommunicationTestCase.NAME present
        
        for location in self.communication.getMemory()._presentItemSensations.keys():
            for itemSensation in self.communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
       
        
        # added
        # make potential response
        item_sensation2 = self.createSensation(
                                                sensationName='item_sensation2',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation2 test', dataId=item_sensation2.getDataId())
        self.assertEqual(len(item_sensation2.getAssociations()), 1)
        
        voice_sensation2 = self.createSensation(
                                                sensationName='voice_sensation2',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTestCase.VOICEDATA2,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
        self.assertEqual(len(voice_sensation2.getAssociations()), 2)
        self.assertEqual(len(item_sensation2.getAssociations()), 2)
        
        image_sensation2 = self.createSensation(
                                                sensationName='image_sensation2',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        self.assertEqual(len(image_sensation2.getAssociations()), 2)
        self.assertEqual(len(item_sensation2.getAssociations()), 3)
        
#         item_sensation2.associate(sensation=voice_sensation2)
#         item_sensation2.associate(sensation=image_sensation2)
#         voice_sensation2.associate(sensation=image_sensation2)

        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation3) # presence
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        # process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation3)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        self.expect(name='Present, response', isEmpty=False,
                    # TODO ??? should not get these
                    muscleImage=image_sensation2, isExactMuscleImage=True,
                    muscleVoice=voice_sensation2, isExactMuscleVoice=True,
#                     communicationImage=image_sensation2, isExactCommunicationImage=True,
#                     communicationVoice=voice_sensation2, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)

        
        print('\n current Absent {}'.format(CommunicationTestCase.NAME))        
        
        Wall_E_item_sensation4 = self.createSensation(
                                                sensationName='Wall_E_item_sensation4',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation4 test', dataId=Wall_E_item_sensation4.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 1')

        #process              
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation4)
        # TODO enable and reimplement next line, because 
        # heardDataIds is location based now       
#         self.assertEqual(len(self.communication.heardDataIds), 0)

        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        self.expect(name='Absent', isEmpty=False, isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
        
        # conversation should be ended, when lst Iten is absent
        for location in self.communication.getLocations():
            self.assertEqual(len(self.communication.itemConversations[location].spokedDataIds),0)
            self.assertEqual(len(self.communication.itemConversations[location].heardDataIds),0)
        
 
        # NAME with NAME2
        
        # should wait here for conversation delay
        
        print('\n NAME current Entering {}',format(CommunicationTestCase.NAME))
        # make potential response
        currentEnteringVoiceSensation = self.createSensation(
                                                sensationName='currentEnteringVoiceSensation',
                                                robot=self.communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTestCase.VOICEDATA3,
                                                locations=self.getLocations())
        self.printSensationNameById(note='currentEnteringVoiceSensation test', dataId=currentEnteringVoiceSensation.getDataId())
        currentEnteringImageSensation = self.createSensation(
                                                sensationName='currentEnteringImageSensation',
                                                robot=self.communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='currentEnteringImageSensation test', dataId=currentEnteringImageSensation.getDataId())
        item_sensation3 = self.createSensation(
                                                sensationName='item_sensation3',
                                                robot=self.communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,                                                
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation3 test', dataId=item_sensation3.getDataId())
#         item_sensation3.associate(sensation=currentEnteringVoiceSensation)
#         item_sensation3.associate(sensation=currentEnteringImageSensation)
#         currentEnteringVoiceSensation.associate(sensation=currentEnteringImageSensation)
        
        # make entering item and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation5 = self.createSensation(
                                                sensationName='Wall_E_item_sensation5',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation5 test', dataId=Wall_E_item_sensation5.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation5) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 2')

        #  We are starting new conversation so there should not be spokedDataIds or heardDataIds
        for location in self.communication.getLocations():
            self.assertEqual(len(self.communication.itemConversations[location].spokedDataIds),0)
            self.assertEqual(len(self.communication.itemConversations[location].heardDataIds),0)

        #process                      
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation5)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
       # TODO What we expect is #1 sensations, but we get currentEnteringVoiceSensation, image_sensation1
        self.expect(name='Present Name 2, new Conversation starts', isEmpty=False,
                    muscleImage=currentEnteringImageSensation, isExactMuscleImage=False,
                    muscleVoice=currentEnteringVoiceSensation, isExactMuscleVoice=False)
#                     communicationImage=currentEnteringImageSensation, isExactCommunicationImage=False,
#                     communicationVoice=currentEnteringVoiceSensation, isExactCommunicationVoice=False)
        
        print('\n NAME2 current Entering {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        
        Eva_item_sensation = self.createSensation(
                                                sensationName='Eva_item_sensation',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
        
        Eva_voice_sensation = self.createSensation(
                                                sensationName='Eva_voice_sensation',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_voice_sensation test', dataId=Eva_voice_sensation.getDataId())
        Eva_image_sensation = self.createSensation(
                                                sensationName='Eva_image_sensation',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_image_sensation test', dataId=Eva_image_sensation.getDataId())
#         Eva_item_sensation.associate(sensation=Eva_voice_sensation)
#         Eva_item_sensation.associate(sensation=Eva_image_sensation)
#         Eva_voice_sensation.associate(sensation=Eva_image_sensation)
        #simulate TensorFlowClassification send presence item to MainRobot
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 3')

        # make entering and process
        Wall_E_item_sensation6 = self.createSensation(
                                                sensationName='Wall_E_item_sensation6',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation6 test', dataId=Wall_E_item_sensation6.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 3')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation6)
        self.expect(name='Entering Name2, change in presentation', isEmpty=False,
                    muscleImage=Eva_image_sensation, isExactMuscleImage=True,
                    muscleVoice=Eva_voice_sensation, isExactMuscleVoice=True,
#                     communicationImage=Eva_image_sensation, isExactCommunicationImage=True,
#                     communicationVoice=Eva_voice_sensation, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        print('\n NAME2 current Present {}'.format(CommunicationTestCase.NAME2))
        # added make potential response
        Eva_item_sensation = self.createSensation(
                                                sensationName='Eva_item_sensation',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,                                                
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
        Eva_voice_sensation = self.createSensation(
                                                sensationName='Eva_voice_sensation',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_voice_sensation test', dataId=Eva_voice_sensation.getDataId())
        Eva_image_sensation = self.createSensation(
                                                sensationName='Eva_image_sensation',
                                                robot=self.communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_image_sensation test', dataId=Eva_image_sensation.getDataId())

        Wall_E_item_sensation7 = self.createSensation(
                                                sensationName='Wall_E_item_sensation7',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,                                                
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation7 test', dataId=Wall_E_item_sensation7.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation7)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 3')
        self.expect(name='Present Name 2, change in presentation', isEmpty=False,
                    muscleImage=Eva_image_sensation, isExactMuscleImage=True,
                    muscleVoice=Eva_voice_sensation, isExactMuscleVoice=True,
#                     communicationImage=Eva_image_sensation, isExactCommunicationImage=True,
#                     communicationVoice=Eva_voice_sensation, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)

        print('\n NAME2 current Present again {}'.format(CommunicationTestCase.NAME2))
        # make potential response to history
        # Note, this is right way to do so, correct test above
        # time change changes what we will get so take your time to correct test
        Eva_voice_sensation2 = self.createSensation(
                                                sensationName='Eva_voice_sensation2',
                                                robot=self.communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                data=CommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_voice_sensation2 test', dataId=Eva_voice_sensation2.getDataId())
        Eva_image_sensation2 = self.createSensation(
                                                sensationName='Eva_image_sensation2',
                                                robot=self.communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                mainNames=mainNames,
                                                robotType=robotType,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_image_sensation2 test', dataId=Eva_image_sensation2.getDataId())
        Eva_item_sensation = self.createSensation(
                                                sensationName='Eva_item_sensation',
                                                robot=self.communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_3,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
        Eva_item_sensation.associate(sensation=Eva_voice_sensation2, feeling = Sensation.Feeling.Good)
        Eva_item_sensation.associate(sensation=Eva_image_sensation2, feeling = Sensation.Feeling.Good)
        Eva_voice_sensation2.associate(sensation=Eva_image_sensation2, feeling = Sensation.Feeling.Good)

        Wall_E_item_sensation8 = self.createSensation(
                                                sensationName='Wall_E_item_sensation8',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation8 test', dataId=Wall_E_item_sensation8.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation8)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 3')
        # We don't get any Communication Sensations, becuse response limit is expected
        # TODO Communication Sensation functionality will be changed
        self.expect(name='Present NAME2 again basic change in presentation', isEmpty=False,
                    muscleImage=Eva_image_sensation2, isExactMuscleImage=True,
                    muscleVoice=Eva_voice_sensation2, isExactMuscleVoice=True,
#                     communicationImage=Eva_image_sensation2, isExactCommunicationImage=True,
#                     communicationVoice=Eva_voice_sensation2, isExactCommunicationVoice=True,
                    communicationImage=None,
                    communicationVoice=None,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        print('\n NAME2 current Absent {}'.format(CommunicationTestCase.NAME2))
        Wall_E_item_sensation9 = self.createSensation(
                                                sensationName='Wall_E_item_sensation9',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTestCase.NAME2,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation9 test', dataId=Wall_E_item_sensation9.getDataId())
       
        #simulate TensorFlowClassification send presence item to MainRobot

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation9)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        self.expect(name='Absent NAME2', isEmpty=False,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isNegativeFeeling=True)
    

        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation10 = self.createSensation(
                                                sensationName='Wall_E_item_sensation10',
                                                robot=self.communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTestCase.NAME,
                                                score=CommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation10 test', dataId=Wall_E_item_sensation10.getDataId())
       #simulate TensorFlowClassification send presence item to MainRobot
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation10)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(name='Absent NAME', isEmpty=True)
       


    '''
    deprecated
    Robot's don't communicate each other, but consult each other
    
    Here we test Communication with other Robot
    
    Sensations should be created to tested Robot (self.commununication) memory.
    
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
    
    If Item.name heard Robot to speak, it reacts and starts to speak out 
    
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
        
    def deprecated_test_ProcessItemImageVoiceFromOtherRobot(self):
        # responses
        # - come from mainNames=self.OTHERMAINNAMES
        # - are marked as robotType=Sensation.RobotType.Communication
        #
        # but Communication should handle these responses as person said,
        # Microphone detects as Sense type Voices in same mainNames
        print('\ntest_ProcessItemImageVoiceFromOtherRobot\n')
        self.do_test_ProcessItemImageVoice(mainNames=self.OTHERMAINNAMES,
                                           robotType=Sensation.RobotType.Communication)
        
        
    def test_ProcessItemImageVoiceFromSameRobotSenses(self):
        #responses
        # - come from mainNames=self.OTHERMAINNAMES
        # - are marked as robotType=Sensation.RobotType.Muscle
        #
        # but Communication should handle these responses as person said,
        # Microphone detects as Sense type Voices in same mainNames
        print('\ntest_ProcessItemImageVoiceFromSameRobotSenses\n')
        self.do_test_ProcessItemImageVoice(mainNames=self.MAINNAMES,
                                           robotType=Sensation.RobotType.Sense)
        
    '''
    do_test_ProcessItemImageVoice is helper method to test main functionality
    of Communication-Robot.
    
    It takes three parameters that define other part Communication is
    communicating. With these parameters we can define person or other Robot.
    - mainNames
    - robotType
    
    Test logic:
    Sensations should be created to tested Robot (self.commununication) memory.
    
    prepare:
    Create elf.Wall_E_item_sensation.
    Create 3 voices and images into  memory,
    associated to self.Wall_E_item_sensation
    and each other.

    test:
    Once
    1) create item Sensation presence
    2) local Communication.process(item)
    
    Many times
    3) Expect to get Image and Voice Sensations from local Communication
       from memory. First we get best responses, then second best etc
    4) We respond with Voice
    
       Because do so many responses in test part (this app),
       finally we 
    5) Expect to get Image and Voice Sensations from local Communication
       that are our first responses, because Communication logic allows
       to use heard responses from other part of communication, if they are
       not last ones.
    6) If this was not not first response, we will get also positive Feeling
       sensations to previous used voices and Images, because those previous
       ones got responses.
       
    7) Finally Communication has used its Memory responses and can't use
       other part heard responses any more, because they are too new
       so we get negative feeling Feeling to Communication last response.

    We test also that Communication send Item.presnce/Absent when its methods
    initRobot/deInitRobot is called.
    
    This test does not test Communication as process, so all methods from
    Communication should be called directly.

    
    ''' 
        
    def do_test_ProcessItemImageVoice(self, mainNames, robotType):#, memoryType):
        print('\ndo_test_ProcessItemImageVoice\n')
        
        ########################################################################################################
        # Prepare part
        
        memoryType=Sensation.MemoryType.Working
        
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        Wall_E_item_sensation = self.createSensation(robot=self.communication,
                                                     sensationName= 'Wall_E_item_sensation',
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=Sensation.RobotType.Sense,
                                                     name=CommunicationTestCase.NAME,
                                                     score=CommunicationTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Present,
                                                     locations=self.getLocations())

        allPresentItemSensations = self.communication.getMemory().getAllPresentItemSensations()
        
        self.assertEqual(len(allPresentItemSensations), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.assertEqual(allPresentItemSensations[0], Wall_E_item_sensation, 'allPresentItemSensations[0] should be Wall_E_item_sensation')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
                
        # self.communication 1. response
        # Voice, 2. best
        Wall_E_voice_sensation_1 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_1',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA5,
                                                    feeling = CommunicationTestCase.BETTER_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_1, feeling = CommunicationTestCase.BETTER_FEELING)
        
        # self.communication 1. response
        # 1. Image, 2. best
        Wall_E_image_sensation_1 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_1',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA5,
                                                    feeling = CommunicationTestCase.BETTER_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_1, feeling = CommunicationTestCase.BETTER_FEELING)
                
        # self.communication 2. response
        # Voice, 1. best
        Wall_E_voice_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_2',
                                                    robot=self.communication,
                                                    time=history_sensationTime,                                                        
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA6,
                                                    feeling = CommunicationTestCase.BEST_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_2, feeling = CommunicationTestCase.BEST_FEELING)
        # self.communication 2. response
        # Image, 1. best
        Wall_E_image_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_2',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA6,
                                                    feeling = CommunicationTestCase.BEST_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_2, feeling = CommunicationTestCase.BEST_FEELING)

        # self.communication 3. response
        # Voice, 3. best
        Wall_E_voice_sensation_3 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_3',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA7,
                                                    feeling = CommunicationTestCase.NORMAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_3, feeling = CommunicationTestCase.NORMAL_FEELING)

        # self.communication 3. response
        # Image, 3. best
        Wall_E_image_sensation_3 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_3',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA7,
                                                    feeling = CommunicationTestCase.NORMAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_3, feeling = CommunicationTestCase.NORMAL_FEELING)
        
        
        # self.communication 4. response
        # Voice, 4. best
        Wall_E_voice_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_4',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA7,
                                                    feeling = CommunicationTestCase.NEUTRAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_4, feeling = CommunicationTestCase.NEUTRAL_FEELING)
        # self.communication 4. response
        # Image, 4. best
        Wall_E_image_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_4',
                                                    robot=self.communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA7,
                                                    feeling = CommunicationTestCase.NEUTRAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_4, feeling = CommunicationTestCase.NEUTRAL_FEELING)
        


        ########################################################################################################
        ## test part
        # simulate that we have started Communication-Robot and all Robots get Item-sensation that it is present
        
        self.communication.initRobot()
        self.expect(name='initRobot',
                    isEmpty=False,
                    #isItem=True,
                    communicationItem=self.technicalSensation) # will get other sensation
                
        #image and Item from Sense, which has other MainNames
        # simulate item and image are connected each other with TensorflowClassifivation
        Wall_E_item_sense_sensation = self.createSensation(
                                                 sensationName='Wall_E_item_sense_sensation',
                                                 robot=self.communication,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,# TOdo Item is always Sense, not robotType
                                                 name=CommunicationTestCase.NAME,
                                                 associations=[],
                                                 presence=Sensation.Presence.Present,
                                                 mainNames=mainNames,
                                                 locations=self.getLocations())

        #self.logCommunicationState(note='before process Starting conversation, get best voice and image')
        #Item is Present, process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sense_sensation)
        # should get just best Voice and Image
        self.expect(name='Starting conversation, get best voice and image',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_2, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_2, isExactMuscleVoice=True)
                    # we don't have other side commicationg Robot
#                     communicationImage=Wall_E_image_sensation_2, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_2, isExactCommunicationVoice=True)
        
        
        # now other conversation part Robot or person responds with voice
        Wall_E_sense_voice_response_sensation = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA8,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
       
        Wall_E_sense_voice_response_sensation.associate(sensation=Wall_E_item_sense_sensation)
        #self.logCommunicationState(note='before process response, second best voice')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation)
        # should get second best voice, image and positive feelings to 1. responses
        self.expect(name='response, second best voice, image',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_1, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_1, isExactMuscleVoice=True,
#                     communicationImage=Wall_E_image_sensation_1, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_1, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        # TODO enable and reimplement next line, because 
        # heardDataIds is location based now       
#         self.assertTrue(Wall_E_sense_voice_response_sensation.getDataId() in self.communication.heardDataIds)
        
        # 2. response from other side communication
        Wall_E_sense_voice_response_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_2',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
        #self.logCommunicationState(note='before process response, third best voice, image')
        # process, should get third best voice, image and positive feelings to previous responses   
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_2)
        self.expect(name='response, third best voice, image',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_3, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_3, isExactMuscleVoice=True,
#                     communicationImage=Wall_E_image_sensation_3, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_3, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        

        # response 3 from other side communication
        Wall_E_sense_voice_response_sensation_3 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_3',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
        #self.logCommunicationState(note='before process response, old responsed voice, response furth bestimage')
        # process, should get fourth best image, voice and positive feelings to previous responses
        # at this point Wall_E_sense_voice_response_sensation is better than Wall_E_image_sensation_4
        # because Wall_E_image_sensation_4 feeling was low
        # We get also positive feeling to revious responses.
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_3)
        # TODO WE will not get Communication Sensations, because limit is exceeded
        # But Communication implementation will be changed
        self.expect(name='response, response voice, fourth best image, voice',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_4, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_4, isExactMuscleVoice=True,#Wall_E_sense_voice_response_sensation_3, isExactMuscleVoice=False, #self.Eva_voice_sensation
#                     communicationImage=Wall_E_image_sensation_4, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_4, isExactCommunicationVoice=True,#self.Eva_voice_sensation
                    communicationImage=None,
                    communicationVoice=None,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        
        Wall_E_sense_voice_response_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_4',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
        Wall_E_item_sensation.associate(sensation=Wall_E_sense_voice_response_sensation_4, feeling = CommunicationTestCase.NEUTRAL_FEELING)
        
        #self.logCommunicationState(note='before process response, Wall_E_sense_voice_response_sensation, no image')
         # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_4)
        # at this point Communication has used all sensations in the memory but
        # it can use responses: Wall_E_sense_voice_response_sensation_2
        # This side has not responded with images, so we should not get image.
        # should get Voice and a Feeling between Voice and Item
        # Voice should be already spoken Voice, but not last one, so it would be Wall_E_sense_voice_response_sensation_2, which is dropped fron heard voices
        # We get also positive feeling to revious responses.
        
        # We don't find responses, because all voices and Images are used and
        # using heard voices, images does not work
        # TODO enable this with subclass
        #self.assertTrue(self.communication._isNoResponseToSay)
        self.expect(name='response, Wall_E_sense_voice_response_sensation, no image',
                    isEmpty=False,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True
                    )
                
        
        
        # communication has used all its voices,but we make other side to spoeak
        #  so at least communication can use its voice, which it is heard
        # wait some time
        
        # TODO diosable this tand enable commented test below
        # Without that we don't get here anything, so expext empty
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")       
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='Empty',
                    isEmpty=True)
        

        # TODO enable and reimplement next lines, because 
        # heardDataIds is location based now       
#         print("\nSTo remove known first reply from self.communication.heardDataIds send replyes to communication untis its first reply is available")        
#         j = 0        
#         i = 5 # for numbering
#         while Wall_E_sense_voice_response_sensation.getDataId() in self.communication.heardDataIds and j < Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
#         # response 4 from other side communication
#             Wall_E_sense_voice_response_sensation_extra = self.createSensation(
#                                                         sensationName='Wall_E_sense_voice_response_sensation_{}'.format(i),
#                                                         robot=self.communication,
#                                                         memoryType=Sensation.MemoryType.Sensory,
#                                                         sensationType=Sensation.SensationType.Voice,
#                                                         robotType=robotType,
#                                                         data=CommunicationTestCase.VOICEDATA9,
#                                                         locations=self.getLocations(),
#                                                         mainNames=mainNames)
#             Wall_E_item_sensation.associate(sensation=Wall_E_sense_voice_response_sensation_extra, feeling = CommunicationTestCase.NEUTRAL_FEELING)
#             
#             #self.logCommunicationState(note='before process response, Wall_E_sense_voice_response_sensation, no image')
#              # process
#             self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_extra)
# 
#             # same conversation keep going on, even if we don't find anythoing to say            
#             self.assertTrue(self.communication._isConversationOn)
#             self.assertFalse(self.communication._isConversationEnded)
#             self.assertFalse(self.communication._isConversationDelay)
#             # if communication could not response, dont cara
#             if self.communication._isNoResponseToSay:
#                 while not self.getAxon().empty():
#                     tranferDirection, sensation = self.getAxon().get(robot=self)
#                     print("\n{} To remove known first reply from self.communication.heardDataIds got sensation {}".format(j,sensation.toDebugStr()))
#     
#                 i=i+1
#                 j=j+1
#             else:
#                 self.expect(name='response, Wall_E_sense_voice_response_sensation, no image',
#                             isEmpty=False,
#                             muscleVoice=Wall_E_sense_voice_response_sensation, isExactMuscleVoice=True,
#                             communicationVoice=Wall_E_sense_voice_response_sensation, isExactCommunicationVoice=True,
#                            )
#                 break
# 
#         # check that we succeeded            
#         self.assertTrue(j < Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH)
#             
#         
#         
# 
#   
#         
#         # we don't response any more, so Communication.stopWaitingResponse
#         # should be run and self.communication.communicationItems) should be empty
#         # wait some time
#         sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
#         print("test is sleeping " + str(sleepTime) + " until continuing")       
#         systemTime.sleep(sleepTime)
#         print("Now stopWaitingResponse should be happened and we test it")       
#         # should get Voice Feeling between Voice and Item
#         # BUT is hard t0 test, just log
#         self.expect(name='NO response, got Negative feelings',
#                     isEmpty=False,
#                     muscleImage=None,
#                     muscleVoice=None,
#                     communicationImage=None,
#                     communicationVoice=None,
#                     isVoiceFeeling=True, isImageFeeling=False, isNegativeFeeling=True)
        
 
        # simulate that we have stopped Communication-Robot and all Robots get Item-sensation that it is absent
        self.communication.deInitRobot()
        self.expect(name='deInitRobot',
                    isEmpty=False,
#                     muscleImage=None,
#                     muscleVoice=None,
#                     communicationImage=None,
#                     communicationVoice=None,
#                     isVoiceFeeling=False,
#                     isImageFeeling=False,
#                     isItem=True,
                    communicationItem=self.technicalSensation) # will get other sensation


       
    '''
    How we expect tested Robot responses
    
    parameters
    name                       name of the tested case
    isEmpty                    do we expect a response at all
    muscleVoice                response is SensasationType.Voice, RobotType.Sense
    isExactMuscleVoice         does dataId match to communicationVoice
    communicationVoice         response is SensasationType.Voice, RobotType.communication
    isExactCommunicationVoice  does dataId match to communicationVoice
    isVoiceFeeling             do we expect to get Feeling to a Voice
    isImageFeeling=False,      do we expect to get Feeling to a Image
    isPositiveFeeling          is/are feelings positive
    isNegativeFeeling          is/are feelings negative
    isItem                     response is SensasationType.Item
    isWait                     do we wait rto get all responses or
                               start to study responses right a way
                               
    TODO Correct parameters muscle and communication responses are same
    but when we limit communication responseses, it can be so, that we don't get them
    '''
        
    def expect(self, name, isEmpty, #isSpoken, isHeard,
               muscleVoice=None,isExactMuscleVoice=False,
               communicationVoice=None,isExactCommunicationVoice=False,
               muscleImage=None, isExactMuscleImage=False,
               communicationImage=None, isExactCommunicationImage=False,
               communicationItem=None, isExactCommunicationItem=False,
               isVoiceFeeling=False,
               isImageFeeling=False,
               isPositiveFeeling=False, isNegativeFeeling=False,
               isItem=False,
               isWait=False):
        print("\nexpect {}".format(name))
        self.muscleVoice = None
        self.muscleImage = None
        self.communicationVoice  = None
        self.communicationImage = None
        gotCommunicationItem = None
        errortext = '{}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        if isWait and not isEmpty: 
            i=0  
            while self.getAxon().empty() and i < CommunicationTestCase.AXON_WAIT:
                systemTime.sleep(1)
                i=i+1
                print('slept {}s to get something to Axon'.format(i))
        self.assertEqual(self.getAxon().empty(), isEmpty, errortext)
        if not isEmpty:   
            isExactMuscleVoiceStillExpected = isExactMuscleVoice
            isExactCommunicationVoiceStillExpected = isExactCommunicationVoice
            isExactMuscleImageStillExpected = isExactMuscleImage
            isExactCommunicationImageStillExpected = isExactCommunicationImage
            isExactCommunicationItemStillExpected = isExactCommunicationItem
            isItemStillExpected = isItem
            if muscleVoice is not None:
                isMuscleVoiceStillExpected = True
            else:
                isMuscleVoiceStillExpected = False
                isExactMuscleVoiceStillExpected = False
            if communicationVoice is not None:
                isCommunicationVoiceStillExpected = True
            else:
                isCommunicationVoiceStillExpected = False
                isExactCommunicationVoiceStillExpected = False
            if muscleImage is not None:
                isMuscleImageStillExpected = True
            else:
                isMuscleImageStillExpected = False
                isExactMuscleImageStillExpected = False
            if communicationImage is not None:
                isCommunicationImageStillExpected = True
            else:
                isCommunicationImageStillExpected = False
                isExactCommunicationImageStillExpected = False
            if communicationItem is not None:
                isCommunicationItemStillExpected = True
            else:
                isCommunicationItemStillExpected = False
                isExactCommunicationItemStillExpected = False
            isVoiceFeelingStillExpected = isVoiceFeeling
            isImageFeelingStillExpected = isImageFeeling
            while(not self.getAxon().empty()):
                tranferDirection, sensation = self.getAxon().get(robot=self)
                self.printSensationNameById(dataId=sensation.getDataId(), note=name + " expect got")
                sensation.detach(robot=self)# We are acting mainrobot and should detach sensation
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if sensation.getRobotType() == Sensation.RobotType.Muscle:
                        self.muscleVoice=sensation
                        self.assertTrue(muscleVoice != None, "got unexpected MuscleVoice")
                        self.assertTrue(isMuscleVoiceStillExpected, "got duplicate Muscle Voice")
                        isMuscleVoiceStillExpected = False
                        if muscleVoice != None:
                            if isExactMuscleVoiceStillExpected:
                                isExactMuscleVoiceStillExpected = (sensation.getDataId() != muscleVoice.getDataId())
                            else:
                                if sensation.getDataId() == muscleVoice.getDataId():
                                    print("exactMuscleVoice was not expected, but got it!")
                                else:
                                    self.printSensationNameById(id=sensation.getId(), note=name + " exactMuscleVoice was not expected, got other Voice")
                        else:
                            self.assertTrue(False,"got unexpected Muscle Voice")
                    elif sensation.getRobotType() == Sensation.RobotType.Communication:
                        self.communicationVoice = sensation
                        self.assertTrue(communicationVoice != None, "got unexpected Communication Voice")
                        self.assertTrue(isCommunicationVoiceStillExpected, "got duplicate Communication Voice")
                        isCommunicationVoiceStillExpected = False
                        if communicationVoice != None:
                            if isExactCommunicationVoiceStillExpected:
                                isExactCommunicationVoiceStillExpected = (sensation.getDataId() != communicationVoice.getDataId())
                            else:
                                if sensation.getDataId() == communicationVoice.getDataId():
                                    print("exactCommunicationVoice was not expected, but got it!")
                                else:
                                    self.printSensationNameById(id=sensation.getId(), note=name + " exactCommunicationVoice was not expected, got other Voice")
                        else:
                            self.assertTrue(False,"got unexpected Communication Voice")
                    else:
                        self.assertTrue(False, 'got unexpected Voice RobotType')
                elif sensation.getSensationType() == Sensation.SensationType.Image:
                    if sensation.getRobotType() == Sensation.RobotType.Muscle:
                        self.muscleImage=sensation
                        self.assertTrue(muscleImage != None, "got unexpected Muscle Image")
                        self.assertTrue(isMuscleImageStillExpected, "got duplicate Muscle Image")
                        isMuscleImageStillExpected = False
                        if muscleImage != None:
                            if isExactMuscleImageStillExpected:
                                isExactMuscleImageStillExpected = (sensation.getDataId() != muscleImage.getDataId())
                            else:
                                if sensation.getDataId() == muscleImage.getDataId():
                                    print("exactMuscleImage was not expected, but got it!")
                                else:
                                    self.printSensationNameById(id=sensation.getId(), note=name + " exactMuscleImage was not expected, got other Image")
                        else:
                            self.assertTrue(False,"got unexpected Muscle Image")
                    elif sensation.getRobotType() == Sensation.RobotType.Communication:
                        self.communicationImage=sensation
                        self.assertTrue(communicationImage != None, "got unexpected Communication Image")
                        self.assertTrue(isCommunicationImageStillExpected, "got duplicate Communication Image")
                        isCommunicationImageStillExpected = False
                        if communicationImage != None:
                            if isExactCommunicationImageStillExpected:
                                isExactCommunicationImageStillExpected = (sensation.getDataId() != communicationImage.getDataId())
                            else:
                                if sensation.getDataId() == communicationImage.getDataId():
                                    print("exactCommunicationImage was not expected, but got it!")
                                else:
                                    self.printSensationNameById(id=sensation.getId(), note=name + " exactCommunicationImage was not expected, got other Image")
                        else:
                            self.assertTrue(False,"got unexpected Communication Image")
                    else:
                        self.assertTrue(False, 'got unexpected Image RobotType')
                elif sensation.getSensationType() == Sensation.SensationType.Feeling:
                    print("got Feeling")
                    self.assertTrue(isVoiceFeeling or isImageFeeling or isPositiveFeeling or isNegativeFeeling,'got Feeling, but Feeling was not expected')
# We can get many Felling for same Voice, so  many feelings is not unexpected
#                     errortext =  '{}: got unexpected Feeling Another Feeling {}'.format(name, str(not (isVoiceFeelingStillExpected or isImageFeelingStillExpected)))
#                     self.assertTrue(isVoiceFeelingStillExpected or isImageFeelingStillExpected, errortext)
# #                     self.assertEqual(len(sensation.getAssociations()), 1)
                    if sensation.getOtherAssociateSensation().getSensationType() == Sensation.SensationType.Voice:
                        self.assertTrue(isVoiceFeeling,'got Voice Feeling, but Voice Feeling was not expected')
                        isVoiceFeelingStillExpected = False
                        self.assertEqual(sensation.getPositiveFeeling(), isPositiveFeeling)
                        self.assertEqual(sensation.getNegativeFeeling(), isNegativeFeeling)
                    elif sensation.getOtherAssociateSensation().getSensationType() == Sensation.SensationType.Image:
                        self.assertTrue(isImageFeeling,'got Image Feeling, but Image Feeling was not expected')
                        isImageFeelingStillExpected = False
                        self.assertEqual(sensation.getPositiveFeeling(), isPositiveFeeling)
                        self.assertEqual(sensation.getNegativeFeeling(), isNegativeFeeling)
                    else:
                        self.assertTrue(False, "Unsupported associate type {} with feeling".format( Sensation.getSensationTypeString(sensation.getOtherAssociateSensation().getSensationType())))

#                     self.assertEqual(sensation.getPositiveFeeling(), isPositiveFeeling)
#                     self.assertEqual(sensation.getNegativeFeeling(), isNegativeFeeling)
                elif sensation.getSensationType() == Sensation.SensationType.Item:
                    # TODO check if this is used
                    gotItem = sensation
                    isItemStillExpected = False
                    if sensation.getRobotType() == Sensation.RobotType.Communication:
                        self.communicationItem = sensation
                        self.assertTrue(communicationItem != None, "got unexpected Communication Item")
                        self.assertTrue(isCommunicationItemStillExpected, "got duplicate Communication Item")
                        isCommunicationItemStillExpected = False
                        if communicationItem != None:
                            if isExactCommunicationItemStillExpected:
                                isExactCommunicationItemStillExpected = (sensation.getDataId() != communicationItem.getDataId())
                            else:
                                if sensation.getDataId() == communicationItem.getDataId():
                                    print("exactCommunicationItem was not expected, but got it!")
                                else:
                                    self.printSensationNameById(id=sensation.getId(), note=name + " exactCommunicationItem was not expected, got other Item")
                        else:
                            self.assertTrue(False,"got unexpected Communication Item")
                    else:
                        self.assertTrue(False, 'got unexpected Item RobotType')
                    
            self.assertFalse(isMuscleVoiceStillExpected,  'Did not get muscleVoice')
            if self.muscleVoice != None and muscleVoice != None:                   
                self.assertFalse(isExactMuscleVoiceStillExpected,  'Did not get expected muscleVoice {} but {}'.format(self.getSensationNameById(note='', id=muscleVoice.getId()), self.getSensationNameById(note='', dataId=self.muscleVoice.getDataId())))                   
            self.assertFalse(isMuscleImageStillExpected,  'Did not get muscleImage')
            if self.muscleImage != None and muscleImage != None:
                self.assertFalse(isExactMuscleImageStillExpected,  'Did not get expected muscleImage {} but {}'.format(self.getSensationNameById(note='', id=muscleImage.getId()), self.getSensationNameById(note='', dataId=self.muscleImage.getDataId())))                  

            self.assertFalse(isCommunicationVoiceStillExpected,  'Did not get communicationVoice')
            if self.communicationVoice  != None and communicationVoice != None:                   
                self.assertFalse(isExactCommunicationVoiceStillExpected,  'Did not get expected communicationVoice {} but {}'.format(self.getSensationNameById(note='', id=communicationVoice.getId()), self.getSensationNameById(note='', dataId=self.communicationVoice .getDataId())))                   
            self.assertFalse(isCommunicationImageStillExpected,  'Did not get communicationImage')
            if self.communicationImage != None and communicationImage != None:
                self.assertFalse(isExactCommunicationImageStillExpected,  'Did not get expected communicationImage {} but {}'.format(self.getSensationNameById(note='', id=communicationImage.getId()), self.getSensationNameById(note='', dataId=self.communicationImage.getDataId())))                  

            self.assertFalse(isCommunicationItemStillExpected,  'Did not get communicationItem')
            if self.communicationItem != None and communicationItem != None:
                self.assertFalse(isExactCommunicationItemStillExpected,  'Did not get expected communicationItem {} but {}'.format(self.getSensationNameById(note='', id=communicationItem.getId()), self.getSensationNameById(note='', dataId=self.communicationItem.getDataId())))                  

            self.assertFalse(isVoiceFeelingStillExpected, 'Did not get voice feeling')                   
            self.assertFalse(isImageFeelingStillExpected, 'Did not get senseImage feeling')                   
            self.assertFalse(isItemStillExpected,  'Did not get item')
            
        # test isForgotytable
        # TODO responses and answers should be Forgettable, bot
        # we should test instead Communication.spokedAssociations
        # and .sensations.
        if self.muscleVoice != None:
            self.assertTrue(self.muscleVoice.isForgettable())
                
        if self.muscleImage != None:
            self.assertTrue(self.muscleImage.isForgettable())

        if self.communicationVoice  != None:
            self.assertTrue(self.communicationVoice .isForgettable())
            
        if self.communicationImage != None:
            self.assertTrue(self.communicationImage.isForgettable())
                
        # previous
        
        if self.previousGotMuscleVoice != None:
            self.previousGotMuscleVoice.logAttachedBy()
            self.assertTrue(self.previousGotMuscleVoice.isForgettable())
                
        if self.previousGotMuscleImage != None:
            self.previousGotMuscleImage.logAttachedBy()
            self.assertTrue(self.previousGotMuscleImage.isForgettable())

        if self.previousGotCommunicationVoice != None:
            self.previousGotCommunicationVoice.logAttachedBy()
            self.assertTrue(self.previousGotCommunicationVoice.isForgettable())
            
        if self.previousGotCommunicationImage != None:
            self.previousGotCommunicationImage.logAttachedBy()
            self.assertTrue(self.previousGotCommunicationImage.isForgettable())
                
        # remember new previous
        self.previousGotMuscleVoice = self.muscleVoice 
        self.previousGotMuscleImage = self.muscleImage
        self.previousGotCommunicationVoice = self.communicationVoice 
        self.previousGotCommunicationImage = self.communicationImage

# TODO enable and reimplement, because
# spokedAssociation is location based now
 
#         self.assertEqual(self.communication.spokedAssociations is None,
#                     muscleImage is None and\
#                     muscleVoice is None and\
#                     communicationImage is None and\
#                     communicationVoice is None)# and\
#                     #not isVoiceFeeling and not isImageFeeling and not isNegativeFeeling)
#         if self.communication.spokedAssociations is not None:
#             for associations in self.communication.spokedAssociations:
#                 for association in associations:
#                     self.assertTrue(association.getSensation().isForgettable())
#                     self.assertTrue(association.getSelfSensation().isForgettable())
        
 
                
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
                tranferDirection, sensation = self.getAxon().get(robot=self)
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
                print('Did not get vvoice feeling')                   

        
if __name__ == '__main__':
    unittest.main()

 