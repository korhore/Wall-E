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
                 level=0):
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        print("We are in AlsaAudioMicrophonePlayback, not Robot")
 
        # load subRobot in Robot way. Otherway we get a conflict with MainRobot loading way
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
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
#         voice_data=None
#         voice_l=0
        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                transferDirection, sensation = self.getAxon().get()
                self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())  
                if transferDirection == Sensation.TransferDirection.Up:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation))')      
                    self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation)
                elif sensation.getSensationType() == Sensation.SensationType.Stop:
                    self.alsaAudioMicrophone.getAxon().put(transferDirection=transferDirection, sensation=sensation)
                    self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation)
                elif sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemory() == Sensation.Memory.LongTerm and\
                     sensation.getDirection() == Sensation.Direction.Out:
                    self.alsaAudioMicrophone.getAxon().put(transferDirection=transferDirection, sensation=sensation)
                else:
                    self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation)
                    # sleep voice playing length, so we don't sense spoken voices
                    systemTime.sleep(self.alsaAudioPlayback.getPlaybackTime())
            else:
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