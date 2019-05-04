'''
Created on 01.05.2019
Updated on 04.05.2019

@author: reijo.korhonen@gmail.com

This class is low level sensory for hearing,
implemented by alasaaudio and need usb-mictophone as hardware

'''
import sys
import time
import getopt
import alsaaudio
import numpy
import math

from threading import Thread
from threading import Timer

#import sys
#sys.path.append('/home/reijo/git/Wall-E/Wall-E/Robot')

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

import sys
#from builtins import None
#import parent.file1



class AlsaAudioMicrophone(Robot):
    """
     Implemenation for out Voice sensation at Sensory level
     using ALSA-library amd microphone hardwate
    """
    
    CONVERSION_FORMAT='<i2'

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
        print("We are in AlsaAudioMicrophone, not Robot")

        # from settings        
        self.device= self.config.getMicrophone()
        self.channels=1
        self.sensitivity=1.25
        self.rate = 44100
        self.format = alsaaudio.PCM_FORMAT_S16_LE
        self.average=self.config.getMicrophoneVoiceAvegageLevel()
        self.average_devider = float(self.rate) * 100.0
        self.short_average=self.average
        self.short_average_devider = float(self.rate) * 1.0
        
        self.voice = False
        self.start_time=0.0

        self.inp = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, device=self.device)
        # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
        self.inp.setchannels(self.channels)
        self.inp.setrate(self.rate)
        self.inp.setformat(self.format)
        self.inp.setperiodsize(2048) #32 160
 
        self.log('cardname ' + self.inp.cardname())

        self.running=False
        self.on=False
        
        self.debug_time=time.time()
        
    def run(self):
        self.log(" Starting robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())      
        
        # starting other threads/senders/capabilities
        
        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        voice_data=None
        voide_l=0
        while self.running:
            # blocking read data from device
            #print "reading " + self.name
            l, data = self.inp.read() # l int, data bytes
            if l > 0:
                # connect voide sate as long we hear a voice and send it then
                if self.analyzeData(l, data, self.CONVERSION_FORMAT):
                    if voice_data is None:
                        voice_data = data
                        voice_l = l
                    else:
                       voice_data += data
                       voice_l += l
                else:
                    if voice_data is not None:
                        self.log("self.outAxon.put(sensation)")
                        sensation = Sensation.create(sensationType = Sensation.SensationType.VoiceData, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, voiceSize=voice_l, voiceData=voice_data)
                        self.outAxon.put(sensation)
                        voice_data=None
                        voide_l=0

        self.mode = Sensation.Mode.Stopping
        self.log("Stopping AlsaAudioMicrophone")
        self.log("self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)")
        self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)
    

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log("run ALL SHUT DOWN")
        
        '''
        Analyze voice sample
        Method:
        Keep long and short term average of sound level
        If sound level in short time average is above limit higher than
        long term average, we have a sound that has voice level higher
        than noise heard.
        
        If we have voice on longer than half of this samplöe, then whole samle is voice
        and we return True, otherwise False
        
        We could also analyse sound volume and sound rate, but yet implemented
        '''
        
    def analyzeData(self, l, data, dtype):
        sensation = None
#        self.log("analyzeData")      
        minim=9999
        maxim=-9999
       
        try:
            aaa = numpy.fromstring(data, dtype=dtype)
        except (ValueError):
            self.log("analyzeData numpy.fromstring(data, dtype=dtype: ValueError")      
            return None
        length = len(aaa)
        voice_items=0
        
        i=0
        for a in aaa:
            square_a = float(a) * float(a)
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
            if time.time() > self.debug_time + 60.0:
                self.log("average " + str(self.average) + ' short_average ' + str(self.short_average))
                self.debug_time = time.time()
                
            # TODO this can be much simpler
            
            if a > maxim:
                maxim = a
            if a < minim:
                minim = a
            if self.voice:
                if self.short_average <= self.sensitivity * self.average:
                   self.log("voice stopped at " + time.ctime() + ' ' + str(self.sum/self.n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average))
                   self.voice = False
                else:
                   self.sum += self.short_average
                   self.square_sum += square_a
                   self.n+=1.0
                   voice_items +=1
            else:
                if self.short_average > self.sensitivity * self.average:
                   self.start_time = time.time() - (float(len(aaa)-i)/self.rate) # sound's start time is when we got sound data minus slots that are not in the sound
                   self.log( "voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average))
                   self.voice = True
                   self.sum=self.short_average
                   self.n=1.0
                   self.square_sum = square_a
                   voice_items +=1
                  
            i += 1
        
        return  float(voice_items)/length >= 0.5
  
            


if __name__ == "__main__":
    alsaAudioMicrophone = AlsaAudioMicrophone()
    alsaAudioMicrophone.start()  