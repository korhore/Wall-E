'''
Created on 21.09.2020
Updated on 07.12.2021
@author: reijo.korhonen@gmail.com

test Microphone and Playpack classes
python3 -m unittest tests/testVoice.py


'''
import time as systemTime
import os
import shutil
from PIL import Image as PIL_Image

import unittest
from Sensation import Sensation
from Robot import Robot
from Axon import Axon
from AlsaAudio import Settings

#MICROPHONEPLAYBACK=False
MICROPHONEPLAYBACK=True
if MICROPHONEPLAYBACK:
    from Microphone.Microphone import Microphone
    from MicrophonePlayback.MicrophonePlayback import MicrophonePlayback
else:
    from Microphone.Microphone import Microphone
    from Playback.Playback import Playback



class VoiceTestCase(unittest.TestCase, Robot):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    TEST_RUNS=5
    TEST_TRIES=60
    INITIAL_SILECE_SLEEP_TIME=30   # WE should hear silence at the beginning of the test
    SLEEP_TIME=3            # ?s when normal test
    SCORE= 0.1
    NAME='Wall-E'           # This should be real Robot name with real identity
                            # Voice sensations to play as test inout
    LOCATION='localhost'    # used to mic presense by location
    LOCATIONS=[LOCATION]    # used to mic presense by location
    
    MAINNAMES = ["VoiceTestCaseMainName"]
    OTHERMAINNAMES = ["OTHER_VoiceTestCaseMainName"]
    
    VOIVEPLAYEDMAXWAITTIME = 1.5 *Microphone.VOIVELENGTHMAXIMUM
        
    '''
    Robot modeling
    '''
        
    '''
    Must fake is_alive to True, so we could test Sensation routing
    '''
    def is_alive(self):
            return True
   
