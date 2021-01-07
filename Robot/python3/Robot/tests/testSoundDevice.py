'''
Created on 09.01.2020
Updated on 09.10.2020
@author: reijo.korhonen@gmail.com

test SoundDeviceMicrophone and SoundDeviceOlaypack classes
python3 -m unittest tests/testoundDevice.py


'''
import time as systemTime
import os
import shutil
from PIL import Image as PIL_Image

import unittest
from Sensation import Sensation
from Robot import Robot
from SoundDeviceMicrophone.SoundDeviceMicrophone import SoundDeviceMicrophone
from SoundDevicePlayback.SoundDevicePlayback import SoundDevicePlayback
from Axon import Axon
from AlsaAudio import Settings


class SoundDeviceTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    TEST_RUNS=3
    #TEST_TIME=300 # 5 min, when debugging
    SLEEP_TIME=3             # ?s when normal test
    SCORE= 0.1
    NAME='Wall-E'           # This should be real Robot name with real identity
                            # Voice sensations to play as test inout
    LOCATION='localhost'    # used to mic presense by location
    MAINNAMES = ["SoundDeviceTestCaseMainName"]
   
    '''
    Robot modeling
    '''
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getName(self):
        return SoundDeviceTestCase.NAME
    def log(self, logStr, logLevel=None):
        if logLevel == None:
            logLevel = self.soundDeviceMicrophone.LogLevel.Normal
        if logLevel <= self.soundDeviceMicrophone.getLogLevel():
             print(self.soundDeviceMicrophone.getName() + ":" + str( self.soundDeviceMicrophone.config.level) + ":" + Sensation.Modes[self.soundDeviceMicrophone.mode] + ": " + logStr)
    def getMainNames(self):
        return self.MAINNAMES
    def getParent(self):
        return None

    '''
    Testing    
    '''
    

    '''
    Testing    
    '''
    
    def setUp(self):
        self.axon = Axon(robot=self) # parent axon
        self.soundDeviceMicrophone = SoundDeviceMicrophone(
                            mainRobot=self,
                            parent=self,
                            instanceName='SoundDeviceMicrophone',
                            instanceType= Sensation.InstanceType.SubInstance,
                            level=2)
        self.soundDevicePlayback = SoundDevicePlayback(
                            mainRobot=self,
                            parent=self,
                            instanceName='SoundDevicePlayback',
                            instanceType= Sensation.InstanceType.SubInstance,
                            level=2)

        self.stopSensation = self.soundDeviceMicrophone.createSensation(memoryType=Sensation.MemoryType.Working,
                                            sensationType=Sensation.SensationType.Stop,
                                            robotType=Sensation.RobotType.Sense)

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.soundDeviceMicrophone.createSensation(
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=SoundDeviceTestCase.NAME,
                                                      score=SoundDeviceTestCase.SCORE,
                                                      presence = Sensation.Presence.Present)
         # presence
        self.soundDeviceMicrophone.getMemory()._presentItemSensations[SoundDeviceTestCase.LOCATION] = {}        

        # get identity for self.visual as MainRobot does it (for images only)        
        self.studyOwnIdentity(robot=self.soundDevicePlayback)
        
        self.soundDeviceMicrophone.start()
        self.soundDevicePlayback.start()
        

    def tearDown(self):
# TODO Re-enable stop       
        print("--- put stop-sensation for SoundDeviceMicrophone")
        self.soundDeviceMicrophone.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        print("--- put stop-sensation for SoundDeviceMicrophone")
        self.soundDevicePlayback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        
        print("--- test sleeping " + str(SoundDeviceTestCase.SLEEP_TIME) + " second until stop should be done")
        systemTime.sleep(SoundDeviceTestCase.SLEEP_TIME) # let result UI be shown until cleared           

        #self.soundDeviceMicrophone.stop()
        #self.assertEqual(self.soundDeviceMicrophone.getAxon().empty(), False, 'Axon should not be empty after self.soundDeviceMicrophone.stop()')
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get()
#             self.assertTrue(sensation.getSensationType() == Sensation.SensationType.Stop,
#                             'parent should get Stop sensation type after test and self.soundDeviceMicrophone.stop()')
        
        while self.soundDeviceMicrophone.running or self.soundDevicePlayback.running:
            systemTime.sleep(SoundDeviceTestCase.SLEEP_TIME)
         
        del self.stopSensation
        del self.Wall_E_item_sensation
        del self.soundDeviceMicrophone
        del self.soundDevicePlayback
        del self.axon
        
    def getPlaybackTime(self, datalen=None):
        if datalen == None:
            datalen = self.last_datalen
            
        return float(datalen)/(float(Settings.AUDIO_RATE*Settings.AUDIO_CHANNELS))
    
    def re_test_1_SoundDevicePlayback(self):
