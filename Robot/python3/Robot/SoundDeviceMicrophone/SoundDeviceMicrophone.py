'''
Created on 03.09.2020
Updated on 09.09.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory for hearing,
implemented by sounddevice and need usb-microphone as hardware

'''
import time
import sounddevice as sd
import numpy
import math

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from AlsaAudio import Settings




class SoundDeviceMicrophone(Robot):
    """
     Implementation for out Voice sensation at Sensory level
     using ALSA-library and usb-microphone hardware
     
     Produces voices connected to present Item.names
    """
        
    SENSITIVITY=1.25
    AVERAGE_PERIOD=100.0                # used as period in seconds
    SHORT_AVERAGE_PERIOD=1.0            # used as period in seconds
    
    DEBUG_INTERVAL=60.0
    SLEEP_TIME=3.0                     # if nothing to do, sleep  
    DURATION = 0.1                     # record 0.1 sec                   


    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        print("We are in SoundDeviceMicrophone, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss = maxRss,
                       minAvailMem = minAvailMem,
                       location = location,
                       config = config)

        # from settings 
        # if device is set in settings, use it
        #otherwise use SourDevice default device that often work       
        self.device= self.config.getMicrophone()
        if len(self.device) > 0:
            sd.default.device = self.device
        else:
            self.device = sd.default.device
        sd.default.samplerate = Settings.AUDIO_RATE
        sd.default.channels = self.config.getMicrophoneChannels()
        sd.default.dtype = Settings.AUDIO_CONVERSION_FORMAT
        
        self.channels=self.config.getMicrophoneChannels()
        self.sensitivity=SoundDeviceMicrophone.SENSITIVITY
        self.rate = Settings.AUDIO_RATE

        self.average=self.config.getMicrophoneVoiceAvegageLevel()
        self.average_devider = float(self.rate) * SoundDeviceMicrophone.AVERAGE_PERIOD
        self.short_average=self.average
        self.short_average_devider = float(self.rate) * SoundDeviceMicrophone.SHORT_AVERAGE_PERIOD
        
        self.voice = False
        self.start_time=0.0
        self.logged = False
 
        self.log('device ' + str(self.device))

        self.running=False
        self.on=False
        
        self.debug_time=time.time()

        # buffer variables for voice        
        self.voice_data=None
        self.voice_l=0
                #self.rawInputStream = sd.RawInputStream(samplerate=Settings.AUDIO_RATE, blocksize=None, device=None, channels=self.channels, dtype='int16', latency=None, extra_settings=None, callback=None, finished_callback=None, clip_off=None, dither_off=None, never_drop_input=None, prime_output_buffers_using_stream_callback=None)
        self.rawInputStream = sd.RawInputStream(samplerate=Settings.AUDIO_RATE, channels=self.channels, dtype=Settings.AUDIO_CONVERSION_FORMAT)#'int16')


        
    def run(self):
        self.log(" run robot robot " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
#         voice_data=None
#         voice_l=0
        self.rawInputStream.start()
        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                # interrupt possible voice and put it to parent for processing
                self.putVoiceToParent()

                transferDirection, sensation = self.getAxon().get()
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
                self.process(transferDirection=transferDirection, sensation=sensation)
                sensation.detach(robot=self)
            else:
                if self.getMemory().hasPresence(): # listen is we have items that can speak
                    if not self.logged:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr=self.getMemory().presenceToStr() + " items speaking, sense")
                        self.logged = True
                    self.sense()
                else:
                    self.logged = False
                    # interrupt possible voice and put it to parent for processing
                    self.putVoiceToParent()
                    # nothing to do until we get itemp presems tp talk, so sleep for a while
                    time.sleep(SoundDeviceMicrophone.SLEEP_TIME)
                    

        self.log("Stopping SoundDeviceMicrophone")
        self.mode = Sensation.Mode.Stopping
        self.rawInputStream.stop()
        
        self.log(logLevel=Robot.LogLevel.Normal, logStr="self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)")
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
        # data is numpy array per period per array by channel of items set by sd.default.dtype
        # so we get intergers
        #data = sd.rec(int(self.DURATION * sd.default.samplerate))
        buf, overflowed  = self.rawInputStream.read(int(self.DURATION * sd.default.samplerate))
        data = bytes(buf)

        if not overflowed and len(data) > 0:
             # collect voice data as long we hear a voice and send it then
            if self.analyzeDataRaw(data):
                if self.voice_data is None:
                    self.voice_data = data
                    self.voice_l = len(data)
                else:
                    self.voice_data += data
                    self.voice_l += len(data)
            else:
                self.putVoiceToParent()

    def putVoiceToParent(self):
        if self.voice_data is not None:
            
            voiceSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
                                                   data=self.voice_data, locations=self.getLocations())
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: voice from " + self.getMemory().presenceToStr())
            for itemSensation in self.getMemory().getAllPresentItemSensations():
                itemSensation.associate(sensation=voiceSensation)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: self.getParent().getAxon().put(robot=self, sensation)")
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)
            self.voice_data=None
            self.voice_l=0
        
        '''
        Analyze voice sample
        Method:
        Keep long and short term average of sound level
        If sound level in short time average is above limit higher than
        long term average, we have a sound that has voice level higher
        than noise heard.
        
        If we have voice on longer than half of this sample, then whole sample is voice
        and we return True, otherwise False
        
        We could also analyse sound volume and sound rate, but yet implemented

        raw data version
        '''
    def analyzeDataRaw(self, data):

        # converti to int array        
        try:
            aaa = numpy.fromstring(data, dtype=Settings.AUDIO_CONVERSION_FORMAT)
        except (ValueError):
            self.log("analyzeData numpy.fromstring(data, dtype=dtype: ValueError")      
            return False
         
        minim=9999.0
        maxim=-9999.0
       
        # we don't care about channels
        # because we are calculating averages
        # and channels are decided to be even each other      
        voice_items=0
        i=0
        for a in aaa:
            square_a = float(a) * float(a)
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
            if time.time() > self.debug_time + SoundDeviceMicrophone.DEBUG_INTERVAL:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr="average " + str(self.average) + ' short_average ' + str(self.short_average))
                self.debug_time = time.time()
                    
            # TODO this can be much simpler
                
            if a > maxim:
                maxim = a
            if a < minim:
                minim = a
            if self.voice:
                if self.short_average <= self.sensitivity * self.average:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr="voice stopped at " + time.ctime() + ' ' + str(self.sum/self.n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average))
                    self.voice = False
                else:
                    self.sum += self.short_average
                    self.square_sum += square_a
                    self.n+=1.0
                    voice_items +=1
            else:
                if self.short_average > self.sensitivity * self.average:
                    self.start_time = time.time() - (float(len(aaa)-i)/self.rate)# arrays of arrays, so /self.channels # sound's start time is when we got sound data minus slots that are not in the sound
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr="voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average))
                    self.voice = True
                    self.sum=self.short_average
                    self.n=1.0
                    self.square_sum = square_a
            i += 1
       
        return  float(voice_items)/float(len(aaa)) >= 0.5
            
            
        '''
        numpy array version
        '''   
    def analyzeData(self, aaa):
