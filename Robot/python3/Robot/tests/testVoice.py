'''
Created on 21.09.2020
Updated on 07.10.2020
@author: reijo.korhonen@gmail.com

test Microphone and SoundDevicePlaypack classes
python3 -m unittest tests/testoundDevice.py


'''
import time as systemTime
import os
import shutil
from PIL import Image as PIL_Image

import unittest
from Sensation import Sensation
from Robot import Robot
from Microphone.Microphone import Microphone
from Playback.Playback import Playback
from Axon import Axon
from AlsaAudio import Settings


class VoiceTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    TEST_RUNS=4
    TEST_TRIES=20
    SLEEP_TIME=3            # ?s when normal test
    SCORE= 0.1
    NAME='Wall-E'           # This should be real Robot name with real identity
                            # Voice sensations to play as test inout
    LOCATION='localhost'    # used to mic presense by location
    
    MAINNAMES = ["VoiceTestCaseMainName"]
    OTHERMAINNAMES = ["OTHER_VoiceTestCaseMainName"]
        
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getName(self):
        return VoiceTestCase.NAME
    def getMainNames(self):
        return self.mainNames
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
    def getParent(self):
        return None
    def log(self, logStr, logLevel=None):
        if logLevel == None:
            logLevel = self.microphone.LogLevel.Normal
        if logLevel <= self.microphone.getLogLevel():
             print(self.microphone.getName() + ":" + str( self.microphone.config.level) + ":" + Sensation.Modes[self.microphone.mode] + ": " + logStr)

    '''
    Testing    
    '''
    

    '''
    Testing    
    '''
    
    def setUp(self):
        self.mainNames = self.MAINNAMES
        self.axon = Axon(robot=self) # parent axon
        self.microphone = Microphone( mainRobot=self,
                                      parent=self,
                                      instanceName='Microphone',
                                      instanceType= Sensation.InstanceType.SubInstance,
                                      level=2)
        self.playback = Playback(     mainRobot=self,
                                      parent=self,
                                      instanceName='Playback',
                                      instanceType= Sensation.InstanceType.SubInstance,
                                      level=2)

        self.stopSensation = self.microphone.createSensation(memoryType=Sensation.MemoryType.Working,
                                            sensationType=Sensation.SensationType.Stop,
                                            robotType=Sensation.RobotType.Sense)

       # simulate item and image are connected each other with TensorflowClassifivation
        # Item is in LongTerm memoryType
        #systemTime.sleep(0.1)  # wait to get really even id
        self.Wall_E_item_sensation = self.microphone.createSensation(
                                                      memoryType=Sensation.MemoryType.Working,
                                                      sensationType=Sensation.SensationType.Item,
                                                      robotType=Sensation.RobotType.Sense,
                                                      name=VoiceTestCase.NAME,
                                                      score=VoiceTestCase.SCORE,
                                                      presence = Sensation.Presence.Present)
        # get identity for self.visual as MainRobot does it (for images only)        
        self.studyOwnIdentity(robot=self.playback)
        
        # presence
        self.microphone.getMemory()._presentItemSensations[VoiceTestCase.LOCATION] = {}        
        
        self.microphone.start()
        self.playback.start()
        

    def tearDown(self):
# TODO Re-enable stop       
        print("--- put stop-sensation for Microphone")
        self.microphone.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        print("--- put stop-sensation for Microphone")
        self.playback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=self.stopSensation)
        
        print("--- test sleeping " + str(VoiceTestCase.SLEEP_TIME) + " second until stop should be done")
        systemTime.sleep(VoiceTestCase.SLEEP_TIME) # let result UI be shown until cleared           

        self.microphone.stop()
        #self.assertEqual(self.microphone.getAxon().empty(), False, 'Axon should not be empty after self.microphone.stop()')
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get()
#             self.assertTrue(sensation.getSensationType() == Sensation.SensationType.Stop,
#                             'parent should get Stop sensation type after test and self.microphone.stop()')
        
        while self.microphone.running or self.playback.running:
            systemTime.sleep(VoiceTestCase.SLEEP_TIME)
         
        del self.stopSensation
        del self.Wall_E_item_sensation
        del self.microphone
        del self.playback
        del self.axon
        
    def getPlaybackTime(self, datalen=None):
        if datalen == None:
            datalen = self.last_datalen
            
        return float(datalen)/(float(Settings.AUDIO_RATE*Settings.AUDIO_CHANNELS))
    
    def test_2_SoundDevicePlayback(self):