#         print("--- test_1_SoundDevicePlayback start")
#         self.soundDevicePlayback.start()

        self.assertEqual(self.soundDevicePlayback.getAxon().empty(), True, 'self.soundDevicePlayback Axon should be empty at the beginning of test_Visual\nCannot test properly this!')

        print("--- Playback identity voice Normal")
        for sensation in self.soundDevicePlayback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = self.soundDevicePlayback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData(),
                                                                  kind = Sensation.Kind.Normal)
            
            
            print("--- Playback identity voice Normal")
            self.do_SoundDevicePlayback(playBackSensation=playBackSensation)
            
        print("--- Playback identity voice Wall-E")
        for sensation in self.soundDevicePlayback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = self.soundDevicePlayback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData(),
                                                                  kind = Sensation.Kind.WallE)
            
            
            print("--- Playback identity Voice Wall-E")
            self.do_SoundDevicePlayback(playBackSensation=playBackSensation)

        print("--- Playback identity voice Eva")
        for sensation in self.soundDevicePlayback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = self.soundDevicePlayback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData(),
                                                                  kind = Sensation.Kind.Eva)
            
            
            print("--- Playback identity Voice Eva")
            self.do_SoundDevicePlayback(playBackSensation=playBackSensation)

        print("--- test_1_SoundDevicePlayback is done")
        
    
    def do_SoundDevicePlayback(self, playBackSensation):
        self.soundDevicePlayback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
        
        playbackTime = 1.25 * self.getPlaybackTime(datalen=len(playBackSensation.getData()))
        print("--- test sleeping {} seconds until playback is done".format(playbackTime))
        systemTime.sleep(playbackTime)   

    def test_2_SoundDevices(self):
        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_2_SoundDevices\nCannot test properly this!')
        
        i = 0
        while i < SoundDeviceTestCase.TEST_RUNS:
            tries=0
            # enable hearing, we claim that this one speaks
            print("\n--- test {} enable hearing\n".format(i))
            self.soundDeviceMicrophone.getMemory()._presentItemSensations[SoundDeviceTestCase.LOCATION][self.Wall_E_item_sensation.getName()] = self.Wall_E_item_sensation          
            while self.getAxon().empty() and tries < 10:
                print("--- test sleeping {} seconds until we have got voice sensations, try {}".format(SoundDeviceTestCase.SLEEP_TIME, tries))
                systemTime.sleep(SoundDeviceTestCase.SLEEP_TIME) # let SoundDeviceMicrophone start before waiting it to stops
                tries = tries+1
                
            if tries < 10:
                gotHeardVoice = False
                hearingDisabled = False
                while(not self.getAxon().empty()):
                    tranferDirection, sensation = self.getAxon().get()
                    if sensation.getSensationType() == Sensation.SensationType.Voice:
                        if sensation.getRobotType() == Sensation.RobotType.Sense:
                            print("--- got Sensations, was heard voice")
                            gotHeardVoice = True  # got it
                            # TODO here we test speaking so we must disable hearing
                            if not hearingDisabled:                           
                                print("--- test {} disable hearing".format(i))
                                del self.soundDeviceMicrophone.getMemory()._presentItemSensations[SoundDeviceTestCase.LOCATION][self.Wall_E_item_sensation.getName()]
                                hearingDisabled = True
                                #sleep as long as sound playing will take
                            print("--- Playback heard voice")
                            playbackTime = 1.5 * self.getPlaybackTime(datalen=len(sensation.getData()))
                            playBackSensation = self.soundDevicePlayback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData())


                            self.soundDevicePlayback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
                            print("--- test sleeping {} seconds until playback is done".format(playbackTime))
                            systemTime.sleep(playbackTime) # let SoundDeviceMicrophone start before waiting it to stops
                            
                            
                    
                if gotHeardVoice:
                    i=i+1
                    tries=0                            
                else:
                    print("--- got Sensations, but no heard voice, test continues")
    
        
    '''
    functionality from Robot
    parameter
    robot any kind read Robot-class instance
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
                                                kind=robot.getKind())
        #if robot.isMainRobot() or robot.getInstanceType() == Sensation.InstanceType.Virtual:
        if True:
            # Fake we are Wall-E
            robot.imageSensations, robot.voiceSensations = robot.getIdentitySensations(name=SoundDeviceTestCase.NAME)
            self.assertTrue(len(robot.voiceSensations) > 0,
                            'should get Robot identity voices as test material')
            
            assert(len(robot.voiceSensations) > 0)
 
        
if __name__ == '__main__':
    unittest.main()

 