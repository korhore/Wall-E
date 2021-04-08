'''
Created on 08.04.2021
Updated on 08.04.2021
@author: reijo.korhonen@gmail.com

test VisualCommunication class
python3 -m unittest tests/testVisualCommunication.py

TODO missing Communication test cases


'''
import time as systemTime
import os
import shutil
from PIL import Image as PIL_Image

import unittest
from Sensation import Sensation
from Robot import Robot
from VisualCommunication.VisualCommunication import VisualCommunication
from Association.Association import Association
from Communication.Communication import Communication
from Axon import Axon

class VisualCommunicationTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    TEST_RUNS=5
    #TEST_RUNS=1
    ASSOCIATION_INTERVAL=3.0
    #TEST_TIME=300 # 5 min, when debugging
    TEST_TIME=30 # 30s when normal test

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
    
    MAINNAMES = ["MainName"]
    OTHERMAINNAMES = ["OTHER_MainName"]

    LOCATIONS_1 = ["location1"]
    LOCATIONS_2 = ["OtherLocation"]
    LOCATIONS_1_2 = ["location1","OtherLocation"]
    ALL_LOCATIONS = [LOCATIONS_1,LOCATIONS_2,LOCATIONS_1_2]
    locationsInd = 0
    
    # from testCommunicatoion
    ASSOCIATION_INTERVAL=3.0 # in float seconds
    AXON_WAIT = 10           # in int time to conditionally wait to get something into Axon

#     SCORE_1 = 0.1
#     SCORE_2 = 0.2
#     SCORE_3 = 0.3
#     SCORE_4 = 0.4
#     SCORE_5 = 0.5
#     SCORE_6 = 0.6
#     SCORE_7 = 0.7
#     SCORE_8 = 0.8
#     NAME='Wall-E'
#     NAME2='Eva'
    TECNICAL_NAME='TechnicalName'
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
    NEUTRAL_FEELING = Sensation.Feeling.Neutral
    
#     MAINNAMES = ["CommunicationTestCaseMainName"]
#     OTHERMAINNAMES = ["OTHER_CommunicationTestCaseMainName"]
#     
#     LOCATIONS_1 =   ['testLocation1']
#     LOCATIONS_2 =   ['testLocation2']
#     LOCATIONS_1_2 = ['testLocation1','testLocation2']

    
    SensationDirectory=[]
    SensationDataDirectory=[]
   
    
    
    '''
    Robot modeling
    '''

    
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getName(self):
        return VisualCommunicationTestCase.NAME
    def setMainNames(self, mainNames):
        self.mainNames = mainNames
    def getMainNames(self):
        return self.mainNames
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
    def getParent(self):
        return None
