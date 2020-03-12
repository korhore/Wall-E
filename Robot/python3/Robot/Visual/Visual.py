'''
Created on 12.03.2020
Updated on 12.03.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for visual
combined with low level sense feedback.
implemented by wxPython and need display hardware and drivers (linux X, Windows its own, etc)

Idea is to implement one way visual and feedback so
that only one function is going on in a time.
Default is to used threading, like Robot-framework uses normally.


'''
import time as systemTime
from threading import Thread
from threading import Timer
import wx

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

class Visual(Robot):

    # Button definitions
    ID_START = wx.NewId()
    ID_STOP = wx.NewId()
        
    # Define notification event for thread completion
    EVT_RESULT_ID = wx.NewId()
    
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0):
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        print("We are in Visual, not Robot")
        
        self.app = Visual.MainApp(0)
        self.app.setRobot(self)
        
        self.wxWorker = Visual.wxWorker(robot=self, app=self.app)

        # not yet running
        self.running=False
        #self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
                            # does not help
                            
                            
    def run(self):
        # default
        self.running=True #called
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run: Starting robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()
        self.studyOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        
        # added
        self.wxWorker.start()       # start ui on its own thread
       
       # default
        while self.running:
            # if we can't sense, the we wait until we get something into Axon
            # or if we can sense, but there is something in our xon, process it
            if not self.getAxon().empty() or not self.canSense():
                transferDirection, sensation, association = self.getAxon().get()
                self.log(logLevel=Robot.LogLevel.Normal, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
                self.process(transferDirection=transferDirection, sensation=sensation, association=association)
                # as a test, echo everything to external device
                #self.out_axon.put(sensation)
            else:
                self.sense()
 
        self.mode = Sensation.Mode.Stopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")
        
        # added
        #self.wxWorker.stop()       # stop ui on its own thread
   

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run ALL SHUT DOWN")
        
#     def run(self):
#         self.log("Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
#         
#         # starting other threads/senders/capabilities
#         
#         self.running=True
#         self.nextSenseTime = None
#                 
#         # live until stopped
#         self.mode = Sensation.Mode.Normal
#         
#         self.wxWorker.start()       # start ui on its own thread
#         
#         self.wxWorker.stop()       # start ui on its own thread
        
        
#         app = Visual.MainApp(0)
#         app.setRobot(self)
#         app.MainLoop()
        # We get here
        # /tmp/pip-install-au36yiyx/wxPython/ext/wxWidgets/src/unix/threadpsx.cpp(1810): assert "wxThread::IsMain()" failed in OnExit(): only main thread can be here [in thread 7f98d05bd740]
        # so thread is stopped here and no other lines are executed
#         app.ExitMainLoop()
#         while self.running:
#             systemTime.sleep(1)
    def process(self, transferDirection, sensation, association=None):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr()) #called
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
            
    def OnIdle(self):
        if not self.getAxon().empty(): #called
            transferDirection, sensation, association = self.getAxon().get()
            self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())  
            if transferDirection == Sensation.TransferDirection.Up:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr='OnIdle: self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation))')      
                self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
            else:
                if sensation.getSensationType() == Sensation.SensationType.Stop:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='OnIdle: SensationSensationType.Stop')      
                    self.stop()
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='OnIdle: TODO Visual processing')      
#                     
#                 # stop
#                 if sensation.getSensationType() == Sensation.SensationType.Stop:
#                 #self.alsaAudioMicrophone.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
#                 self.alsaAudioMicrophone.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                         self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                         self.running=False
#                    # Item.name.presence to microphone
# #                     elif sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemory() == Sensation.Memory.Working and\
# #                          sensation.getDirection() == Sensation.Direction.Out:
# #                         #self.alsaAudioMicrophone.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
# #                         self.alsaAudioMicrophone.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                     # Voice to playback
#                     else:
#                         #self.alsaAudioPlayback.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
#                         self.nextSenseTime = systemTime.time() + self.alsaAudioPlayback.getPlaybackTime(datalen=len(sensation.getData()))
#                         self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                         
#                         # sleep voice playing length, so we don't sense spoken voices
#                         #systemTime.sleep(self.alsaAudioPlayback.getPlaybackTime())
#             # we have time to sense
#             else:
#                 # check, id playback is going on
#                 if self.nextSenseTime is not None and\
#                    systemTime.time() < self.nextSenseTime:
#                     systemTime.sleep(self.nextSenseTime - systemTime.time())
#                     self.nextSenseTime = None
# 
#                 self.alsaAudioMicrophone.sense()
                    
    #def EVT_RESULT(self, win, func):
    def EVT_RESULT(win, func):
        """Define Result Event."""
        win.Connect(-1, -1, Visual.EVT_RESULT_ID, func) #called

                     
    '''
    We can't sense as a meaning of Robot-framework
    even if we can produce feedback.
    '''
                
    def canSense(self):
        return False #     def test_Presense(self): #called
