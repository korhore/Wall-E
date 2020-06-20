'''
Created on 19.07.2019
Updated on 19.07.2019

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for speaking
combined with low level sense hearing.

Idea is to implement one way hearing and speaking so
that only one function is going on in a time.
This is needed, if we don't use devices that has build in
loudspeaker voice filtering from microphone. In this situation, if we use
AlsaAudioMicrophone and AlsaAudioPlayback at same Robot system, then Microphone hears
what Playback speaks and then it is confused as real heard voices.

 
implemented by alsaaudio-library and needs usb-speaker  and
usb-microphone hardware.


'''
import time as systemTime
import alsaaudio

from threading import Thread
from threading import Timer


from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from AlsaAudioPlayback import AlsaAudioPlayback
from AlsaAudioMicrophone import AlsaAudioMicrophone

class AlsaAudioMicrophonePlayback(Robot):

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT):
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss =  maxRss,
                       minAvailMem = minAvailMem)
        print("We are in AlsaAudioMicrophonePlayback, not Robot")
 
        # load subRobot in Robot way. Other way we get a conflict with MainRobot loading way
        self.alsaAudioPlayback = self.loadSubRobot(subInstanceName='AlsaAudioPlayback', level=self.level)
        self.alsaAudioMicrophone = self.loadSubRobot(subInstanceName='AlsaAudioMicrophone', level=self.level)
        # No try transferDirection
        # should fix Axon one level up, so alsaAudioPlayback won't read self.alsaAudioMicrophone parents Axon
        #self.alsaAudioMicrophone.setParent(parent)



        # not yet running
        self.running=False
        self.alsaAudioPlayback.running=False
        self.alsaAudioMicrophone.running=False
        
    def run(self):
        self.log("Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.alsaAudioPlayback.running=True
        self.alsaAudioMicrophone.running=True

        self.nextSenseTime = None
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        self.alsaAudioPlayback.mode = Sensation.Mode.Normal
        self.alsaAudioMicrophone.mode = Sensation.Mode.Normal
#         voice_data=None
#         voice_l=0
        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                # interrupt voice and put it to parent for processing
                self.alsaAudioMicrophone.putVoiceToParent()

                transferDirection, sensation = self.getAxon().get()
                self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())  
                if transferDirection == Sensation.TransferDirection.Up:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation))')      
                    self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
                else:
                    # stop
                    if sensation.getSensationType() == Sensation.SensationType.Stop:
                        #self.alsaAudioMicrophone.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
                        self.alsaAudioMicrophone.process(transferDirection=transferDirection, sensation=sensation)
                        self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation)
                        self.running=False
                   # Item.name.presence to microphone
#                     elif sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemoryType() == Sensation.MemoryType.Working and\
#                          sensation.getRobotType() == Sensation.RobotType.Sense:
#                         #self.alsaAudioMicrophone.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
#                         self.alsaAudioMicrophone.process(transferDirection=transferDirection, sensation=sensation)
                    # Voice to playback
                    else:
                        #self.alsaAudioPlayback.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation, association=association)
                        self.nextSenseTime = systemTime.time() + self.alsaAudioPlayback.getPlaybackTime(datalen=len(sensation.getData()))
                        self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation)
                        if  self.nextSenseTime is None:
                            self.nextSenseTime = systemTime.time() + self.alsaAudioPlayback.getPlaybackTime(datalen=len(sensation.getData()))
                        elif self.nextSenseTime > systemTime.time(): # there was pending wait time
                            self.nextSenseTime = self.nextSenseTime - systemTime.time() + systemTime.time() + self.alsaAudioPlayback.getPlaybackTime(datalen=len(sensation.getData()))
                        else:   # no pending wait time left, sleep normal time for this voice
                            self.nextSenseTime = systemTime.time() + self.alsaAudioPlayback.getPlaybackTime(datalen=len(sensation.getData()))
                            
                    sensation.detach(robot=self) # all done, for this sensation remember to detach                 
                        # sleep voice playing length, so we don't sense spoken voices
                        #systemTime.sleep(self.alsaAudioPlayback.getPlaybackTime())
            # we have time to sense
            else:
                # check, if playback is going on
                if self.nextSenseTime is not None and\
                   systemTime.time() < self.nextSenseTime:
                    systemTime.sleep(self.nextSenseTime - systemTime.time())
                    self.nextSenseTime = None

                self.alsaAudioMicrophone.sense()
                    
    '''
    We can sense
    We are Sense type Robot
    '''        
    def canSense(self):
        return True 
     

if __name__ == "__main__":
    alsaAudioMicrophonePlayback = AlsaAudioMicrophonePlayback()
    #alsaAudioMicrophonePlayback.start()  