#     def log(self, logStr, logLevel=None):
#         if logLevel == None:
#             logLevel = self.visualCommunication.LogLevel.Normal
#         if logLevel <= self.visualCommunication.getLogLevel():
#              print(self.visualCommunication.getName() + ":" + str( self.visualCommunication.config.level) + ":" + Sensation.Modes[self.visualCommunication.mode] + ": " + logStr)

    '''
    get test locations
    NOTE Communication is now location based.
         We use now only one location in test
         and test Communication.ConversationWithItem subclass
         functionality. This subclass serves one location.
         So test is same than in previous versions, where
         Communication produced Communication Sensations for
         all  locations.
         
         Lets test how our new Communication strategy works.
    
    '''   
    def getLocations(self):
        return self.LOCATIONS_1
    def setRobotLocations(self, robot, locations):
        robot.locations = locations
        robot.uplocations = locations
        robot.downlocations = locations
    
    def setMainNames(self, mainNames):
        self.mainNames = mainNames
    def getMainNames(self):
        return self.mainNames
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames

    def getParent(self):
        return None
    
    def log(self, logStr, logLevel=None):
        if hasattr(self, 'visualCommunication'):
            if self.visualCommunication:
                if logLevel == None:
                    logLevel = self.visualCommunication.LogLevel.Normal
                if logLevel <= self.visualCommunication.getLogLevel():
                     print(self.visualCommunication.getName() + ":" + str( self.visualCommunication.config.level) + ":" + Sensation.Modes[self.visualCommunication.mode] + ": " + logStr)
    
    def logAxon(self):
        self.log("{} Axon with queue length {} full {}".format(self.getName(), self.getAxon().queue.qsize(), self.getAxon().queue.full()))

    '''
    Helper methods
    '''
        
    '''
    Sensation constructor for test purposes
    
    Parameters are exactly same than in default constructor
    but some parameters are added to do the job is added
    
    robot           robot to do the job
    sensationName   name for this Sensation, so we can log created sensation
                    so we can tell content of Robot's memory and tell
                    if something goes wrong in tested Communication Rpbot's
                    expected logic
                    
    sensationNames and created sensations are added to SensationDirectory
    '''
       
    def createSensation(self,
                 robot,
                 sensationName,
                 log=True,
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 
                  # base field are by default None, so we know what fields are given and what not
                 sensationType = None,
                 memoryType = None,
                 robotType = None,
                 locations =  None,
                 mainNames = None,
                 leftPower = None, rightPower = None,                        # Walle motors state
                 azimuth = None,                                             # Walle robotType relative to magnetic north pole
                 x=None, y=None, z=None, radius=None,                        # location and acceleration of Robot
                 hearDirection = None,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection = None,observationDistance = None,     # Walle's observation of something, relative to Walle
                 filePath = None,
                 data = None,                                                # ALSA voice is string (uncompressed voice information)
                 image = None,                                               # Image internal representation is PIl.Image 
                 calibrateSensationType = None,
                 capabilities = None,                                        # capabilitis of sensorys, robotType what way sensation go
                 name = None,                                                # name of Item
                 score = None,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence = None,                                            # presence of Item
                 kind = None,                                                # kind (for instance voice)
                 firstAssociateSensation = None,                             # associated sensation first side
                 otherAssociateSensation = None,                             # associated Sensation other side
                 feeling = None,                                             # feeling of sensation or association
                 positiveFeeling = None,                                     # change association feeling to more positive robotType if possible
                 negativeFeeling = None):                                    # change association feeling to more negative robotType if possible
        
        sensation = robot.createSensation(
                 log=log,
                 robot=self,
                 associations = associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 robotType=robotType,
                 #robot=robot,
                 locations=locations,
                 mainNames = mainNames, #self.getMainNames(),
                 leftPower = leftPower, rightPower = rightPower,
                 azimuth = azimuth,
                 x=x, y = y, z = z, radius=radius,
                 hearDirection = hearDirection,
                 observationDirection = observationDirection, observationDistance = observationDistance,
                 filePath = filePath,
                 data = data,
                 image = image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name = name,
                 score = score,
                 presence = presence,
                 kind = kind,
                 firstAssociateSensation = firstAssociateSensation,
                 otherAssociateSensation = otherAssociateSensation,
                 feeling = feeling,
                 positiveFeeling=positiveFeeling,
                 negativeFeeling=negativeFeeling)
            
        # if we get mainNames. overwrite Robots given mainNames
        if mainNames != None and len(mainNames) > 0:
            sensation.setMainNames(mainNames)
        # associate to self.technicalSensation so all created Sensations
        # can be found associated to self.technicalSensation.name.
        sensation.associate(sensation=self.technicalSensation, feeling=feeling)

        # add sensation to directory, so we can find it's name by ids
        self.addToSensationDirectory(name=sensationName, dataId=sensation.getDataId(), id=sensation.getId())
        sensation.detach(robot=robot)
        return sensation
        


        
    def addToSensationDirectory(self, name, dataId, id=None):
        if id != None:
            self.SensationDirectory.append((id, name))
        self.SensationDataDirectory.append((dataId, name))
       
    def getSensationNameById(self, note, dataId=None,id=None):
        assert(dataId is not None or id is not None)
        if dataId is not None:
            for did, name in self.SensationDataDirectory:
                if did == dataId:
                    return '{} | dataId {} | name: {}'.format(note, dataId, name)
        if id is not None:
            for iid, name in self.SensationDataDirectory:
                if iid == id:
                    return '{} | dataId {} | name: {}'.format(note, id, name)
        if dataId is not None:
            return'{} | dataId {} | was not found'.format(note, dataId)
        return'{} | id {} | was not found'.format(note, id)
        
    def printSensationNameById(self, note, dataId=None,id=None):
        print('\n{}\n'.format(self.getSensationNameById(note=note, dataId=dataId, id=id)))

    '''
    Clean data directory from bi9nary files files.
    Test needs this so known sensations are only created
    '''  
    def CleanDataDirectory(self):
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    if filename.endswith('.'+Sensation.BINARY_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print('os.remove(' + filepath + ') error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
            except Exception as e:
                    print('os.listdir error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
        
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
            while self.getAxon().empty() and i < VisualCommunicationTestCase.AXON_WAIT:
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

    '''
    Testing    
    '''
    
    def setUp(self):
        self.mainNames = self.MAINNAMES
        self.axon = Axon(robot=self) # parent axon
        self.visualCommunication = VisualCommunication(mainRobot=self,
                             parent=self,
                             instanceName='VisualCommunication',
                             instanceType= Sensation.InstanceType.SubInstance,
                             level=2)
        self.setRobotLocations(self.visualCommunication, self.getLocations())

        # define time in history, that is different than in all tests
        # not too far away in history, so sensation will not be deleted
        self.history_sensationTime = systemTime.time() -2*max(VisualCommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.stopSensation = self.visualCommunication.createSensation(memoryType=Sensation.MemoryType.Working,
                                            sensationType=Sensation.SensationType.Stop,
                                            robotType=Sensation.RobotType.Sense,
                                            locations=self.getLocations())

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.visualCommunication.createSensation(time=self.history_sensationTime,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VisualCommunicationTestCase.NAME,
                                                      score=VisualCommunicationTestCase.SCORE_1,
                                                      presence = Sensation.Presence.Present,
                                                      locations=self.getLocations())
        # Image is in LongTerm memoryType, it comes from TensorFlowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_image_sensation = self.visualCommunication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       locations=self.getLocations())
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = self.visualCommunication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data="1",
                                                       locations=self.getLocations())
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
        # these connected each other
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)

       
         
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)
#         
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())

        # get identity for self.visualCommunication as MainRobot does it (for images only)        
        self.studyOwnIdentity(robot=self.visualCommunication)
        
        # from testCommunication
        # other Robot
        self.sense = Robot(             mainRobot=self,
                                        parent=self,
                                        instanceName='Sense',
                                        instanceType= Sensation.InstanceType.SubInstance,
                                         level=2)
        self.setRobotMainNames(self.sense, self.OTHERMAINNAMES)
        self.setRobotLocations(self.sense, self.getLocations)
        
        # TODO other settings can be missing
        # We have not fetched communication! but hope it works as it is
        # without modification its data for test as testCommunication does
        
        self.technicalSensation = self.visualCommunication.createSensation(
                                                    robot = self.visualCommunication,
                                                    time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    name=VisualCommunicationTestCase.TECNICAL_NAME,
                                                    score=VisualCommunicationTestCase.SCORE_1,
                                                    presence=Sensation.Presence.Absent,
                                                    locations=self.getLocations())
        self.addToSensationDirectory(name='self.technicalSensation', dataId=self.technicalSensation.getDataId(), id=self.technicalSensation.getId())
        self.printSensationNameById(note='self.technicalSensation test', dataId=self.technicalSensation.getDataId())
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 1')

        # remember new previous
        self.previousGotMuscleVoice = None
        self.previousGotMuscleImage = None
        self.previousGotCommunicationVoice = None
        self.previousGotCommunicationImage = None
        
        # remember last got
        self.muscleVoice = None
        self.communicationVoice = None
        self.muscleImage = None
        self.communicationImage = None
        self.communicationItem = None
        
        

        
       
    def getSensations(self):

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        locations=self.getLocations()
        self.Wall_E_item_sensation = self.visualCommunication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VisualCommunicationTestCase.NAME,
                                                      score=VisualCommunicationTestCase.SCORE_1,
                                                      presence = Sensation.Presence.Present,
                                                      locations=locations)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
        image = self.visualCommunication.selfImage
        self.assertNotEqual(image, None, "image should not be None in this test")

        self.Wall_E_image_sensation = self.visualCommunication.createSensation( memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       image=image,
                                                       locations=locations)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
