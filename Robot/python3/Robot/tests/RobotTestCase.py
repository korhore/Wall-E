'''
Created on 10.04.2021
Updated on 09.12.2021
@author: reijo.korhonen@gmail.com

Base class routines used to test-clersses for Robot-delivered classes.
This class do't make tests, but includes helper methods for testing.

Robot modeling
--------------
 Plays a (Main)Robot so we run tested Robot class as subRobot as they
 are run normally
 
 Robot set methods
 -----------------
 Methods that set Robot configuration to certain state, needed for testing.
 
 Sensation directory
 -------------------
 Expect
 ------
 
 When we test Robot we put by MainRobot Sensations to Robots Axon,
 which we test. That Robot proceses it and Return to MainRobot - This testing class -
 Sensations that this class checks that wanted functionality is got.
 This is goal of testing Robots.
 

python3 -m unittest tests/<RobotTestCase delivered test cladssfile>.py



'''
import time as systemTime
import os
import shutil
from PIL import Image as PIL_Image

from Sensation import Sensation
from Robot import Robot
from VisualCommunication.VisualCommunication import VisualCommunication
from Association.Association import Association
from Communication.Communication import Communication
from Axon import Axon

class RobotTestCase():
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
    
    MAINNAMES = ["MainName"]
    OTHERMAINNAMES = ["OTHER_MainName"]

    LOCATIONS_1 = ["location1"]
    LOCATIONS_2 = ["OtherLocation"]
    LOCATIONS_1_2 = ["location1","OtherLocation"]
    ALL_LOCATIONS = [LOCATIONS_1,LOCATIONS_2,LOCATIONS_1_2]
    locationsInd = 0
    
    # from testCommunicatoion
    ASSOCIATION_INTERVAL=3.0 # in float seconds
    AXON_WAIT = 60           # in int time to conditionally wait to get something into Axon

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
    VOICEDATA_IGNORED=b'0x000x00x01x01x01x01x01x01x01x01x01'
    BEST_FEELING = Sensation.Feeling.Happy
    BETTER_FEELING = Sensation.Feeling.Good
    NORMAL_FEELING = Sensation.Feeling.Normal
    NEUTRAL_FEELING = Sensation.Feeling.Neutral
        
    SensationDirectory=[]
    SensationDataDirectory=[]
   
       
    '''
    Robot modeling
    '''

    
    
    def getAxon(self):
        #return self.axon
        # try
        return self.robot.axon
        print ("self.axon was OK")
    def getId(self):
        return 1.1
    def getName(self):
        return RobotTestCase.NAME
    def setMainNames(self, mainNames):
        self.mainNames = mainNames
    def getMainNames(self):
        return self.mainNames
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
    def setSubInstances(self, robot, subInstances):
        robot.subInstances = subInstances

    def getParent(self):
        return None
    '''
    route to test class
    '''
    def route(self, transferDirection, sensation):
        self.log(logLevel=self.robot.LogLevel.Normal, logStr='route: ' + sensation.toDebugStr())
        self.log(logLevel=self.robot.LogLevel.Detailed, logStr='route: '  + str(transferDirection) +  ' ' + sensation.toDebugStr())
        self.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
        
    def getCapabilityInstances(self, robotType, memoryType, sensationType, locations, mainNames):
        robots=[self]
        return robots
    def getInstanceType(self):
        return Sensation.InstanceType.Real
 
    '''
    get test locations
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
            if self.robot:
                if logLevel == None:
                    logLevel = self.robot.LogLevel.Normal
                if logLevel <= self.robot.getLogLevel():
                     print(self.robot.getName() + ":" + str( self.robot.config.level) + ":" + Sensation.Modes[self.robot.mode] + ": " + logStr)
    
    def logAxon(self):
        self.log("{} Axon with queue length {} full {}".format(self.getName(), self.getAxon().queue.qsize(), self.getAxon().queue.full()))
        
    '''
    process sensation in tested Robot
    If living process we put sensation in Robots Axon
    but if robot is static state, then we call oitst process-method
    '''
        
    def doProcess(self, robot, sensation):
        if self.robot.running:
            robot.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        else:
            robot.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
        

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
                 negativeFeeling = None,
                 robotState = None):
        
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
                 negativeFeeling=negativeFeeling,
                 robotState=robotState)
            
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
    Clean data directory from image, voice, binary and bak -files.
    Test needs this so known sensations are only created
    '''  
    def CleanDataDirectory(self):
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    for format in (Sensation.IMAGE_FORMAT, Sensation.VOICE_FORMAT, Sensation.BINARY_FORMAT,'bak'):
                        if filename.endswith('.'+format):
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
               isWait=False,
               robotStates=None):
        print("\nexpect {}".format(name))
        self.muscleVoice = None
        self.muscleImage = None
        self.communicationVoice  = None
        self.communicationImage = None
        self.robotStates = None

        gotCommunicationItem = None
        errortext = '{}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        i=0  
        if isWait:# and not isEmpty: 
             while self.getAxon().empty() and i < Communication.COMMUNICATION_INTERVAL:
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
            if robotStates is not None:
                isrobotStateStillExpected = True
            else:
                isrobotStateStillExpected = False
                
            isVoiceFeelingStillExpected = isVoiceFeeling
            isImageFeelingStillExpected = isImageFeeling
            while (not isWait and not self.getAxon().empty()) or\
                  (isWait and (i < Communication.COMMUNICATION_INTERVAL and\
                   (isMuscleVoiceStillExpected or isCommunicationVoiceStillExpected or\
                    isMuscleImageStillExpected or isCommunicationImageStillExpected or\
                    isVoiceFeelingStillExpected or isImageFeelingStillExpected or
                    isItemStillExpected or isrobotStateStillExpected))):
                while isWait and self.getAxon().empty() and i < Communication.COMMUNICATION_INTERVAL:
                    systemTime.sleep(1)
                    i=i+1
                    print('slept {}s to get something to Axon'.format(i))
                    
                if not self.getAxon().empty():
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
    # We can get many Feeling for same Voice, so  many feelings is not unexpected
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
                    elif sensation.getSensationType() == Sensation.SensationType.RobotState:
                        if robotStates is None:
                            self.assertTrue(False,"got RobotState but it was not expected to get at all {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                        if sensation.getRobotState() in robotStates:
                            isRobotStateStillExpected = False
                        else:
                            self.assertTrue(False,"got unexpected RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                    
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
        # TODO responses and answers should be Forgettable, but
        # we should test instead Communication.spokedAssociations
        # and .sensations.
        if self.muscleVoice != None:
            self.muscleVoice.logAttachedBy()
            self.assertTrue(self.muscleVoice.isForgettable(), self.muscleVoice.getAttachedByRobotStr())
                
        if self.muscleImage != None:
            self.muscleImage.logAttachedBy()
            self.assertTrue(self.muscleImage.isForgettable(), self.muscleImage.getAttachedByRobotStr())

        if self.communicationVoice  != None:
            self.communicationVoice.logAttachedBy()
            self.assertTrue(self.communicationVoice .isForgettable(), self.communicationVoice.getAttachedByRobotStr())
            
        if self.communicationImage != None:
            self.communicationImage.logAttachedBy()
            self.assertTrue(self.communicationImage.isForgettable(), self.communicationImage.getAttachedByRobotStr())
                
        # previous
        
        if self.previousGotMuscleVoice != None:
            self.previousGotMuscleVoice.logAttachedBy()
            self.assertTrue(self.previousGotMuscleVoice.isForgettable(), self.previousGotMuscleVoice.getAttachedByRobotStr())
                
        if self.previousGotMuscleImage != None:
            self.previousGotMuscleImage.logAttachedBy()
            self.assertTrue(self.previousGotMuscleImage.isForgettable(), self.previousGotMuscleImage.getAttachedByRobotStr())

        if self.previousGotCommunicationVoice != None:
            self.previousGotCommunicationVoice.logAttachedBy()
            self.assertTrue(self.previousGotCommunicationVoice.isForgettable(), self.previousGotCommunicationVoice.getAttachedByRobotStr())
            
        if self.previousGotCommunicationImage != None:
            self.previousGotCommunicationImage.logAttachedBy()
            self.assertTrue(self.previousGotCommunicationImage.isForgettable(), self.previousGotCommunicationImage.getAttachedByRobotStr())
                
        # remember new previous
        self.previousGotMuscleVoice = self.muscleVoice 
        self.previousGotMuscleImage = self.muscleImage
        self.previousGotCommunicationVoice = self.communicationVoice 
        self.previousGotCommunicationImage = self.communicationImage

        return self.muscleVoice

    '''
    Testing    
    '''
    '''
    setUp is overridden  in subclass
    and it should call this
    
    doSetUp
    '''    
    def doSetUp(self, robot):
        self.robot = robot
        self.mainNames = self.MAINNAMES
        self.axon = Axon(robot=self) # parent axon

        self.history_sensationTime = systemTime.time() -2*max(RobotTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
        self.technicalSensation = robot.createSensation(
                                                    robot = robot,
                                                    time=self.history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Working,
                                                    sensationType=Sensation.SensationType.Item,
                                                    robotType=Sensation.RobotType.Sense,
                                                    name=RobotTestCase.TECNICAL_NAME,
                                                    score=RobotTestCase.SCORE_1,
                                                    presence=Sensation.Presence.Absent,
                                                    locations=self.getLocations())
        self.addToSensationDirectory(name='self.technicalSensation', dataId=self.technicalSensation.getDataId(), id=self.technicalSensation.getId())
        self.printSensationNameById(note='self.technicalSensation test', dataId=self.technicalSensation.getDataId())
        self.assertEqual(len(robot.getMemory().getAllPresentItemSensations()), 0, 'len(self.robot.getMemory().getAllPresentItemSensations() should be 0')

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
        
        

        

    '''
    tearDown is overridden in subclass and it should call this
    doTearDown
    '''
    def doTearDown(self):
        print('\nRobotTestCase:doTearDown')       
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get(robot=self)
            self.log(logStr='doTearDown self.getAxon().get(robot=self) sensation = {}'.format(sensation.toDebugStr()))
         
        del self.axon
        del self.technicalSensation
        
 