#         print('\ntest_Presense')
#         history_sensationTime = systemTime.time() -2*max(VisualTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
# 
#         self.assertEqual(self.getAxon().empty(), True, 'Axon should be empty at the beginning of test_Presense\nCannot test properly this!')
#         print('\n too old_Presense')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(time=history_sensationTime,
#                                                  memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Entering)
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         # Not sure do we always get a voice
#         self.assertEqual(self.getAxon().empty(), True, 'Axon should  be empty')
#         self.assertEqual(len(self.visual.presentItemSensations), 0, 'len(self.visual.presentItemSensations should be 0')
#       
#         print('\n current Entering')
#         # make potential response
#         #systemTime.sleep(0.1)  # wait to get really even id
#         voice_sensation = Sensation.create(time=self.history_sensationTime,
#                                                   memory=Sensation.Memory.Sensory,
#                                                   sensationType=Sensation.SensationType.Voice,
#                                                   direction=Sensation.Direction.Out,
#                                                   data="22")
#         #systemTime.sleep(0.1)  # wait to get really even id
#         item_sensation = Sensation.create(time=self.history_sensationTime,
#                                           memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Entering)
#         item_sensation.associate(sensation=voice_sensation,
#                                            score=VisualTestCase.SCORE_1)
# 
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Entering)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
#         #self.assertEqual(len(self.visual.presentItemSensations[Wall_E_item_sensation.getName()].getAssociations()), 1)
#         
#         # process
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty when name entering')
#         tranferDirection, sensation, association = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
#         
#         print('\n current Present')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Present)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
# 
#         # process       
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
#         self.assertEqual((self.getAxon().empty()), True,  'Axon should be empty when present, because only Voice is used')
# # no voice given so we don't get a voice back
# #         tranferDirection, sensation = self.getAxon().get()
# #         #Voice
# #         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
# #         # to be spoken
# #         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
# 
#         print('\n current Present again')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Present)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
# 
#         #process       
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
#         self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty when entering again because only Voice is used')
# # no voice given so we don't get a voice back
# #         tranferDirection, sensation = self.getAxon().get()
# #         #Voice
# #         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
# #         # to be spoken
# #         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
#         
#         print('\n current Absent')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Absent)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 0, 'len(self.visual.presentItemSensations after Absent Item Sensation should be 0')
# 
#         #process              
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
#         self.assertEqual(len(self.visual.presentItemSensations), 0, 'len(self.visual.presentItemSensations should be 0')
#         self.assertEqual((self.getAxon().empty()), True,  'Axon should be empty')
#         
#     # #NAME2
#         print("test is sleeping " + str(Communication.COMMUNICATION_INTERVAL+ 1.0) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human visual then, so change it back)")       
#         systemTime.sleep(Communication.COMMUNICATION_INTERVAL+ 2.0)
#     
#         print('\n current Entering')
#         # make potential response
#         #systemTime.sleep(0.1)  # wait to get really even id
#         voice_sensation = Sensation.create(time=self.history_sensationTime,
#                                                   memory=Sensation.Memory.Sensory,
#                                                   sensationType=Sensation.SensationType.Voice,
#                                                   direction=Sensation.Direction.Out,
#                                                   data="333")
#         #systemTime.sleep(0.1)  # wait to get really even id
#         item_sensation = Sensation.create(time=self.history_sensationTime,
#                                           memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Entering)
#         item_sensation.associate(sensation=voice_sensation,
#                                            score=VisualTestCase.SCORE_1)
#         
#         # make entering item and process
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Entering)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations after Entering Item Sensation should be 1')
# 
#         #process                      
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual((self.getAxon().empty()), False,  'Axon should not be empty, when entering')
#         tranferDirection, sensation, association = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
# 
#         print('\n current Entering')
#         # make potential response
#         #systemTime.sleep(0.1)  # wait to get really even id
#         voice_sensation = Sensation.create(time=self.history_sensationTime,
#                                                   memory=Sensation.Memory.Sensory,
#                                                   sensationType=Sensation.SensationType.Voice,
#                                                   direction=Sensation.Direction.Out,
#                                                   data="4444")
#         #systemTime.sleep(0.1)  # wait to get really even id
#         item_sensation = Sensation.create(time=self.history_sensationTime,
#                                           memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME2,
#                                                  presence=Sensation.Presence.Entering)
#         item_sensation.associate(sensation=voice_sensation,
#                                            score=VisualTestCase.SCORE_2)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 2, 'len(self.visual.presentItemSensations after Entering Item Sensation should NAME2 be 2')
# 
#         # make entering and process
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME2,
#                                                  presence=Sensation.Presence.Entering)
#         #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         # Now we should have 1 item in Robot.presentItemSensations (can be assigned as self.association) with with  name and associations count
#         self.assertEqual(len(self.visual.presentItemSensations), 2, 'len(self.visual.presentItemSensations after Entering Item NAME2 Sensation should NAME2 be 2')
# 
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual((self.getAxon().empty()), True,  'Axon should be empty when entered and present')
#         
# # no voice given so we don't get a voice back
# #         tranferDirection, sensation = self.getAxon().get()
# #         #Voice
# #         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
# #         # to be spoken
# #         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
#         
#         print('\n current Present')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME2,
#                                                  presence=Sensation.Presence.Present)
#          #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#        
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(len(self.visual.presentItemSensations), 2, 'len(self.visual.presentItemSensations should be 2')
#         self.assertEqual((self.getAxon().empty()), True,  'Axon should  be empty')
# # no voice given so we don't get a voice back
# #         tranferDirection, sensation = self.getAxon().get()
# #         #Voice
# #         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
# #         # to be spoken
# #         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
# 
#         print('\n current Present again')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME2,
#                                                  presence=Sensation.Presence.Present)
#          #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#        
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(len(self.visual.presentItemSensations), 2, 'len(self.visual.presentItemSensations should be 2')
# # no voice given so we don't get a voice back
# #         tranferDirection, sensation = self.getAxon().get()
# #         #Voice
# #         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
# #         # to be spoken
# #         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
#         
#         print('\n current Absent')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME2,
#                                                  presence=Sensation.Presence.Absent)
#        
#          #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
# 
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(self.getAxon().empty(), True, 'Axon should  be empty')
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
#     
#         print('\n current Absent')
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  presence=Sensation.Presence.Absent)
#          #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#        
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         self.assertEqual(self.getAxon().empty(), True, 'Axon should  be empty')
#         self.assertEqual(len(self.visual.presentItemSensations), 0, 'len(self.visual.presentItemSensations should be 0')
#         
#     '''
#     1) item.name
#     2) process(item) should get old self.Wall_E_voice_sensation, that will be
#        spoken out
#     3) parent Axon should get self.Wall_E_voice_sensation
#     '''
# 
#     def test_ProcessItemVoice(self):
#         print('\ntest_ProcessItemVoice')
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
# 
#         print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Working)')
#         self.do_test_ProcessItemVoice(memory=Sensation.Memory.Working)
#         
#         # nope, Memory.Sensory is not ment to work
# #         print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)')
# #         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
# #         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         #self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)
#         
#         # test again
# 
#         print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Working)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_ProcessItemVoice(memory=Sensation.Memory.Working)
#         
#         # nope, Memory.Sensory is not ment to work
# #         print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)')
# #         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
# #         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
# #         self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)
# 
#         # and test again once more 
# 
#         print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Working)')
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         self.do_test_ProcessItemVoice(memory=Sensation.Memory.Working)
#         
#         # nope, Memory.Sensory is not ment to work
# #         print('self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)')
# #         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
# #         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
# #         self.do_test_ProcessItemVoice(memory=Sensation.Memory.Sensory)
# 
#        
#     def do_test_ProcessItemVoice(self, memory):
#         history_sensationTime = systemTime.time() -2*max(VisualTestCase.ASSOCIATION_INTERVAL, Communication.COMMUNICATION_INTERVAL)
# 
#         # Make Voice to the history by parameter Memory type       
#         # simulate Association has connected an voice to Item and Image 
#         # Voice is in Sensory Memory, it is not used in Visual yet or
#         # it can be in n LongTerm memory, classified to be a good Voice
#         # Make two test of these 
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
# 
#         # response # 1
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_voice_sensation_1 = Sensation.create(time=history_sensationTime,
#                                                     memory=memory,
#                                                     sensationType=Sensation.SensationType.Voice,
#                                                     direction=Sensation.Direction.Out,                                                   
#                                                     data="55555")
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
#         
#         self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 0)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len)
#         
#         Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_image_sensation,
#                                            score=VisualTestCase.SCORE_1)
#                                                                      
#         self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 1)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         
#         Wall_E_voice_sensation_1.associate(sensation=self.Wall_E_item_sensation,
#                                            score=VisualTestCase.SCORE_1)
#         self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         
#         
#         # response # 2
#         #systemTime.sleep(0.1)  # wait to get really even id        
#         Wall_E_voice_sensation_2 = Sensation.create(time=history_sensationTime,
#                                                     memory=memory,
#                                                     sensationType=Sensation.SensationType.Voice,
#                                                     direction=Sensation.Direction.Out,                                                   
#                                                     data="666666")
#         
#         Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_image_sensation,
#                                            score=VisualTestCase.SCORE_2)
#         self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 1)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         
#         Wall_E_voice_sensation_2.associate(sensation=self.Wall_E_item_sensation,
#                                            score=VisualTestCase.SCORE_2)
#         self.assertEqual(len(Wall_E_voice_sensation_2.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
# 
#         # response # 3
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_voice_sensation_3 = Sensation.create(time=history_sensationTime,
#                                                     memory=memory,
#                                                     sensationType=Sensation.SensationType.Voice,
#                                                     direction=Sensation.Direction.Out,
#                                                     data="7777777")
#         
#         Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_image_sensation,
#                                            score=VisualTestCase.SCORE_3)
#         self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 1)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         
#         Wall_E_voice_sensation_3.associate(sensation=self.Wall_E_item_sensation,
#                                            score=VisualTestCase.SCORE_3)
#         self.assertEqual(len(Wall_E_voice_sensation_3.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
# 
#         
#         
#         
# 
#         ## test part
#                 
#         #image and Item
#         # simulate item and image are connected each other with TensorflowClassifivation
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_item_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                  sensationType=Sensation.SensationType.Item,
#                                                  direction=Sensation.Direction.Out,
#                                                  name=VisualTestCase.NAME,
#                                                  associations=[],
#                                                  presence=Sensation.Presence.Entering)
#         #systemTime.sleep(0.1)  # wait to ger really even id
#         Wall_E_image_sensation = Sensation.create(memory=Sensation.Memory.Working,
#                                                   sensationType=Sensation.SensationType.Image,
#                                                   direction=Sensation.Direction.Out)
#         
#         Wall_E_image_sensation.associate(sensation=Wall_E_item_sensation,
#                                          score=VisualTestCase.SCORE_1)
#         # these connected each other
#         self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
#         self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
#         # TODO this verifies test, but not implementation
#         '''
#         Commented out, so we can  correct implementation
#         # simulate Association has connected an voice to Item and Image 
#         Wall_E_voice_sensation_1 = Sensation.create(sensationType=Sensation.SensationType.Voice, 
#                                                        associations=[Sensation.Association(sensation=Wall_E_image_sensation,
#                                                                                          score=VisualTestCase.SCORE_1),
#                                                                     Sensation.Association(sensation=Wall_E_item_sensation,
#                                                                                          score=VisualTestCase.SCORE_1)])
#          # test that all is OK for tests
#         self.assertEqual(len(Wall_E_voice_sensation_1.getAssociations()), 2)
#         # add missing associations test that all is OK for tests
#         Wall_E_image_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation_1,
#                                                                        score=VisualTestCase.SCORE_1))
#         self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
#         # add missing associations test that all is OK for tests
#         Wall_E_item_sensation.addAssociation(Sensation.Association(sensation=Wall_E_voice_sensation_1,
#                                                                       score=VisualTestCase.SCORE_1))
#         self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 2)
# 
#         
#         #######################
#         '''
# 
#          #simulate TensorflowClassification send presence item to MainBobot
#         self.visual.tracePresents(Wall_E_item_sensation) # presence
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
# 
#         #process
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation, association=None)
#         # We have Voice to be spoken out
#         # minimum is that we get something
#         self.assertNotEqual(self.getAxon().empty(), True, 'Axon should not be empty')
#         
#         tranferDirection, sensation, association = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
#         
#         # score or importance TODO check this
#         # this is hard to implement, because used voiced get higher importance, so lower score voices can get higher importance
#         # than higher score Voices,
#         # When test begibs, we get Voices with score CORE_2, but after that we cab get also SCORE_1
#         # Soooo seems that there is nothing wrong with algorithm, but hard to test
#         #self.assertEqual(sensation.getScore(),self.SCORE_2, 'should get Voice scored ' + str(self.SCORE_2))
# 
#         Wall_E_voice_sensation_1.delete()
#         Wall_E_voice_sensation_2.delete()
#         
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         
#         # now we respond
#         #systemTime.sleep(0.1)  # wait to get really even id
#         Wall_E_voice_response_sensation = Sensation.create(#Stime=history_sensationTime,
#                                                     memory=memory,
#                                                     sensationType=Sensation.SensationType.Voice,
#                                                     direction=Sensation.Direction.Out,
#                                                     data="88888888")
#         # To be sure to get a new response, no this will be too new
#         #Wall_E_voice_response_sensation.setTime(systemTime.time())
#        
#         Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_image_sensation,
#                                            score=VisualTestCase.SCORE_2)
#         self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 1)
#         self.assertEqual(len(self.Wall_E_image_sensation.getAssociations()), self.Wall_E_image_sensation_association_len+1)
#         self.Wall_E_image_sensation_association_len = len(self.Wall_E_image_sensation.getAssociations())
#         
#         Wall_E_voice_response_sensation.associate(sensation=self.Wall_E_item_sensation,
#                                            score=VisualTestCase.SCORE_2)
#         self.assertEqual(len(Wall_E_voice_response_sensation.getAssociations()), 2)
#         self.assertEqual(len(self.Wall_E_item_sensation.getAssociations()), self.Wall_E_item_sensation_association_len+1)
#         self.Wall_E_item_sensation_association_len = len(self.Wall_E_item_sensation.getAssociations())
#         
#         self.assertEqual(len(self.visual.presentItemSensations), 1, 'len(self.visual.presentItemSensations should be 1')
#         # process
#         self.visual.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_response_sensation, association=None)
# 
#         # We should have a Voice to be spoken out again 
#         # minimum is that we get something
# 
#         # wait some time        
#         #systemTime.sleep(5)
#         # OOPS Why we don't get response, but getMostImportantSensation did not find any 
#         
#         self.assertEqual(self.getAxon().empty(), False, 'Axon should not be empty')
#         
#         tranferDirection, sensation, association = self.getAxon().get()
#         #Voice
#         self.assertEqual(sensation.getSensationType(),Sensation.SensationType.Voice, 'should get Voice')
#         # to be spoken
#         self.assertEqual(sensation.getDirection(),Sensation.Direction.In, 'should get Voice to be spoken')
#         
# 
#         # we son't response any more, so Visual.stopWaitingResponse
#         # should be run and self.visual.communicationItems) should be empty
#         # wait some time
#         print("test is sleeping " + str(Communication.COMMUNICATION_INTERVAL+ 1.0) + " until continuing. To get faster test change temporarely Communication.COMMUNICATION_INTERVAL\n(Test logic does not change, but functionality is for testing only, not for human visual then, so change it back)")       
#         systemTime.sleep(Communication.COMMUNICATION_INTERVAL+ 2.0)
#         # no communicationItems should be left in 
#         self.assertEqual(len(self.visual.communicationItems),0, 'no communicationItems should be left in Visual ')
#         print("test continues, should got  stopWaitingResponse")       

     
    # Thread class that executes wxPython gui on its own thread
    class wxWorker(Thread):
        """Worker Thread Class."""
        def __init__(self, app, robot):
            """Init wxWorker Thread Class."""
            Thread.__init__(self) #called
            self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
            self.app = app
            self.robot = robot
     
        def setRobot(self, robot):
            self.robot=robot
        def getRobot(self):
            return self.robot
        
        def run(self):
            """Run wxWorker Thread."""
            self.app.MainLoop() #ccalled
    
        def abort(self):
            """abort worker thread."""
            # Method for use by main thread to signal an abort
            self.want_abort = True

    class ResultEvent(wx.PyEvent):
        """Simple event to carry arbitrary result data."""
        def __init__(self, data):
            """Init Result Event."""
            wx.PyEvent.__init__(self)
            self.SetEventType(Visual.EVT_RESULT_ID)
            self.data = data

    # Thread class that executes processing
    class WorkerThread(Thread):
        """Worker Thread Class."""
        def __init__(self, notify_window, robot):
            """Init Worker Thread Class."""
            Thread.__init__(self)
            self.notify_window = notify_window
            self.robot = robot
            self.want_abort = False
            # This starts the thread running on creation, but you could
            # also make the GUI thread responsible for calling this
            self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
            self.start()
    
        def setRobot(self, robot):
            self.robot=robot
        def getRobot(self):
            return self.robot
        
        def run(self):
            """Run Worker Thread."""
            
            while self.getRobot().running:
                self.getRobot().OnIdle()
#             # This is the code executing in the new thread. Simulation of
#             # a long process (well, 10s here) as a simple loop - you will
#             # need to structure your processing so that you periodically
#             # peek at the abort variable
#             for i in range(10):
#                 systemTime.sleep(1)
#                 if self.want_abort:
#                     # Use a result of None to acknowledge the abort (of
#                     # course you can use whatever you'd like or even
#                     # a separate event type)
#                     if self.notify_window is not None:
#                         wx.PostEvent(self.notify_window, Visual.ResultEvent(None))
#                     return
#             # Here's where the result would be returned (this is an
#             # example fixed result of the number 10, but it could be
#             # any Python object)
#             wx.PostEvent(self.notify_window, Visual.ResultEvent(10))
#     
        def abort(self):
            """abort worker thread."""
            # Method for use by main thread to signal an abort
            self.want_abort = True
            
    # GUI Frame class that spins off the worker thread
    class MainFrame(wx.Frame):
        """Class MainFrame."""
        def __init__(self, parent, id):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, 'Thread Test') #called
    
            # Dumb sample frame with two buttons
            wx.Button(self, Visual.ID_START, 'Start', pos=(0,0))
            wx.Button(self, Visual.ID_STOP, 'Stop', pos=(0,50))
            self.status = wx.StaticText(self, -1, '', pos=(0,100))
    
            self.Bind(wx.EVT_BUTTON, self.OnStart, id=Visual.ID_START)
            self.Bind(wx.EVT_BUTTON, self.OnStop, id=Visual.ID_STOP)