#         if len(self.visualCommunication.getMemory().getRobot().images) > 1:
#             image=self.visualCommunication.getMemory().getRobot().images[1]
        if len(self.visualCommunication.imageSensations) > 1:
           image = self.visualCommunication.imageSensations[1].getImage()
        else:
            image=None
        self.assertNotEqual(image, None, "image should not be None in this test")
        self.Wall_E_image_sensation_2 = self.visualCommunication.createSensation( memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense,
                                                       image=image,
                                                       locations=locations)
        
        
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation_2)

        # set association also to history
        self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
        
        # these connected each other
        #self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 4)# 4/3
        self.assertTrue(len(self.Wall_E_item_sensation.getAssociations()) == 3 or len(self.Wall_E_item_sensation.getAssociations()) == 4)# 3/4
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)#/1/2
        self.assertTrue(len(self.Wall_E_image_sensation.getAssociations()) == 1 or len(self.Wall_E_image_sensation.getAssociations()) == 2)#/1/2
        self.assertTrue(len(self.Wall_E_image_sensation_2.getAssociations()) == 1 or len(self.Wall_E_image_sensation_2.getAssociations()) == 2)
        
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_voice_sensation = self.visualCommunication.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Sense,
                                                       data="1",
                                                       locations=locations)
        self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
        self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
        # these connected each other
        self.assertTrue(len(self.Wall_E_item_sensation.getAssociations()) == 4 or len(self.Wall_E_item_sensation.getAssociations()) ==  5)
        self.assertTrue(len(self.Wall_E_image_sensation.getAssociations()) == 2 or len(self.Wall_E_image_sensation.getAssociations()) == 3) 
        self.assertTrue(len(self.Wall_E_voice_sensation.getAssociations()) == 2 or len(self.Wall_E_voice_sensation.getAssociations()) == 3)

        self.assertTrue(len(self.Wall_E_item_sensation.getAssociations()) == 4 or len(self.Wall_E_item_sensation.getAssociations()) == 5)
        self.assertTrue(len(self.Wall_E_image_sensation.getAssociations()) == 2 or len(self.Wall_E_image_sensation.getAssociations()) == 3)
        self.assertTrue(len(self.Wall_E_voice_sensation.getAssociations()) == 2 or len(self.Wall_E_voice_sensation.getAssociations()) == 3)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())
        
        # communication
        self.communication_item_sensation = self.visualCommunication.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Muscle,
                                                      name=VisualCommunicationTestCase.NAME,
                                                      presence = Sensation.Presence.Present,
                                                      locations=self.getLocations())

        image = self.visualCommunication.selfImage
        self.assertNotEqual(image, None, "image should not be None in this test")
        self.communication_image_sensation = self.visualCommunication.createSensation( memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       image=image,
                                                       locations=locations)
        
        self.communication_voice_sensation = self.visualCommunication.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Voice,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       data="1",
                                                       locations=locations)
        
        self.communication_positive_feeling_sensation = self.visualCommunication.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                                       sensationType=Sensation.SensationType.Feeling,
                                                       robotType=Sensation.RobotType.Muscle,
                                                       firstAssociateSensation=self.communication_item_sensation,
                                                       otherAssociateSensation=self.communication_voice_sensation,
                                                       positiveFeeling=True,
                                                       locations=locations)
