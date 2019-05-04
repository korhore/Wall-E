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

    def __init__(self,
                 instance=None,
                 is_virtualInstance=False,
                 is_subInstance=False,
                 level=0,
                 inAxon=None, 
                 outAxon=None):
        Robot.__init__(self,
                       instance=instance,
                       is_virtualInstance=is_virtualInstance,
                       is_subInstance=is_subInstance,
                       level=level,
                       inAxon=inAxon,
                       outAxon=outAxon)
        print("We are in AlsaAudioPlayback, not Robot")

        # from settings        
        self.device= self.config.getMicrophone()    # TODO with headset works
        self.channels=1
        self.rate = 44100
        self.format = alsaaudio.PCM_FORMAT_S16_LE
 
        self.outp = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, device=self.device)
        # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
        self.outp.setchannels(self.channels)
        self.outp.setrate(self.rate)
        self.outp.setformat(self.format)
        self.outp.setperiodsize(2048) #32 160
 
        self.log('cardname ' + self.outp.cardname())

        self.running=False
        self.on=False
        
        self.debug_time=time.time()
        
    def run(self):
        self.log(" Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())      
        
        
        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            sensation=self.inAxon.get()
            self.log("got sensation from queue " + sensation.toDebugStr())
            # if we get something we can do    
            if sensation.getSensationType() == Sensation.SensationType.VoiceData:
                self.log('run: Sensation.SensationType.VoiceData self.outp.write(sensation.getVoiceData()')
                self.outp.write(sensation.getVoiceData())
            elif sensation.getSensationType() == Sensation.SensationType.Stop:
                self.log('run: SensationSensationType.Stop')      
                self.stop()

        self.mode = Sensation.Mode.Stopping
        self.log("Stopping AlsaAudioPlayback")
    

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log("run ALL SHUT DOWN")
                    


if __name__ == "__main__":
    alsaAudioPlayback = AlsaAudioPlayback()
    alsaAudioPlayback.start()  