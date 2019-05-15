'''
Created on 04.05.2019
Updated on 04.05.2019

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for speaking
implemented by alasaaudio and need usb-speaker hardware

'''
import time
import alsaaudio

from threading import Thread
from threading import Timer


from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

class AlsaAudioPlayback(Robot):
    """
     Implementaion for out Voice sensation at Sensory level
     using ALSA-library and speaker as hardware
    """
    CHANNELS=1
    RATE = 44100
    FORMAT = alsaaudio.PCM_FORMAT_S16_LE

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
        print("We are in AlsaAudioPlayback, not Robot")

        # from settings        
        self.device= self.config.getPlayback()
        self.channels=AlsaAudioPlayback.CHANNELS
        self.rate = AlsaAudioPlayback.RATE
        self.format = AlsaAudioPlayback.FORMAT
        
        try:
            self.log("alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, device=" + self.device + ')')
            self.outp = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, device=self.device)
            # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
            self.log("self.outp.setchannels(self.channels")
            self.outp.setchannels(self.channels)
            self.outp.setrate(self.rate)
            self.outp.setformat(self.format)
            self.outp.setperiodsize(2048) #32 160
            self.ok=True
            self.log('cardname ' + self.outp.cardname())
        except Exception as e:
            print ("AlsaAudioPlayback exception " + str(e))
            self.ok=False

 

        self.running=False
        self.on=False
        
        self.debug_time=time.time()
        
    def run(self):
        if self.ok:
            self.log("Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))
            
            self.running=True
                    
            # live until stopped
            self.mode = Sensation.Mode.Normal
            while self.running:
                sensation=self.axon.get()
                self.log("got sensation from queue " + sensation.toDebugStr())
                # if we get something we can do    
                if sensation.getSensationType() == Sensation.SensationType.Voice:
                    self.log('run: Sensation.SensationType.VoiceData self.outp.write(sensation.getVoiceData()')
                    self.outp.write(sensation.getData())
                elif sensation.getSensationType() == Sensation.SensationType.Stop:
                    self.log('run: SensationSensationType.Stop')      
                    self.stop()
    
            self.mode = Sensation.Mode.Stopping
            self.log("Stopping AlsaAudioPlayback")
        
    
             # stop virtual instances here, when main instanceName is not running any more
            for robot in self.subInstances:
                robot.stop()
           
            self.log("run ALL SHUT DOWN")
                    


if __name__ == "__main__":
    alsaAudioPlayback = AlsaAudioPlayback()
    alsaAudioPlayback.start()  