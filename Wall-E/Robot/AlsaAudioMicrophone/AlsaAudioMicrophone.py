'''
Created on 01.05.2019
Updated on 08.06.2019

@author: reijo.korhonen@gmail.com

This class is low level sensory for hearing,
implemented by alasaaudio and need usb-microphone as hardware

'''
import time
import alsaaudio
import numpy
import math

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation



class AlsaAudioMicrophone(Robot):
    """
     Implementation for out Voice sensation at Sensory level
     using ALSA-library and microphone hardware
    """
    
    CONVERSION_FORMAT='<i2'
    CHANNELS=1
    SENSITIVITY=1.25
    RATE = 44100
    FORMAT = alsaaudio.PCM_FORMAT_S16_LE
    AVERAGE_PERIOD=100.0                # used as period in seconds
    SHORT_AVERAGE_PERIOD=1.0             # used as period in seconds
    
    DEBUG_INTERVAL=60.0


    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0):
        print("We are in AlsaAudioMicrophone, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)

        # from settings        
        self.device= self.config.getMicrophone()
        self.channels=AlsaAudioMicrophone.CHANNELS
        self.sensitivity=AlsaAudioMicrophone.SENSITIVITY
        self.rate = AlsaAudioMicrophone.RATE
        self.format = AlsaAudioMicrophone.FORMAT
        self.average=self.config.getMicrophoneVoiceAvegageLevel()
        self.average_devider = float(self.rate) * AlsaAudioMicrophone.AVERAGE_PERIOD
        self.short_average=self.average
        self.short_average_devider = float(self.rate) * AlsaAudioMicrophone.SHORT_AVERAGE_PERIOD
        
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

        # buffer variables for voice        
        self.voice_data=None
        self.voice_l=0

        
    def run(self):
        self.log(" Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=True
                
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
                self.process(transferDirection=transferDirection, sensation=sensation)
            else:
                self.sense()
#             #otherwise we have time to read our senses
#                 # blocking read data from device
#                 #print "reading " + self.name
#                 l, data = self.inp.read() # l int, data bytes
#                 if l > 0:
#                     # collect voice data as long we hear a voice and send it then
#                     if self.analyzeData(l, data, self.CONVERSION_FORMAT):
#                         if voice_data is None:
#                             voice_data = data
#                             voice_l = l
#                         else:
#                            voice_data += data
#                            voice_l += l
#                     else:
#                         if voice_data is not None:
#                             self.log("self.getParent().getAxon().put(sensation)")
#                             sensation = Sensation.create(connections=[], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, data=voice_data)
#                             self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation) # or self.process
#                             voice_data=None
#                             voice_l=0

        self.log("Stopping AlsaAudioMicrophone")
        self.mode = Sensation.Mode.Stopping
        self.log("self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)")
        self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)
       
        self.log("run ALL SHUT DOWN")
        
    '''
    We can sense
    We are Sense type Robot
    '''        
    def canSense(self):
        return True 
     
    '''
    We can sense
    We are Sense type Robot
    '''        
    def sense(self):
        # blocking read data from device
        #print "reading " + self.name
        l, data = self.inp.read() # l int, data bytes
        if l > 0:
            # collect voice data as long we hear a voice and send it then
            if self.analyzeData(l, data, self.CONVERSION_FORMAT):
                if self.voice_data is None:
                    self.voice_data = data
                    self.voice_l = l
                else:
                    self.voice_data += data
                    self.voice_l += l
            else:
                if self.voice_data is not None:
                    self.log("self.getParent().getAxon().put(sensation)")
                    # put direction out (heard voice) to the parent Axon going up to main Robot
                    sensation = Sensation.create(connections=[], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, data=self.voice_data)
                    self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation) # or self.process
                    self.voice_data=None
                    self.voice_l=0

        
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
            if time.time() > self.debug_time + AlsaAudioMicrophone.DEBUG_INTERVAL:
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