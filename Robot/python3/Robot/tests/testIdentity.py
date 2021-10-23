'''
Created on 03.06.2020
Updated on 23.10.2021
@author: reijo.korhonen@gmail.com

test Robot.Identity class

Testing is complicated, because we must test Identity thread
and unittest goes to tearDown while we are in the middle of testing.
so we must set sleep in tearDown

python3 -m unittest tests/testidentity.py

from AlsaAudio import Settings as AudioSettings


'''
import time as systemTime
import os
import io
import shutil
import ntpath
import tempfile

import unittest
from Sensation import Sensation
from Robot import Robot, Identity
from Axon import Axon
from Memory import Memory
from Config import Config
from AlsaAudio import Settings as AudioSettings

from PIL import Image as PIL_Image


class IdentityTestCase(unittest.TestCase):
    TEST_TIME = 10
    TEST_STOP_TIME = 10

    MAINNAMES = ["IdentityTestCaseMainName"]
    IDENTITYS = 'Identitys'
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getParent(self):
        return None
    def getName(self):
        return "IdentityTestCase"
    def getName(self):
        #print('CommunicationTestCase getName')
        return "Wall-E"
    def getMainNames(self):
        return self.MAINNAMES
    def getLocation(self): 
        return 'testLocation'  
    def getExposures(self):
#        return ['Eva']
        return ['Eva','father','family']
    def log(self, logStr, logLevel=None):
        #print('CommunicationTestCase log')
        if hasattr(self, 'identity'):
            if self.identity:
                if logLevel == None:
                    logLevel = self.identity.LogLevel.Normal
                if logLevel <= self.identity.getLogLevel():
                     print(self.identity.getName() + ":" + str( self.identity.config.level) + ":" + Sensation.Modes[self.identity.mode] + ": " + logStr)
    
    '''
    route to test class
    '''
    def route(self, transferDirection, sensation):
        self.log(logLevel=self.identity.LogLevel.Normal, logStr='route: ' + sensation.toDebugStr())
        self.log(logLevel=self.identity.LogLevel.Detailed, logStr='route: '  + str(transferDirection) +  ' ' + sensation.toDebugStr())
        self.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)

    '''
    fake from Congig
    '''
    def getIdentityDirPath(self, name):
        return self.IDENTITYS +'/'+ name


    '''
    fake
    '''
    def createSensation(self,
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
                 robot = None,
#                 isCommunication=False,
                 mainNames = None,                 
                 locations =  None,
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


        
        return self.identity.createSensation(
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
#                 isCommunication=isCommunication,
                 mainNames=mainNames,
                 locations=locations,
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

    
    '''
    from Robot
    '''    
    
    def getIdentitySensations(self, name):
        imageSensations=[]
        voiceSensations=[]
        # faked this
        #identitypath = self.config.getIdentityDirPath(name)
        identitypath = self.getIdentityDirPath(name)
        self.log('Identitypath for {} is {}'.format(name, identitypath))
        for dirName, subdirList, fileList in os.walk(identitypath):
            self.log('Found directory: %s' % dirName)      
            image_file_names=[]
            voice_file_names=[]
            for fname in fileList:
                self.log('\t%s' % fname)
                if fname.endswith(Robot.IMAGE_FILENAME_TYPE):# or\
                    # png do not work yet
                    #fname.endswith(".png"):
                    image_file_names.append(fname)
                elif fname.endswith(Robot.VOICE_FILENAME_TYPE):
                    voice_file_names.append(fname)
            # images
            for fname in image_file_names:
                image_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join(tempfile.gettempdir(),fname)
                shutil.copyfile(image_path, sensation_filepath)
                image = PIL_Image.open(sensation_filepath)
                image.load()
                # imageSensation memoryType = Sensation.MemoryType.Sensory, because it is needed to process it later, but this can change in future, so maybe it can be given as parameter
                imageSensation = self.createSensation( sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,\
                                                       image=image)
                imageSensations.append(imageSensation)
            # voices
            for fname in voice_file_names:
                voice_path=os.path.join(dirName,fname)
                sensation_filepath = os.path.join(tempfile.gettempdir(),fname)
                shutil.copyfile(voice_path, sensation_filepath)
                with open(sensation_filepath, 'rb') as f:
                    data = f.read()
                            
                    # length must be AudioSettings.AUDIO_PERIOD_SIZE
                    remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                    if remainder != 0:
                        self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) + " correcting " )
                        len_zerobytes = AudioSettings.AUDIO_PERIOD_SIZE - remainder
                        ba = bytearray(data)
                        for i in range(len_zerobytes):
                            ba.append(0)
                        data = bytes(ba)
                        remainder = len(data) % AudioSettings.AUDIO_PERIOD_SIZE
                        if remainder != 0:
                            self.log("Did not succeed to fix!")
                            self.log(str(remainder) + " over periodic size " + str(AudioSettings.AUDIO_PERIOD_SIZE) )
                    # voiceSensation memoryType = Sensation.MemoryType.LongTerm, because we wan't to remember voice and it is not needed to process it later, but this can change in future, so maybe it can be given as parameter
                    voiceSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.LongTerm, robotType = Sensation.RobotType.Sense, data=data)
                    voiceSensations.append(voiceSensation)
                    
        return imageSensations, voiceSensations
    
    '''
    Testing    
    '''
    
    def setUp(self):
        
        self.isFirstSleep=True
        self.processTimeSum = 0.0
        self.processNumber = 0

        self.axon = Axon(robot=self)
        
        self.memory = Memory(robot = self,
                             maxRss = Config.MAXRSS_DEFAULT,
                             minAvailMem = Config.MINAVAILMEM_DEFAULT)

        self.identity = Identity(      mainRobot=self,
                                       parent=self,
                                       instanceName='identity',
                                       instanceType= Sensation.InstanceType.SubInstance,
                                       memory = self.memory,
                                       level=2)
        self.identity.SLEEPTIME = 5    # test faster
        self.identity.sleeptime = 5

        self.identity.CLASSIFICATION_TIME = 20
        Identity.CLASSIFICATION_TIME = 20
        
        self.identity.SLEEP_BETWEEN_VOICES = 1
        
        # TODO to properly test we should get self.imageSensations and self.voiceSensations
        # same way, than mainRobot gets them.
        self.imageSensations, self.voiceSensations = self.getIdentitySensations(name=self.getName())
#         self.imageSensations =   []
#         self.voiceSensations =   []


    def tearDown(self):
        if self.identity.isRunning():
            self.identity.stop()
            print('tearDown sleep ' + str(IdentityTestCase.TEST_STOP_TIME) + ' time for self.identity to stop')
            systemTime.sleep(IdentityTestCase.TEST_STOP_TIME)       # give Robot some time to stop

        del self.identity
        del self.axon
        
    def test_Identity(self):
        i=0
        self.identity.start()
        while self.identity.isRunning() and i < 100:
            print('test_Identification sleep ' + str(IdentityTestCase.TEST_TIME) + ' waiting while self.identity.isRunning() and {} < 100: sleep {}s'.format(i, IdentityTestCase.TEST_TIME))
            systemTime.sleep(IdentityTestCase.TEST_TIME)
            i=i+1

if __name__ == '__main__':
    unittest.main()

 
