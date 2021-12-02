'''
Created on 21.06.2019
Updated on 02.12.2021
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


from CommunicationTest import CommunicationTest

class CommunicationTestCase(unittest.TestCase, CommunicationTest):
    SEARCH_LENGTH=20                # How many response voices we check

    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        
#         Robot.mainRobotInstance = self
        self.mainNames = self.MAINNAMES

        # Robot to test        
        self.communication = Communication(mainRobot=self,
                                           parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.setRobotMainNames(self.communication, self.MAINNAMES)
        self.setRobotLocations(self.communication, self.getLocations())
        # if communication is configured to be MainRobot, reject this configuration and test only Communication feature.
        self.setSubInstances(self.communication, [])
           
        # should get Identity for proper functionality. Use Wall-E Identity in test
        self.communication.imageSensations, self.communication.voiceSensations = \
            self.communication.getIdentitySensations(name=CommunicationTestCase.NAME)
        self.assertTrue(len(self.communication.getMemory().getRobot().voiceSensations) > 0, "should have identity for testing")
        
        self.doSetUp(robot=self.communication)
        self.doSetUpCommunication(communication=self.communication)
        

    def tearDown(self):
        print('\ntearDown')       
        self.doTearDown()

        del self.communication
        
    '''
    TensorfloClassafication produces
    Item.name Working Out    
    ''' 
           
    def re_test_PresenseItemPresentRobot(self):
        print('\ntest_PresenseItemPresentRobot\n')       
        self.doTest_PresenseItemPresentRobot(robot=self.communication, isWait=False)
       
            
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def re_test_PresenseItemAbsentRobot(self):
        print('\ntest_PresenseItemAbsentRobot\n')       
        self.doTest_PresenseItemAbsentRobot(robot=self.communication, isWait=False)
        

    '''
    TensorfloClassification produces
    Item.name Working Out
    Sensations outside Robot are in same Robot.mainNames and robotType=Sensation.RobotType.Sense
    so this test is same than without parameters
    '''    
    def test_2_Presense(self):
        print('\ntest_2_Presense\n')       
        self.doTest_2_Presense(robot=self.communication, communication=self.communication, isWait=False)
        
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in other Robot.mainNames and robotType=Sensation.RobotType.Communication
    so this test result should  same than with test where robotType=Sensation.RobotType.Sense,
    because Communication should handle those sensation equally, when Robot.mainNames differ
    
    disabled until Communication Robot is planned again.
    '''

    def re_test_3_Presense(self):
        print('\ntest_3_Presense\n')       
        self.doTest_3_Presense(robot=self.communication, communication=self.communication, isWait=False)

        
    '''
    Voice comes from this Robots Sense-Robot (Microphone)
    '''    
        
    def re_test_ProcessItemImageVoiceFromSameRobotSenses(self):
        print('\ntest_ProcessItemImageVoiceFromSameRobotSenses\n')
        self.doTest_ProcessItemImageVoiceFromSameRobotSenses(robot = self.communication, isWait = False)
        
        
    '''
    Tests from testMemory
    because implementation is moved in Communication
    '''
    def re_test_getBestSensationsSense(self):
        self.do_test_getBestSensations(robotType=Sensation.RobotType.Sense, robotMainNames=self.MAINNAMES, succeed=True)
        
    def re_test_getBestSensationsCommunication(self):
        self.do_test_getBestSensations(robotType=Sensation.RobotType.Communication, robotMainNames=self.OTHERMAINNAMES, succeed=True)

    def re_test_getBestSensationsCommunicationFail(self):
        self.do_test_getBestSensations(robotType=Sensation.RobotType.Communication, robotMainNames=self.MAINNAMES, succeed=False)

    def do_test_getBestSensations(self, robotType, robotMainNames, succeed):
        # Memory is empty, We should get nothing
        print('\ntest_getBestSensationSense')
        name='test'
        ignoredDataIds=[]
        history_sensationTime = systemTime.time() -2*300.0

        # Item where all test created and self.robot seen Sensations are associated
        # WE can't use self.createSensation yet
        self.Wall_E_item_sensation = self.robot.createSensation(
                                                    robot = self.robot,
                                                    time = history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=robotType,
                                                    name=self.NAME,
                                                    score=self.SCORE_1)
        itemConversation = None
        if len(self.communication.getLocations()) > 0:
            for location in self.communication.getLocations():
                itemConversation = self.communication.itemConversations[location]
                break;
        else:
            itemConversation = self.communication.itemConversations['']
        # Memory is empty, We should get nothing

        sensations, sensationAssociations = itemConversation.getBestSensations(itemSensations=[self.Wall_E_item_sensation],
                                                                sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                robotMainNames = robotMainNames,
                                                                ignoredDataIds = ignoredDataIds)
        self.assertEqual(len(sensations), 0)
        self.assertEqual(len(sensationAssociations), 0)
        # Potential      
        # First item, voice and image
        
        voice_sensation1 = self.createSensation(
                                                sensationName='voice_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=self.MAINNAMES
                                                )
        self.printSensationNameById(note='voice_sensation1 test', dataId=voice_sensation1.getDataId())
        image_sensation1 = self.createSensation(
                                                sensationName='image_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=self.MAINNAMES)
        self.printSensationNameById(note='image_sensation1 test', dataId=image_sensation1.getDataId())
        
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=robotType,
                                                name=self.NAME,
                                                score=self.SCORE_1,
                                                presence=Sensation.Presence.Entering)
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        
        # Don't yet use Feelings associations, so they are neutral        
        item_sensation1.associate(sensation=voice_sensation1)
        item_sensation1.associate(sensation=image_sensation1)
        voice_sensation1.associate(sensation=image_sensation1)
        
        sensations, sensationAssociations = itemConversation.getBestSensations( itemSensations = [item_sensation1],
                                                                  sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                  robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                  robotMainNames = robotMainNames,
                                                                  ignoredDataIds = ignoredDataIds,
                                                                  searchLength=self.SEARCH_LENGTH)
        if succeed:
            self.assertEqual(len(sensations), 2)
            self.assertEqual(len(sensationAssociations), 2)
            associationSensations=[]
            for associations in sensationAssociations:
                for association in associations:
                    associationSensations.append(association.getSelfSensation())
                
            self.assertTrue(voice_sensation1 in sensations)
            self.assertTrue(voice_sensation1 in associationSensations)
            
            self.assertTrue(image_sensation1 in sensations)
            #self.assertTrue(image_sensation1 in associationSensations)
        else:
            self.assertEqual(len(sensations), 0)
            self.assertEqual(len(sensationAssociations), 0)
       
        # second item, voice and image, better score and Feeling
        
        voice_sensation2 = self.createSensation(
                                                sensationName='voice_sensation2',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=robotType,
                                                mainNames=self.MAINNAMES
                                                )
        self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
        image_sensation2 = self.createSensation(
                                                sensationName='image_sensation2',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=robotType,
                                                mainNames=self.MAINNAMES)
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        
        item_sensation2 = self.createSensation(
                                                sensationName='item_sensation2',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=robotType,
                                                name=self.NAME,
                                                score=self.SCORE_2,
                                                presence=Sensation.Presence.Entering)
        self.printSensationNameById(note='item_sensation2 test', dataId=item_sensation2.getDataId())
        
        item_sensation2.associate(sensation=voice_sensation2, feeling = Sensation.Feeling.Normal)
        item_sensation2.associate(sensation=image_sensation2, feeling = Sensation.Feeling.Normal)
        voice_sensation2.associate(sensation=image_sensation2)
        
        
        sensations, sensationAssociations = itemConversation.getBestSensations( itemSensations = [item_sensation2],
                                                                  sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                  robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                  robotMainNames = robotMainNames,
                                                                  ignoredDataIds = ignoredDataIds,
                                                                  searchLength=self.SEARCH_LENGTH)
        if succeed:
            self.assertEqual(len(sensations), 2)
            self.assertEqual(len(sensationAssociations), 2)
            associationSensations=[]
            sensationAssociations
            for associations in sensationAssociations:
                for association in associations:
                    associationSensations.append(association.getSelfSensation())
                
            self.assertTrue(voice_sensation2 in sensations)
            self.assertTrue(voice_sensation2 in associationSensations)
            
            self.assertTrue(image_sensation2 in sensations)
            #self.assertTrue(image_sensation2 in associationSensations)
            
            # Test again with ignoredDataIds for last results, so we should get 1. results again
            sensations, sensationAssociations = itemConversation.getBestSensations( itemSensations = [item_sensation2],
                                                                      sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                      robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                      robotMainNames = robotMainNames,
                                                                      ignoredDataIds = [voice_sensation2.getDataId(), image_sensation2.getDataId()],
                                                                      searchLength=self.SEARCH_LENGTH)
            self.assertEqual(len(sensations), 2)
            self.assertEqual(len(sensationAssociations), 2)
            associationSensations=[]
            for associations in sensationAssociations:
                for association in associations:
                    associationSensations.append(association.getSelfSensation())
                    
            self.assertTrue(voice_sensation1 in sensations)
            self.assertTrue(voice_sensation1 in associationSensations)
                
            self.assertTrue(image_sensation1 in sensations)
            #self.assertTrue(image_sensation1 in associationSensations)

        # set first item core also higher as high as item3, set feeling same so we would its items
        # NOTE Feeling is much more meaningful than score, so this test works even if we let lower, SCORE_2
        
        item_sensation1.setScore(score=self.SCORE_2)
        item_sensation1.getAssociation(sensation=voice_sensation1).setFeeling(feeling = Sensation.Feeling.Good)
        item_sensation1.getAssociation(sensation=image_sensation1).setFeeling(feeling = Sensation.Feeling.Good)
        
        
        sensations, sensationAssociations = itemConversation.getBestSensations( itemSensations = [item_sensation1],
                                                                  sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                  robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                  robotMainNames = robotMainNames,
                                                                  ignoredDataIds = ignoredDataIds,
                                                                  searchLength=self.SEARCH_LENGTH)
        if succeed:
            self.assertEqual(len(sensations), 2)
            self.assertEqual(len(sensationAssociations), 2)
            associationSensations=[]
            for associations in sensationAssociations:
                for association in associations:
                    associationSensations.append(association.getSelfSensation())
                    
            self.assertTrue(voice_sensation1 in sensations)
            self.assertTrue(voice_sensation1 in associationSensations)
            
            self.assertTrue(image_sensation1 in sensations)
            self.assertTrue(image_sensation1 in associationSensations)
            
            # Test again with ignoredDataIds for last results, so we should get 2. results again
            sensations, sensationAssociations = itemConversation.getBestSensations( itemSensations = [item_sensation2],
                                                                      sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                      robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                      robotMainNames = robotMainNames,
                                                                      ignoredDataIds = [voice_sensation1.getDataId(), image_sensation1.getDataId()],
                                                                      searchLength=self.SEARCH_LENGTH)
            self.assertEqual(len(sensations), 2)
            self.assertEqual(len(sensationAssociations), 2)
            associationSensations=[]
            for associations in sensationAssociations:
                for association in associations:
                    associationSensations.append(association.getSelfSensation())
                    
            self.assertTrue(voice_sensation2 in sensations)
            self.assertTrue(voice_sensation2 in associationSensations)
                
            self.assertTrue(image_sensation2 in sensations)
            #self.assertTrue(image_sensation2 in associationSensations)
        else:
            self.assertEqual(len(sensations), 0)
            self.assertEqual(len(sensationAssociations), 0)
            
        # Finally test situation, where we have many Sensation.Item.Names present
        # with same Voice and Image assigned. This is situation, when certain
        # Voice/Image is heard/seen when these Iten.names are present together.
        # In this situation this Voice/Image is best.
        #
        # Now best Feeling/Score is is Sensation.Feeling.Good/Score2
        # Calculate how many Voices/Images wins this with
        # Sensation.Feeling.Normal/Score2
        
        new_voice_sensation = self.createSensation(
                                                    sensationName='new_voice_sensation',
                                                    robot=self.robot,
                                                    time=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    mainNames=self.MAINNAMES
                                                    )
        self.printSensationNameById(note='new_voice_sensation test', dataId=new_voice_sensation.getDataId())
        new_image_sensation = self.createSensation(
                                                    sensationName='new_image_sensation',
                                                    robot=self.robot,
                                                    time=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Image,
                                                    robotType=robotType,
                                                    mainNames=self.MAINNAMES)
        self.printSensationNameById(note='new_image_sensation test', dataId=new_image_sensation.getDataId())
        
 
        itemSensations = []   
        for i in range(0,int(Sensation.Feeling.Good/Sensation.Feeling.Normal)+2):
                name = '{}_{}'.format(self.NAME,i)
                new_item_sensation = self.createSensation(
                                                        sensationName='item'+name,
                                                        robot=self.robot,
                                                        time=history_sensationTime,
                                                        memoryType=Sensation.MemoryType.Working,
                                                        sensationType=Sensation.SensationType.Item,
                                                        robotType=robotType,
                                                        name=name,
                                                        score=self.SCORE_2,
                                                        presence=Sensation.Presence.Present,
                                                        mainNames=self.MAINNAMES
                                                        )
                self.printSensationNameById(note='item '+name+' test', dataId=new_item_sensation.getDataId())
    
                itemSensations.append(new_item_sensation)            
                new_item_sensation.associate(sensation=new_voice_sensation, feeling = Sensation.Feeling.Normal)
                new_item_sensation.associate(sensation=new_image_sensation, feeling = Sensation.Feeling.Normal)
                new_voice_sensation.associate(sensation=new_image_sensation)
                
        # Test without ignoredDataIds
        sensations, sensationAssociations = itemConversation.getBestSensations( itemSensations = itemSensations,
                                                                      sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                      robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                      robotMainNames = robotMainNames,
                                                                      ignoredDataIds = [],
                                                                      searchLength=self.SEARCH_LENGTH)
        if succeed:
            self.assertEqual(len(sensations), 2)
            self.assertEqual(len(sensationAssociations), 2)
            for associations in sensationAssociations:
                self.assertEqual(len(associations), len(itemSensations))
                for association in associations:
                    self.assertTrue(association.getSensation() in itemSensations)
                    self.assertTrue(association.getSelfSensation() in [new_voice_sensation, new_image_sensation])
        else:
            self.assertEqual(len(sensations), 0)
            self.assertEqual(len(sensationAssociations), 0)
