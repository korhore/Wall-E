'''
Created on 14.04.2021
Updated on 13.01.2022
@author: reijo.korhonen@gmail.com

test Communication class
This class includes all tests for this class.
This file can't be run directly, but is a library for tests.
Test methods take as a parameter Robot instance to test.

Test runner class inherits this class and uses these methods to implement
tests normal way with unittest. This class is used to in
testCommunication.py and test VisualCommunication.py, where unittest
frameworks.

python3 -m unittest tests/testCommunication.py


'''
import time as systemTime
import os


from Sensation import Sensation
from Memory import Memory
from Config import Config
# import Communication, but
# set Communication.COMMUNICATION_INTERVAL smaller,
# so test runs faster, when no waits normal time 30s, when we don't get
# response from person
TEST_COMMUNICATION_INTERVAL=5.0 # 1.0 works if we don't use living processes, but min for living process this is 2.5
from Communication.Communication import Communication
Communication.COMMUNICATION_INTERVAL = TEST_COMMUNICATION_INTERVAL
Memory.COMMUNICATION_INTERVAL = TEST_COMMUNICATION_INTERVAL

from Axon import Axon
from Robot import Robot

from RobotTestCase import RobotTestCase

class CommunicationTest(RobotTestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    


    '''
    doSetUp
    
    parameters
    communication    Communication instance to test,
    '''
    
    def doSetUp(self, communication):
        print('\nsetUp')
        self.communication=communication
        
        ######################################
        #
        # Robot class specific setup
        
        self.CleanDataDirectory()

        Robot.mainRobotInstance = self
        self.mainNames = self.MAINNAMES
        #self.axon = Axon(robot=self)

        # Robot to test        
        self.setRobotMainNames(communication, self.MAINNAMES)
        self.setRobotLocations(communication, self.getLocations())

        # base class (RobotTestCase) doSetUp
        super(CommunicationTest, self).doSetUp(robot=self.communication)
        
        ######################################
        #
        # Communication class specific setup
        
        self.setRobotMainNames(communication, self.MAINNAMES)
        self.setRobotLocations(communication, self.getLocations())
        # should correct self.communication.itemConversations,
        # because it is tested in _init__ normal way with configuration settings
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
            
        # reject mainRobot functionality
        communication._isMainRobot = False
        communication.level = 2
        communication.subInstances = []
        communication.tcpServer = None
        communication.identity = None
        # clean up memory
        communication.memory = Memory(robot = self,
                               maxRss = Config.MAXRSS_DEFAULT,
                               minAvailMem = Config.MINAVAILMEM_DEFAULT)
        


    def doTearDown(self):
        print('\nCommunicationTest:doTearDown')       
        # base class (RobotTestCase) doTearDown
        super(CommunicationTest, self).doTearDown()
        print('\nCommunicationTest:doTearDown\n')       
        
    '''
    TensorfloClassafication produces
    Item.name Working Out
    
    '''            
    def doTest_PresenseItemPresentRobot(self, communication, isWait):
        # create Robot sensation
        self.assertFalse(len(communication.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertFalse(communication.getMemory().hasRobotsPresence())
        roboSensation=self.createSensation(associations=[],
                                           robotType=Sensation.RobotType.Communication,
                                           sensationName='roboSensation',
                                           robot=communication,
                                           sensationType = Sensation.SensationType.Robot,
                                           memoryType = Sensation.MemoryType.Working,
                                           name = communication.getName(),
                                           presence = Sensation.Presence.Present,
                                           locations = self.getLocations(),
                                           mainNames=self.OTHERMAINNAMES), # Should haver other mainnames than this Robot to get robot presence
        
        self.assertTrue(len(communication.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertTrue(communication.getMemory().hasRobotsPresence())

        self.do_test_PresenseItemRobot(communication=communication, isWait=isWait, isPresentRobot = True)
            
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''            
    def doTest_PresenseItemAbsentRobot(self, communication, isWait):
        # create Robot sensation
        self.assertFalse(len(communication.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertFalse(communication.getMemory().hasRobotsPresence())
        roboSensation=self.createSensation(associations=[],
                                           robotType=Sensation.RobotType.Communication,
                                           sensationName='roboSensation',
                                           robot=communication,
                                           sensationType = Sensation.SensationType.Robot,
                                           memoryType = Sensation.MemoryType.Working,
                                           name = communication.getName(),
                                           presence = Sensation.Presence.Absent,
                                           locations = self.getLocations())
        
        self.assertFalse(len(communication.getMemory().getAllPresentRobotSensations()) > 0)

        self.do_test_PresenseItemRobot(communication=communication, isWait=isWait, isPresentRobot = False)
        self.assertFalse(communication.getMemory().hasRobotsPresence())
        

  
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def do_test_PresenseItemRobot(self, communication, isWait, isPresentRobot):
        print('\ntest_Presense')
                
        # make voice that should be ignored
        # should be created before current items
        voice_sensation_ignored  = self.createSensation(
                                                sensationName='voice_sensation_ignored',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA_IGNORED,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation_ignored.isForgettable())
        self.printSensationNameById(note='voice_sensation_ignored', dataId=voice_sensation_ignored.getDataId())

        history_sensationTime = systemTime.time() -2*max(CommunicationTest.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Entering {}'.format(CommunicationTest.NAME))
        Wall_E_item_sensation_entering = self.createSensation(
                                                 sensationName='Wall_E_item_sensation_entering',
                                                 robot=communication,
                                                 time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTest.NAME,
                                                 score=CommunicationTest.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.getLocations())
        self.assertTrue(Wall_E_item_sensation_entering.isForgettable())
        self.printSensationNameById(note='Wall_E_item_sensation_entering test', dataId= Wall_E_item_sensation_entering.getDataId())
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering)
        # We get Voice, Image, if Communication can respond but it can't
        self.expect(isWait=isWait,
                    name='Entering, Too old response', isEmpty=True)
        # TODO Note getAllPresentItemSensations() and we should use getPresentItemSensations, which has location parameter, but it takes a lot time to change
        # all these tests and in practice this test works as well.
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory()..getAllPresentItemSensations() should be 0')
        # test that we have conversation in locations given
        self.assertEqual(len(self.communication.itemConversations),len(self.getLocations()))
        for location in self.getLocations():
            self.assertTrue(self.communication.itemConversations[location].robotState in [Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationNotStarted])
        
        
        print('\n current Entering {}'.format(CommunicationTest.NAME))
        # make potential response
        voice_sensation1 = self.createSensation(
                                                sensationName='voice_sensation1',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA2,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation1.isForgettable())
        self.printSensationNameById(note='voice_sensation1 test', dataId=voice_sensation1.getDataId())
        image_sensation1 = self.createSensation(
                                                sensationName='image_sensation1',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.assertTrue(image_sensation1.isForgettable())
        self.printSensationNameById(note='image_sensation1 test', dataId=image_sensation1.getDataId())
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(item_sensation1.isForgettable())
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        item_sensation1.associate(sensation=voice_sensation1)
        item_sensation1.associate(sensation=image_sensation1)
        voice_sensation1.associate(sensation=image_sensation1)

        Wall_E_item_sensation_entering2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering2',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(systemTime.time() - Wall_E_item_sensation_entering2.getTime() < Communication.COMMUNICATION_INTERVAL)
       
        self.assertTrue(Wall_E_item_sensation_entering2.isForgettable())
        self.printSensationNameById(note='Wall_E_item_sensation_entering2 test', dataId=Wall_E_item_sensation_entering2.getDataId())
         
        #simulate TensorFlowClassification send presence item to MainRobot == Communication
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        # test test
        self.assertTrue(voice_sensation1.isForgettable())
        
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering2)

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            muscleVoice = self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation1, isExactMuscleImage=True,
                        muscleVoice=voice_sensation1, isExactMuscleVoice=True,
                        communicationItem=Wall_E_item_sensation_entering2, isExactCommunicationItem=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
            # make voice that should be ignored 
            voice_sensation_ignored_isPresentRobotEntering  = self.createSensation(
                                                    sensationName='voice_sensation_ignored_isPresentRobotEntering',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTest.VOICEDATA_IGNORED,
                                                    locations=self.getLocations())
            self.assertTrue(voice_sensation_ignored_isPresentRobotEntering.isForgettable())
            self.printSensationNameById(note='voice_sensation_ignored_isPresentRobotEntering', dataId=voice_sensation_ignored_isPresentRobotEntering.getDataId())
            communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored_isPresentRobotEntering)
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 1, voice_sensation_ignored_isPresentRobotEntering should be ignored',
                        isEmpty=True)

            # simulate Playback,
            robotStateSensation=self.createSensation(
                                                    sensationName='voice_sensation1Played',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.RobotState,
                                                    robotType=Sensation.RobotType.Sense,
                                                    robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                    locations=self.getLocations())
            robotStateSensation.associate(muscleVoice)
            self.doProcess(robot=communication, sensation=robotStateSensation)
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 1, CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # To test other Communication Robots functionality we must make a trick and change this Sensation location
            # so this Robot think that Sensation comes from other Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, reply to communicationItem, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation1, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation1, isExactCommunicationVoice=True,
                        communicationItem=None)        # TODO remove this, it is not valid any more
        else:  
            muscleVoice = self.expect(isWait=isWait,
                        name='Entering, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation1, isExactMuscleImage=True,
                        muscleVoice=voice_sensation1, isExactMuscleVoice=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed,
                                 "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationWaitingVoicePlayed)))
            # simulate Playback
            robotStateSensation=self.createSensation(
                                                    sensationName='voice_sensation1Played',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.RobotState,
                                                    robotType=Sensation.RobotType.Sense,
                                                    robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                    locations=self.getLocations())
            robotStateSensation.associate(muscleVoice)

            self.doProcess(robot=communication, sensation=robotStateSensation)
            self.expect(isWait=isWait,
                        name='Entering, response 1, CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
 

        print('\n1: current Present {}'.format(CommunicationTest.NAME))
        Wall_E_item_sensation_present = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present test', dataId=Wall_E_item_sensation_present.getDataId())


        # make potential response
        voice_sensation2 = self.createSensation(
                                                sensationName='voice_sensation2',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA2,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation2.isForgettable())
        self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
        
        image_sensation2 = self.createSensation(
                                                sensationName='image_sensation2',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.assertTrue(image_sensation2.isForgettable())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        
        item_sensation2 = self.createSensation(
                                                sensationName='item_sensation2',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(item_sensation2.isForgettable())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        item_sensation2.associate(sensation=voice_sensation2)
        item_sensation2.associate(sensation=image_sensation2)
        voice_sensation2.associate(sensation=image_sensation2)

        #simulate TensorFlowClassification send presence item to MainRobot/Communication
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (and be assigned as self.association) with with  name and associations count
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            # But because we are already waiting for a reply, we don't expect anything!
            muscleVoice = self.expect(isWait=isWait,
                        name='isPresentRobot Present, response 2', isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation2, isExactMuscleImage=True,
                        muscleVoice=voice_sensation2, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_present, isExactCommunicationItem=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            # # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
            # communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Present, voice_sensation_ignored should be ignored',
            #             isEmpty=True)
            #
            # # simulate Playback
            # robotStateSensation=self.createSensation(
            #                                         sensationName='voice_sensation2Played',
            #                                         robot=communication,
            #                                         memoryType=Sensation.MemoryType.Sensory,
            #                                         sensationType=Sensation.SensationType.RobotState,
            #                                         robotType=Sensation.RobotType.Sense,
            #                                         robotState = Sensation.RobotState.CommunicationVoicePlayed,
            #                                         locations=self.getLocations())
            # robotStateSensation.associate(muscleVoice)
            #
            # self.doProcess(robot=communication, sensation=robotStateSensation)
            # self.expect(isWait=isWait,
            #              name='isPresentRobot Present, response 2, CommunicationWaitingResponse', isEmpty=False,
            #              robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # # To test other Communication Robots functionality we must make a trick and change this Sensation Location
            # # so this Robot think that Sensation comes from other Robot, not it self
            # self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            #
            # # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # # We will get same result, but no ask-sensation
            # communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Present, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
            #             communicationImage=image_sensation2, isExactCommunicationImage=True,
            #             communicationVoice=voice_sensation2, isExactCommunicationVoice=True,
            #             communicationItem=None)        # TODO remove this, it is not valid any more
        else:
            # We are still waiting response
            muscleVoice = self.expect(isWait=isWait,
                        name='Present, response 2', isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation2, isExactMuscleImage=True,
                        muscleVoice=voice_sensation2, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse,
                                 "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationWaitingResponse)))

#             # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
#             communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored)
#             self.expect(isWait=isWait,
#                         name='isPresentRobot Present, voice_sensation_ignored should be ignored',
#                         isEmpty=True)
# 
#             # simulate Playback
#             robotStateSensation=self.createSensation(
#                                                     sensationName='voice_sensation2Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotType=Sensation.RobotType.Sense,
#                                                     robotState = Sensation.RobotState.CommunicationVoicePlayed,
#                                                     locations=self.getLocations())
#             robotStateSensation.associate(muscleVoice)
# 
#             self.doProcess(robot=communication, sensation=robotStateSensation)
#             self.expect(isWait=isWait,
#                         name='Present, response 2, CommunicationWaitingResponse', isEmpty=False,
#                         robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
#             for location in self.getLocations():
#                 self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)


        # We should remove remote Robot Item-presence to test this local Absent feature
        if isPresentRobot and Robot.GLOBAL_LOCATION in communication.getMemory()._presentItemSensations:
            del communication.getMemory()._presentItemSensations[Robot.GLOBAL_LOCATION]
        

        
        print('\n current Absent {}'.format(CommunicationTest.NAME))
        Wall_E_item_sensation_absent = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent test', dataId=Wall_E_item_sensation_absent.getDataId())
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 0')

        #process              
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 0')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        self.expect(isWait=isWait,
                    name='Absent', isEmpty=False, #isSpoken=False, isHeard=False,
                    isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationEnded))
 
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
        
 
        # NAME with NAME2
        
        print('\n NAME current Entering {}',format(CommunicationTest.NAME))
        # make potential response
        voice_sensation3 = self.createSensation(
                                                sensationName='voice_sensation3',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA3,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation3 test', dataId=voice_sensation3.getDataId())
        image_sensation3 = self.createSensation(
                                                sensationName='image_sensation3',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation3 test', dataId=image_sensation3.getDataId())
        item_sensation3 = self.createSensation(
                                                sensationName='item_sensation3',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation3 test', dataId=item_sensation3.getDataId())
        item_sensation3.associate(sensation=voice_sensation3)
        item_sensation3.associate(sensation=image_sensation3)
        voice_sensation3.associate(sensation=image_sensation3)
        
        # make entering item and process
        Wall_E_item_sensation_entering3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering3',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_entering3 test', dataId=Wall_E_item_sensation_entering3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 1')

        #process                      
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering3)
                        
        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            muscleVoice = self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 3', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation3, isExactMuscleImage=True,
                        muscleVoice=voice_sensation3, isExactMuscleVoice=True,
                        communicationItem=Wall_E_item_sensation_entering3, isExactCommunicationItem=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
            communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored_isPresentRobotEntering)
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, voice_sensation_ignored_isPresentRobotEntering should be ignored',
                        isEmpty=True)

            # simulate Playback
            robotStateSensation=self.createSensation(
                                                    sensationName='voice_sensation3Played',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.RobotState,
                                                    robotType=Sensation.RobotType.Sense,
                                                    robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                    locations=self.getLocations())
            robotStateSensation.associate(muscleVoice)
            self.doProcess(robot=communication, sensation=robotStateSensation)
            self.expect(isWait=isWait,
                        name='isPresentRobot Entering, response 3, CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # To test other Communication Robots functionality we must make a trick and change this Sensation MainNames
            # so this Robot think that Sensation comes from other Robot, not it self
            self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=isWait,
                        name='isPresentRobot Present, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation3, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation3, isExactCommunicationVoice=True,
                        communicationItem=None)        # TODO remove this, it is not valid any more
        else:  
            muscleVoice = self.expect(isWait=isWait,
                        name='Entering, response 3', isEmpty=False,
                        muscleImage=image_sensation3, isExactMuscleImage=True,
                        muscleVoice=voice_sensation3, isExactMuscleVoice=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed,
                                 "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationWaitingVoicePlayed)))

            # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
            communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored)
            self.expect(isWait=isWait,
                        name='Entering, response 3, voice_sensation_ignored should be ignored',
                        isEmpty=True)

            # simulate Playback
            robotStateSensation=self.createSensation(
                                                    sensationName='voice_sensation3Played',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.RobotState,
                                                    robotType=Sensation.RobotType.Sense,
                                                    robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                    locations=self.getLocations())
            robotStateSensation.associate(muscleVoice)
            self.doProcess(robot=communication, sensation=robotStateSensation)
            self.expect(isWait=isWait,
                        name='Entering, response 3, CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
            

        
        print('\n NAME2 current Entering {}'.format(CommunicationTest.NAME2))
        # make potential response
        voice_sensation4 = self.createSensation(
                                                sensationName='voice_sensation4',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation4 test', dataId=voice_sensation4.getDataId())
        image_sensation4 = self.createSensation(
                                                sensationName='image_sensation4',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation4 test', dataId=image_sensation4.getDataId())
        item_sensation4 = self.createSensation(
                                                sensationName='image_sensation4',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation4 test', dataId=item_sensation4.getDataId())
        item_sensation4.associate(sensation=voice_sensation4)
        item_sensation4.associate(sensation=image_sensation4)
        voice_sensation4.associate(sensation=image_sensation4)
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertTrue(len(communication.getMemory().getAllPresentItemSensations()) in (1, 2), 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 1,2')

        # make entering and process
        Wall_E_item_sensation_entering4 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering4',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_entering4 test', dataId=Wall_E_item_sensation_entering4.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        # other entering is handled as response
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 2')


        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering4)
        
        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            # But because we are already waiting a reply, we expect nothing
            muscleVoice = self.expect(isWait=isWait,
                        name='isPresentRobot Name2 entering, response 4', isEmpty=True,
                        muscleImage=image_sensation4, isExactMuscleImage=True,
                        muscleVoice=voice_sensation4, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_entering4, isExactCommunicationItem=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            # # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
            # communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored_isPresentRobotEntering)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Name2 entering, voice_sensation_ignored_isPresentRobotEntering should be ignored',
            #             isEmpty=True)
            #
            # # simulate Playback
            # robotStateSensation=self.createSensation(
            #                                         sensationName='voice_sensation4Played',
            #                                         robot=communication,
            #                                         memoryType=Sensation.MemoryType.Sensory,
            #                                         sensationType=Sensation.SensationType.RobotState,
            #                                         robotType=Sensation.RobotType.Sense,
            #                                         robotState = Sensation.RobotState.CommunicationVoicePlayed,
            #                                         locations=self.getLocations())
            # robotStateSensation.associate(muscleVoice)
            #
            # self.doProcess(robot=communication, sensation=robotStateSensation)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Entering, response 4, CommunicationWaitingResponse', isEmpty=False,
            #             robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # # To test other Communication Robots functionality we must make a trick and change this Sensation MainNames
            # self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            #
            # # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # # We will get same result, but no ask-sensation
            # communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Name2 entering, reply to communicationItem, response 4', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
            #             communicationImage=image_sensation4, isExactCommunicationImage=True,
            #             communicationVoice=voice_sensation4, isExactCommunicationVoice=True,
            #             communicationItem=None)
        else:
            # We are still waiting response. 
            muscleVoice = self.expect(isWait=isWait,
                        name='Name2 entering , response 4', isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation4, isExactMuscleImage=True,
                        muscleVoice=voice_sensation4, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse,
                                 "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationWaitingResponse)))

#             # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
#             communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored)
#             self.expect(isWait=isWait,
#                         name='Name2 entering, voice_sensation_ignored should be ignored',
#                         isEmpty=True)
# 
#             # simulate Playback
#             robotStateSensation=self.createSensation(
#                                                     sensationName='voice_sensation4Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotType=Sensation.RobotType.Sense,
#                                                     robotState = Sensation.RobotState.CommunicationVoicePlayed,
#                                                     locations=self.getLocations())
#             robotStateSensation.associate(muscleVoice)
# 
#             self.doProcess(robot=communication, sensation=robotStateSensation)
#             self.expect(isWait=isWait,
#                         name='Name2 entering , response 4, CommunicationWaitingResponse', isEmpty=False,
#                         robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
#             for location in self.getLocations():
#                 self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)

        print('\n2: NAME2 current Present {}'.format(CommunicationTest.NAME2))
        #  make potential response
        voice_sensation5 = self.createSensation(
                                                sensationName='voice_sensation5',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation5 test', dataId=voice_sensation5.getDataId())
        image_sensation5 = self.createSensation(
                                                sensationName='image_sensation5',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation5 test', dataId=image_sensation5.getDataId())
        item_sensation5 = self.createSensation(
                                                sensationName='item_sensation5',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation5 test', dataId=item_sensation5.getDataId())
        item_sensation5.associate(sensation=voice_sensation5)
        item_sensation5.associate(sensation=image_sensation5)
        voice_sensation5.associate(sensation=image_sensation5)

        Wall_E_item_sensation_present2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present2',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present2 test', dataId=Wall_E_item_sensation_present2.getDataId())

        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present2)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() should be 2')

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            # But because we are already waiting a reply, we expect nothing
            muscleVoice = self.expect(isWait=isWait,
                        name='isPresentRobot Name2 present, response 5', isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation5, isExactMuscleImage=True,
                        muscleVoice=voice_sensation5, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_present2, isExactCommunicationItem=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

        #     # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
        #     communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored_isPresentRobotEntering)
        #     self.expect(isWait=isWait,
        #                 name='isPresentRobot Name2 present, voice_sensation_ignored should be ignored',
        #                 isEmpty=True)
        #
        #     # simulate Playback
        #     robotStateSensation=self.createSensation(
        #                                             sensationName='voice_sensation5Played',
        #                                             robot=communication,
        #                                             memoryType=Sensation.MemoryType.Sensory,
        #                                             sensationType=Sensation.SensationType.RobotState,
        #                                             robotType=Sensation.RobotType.Sense,
        #                                             robotState = Sensation.RobotState.CommunicationVoicePlayed,
        #                                             locations=self.getLocations())
        #     robotStateSensation.associate(muscleVoice)
        #
        #     self.doProcess(robot=communication, sensation=robotStateSensation)
        #     self.expect(isWait=isWait,
        #                 name='isPresentRobot Entering, response 5, CommunicationWaitingResponse', isEmpty=False,
        #                 robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        #     # To test other Communication Robots functionality we must make a trick and change this Sensation MainNames
        #     # so this Robot think that Sensation comes from other Robot, not it self
        #     self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
        #
        #     # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
        #     # We will get same result, but no ask-sensation
        #     communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
        #     self.expect(isWait=isWait,
        #                 name='isPresentRobot Name2 enteringt, reply to communicationItem, response 5', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
        #                 communicationImage=image_sensation5, isExactCommunicationImage=True,
        #                 communicationVoice=voice_sensation5, isExactCommunicationVoice=True,
        #                 communicationItem=None)
        else:
            # We still wait response
            muscleVoice = self.expect(isWait=isWait,
                        name= "Name2 present, response 5", isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation5, isExactMuscleImage=True,
                        muscleVoice=voice_sensation5, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse,
                                 "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationWaitingResponse)))
#             # simulate Playback
#             robotStateSensation=self.createSensation(
#                                                     sensationName='voice_sensation5Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotType=Sensation.RobotType.Sense,
#                                                     robotState = Sensation.RobotState.CommunicationVoicePlayed,
#                                                     locations=self.getLocations())
#             robotStateSensation.associate(muscleVoice)
# 
#             self.doProcess(robot=communication, sensation=robotStateSensation)
#             self.expect(isWait=isWait,
#                         name='Name2 present, response 5, CommunicationWaitingResponse', isEmpty=False,
#                         robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
#             for location in self.getLocations():
#                 self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)


        print('\n3: NAME2 current Present again {}'.format(CommunicationTest.NAME2))
        # make potential response
        voice_sensation6 = self.createSensation(
                                                sensationName='voice_sensation6',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=CommunicationTest.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation6 test', dataId=voice_sensation6.getDataId())
        image_sensation6 = self.createSensation(
                                                sensationName='image_sensation6',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation6 test', dataId=image_sensation6.getDataId())
        item_sensation6 = self.createSensation(
                                                sensationName='item_sensation6',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation6 test', dataId=item_sensation6.getDataId())
        item_sensation6.associate(sensation=voice_sensation6)
        item_sensation6.associate(sensation=image_sensation6)
        voice_sensation6.associate(sensation=image_sensation6)

        Wall_E_item_sensation_present3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present3',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_1,
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
       
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present3)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() should be 2')

        if isPresentRobot:
            # We expect to get communication to a Item.name and request to consult other robot what to say.
            # But because we already wait a reply, we expect nothing
            muscleVoice = self.expect(isWait=isWait,
                        name='isPresentRobot Name2 present, response 6', isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation6, isExactMuscleImage=True,
                        muscleVoice=voice_sensation6, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        communicationItem=Wall_E_item_sensation_present3, isExactCommunicationItem=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))
            # # simulate Playback
            # robotStateSensation=self.createSensation(
            #                                         sensationName='voice_sensation6Played',
            #                                         robot=communication,
            #                                         memoryType=Sensation.MemoryType.Sensory,
            #                                         sensationType=Sensation.SensationType.RobotState,
            #                                         robotType=Sensation.RobotType.Sense,
            #                                         robotState = Sensation.RobotState.CommunicationVoicePlayed,
            #                                         locations=self.getLocations())
            # robotStateSensation.associate(muscleVoice)
            #
            # self.doProcess(robot=communication, sensation=robotStateSensation)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Entering, response 6, CommunicationWaitingResponse', isEmpty=False,
            #             robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # # To test other Communication Robots functionality we must make a trick and change this Sensation MainNames
            # # so this Robot think that Sensation comes fromother Robot, not it self
            # self.communicationItem.setMainNames(mainNames=self.OTHERMAINNAMES)
            #
            # # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # # We will get same result, but no ask-sensation
            # communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            # self.expect(isWait=isWait,
            #             name='isPresentRobot Name2 present, reply to communicationItem, response 6', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
            #             communicationImage=image_sensation6, isExactCommunicationImage=True,
            #             communicationVoice=voice_sensation6, isExactCommunicationVoice=True,
            #             communicationItem=None)
        else:
            # We still wait response
            muscleVoice = self.expect(isWait=isWait,
                        name= "Name2 present, response 6", isEmpty=True, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        muscleImage=image_sensation6, isExactMuscleImage=True,
                        muscleVoice=voice_sensation6, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))#(Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingResponse))

            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse,
                                 "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationWaitingResponse)))
#             # simulate Playback
#             robotStateSensation=self.createSensation(
#                                                     sensationName='voice_sensation6Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotType=Sensation.RobotType.Sense,
#                                                     robotState = Sensation.RobotState.CommunicationVoicePlayed,
#                                                     locations=self.getLocations())
#             robotStateSensation.associate(muscleVoice)
# 
#             self.doProcess(robot=communication, sensation=robotStateSensation)
#             self.expect(isWait=isWait,
#                         name='Name2 present, response 6, CommunicationWaitingResponse', isEmpty=False,
#                         robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
#             for location in self.getLocations():
#                 self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
#             
            

        # We should remove remote Robot Item-presence to test this local Absent feature
        if isPresentRobot and Robot.GLOBAL_LOCATION in communication.getMemory()._presentItemSensations:
            del communication.getMemory()._presentItemSensations[Robot.GLOBAL_LOCATION]
        
        print('\n NAME2 current Absent {}'.format(CommunicationTest.NAME2))
        Wall_E_item_sensation_absent2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent2',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME2,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent2 test', dataId=Wall_E_item_sensation_absent2.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent2)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(isWait=isWait,
                    name='Absent NAME2', isEmpty=False, #isSpoken=False, isHeard=False,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isNegativeFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationDelay, Sensation.RobotState.CommunicationNoResponseHeard))
        for location in self.getLocations():
            self.assertTrue(self.communication.itemConversations[location].robotState in (Sensation.RobotState.CommunicationDelay, Sensation.RobotState.CommunicationNoResponseHeard))
    

        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTest.NAME))
        Wall_E_item_sensation_absent3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent3',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent3 test', dataId=Wall_E_item_sensation_absent3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot       
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent3)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 0')
        self.expect(isWait=isWait,
                    name='Absent NAME', isEmpty=False,
                    robotStates = (Sensation.RobotState.CommunicationEnded))#isSpoken=False, isHeard=False, isVoiceFeeling=False)
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
       

    '''
    TensorfloClassification produces
    Item.name Working Out
    Sensations outside Robot are in same Robot.mainNames and robotType=Sensation.RobotType.Sense
    so this test is same than without parameters
    '''    
    def doTest_2_Presense(self, communication, isWait):
        self.do_test_Presense(communication=communication, isWait=isWait, mainNames=self.MAINNAMES, robotType=Sensation.RobotType.Sense)
        
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in other Robot.mainNames and robotType=Sensation.RobotType.Communication
    so this test result should  same than with test where robotType=Sensation.RobotType.Sense,
    because Communication should handle those sensation equally, when Robot.mainNames differ
    
    Still there is difference with RoboState. If robotType==Sensation.RobotType.Communication
    it means, that this robot is consult-robot
    '''    
    def doTest_3_Presense(self, communication, isWait):
        self.do_test_Presense(communication=communication, isWait=isWait, mainNames=self.OTHERMAINNAMES, robotType=Sensation.RobotType.Communication)

    '''
    TensorfloClöassafication produces
    Item.name Working Out
    
    At his moment only TenserflowClassification creates SEnsationType.Item presense
    Sensations and RobotType is always Sense. Test same way
    
    TODO This test logic is obsolote, because we don't get Presence items repeated, but
    Present and the Absent and so on.
    
    '''    
    def do_test_Presense(self, communication, isWait, mainNames, robotType):
        print('\ndo_test_Presense {} {}'.format(mainNames, robotType))

        # robot setup 
        # Because current implementation does not forget said sensation, when conversation end
        # We have in this run old sensations left from earlier runs, so we must clens these
        for location in communication.getLocations():
            del communication.itemConversations[location].spokedDataIds[:]
            del communication.itemConversations[location].heardDataIds[:]
          
        # TODO is this needed, because we don't use to create Sensations
        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("Present name {}".format(sensation.getName()))        
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 0')
      
        history_sensationTime = systemTime.time() -2*max(CommunicationTest.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\ntoo old_Entering {}'.format(CommunicationTest.NAME))
        Wall_E_item_sensation1 = self.createSensation(
                                                sensationName='Wall_E_item_sensation1',
                                                robot=communication,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation1 test', dataId=Wall_E_item_sensation1.getDataId())
        self.doProcess(robot=communication, sensation=Wall_E_item_sensation1)
        # Communication can not respond, because there is not Voice Items, its could use
        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("Entering, Too old response after process, Present name {}".format(sensation.getName()))
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        # Should have now one item present?
        # No, because Memory does care about times.
        # and Sensation time is too old to fit Communication time window
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 0')

        self.expect(isWait=isWait,
                    name='Entering, Too old item, empty', isEmpty=True)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory()..getAllPresentItemSensations() should be 0')
        for location in self.getLocations():
            self.assertTrue(self.communication.itemConversations[location].robotState in  [Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationNotStarted])

        # Create here present items and then make it absent
        print('\ncurrent time Entering {}'.format(CommunicationTest.NAME))
        Wall_E_item_sensation1 = self.createSensation(
                                                sensationName='Wall_E_item_sensation1',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='current Wall_E_item_sensation1 test', dataId=Wall_E_item_sensation1.getDataId())
        self.doProcess(robot=communication, sensation=Wall_E_item_sensation1)
        # Communication can not respond, because there there is no responses in the memory
        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("Entering, currentresponse after process, Present name {}".format(sensation.getName()))
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')

        self.expect(isWait=isWait,
                    name='Entering, current item', isEmpty=False,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationOn, Sensation.RobotState.CommunicationNoResponseToSay))
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory()..getAllPresentItemSensations() should be 1')
        for location in self.getLocations():
            self.assertTrue(self.communication.itemConversations[location].robotState in  (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationNoResponseToSay))#Sensation.RobotState.CommunicationNotStarted])
        
        
        ###########
        # Make this item absent
        
        absent_item_sensation1 = self.createSensation(
                                                sensationName='absent_item_sensation1',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='absent_item_sensation1 test', dataId=absent_item_sensation1.getDataId())

        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("absent1 after process, Present name {}".format(sensation.getName()))
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 0')

        self.doProcess(robot=communication, sensation=absent_item_sensation1)

        # Communication should be ended, because only present item is now absent 
        self.expect(isWait=isWait,
                    name='absent1, CommunicationEnded', isEmpty=False,
                    robotStates = (Sensation.RobotState.CommunicationEnded))
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory()..getAllPresentItemSensations() should be 0')
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)

        
              
        print('\ncurrent Entering {}'.format(CommunicationTest.NAME))
        # there is no potential response
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        
        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("absent1 after process, Present name {}".format(sensation.getName()))
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')

        self.doProcess(robot=communication, sensation=item_sensation1)
        # there is no potential response
        # We get Voice, if Communication can respond but it can't
        # TODO Check this, self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay but
        # robotStates = Sensation.RobotState.CommunicationWaiting
        self.expect(isWait=isWait,
                    name='current Entering, no response', isEmpty=False,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationNoResponseToSay))
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay)
       
         # We hear voice and see image
        voice_sensation1 = self.createSensation(
                                                sensationName='voice_sensation1',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTest.VOICEDATA2,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation1 test', dataId=voice_sensation1.getDataId())
        self.assertEqual(len(item_sensation1.getAssociations()), 4)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')

        self.doProcess(robot=communication, sensation=voice_sensation1)
        # TODO enable and reimplement next 2 lines, because 
        # heardDataIds is location based now       
#         self.assertEqual(len(communication.heardDataIds), 1)
#         self.assertEqual(communication.heardDataIds[0], voice_sensation1.getDataId())
        # We get Voice, if Communication can respond but it can't, we hear it in this discussion
        if robotType == Sensation.RobotType.Sense:
            self.expect(isWait=isWait,
                        name='voice_sensation1, no response', isEmpty=True,#False,
                        robotStates = (Sensation.RobotState.CommunicationOn, Sensation.RobotState.CommunicationNoResponseToSay))
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay)
        elif robotType == Sensation.RobotType.Communication:
            self.expect(isWait=isWait,
                        name='voice_sensation1, empty', isEmpty=True)
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
       
 
        # TODO We don't get SensationType.Image from Item.name (==person)
        # so this test is very obsolete
        # remove test? 
        image_sensation1 = self.createSensation(
                                                sensationName='image_sensation1',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation1 test', dataId=image_sensation1.getDataId())
        print ("\n\n===== len(item_sensation1.getAssociations()) {}\n\n".format(len(item_sensation1.getAssociations())))
        self.assertTrue(len(item_sensation1.getAssociations()) in [4,5,6], "len(item_sensation1.getAssociations() should be 5 or 6, not {}".format(len(item_sensation1.getAssociations())))
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
 
#         communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=image_sensation1)
        self.doProcess(robot=communication, sensation=image_sensation1)
        self.expect(isWait=isWait,
                    name='image_sensation1, empty', isEmpty=True)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay)
 
        # Absent
        # remove this one
        absent_item_sensation2 = self.createSensation(
                                                sensationName='absent_item_sensation2',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='absent_item_sensation2 test', dataId=absent_item_sensation2.getDataId())

        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("absent1 after process, Present name {}".format(sensation.getName()))
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))
        self.assertFalse(communication.getMemory().hasItemsPresence(), 'should not have presence')

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 0')

        self.doProcess(robot=communication, sensation=absent_item_sensation2)
        self.expect(isWait=isWait,
                    name='absent1, CommunicationEnded', isEmpty=False,
                    robotStates = (Sensation.RobotState.CommunicationEnded))
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory()..getAllPresentItemSensations() should be 0')
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
       
        # Now we have heard something when CommunicationTest.NAME was present       
        # We have present item
        
        Wall_E_item_sensation2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation2',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation2 test', dataId=Wall_E_item_sensation2.getDataId())
        self.assertTrue(len(Wall_E_item_sensation1.getAssociations()) in  (1,2,3))
        print("\nitem_sensation1.getAssociations() {}\n".format(len(item_sensation1.getAssociations())))
        self.assertTrue(len(item_sensation1.getAssociations()) in (4,5,6,7), "len(item_sensation1.getAssociations()) should be 5,6 or 7, not {}".format(len(item_sensation1.getAssociations())))
        self.assertEqual(len(Wall_E_item_sensation2.getAssociations()), 1)
        
        for sensation in communication.getMemory().getAllPresentItemSensations():
            print("Wall_E_item_sensation2 before process, Present name {}".format(sensation.getName()))
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("Wall_E_item_sensation2 before process present in location {} name {}".format(location, itemSensation.getName()))

        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        
        #simulate TensorFlowClassification send presence item to MainRobot
        # should still have only CommunicationTest.NAME present
        
        # process
        print("process Wall_E_item_sensation2")
#         communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation2)
        self.doProcess(robot=communication, sensation=Wall_E_item_sensation2)
        #  we will get response and 4 associations are created more
        self.assertTrue(len(Wall_E_item_sensation1.getAssociations()) in (1,2,3))
        print("\nitem_sensation1.getAssociations() {}\n".format(len(item_sensation1.getAssociations())))
        self.assertTrue(len(item_sensation1.getAssociations())in (4, 5,6,7,8, 9), "len(item_sensation1.getAssociations()) should be 4, 5,6,7,8, 9, not {}".format(len(item_sensation1.getAssociations())))
        print("len(Wall_E_item_sensation2.getAssociations() {}".format(len(Wall_E_item_sensation2.getAssociations())))
        self.assertTrue(len(Wall_E_item_sensation2.getAssociations()) in (2,3,4,5,6) , "len(Wall_E_item_sensation2.getAssociations()) should be 5 or 6, not {}".format(len(Wall_E_item_sensation2.getAssociations())))
#
        # We can useimage_sensation1,
        # but not voice_sensation1 after Absent,
        # because it is still in heard voices.
        # it is hard to communicate with person only with images, so we have problems with
        # Communication implementation., We should get Sensation.RobotState.CommunicationNoResponseToSay
        muscleVoice = self.expect(isWait=isWait,
                    name='Wall_E_item_sensation2, no feeling', isEmpty=False,
                    #muscleImage=image_sensation1, isExactMuscleImage=True,
                    #muscleVoice=voice_sensation1, isExactMuscleVoice=True,
                    robotStates = (Sensation.RobotState.CommunicationNoResponseToSay, Sensation.RobotState.CommunicationWaiting))
                    #robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed,  Sensation.RobotState.CommunicationWaitingResponse))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay,
                             "got {}, expected {}".format(Sensation.getRobotStateString(self.communication.itemConversations[location].robotState), Sensation.getRobotStateString(Sensation.RobotState.CommunicationNoResponseToSay)))
            
        #     # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
        #     # make voice that should be ignored 
        #     voice_sensation_ignored_Wall_E_item_sensation2  = self.createSensation(
        #                                             sensationName='voice_sensation_ignored_Wall_E_item_sensation2',
        #                                             robot=communication,
        #                                             memoryType=Sensation.MemoryType.Sensory,
        #                                             sensationType=Sensation.SensationType.Voice,
        #                                             robotType=Sensation.RobotType.Sense,
        #                                             data=CommunicationTest.VOICEDATA_IGNORED,
        #                                             locations=self.getLocations())
        #     self.assertTrue(voice_sensation_ignored_Wall_E_item_sensation2.isForgettable())
        #     self.printSensationNameById(note='voice_sensation_ignored_Wall_E_item_sensation2', dataId=voice_sensation_ignored_Wall_E_item_sensation2.getDataId())
        #     communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored_Wall_E_item_sensation2)
        #     self.expect(isWait=isWait,
        #                 name='Wall_E_item_sensation2, no feeling, voice_sensation_ignored_Wall_E_item_sensation2 should be ignored',
        #                 isEmpty=True)
        #
        # # simulate Playback
        # robotStateSensation=self.createSensation(
        #                                             sensationName='voice_sensation1Played',
        #                                             robot=communication,
        #                                             memoryType=Sensation.MemoryType.Sensory,
        #                                             sensationType=Sensation.SensationType.RobotState,
        #                                             robotType=Sensation.RobotType.Sense,
        #                                             robotState = Sensation.RobotState.CommunicationVoicePlayed,
        #                                             locations=self.getLocations())
        # robotStateSensation.associate(muscleVoice)
        #
        # self.doProcess(robot=communication, sensation=robotStateSensation)
        # self.expect(isWait=isWait,
        #             name='Wall_E_item_sensation2, CommunicationWaitingResponse', isEmpty=False,
        #             robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        # for location in self.getLocations():
        #     self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
        
        # Now we got answer and we will get feeling pending, good or bad, depending if Robot hears an answer from us
        # of if another item cones present
        
        # No communication robot
#                     communicationImage=image_sensation1, isExactCommunicationImage=True,
#                     communicationVoice=voice_sensation1, isExactCommunicationVoice=True)
        
        
        print('\n4: current Present {}'.format(CommunicationTest.NAME))

        # voice_sensation_ignored_currentPresent before present item
        voice_sensation_ignored_currentPresent = self.createSensation(
                                                sensationName='voice_sensation_ignored_currentPresent',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTest.VOICEDATA_IGNORED,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation_ignored_currentPresent test', dataId=voice_sensation_ignored_currentPresent.getDataId())
        self.assertEqual(len(voice_sensation_ignored_currentPresent.getAssociations()), 2)
        self.assertEqual(len(voice_sensation_ignored_currentPresent.getAssociations()), 2)
        
        Wall_E_item_sensation3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation3',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation3 test', dataId=Wall_E_item_sensation3.getDataId())

        self.assertTrue(len(Wall_E_item_sensation1.getAssociations()) in (1,2,3)) # present in location ''
        self.assertTrue(len(Wall_E_item_sensation2.getAssociations()) in (4,5,6,7,8), "len(Wall_E_item_sensation2.getAssociations()) should be 4,5,6,7,8, not {}".format(len(Wall_E_item_sensation2.getAssociations())))
        self.assertTrue(len(Wall_E_item_sensation3.getAssociations()) in (1,2,3,4))
        print("len(item_sensation1.getAssociations()) {}".format(len(item_sensation1.getAssociations())))
        self.assertTrue(len(item_sensation1.getAssociations()) in (4,5,6,7,8,9), "len(item_sensation1.getAssociations()) should be 4,5,6,7,8,9, not {}".format(len(item_sensation1.getAssociations())))
        
        self.assertEqual(len(image_sensation1.getAssociations()), 2)
        # TODO is test code still valid
        # self.assertEqual(len(voice_sensation1.getAssociations()), 2)
        self.assertEqual(len(voice_sensation1.getAssociations()), 0)
       
        #simulate TensorFlowClassification send presence item to MainRobot
        # should still have only CommunicationTest.NAME present
        
        for location in communication.getMemory()._presentItemSensations.keys():
            for itemSensation in communication.getMemory()._presentItemSensations[location].values():
                print("present in location {} name {}".format(location, itemSensation.getName()))
        
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
       
        
        # make potential response
        item_sensation2 = self.createSensation(
                                                sensationName='item_sensation2',
                                                robot=communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation2 test', dataId=item_sensation2.getDataId())
        self.assertTrue(len(item_sensation2.getAssociations()) in (1,2,3,4))
        
        voice_sensation2 = self.createSensation(
                                                sensationName='voice_sensation2',
                                                robot=communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTest.VOICEDATA2,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
        self.assertEqual(len(voice_sensation2.getAssociations()), 2)
        self.assertTrue(len(item_sensation2.getAssociations()) in (2,3,4,5))
        
        image_sensation2 = self.createSensation(
                                                sensationName='image_sensation2',
                                                robot=communication,
                                                #time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        self.assertEqual(len(image_sensation2.getAssociations()), 2)
        self.assertTrue(len(item_sensation2.getAssociations()) in (2,3,4,5,6),"len(item_sensation2.getAssociations() not in (2,3,4,5,6), but is {}".format(len(item_sensation2.getAssociations())))
        
        #simulate TensorFlowClassification send presence item to MainRobot
        #robot.tracePresents(Wall_E_item_sensation3) # presence
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')

        # process       
        self.doProcess(robot=communication, sensation=Wall_E_item_sensation3)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')

        # TODO What we test here?
        # voice_sensation_ignored_currentPresent was assigned to item CommunicationTest.NAME
        # before, so we get it now, not voice_sensation2 as in this test previous version
        # should be OK?
        #
        # test, that if we get new present Item it is ignored
        # ???? We can now respond ????      
        # self.expect(isWait=isWait,
        #             name='Present, response, feeling', isEmpty=False)
        # pending feeling is got
        # next pending feeling
        muscleVoice = self.expect(isWait=isWait,
                    name='Present, response, feeling', isEmpty=False,
                    muscleImage=image_sensation2, isExactMuscleImage=True,
                    muscleVoice=voice_sensation2, isExactMuscleVoice=True,#voice_sensation2, 
                    # isVoiceFeeling=True,
                    # isImageFeeling=True,
                    # isPositiveFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
        # TODO test here that itemConversation state is still unchanged
        # for location in self.getLocations():
        #     self.assertEqual(self.communication.itemConversations[location].robotState,  Sensation.RobotState.CommunicationWaitingVoicePlayed)

        # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored        
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=voice_sensation_ignored_currentPresent)
        self.expect(isWait=isWait,
                    name='response, Present, response, feeling, voice should be ignored',
                    isEmpty=True)

        # simulate playback
        robotStateSensation=self.createSensation(
                                                    sensationName='voice_sensation2 Played',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.RobotState,
                                                    robotType=Sensation.RobotType.Sense,
                                                    robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                    locations=self.getLocations())
        robotStateSensation.associate(muscleVoice)

        self.doProcess(robot=communication, sensation=robotStateSensation)
        # self.expect(isWait=isWait,
        #                 name='Present, response CommunicationWaitingResponse', isEmpty=False,
        #                 robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        # pending feeling is got
        # next pending feeling
        # final state is CommunicationWaitingResponse
        muscleVoice = self.expect(isWait=isWait,
                    name='Present, response, feeling', isEmpty=False,
                    # muscleImage=image_sensation2, isExactMuscleImage=True,
                    # muscleVoice=voice_sensation2, isExactMuscleVoice=True,
                    # isVoiceFeeling=True,
                    # isImageFeeling=True,
                    # isPositiveFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationWaitingResponse, Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState,  Sensation.RobotState.CommunicationWaitingResponse)
        
        
        print('\n current Absent {}'.format(CommunicationTest.NAME))        
        
        Wall_E_item_sensation4 = self.createSensation(
                                                sensationName='Wall_E_item_sensation4',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation4 test', dataId=Wall_E_item_sensation4.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 1')

        #process              
        self.doProcess(robot=communication, sensation=Wall_E_item_sensation4)
       # TODO enable and reimplement next line, because 
        # heardDataIds is location based now       
#         self.assertEqual(len(communication.heardDataIds), 0)

        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        # pending feeling is got
        # no next pending feeling
        self.expect(isWait=isWait,
                    name='Absent, feeling', isEmpty=False, isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationEnded))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
        
        # conversation should be ended, when last Item is absent
        # current implementation does not forget spoked sensations, so we can't now test this
        # enable, if implementation changes
#         for location in communication.getLocations():
#             self.assertEqual(len(communication.itemConversations[location].spokedDataIds),0, "spokedDataIds {}".format(location))
#             self.assertEqual(len(communication.itemConversations[location].heardDataIds),0, "heardDataIds {}".format(location))
        
 
        # NAME with NAME2
        
        # should wait here for conversation delay
        
        print('\n NAME current Entering {}',format(CommunicationTest.NAME))
        # make potential response
        currentEnteringVoiceSensation = self.createSensation(
                                                sensationName='currentEnteringVoiceSensation',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                data=CommunicationTest.VOICEDATA3,
                                                locations=self.getLocations())
        self.printSensationNameById(note='currentEnteringVoiceSensation test', dataId=currentEnteringVoiceSensation.getDataId())
        currentEnteringImageSensation = self.createSensation(
                                                sensationName='currentEnteringImageSensation',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=mainNames,
                                                locations=self.getLocations())
        self.printSensationNameById(note='currentEnteringImageSensation test', dataId=currentEnteringImageSensation.getDataId())
        item_sensation3 = self.createSensation(
                                                sensationName='item_sensation3',
                                                robot=communication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,                                                
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation3 test', dataId=item_sensation3.getDataId())
        
        # make entering item and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation5 = self.createSensation(
                                                sensationName='Wall_E_item_sensation5',
                                                robot=communication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                mainNames=mainNames,
                                                name=CommunicationTest.NAME,
                                                score=CommunicationTest.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation5 test', dataId=Wall_E_item_sensation5.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #communication.tracePresents(Wall_E_item_sensation5) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 2')

        #  We are starting new conversation so there should not be spokedDataIds or heardDataIds
        # current implementation does not forget spoked Sensations
        # Enable if implementation changes
#         for location in communication.getLocations():
#             self.assertEqual(len(communication.itemConversations[location].spokedDataIds),0)
#             self.assertEqual(len(communication.itemConversations[location].heardDataIds),0)

        #process                      
        self.doProcess(robot=communication, sensation=Wall_E_item_sensation5)
        self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        
        # NOTE rest of the test depends on
        # if robotType=Sensation.RobotType.Sense, we have used all out voices and images and have nothing to say
        # if robotType=Sensation.RobotType.Communication, it can always give best suggestions what to say
        
        # TODO Sometimes Robot finds something to speak, but not always. Why?

        if robotType == Sensation.RobotType.Sense:
            muscleVoice = self.expect(isWait=isWait,
#                        muscleVoice = currentEnteringVoiceSensation,
#                        muscleImage = currentEnteringImageSensation,
                        name='Present Name 2, new Conversation starts, no feeling', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationNoResponseToSay, Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
            if muscleVoice != None:
                for location in self.getLocations():
                    self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed, Sensation.getRobotStateString(self.communication.itemConversations[location].robotState))
                # simulate playback
                robotStateSensation=self.createSensation(
                                                            sensationName='voice_sensation played',
                                                            robot=communication,
                                                            memoryType=Sensation.MemoryType.Sensory,
                                                            sensationType=Sensation.SensationType.RobotState,
                                                            robotType=Sensation.RobotType.Sense,
                                                            robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                            locations=self.getLocations())
                robotStateSensation.associate(muscleVoice)
        
                self.doProcess(robot=communication, sensation=robotStateSensation)
                muscleVoice = self.expect(isWait=isWait,
                            name='Present, response, feeling', isEmpty=False,
                            # muscleImage=None,#image_sensation2,
                            # muscleVoice=None,#voice_sensation2, 
                            # isVoiceFeeling=True,
                            # isImageFeeling=True,
                            # isPositiveFeeling=True,
                            robotStates = (Sensation.RobotState.CommunicationWaitingResponse, Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
                for location in self.getLocations():
                    self.assertEqual(self.communication.itemConversations[location].robotState,  Sensation.RobotState.CommunicationWaitingResponse)
            else:
                for location in self.getLocations():
                    self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay, Sensation.getRobotStateString(self.communication.itemConversations[location].robotState))
            
            print('\n NAME2 current Entering {}'.format(CommunicationTest.NAME2))
            # make potential response
            
            Eva_item_sensation = self.createSensation(
                                                    sensationName='Eva_item_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_2,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
            
            Eva_voice_sensation = self.createSensation(
                                                    sensationName='Eva_voice_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    data=CommunicationTest.VOICEDATA4,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_voice_sensation test', dataId=Eva_voice_sensation.getDataId())
            Eva_image_sensation = self.createSensation(
                                                    sensationName='Eva_image_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_image_sensation test', dataId=Eva_image_sensation.getDataId())
            #simulate TensorFlowClassification send presence item to MainRobot
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 3')
    
            # make entering and process
            Wall_E_item_sensation6 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation6',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_2,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation6 test', dataId=Wall_E_item_sensation6.getDataId())
            #simulate TensorFlowClassification send presence item to MainRobot
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 3')
    
    #         communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation6)
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation6)
            # 
            # pending feeling is got
            # next pending feeling
            muscleVoice = self.expect(isWait=isWait,
                        name='Entering Name2, change in presentation', isEmpty=False,
                        muscleImage=Eva_image_sensation, isExactMuscleImage=True,
                        muscleVoice=Eva_voice_sensation, isExactMuscleVoice=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed)
                
            # simulate playback
            robotStateSensation=self.createSensation(
                                                        sensationName='Eva_voice_sensationPlayed',
                                                        robot=communication,
                                                        memoryType=Sensation.MemoryType.Sensory,
                                                        sensationType=Sensation.SensationType.RobotState,
                                                        robotType=Sensation.RobotType.Sense,
                                                        robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                        locations=self.getLocations())
            robotStateSensation.associate(muscleVoice)

            self.doProcess(robot=communication, sensation=robotStateSensation)
            self.expect(isWait=isWait,
                        name='Entering Name2, change in presentation CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
            
                          
            print('\n5: NAME2 current Present {}'.format(CommunicationTest.NAME2))
            # added make potential response
            Eva_item_sensation = self.createSensation(
                                                    sensationName='Eva_item_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,                                                
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_2,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
            Eva_voice_sensation2 = self.createSensation(
                                                    sensationName='Eva_voice_sensation2',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    data=CommunicationTest.VOICEDATA5,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_voice_sensation2 test', dataId=Eva_voice_sensation2.getDataId())
            Eva_image_sensation = self.createSensation(
                                                    sensationName='Eva_image_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_image_sensation test', dataId=Eva_image_sensation.getDataId())
    
            Wall_E_item_sensation7 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation7',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,                                                
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Present,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation7 test', dataId=Wall_E_item_sensation7.getDataId())

            #simulate TensorFlowClassification send presence item to MainRobot       
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation7)
            # pending feeling is got
            # next pending feeling
            # We don't get anything because we are waiting response and now we gor nest present Items and Communication should not react to it
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() should be 3')
            muscleVoice = self.expect(isWait=isWait,
                        name='Present Name 2, change in presentation, feeling', isEmpty=True,
                        muscleImage=Eva_image_sensation, isExactMuscleImage=True,
                        muscleVoice=Eva_voice_sensation2, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True,
                        robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)

            # # simulate playback
            # robotStateSensation=self.createSensation(
            #                                             sensationName='Eva_voice_sensationPlayed',
            #                                             robot=communication,
            #                                             memoryType=Sensation.MemoryType.Sensory,
            #                                             sensationType=Sensation.SensationType.RobotState,
            #                                             robotType=Sensation.RobotType.Sense,
            #                                             robotState = Sensation.RobotState.CommunicationVoicePlayed,
            #                                             locations=self.getLocations())
            # robotStateSensation.associate(muscleVoice)
            #
            # self.doProcess(robot=communication, sensation=robotStateSensation)
            # self.expect(isWait=isWait,
            #             name='Present Name 2, change in presentation CommunicationWaitingResponse', isEmpty=False,
            #             robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # for location in self.getLocations():
            #     self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)

 
            # TODO Test is broken, because we are still waiting response and
            # If we test with prenent items, we should not get anything   
            # print('\n6: NAME2 current Present again {}'.format(CommunicationTest.NAME2))
            # # make potential response to history
            # # Note, this is right way to do so, correct test above
            # # time change changes what we will get so take your time to correct test
            # Eva_voice_sensation2 = self.createSensation(
            #                                         sensationName='Eva_voice_sensation2',
            #                                         robot=communication,
            #                                         time=self.history_sensationTime,
            #                                         memoryType=Sensation.MemoryType.Sensory,
            #                                         sensationType=Sensation.SensationType.Voice,
            #                                         robotType=Sensation.RobotType.Sense,
            #                                         mainNames=mainNames,
            #                                         data=CommunicationTest.VOICEDATA4,
            #                                         locations=self.getLocations())
            # self.printSensationNameById(note='Eva_voice_sensation2 test', dataId=Eva_voice_sensation2.getDataId())
            # Eva_image_sensation2 = self.createSensation(
            #                                         sensationName='Eva_image_sensation2',
            #                                         robot=communication,
            #                                         time=self.history_sensationTime,
            #                                         memoryType=Sensation.MemoryType.Sensory,
            #                                         sensationType=Sensation.SensationType.Image,
            #                                         mainNames=mainNames,
            #                                         robotType=robotType,
            #                                         locations=self.getLocations())
            # self.printSensationNameById(note='Eva_image_sensation2 test', dataId=Eva_image_sensation2.getDataId())
            # Eva_item_sensation = self.createSensation(
            #                                         sensationName='Eva_item_sensation',
            #                                         robot=communication,
            #                                         time=self.history_sensationTime,
            #                                         memoryType=Sensation.MemoryType.Working,
            #                                         sensationType=Sensation.SensationType.Item,
            #                                         robotType=Sensation.RobotType.Sense,
            #                                         mainNames=mainNames,
            #                                         name=CommunicationTest.NAME2,
            #                                         score=CommunicationTest.SCORE_3,
            #                                         presence=Sensation.Presence.Entering,
            #                                         locations=self.getLocations())
            # self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
            # Eva_item_sensation.associate(sensation=Eva_voice_sensation2, feeling = Sensation.Feeling.Good)
            # Eva_item_sensation.associate(sensation=Eva_image_sensation2, feeling = Sensation.Feeling.Good)
            # Eva_voice_sensation2.associate(sensation=Eva_image_sensation2, feeling = Sensation.Feeling.Good)
            #
            # Wall_E_item_sensation8 = self.createSensation(
            #                                         sensationName='Wall_E_item_sensation8',
            #                                         robot=communication,
            #                                         memoryType=Sensation.MemoryType.Working,
            #                                         sensationType=Sensation.SensationType.Item,
            #                                         robotType=Sensation.RobotType.Sense,
            #                                         mainNames=mainNames,
            #                                         name=CommunicationTest.NAME2,
            #                                         score=CommunicationTest.SCORE_1,
            #                                         presence=Sensation.Presence.Present,
            #                                         locations=self.getLocations())
            # self.printSensationNameById(note='Wall_E_item_sensation8 test', dataId=Wall_E_item_sensation8.getDataId())
            # #simulate TensorFlowClassification send presence item to MainRobot
            #
            # self.doProcess(robot=communication, sensation=Wall_E_item_sensation8)
            # self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() should be 3')
            # # We don't get any Communication Sensations, because response limit is expected
            # # TODO Communication Sensation functionality will be changed
            # # pending feeling is got
            # # next pending feeling
            # muscleVoice = self.expect(isWait=isWait,
            #             name='Present NAME2 again basic change in presentation, feeling', isEmpty=False,
            #             muscleImage=Eva_image_sensation2, isExactMuscleImage=True,
            #             muscleVoice=Eva_voice_sensation2, isExactMuscleVoice=True,
            #             communicationImage=None,
            #             communicationVoice=None,
            #             isVoiceFeeling=True,
            #             isImageFeeling=True,
            #             isPositiveFeeling=True,
            #             robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
            # for location in self.getLocations():
            #     self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed)
            #
            # # simulate playback
            # robotStateSensation=self.createSensation(
            #                                             sensationName='Eva_voice_sensation2Played',
            #                                             robot=communication,
            #                                             memoryType=Sensation.MemoryType.Sensory,
            #                                             sensationType=Sensation.SensationType.RobotState,
            #                                             robotType=Sensation.RobotType.Sense,
            #                                             robotState = Sensation.RobotState.CommunicationVoicePlayed,
            #                                             locations=self.getLocations())
            # robotStateSensation.associate(muscleVoice)
            #
            # self.doProcess(robot=communication, sensation=robotStateSensation)
            # self.expect(isWait=isWait,
            #             name='Present NAME2 again basic change in presentation CommunicationWaitingResponse', isEmpty=False,
            #             robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
            # for location in self.getLocations():
            #     self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
            
            print('\n NAME2 current Absent {}'.format(CommunicationTest.NAME2))
            Wall_E_item_sensation9 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation9',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Absent,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation9 test', dataId=Wall_E_item_sensation9.getDataId())
           
            #simulate TensorFlowClassification send presence item to MainRobot
    
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation9)
            sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
            print("test is sleeping " + str(sleepTime) + " until continuing")       
            systemTime.sleep(sleepTime)
    
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
            # pending feeling is got
            # no next pending feeling
            self.expect(isWait=isWait,
                        name='Absent NAME2, feeling', isEmpty=False,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isNegativeFeeling=True,
                        robotStates = (Sensation.RobotState.CommunicationDelay, Sensation.RobotState.CommunicationNoResponseHeard))
            for location in self.getLocations():
                self.assertTrue(self.communication.itemConversations[location].robotState in (Sensation.RobotState.CommunicationDelay, Sensation.RobotState.CommunicationNoResponseHeard))
        
    
            # last item.name will we be absent
            print('\n NAME current Absent {}'.format(CommunicationTest.NAME))
            Wall_E_item_sensation10 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation10',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    name=CommunicationTest.NAME,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Absent,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation10 test', dataId=Wall_E_item_sensation10.getDataId())
           #simulate TensorFlowClassification send presence item to MainRobot
           
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation10)
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
            self.expect(isWait=isWait,
                        name='Absent NAME', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationEnded))
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
        elif robotType == Sensation.RobotType.Communication:
            self.expect(isWait=isWait,
                        name='Present Name 2, new Conversation starts, no feeling', isEmpty=False,
                        muscleImage=currentEnteringImageSensation, isExactMuscleImage=False,
                        muscleVoice=currentEnteringVoiceSensation, isExactMuscleVoice=False,
                        robotStates = (Sensation.RobotState.CommunicationWaiting))
            for location in self.getLocations():
                self.assertEqual(self.communication.robotConversations[location].robotState, Sensation.RobotState.CommunicationOn)
            
            print('\n NAME2 current Entering {}'.format(CommunicationTest.NAME2))
            # make potential response
            
            Eva_item_sensation = self.createSensation(
                                                    sensationName='Eva_item_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_2,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
            
            Eva_voice_sensation = self.createSensation(
                                                    sensationName='Eva_voice_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    data=CommunicationTest.VOICEDATA4,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_voice_sensation test', dataId=Eva_voice_sensation.getDataId())
            Eva_image_sensation = self.createSensation(
                                                    sensationName='Eva_image_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_image_sensation test', dataId=Eva_image_sensation.getDataId())
            #simulate TensorFlowClassification send presence item to MainRobot
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 3')
    
            # make entering and process
            Wall_E_item_sensation6 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation6',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_2,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation6 test', dataId=Wall_E_item_sensation6.getDataId())
            #simulate TensorFlowClassification send presence item to MainRobot
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 3')
    
    #         communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation6)
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation6)
            # pending feeling is got
            # next pending feeling
            self.expect(isWait=isWait,
                        name='Entering Name2, change in presentation', isEmpty=False,
                        muscleImage=Eva_image_sensation, isExactMuscleImage=True,
                        muscleVoice=Eva_voice_sensation, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationOn)
            
            print('\n7: NAME2 current Present {}'.format(CommunicationTest.NAME2))
            # added make potential response
            Eva_item_sensation = self.createSensation(
                                                    sensationName='Eva_item_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,                                                
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_2,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
            Eva_voice_sensation = self.createSensation(
                                                    sensationName='Eva_voice_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    data=CommunicationTest.VOICEDATA4,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_voice_sensation test', dataId=Eva_voice_sensation.getDataId())
            Eva_image_sensation = self.createSensation(
                                                    sensationName='Eva_image_sensation',
                                                    robot=communication,
                                                    #time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=robotType,
                                                    mainNames=mainNames,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_image_sensation test', dataId=Eva_image_sensation.getDataId())
    
            Wall_E_item_sensation7 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation7',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,                                                
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Present,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation7 test', dataId=Wall_E_item_sensation7.getDataId())
            #simulate TensorFlowClassification send presence item to MainRobot       

            self.doProcess(robot=communication, sensation=Wall_E_item_sensation7)
            # pending feeling is got
            # next pending feeling
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() should be 3')
            self.expect(isWait=isWait,
                        name='Present Name 2, change in presentation, feeling', isEmpty=False,
                        muscleImage=Eva_image_sensation, isExactMuscleImage=True,
                        muscleVoice=Eva_voice_sensation, isExactMuscleVoice=True,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationOn)
    
            print('\n8: NAME2 current Present again {}'.format(CommunicationTest.NAME2))
            # make potential response to history
            # Note, this is right way to do so, correct test above
            # time change changes what we will get so take your time to correct test
            Eva_voice_sensation2 = self.createSensation(
                                                    sensationName='Eva_voice_sensation2',
                                                    robot=communication,
                                                    time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    data=CommunicationTest.VOICEDATA4,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_voice_sensation2 test', dataId=Eva_voice_sensation2.getDataId())
            Eva_image_sensation2 = self.createSensation(
                                                    sensationName='Eva_image_sensation2',
                                                    robot=communication,
                                                    time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Image,
                                                    mainNames=mainNames,
                                                    robotType=robotType,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_image_sensation2 test', dataId=Eva_image_sensation2.getDataId())
            Eva_item_sensation = self.createSensation(
                                                    sensationName='Eva_item_sensation',
                                                    robot=communication,
                                                    time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_3,
                                                    presence=Sensation.Presence.Entering,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Eva_item_sensation test', dataId=Eva_item_sensation.getDataId())
            Eva_item_sensation.associate(sensation=Eva_voice_sensation2, feeling = Sensation.Feeling.Good)
            Eva_item_sensation.associate(sensation=Eva_image_sensation2, feeling = Sensation.Feeling.Good)
            Eva_voice_sensation2.associate(sensation=Eva_image_sensation2, feeling = Sensation.Feeling.Good)
    
            Wall_E_item_sensation8 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation8',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Present,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation8 test', dataId=Wall_E_item_sensation8.getDataId())
            #simulate TensorFlowClassification send presence item to MainRobot
           
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation8)
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 2, 'len(communication.getMemory().getAllPresentItemSensations() should be 3')
            # We don't get any Communication Sensations, becuse response limit is expected
            # TODO Communication Sensation functionality will be changed
            # pending feeling is got
            # next pending feeling
            self.expect(isWait=isWait,
                        name='Present NAME2 again basic change in presentation, feeling', isEmpty=False,
                        muscleImage=Eva_image_sensation2, isExactMuscleImage=True,
                        muscleVoice=Eva_voice_sensation2, isExactMuscleVoice=True,
                        communicationImage=None,
                        communicationVoice=None,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isPositiveFeeling=True)
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationOn)
            
            print('\n NAME2 current Absent {}'.format(CommunicationTest.NAME2))
            Wall_E_item_sensation9 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation9',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    mainNames=mainNames,
                                                    name=CommunicationTest.NAME2,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Absent,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation9 test', dataId=Wall_E_item_sensation9.getDataId())
           
            #simulate TensorFlowClassification send presence item to MainRobot
    
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation9)
            sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
            print("test is sleeping " + str(sleepTime) + " until continuing")       
            systemTime.sleep(sleepTime)
    
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
            # pending feeling is got
            # no next pending feeling
            self.expect(isWait=isWait,
                        name='Absent NAME2, feeling', isEmpty=False,
                        isVoiceFeeling=True,
                        isImageFeeling=True,
                        isNegativeFeeling=True)
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationDelay)
        
    
            # last item.name will we be absent
            print('\n NAME current Absent {}'.format(CommunicationTest.NAME))
            Wall_E_item_sensation10 = self.createSensation(
                                                    sensationName='Wall_E_item_sensation10',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    name=CommunicationTest.NAME,
                                                    score=CommunicationTest.SCORE_1,
                                                    presence=Sensation.Presence.Absent,
                                                    locations=self.getLocations())
            self.printSensationNameById(note='Wall_E_item_sensation10 test', dataId=Wall_E_item_sensation10.getDataId())
           #simulate TensorFlowClassification send presence item to MainRobot
           
    #         communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation10)
            self.doProcess(robot=communication, sensation=Wall_E_item_sensation10)
            self.assertEqual(len(communication.getMemory().getAllPresentItemSensations()), 0, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
            self.expect(isWait=isWait,
                        name='Absent NAME', isEmpty=True)
            for location in self.getLocations():
                self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
       


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
        
        
    def doTest_ProcessItemImageVoiceFromSameRobotSenses(self, communication, isWait):
        #responses
        # - come from mainNames=self.OTHERMAINNAMES
        # - are marked as robotType=Sensation.RobotType.Muscle
        #
        # but Communication should handle these responses as person said,
        # Microphone detects as Sense type Voices in same mainNames
        print('\ntest_ProcessItemImageVoiceFromSameRobotSenses\n')
        self.do_test_ProcessItemImageVoice(communication=communication, isWait=isWait,
                                           mainNames=self.MAINNAMES,
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
        
    def do_test_ProcessItemImageVoice(self, communication, isWait, mainNames, robotType):#, memoryType):
        print('\ndo_test_ProcessItemImageVoice\n')
        
        ########################################################################################################
        # Prepare part
        
        memoryType=Sensation.MemoryType.Working
        
        history_sensationTime = systemTime.time() -2*max(CommunicationTest.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
        
        print('\n9: current Present {}'.format(CommunicationTest.NAME))
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        Wall_E_item_sensation = self.createSensation(robot=communication,
                                                     sensationName= 'Wall_E_item_sensation',
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=Sensation.RobotType.Sense,
                                                     name=CommunicationTest.NAME,
                                                     score=CommunicationTest.SCORE_1,
                                                     presence=Sensation.Presence.Present,
                                                     locations=self.getLocations())

        allPresentItemSensations = communication.getMemory().getAllPresentItemSensations()
        
        self.assertEqual(len(allPresentItemSensations), 1, 'len(communication.getMemory().getAllPresentItemSensations() should be 1')
        self.assertEqual(allPresentItemSensations[0], Wall_E_item_sensation, 'allPresentItemSensations[0] should be Wall_E_item_sensation')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
                
        # communication 1. response
        # Voice, 2. best
        Wall_E_voice_sensation_1 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_1',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTest.VOICEDATA5,
                                                    feeling = CommunicationTest.BETTER_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_1, feeling = CommunicationTest.BETTER_FEELING)
        
        # communication 1. response
        # 1. Image, 2. best
        Wall_E_image_sensation_1 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_1',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTest.VOICEDATA5,
                                                    feeling = CommunicationTest.BETTER_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_1, feeling = CommunicationTest.BETTER_FEELING)
                
        # communication 2. response
        # Voice, 1. best
        Wall_E_voice_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_2',
                                                    robot=communication,
                                                    time=history_sensationTime,                                                        
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTest.VOICEDATA6,
                                                    feeling = CommunicationTest.BEST_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_2, feeling = CommunicationTest.BEST_FEELING)
        # communication 2. response
        # Image, 1. best
        Wall_E_image_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_2',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTest.VOICEDATA6,
                                                    feeling = CommunicationTest.BEST_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_2, feeling = CommunicationTest.BEST_FEELING)

        # communication 3. response
        # Voice, 3. best
        Wall_E_voice_sensation_3 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_3',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTest.VOICEDATA7,
                                                    feeling = CommunicationTest.NORMAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_3, feeling = CommunicationTest.NORMAL_FEELING)

        # communication 3. response
        # Image, 3. best
        Wall_E_image_sensation_3 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_3',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTest.VOICEDATA7,
                                                    feeling = CommunicationTest.NORMAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_3, feeling = CommunicationTest.NORMAL_FEELING)
        
        
        # communication 4. response
        # Voice, 4. best
        Wall_E_voice_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_voice_sensation_4',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTest.VOICEDATA7,
                                                    feeling = CommunicationTest.NEUTRAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_voice_sensation_4, feeling = CommunicationTest.NEUTRAL_FEELING)
        # communication 4. response
        # Image, 4. best
        Wall_E_image_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_image_sensation_4',
                                                    robot=communication,
                                                    time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTest.VOICEDATA7,
                                                    feeling = CommunicationTest.NEUTRAL_FEELING,
                                                    locations=self.getLocations())
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation_4, feeling = CommunicationTest.NEUTRAL_FEELING)
        


        ########################################################################################################
        ## test part
        # simulate that we have started Communication-Robot and all Robots get Item-sensation that it is present
        # TODO iitRobot is now empty method that can be overridden. Socker-classes create Robot presense sensations and handle them also
        # so thios can't be tested here, we don't get sensation here.
        
#         communication.initRobot()
#         self.expect(isWait=isWait,
#                     name='initRobot',
#                     isEmpty=False,
#                     #isItem=True,
#                     communicationItem=self.technicalSensation) # will get other sensation
                
        #image and Item from Sense, which has other MainNames
        # simulate item and image are connected each other with TensorflowClassifivation
        Wall_E_item_sense_sensation = self.createSensation(
                                                 sensationName='Wall_E_item_sense_sensation',
                                                 robot=communication,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTest.NAME,
                                                 associations=[],
                                                 presence=Sensation.Presence.Present,
                                                 mainNames=mainNames,
                                                 locations=self.getLocations())

        #self.logCommunicationState(note='before process Starting conversation, get best voice and image')
        #Item is Present, process
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sense_sensation)
        # should get just best Voice and Image
        muscleVoice = self.expect(isWait=isWait,
                    name='Starting conversation, get best voice and image',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_2, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_2, isExactMuscleVoice=True,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationWaitingVoicePlayed))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed)
            
        # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.createSensation(sensation=Wall_E_voice_sensation_2,
                                                                                                         sensationName='Wall_E_voice_sensation_2_ignored',
                                                                                                         robot=communication,
                                                                                                         time = systemTime.time() +5*max(CommunicationTest.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL), # time to future do be sure, we can debug
                                                                                                         robotType=Sensation.RobotType.Sense))
        self.expect(isWait=isWait,
                    name='Starting conversation, get best voice and imaget, voice should be ignored',
                    isEmpty=True)

        # simulate playback
        robotStateSensation=self.createSensation(
                                                        sensationName='Wall_E_voice_sensation_2Played',
                                                        robot=communication,
                                                        memoryType=Sensation.MemoryType.Sensory,
                                                        sensationType=Sensation.SensationType.RobotState,
                                                        robotType=Sensation.RobotType.Sense,
                                                        robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                        locations=self.getLocations())
        robotStateSensation.associate(muscleVoice)
        self.doProcess(robot=communication, sensation=robotStateSensation)
#         self.doProcess(robot=communication, sensation=self.createSensation(
#                                                     sensationName='Eva_voice_sensation2Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotState=Sensation.RobotState.CommunicationVoicePlayed,
#                                                     mainNames=mainNames,
#                                                     locations=self.getLocations())) 
        self.expect(isWait=isWait,
                        name='Present NAME2 again basic change in presentation CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
                    
                    # we don't have other side commicationg Robot
#                     communicationImage=Wall_E_image_sensation_2, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_2, isExactCommunicationVoice=True)
        
        
        # now other conversation part Robot or person responds with voice
        Wall_E_sense_voice_response_sensation = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTest.VOICEDATA8,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
       
        Wall_E_sense_voice_response_sensation.associate(sensation=Wall_E_item_sense_sensation)
        #self.logCommunicationState(note='before process response, second best voice')
        # process
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation)
        # should get second best voice, image and positive feelings to 1. responses
        # we resposend to personsvoice, so we first get CommunicationResponseHeard and then (Sensation.RobotState.CommunicationWaiting) or Sensation.RobotState.CommunicationWaitingResponse
        muscleVoice = self.expect(isWait=isWait,
                    name='response, second best voice, image',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_1, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_1, isExactMuscleVoice=True,
#                     communicationImage=Wall_E_image_sensation_1, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_1, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationResponseHeard, Sensation.RobotState.CommunicationWaitingVoicePlayed))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed)

        # test, that if we get new voice before getting Sensation.RobotState.CommunicationVoicePlayed, it is ignored        
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=self.createSensation( sensation=Wall_E_voice_sensation_2,
                                                                                                          sensationName='Wall_E_voice_sensation_2_ignored',
                                                                                                          robot=communication,
                                                                                                          robotType=Sensation.RobotType.Sense,
                                                                                                          memoryType=Sensation.MemoryType.Sensory))

        self.expect(isWait=isWait,
                    name='response, second best voice, image, voice should be ignored',
                    isEmpty=True)

        # simulate playback
        robotStateSensation=self.createSensation(
                                                        sensationName='Wall_E_voice_sensation_1Played',
                                                        robot=communication,
                                                        memoryType=Sensation.MemoryType.Sensory,
                                                        sensationType=Sensation.SensationType.RobotState,
                                                        robotType=Sensation.RobotType.Sense,
                                                        robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                        locations=self.getLocations())
        robotStateSensation.associate(muscleVoice)
        self.doProcess(robot=communication, sensation=robotStateSensation)
#         self.doProcess(robot=communication, sensation=self.createSensation(
#                                                     sensationName='Wall_E_voice_sensation_1Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotState=Sensation.RobotState.CommunicationVoicePlayed,
#                                                     mainNames=mainNames,
#                                                     locations=self.getLocations())) 
        self.expect(isWait=isWait,
                        name='response, second best voice, image CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
        
        # TODO enable and reimplement next line, because 
        # heardDataIds is location based now       
#         self.assertTrue(Wall_E_sense_voice_response_sensation.getDataId() in communication.heardDataIds)
        
        # 2. response from other side communication
        Wall_E_sense_voice_response_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_2',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTest.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
        #self.logCommunicationState(note='before process response, third best voice, image')
        # process, should get third best voice, image and positive feelings to previous responses   
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_2)
        muscleVoice = self.expect(isWait=isWait,
                    name='response, third best voice, image',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_3, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_3, isExactMuscleVoice=True,
#                     communicationImage=Wall_E_image_sensation_3, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_3, isExactCommunicationVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationResponseHeard, Sensation.RobotState.CommunicationWaitingVoicePlayed))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed)

        # simulate playback
        robotStateSensation=self.createSensation(
                                                        sensationName='Wall_E_voice_sensation_3Played',
                                                        robot=communication,
                                                        memoryType=Sensation.MemoryType.Sensory,
                                                        sensationType=Sensation.SensationType.RobotState,
                                                        robotType=Sensation.RobotType.Sense,
                                                        robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                        locations=self.getLocations())
        robotStateSensation.associate(muscleVoice)
        self.doProcess(robot=communication, sensation=robotStateSensation)
#         self.doProcess(robot=communication, sensation=self.createSensation(
#                                                     sensationName='Wall_E_voice_sensation_3Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotState=Sensation.RobotState.CommunicationVoicePlayed,
#                                                     mainNames=mainNames,
#                                                     locations=self.getLocations())) 
        self.expect(isWait=isWait,
                        name='response, third best voice, image CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)

        # response 3 from other side communication
        Wall_E_sense_voice_response_sensation_3 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_3',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTest.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
        #self.logCommunicationState(note='before process response, old responsed voice, response fourth best image')
        # process, should get fourth best image, voice and positive feelings to previous responses
        # at this point Wall_E_sense_voice_response_sensation is better than Wall_E_image_sensation_4
        # because Wall_E_image_sensation_4 feeling was low
        # We get also positive feeling to previous responses.
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_3)
        # TODO WE will not get Communication Sensations, because limit is exceeded
        # But Communication implementation will be changed
        muscleVoice = self.expect(isWait=isWait,
                    name='response, response voice, fourth best image, voice',
                    isEmpty=False,
                    muscleImage=Wall_E_image_sensation_4, isExactMuscleImage=True,
                    muscleVoice=Wall_E_voice_sensation_4, isExactMuscleVoice=True,#Wall_E_sense_voice_response_sensation_3, isExactMuscleVoice=False, #self.Eva_voice_sensation
#                     communicationImage=Wall_E_image_sensation_4, isExactCommunicationImage=True,
#                     communicationVoice=Wall_E_voice_sensation_4, isExactCommunicationVoice=True,#self.Eva_voice_sensation
                    communicationImage=None,
                    communicationVoice=None,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationResponseHeard, Sensation.RobotState.CommunicationWaitingVoicePlayed))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingVoicePlayed)

        # simulate playback
        robotStateSensation=self.createSensation(
                                                        sensationName='Wall_E_voice_sensation_4Played',
                                                        robot=communication,
                                                        memoryType=Sensation.MemoryType.Sensory,
                                                        sensationType=Sensation.SensationType.RobotState,
                                                        robotType=Sensation.RobotType.Sense,
                                                        robotState = Sensation.RobotState.CommunicationVoicePlayed,
                                                        locations=self.getLocations())
        robotStateSensation.associate(muscleVoice)
        self.doProcess(robot=communication, sensation=robotStateSensation)
#         self.doProcess(robot=communication, sensation=self.createSensation(
#                                                     sensationName='Wall_E_voice_sensation_4Played',
#                                                     robot=communication,
#                                                     memoryType=Sensation.MemoryType.Sensory,
#                                                     sensationType=Sensation.SensationType.RobotState,
#                                                     robotState=Sensation.RobotState.CommunicationVoicePlayed,
#                                                     mainNames=mainNames,
#                                                     locations=self.getLocations())) 
        self.expect(isWait=isWait,
                        name='response, response voice, fourth best image, voice CommunicationWaitingResponse', isEmpty=False,
                        robotStates = (Sensation.RobotState.CommunicationWaitingResponse))
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
#                     robotStates = (Sensation.RobotState.CommunicationResponseHeard, Sensation.RobotState.CommunicationWaitingResponse))
#         for location in self.getLocations():
#             self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationWaitingResponse)
        
        
        Wall_E_sense_voice_response_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_4',
                                                    robot=communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTest.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    mainNames=mainNames)
        Wall_E_item_sensation.associate(sensation=Wall_E_sense_voice_response_sensation_4, feeling = CommunicationTest.NEUTRAL_FEELING)
        
        #self.logCommunicationState(note='before process response, Wall_E_sense_voice_response_sensation, no image')
         # process
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_4)
        # at this point Communication has used all sensations 
        self.expect(isWait=isWait,
                    name='response, Wall_E_sense_voice_response_sensation, no response will be found',
                    isEmpty=False,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True,
                    robotStates = (Sensation.RobotState.CommunicationResponseHeard, Sensation.RobotState.CommunicationNoResponseToSay)
                    )
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationNoResponseToSay)
            
        # TODO should we test reasonable way to continue this conversation
        
        # end conversation
        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTest.NAME))
        Wall_E_item_sense_sensation2 = self.createSensation(
                                                 sensationName='Wall_E_item_sense_sensation2',
                                                 robot=communication,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTest.NAME,
                                                 associations=[],
                                                 presence=Sensation.Presence.Absent,
                                                 mainNames=mainNames,
                                                 locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sense_sensation2 test', dataId=Wall_E_item_sense_sensation2.getDataId())
        
        communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sense_sensation2)
        # at this point Communication has used all sensations 
        self.expect(isWait=isWait,
                    name='no response, Wall_E_item_sense_sensation2, Absent',
                    isEmpty=False,
                    robotStates = (Sensation.RobotState.CommunicationWaiting, Sensation.RobotState.CommunicationEnded)
                    )
        for location in self.getLocations():
            self.assertEqual(self.communication.itemConversations[location].robotState, Sensation.RobotState.CommunicationEnded)
                
        
        
        

        # TODO enable and reimplement next lines, because 
        # heardDataIds is location based now       
#         print("\nSTo remove known first reply from communication.heardDataIds send replyes to communication untis its first reply is available")        
#         j = 0        
#         i = 5 # for numbering
#         while Wall_E_sense_voice_response_sensation.getDataId() in communication.heardDataIds and j < Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
#         # response 4 from other side communication
#             Wall_E_sense_voice_response_sensation_extra = self.createSensation(
#                                                         sensationName='Wall_E_sense_voice_response_sensation_{}'.format(i),
#                                                         robot=communication,
#                                                         memoryType=Sensation.MemoryType.Sensory,
#                                                         sensationType=Sensation.SensationType.Voice,
#                                                         robotType=robotType,
#                                                         data=CommunicationTest.VOICEDATA9,
#                                                         locations=self.getLocations(),
#                                                         mainNames=mainNames)
#             Wall_E_item_sensation.associate(sensation=Wall_E_sense_voice_response_sensation_extra, feeling = CommunicationTest.NEUTRAL_FEELING)
#             
#             #self.logCommunicationState(note='before process response, Wall_E_sense_voice_response_sensation, no image')
#              # process
#             communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_extra)
# 
#             # same conversation keep going on, even if we don't find anythoing to say            
#             self.assertTrue(communication._isConversationOn)
#             self.assertFalse(communication._isConversationEnded)
#             self.assertFalse(communication._isConversationDelay)
#             # if communication could not response, dont cara
#             if communication._isNoResponseToSay:
#                 while not self.getAxon().empty():
#                     tranferDirection, sensation = self.getAxon().get(robot=self)
#                     print("\n{} To remove known first reply from communication.heardDataIds got sensation {}".format(j,sensation.toDebugStr()))
#     
#                 i=i+1
#                 j=j+1
#             else:
#                 self.expect(isWait=isWait,
#                               name='response, Wall_E_sense_voice_response_sensation, no image',
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
#         # should be run and communication.communicationItems) should be empty
#         # wait some time
#         sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
#         print("test is sleeping " + str(sleepTime) + " until continuing")       
#         systemTime.sleep(sleepTime)
#         print("Now stopWaitingResponse should be happened and we test it")       
#         # should get Voice Feeling between Voice and Item
#         # BUT is hard t0 test, just log
#         self.expect(isWait=isWait,
#                       name='NO response, got Negative feelings',
#                     isEmpty=False,
#                     muscleImage=None,
#                     muscleVoice=None,
#                     communicationImage=None,
#                     communicationVoice=None,
#                     isVoiceFeeling=True, isImageFeeling=False, isNegativeFeeling=True)
        
 
        # simulate that we have stopped Communication-Robot and all Robots get Item-sensation that it is absent
# TODO Robot.Deinit is empty method now and Socket classes handle Robot presences, so
# This can't be tested here.
#         communication.deInitRobot()
#         self.expect(isWait=isWait,
#                     name='deInitRobot',
#                     isEmpty=False,
#                     communicationItem=self.technicalSensation) # will get other sensation


       
        
 
                
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
                print('Did not get voice feeling')                   

        
if __name__ == '__main__':
    unittest.main()

 