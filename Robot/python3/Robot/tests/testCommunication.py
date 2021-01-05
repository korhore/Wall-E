'''
Created on 21.06.2019
Updated on 04.01.2021
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
from Robot import Robot

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
    NEUTRAL_FEELING = Sensation.Feeling.Neutral
    
    MAINNAMES = ["CommunicationTestCaseMainName"]
    OTHERMAINNAMES = ["OTHER_CommunicationTestCaseMainName"]
    
    LOCATIONS = ['testLocation']

    
    SensationDirectory=[]
    SensationDataDirectory=[]
   
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        #print('CommunicationTestCase getAxon')
        return self.axon
    def getId(self):
        #print('CommunicationTestCase getId')
        return 1.1
    def getName(self):
        #print('CommunicationTestCase getName')
        return "CommunicationTestCase"
    
    def getLocations(self):
        return self.LOCATIONS
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
        #print('CommunicationTestCase log')
        if hasattr(self, 'communication'):
            if self.communication:
                if logLevel == None:
                    logLevel = self.communication.LogLevel.Normal
                if logLevel <= self.communication.getLogLevel():
                     print(self.communication.getName() + ":" + str( self.communication.config.level) + ":" + Sensation.Modes[self.communication.mode] + ": " + logStr)
    
    def logAxon(self):
        self.log("{} Axon with queue length {} full {}".format(self.getName(), self.getAxon().queue.qsize(), self.getAxon().queue.full()))
        
    '''
    Helper methods
    '''
    '''
    Sensation constructor that takes care, that we have only one instance
    per Sensation per number
    
    This is needed if we want handle associations properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constructor
    but robot to do the job is added
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
                 isCommunication = None,                 
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
                 isCommunication=isCommunication,
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
        # associate to self sensations
        sensation.associate(sensation=self.Wall_E_item_sensation, feeling=feeling)
#         sensation.associate(sensation=self.Wall_E_image_sensation, feeling=feeling)
#         sensation.associate(sensation=self.Wall_E_voice_sensation, feeling=feeling)

        # add sensation to directory, so we can find it's name by ids
        self.addToSensationDirectory(name=sensationName, dataId=sensation.getDataId(), id=sensation.getId())
        return sensation
        


        
    def addToSensationDirectory(self,  name, dataId, id=None):
        if id != None:
            self.SensationDirectory.append((id, name))
        self.SensationDataDirectory.append((dataId, name))
       
    def getSensationNameByDataId(self, note, dataId=None,id=None):
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
        print('\n{}\n'.format(self.getSensationNameByDataId(note=note, dataId=dataId,id=id)))
        
    def logCommunicationState(self, note=''):
        print('logCommunicationState ' + note)
        for i in range(len(self.communication.heardSensations)):
            print("self.communication.heardSensations[{}] {}".format(i, self.getSensationNameByDataId(id=self.communication.heardSensations[i], note='')))
        for i in range(len(self.communication.saidSensations)):
            print("self.communication.saidSensations[{}] {}".format(i, self.getSensationNameByDataId(id=self.communication.saidSensations[i], note='')))


    '''
    Testing    
    '''
    
    def setUp(self):
        print('\nsetUp')
        Robot.mainRobotInstance = self
        self.mainNames = self.MAINNAMES
        self.axon = Axon(robot=self)
        # Communication gets its own Memory
        # this is not same situation thab in normal run, where MainRobot level own Memory
        # this should be handled in test
        self.sense = Robot(parent=self,
                                           instanceName='Sense',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.setRobotMainNames(self.sense, self.OTHERMAINNAMES)
        self.setRobotLocations(self.sense, self.LOCATIONS)
        
        self.communication = Communication(parent=self,
                                           instanceName='Communication',
                                           instanceType= Sensation.InstanceType.SubInstance,
                                           level=2)
        self.setRobotMainNames(self.communication, self.MAINNAMES)
        self.setRobotLocations(self.communication, self.LOCATIONS)
#         # remember original MainNames
#         self.originalMainNames = self.communication.getMainNames()
        # should get Identity for proper functionality. Use Wall-E Identity in test
        self.communication.imageSensations, self.communication.voiceSensations = \
            self.communication.getIdentitySensations(name=CommunicationTestCase.NAME)
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
        #self.SensationDirectory.append((self.Wall_E_item_sensation.getDataId(),'self.Wall_E_item_sensation'))
        self.addToSensationDirectory(name='self.Wall_E_item_sensation', dataId=self.Wall_E_item_sensation.getDataId(), id=self.Wall_E_item_sensation.getId())
        self.printSensationNameById(note='self.Wall_E_item_sensation test', dataId=self.Wall_E_item_sensation.getDataId())
        # Image is in LongTerm memoryType, it comes from TensorFlowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
# commented out, so test will use their own sensations
#         self.Wall_E_image_sensation = self.communication.createSensation(time=self.history_sensationTime,
#                                                        memoryType=Sensation.MemoryType.Working,
#                                                        sensationType=Sensation.SensationType.Image,
#                                                        robotType=Sensation.RobotType.Sense)
#         #self.SensationDirectory.append((self.Wall_E_image_sensation.getDataId(),'self.Wall_E_image_sensation'))
#         self.addToSensationDirectory(name='self.Wall_E_image_sensation', dataId=self.Wall_E_image_sensation.getDataId(), id=self.Wall_E_image_sensation.getId())
#         self.printSensationNameById(note='self.Wall_E_image_sensation', dataId=self.Wall_E_image_sensation.getDataId())
#         self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation)
#         # set association also to history
#         self.Wall_E_item_sensation.getAssociation(sensation=self.Wall_E_image_sensation).setTime(time=self.history_sensationTime)
#         
#         # these connected each other
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 1)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 1)
#         
#         #systemTime.sleep(0.1)  # wait to get really even id
#         self.Wall_E_voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
#                                                        memoryType=Sensation.MemoryType.Sensory,
#                                                        sensationType=Sensation.SensationType.Voice,
#                                                        robotType=Sensation.RobotType.Sense,
#                                                        data=CommunicationTestCase.VOICEDATA1)
#         #self.SensationDirectory.append((self.Wall_E_voice_sensation.getDataId(),'self.Wall_E_voice_sensation'))
#         self.addToSensationDirectory(name='self.Wall_E_voice_sensation', dataId=self.Wall_E_voice_sensation.getDataId(), id=self.Wall_E_voice_sensation.getId())
#         self.printSensationNameById(note='self.Wall_E_voice_sensation test', dataId=self.Wall_E_voice_sensation.getDataId())
#         self.Wall_E_item_sensation.associate(sensation=self.Wall_E_voice_sensation)
#         self.Wall_E_image_sensation.associate(sensation=self.Wall_E_voice_sensation)
#         # these connected each other
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)

       
         
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), 0)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_voice_sensation.getAssociations()), 2)
        
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.Wall_E_voice_sensation_association_len = len(self.Wall_E_voice_sensation.getAssociations())
        
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
        #self.SensationDirectory.append((self.Eva_item_sensation.getDataId(),'self.Eva_item_sensation'))
        self.addToSensationDirectory(name='self.Eva_item_sensation', dataId=self.Eva_item_sensation.getDataId(), id=self.Eva_item_sensation.getId())
        self.printSensationNameById(note='self.Eva_item_sensation test', dataId=self.Eva_item_sensation.getDataId())
        # Image is in LongTerm memoryType, it comes from TensorFlowClassification and is crop of original big image
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Eva_image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       sensationType=Sensation.SensationType.Image,
                                                       robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((self.Eva_image_sensation.getDataId(),'self.Eva_image_sensation'))
        self.addToSensationDirectory(name='self.Eva_image_sensation', dataId=self.Eva_image_sensation.getDataId(), id=self.Eva_image_sensation.getId())
        self.printSensationNameById(note='self.Eva_image_sensation test', dataId=self.Eva_image_sensation.getDataId())
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
        #self.SensationDirectory.append((self.Eva_voice_sensation.getDataId(),'self.Eva_voice_sensation'))
        self.addToSensationDirectory(name='self.Eva_voice_sensation', dataId=self.Eva_voice_sensation.getDataId(), id=self.Eva_voice_sensation.getId())
        self.printSensationNameById(note='self.Eva_voice_sensation test', dataId=self.Eva_voice_sensation.getDataId())
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
        del self.sense