#         associationSensations=[]
#         for association in associations:
#             associationSensations.append(association.getSensation())
           
       
    '''
    TODO What is difference of this and previous test
    This is valid Test, where source of candidates comes from other robot
    TODO combine with test above
    RobotType and MAINNAMES are at least valid
    '''       
    def retest_getBestSensationsCommunication(self):
        # Memory is empty, We should get nothing
        print('\ntest_getBestSensationsCommunication')
        name='test'
        ignoredDataIds=[]
        itemSensations=[]
        ignoredDataIds=[]
        history_sensationTime = systemTime.time() -2*300.0

        sensations, associations = itemConversation.getBestSensations(itemSensations=itemSensations,
                                                                sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                robotMainNames = [],
                                                                ignoredDataIds = ignoredDataIds)
        self.assertEqual(len(sensations), 0)
        self.assertEqual(len(associations), 0)
        
        # Create technical item where we assign all Sensations
        
        # WE can't use self.createSensation yet
        self.Wall_E_item_sensation = self.robot.createSensation(
                                                    robot = self.robot,
                                                    time = history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    name=self.NAME,
                                                    score=self.SCORE_1)
 
        # Create potential sensation to memory
        
        # Item 
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=self.NAME,
                                                score=self.SCORE_1,
                                                presence=Sensation.Presence.Entering)
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        itemSensations.append(item_sensation1)
        
        
        
        
 
        
        # Sense voice and image
        #
        voice_sense_sensation1 = self.createSensation(
                                                sensationName='voice_sense_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Communication,
                                                mainNames=self.OTHERMAINNAMES
                                                )
        self.printSensationNameById(note='voice_sense_sensation1 test', dataId=voice_sense_sensation1.getDataId())
        image_sense_sensation1 = self.createSensation(
                                                sensationName='image_sense_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Communication,
                                                mainNames=self.OTHERMAINNAMES)
        self.printSensationNameById(note='image_sense_sensation1 test', dataId=image_sense_sensation1.getDataId())
                
        item_sensation1.associate(sensation=voice_sense_sensation1)
        item_sensation1.associate(sensation=image_sense_sensation1)
        image_sense_sensation1.associate(sensation=voice_sense_sensation1)
        
        sensations, associations = itemConversation.getBestSensations(itemSensations = itemSensations,
                                                                sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                robotMainNames = self.MAINNAMES,
                                                                ignoredDataIds = [])
        self.assertEqual(len(sensations), 2)
        self.assertEqual(len(associations), 2)
        self.assertTrue(voice_sense_sensation1 in sensations)        
        self.assertTrue(image_sense_sensation1 in sensations)
        
        # Communication voice and image
        # MAINnAMES
        voice_communication_sensation1 = self.createSensation(
                                                sensationName='voice_communication_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Communication,
                                                mainNames=self.MAINNAMES
                                                )
        self.assertEqual(self.MAINNAMES, voice_communication_sensation1.getMainNames())
        self.printSensationNameById(note='voice_communication_sensation1 test', dataId=voice_communication_sensation1.getDataId())
        image_communication_sensation1 = self.createSensation(
                                                sensationName='image_communication_sensation1',
                                                robot=self.robot,
                                                time=history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Communication,
                                                mainNames=self.MAINNAMES)
        self.assertEqual(self.MAINNAMES, image_communication_sensation1.getMainNames())
        self.printSensationNameById(note='image_communication_sensation1 test', dataId=image_communication_sensation1.getDataId())
                
        item_sensation1.associate(sensation=voice_communication_sensation1)
        item_sensation1.associate(sensation=image_communication_sensation1)
        image_communication_sensation1.associate(sensation=voice_communication_sensation1)
        
        sensations, associations = itemConversation.getBestSensations(itemSensations = itemSensations,
                                                                sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                robotMainNames = self.MAINNAMES,
                                                                ignoredDataIds = [])
        self.assertEqual(len(sensations), 2)
        self.assertEqual(len(associations), 2)
        self.assertTrue(voice_sense_sensation1 in sensations)        
        self.assertTrue(image_sense_sensation1 in sensations)
        
        voice_sense_sensation1_memorability = voice_sense_sensation1.getMemorability(
                                                    itemSensations = itemSensations,
                                                    robotMainNames = self.MAINNAMES,
                                                    robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                    ignoredDataIds=ignoredDataIds,
                                                    positive = True,
                                                    negative = False,
                                                    absolute = False)
 
        image_sense_sensation1_memorability = image_sense_sensation1.getMemorability(
                                                    itemSensations = itemSensations,
                                                    robotMainNames = self.MAINNAMES,
                                                    robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                    ignoredDataIds=ignoredDataIds,
                                                    positive = True,
                                                    negative = False,
                                                    absolute = False)
 
        
        #set now communication sensation to different mainNames and we should get then best now
        # when we set now got best sensation to history
        history_sensationTime = systemTime.time() -2*300.0
        for sensation in sensations:
            sensation.setTime(time=history_sensationTime)
        for association in associations:
            association.setTime(time=history_sensationTime)
        history_voice_sense_sensation1_memorability = voice_sense_sensation1.getMemorability(
                                                    itemSensations = itemSensations,
                                                    robotMainNames = self.MAINNAMES,
                                                    robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                    ignoredDataIds=ignoredDataIds,
                                                    positive = True,
                                                    negative = False,
                                                    absolute = False)
        # TODO Correct this, getMemorability does not use time
        self.assertTrue(history_voice_sense_sensation1_memorability < voice_sense_sensation1_memorability)
 
        history_image_sense_sensation1_memorability = image_sense_sensation1.getMemorability(
                                                    itemSensations = itemSensations,
                                                    robotMainNames = self.MAINNAMES,
                                                    robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                    ignoredDataIds=ignoredDataIds,
                                                    positive = True,
                                                    negative = False,
                                                    absolute = False)
        self.assertTrue(history_image_sense_sensation1_memorability < image_sense_sensation1_memorability)
            
        voice_communication_sensation1.setMainNames(self.OTHERMAINNAMES)
        self.assertEqual(self.OTHERMAINNAMES, voice_communication_sensation1.getMainNames())
        self.assertFalse(voice_communication_sensation1.isInMainNames(self.MAINNAMES))
        image_communication_sensation1.setMainNames(self.OTHERMAINNAMES)
        self.assertEqual(self.OTHERMAINNAMES, image_communication_sensation1.getMainNames())
        self.assertFalse(image_communication_sensation1.isInMainNames(self.MAINNAMES))
        
        sensations, associations = itemConversation.getBestSensations(itemSensations = itemSensations,
                                                                 sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                                 robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                 #robotTypes = [Sensation.RobotType.Communication],
                                                                 robotMainNames = self.MAINNAMES,
                                                                 ignoredDataIds = [])
        self.assertEqual(len(sensations), 2)
        self.assertEqual(len(associations), 2)
        self.assertTrue(voice_communication_sensation1 in sensations)        
        self.assertTrue(image_communication_sensation1 in sensations)

        
        #self.assertEqual(candidate_for_communication_item, item_sensation1)