#        self.log("analyzeData")
        # try that aa is floats
        # alsaaudio uses ints    
        minim=9999.0
        maxim=-9999.0
       
        # we don't care about channels
        # because we are calculating averages
        # and channels are decided to be even each other      
        voice_items=0
        i=0
        for aa in aaa:
            for a in aa:
                square_a = float(a) * float(a)
                self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
                self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
                if time.time() > self.debug_time + SoundDeviceMicrophone.DEBUG_INTERVAL:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr="average " + str(self.average) + ' short_average ' + str(self.short_average))
                    self.debug_time = time.time()
                    
                # TODO this can be much simpler
                
                if a > maxim:
                    maxim = a
                if a < minim:
                    minim = a
                if self.voice:
                    if self.short_average <= self.sensitivity * self.average:
                       self.log(logLevel=Robot.LogLevel.Detailed, logStr="voice stopped at " + time.ctime() + ' ' + str(self.sum/self.n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average))
                       self.voice = False
                    else:
                       self.sum += self.short_average
                       self.square_sum += square_a
                       self.n+=1.0
                       voice_items +=1
                else:
                    if self.short_average > self.sensitivity * self.average:
                       self.start_time = time.time() - (float(len(aaa)-i)/self.rate)# arrays of arrays, so /self.channels # sound's start time is when we got sound data minus slots that are not in the sound
                       self.log(logLevel=Robot.LogLevel.Detailed, logStr="voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average))
                       self.voice = True
                       self.sum=self.short_average
                       self.n=1.0
                       self.square_sum = square_a
                i += 1
       
        return  float(voice_items)/float(len(aaa)*self.channels) >= 0.5
    
    '''
    Convert read data to expected voice format
    We expect output to be PC; 2-channels,
    but we can have mono-mictophones that produce 1-channels data,
    which is ser in config file to be known,
    so only conversion supported now i 1-channel to 2-channels
    
    TODO This does not work
    We should check if get get array of array by chaannel if mono-mictophones
    '''
    
    
    def getVoiceData(self, data, dtype):
        if self.channels == 1 and Settings.AUDIO_CHANNELS == 2:
#             try:
#                 aaa = numpy.fromstring(data, dtype=dtype)
#             except (ValueError):
#                 self.log("getVoiceData numpy.fromstring(data, dtype=dtype: ValueError")      
#                 return None
#             
            ret_data=[]
            for a in aaa:
                ret_data.append(a)
                ret_data.append(a)
            data = ret_data
            
        try:
            return(numpy.array(object=data, dtype=Settings.AUDIO_CONVERSION_FORMAT, subok=True).tobytes())
        except (ValueError):
            self.log("getVoiceData numpy.array(ret_data,Settings.AUDIO_CONVERSION_FORMAT).tobytes(): ValueError") 
                 
        return None
    
  
            


if __name__ == "__main__":
    soundDeviceMicrophone = SoundDeviceMicrophone()
    soundDeviceMicrophone.start()  