#         del self.Wall_E_voice_sensation
#         del self.Wall_E_image_sensation
        del self.Wall_E_item_sensation
  
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    '''    
    def test_Presense(self):
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
        self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId= Wall_E_item_sensation.getDataId())
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
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
         
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        #self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()[Wall_E_item_sensation.getName()].getAssociations()), 1)
        
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        # now we should get Voice, Robot is presenting itself
        # TODO, but we get 2 voices, Communication is too voice, because it introduces itself and starts to speak.
        self.expect(name='Entering, response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False,
                    image=image_sensation, voice=voice_sensation)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        # added
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA2)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (and be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')

        # process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(name='Present, response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False,
                    image=image_sensation, voice=voice_sensation)

        
        print('\n current Absent {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
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
        self.expect(name='Absent', isEmpty=False, isSpoken=False, isHeard=False, isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
        
 
        # NAME with NAME2
        
        print('\n NAME current Entering {}',format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA3)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME,
                                                  score=CommunicationTestCase.SCORE_1,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)
        
        # make entering item and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME,
                                                  score=CommunicationTestCase.SCORE_1,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 1')

        #process                      
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        #self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty, when entering')
        self.expect(name='Present Name 2, Conversation continues', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)
        
        print('\n NAME2 current Entering {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA4)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME2,
                                                  score=CommunicationTestCase.SCORE_2,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)
        #simulate TensorFlowClassification send presence item to MainRobot
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
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
       #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 2')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.expect(name='Entering Name 2, change in presentation',  isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)
        
        print('\n NAME2 current Present {}'.format(CommunicationTestCase.NAME2))
        # added make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA4)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME2,
                                                  score=CommunicationTestCase.SCORE_2,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # TODO We find response
        # TODO if we find voice we speak, but now all voices are used. at this point
        # There has not been changes of present items and we have conversation on, but we have not send response
        # so we don't get response at this point
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        self.expect(name='Present Name 2, change in presentation',  isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)

        print('\n NAME2 current Present again {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=Sensation.RobotType.Sense,
                                                  data=CommunicationTestCase.VOICEDATA4)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME2,
                                                  score=CommunicationTestCase.SCORE_2,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # There has not been changes of present items and we have conversation on, but we have not send response
        # so we don't get response at this point
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        # TODO Next commented test should be valid Why this?
        #self.expect(name='Present NAME2 again basic change in presentation', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
        self.expect(name='Present NAME2 again basic change in presentation', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)
        
        print('\n NAME2 current Absent {}'.format(CommunicationTestCase.NAME2))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
       
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(name='Absent NAME2', isEmpty=False, isSpoken=False, isHeard=False, isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
    

        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 0, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 0')
        self.expect(name='Absent NAME', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
       

    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in same Robot.mainNames and robotType=Sensation.RobotType.Sense
    so this test is same than without paramweters
    '''    
    def test_2_Presense(self):
        self.do_test_Presense(mainNames=self.MAINNAMES, robotType=Sensation.RobotType.Sense, isCommunication=False)
        
    '''
    TensorfloClöassafication produces
    Item.name Working Out
    Sensations outside Robot are in other Robot.mainNames and robotType=Sensation.RobotType.Muscle
    so this test result should  same than with test where robotType=Sensation.RobotType.Sense,
    because Communication should handle those sensation equally, when Robot.mainNames differ
    
    TODO study this
    '''    
    def re_test_3_Presense(self):
        self.do_test_Presense(mainNames=self.OTHERMAINNAMES, robotType=Sensation.RobotType.Muscle, isCommunication=True)

    '''
    TensorfloClöassafication produces
    Item.name Working Out
    
    # TODO self.create
    '''    
    def do_test_Presense(self, mainNames, robotType, isCommunication):
        print('\ndo_test_Presense {} {}'.format(mainNames, robotType))

        # robot setup        
        self.setRobotMainNames(self.sense, mainNames)
                
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
                                                 presence=Sensation.Presence.Entering,
                                                 locations=self.getLocations())
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        # We get Voice, if Communication can respond but it cant
        self.expect(name='Entering, Too old response', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)        # Not sure do we always get a voice
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory()..getAllPresentItemSensations() should be 1')
      
        print('\n current Entering {}'.format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=robotType,
                                                  isCommunication=isCommunication,
                                                  data=CommunicationTestCase.VOICEDATA2)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=robotType,
                                                  isCommunication=isCommunication)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        #self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()[Wall_E_item_sensation.getName()].getAssociations()), 1)
        
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        # now we should get Voice, Robot is presenting itself
        # TODO, but we get 2 voices, Communication is too voice, because it introduces itself and starts to speak.
        self.expect(name='Entering, response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False,
                    image=image_sensation, voice=voice_sensation)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        # added
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=robotType,
                                                  data=CommunicationTestCase.VOICEDATA2)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=robotType)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                          memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Entering)
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (and be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')

        # process       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        self.expect(name='Present, response', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False,
                    image=image_sensation, voice=voice_sensation)

        
        print('\n current Absent {}'.format(CommunicationTestCase.NAME))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() after Absent Item Sensation should be 1')

        #process              
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
 
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        # if absent, Communication does not anyone to speak with
        # at this point Communication should cancel timer, because there no one to speak with.
        # We had said something else than presenting ourselves, so we would get a negative feeling
        self.expect(name='Absent', isEmpty=False, isSpoken=False, isHeard=False, isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
        
 
        # NAME with NAME2
        
        print('\n NAME current Entering {}',format(CommunicationTestCase.NAME))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=robotType,
                                                  data=CommunicationTestCase.VOICEDATA3)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=robotType)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME,
                                                  score=CommunicationTestCase.SCORE_1,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)
        
        # make entering item and process
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME,
                                                  score=CommunicationTestCase.SCORE_1,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should be 2')

        #process                      
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        #self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty, when entering')
        self.expect(name='Present Name 2, Conversation continues', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)
        
        print('\n NAME2 current Entering {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=robotType,
                                                  data=CommunicationTestCase.VOICEDATA4)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=robotType)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME2,
                                                  score=CommunicationTestCase.SCORE_2,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 3, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item Sensation should NAME2 be 3')

        # make entering and process
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_2,
                                                 presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 3, 'len(self.communication.getMemory().getAllPresentItemSensations() after Entering Item NAME2 Sensation should NAME2 be 3')

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.expect(name='Entering Name 2, change in presentation',  isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)
        
        print('\n NAME2 current Present {}'.format(CommunicationTestCase.NAME2))
        # added make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=robotType,
                                                  data=CommunicationTestCase.VOICEDATA4)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=robotType)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME2,
                                                  score=CommunicationTestCase.SCORE_2,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # TODO We find response
        # TODO if we find voice we speak, but now all voices are used. at this point
        # There has not been changes of present items and we have conversation on, but we have not send response
        # so we don't get response at this point
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 3, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 3')
        self.expect(name='Present Name 2, change in presentation',  isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)

        print('\n NAME2 current Present again {}'.format(CommunicationTestCase.NAME2))
        # make potential response
        voice_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Voice,
                                                  robotType=robotType,
                                                  data=CommunicationTestCase.VOICEDATA4)
        #self.SensationDirectory.append((voice_sensation.getDataId(),'voice_sensation'))
        self.addToSensationDirectory(name='voice_sensation', dataId=voice_sensation.getDataId(), id=voice_sensation.getId())
        self.printSensationNameById(note='voice_sensation test', dataId=voice_sensation.getDataId())
        image_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Sensory,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=robotType)
        #self.SensationDirectory.append((image_sensation.getDataId(),'image_sensation'))
        self.addToSensationDirectory(name='image_sensation', dataId=image_sensation.getDataId(), id=image_sensation.getId())
        self.printSensationNameById(note='image_sensation test', dataId=image_sensation.getDataId())
        item_sensation = self.communication.createSensation(time=self.history_sensationTime,
                                                  memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Item,
                                                  robotType=Sensation.RobotType.Sense,
                                                  name=CommunicationTestCase.NAME2,
                                                  score=CommunicationTestCase.SCORE_2,
                                                  presence=Sensation.Presence.Entering)
        #self.SensationDirectory.append((item_sensation.getDataId(),'item_sensation'))
        self.addToSensationDirectory(name='item_sensation', dataId=item_sensation.getDataId(), id=item_sensation.getId())
        self.printSensationNameById(note='item_sensation test', dataId=item_sensation.getDataId())
        item_sensation.associate(sensation=voice_sensation)
        item_sensation.associate(sensation=image_sensation)
        voice_sensation.associate(sensation=image_sensation)

        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
       #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # There has not been changes of present items and we have conversation on, but we have not send response
        # so we don't get response at this point
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 3, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 3')
        # TODO Next commented test should be valid Why this?
        #self.expect(name='Present NAME2 again basic change in presentation', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
        self.expect(name='Present NAME2 again basic change in presentation', isEmpty=False, isSpoken=True, isHeard=False, isVoiceFeeling=False, isImageFeeling=False,
                    voice=voice_sensation, image=image_sensation)
        
        print('\n NAME2 current Absent {}'.format(CommunicationTestCase.NAME2))
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME2,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
       
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence

        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        self.expect(name='Absent NAME2', isEmpty=False, isSpoken=False, isHeard=False, isVoiceFeeling=True, isImageFeeling=True, isNegativeFeeling=True)
    

        # last item.name will we be absent
        print('\n NAME current Absent {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Absent)
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
       #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
       
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sensation)
#         sleepTime = Communication.COMMUNICATION_INTERVAL+ 5.0
#         print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
#         systemTime.sleep(sleepTime)

        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.expect(name='Absent NAME', isEmpty=True, isSpoken=False, isHeard=False, isVoiceFeeling=False)
       

    '''
    Test and simulate Communication.process logic
    TODO This test is disabled, because we don't need if this is needed
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
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        allPresentItemSensations = self.communication.getMemory().getAllPresentItemSensations()
        self.assertEqual(len(allPresentItemSensations), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.assertEqual(allPresentItemSensations[0], Wall_E_item_sensation, 'allPresentItemSensations[0] should be Wall_E_item_sensation')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
        
        print('self.do_test_SimulateProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
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
        print('\ndo_test_SimulateProcessItemVoice 1')
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
        #self.SensationDirectory.append((Wall_E_voice_sensation_1.getDataId(),'Wall_E_voice_sensation_1'))
        self.addToSensationDirectory(name='Wall_E_voice_sensation_1', dataId=Wall_E_voice_sensation_1.getDataId(), id=Wall_E_voice_sensation_1.getId())
        self.printSensationNameById(note='Wall_E_voice_sensation_1 test', dataId=Wall_E_voice_sensation_1.getDataId())
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
        #self.SensationDirectory.append((Wall_E_voice_sensation_2.getDataId(),'Wall_E_voice_sensation_2'))
        self.addToSensationDirectory(name='Wall_E_voice_sensation_2', dataId=Wall_E_voice_sensation_2.getDataId(), id=Wall_E_voice_sensation_2.getId())
        self.printSensationNameById(note='Wall_E_voice_sensation_2 test', dataId=Wall_E_voice_sensation_2.getDataId())
        
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
        #self.SensationDirectory.append((Wall_E_voice_sensation_3.getDataId(),'Wall_E_voice_sensation_3'))
        self.addToSensationDirectory(name='Wall_E_voice_sensation_3', dataId=Wall_E_voice_sensation_3.getDataId(), id=Wall_E_voice_sensation_3.getId())
        self.printSensationNameById(note='Wall_E_voice_sensation_3 test', dataId=Wall_E_voice_sensation_3.getDataId())
        
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
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_image_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
        #self.SensationDirectory.append((Wall_E_image_sensation.getDataId(),'Wall_E_image_sensation'))
        self.addToSensationDirectory(name='Wall_E_image_sensation', dataId=Wall_E_image_sensation.getDataId(), id=Wall_E_image_sensation.getId())
        self.printSensationNameById(note='Wall_E_image_sensation test', dataId=Wall_E_image_sensation.getDataId())
        
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

         #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')

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
        #self.SensationDirectory.append((Wall_E_voice_response_sensation.getDataId(),'Wall_E_voice_response_sensation'))
        self.addToSensationDirectory(name='Wall_E_voice_response_sensation', dataId=Wall_E_voice_response_sensation.getDataId(), id=Wall_E_voice_response_sensation.getId())
        self.printSensationNameById(note='Wall_E_voice_response_sensation test', dataId=Wall_E_voice_response_sensation.getDataId())
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
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
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
        #self.SensationDirectory.append((Wall_E_voice_response_sensation.getDataId(),'Wall_E_voice_response_sensation'))
        self.addToSensationDirectory(name='Wall_E_voice_response_sensation', dataId=Wall_E_voice_response_sensation.getDataId(), id=Wall_E_voice_response_sensation.getId())
        self.printSensationNameById(note='Wall_E_voice_response_sensation test', dataId=Wall_E_voice_response_sensation.getDataId())
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
        
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
        # process
        self.simulateCommunicationProcess(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_voice_response_sensation)

        # should get Voice and a Feeling between Voice and Item
       #self.expect(name='response', isEmpty=False, isSpoken=True, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        # But voice is still 1. best voice, why
        self.expect(name='response, second best voice', isEmpty=False, isSpoken=True, voice=Wall_E_voice_sensation_3, isHeard=False,  isVoiceFeeling=True, isPositiveFeeling=True)
        

        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
#         sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
#         print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
#         systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")       
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='NO response', isEmpty=False, isSpoken=False, isHeard=False,  isVoiceFeeling=True, isNegativeFeeling=True)
        # no communicationItems should be left in 
        #self.assertEqual(len(self.communication.communicationItems),0, 'no communicationItems should be left in Communication ')
        print("test continues, should have got Feeling from stopWaitingResponse")
        

        
    
    '''
    depreated
    
    1) item.name MemoryType.Working Presence.Present
    2) process(item) should get old self.Wall_E_voice_sensation, that will be
       spoken out
    3) parent Axon should get self.Wall_E_voice_sensation
    4) parent Axon should get Sensation.SensationType.Feeling
    '''

    def re_test_2_ProcessItemPresent(self):
        print('\ntest_2_ProcessItemPresent')
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        Wall_E_item_sensation = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 score=CommunicationTestCase.SCORE_1,
                                                 presence=Sensation.Presence.Present)
        #self.SensationDirectory.append((self.Wall_E_item_sensation.getDataId(), 'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        allPresentItemSensations = self.communication.getMemory().getAllPresentItemSensations()
        self.assertEqual(len(allPresentItemSensations), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 1')
        self.assertEqual(allPresentItemSensations[0], Wall_E_item_sensation, 'allPresentItemSensations[0] should be Wall_E_item_sensation')
        self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty before testing')
        
        print('self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)')
        self.do_test_ProcessItemVoice(memoryType=Sensation.MemoryType.Working)
                                      
        #TODO What we get as response depend that we have run before, meaning that when we run test
        # self.do_test_ProcessItemVoice it puts responces to menory that self.do_test_ProcessItemVoiceFromOtherRobot can use
        # so if we don't run previous test, then latter test will fail even if code to test is OK
        print('\nself.do_test_ProcessItemVoiceFromOtherRobot(memoryType=Sensation.MemoryType.Working)\n')
        self.do_test_ProcessItemVoiceFromOtherRobot(memoryType=Sensation.MemoryType.Working)

        
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
    deprecated
    
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

    def do_test_ProcessItemVoice(self, memoryType):
        print('\ndo_test_ProcessItemVoice 1')
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
 
        # Make Voice to the history by parameter Memory type       
        # simulate Association has connected an voice to Item and Image 
        # Voice is in Sensory Memory, it is not used in Communication yet or
        # it can be in n LongTerm memoryType, classified to be a good Voice
        # Make two test of these 
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        #self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
 
        # response # 1
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_sensation_1 = self.communication.createSensation(time=history_sensationTime,
                                                    memoryType=memoryType,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,                                                   
                                                    data=CommunicationTestCase.VOICEDATA5)
        #self.SensationDirectory.append((Wall_E_voice_sensation_1.getDataId(),'Wall_E_voice_sensation_1'))
        self.addToSensationDirectory(name='Wall_E_voice_sensation_1', dataId=Wall_E_voice_sensation_1.getDataId(), id=Wall_E_voice_sensation_1.getId())
        self.printSensationNameById(note='Wall_E_voice_sensation_1 test', dataId=Wall_E_voice_sensation_1.getDataId())
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
         
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 0) # this is sometimes 1, sometimes 0
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len) # same
         
        #Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation)
                                                                      
        #self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)# sometime 1, sometimes 2
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        #self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
         
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
        #self.SensationDirectory.append((Wall_E_voice_sensation_2.getDataId(),'Wall_E_voice_sensation_2'))
        self.addToSensationDirectory(name='Wall_E_voice_sensation_2', dataId=Wall_E_voice_sensation_2.getDataId(), id=Wall_E_voice_sensation_2.getId())
        self.printSensationNameById(note='Wall_E_voice_sensation_2 test', dataId=Wall_E_voice_sensation_2.getDataId())
         
        #Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 1) # sometimes 1. sometimes 2
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        #self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
         
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
        #self.SensationDirectory.append((Wall_E_voice_sensation_3.getDataId(),'Wall_E_voice_sensation_3'))
        self.addToSensationDirectory(name='Wall_E_voice_sensation_3', dataId=Wall_E_voice_sensation_3.getDataId(), id=Wall_E_voice_sensation_3.getId())
        self.printSensationNameById(note='Wall_E_voice_sensation_3 test', dataId=Wall_E_voice_sensation_3.getDataId())
         
        #Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 1)# sometimes 1, sometimes 2
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        #self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
         
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
        #self.SensationDirectory.append((Wall_E_item_sensation.getDataId(),'Wall_E_item_sensation'))
        self.addToSensationDirectory(name='Wall_E_item_sensation', dataId=Wall_E_item_sensation.getDataId(), id=Wall_E_item_sensation.getId())
        self.printSensationNameById(note='Wall_E_item_sensation test', dataId=Wall_E_item_sensation.getDataId())
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_image_sensation_1 = self.communication.createSensation(memoryType=Sensation.MemoryType.Working,
                                                  sensationType=Sensation.SensationType.Image,
                                                  robotType=Sensation.RobotType.Sense)
         
        #self.SensationDirectory.append((Wall_E_image_sensation_1.getDataId(),'Wall_E_image_sensation_1'))
        self.addToSensationDirectory(name='Wall_E_image_sensation_1', dataId=Wall_E_image_sensation_1.getDataId(), id=Wall_E_image_sensation_1.getId())
        self.printSensationNameById(note='Wall_E_image_sensation_1 test', dataId=Wall_E_image_sensation_1.getDataId())
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
 
         #simulate TensorFlowClassification send presence item to MainRobot
        #self.communication.tracePresents(Wall_E_item_sensation) # presence
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
 
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
        #self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
         
        # now we respond
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_voice_response_sensation = self.communication.createSensation(#Stime=history_sensationTime,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=Sensation.RobotType.Sense,
                                                    data=CommunicationTestCase.VOICEDATA8)
        #self.SensationDirectory.append((Wall_E_voice_response_sensation.getDataId(),'Wall_E_voice_response_sensation'))
        self.addToSensationDirectory(name='Wall_E_voice_response_sensation', dataId=Wall_E_voice_response_sensation.getDataId(), id=Wall_E_voice_response_sensation.getId())
        self.printSensationNameById(note='Wall_E_voice_response_sensation test', dataId=Wall_E_voice_response_sensation.getDataId())
        # To be sure to get a new response, no this will be too new
        #Wall_E_voice_response_sensation.setTime(systemTime.time())
        
        #Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_image_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 2)#1
        #self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
        #self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
         
        Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_item_sensation)
        #self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 3)#2
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
         
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 1, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
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
        #self.assertEqual(self.communication.saidSensations[2], self.Wall_E_image_sensation.getDataId(), 'self.communication.saidSensations[2] should have Wall_E_image_sensation_1.getDataId()')
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
        #self.SensationDirectory.append((Wall_E_voice_response_sensation_2.getDataId(),'Wall_E_voice_response_sensation_2'))
        self.addToSensationDirectory(name='Wall_E_voice_response_sensation_2', dataId=Wall_E_voice_response_sensation_2.getDataId(), id=Wall_E_voice_response_sensation_2.getId())
        self.printSensationNameById(note='Wall_E_voice_response_sensation_2 test', dataId=Wall_E_voice_response_sensation_2.getDataId())
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
         
        self.assertEqual(len(self.communication.getMemory().getAllPresentItemSensations()), 2, 'len(self.communication.getMemory().getAllPresentItemSensations() should be 2')
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
        #self.SensationDirectory.append((Wall_E_voice_response_sensation_3.getDataId(),'Wall_E_voice_response_sensation_3'))
        self.addToSensationDirectory(name='Wall_E_voice_response_sensation_3', dataId=Wall_E_voice_response_sensation_3.getDataId(), id=Wall_E_voice_response_sensation_3.getId())
        self.printSensationNameById(note='Wall_E_voice_response_sensation_3 test', dataId=Wall_E_voice_response_sensation_3.getDataId())
        
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
        #self.SensationDirectory.append((Wall_E_voice_response_sensation_4.getDataId(),'Wall_E_voice_response_sensation_4'))
        self.addToSensationDirectory(name='Wall_E_voice_response_sensation_4', dataId=Wall_E_voice_response_sensation_4.getDataId(), id=Wall_E_voice_response_sensation_4.getId())
        self.printSensationNameById(note='Wall_E_voice_response_sensation_4 test', dataId=Wall_E_voice_response_sensation_4.getDataId())
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
        
    def test_ProcessItemImageVoiceFromOtherRobot(self):
        #resposes
        # - come from mainNames=self.OTHERMAINNAMES
        # - are send to Playback robotType=Sensation.RobotType.Muscle
        # - are marked as robotType=Sensation.RobotType.Muscle
        #
        # but Communucation should handle these renposes as person said,
        # Mictophone detects as Sense type Voices in same mainNames
        print('\ntest_ProcessItemImageVoiceFromOtherRobot\n')
        self.do_test_ProcessItemImageVoice(mainNames=self.OTHERMAINNAMES,
                                           robotType=Sensation.RobotType.Muscle,
                                           isCommunication=True)
        
        
    def test_ProcessItemImageVoiceFromSameRobotSenses(self):
        #resposes
        # - come from mainNames=self.OTHERMAINNAMES
        # - are send to Playback robotType=Sensation.RobotType.Muscle
        # - are marked as robotType=Sensation.RobotType.Muscle
        #
        # but Communucation should handle these renposes as person said,
        # Mictophone detects as Sense type Voices in same mainNames
        print('\ntest_ProcessItemImageVoiceFromSameRobotSenses\n')
        self.do_test_ProcessItemImageVoice(mainNames=self.MAINNAMES,
                                           robotType=Sensation.RobotType.Sense,
                                           isCommunication=False)
        
    '''
    do_test_ProcessItemImageVoice is helper metod to test main functionality
    of Communication-Robot.
    
    It takes three parameters that define other part Communication is
    communicating. With thse parameters we can define person or other Robot.
    - mainNames
    - robotType
    - isCommunication
    
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
       that are our first responses, because Communication logic allowes
       to use heartd responses from other part od communication, if they are
       not lat ones.
    6) If this was not not first response, se will get also positive Feeling
       sensations tp previous used voices and Images, because tho previous
       ones got responses.
       
    7) Finally Communication has used its Memory responses and can't use
       other part heard responses any morfe, because they are too new
       so we get negative feeling Feeking to Cpommunication last response.

    We test also that Communication send Item.presnce/Absent when its methods
    initRobot/deInitRobot is colled.
    
    This test does not test Communocation as process, so all methods from
    Communication should be called directly.

    
    ''' 
        
    def do_test_ProcessItemImageVoice(self, mainNames, robotType, isCommunication):#, memoryType):
        print('\ndo_test_ProcessItemImageVoice\n')
        
        ########################################################################################################
        # Prepare part
        
        memoryType=Sensation.MemoryType.Working
        
        history_sensationTime = systemTime.time() -2*max(CommunicationTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
        self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
        
        print('\n current Present {}'.format(CommunicationTestCase.NAME))
        # Now we should have 1 item in self.getMemory().getAllPresentItemSensations() (can be assigned as self.association) with with  name and associations count
        Wall_E_item_sensation = self.createSensation(robot=self.communication,
                                                     sensationName= 'Wall_E_item_sensation',
                                                     memoryType=Sensation.MemoryType.Working,
                                                     sensationType=Sensation.SensationType.Item,
                                                     robotType=Sensation.RobotType.Sense,
                                                     name=CommunicationTestCase.NAME,
                                                     score=CommunicationTestCase.SCORE_1,
                                                     presence=Sensation.Presence.Present)

        allPresentItemSensations = self.communication.getMemory().getAllPresentItemSensations()
        self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
        
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
                                                    feeling = CommunicationTestCase.BETTER_FEELING)
        
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
                                                    feeling = CommunicationTestCase.BETTER_FEELING)
                
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
                                                    feeling = CommunicationTestCase.BEST_FEELING)
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
                                                    feeling = CommunicationTestCase.BEST_FEELING)

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
                                                    feeling = CommunicationTestCase.NORMAL_FEELING)

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
                                                    feeling = CommunicationTestCase.NORMAL_FEELING)
        
        
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
                                                    feeling = CommunicationTestCase.NEUTRAL_FEELING)
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
                                                    feeling = CommunicationTestCase.NEUTRAL_FEELING)
        


        ########################################################################################################
        ## test part
        # simulate that we have started Comminucation-Roibot and all Robots get Item-sensation that it is present
        
        self.communication.initRobot()
        self.expect(name='initRobot', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=None,
                    image=None,
                    isVoiceFeeling=False,
                    isImageFeeling=False,
                    isItem=True)
                
        #image and Item from Sense, which has other MainNames
        # simulate item and image are connected each other with TensorflowClassifivation
        #systemTime.sleep(0.1)  # wait to get really even id
        Wall_E_item_sense_sensation = self.createSensation(
                                                 sensationName='Wall_E_item_sense_sensation',
                                                 robot=self.communication,
                                                 memoryType=Sensation.MemoryType.Working,
                                                 sensationType=Sensation.SensationType.Item,
                                                 robotType=robotType,#Sensation.RobotType.Sense,
                                                 name=CommunicationTestCase.NAME,
                                                 associations=[],
                                                 presence=Sensation.Presence.Present,
                                                 locations=self.getLocations(),
                                                 isCommunication=isCommunication,
                                                 mainNames=mainNames)

        self.logCommunicationState(note='before process Starting conversation, get best voice and image')
        #Item is Present, process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_item_sense_sensation)
        # should get just best Voice and Image
        self.expect(name='Starting conversation, get best voice and image', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_voice_sensation_2, isExactVoice=True,
                    image=Wall_E_image_sensation_2, isExactImage=True,
                    isVoiceFeeling=False,
                    isImageFeeling=False)
        
        
        # now other conversation part Robot or person responds with voice
        Wall_E_sense_voice_response_sensation = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA8,
                                                    locations=self.getLocations(),
                                                    isCommunication=isCommunication,
                                                    mainNames=mainNames)
       
        Wall_E_sense_voice_response_sensation.associate(sensation=Wall_E_item_sense_sensation)
        self.logCommunicationState(note='before process response, second best voice')
        # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation)
        # should get second best voice, image and positive feelins to 1. responses
        self.expect(name='response, second best voice, image', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_voice_sensation_1, isExactVoice=True,
                    image=Wall_E_image_sensation_1, isExactImage=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        
        # 2. responce from other side communication
        Wall_E_sense_voice_response_sensation_2 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_2',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    isCommunication=isCommunication,
                                                    mainNames=mainNames)
        self.logCommunicationState(note='before process response, third best voice, image')
        # process, should get third best voice, image and positive feelings to previous responses   
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_2)
        self.expect(name='response, third best voice, image', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_voice_sensation_3, isExactVoice=True,
                    image=Wall_E_image_sensation_3, isExactImage=True,
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
                                                    isCommunication=isCommunication,
                                                    mainNames=mainNames)
        self.logCommunicationState(note='before process response, old responsed voice, response furth bestimage')
        # process, should get fourth best image, voice and positive feelings to previous responses
        # at this point Wall_E_sense_voice_response_sensation is better than Wall_E_image_sensation_4
        # because Wall_E_image_sensation_4 feeling was low
        # We get also positive feeling to revious responses.
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_3)
        self.expect(name='response, response voice, fourth best image, voice', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=Wall_E_sense_voice_response_sensation, isExactVoice=True,
                    image=Wall_E_image_sensation_4, isExactImage=True,
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)
        

        # response 4 from other side communication
        Wall_E_sense_voice_response_sensation_4 = self.createSensation(
                                                    sensationName='Wall_E_sense_voice_response_sensation_4',
                                                    robot=self.communication,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    sensationType=Sensation.SensationType.Voice,
                                                    robotType=robotType,
                                                    data=CommunicationTestCase.VOICEDATA9,
                                                    locations=self.getLocations(),
                                                    isCommunication=isCommunication,
                                                    mainNames=mainNames)
        
        self.logCommunicationState(note='before process response, Wall_E_sense_voice_response_sensation, no image')
         # process
        self.communication.process(transferDirection=Sensation.TransferDirection.Down, sensation=Wall_E_sense_voice_response_sensation_4)
        # at this point Communication has used all sensations in the memory but
        # it can use responses: Wall_E_sense_voice_response_sensation_2
        # This side has not responded with images, so we should not get image.
        # should get Voice and a Feeling between Voice and Item
        # Voice should be already spoken Voice, but not last one, so it would be Wall_E_sense_voice_response_sensation_2, which is dropped fron heard voices
        # We get also positive feeling to revious responses.
        self.expect(name='response, Wall_E_sense_voice_response_sensation, no image', isEmpty=False, isSpoken=True, isHeard=False,  
                    voice=Wall_E_sense_voice_response_sensation_2, isExactVoice=True,
                    image=None, 
                    isVoiceFeeling=True,
                    isImageFeeling=True,
                    isPositiveFeeling=True)

        #  end
 
        
        # we don't response any more, so Communication.stopWaitingResponse
        # should be run and self.communication.communicationItems) should be empty
        # wait some time
        sleepTime = Communication.COMMUNICATION_INTERVAL+ 1.0
        print("test is sleeping " + str(sleepTime) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human communication then, so change it back)")       
        systemTime.sleep(sleepTime)
        print("Now stopWaitingResponse should be happened and we test it")       
        # should get Voice Feeling between Voice and Item
        # BUT is hard t0 test, just log
        self.expect(name='NO response, got Negative voice feelings', isEmpty=False, isSpoken=False, isHeard=False,
                    voice=None, image=None,
                    isVoiceFeeling=True, isImageFeeling=False, isNegativeFeeling=True)
        
 
        # simulate that we have stopped Comminucation-Roibot and all Robots get Item-sensation that it is absent
        self.communication.deInitRobot()
        self.expect(name='deInitRobot', isEmpty=False, isSpoken=True, isHeard=False,
                    voice=None,
                    image=None,
                    isVoiceFeeling=False,
                    isImageFeeling=False,
                    isItem=True)

       
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
               isVoiceFeeling, voice=None,isExactVoice=False,
               isImageFeeling=False, image=None, isExactImage=False,
               isPositiveFeeling=False, isNegativeFeeling=False,
               isItem=False,
               isWait=False):
        print("\nexpect {}".format(name))
        gotVoice = None
        gotImage = None
        errortext = '{}: Axon empty should not be {}'.format(name, str(self.getAxon().empty()))
        if isWait and not isEmpty: 
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
            isExactVoiceStillExpected = isExactVoice
            isSpokenImageStillExpected = isSpoken
            isHeardImageStillExpected = isHeard
            isExactImageStillExpected = isExactImage
            isItemStillExpected = isItem
            isSpokenItemStillExpected = isItem and isSpoken
            isHeardItemStillExpected = isItem and isHeard
            if voice is not None:
                isVoiceStillExpected = True
            else:
                isVoiceStillExpected = False
                isExactVoiceStillExpected = False
                isSpokenVoiceStillExpected = False
                isHeardVoiceStillExpected = False
            if image is not None:
                isImageStillExpected = True
            else:
                isImageStillExpected = False
                isExactImageStillExpected = False
                isSpokenImageStillExpected = False
                isHeardImageStillExpected = False
            isVoiceFeelingStillExpected = isVoiceFeeling
            isImageFeelingStillExpected = isImageFeeling
            while(not self.getAxon().empty()):
                tranferDirection, sensation = self.getAxon().get()
                self.getSensationNameByDataId(dataId=sensation.getDataId(), note="expect {} got".format(name))
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    gotVoice=sensation
                    isVoiceStillExpected = False
                    if isExactVoiceStillExpected:
                        isExactVoiceStillExpected = (sensation.getDataId() != voice.getDataId())
                    else:
                        if sensation.getDataId() == voice.getDataId():
                            print("isExactVoice was not expected, but got it!")
                        else:
                            self.getSensationNameByDataId(sensation, "isExactVoice was not expected, and did got it, but")
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
                    gotImage = sensation
                    isImageStillExpected = False
                    if isExactImageStillExpected:
                        isExactImageStillExpected = (sensation.getDataId() != image.getDataId())
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
                elif sensation.getSensationType() == Sensation.SensationType.Item:
                    gotItem = sensation
                    isItemStillExpected = False
                    if isSpokenItemStillExpected:
                        if sensation.getRobotType(robotMainNames=self.getMainNames()) == Sensation.RobotType.Muscle:
                            isSpokenItemStillExpected = False # got it
                    elif isHeardItemStillExpected:
                        if sensation.getRobotType(robotMainNames=self.getMainNames()) == Sensation.RobotType.Sense:
                            isHeardItemStillExpected = False # got it
                    else: # got something unexpected Image
                        errortext = '{}: Got unexpected Item, duplicate {}'.format(name, isSpoken or isHeard)
                        self.assertTrue(False, errortext)
                  
            # check that we got all
            self.assertFalse(isSpokenVoiceStillExpected, 'Did not get expected voice to be Spoken')                   
            self.assertFalse(isHeardVoiceStillExpected,  'Did not get expected voice to be Heard')                   
            self.assertFalse(isVoiceStillExpected,  'Did not get voice')
            if gotVoice != None and voice != None:                   
                self.assertFalse(isExactVoiceStillExpected,  'Did not get expected voice {} but {}'.format(self.getSensationNameByDataId(note='', id=voice.getId()), self.getSensationNameByDataId(note='', dataId=gotVoice.getDataId())))                   
            self.assertFalse(isSpokenImageStillExpected, 'Did not get expected image to be Spoken')                   
            self.assertFalse(isHeardImageStillExpected,  'Did not get expected image to be Heard')                   
            self.assertFalse(isImageStillExpected,  'Did not get image')
            if gotImage != None and image != None:
                self.assertFalse(isExactImageStillExpected,  'Did not get expected image {} but {}'.format(self.getSensationNameByDataId(note='', id=image.getId()), self.getSensationNameByDataId(note='', dataId=gotImage.getDataId())))                  
            self.assertFalse(isVoiceFeelingStillExpected, 'Did not get voice feeling')                   
            self.assertFalse(isImageFeelingStillExpected, 'Did not get image feeling')                   
            self.assertFalse(isSpokenItemStillExpected, 'Did not get expected item to be Spoken')                   
            self.assertFalse(isHeardItemStillExpected,  'Did not get expected item to be Heard')                   
            self.assertFalse(isItemStillExpected,  'Did not get item')
                
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

 