#     def log(self, logStr, logLevel=None):
#         if logLevel == None:
#             logLevel = self.microphone.LogLevel.Normal
#         if logLevel <= self.microphone.getLogLevel():
#              print(self.microphone.getName() + ":" + str( self.microphone.config.level) + ":" + Sensation.Modes[self.microphone.mode] + ": " + logStr)

    '''
    return subrobots that have themselves have capabilities requires.
    Owner Robots are not mentioned
    This method is used in star routing
    '''   

    '''
    Helper methods   
    '''
    def setRobotLocations(self, robot, locations):
        robot.locations = locations
        robot.uplocations = locations
        robot.downlocations = locations    
 
    def setRobotMainNames(self, robot, mainNames):
        robot.mainNames = mainNames
    '''
    set capabilities  Item, Image, Voice
    '''
    def setRobotCapabilities(self, robot, robotTypes):
        capabilities  =  robot.getCapabilities()

        for robotType in Sensation.RobotTypesOrdered:
            is_set = robotType in robotTypes    
            #sensory
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.Voice, is_set=is_set)   
            capabilities.setCapability(robotType=robotType, memoryType=Sensation.MemoryType.Sensory, sensationType=Sensation.SensationType.RobotState, is_set=is_set)   

        robot.setCapabilities(capabilities)
    

    '''
    Testing    
    '''
    
    def setUp(self):
        Robot.__init__(self=self,
                       mainRobot=None,
                       parent=None,
                       instanceName='testVoice',
                       instanceType= Sensation.InstanceType.Real,
                       level=1)
        self.axon = Axon(robot=self)
        self.setRobotLocations(robot=self, locations=VoiceTestCase.LOCATIONS)
        self.setRobotMainNames(robot=self,mainNames=VoiceTestCase.MAINNAMES)        
        self.setRobotCapabilities(robot=self, robotTypes=[Sensation.RobotType.Sense])
        
        if MICROPHONEPLAYBACK:
            self.microphonePlayback = MicrophonePlayback( mainRobot=self,
                                      parent=self,
                                      instanceName='MicrophonePlayback',
                                      instanceType= Sensation.InstanceType.SubInstance,
                                      level=2)
            self.setRobotLocations(robot=self.microphonePlayback, locations=VoiceTestCase.LOCATIONS)
            self.setRobotMainNames(robot=self.microphonePlayback, mainNames=VoiceTestCase.MAINNAMES)        
            self.setRobotLocations(robot=self.microphonePlayback.microphone, locations=VoiceTestCase.LOCATIONS)
            self.setRobotMainNames(robot=self.microphonePlayback.microphone, mainNames=VoiceTestCase.MAINNAMES)        
            self.setRobotLocations(robot=self.microphonePlayback.playback, locations=VoiceTestCase.LOCATIONS)
            self.setRobotMainNames(robot=self.microphonePlayback.playback, mainNames=VoiceTestCase.MAINNAMES)        
            self.subInstances.append(self.microphonePlayback)

            self.stopSensation = self.microphonePlayback.createSensation(memoryType=Sensation.MemoryType.Working,
                                                sensationType=Sensation.SensationType.Stop,
                                                robotType=Sensation.RobotType.Sense)
    
           # simulate item and image are connected each other with TensorflowClassifivation
            # Item is in LongTerm memoryType
            #systemTime.sleep(0.1)  # wait to get really even id
            self.Wall_E_item_sensation = self.microphonePlayback.createSensation(
                                                          memoryType=Sensation.MemoryType.Working,
                                                          sensationType=Sensation.SensationType.Item,
                                                          robotType=Sensation.RobotType.Sense,
                                                          name=VoiceTestCase.NAME,
                                                          score=VoiceTestCase.SCORE,
                                                          presence = Sensation.Presence.Present)
            # get identity for self.visual as MainRobot does it (for images only)        
            self.studyOwnIdentity(robot=self.microphonePlayback)
            
            # presence
            self.microphonePlayback.getMemory()._presentItemSensations[VoiceTestCase.LOCATION] = {}        
            
            self.microphonePlayback.start()
        else:      
            self.microphone = Microphone( mainRobot=self,
                                          parent=self,
                                          instanceName='Microphone',
                                          instanceType= Sensation.InstanceType.SubInstance,
                                          level=2)
            self.setRobotLocations(robot=self.microphone, locations=VoiceTestCase.LOCATIONS)
            self.setRobotMainNames(robot=self.microphone, mainNames=VoiceTestCase.MAINNAMES)        
            self.subInstances.append(self.microphone)
            
            self.playback = Playback(     mainRobot=self,
                                          parent=self,
                                          instanceName='Playback',
                                          instanceType= Sensation.InstanceType.SubInstance,
                                          level=2)
            self.setRobotLocations(robot=self.playback, locations=VoiceTestCase.LOCATIONS)
            self.setRobotMainNames(robot=self.playback, mainNames=VoiceTestCase.MAINNAMES)        
            self.subInstances.append(self.playback)


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
        if MICROPHONEPLAYBACK:
            self.microphonePlayback.stop()
        else:
            self.microphone.stop()
            self.playback.stop()
        #self.assertEqual(self.microphone.getAxon().empty(), False, 'Axon should not be empty after self.microphone.stop()')
        while(not self.getAxon().empty()):
            transferDirection, sensation = self.getAxon().get(robot=self)