#         print("--- test_1_SoundDevicePlayback start")
#         self.playback.start()

        self.assertEqual(self.playback.getAxon().empty(), True, 'self.playback Axon should be empty at the beginning of test_Visual\nCannot test properly this!')

        print("--- Playback identity voice Normal")
        for sensation in self.playback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = self.playback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData(),
                                                                  kind = Sensation.Kind.Normal)
            
            
            print("--- Playback identity voice Normal")
            self.do_SoundDevicePlayback(playBackSensation=playBackSensation)
            
        print("--- Playback identity voice Wall-E")
        for sensation in self.playback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = self.playback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData(),
                                                                  kind = Sensation.Kind.WallE)
            
            
            print("--- Playback identity Voice Wall-E")
            self.do_SoundDevicePlayback(playBackSensation=playBackSensation)

        print("--- Playback identity voice Eva")
        for sensation in self.playback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = self.playback.createSensation(
                                                                  memoryType=Sensation.MemoryType.Sensory,
                                                                  sensationType=Sensation.SensationType.Voice,
                                                                  robotType=Sensation.RobotType.Muscle,
                                                                  data=sensation.getData(),
                                                                  kind = Sensation.Kind.Eva)
            
            
            print("--- Playback identity Voice Eva")
            self.do_SoundDevicePlayback(playBackSensation=playBackSensation)

        print("--- test_1_SoundDevicePlayback is done")
        
    
    def do_SoundDevicePlayback(self, playBackSensation):
        self.playback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
        
        playbackTime = 1.25 * self.getPlaybackTime(datalen=len(playBackSensation.getData()))
        print("--- test sleeping {} seconds until playback is done".format(playbackTime))
        systemTime.sleep(playbackTime)   

    def test_1_SoundDevices(self):
        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_2_SoundDevices\nCannot test properly this!')
        
        test_runs = 0
        test_tries=0
        hearingDisabled = True

        while test_runs < VoiceTestCase.TEST_RUNS and test_tries < VoiceTestCase.TEST_TRIES:
            # enable hearing, we claim that this one speaks
            print("\n\n--- test {} try {}\n".format(test_runs, test_tries))
            if hearingDisabled:
                print("\n\n--- test {} try {} Enable hearing\n".format(test_runs, test_tries))
                self.microphone.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()] = self.Wall_E_item_sensation          
                hearingDisabled = False
            while self.getAxon().empty() and test_runs < VoiceTestCase.TEST_RUNS and test_tries < VoiceTestCase.TEST_TRIES:
                print("--- test sleeping {} seconds until we have got voice sensations, try {}".format(VoiceTestCase.SLEEP_TIME, test_tries))
                systemTime.sleep(VoiceTestCase.SLEEP_TIME) # let Microphone start before waiting it to stops
                test_tries = test_tries+1
                
            gotHeardVoice = False
            while(not self.getAxon().empty()):
                isHeardVoice = False
                tranferDirection, sensation = self.getAxon().get()
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if sensation.getRobotType() == Sensation.RobotType.Sense:
                        print("--- got Sensations, was heard voice")
                        if not gotHeardVoice:
                            test_runs=test_runs+1
                            gotHeardVoice = True  # got it
                        isHeardVoice = True
                        # TODO here we test speaking so we must disable hearing
                        if not hearingDisabled:                           
                            print("--- test {} disable hearing".format(test_runs))
                            del self.microphone.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()]
                            hearingDisabled = True
                                #sleep as long as sound playing will take
                        print("--- Playback heard voice test {} try {}".format(test_runs, test_tries))
                        playbackTime = 1.5 * self.getPlaybackTime(datalen=len(sensation.getData()))
                        playBackSensation = self.playback.createSensation(
                                                                memoryType=Sensation.MemoryType.Sensory,
                                                                sensationType=Sensation.SensationType.Voice,
                                                                robotType=Sensation.RobotType.Muscle,
                                                                data=sensation.getData(),
                                                                kind = Sensation.Kind.Normal)


                        self.playback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
                        print("--- test sleeping {} seconds until playback is done test {} try {} ".format(playbackTime, test_runs, test_tries))
                        systemTime.sleep(playbackTime) # let Microphone start before waiting it to stops
                if not isHeardVoice:
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
            robot.imageSensations, robot.voiceSensations = robot.getIdentitySensations(name=VoiceTestCase.NAME)
            self.assertTrue(len(robot.voiceSensations) > 0,
                            'should get Robot identity voices as test material')
            
            assert(len(robot.voiceSensations) > 0)
 
        
if __name__ == '__main__':
    unittest.main()

 