#     '''
#     helper method to return different kind locations
#     '''       
#     def getLocations(self):    
#         if self.locationsInd >= len(self.ALL_LOCATIONS):
#             self.locationsInd=0
#         locations = self.ALL_LOCATIONS[self.locationsInd]
#         self.locationsInd = self.locationsInd+1
#         return locations
        


    def tearDown(self):
        #self.visualCommunication.stop()
        #self.assertEqual(self.visualCommunication.getAxon().empty(), False, 'Axon should not be empty after self.visualCommunication.stop()')
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get(robot=self)
            self.log(logStr='teardown self.getAxon().get(robot=self) sensation = {}'.format(sensation.toDebugStr()))
# assert disabled until we know if we need this
#             self.assertTrue(sensation.getSensationType() == Sensation.SensationType.Stop or\
#                             sensation.getSensationType() == Sensation.SensationType.Feeling,
#                             'parent should get Stop or Feeling sensation type after test and self.visualCommunication.stop()')
        
        while self.visualCommunication.running:
            systemTime.sleep(1)
         
        del self.visualCommunication
        del self.Wall_E_voice_sensation
# TODO check these
#         del self.Wall_E_image_sensation_2
#         del self.Wall_E_image_sensation
#         del self.Wall_E_item_sensation
        del self.axon
        
    def re_test_VisualCommunication(self):
        self.assertEqual(self.visualCommunication.getAxon().empty(), True, 'Axon should be empty at the beginning of test_VisualCommunication\nCannot test properly this!')
        self.visualCommunication.start()
        
        sleeptime = VisualCommunication.SLEEPTIME+VisualCommunication.SLEEPTIMERANDOM
        #sleeptime = VisualCommunication.SLEEPTIMERANDOM
        print("--- test sleeping " + str(sleeptime) + " second until starting to test")
        systemTime.sleep(sleeptime ) # let VisualCommunication start before waiting it to stops
        for i in range(VisualCommunicationTestCase.TEST_RUNS):
            self.getSensations()
            
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_item_sensation)
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_voice_sensation)
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation)
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_image_sensation_2)
 
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_item_sensation)
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_image_sensation)
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_voice_sensation)
 
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communication_positive_feeling_sensation)
                       
            sleeptime = 3
            print("--- test sleeping " + str(sleeptime) + " second until test results")
            systemTime.sleep(sleeptime ) # let VisualCommunication start before waiting it to stops
            # OOps assertEqual removed, study
            self.assertEqual(self.visualCommunication.getAxon().empty(), True, 'Axon should be empty again at the end of test_VisualCommunication!')
            #self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.Wall_E_voice_sensation)

# TODO Reenable stop       
#         print("--- put stop-sensation for VisualCommunication")
#         self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        
        print("--- test sleeping " + str(VisualCommunicationTestCase.TEST_TIME) + " second until stop should be done")
        systemTime.sleep(VisualCommunicationTestCase.TEST_TIME) # let result UI be shown until cleared           
        print("--- VisualCommunication should disappear when you press Stop now")
        
    '''
    functionality from Robot
    '''
    def studyOwnIdentity(self, robot):
        print("My name is " + robot.getName())
        # What kind we are
        print("My kind is " + str(robot.getKind()))      
        robot.selfSensation=robot.createSensation(sensationType=Sensation.SensationType.Item,
                                                memoryType=Sensation.MemoryType.LongTerm,
                                                robotType=Sensation.RobotType.Sense,# We have found this
                                                robot = robot.getName(),
                                                name = robot.getName(),
                                                presence = Sensation.Presence.Present,
                                                kind=robot.getKind(),
                                                locations=self.getLocations())
        robot.imageSensations, robot.voiceSensations = robot.getIdentitySensations(name=robot.getName())
        if len(robot.imageSensations) > 0:
            robot.selfImage = robot.imageSensations[0].getImage()
        else:
            robot.selfImage = None
            