#             self.assertTrue(sensation.getSens6ationType() == Sensation.SensationType.Stop,
#                             'parent should get Stop sensation type after test and self.microphone.stop()')
        
        if MICROPHONEPLAYBACK:
            while self.microphonePlayback.running:
                systemTime.sleep(VoiceTestCase.SLEEP_TIME)
        else:
            while self.microphone.running or self.playback.running:
                systemTime.sleep(VoiceTestCase.SLEEP_TIME)
        # one sleep more
        systemTime.sleep(VoiceTestCase.SLEEP_TIME)
         
        del self.stopSensation
        del self.Wall_E_item_sensation
        if MICROPHONEPLAYBACK:
            del self.microphonePlayback
        else:
            del self.microphone
            del self.playback
        del self.axon
        
    def getPlaybackTime(self, datalen=None):
        if datalen == None:
            datalen = self.last_datalen
            
        return float(datalen)/(float(Settings.AUDIO_RATE*Settings.AUDIO_CHANNELS))
    
    def test_2_Playback(self):
        print("\n\n--- test_1_Playback")
        self.playBackSensations=[]
        self.playBackWait=0.0
        if MICROPHONEPLAYBACK:
            playback = self.microphonePlayback
        else:
            playback = self.playback


        self.assertEqual(playback.getAxon().empty(), True, 'playback Axon should be empty at the beginning of test_Visual\nCannot test properly this!')

        print("--- Playback identity voice Normal")
        for sensation in playback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = playback.createSensation(
                                                                      memoryType=Sensation.MemoryType.Sensory,
                                                                      sensationType=Sensation.SensationType.Voice,
                                                                      robotType=Sensation.RobotType.Muscle,
                                                                      data=sensation.getData(),
                                                                      kind = Sensation.Kind.Normal)
            
            
            print("--- Playback identity voice Normal")
            self.do_Playback(playback=playback, playBackSensation=playBackSensation)
            
        print("--- Playback identity voice Wall-E")
        for sensation in playback.voiceSensations:
            print("--- Playback identity voice ")
            # Normal voice
            playBackSensation = playback.createSensation(
                                                                      memoryType=Sensation.MemoryType.Sensory,
                                                                      sensationType=Sensation.SensationType.Voice,
                                                                      robotType=Sensation.RobotType.Muscle,
                                                                      data=sensation.getData(),
                                                                      kind = Sensation.Kind.WallE)
            
            
            print("--- Playback identity Voice Wall-E")
            self.do_Playback(playback=playback, playBackSensation=playBackSensation)

        print("--- Playback identity voice Eva")
        for sensation in playback.voiceSensations:
            print("--- Playback identity voice ")
            playBackSensation = playback.createSensation(
                                                                      memoryType=Sensation.MemoryType.Sensory,
                                                                      sensationType=Sensation.SensationType.Voice,
                                                                      robotType=Sensation.RobotType.Muscle,
                                                                      data=sensation.getData(),
                                                                      kind = Sensation.Kind.Eva)
                        
            print("--- Playback identity Voice Eva")
            self.do_Playback(playback=playback, playBackSensation=playBackSensation)
        self.wait_Playback()

        print("--- test_1_Playback is done")
        
    
    def do_Playback(self, playback, playBackSensation):
        playBackSensation.setTime(systemTime.time())
        self.playBackSensations.append(playBackSensation)
        playback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
        
        playbackTime = 1.25 * self.getPlaybackTime(datalen=len(playBackSensation.getData()))
        print("--- test waits {} seconds until this playback is done".format(playbackTime))
        #systemTime.sleep(playbackTime)
        self.playBackWait += playbackTime
        print("--- test waits {} seconds until this all playbacks are done".format(self.playBackWait))
        self.wait_Playback()
#         while not self.getAxon().empty():
#             tranferDirection, sensation = self.getAxon().get(robot=self)
#             if sensation.getSensationType() == Sensation.SensationType.RobotState:
#                 if sensation.getRobotType() == Sensation.RobotType.Sense:
#                     print("--- Sense RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
#                     if sensation.getRobotState() == Sensation.RobotState.CommunicationVoicePlayed:
#                         print("---1:Voice is played")
#                         for a in sensation.getAssociations():
#                             if a.getSensation() in self.playBackSensations:
#                                 self.playBackSensations.remove(a.getSensation())
#                                 print("---1:OUR Voice is played")
#                                 playbackTime = 1.25 * self.getPlaybackTime(datalen=len(a.getSensation().getData()))
#                                 self.playBackWait -= playbackTime

    def wait_Playback(self):
        timeToStart = systemTime.time()
        timeToEnd = systemTime.time() + self.playBackWait
        waited=0.0
        # Note if we have here 'or' test is more realistic for reality, but 'and' makes it testing throughput
        while self.playBackWait > 0 or len(self.playBackSensations) > 0:
#        while self.playBackWait > 0 and len(self.playBackSensations) > 0:
            if self.getAxon().empty():
                self.playBackWait -= 1.0
                systemTime.sleep(1.0)
                waited+=1.0
            else:
                tranferDirection, sensation = self.getAxon().get(robot=self)
                if sensation.getSensationType() == Sensation.SensationType.RobotState:
                    if sensation.getRobotType() == Sensation.RobotType.Sense:
                        print("--- Sense RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                        if sensation.getRobotState() == Sensation.RobotState.CommunicationVoicePlayed:
                            print("---Voice is played")
                            for a in sensation.getAssociations():
                                if a.getSensation() in self.playBackSensations:
                                    self.playBackSensations.remove(a.getSensation())
                                    print("---OUR Voice is played")
                                    playbackTime = 1.25 * self.getPlaybackTime(datalen=len(a.getSensation().getData()))
                                    self.playBackWait -= playbackTime
        self.playBackWait += waited
#         systemTime.sleep(timeToEnd - systemTime.time())
        print("--- wait_Playback playBackWait {} len(self.playBackSensations) {}".format(self.playBackWait, len(self.playBackSensations)))



    def re_test_1_Microphone(self):
        self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_1_Microphone\nCannot test properly this!')
        
        test_runs = 0
        test_tries=0
        hearingDisabled = True
        waitingRobotStateCommunicationVoicePlayed = False
        
        # At first Microphone should hear silence to set its voice levels
        if MICROPHONEPLAYBACK:
            self.microphonePlayback.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()] = self.Wall_E_item_sensation
        else:        
            self.microphone.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()] = self.Wall_E_item_sensation
        hearingDisabled = False
        print("\n\n--- test sleeping {} seconds to let Microphone hear silence level\n\n".format(VoiceTestCase.INITIAL_SILECE_SLEEP_TIME))
        systemTime.sleep(VoiceTestCase.INITIAL_SILECE_SLEEP_TIME) # let Microphone start before waiting it to stops
        print("--- There should not be anything in out Axon, but we clear it to be sure")
        while(not self.getAxon().empty()):
            isHeardVoice = False
            tranferDirection, sensation = self.getAxon().get(robot=self)
            if sensation.getSensationType() == Sensation.SensationType.Voice:
                if sensation.getRobotType() == Sensation.RobotType.Sense:
                    print("--- got Sense Voice {}s".format(self.getPlaybackTime(len(sensation.getData()))))
                else:
                    print("--- got Other Voice {}s".format(self.getPlaybackTime(len(sensation.getData()))))
            elif sensation.getSensationType() == Sensation.SensationType.RobotState:
                if sensation.getRobotType() == Sensation.RobotType.Sense:
                    print("--- got Sense RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                else:
                    print("--- got Other RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
            else:
                print("--- got Other Sensation")

        while test_runs < VoiceTestCase.TEST_RUNS and test_tries < VoiceTestCase.TEST_TRIES:
            # enable hearing, we claim that this one speaks
            print("\n\n\n--- test {} try {} SPEAK NOW\n".format(test_runs, test_tries))
            if hearingDisabled:
                print("\n\n--- test {} try {} Enable hearing, \n".format(test_runs, test_tries))
                if MICROPHONEPLAYBACK:
                    self.microphonePlayback.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()] = self.Wall_E_item_sensation          
                else:
                    self.microphone.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()] = self.Wall_E_item_sensation          
                hearingDisabled = False
            while self.getAxon().empty() and test_runs < VoiceTestCase.TEST_RUNS and test_tries < VoiceTestCase.TEST_TRIES:
                print("--- test sleeping {} seconds until we have got voice sensations, try {}".format(VoiceTestCase.SLEEP_TIME, test_tries))
                systemTime.sleep(VoiceTestCase.SLEEP_TIME) # let Microphone start before waiting it to stops
                test_tries = test_tries+1
                
            gotHeardVoice = False
            playbackTime = 0
            voicenumber = 0
            playedVoiceNumber = 0
            toBePlayedVoiceNumber = 0
            playBackSensations=[]
            isHeardVoice = False
            while(not self.getAxon().empty()):
                isHeardVoice = False
                tranferDirection, sensation = self.getAxon().get(robot=self)
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    if sensation.getRobotType() == Sensation.RobotType.Sense:
                        print("--- got Sense Voice {}s".format(self.getPlaybackTime(len(sensation.getData()))))
                        voicenumber +=1
                        if not gotHeardVoice:
                            test_runs += 1
                            gotHeardVoice = True  # got it
                        isHeardVoice = True
                        # TODO here we test speaking so we must disable hearing
                        if not hearingDisabled:                           
                            print("--- test {} disable hearing".format(test_runs))
                            if MICROPHONEPLAYBACK:
                                del self.microphonePlayback.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()]
                            else:
                                del self.microphone.getMemory()._presentItemSensations[VoiceTestCase.LOCATION][self.Wall_E_item_sensation.getName()]
                            hearingDisabled = True
                                #sleep as long as sound playing will take
                        print("--- BE SILENT Playback heard voice test {} try {}".format(test_runs, test_tries))
                        playbackTime += 3.0 * self.getPlaybackTime(datalen=len(sensation.getData()))
                        if MICROPHONEPLAYBACK:
                            playBackSensation = self.microphonePlayback.createSensation(
                                                                        memoryType=Sensation.MemoryType.Sensory,
                                                                        sensationType=Sensation.SensationType.Voice,
                                                                        robotType=Sensation.RobotType.Muscle,
                                                                        data=sensation.getData(),
                                                                        kind = Sensation.Kind.Normal)
                            playBackSensation.setKind(kind = Sensation.Kind.Normal)
                            self.microphonePlayback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
                        else:
                            playBackSensation = self.playback.createSensation(
                                                                        memoryType=Sensation.MemoryType.Sensory,
                                                                        sensationType=Sensation.SensationType.Voice,
                                                                        robotType=Sensation.RobotType.Muscle,
                                                                        data=sensation.getData(),
                                                                        kind = Sensation.Kind.Normal)
                            playBackSensation.setKind(kind = Sensation.Kind.Normal)
                            self.playback.getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Down, sensation=playBackSensation)
                        toBePlayedVoiceNumber +=1
                        playBackSensations.append(playBackSensation)
                elif sensation.getSensationType() == Sensation.SensationType.RobotState:
                    if sensation.getRobotType() == Sensation.RobotType.Sense:
                        print("--- got Sense RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                        if sensation.getRobotState() == Sensation.RobotState.CommunicationVoicePlayed:
                            print("---Voice is played")
                            playedVoiceNumber +=1
                            for a in sensation.getAssiciations():
                                if a.getSensation() in playBackSensations:
                                    playBackSensations.remove(a.getSensation())
                                    print("---1: OUR Voice is played")
                    else:
                        print("--- got Other RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                else:
                    print("--- got Other Sensation")
            print ("toBePlayedVoiceNumber {} playedVoiceNumber {} should wait {}".format(toBePlayedVoiceNumber, playedVoiceNumber, toBePlayedVoiceNumber != playedVoiceNumber))

            if toBePlayedVoiceNumber > playedVoiceNumber or len(playBackSensations) > 0:
                print("Waiting max {}s until all voices are played".format((toBePlayedVoiceNumber - playedVoiceNumber) * VoiceTestCase.VOIVEPLAYEDMAXWAITTIME))
                sleepedNumber = 0
                while sleepedNumber < (toBePlayedVoiceNumber - playedVoiceNumber) * VoiceTestCase.VOIVEPLAYEDMAXWAITTIME and\
                      toBePlayedVoiceNumber > playedVoiceNumber or len(playBackSensations) > 0:
                    if self.getAxon().empty():
                        systemTime.sleep(1)
                        sleepedNumber +=1
                    else:
                        tranferDirection, sensation = self.getAxon().get(robot=self)
                        if sensation.getSensationType() == Sensation.SensationType.Voice:
                            if sensation.getRobotType() == Sensation.RobotType.Sense:
                                print("--- waiting got Sense Voice {}s".format(self.getPlaybackTime(len(sensation.getData()))))
                        elif sensation.getSensationType() == Sensation.SensationType.RobotState:
                            if sensation.getRobotType() == Sensation.RobotType.Sense:
                                print("---waiting  got Sense RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                                if sensation.getRobotState() == Sensation.RobotState.CommunicationVoicePlayed:
                                    print("---Voice is played")
                                    playedVoiceNumber +=1
                                    for a in sensation.getAssociations():
                                        if a.getSensation() in playBackSensations:
                                            playBackSensations.remove(a.getSensation())
                                            print("---2: OUR Voice is played")
                            else:
                                print("--- got Other RobotState {}".format(Sensation.getRobotStateString(sensation.getRobotState())))
                        else:
                            print("--- got Other Sensation")
                        
#             if playbackTime > 0:
#                 print("\n--- BE SILENT test sleeping {} seconds until playback is done test {} try {}\n    got {} Voices ".format(playbackTime, test_runs, test_tries, voicenumber))
#                 systemTime.sleep(playbackTime) # let Microphone start before waiting it to stops
            if not isHeardVoice:
                print("\n--- got Sensations, but no heard voice, test continues")
    
        
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

 