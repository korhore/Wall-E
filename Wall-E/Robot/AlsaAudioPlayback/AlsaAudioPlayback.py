'''
Created on 04.05.2019
Updated on 19.07.2019

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for speaking
implemented by alsaaudio and need usb-speaker hardware

'''
import time as systemTime
import alsaaudio
import numpy
import math

from threading import Timer


from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from AlsaAudio import Settings
from AlsaAudio import AlsaAudioNeededSettings

class AlsaAudioPlayback(Robot):
    """
     Implementaion for out Voice sensation at Sensory level
     using ALSA-library and speaker as hardware
    """
    
    COMMUNICATION_INTERVAL=15.0     # time window to history 
                                    # for sensations we communicate
    WALLE_SPEAK_SPEED=1.25

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
        self.channels=Settings.AUDIO_CHANNELS
        self.rate = Settings.AUDIO_RATE
        self.format = AlsaAudioNeededSettings.AUDIO_FORMAT
        
        self.last_datalen=0
        self.last_write_time = systemTime.time()
        self.playbackTime=0.0
       
        try:
            self.log("alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, device=" + self.device + ')')
            self.outp = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, device=self.device)
            # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
            self.log("self.outp.setchannels(self.channels")
            self.outp.setchannels(self.channels)
            self.outp.setrate(self.rate)
            self.outp.setformat(self.format)
            self.outp.setperiodsize(Settings.AUDIO_PERIOD_SIZE)
            self.ok=True
            self.log('cardname ' + self.outp.cardname())
        except Exception as e:
            print ("AlsaAudioPlayback exception " + str(e))
            self.ok=False

        # not yet running
        self.running=False
        
                    
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        self.playbackTime=0.0
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
        # we can speak, but only if sensation is new enough
        elif self.ok and self.running and sensation.getSensationType() == Sensation.SensationType.Voice and sensation.getDirection() == Sensation.Direction.In:
        # Test
        #elif self.ok and self.running and sensation.getSensationType() == Sensation.SensationType.Voice:
            if systemTime.time() - sensation.getTime() < AlsaAudioPlayback.COMMUNICATION_INTERVAL:
                if self.last_datalen != len(sensation.getData()) or systemTime.time() - self.last_write_time > AlsaAudioPlayback.COMMUNICATION_INTERVAL:
                    data = sensation.getData()
                    if sensation.getKind() == Sensation.Kind.WallE:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: Sensation.SensationType.Voice play as Wall-E')
                        try:
                            aaa = numpy.fromstring(data, dtype=Settings.AUDIO_CONVERSION_FORMAT)
                        except (ValueError):
                            self.log("process numpy.fromstring(data, dtype=dtype: ValueError")      
                            return
                        step_length=self.WALLE_SPEAK_SPEED
                        step_point = 0.0    # where we are in source as float
                        ind_step_point = 0  # in which table index we are
                        result_aaa=[]
                        # while not and of source
                        while ind_step_point < len(aaa):
                            a = 0.0     # fill next a for destination
                            dest_step=0.0
                            while ind_step_point < len(aaa) and\
                                  dest_step <  step_length:
                                # how much we we get on this source ind
                                source_boundary = math.floor(step_point + 1.0)
                                can_get = source_boundary - step_point
                                if dest_step + can_get <= step_length:
                                    a = a+can_get*aaa[ind_step_point]
                                    step_point = float(source_boundary)
                                    ind_step_point = ind_step_point+1   # source to next boundary
                                else:
                                    can_get = min(source_boundary - step_point, step_length- dest_step)
                                    a = a+can_get*aaa[ind_step_point]
                                    step_point = step_point + can_get  # firward in this source ind
                                    if abs(step_point-source_boundary) < 0.001:
                                        ind_step_point = ind_step_point+1 # source to next boundary
                                   
                                dest_step = dest_step + can_get
                                if dest_step >=  step_length:   # destination a is ready
                                    result_aaa.append(a/step_length)    # normalize, so voice loudness don't change
                                    
                         
                        #convert to bytes again
                        
                        try:
                            #result_data = numpy.array(result_aaa,'<f').tobytes()
                            result_data = numpy.array(result_aaa,Settings.AUDIO_CONVERSION_FORMAT).tobytes()
                        except (ValueError):
                            self.log("process numpy.array(result_aaa,'<f').bytes(): ValueError")      
                            return
                        
                        # add missing 0 bytes for 
                        # length must be Settings.AUDIO_PERIOD_SIZE
                        remainder = len(result_data) % Settings.AUDIO_PERIOD_SIZE
                        if remainder is not 0:
                            self.log(str(remainder) + " over periodic size " + str(Settings.AUDIO_PERIOD_SIZE) + " correcting " )
                            len_zerobytes = Settings.AUDIO_PERIOD_SIZE - remainder
                            ba = bytearray(result_data)
                            for i in range(len_zerobytes):
                                ba.append(0)
                            result_data = bytes(ba)
                            remainder = len(result_data) % Settings.AUDIO_PERIOD_SIZE
                            if remainder is not 0:
                                self.log("Did not succeed to fix!")
                                self.log(str(remainder) + " over periodic size " + str(Settings.AUDIO_PERIOD_SIZE) )
                       
 
                        # for debug reasons play original and changed voice                           
                        data = result_data + data
                                
                        
                        
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: Sensation.SensationType.VoiceData self.outp.write(data)')
                    self.outp.write(data)
                    sensation.save()    #remember what we played
                    self.last_datalen = len(sensation.getData())
                    self.playbackTime = float(self.last_datalen)/float(Settings.AUDIO_RATE)
                    self.last_write_time = systemTime.time()
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: this Voice already played in this interval')
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got too old Voice to play')
        else:
            self.log(logLevel=Robot.LogLevel.Error, logStr='process: got sensation this robot can\'t process, NOT a Voice In or not running')
        self.log(logLevel=Robot.LogLevel.Detailed, logStr="self.running " + str(self.running))
        
    def getPlaybackTime(self):
        return self.playbackTime

if __name__ == "__main__":
    alsaAudioPlayback = AlsaAudioPlayback()
    alsaAudioPlayback.start()  