######################
#
# first test from testCommunication
#
# self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
# -> 
# self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation=
#
# self.communication.getMemory()
# ->
# self.visualCommunication.getMemory()


    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def test_PresenseItemPresentRobot(self):
        self.assertEqual(self.visualCommunication.getAxon().empty(), True, 'Axon should be empty at the beginning of test_VisualCommunication\nCannot test properly this!')
        # TODO we should change elf.visualCommunication and its subRoobot Communication locations, but they are read from cfg-file
        # so this does not help
        self.setRobotLocations(self.visualCommunication, self.getLocations())
        self.visualCommunication.start()
        
        sleeptime = VisualCommunication.SLEEPTIME+VisualCommunication.SLEEPTIMERANDOM
        #sleeptime = VisualCommunication.SLEEPTIMERANDOM
        print("--- test sleeping " + str(sleeptime) + " second until starting to test")
        systemTime.sleep(sleeptime ) # let VisualCommunication start before waiting it to stops
        self.communication=None
        for subRobot in self.visualCommunication.getSubInstances():
            if subRobot.getName() == 'Communication':
                self.communication = subRobot
        self.assertFalse(self.communication==None, "No Communication found")
        self.assertTrue(self.communication.running, "No Communication running'")
        #Forse same location
        self.setRobotLocations(self.communication, self.getLocations())
         # TODO should set these, deleting others missing
        for location in self.communication.getLocations():
            self.communication.itemConversations[location] =\
                Communication.ConversationWithItem(robot=self.communication, location=location)
            self.communication.robotConversations[location] =\
                Communication.ConversationWithRobot(robot=self, location=location)
       # TODO proble is subinstabces in Communication, self.itemConversations[location] is wrong, should change this {} index
        # in live process

        # create Robot sensation
        # don't We test lining process so there should be this one in Axon