#            self.Bind (wx.EVT_IDLE, self.OnIdle)

    
            # Set up event handler for any worker thread results
#             Visual.EVT_RESULT(self,self.OnResult)
#             Visual.EVT_RESULT(self,self.OnResult)
    
            # And indicate we don't have a worker thread yet
            self.worker = None
    
        def setRobot(self, robot):
            self.robot=robot #called
        def getRobot(self):
            return self.robot #called
        
        def OnStart(self, event):
            """Start Computation."""
            # Trigger the worker thread unless it's already busy
            if not self.worker: #called
                self.status.SetLabel('Starting computation')
                #self.worker = Visual.WorkerThread(notify_window=self, robot=self.getRobot())
    
        def OnStop(self, event):
            """Stop Computation."""
            # Flag the worker thread to stop if running
#             if self.worker:
#                 self.status.SetLabel('Trying to abort computation')
#                 self.worker.abort()
            #Tell also our Robot that we wan't to stop
            self.getRobot().running=False
            self.Close()
#            wx.WakeUpMainThread() # to get the main thread to process events.
    
#         def OnResult(self, event):
#             """Show Result status."""
#             if event.data is None:
#                 # Thread aborted (using our convention of None return)
#                 self.status.SetLabel('Computation aborted')
#             else:
#                 # Process results here
#                 self.status.SetLabel('Computation Result: %s' % event.data)
#             # In either event, the worker is done
#             self.worker = None
#             
#         def OnIdle(self, event):
#             """ on Idle do Robot processing """
#             self.getRobot().OnIdle() #called
    
    class MainApp(wx.App):
        """Class Main App."""
        def OnInit(self):
            """Init Main App."""
            self.frame = Visual.MainFrame(None, -1) #called
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True

        def setRobot(self, robot):
            self.robot=robot #called
            self.frame.setRobot(robot)
        def getRobot(self):
            return self.robot
            

if __name__ == "__main__":
    visual = Visual()
    #alsaAudioMicrophonePlayback.start()  