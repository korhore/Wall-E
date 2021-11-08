'''
Created on 23.09.2020
Updated on 14.06.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for speaking
combined with low level sense hearing.

Idea is to implement one way hearing and speaking so
that only one function is going on in a time.
This is needed, if we don't use devices that has build in
loudspeaker voice filtering from microphone. In this situation, if we use
Microphone and Playback at same Robot system, then Microphone hears
what Playback speaks and then it is confused as real heard voices.

 
implemented by alsaaudio or by SoundDevice and needs usb-speaker  and
usb-microphone hardware.


'''
import time as systemTime
#import alsaaudio

from threading import Thread
#from threading import Timer


from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from Playback import Playback
from Microphone import Microphone

class MicrophonePlayback(Robot):

    def __init__(self,
                 mainRobot,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        Robot.__init__(self,
                       mainRobot=mainRobot,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss =  maxRss,
                       minAvailMem = minAvailMem,
                       location = location,
                       config = config)
        print("We are in MicrophonePlayback, not Robot")
 
        # load subRobot in Robot way. Other way we get a conflict with MainRobot loading way
        self.playback = self.loadSubRobot(subInstanceName='Playback', level=self.level)
        self.microphone = self.loadSubRobot(subInstanceName='Microphone', level=self.level)
        # No try transferDirection
        # should fix Axon one level up, so playback won't read self.microphone parents Axon
        #self.microphone.setParent(parent)



        # not yet running
        self.running=False
        self.playback.running=False
        self.microphone.running=False
        
    def run(self):
        self.log("Starting robot robot " + self.getName() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.playback.running=True
        self.microphone.running=True

        self.nextSenseTime = None
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        self.playback.mode = Sensation.Mode.Normal
        self.microphone.mode = Sensation.Mode.Normal
#         voice_data=None
#         voice_l=0
        self.microphone.informRobotState(robotState = Sensation.RobotState.MicrophoneSensing)
        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                # interrupt voice and put it to parent for processing
                self.microphone.putVoiceToParent()

                transferDirection, sensation = self.getAxon().get(robot=self)
                self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())  
#                 if transferDirection == Sensation.TransferDirection.Up:
                if transferDirection != Sensation.TransferDirection.Down:
                    # NOTE this handling is obsolete with self.route and
                    # should never happened and will be removed later from code,
                    # because sensations are routed directly to target Axons
#                     self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation))')      
#                     self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=sensation)')      
                    self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=sensation)(transferDirection=Sensation.TransferDirection.Direct, sensation=sensation)
                else:
                    # stop
                    if sensation.getSensationType() == Sensation.SensationType.Stop:
                        #self.microphone.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
                        self.microphone.process(transferDirection=transferDirection, sensation=sensation)
                        self.playback.process(transferDirection=transferDirection, sensation=sensation)
                        self.running=False
                    # Voice to playback
                    else:
                        # TODO old code did not work, because self.nextSenseTim is never None, self.playback.getPlaybackTime return always time to 
#                         self.nextSenseTime = systemTime.time() + self.playback.getPlaybackTime(datalen=len(sensation.getData()))
                        self.microphone.informRobotState(robotState = Sensation.RobotState.MicrophoneDisabled)
                        self.playback.process(transferDirection=transferDirection, sensation=sensation)
#                         if  self.nextSenseTime is None:
#                             self.nextSenseTime = systemTime.time() + self.playback.getPlaybackTime(datalen=len(sensation.getData()))
#                         elif self.nextSenseTime > systemTime.time(): # there was pending wait time
#                         if self.nextSenseTime > systemTime.time(): # there was pending wait time
#                             self.nextSenseTime = self.nextSenseTime - systemTime.time() + systemTime.time() + self.playback.getPlaybackTime(datalen=len(sensation.getData()))
#                         else:   # no pending wait time left, sleep normal time for this voice
#                             self.nextSenseTime = systemTime.time() + self.playback.getPlaybackTime(datalen=len(sensation.getData()))
                        self.nextSenseTime = systemTime.time() + self.playback.getPlaybackTime(datalen=len(sensation.getData()))
                            
                    sensation.detach(robot=self) # all done, for this sensation remember to detach                 
                        # sleep voice playing length, so we don't sense spoken voices
                        #systemTime.sleep(self.playback.getPlaybackTime())
            # we have time to sense
            else:
                # check, if playback is going on
                if self.nextSenseTime is not None and\
                   systemTime.time() < self.nextSenseTime:
                    self.microphone.informRobotState(robotState = Sensation.RobotState.MicrophoneDisabled)
                    systemTime.sleep(self.nextSenseTime - systemTime.time())
                    self.nextSenseTime = None
                    self.microphone.informRobotState(robotState = Sensation.RobotState.MicrophoneSensing)

                self.microphone.sense()
                    
    '''
    We can sense
    We are Sense type Robot
    '''        
    def canSense(self):
        return True 
     

if __name__ == "__main__":
    alsaAudioMicrophonePlayback = MicrophonePlayback()
    #alsaAudioMicrophonePlayback.start()  