#         self.assertFalse(len(self.visualCommunication.getMemory().getAllPresentRobotSensations()) > 0)
#         self.assertFalse(self.visualCommunication.getMemory().hasRobotsPresence())
#         roboSensation=self.createSensation(associations=[],
#                                            robotType=Sensation.RobotType.Communication,
#                                            sensationName='roboSensation',
#                                            robot=self.visualCommunication,
#                                            sensationType = Sensation.SensationType.Robot,
#                                            memoryType = Sensation.MemoryType.Working,
#                                            name = self.visualCommunication.getName(),
#                                            presence = Sensation.Presence.Present,
#                                            locations = self.getLocations(),
#                                            mainNames=self.OTHERMAINNAMES), # Should haver other mainnames than this Robot to get robot presence
        
        self.assertTrue(len(self.visualCommunication.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertTrue(self.visualCommunication.getMemory().hasRobotsPresence())

        self.do_test_PresenseItemRobot(isPresentRobot = True)
            
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def test_PresenseItemAbsentRobot(self):
        self.assertEqual(self.visualCommunication.getAxon().empty(), True, 'Axon should be empty at the beginning of test_VisualCommunication\nCannot test properly this!')
        self.visualCommunication.start()
        
        sleeptime = VisualCommunication.SLEEPTIME+VisualCommunication.SLEEPTIMERANDOM
        #sleeptime = VisualCommunication.SLEEPTIMERANDOM
        print("--- test sleeping " + str(sleeptime) + " second until starting to test")
        systemTime.sleep(sleeptime ) # let VisualCommunication start before waiting it to stops

        self.communication=None
        for subRobot in self.visualCommunication.getSubInstances():
            if subRobot.getName() == 'Communication':
                self.communication = subRobot
        self.assertFalse(self.communication==None, "No Communication found")
        self.assertTrue(self.communication.running, "No Communication running'")
        #Forse same location
        self.setRobotLocations(self.communication, self.getLocations())
        # TODO should set these, deleting others missing
        for location in self.communication.getLocations():
            self.communication.itemConversations[location] =\
                Communication.ConversationWithItem(robot=self.communication, location=location)
            self.communication.robotConversations[location] =\
                Communication.ConversationWithRobot(robot=self, location=location)

       # create Robot sensation
        self.assertFalse(len(self.visualCommunication.getMemory().getAllPresentRobotSensations()) > 0)
        self.assertFalse(self.visualCommunication.getMemory().hasRobotsPresence())
        roboSensation=self.createSensation(associations=[],
                                           robotType=Sensation.RobotType.Communication,
                                           sensationName='roboSensation',
                                           robot=self.visualCommunication,
                                           sensationType = Sensation.SensationType.Robot,
                                           memoryType = Sensation.MemoryType.Working,
                                           name = self.visualCommunication.getName(),
                                           presence = Sensation.Presence.Absent,
                                           locations = self.getLocations())
        
        self.assertFalse(len(self.visualCommunication.getMemory().getAllPresentRobotSensations()) > 0)

        self.do_test_PresenseItemRobot(isPresentRobot = False)
        self.assertFalse(self.visualCommunication.getMemory().hasRobotsPresence())
        

  
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def do_test_PresenseItemRobot(self, isPresentRobot):
        print('\ntest_Presense')
        
        # We run lining process so here we clear Axon
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get(robot=self)
            self.log(logStr='do_test_PresenseItemRobot self.getAxon().get(robot=self) sensation = {}'.format(sensation.toDebugStr()))
        
                
        history_sensationTime = systemTime.time() -2*max(VisualCommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)

        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
        print('\n too old_Entering {}'.format(VisualCommunicationTestCase.NAME))
        Wall_E_item_sensation_entering = self.createSensation(
                                                 sensationName='Wall_E_item_sensation_entering',
                                                 robot=self.visualCommunication,
                                                 time=history_sensationTime,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=VisualCommunicationTestCase.NAME,
                                                 score=VisualCommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.getLocations())
        self.assertTrue(Wall_E_item_sensation_entering.isForgettable())
        self.printSensationNameById(note='Wall_E_item_sensation_entering test', dataId= Wall_E_item_sensation_entering.getDataId())
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering)
        # We get Voice, Image, if Communication can respond but it can't
        self.expect(isWait=True, name='Entering, Too old response', isEmpty=True)
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory()..getAllPresentItemSensations() should be 1')
      
        print('\n current Entering {}'.format(VisualCommunicationTestCase.NAME))
        # make potential response
        voice_sensation1 = self.createSensation(
                                                sensationName='voice_sensation1',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=VisualCommunicationTestCase.VOICEDATA2,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation1.isForgettable())
        self.printSensationNameById(note='voice_sensation1 test', dataId=voice_sensation1.getDataId())
        image_sensation1 = self.createSensation(
                                                sensationName='image_sensation1',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.assertTrue(image_sensation1.isForgettable())
        self.printSensationNameById(note='image_sensation1 test', dataId=image_sensation1.getDataId())
        item_sensation1 = self.createSensation(
                                                sensationName='item_sensation1',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(item_sensation1.isForgettable())
        self.printSensationNameById(note='item_sensation1 test', dataId=item_sensation1.getDataId())
        item_sensation1.associate(sensation=voice_sensation1)
        item_sensation1.associate(sensation=image_sensation1)
        voice_sensation1.associate(sensation=image_sensation1)

        Wall_E_item_sensation_entering2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering2',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(systemTime.time() - Wall_E_item_sensation_entering2.getTime() < Communication.COMMUNICATION_INTERVAL)
       
        self.assertTrue(Wall_E_item_sensation_entering2.isForgettable())
        self.printSensationNameById(note='Wall_E_item_sensation_entering2 test', dataId=Wall_E_item_sensation_entering2.getDataId())
         
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 1')
        # do we have Robots present
        if isPresentRobot:
            self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentRobotSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentRobotSensations() should be 1')
            communicationItem=Wall_E_item_sensation_entering2
            isExactCommunicationItem=True
        else:
            self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentRobotSensations()), 0, 'len(self.visualCommunication.getMemory().getAllPresentRobotSensations() should be 0')
            communicationItem=None
            isExactCommunicationItem=False
        # process Item SensaqtionType.Sense
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering2)
        self.expect(isWait=True,
                    name='Entering, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                    muscleImage=image_sensation1, isExactMuscleImage=True,
                    muscleVoice=voice_sensation1, isExactMuscleVoice=True,
                    communicationItem=communicationItem, isExactCommunicationItem=isExactCommunicationItem)
        

        if isPresentRobot:
            # This sensation should be processed in foreign Robot, but is test we do it in directly in same Communication-Robot
            # We will get same result, but no ask-sensation
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=True,
                        name='Entering, reply to communicationItem, response 1', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation1, isExactCommunicationImage=True,
                        communicationVoice=voice_sensation1, isExactCommunicationVoice=True,
                        communicationItem=None)        # TODO remove this, it is not valid any more       


       
        print('\n current Present {}'.format(VisualCommunicationTestCase.NAME))
        Wall_E_item_sensation_present = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present test', dataId=Wall_E_item_sensation_present.getDataId())
        # make potential response
        voice_sensation2 = self.createSensation(
                                                sensationName='voice_sensation2',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=VisualCommunicationTestCase.VOICEDATA2,
                                                locations=self.getLocations())
        self.assertTrue(voice_sensation2.isForgettable())
        self.printSensationNameById(note='voice_sensation2 test', dataId=voice_sensation2.getDataId())
        
        image_sensation2 = self.createSensation(
                                                sensationName='image_sensation2',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.assertTrue(image_sensation2.isForgettable())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        
        item_sensation2 = self.createSensation(
                                                sensationName='item_sensation2',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.assertTrue(item_sensation2.isForgettable())
        self.printSensationNameById(note='image_sensation2 test', dataId=image_sensation2.getDataId())
        item_sensation2.associate(sensation=voice_sensation2)
        item_sensation2.associate(sensation=image_sensation2)
        voice_sensation2.associate(sensation=image_sensation2)

        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (and be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 1')

         # do we have Robots present
        if isPresentRobot:
            communicationItem=Wall_E_item_sensation_present
            isExactCommunicationItem=True
        else:
            communicationItem=None
            isExactCommunicationItem=False
       # process       
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present)
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(isWait=True,
                    name='Present, response', isEmpty=False,
                    muscleImage=image_sensation2, isExactMuscleImage=True,
                    muscleVoice=voice_sensation2, isExactMuscleVoice=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True,
                    communicationItem=communicationItem, isExactCommunicationItem=isExactCommunicationItem)
        
        if isPresentRobot:
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=True,
                        name='Entering, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationImage=image_sensation2, isExactMuscleImage=True,
                        communicationVoice=voice_sensation2, isExactMuscleVoice=True,
                        communicationItem=None)


        
        print('\n current Absent {}'.format(VisualCommunicationTestCase.NAME))
        Wall_E_item_sensation_absent = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent test', dataId=Wall_E_item_sensation_absent.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 0, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 0')

        #process              
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 0, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 0')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        self.expect(isWait=True,
                    name='Absent', isEmpty=False, #isSpoken=False, isHeard=False,
                    isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
        
 
        # NAME with NAME2
        
        print('\n NAME current Entering {}',format(VisualCommunicationTestCase.NAME))
        # make potential response
        voice_sensation3 = self.createSensation(
                                                sensationName='voice_sensation3',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=VisualCommunicationTestCase.VOICEDATA3,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation3 test', dataId=voice_sensation3.getDataId())
        image_sensation3 = self.createSensation(
                                                sensationName='image_sensation3',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation3 test', dataId=image_sensation3.getDataId())
        item_sensation3 = self.createSensation(
                                                sensationName='item_sensation3',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation3 test', dataId=item_sensation3.getDataId())
        item_sensation3.associate(sensation=voice_sensation3)
        item_sensation3.associate(sensation=image_sensation3)
        voice_sensation3.associate(sensation=image_sensation3)
        
        # make entering item and process
        Wall_E_item_sensation_entering3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering3',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_entering3 test', dataId=Wall_E_item_sensation_entering3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 1')

         # do we have Robots present
        if isPresentRobot:
            communicationItem=Wall_E_item_sensation_entering3
            isExactCommunicationItem=True
        else:
            communicationItem=None
            isExactCommunicationItem=False

        #process                      
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering3)
        # will get images/voices #2, because they have better feeling than #3
        # TODO Check this, we get #3 sensations
        self.expect(isWait=True,
                    name='Present Name 2, Conversation continues', isEmpty=False,# isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    muscleVoice=voice_sensation3, isExactMuscleVoice=True,
                    muscleImage=image_sensation3, isExactMuscleImage=True,
                    communicationItem=communicationItem, isExactCommunicationItem=isExactCommunicationItem)

        if isPresentRobot:
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=True,
                        name='Entering, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationVoice=voice_sensation3, isExactCommunicationVoice=True,
                        communicationImage=image_sensation3, isExactCommunicationImage=True,
                        communicationItem=None)

        
        print('\n NAME2 current Entering {}'.format(VisualCommunicationTestCase.NAME2))
        # make potential response
        voice_sensation4 = self.createSensation(
                                                sensationName='voice_sensation4',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=VisualCommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation4 test', dataId=voice_sensation4.getDataId())
        image_sensation4 = self.createSensation(
                                                sensationName='image_sensation4',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation4 test', dataId=image_sensation4.getDataId())
        item_sensation4 = self.createSensation(
                                                sensationName='image_sensation4',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation4 test', dataId=item_sensation4.getDataId())
        item_sensation4.associate(sensation=voice_sensation4)
        item_sensation4.associate(sensation=image_sensation4)
        voice_sensation4.associate(sensation=image_sensation4)
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 2, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 2')

        # make entering and process
        Wall_E_item_sensation_entering4 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_entering4',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_entering4 test', dataId=Wall_E_item_sensation_entering4.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        # other entering is handled as response
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 2, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 2')

         # do we have Robots present
        if isPresentRobot:
            communicationItem=Wall_E_item_sensation_entering4
            isExactCommunicationItem=True
        else:
            communicationItem=None
            isExactCommunicationItem=False

        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_entering4)
        self.expect(isWait=True,
                    name='Entering Name2, change in presentation',  isEmpty=False, #isSpoken=True, isHeard=False,
                    muscleVoice=voice_sensation4, isExactMuscleVoice=True,
                    muscleImage=image_sensation4, isExactMuscleImage=True,
                    communicationItem=communicationItem,
                    isExactCommunicationItem=isExactCommunicationItem,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)

        if isPresentRobot:
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            self.expect(isWait=True,
                        name='Entering, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationVoice=voice_sensation4, isExactMuscleVoice=True,
                        communicationImage=image_sensation4, isExactMuscleImage=True,
                        communicationItem=None)
        

        print('\n NAME2 current Present {}'.format(VisualCommunicationTestCase.NAME2))
        # added make potential response
        voice_sensation5 = self.createSensation(
                                                sensationName='voice_sensation5',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=VisualCommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation5 test', dataId=voice_sensation5.getDataId())
        image_sensation5 = self.createSensation(
                                                sensationName='image_sensation5',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation5 test', dataId=image_sensation5.getDataId())
        item_sensation5 = self.createSensation(
                                                sensationName='item_sensation5',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation5 test', dataId=item_sensation5.getDataId())
        item_sensation5.associate(sensation=voice_sensation5)
        item_sensation5.associate(sensation=image_sensation5)
        voice_sensation5.associate(sensation=image_sensation5)

        Wall_E_item_sensation_present2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present2',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Present,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_present2 test', dataId=Wall_E_item_sensation_present2.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
       
         # do we have Robots present
        if isPresentRobot:
            communicationItem=Wall_E_item_sensation_present2
            isExactCommunicationItem=True
        else:
            communicationItem=None
            isExactCommunicationItem=False

        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present2)
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 2, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 2')
        self.expect(isWait=True,
                    name='Present Name 2, change in presentation',  isEmpty=False, #isSpoken=True, isHeard=False,
                    muscleVoice=voice_sensation5, isExactMuscleVoice=True,
                    muscleImage=image_sensation5, isExactMuscleImage=True,
                    communicationItem=communicationItem,
                    isExactCommunicationItem=isExactCommunicationItem,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        if isPresentRobot:
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            
            self.expect(isWait=True,
                        name='Entering, reply to communicationItem, response 2', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationVoice=voice_sensation5, isExactCommunicationVoice=True,
                        communicationImage=image_sensation5, isExactCommunicationImage=True,
                        communicationItem=None)

        print('\n NAME2 current Present again {}'.format(VisualCommunicationTestCase.NAME2))
        # make potential response
        voice_sensation6 = self.createSensation(
                                                sensationName='voice_sensation6',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Voice,
                                                robotType=Sensation.RobotType.Sense,
                                                data=VisualCommunicationTestCase.VOICEDATA4,
                                                locations=self.getLocations())
        self.printSensationNameById(note='voice_sensation6 test', dataId=voice_sensation6.getDataId())
        image_sensation6 = self.createSensation(
                                                sensationName='image_sensation6',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Sensory,
                                                sensationType=Sensation.SensationType.Image,
                                                robotType=Sensation.RobotType.Sense,
                                                locations=self.getLocations())
        self.printSensationNameById(note='image_sensation6 test', dataId=image_sensation6.getDataId())
        item_sensation6 = self.createSensation(
                                                sensationName='item_sensation6',
                                                robot=self.visualCommunication,
                                                time=self.history_sensationTime,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_2,
                                                presence=Sensation.Presence.Entering,
                                                locations=self.getLocations())
        self.printSensationNameById(note='item_sensation6 test', dataId=item_sensation6.getDataId())
        item_sensation6.associate(sensation=voice_sensation6)
        item_sensation6.associate(sensation=image_sensation6)
        voice_sensation6.associate(sensation=image_sensation6)

        Wall_E_item_sensation_present3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_present3',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_1,
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
       
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_present3)
        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 2, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 2')
        # TODO Next commented test should be valid Why this?
        #self.expect(name='Present NAME2 again basic change in presentation', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
        # TODO We don't get Communication sensations, because limit is exceede
        # But Communication implementation will we Changed
        self.expect(isWait=True,
                    name='Present NAME2 again basic change in presentation', isEmpty=False, # isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    muscleVoice=voice_sensation6, isExactMuscleVoice=True,
                    muscleImage=image_sensation6, isExactMuscleImage=True,
                    communicationItem=communicationItem,
                    isExactCommunicationItem=isExactCommunicationItem,
                    communicationVoice=None,
                    communicationImage=None,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)

        if isPresentRobot:
            self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.communicationItem)
            
            self.expect(isWait=True,
                        name='Entering, reply to communicationItem, response 6', isEmpty=False, #isSpoken=True, isHeard=False, isVoiceFeeling=False,
                        communicationVoice=voice_sensation6, isExactCommunicationVoice=True,
                        communicationImage=image_sensation6, isExactCommunicationImage=True,
                        communicationItem=None)
        
        print('\n NAME2 current Absent {}'.format(VisualCommunicationTestCase.NAME2))
        Wall_E_item_sensation_absent2 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent2',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME2,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent2 test', dataId=Wall_E_item_sensation_absent2.getDataId())
       
        #simulate TensorFlowClassification send presence item to MainRobot
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent2)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 1, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(isWait=True,
                    name='Absent NAME2', isEmpty=False, #isSpoken=False, isHeard=False,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isNegativeFeeling=True)
    

        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(VisualCommunicationTestCase.NAME))
        Wall_E_item_sensation_absent3 = self.createSensation(
                                                sensationName='Wall_E_item_sensation_absent3',
                                                robot=self.visualCommunication,
                                                memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Item,
                                                robotType=Sensation.RobotType.Sense,
                                                name=VisualCommunicationTestCase.NAME,
                                                score=VisualCommunicationTestCase.SCORE_1,
                                                presence=Sensation.Presence.Absent,
                                                locations=self.getLocations())
        self.printSensationNameById(note='Wall_E_item_sensation_absent3 test', dataId=Wall_E_item_sensation_absent3.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot       
        self.visualCommunication.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation_absent3)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.visualCommunication.getMemory().getAllPresentItemSensations()), 0, 'len(self.visualCommunication.getMemory().getAllPresentItemSensations() should be 0')
        self.expect(isWait=True,
                    name='Absent NAME', isEmpty=True)#isSpoken=False, isHeard=False, isVoiceFeeling=False)
       


# first test from testCommunication
#
######################
 
        
if __name__ == '__main__':
    unittest.main()

 