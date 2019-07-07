'''
Created on 04.05.2019
Updated on 02.07.2019

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for speaking
implemented by alsaaudio and need usb-speaker hardware

'''
import time as systemTime
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
    
    COMMUNICATION_INTERVAL=60.0     # time window to history 
                                    # for sensations we communicate

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
        
        self.last_datalen=0
        self.last_write_time = systemTime.time()
       
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

        # not yet running
        self.running=False
        
                    
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
        # we can speak, but only if sensation is new enough
        elif self.ok and self.running and sensation.getSensationType() == Sensation.SensationType.Voice and sensation.getDirection() == Sensation.Direction.In:
            if systemTime.time() - sensation.getTime() < AlsaAudioPlayback.COMMUNICATION_INTERVAL:
                if self.last_datalen != len(sensation.getData()) or systemTime.time() - self.last_write_time > AlsaAudioPlayback.COMMUNICATION_INTERVAL:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: Sensation.SensationType.VoiceData self.outp.write(sensation.getVoiceData()')
                    self.outp.write(sensation.getData())
                    sensation.save()    #remember what we played
                    self.last_datalen = len(sensation.getData())
                    self.last_write_time = systemTime.time()
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: this Voice already played in this interval')
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got too old Voice to play')
        else:
            self.log(logLevel=Robot.LogLevel.Error, logStr='process: got sensation we this robot can\'t process')
        self.log(logLevel=Robot.LogLevel.Detailed, logStr="self.running " + str(self.running))      

if __name__ == "__main__":
    alsaAudioPlayback = AlsaAudioPlayback()
    alsaAudioPlayback.start()  