#         self.assertEqual(candidate_for_voice, voice_sensation1)
#         self.assertEqual(candidate_for_voice_association, item_sensation1.getAssociation(sensation=candidate_for_voice))
#         self.assertEqual(candidate_for_image, image_sensation1)
#         self.assertEqual(candidate_for_image_association, item_sensation1.getAssociation(sensation=image_sensation1))
#         
        
        # TODO Enable these
       
#         # second item, voice and image, better score
#         
#         voice_sensation2 = self.createSensation(
#                                                 sensationName='voice_sensation2',
#                                                 robot=self.robot,
#                                                 time=history_sensationTime,
#                                                 memoryType=Sensation.MemoryType.Sensory,
#                                                 sensationType=Sensation.SensationType.Voice,
#                                                 robotType=Sensation.RobotType.Sense,
#                                                 #data=self.VOICEDATA2
#                                                 )
#         self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
#         image_sensation2 = self.createSensation(
#                                                 sensationName='image_sensation2',
#                                                 robot=self.robot,
#                                                 time=history_sensationTime,
#                                                 memoryType=Sensation.MemoryType.Sensory,
#                                                 sensationType=Sensation.SensationType.Image,
#                                                 robotType=Sensation.RobotType.Sense)
#         self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
#         
#         item_sensation2 = self.createSensation(
#                                                 sensationName='item_sensation2',
#                                                 robot=self.robot,
#                                                 time=history_sensationTime,
#                                                 memoryType=Sensation.MemoryType.Working,
#                                                 sensationType=Sensation.SensationType.Item,
#                                                 robotType=Sensation.RobotType.Sense,
#                                                 name=self.NAME,
#                                                 score=self.SCORE_1,
#                                                 presence=Sensation.Presence.Entering)
#         self.printSensationNameById(note='item_sensation2 test', dataId=item_sensation2.getDataId())
#         
#         
#         
#         
#         
#         item_sensation2.associate(sensation=voice_sensation2)
#         item_sensation2.associate(sensation=image_sensation2)
#         voice_sensation2.associate(sensation=image_sensation2)
#         
#         candidate_for_communication_item, candidate_for_voice, candidate_for_voice_association,\
#         candidate_for_image, candidate_for_image_association = \
#             self.memory.getMostImportantCommunicationSensations( 
#                                                                      robotMainNames=self.MAINNAMES,
#                                                                      name = self.NAME,
#                                                                      timemin = None,
#                                                                      timemax = None,
#                                                                      ignoredDataIds = ignoredDataIds,
#                                                                      searchLength=self.SEARCH_LENGTH)
#         self.assertEqual(candidate_for_communication_item, item_sensation2)
#         self.assertEqual(candidate_for_voice, voice_sensation2)
#         self.assertEqual(candidate_for_voice_association, item_sensation2.getAssociation(sensation=candidate_for_voice))
#         self.assertEqual(candidate_for_image, image_sensation2)
#         self.assertEqual(candidate_for_image_association, item_sensation2.getAssociation(sensation=image_sensation2))
#         
#         # set first item core higher, so we would its items
#         
#         item_sensation1.setScore(score=self.SCORE_8)
#         candidate_for_communication_item, candidate_for_voice, candidate_for_voice_association,\
#         candidate_for_image, candidate_for_image_association = \
#             self.memory.getMostImportantCommunicationSensations( 
#                                                                      robotMainNames=self.MAINNAMES,
#                                                                      name = self.NAME,
#                                                                      timemin = None,
#                                                                      timemax = None,
#                                                                      ignoredDataIds = ignoredDataIds,
#                                                                      searchLength=self.SEARCH_LENGTH)
#         # TODO what we should get now
#         # TODO What we should get voice_sensation1 or voice_sensation2
#         # Hmm.. implementatiis broken
#         self.assertEqual(candidate_for_communication_item, item_sensation1)
#         self.assertEqual(candidate_for_voice, voice_sensation1)
#         self.assertEqual(candidate_for_voice_association, item_sensation1.getAssociation(sensation=candidate_for_voice))
#         self.assertEqual(candidate_for_image, image_sensation1)
#         self.assertEqual(candidate_for_image_association, item_sensation1.getAssociation(sensation=image_sensation1))
#         
       
    '''
    deprecated
    '''
#         
#     def re_test_Picleability(self):
#         print("\ntest_Picleability\n")
#         
#         originalSensations=[]
#         for sensation in self.memory.sensationMemory:
#             if sensation.getMemoryType() == Sensation.MemoryType.LongTerm and\
#                sensation.getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY:
#                 originalSensations.append(sensation)
# 
#         self.memory.saveLongTermMemory()
#         del self.memory.sensationMemory[:]
#         
#         self.memory.loadLongTermMemory()
#         
#         self.assertEqual(len(self.memory.sensationMemory),len(originalSensations), "should load same amount Sensations")
#         i=0
#         while i < len(self.memory.sensationMemory):
#             self.assertEqual(self.memory.sensationMemory[i],originalSensations[i], "loaded sensation must be same than dumped one")
#             i=i+1
 
        
        
if __name__ == '__main__':
    unittest.main()

 