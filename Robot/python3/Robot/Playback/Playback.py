'''
Created on 21.09.2020
Updated on 08.12.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for speaking
implemented by alsaaudio or SoundDevice and need usb-speaker hardware

Started to implement VoCoder voice  analyzing and synthesizing,
meaning that voice is first divided to frequency band components
which are played back. Original VoCoder voice sounded very robot like
and goal is to make same with this project.

The voiced speech of a typical adult male will have a fundamental frequency from 85 to 180 Hz,
and that of a typical adult female from 165 to 255 Hz. We start with theoretic
256 bands from 85 to 255 Hz and get band width (255-85)/255 Hz

Amplitude bands are also 255.


'''
import time as systemTime
import numpy
import math

from threading import Timer


from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from AlsaAudio import Settings

# prefer AlsaAidio before SoundDevice
IsAlsaAudio=True
#IsAlsaAudio=False

if IsAlsaAudio:
    try:
        print("Playback import alsaaudio")
        import alsaaudio
        from AlsaAudio import AlsaAudioNeededSettings
    except ImportError as e:
        print("Playback import import alsaaudio error " + str(e))
        IsAlsaAudio=False

if not IsAlsaAudio:
    try:
        print("Playback import sounddevice as sd")
        import sounddevice as sd
    except ImportError as e:
        print("Playback import sounddevice as sd error " + str(e))


class Playback(Robot):
    """
     Implementation for out Voice sensation at Sensory level
     using ALSA- or SoundDevice-library and speaker as hardware
    """
    
    COMMUNICATION_INTERVAL=15.0     # time window to history 
                                    # for sensations we communicate
    NORMAL_SPEAK_SPEED=1.0                                   
    WALLE_SPEAK_SPEED=1.25
    EVA_SPEAK_SPEED=1.5
    NORMALIZED_VOICE_LEVEL=300.0

    MIN_SPEACH_FREQUENCY=85.0
    MAX_SPEACH_FREQUENCY=255.0
    NUMBER_OF_BANDS = 128.0   
    FREQUENCY_BAND_WIDTH = (MAX_SPEACH_FREQUENCY-MIN_SPEACH_FREQUENCY)/NUMBER_OF_BANDS
    AMPLITUDE_BAND_WIDTH = NORMALIZED_VOICE_LEVEL*NORMALIZED_VOICE_LEVEL/NUMBER_OF_BANDS
    AVERAGE_PERIOD=0.0001               # used as period in seconds
    
    test_filenumber=0


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
        print("We are in Playback, not Robot")

        # from settings        
        self.device = self.config.getPlayback()
        self.isVoCode = self.config.isPlaybackFilterVoCode()
        self.isSaw = self.config.isPlaybackFilterSaw()
        self.isSineWave = self.config.isPlaybackFilterSineWave()
        
        self.channels = Settings.AUDIO_CHANNELS
        self.rate = Settings.AUDIO_RATE
        self.minWaweLength = Settings.AUDIO_RATE/self.MAX_SPEACH_FREQUENCY*2
        if IsAlsaAudio:
            self.format = AlsaAudioNeededSettings.AUDIO_FORMAT
        
        self.last_datalen=0
        self.last_write_time = systemTime.time()
        self.last_dataid=None
        
        #self.average_devider = float(self.rate * self.channels) * Playback.AVERAGE_PERIOD
        self.average_devider = float(self.rate) * Playback.AVERAGE_PERIOD
       
        
        if IsAlsaAudio:
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
                print ("Playback exception " + str(e))
                self.ok=False
        else:
            self.device= self.config.getPlayback()
            if len(self.device) > 0:
                sd.default.device = self.device
            else:
                self.device = sd.default.device
            sd.default.samplerate = Settings.AUDIO_RATE
            #sd.default.channels = self.config.getMicrophoneChannels()
            sd.default.dtype = Settings.AUDIO_CONVERSION_FORMAT
            self.ok=True
            self.log('device ' + str(self.device))
            self.rawOutputStream = sd.RawOutputStream(samplerate=Settings.AUDIO_RATE, channels=self.channels, dtype=Settings.AUDIO_CONVERSION_FORMAT)#'int16')
        

        # not yet running
        self.running=False
        
    '''
    SoundComponent
    '''
        
    class SoundComponent():
        def __init__(self,
                     duration,
                     frequency,
                     amplitude):
            self.duration = duration
            self.frequency = frequency
            self.amplitude = amplitude
            
        def setDuration(self,
                        duration):
            self.duration = duration
        def getDuration(self):
            return self.duration
        
        def setFrequency(self,
                        frequency):
            self.frequency = frequency
        def getFrequency(self):
            return self.frequency

        def setAmplitude(self,
                        amplitude):
            self.amplitude = amplitude
        def getAmplitude(self):
            return self.amplitude
                   
    '''
    AmplitudeValue
    Represents one value in series if digital sound values
    '''
        
    class AmplitudeValue():
        def __init__(self,
                     index,
                     amplitude):
            self.index = index
            self.amplitude = amplitude
            
        def setIndex(self,
                    index):
            self.index = index
        def getIndex(self):
            return self.index
        
        def setAmplitude(self,
                        amplitude):
            self.amplitude = amplitude
        def getAmplitude(self):
            return self.amplitude

    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
        # we can speak, but only if sensation is new enough
        elif self.ok and self.running and sensation.getSensationType() == Sensation.SensationType.Voice and sensation.getRobotType(robotMainNames=self.getMainNames()) == Sensation.RobotType.Muscle:
        # Test
        #elif self.ok and self.running and sensation.getSensationType() == Sensation.SensationType.Voice:
            if systemTime.time() - sensation.getTime() < Playback.COMMUNICATION_INTERVAL:
                if self.last_dataid != sensation.getDataId() or systemTime.time() - self.last_write_time > Playback.COMMUNICATION_INTERVAL:
                    self.last_dataid = sensation.getDataId()
                    #self.last_datalen = len(sensation.getData())
                    data = sensation.getData()
                    
                    # process voice
                    try:
                        aaa = numpy.fromstring(data, dtype=Settings.AUDIO_CONVERSION_FORMAT)
                    except (ValueError):
                        self.log("process numpy.fromstring(data, dtype=dtype: ValueError")      
                        return
                    # convert voice as kind if needed
                    aaa = self.changeVoiceByKind(kind=sensation.getKind(), aaa=aaa)
                    # normalize voice                 
                    # calculate average   
                    # no need to take care of  Settings.AUDIO_CHANNELS 
                    # because this is average of all channels            
                    sum=0.0 # try float
                    for a in aaa:
                        sum += abs(a) # We can get: Playback.py:136: RuntimeWarning: overflow encountered in long_scalars
                    average = sum/len(aaa)
                    multiplier = Playback.NORMALIZED_VOICE_LEVEL/average
                    
                    # normalize voice                 
                    i=0
                    while i < len(aaa):
                        aaa[i]=multiplier*aaa[i]
                        i += 1
                        
                    if self.isVoCode:
                        aaa = self.voCode(kind=sensation.getKind(), data=aaa)
                    if self.isSineWave:
                        aaa = self.sineWave(kind=sensation.getKind(), data=aaa)
                    if self.isSaw:
                        aaa = self.saw(kind=sensation.getKind(), data=aaa)
                    #           Usable
#                     aaa = aaa + self.saw(kind=sensation.getKind(), data=aaa) + self.voCode(kind=sensation.getKind(), data=aaa) +\
#                           self.sineWave(kind=sensation.getKind(), data=aaa) # self.voCode(kind=sensation.getKind(), data=aaa) 
#                     #aaa = self.voCode(kind=sensation.getKind(), data=aaa)
                    

                    #convert to bytes again                         
                    try:
                        #result_data = numpy.array(result_aaa,'<f').tobytes()
                        result_data = numpy.array(aaa,Settings.AUDIO_CONVERSION_FORMAT).tobytes()
                    except (ValueError):
                        self.log("process numpy.array(result_aaa,'<f').bytes(): ValueError")      
                        return
                         
                    # add missing 0 bytes for 
                    # length must be Settings.AUDIO_PERIOD_SIZE
                    remainder = len(result_data) % (Settings.AUDIO_PERIOD_SIZE*Settings.AUDIO_CHANNELS)
                    if remainder is not 0:
                        self.log(str(remainder) + " over periodic size " + str(Settings.AUDIO_PERIOD_SIZE*Settings.AUDIO_CHANNELS) + " correcting " )
                        len_zerobytes = (Settings.AUDIO_PERIOD_SIZE*Settings.AUDIO_CHANNELS - remainder)
                        ba = bytearray(result_data)
                        for i in range(len_zerobytes):
                            ba.append(0)
                        result_data = bytes(ba)
                        remainder = len(result_data) % (Settings.AUDIO_PERIOD_SIZE*Settings.AUDIO_CHANNELS)
                        if remainder is not 0:
                            self.log("Did not succeed to fix!")
                            self.log(str(remainder) + " over periodic size " + str(Settings.AUDIO_PERIOD_SIZE*Settings.AUDIO_CHANNELS) )
                        
  
                    # for debug reasons play original and changed voice                           
                    #data = result_data + data
                    #normal                        
                    data = result_data
                    
#                     data = self.voCode(kind=sensation.getKind(), data=data)
#                     
                    self.last_datalen = len(data) # this is real datalen
                                                        
                    if IsAlsaAudio:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: Sensation.SensationType.VoiceData self.outp.write(data)')
                        self.outp.write(data)
                    else:
                        self.rawOutputStream.start()
                        self.rawOutputStream.write(data)
                        self.rawOutputStream.stop()
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: Sensation.SensationType.VoiceData self.rawOutputStream.write(data')
                        
                    self.last_write_time = systemTime.time()                    
                    sensation.save()    #remember what we played
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: this Voice already played in this interval')
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got too old Voice to play')
        else:
            self.log(logLevel=Robot.LogLevel.Error, logStr='process: got sensation this robot can\'t process, NOT a Voice In or not running')
        self.log(logLevel=Robot.LogLevel.Detailed, logStr="self.running " + str(self.running))
        sensation.detach(robot=self) # finally release played sensation
        
    def changeVoiceByKind(self, kind, aaa):
        if kind == Sensation.Kind.WallE:
            aaa = self.changeVoiceSpeed(speed=self.WALLE_SPEAK_SPEED,aaa = aaa)
        elif kind == Sensation.Kind.Eva:
            aaa = self.changeVoiceSpeed(speed=self.EVA_SPEAK_SPEED,aaa = aaa)
        else:
            aaa = self.changeVoiceSpeed(speed=self.NORMAL_SPEAK_SPEED,aaa = aaa)
        return aaa

    def changeVoiceSpeed(self, speed, aaa):
        #step_length=speed
        #randowm
        step_length = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
        frequency_random_multiplier = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
        step_point = 0.0    # where we are in source as float
        ind_step_point = 0  # in which table index we are
        result_aaa=[]
        # while not end of source
        a={}
        while ind_step_point < len(aaa)/Settings.AUDIO_CHANNELS:
            for i in range(Settings.AUDIO_CHANNELS):
                a[i] = 0.0     # fill next a for destination
            dest_step=0.0
            ## TODO test variance in speed
            #step_length = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
            ## TODO test varance in speed
            while ind_step_point < len(aaa)/Settings.AUDIO_CHANNELS and\
                  dest_step <  step_length:
                # how much we we get on this source ind
                source_boundary = math.floor(step_point + 1.0)
                can_get = source_boundary - step_point
                if dest_step + can_get <= step_length:
                    for i in range(Settings.AUDIO_CHANNELS):
                        a[i] = a[i]+can_get*aaa[Settings.AUDIO_CHANNELS*ind_step_point+i]
                        # TODO Random
                        a[i] = a[i]*frequency_random_multiplier
                    step_point = float(source_boundary)
                    ind_step_point = ind_step_point+1   # source to next boundary
                else:
                    can_get = min(source_boundary - step_point, step_length- dest_step)
                    for i in range(Settings.AUDIO_CHANNELS):
                        a[i] =  a[i]+can_get*aaa[Settings.AUDIO_CHANNELS*ind_step_point+i]
                        # TODO Random
                        # TODO Random
                        a[i] = a[i]*frequency_random_multiplier
                    step_point = step_point + can_get  # forward in this source ind
                    if abs(step_point-source_boundary) < 0.001:
                        ind_step_point = ind_step_point+1 # source to next boundary
                                    
                dest_step = dest_step + can_get
                if dest_step >=  step_length:   # destination a is ready
                    for i in range(Settings.AUDIO_CHANNELS):
                        result_aaa.append(a[i]/step_length)    # normalize, so voice loudness don't change
        return result_aaa
    
    '''
    deprecated logic
    
    Started to implement VoCoder voice  analyzing and synthesizing,
    meaning that voice is first divided to frequency band components
    which are played back. Original VoCoder voice sounded very robot like
    and goal is to make same with this project.
    
    https://en.wikipedia.org/wiki/Vocoder
    
    The voiced speech of a typical adult male will have a fundamental frequency from 85 to 180 Hz,
    and that of a typical adult female from 165 to 255 Hz. We start with theoretic
    256 bands from 85 to 255 Hz and get band width (255-85)/255 Hz
    
    Amplitude bands are also 255.
    
    Seems that typical half wave is 5 steps, meaning much higher frequency,
    What if we just detect hald waves and produch half wawes from zeto to max
    to zero as sin wave, just rounding the voice.
    
    Parameters
    kind    kind of output voice
    data    array of integers PCM voice
    Return  array of integers PCM voice    
    '''
#     def voCode(self, kind, data):
#         
#         duration = 0.0
#         frequency = (self.MIN_SPEACH_FREQUENCY + self.MAX_SPEACH_FREQUENCY)/2.0
#         amplitude = self.NORMALIZED_VOICE_LEVEL
#         
#         last_duration = 0.0
#         last_frequency = frequency
#         last_amplitude = amplitude 
#         
#         last_a = 0.0
# 
#         wave_going_up = True
#         wave_going = True
#         
#         #random
# #         step_length = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
# #         frequency_random_multiplier = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
# #         step_point = 0.0    # where we are in source as float
# #         ind_step_point = 0  # in which table index we are
#         result_data=[]
#         component_period_length = 0
#         wave_period_length = 0
#         
#         # handle as 1 channel voice
#         # meaning that if 2-channels in use, then we converts left and rigth channels as average
#         # because Robots will speak as mono until we have reason to speak as stereo
#         
#         i=0
#         up_a = 0
#         down_a = 0
#         up_i = 0
#         down_i = 0
#         
#         set_previous_up_a=False
#         previous_up_a = 0
#         set_previous_down_a=False
#         previous_down_a = 0
#         previous_up_i = 0
#         previous_down_i = 0
#         
#         #for a in data:
#         while i < len(data):
#             if self.channels > 1:
#                 sum=0
#                 for j in range(0,self.channels):
#                     sum = sum + data[i]
#                     i = i+1
#                 a = sum/self.channels
#             else:
#                 a=data[i]
#                 i = i+1
#             #square_a = float(a) * float(a)
#             #amplitude = math.sqrt(( (amplitude * amplitude * (self.average_devider - 1.0))  + square_a)/self.average_devider)
#             amplitude = ( (amplitude * (self.average_devider - 1.0)  + abs(a))/self.average_devider)
#             wave_period_length = wave_period_length+1
#             # todo we should look wider
#             if wave_going_up:
#                 # highest point
#                 if a > 0 and a > up_a:
#                     set_previous_up_a = True
#                     up_a = a
#                     up_i = i
#                 # if we are in candidate high point, then we know last half wave
#                 # from previous_up_i to previous_down_i
# #                 if a > 0 and a < last_a:
#                 if a < last_a:
#                     wave_going_up = False
#                     wave_going = False
#                     # if we are in the candidate high point, then we know last half wave
#                     # we know now previous lowest point if not yet marked
#                     if a > 0 and set_previous_down_a:
#                         previous_down_a = down_a
#                         previous_down_i = down_i
#                         down_a = 0
#                         set_previous_down_a = False
#                         # from previous_up_i to previous_down_i
#                         if previous_up_a >= 0 and previous_down_a < 0:
#                             #we know now half wave period length
#                             #we know now half wave as line
#                             step = float(previous_up_a-previous_down_a)/float(previous_down_i-previous_up_i)
#                             step_i=0
#                             for j in range(previous_up_i, previous_down_i):
#                                 result_a = previous_up_a - (float(step_i) * step)
#                                 step_i = step_i+1
#                                 for si in range(self.channels):
#                                     result_data.append(int(result_a))
# #                             wave_period_length = (previous_down_i - previous_up_i) * 2
# #                             # we can calculate sliding average
# #                             f = (float(self.rate))/(float(wave_period_length))
# #                             frequency = (frequency * (self.average_devider - 1.0)  + f)/self.average_devider
#                             previous_up_a = 0 # we should mark that we have raported lat hald wave, down
#                                                 # when we go up but is this the way?
#                             set_previous_down_a = False
#             else:
#                 # lowest point
#                 if a < 0 and a < down_a:
#                     set_previous_down_a=True
#                     down_a = a
#                     down_i = i
#                 if a > last_a:
#                     wave_going_up = True
#                     wave_going = False
#                     # if we are in the candidate low point, then we know last half wave
#                     # we know now previous lowest point if not yet marked
#                     if a < 0 and set_previous_up_a:
#                         previous_up_a = up_a
#                         previous_up_i = up_i
#                         up_a = 0
#                         set_previous_up_a = False
#                         # from previous_up_i to previous_down_i
#                         if previous_down_a <= 0 and previous_up_a > 0:
#                             #we know now half wave period length
#                             #we know now half wave as line
#                             step = float(previous_down_a-previous_up_a)/float(previous_up_i-previous_down_i)
#                             step_i=0
#                             for j in range(previous_down_i, previous_up_i):
#                                 result_a = previous_down_a - (float(step_i) * step)
#                                 step_i = step_i+1
#                                 for si in range(self.channels):
#                                     result_data.append(int(result_a))
#                                     #pass
# #                             wave_period_length = (previous_down_i - previous_up_i) * 2
# #                             # we can calculate sliding average
# #                             f = (float(self.rate))/(float(wave_period_length))
# #                             frequency = (frequency * (self.average_devider - 1.0)  + f)/self.average_devider
#                             previous_down_a = 0 # we should mark that we have reported lat hald wave, down
#                                                 # when we go up but is this the way?
#                             set_previous_up_a = False
# 
# #                 
# #                 
# #                 else:
# #                     if a < 0 and a < down_a:
# #                         down_a = a
# #                         down_i = i
# #                 if a < 0 and a > last_a:
# #                     wave_going_up = True
# # #                    wave_going = False
#             last_a = a
# #                    
# #             if not wave_going:
# # #                f = (float(self.rate) * float(self.channels))/(float(wave_period_length) * 2.0)
# #                 f = (float(self.rate))/(float(wave_period_length))
# #                 frequency = (frequency * (self.average_devider - 1.0)  + f)/self.average_devider
# #                 wave_going = True
# #                 wave_period_length = 0
# 
# #             component_period_length = component_period_length +1
# #             last_a = a
# # #            if wave_period_length >= self.minWaweLength and\
# #             if abs(amplitude-last_amplitude) > self.AMPLITUDE_BAND_WIDTH or\
# #                abs(frequency-last_frequency) > self.FREQUENCY_BAND_WIDTH:
# #                 
# #                # TODO generate synthetized voice
# #                 if abs(amplitude -last_amplitude) > self.AMPLITUDE_BAND_WIDTH:
# #                    self.log(logLevel=Robot.LogLevel.Normal, logStr='voCode: amplitude: component_period_length {} abs((amplitude {} - last_amplitude {}) > self.AMPLITUDE_BAND_WIDTH {}'.format(component_period_length, amplitude, last_amplitude, self.AMPLITUDE_BAND_WIDTH))
# #                 if abs(frequency - last_frequency) > self.FREQUENCY_BAND_WIDTH:
# #                    self.log(logLevel=Robot.LogLevel.Normal, logStr='voCode: frequency: component_period_length {} abs(frequency {} - last_frequency {}) > self.FREQUENCY_BAND_WIDTH {}'.format(component_period_length, frequency, last_frequency, self.FREQUENCY_BAND_WIDTH))
# # 
# #                 #duration = float(component_period_length) / (float(self.rate) * float(self.channels)) # seconds
# #                 duration = float(component_period_length) / (float(self.rate)) # seconds
# #                 
# # #                 length = 2.5  # in seconds
# # #                 samplerate = 44100  # in Hz
# # #                 frequency = 440 #440  # an A4
# #                 
# #                 # pure voice
# #                 x = numpy.linspace(0, duration * 2 * numpy.pi, int(component_period_length))
# #                 sinewave_data = numpy.sin(frequency * x)#.reshape((1, -1))
# #                 # get nd-array 0-1
# #                 # get intergers
# #                 for s in sinewave_data:
# #                     for si in range(self.channels):
# #                         result_data.append(int(s*amplitude))
# #                 
# #                 
# #                 last_frequency = frequency
# #                 last_amplitude = amplitude
# #                 self.log(logLevel=Robot.LogLevel.Normal, logStr='voCode: component_period_length {} duration {} frequency {} amplitude {}'.format(component_period_length, duration, frequency, amplitude))
# #                 component_period_length = 0
#                             
#         #return data + result_data
#         # pure voice
# #         duration = float(len(data))/(self.channels*self.rate)
# #         x = numpy.linspace(0, duration * 2 * numpy.pi, int(len(data)/self.channels))
# #         sinewave_data = numpy.sin(frequency * x)#.reshape((1, -1))
# #         for s in sinewave_data:
# #             for si in range(self.channels):
# #                 result_data.append(int(s*600))
# #        return data + result_data
#         return result_data

    '''
    VoCoder voice  analyzing and synthesizing,
    
    meaning that voice is first divided to frequency band components
    which are played back. Original VoCoder voice sounded very robot like
    and goal is to make same with this project.
    
    https://en.wikipedia.org/wiki/Vocoder
    
    The voiced speech of a typical adult male will have a fundamental frequency from 85 to 180 Hz,
    and that of a typical adult female from 165 to 255 Hz. We start with theoretic
    256 bands from 85 to 255 Hz and get band width (255-85)/255 Hz
    
    Amplitude bands are also 255.
    
    This version simply changes amplitudes to middle of band widths,
    removing details of voice, hoping that voice come more robot-like.
    
    Parameters
    kind    kind of output voice
    data    array of integers PCM voice
    Return  array of integers PCM voice
    
    
    '''
    def voCode(self, kind, data):
        
        result_data=[]
        
        for a in data:
            if a > 0.0:
                a_channnel_number = math.floor((a-(self.AMPLITUDE_BAND_WIDTH/2))/self.AMPLITUDE_BAND_WIDTH)
                new_a = ((a_channnel_number)*self.AMPLITUDE_BAND_WIDTH)
            else:
                a_channnel_number = math.floor((a+(self.AMPLITUDE_BAND_WIDTH/2))/self.AMPLITUDE_BAND_WIDTH)
                new_a = ((a_channnel_number)*self.AMPLITUDE_BAND_WIDTH)
            result_data.append(new_a)
#                 result_data.append(int(s*600))
#        return data + result_data
        return result_data
    
#----------------------------------------------------------------------------

    '''    
    getAmplitudes gives us high and low points of waves of the voice
    
    Parameters
    data    array of integers PCM voice
    Return  array of class AmplitudeValue instances
    
    
    '''
    def getAmplitudeValues(self, data):
        
        self.test_filenumber = self.test_filenumber+1
        f_original = open('/tmp/original_{}.csv'.format(self.test_filenumber),'w')
        f_amplitude = open('/tmp/amplitude_{}.csv'.format(self.test_filenumber),'w')
        
        last_a = 0.0

        wave_going_up = True
        wave_going = True
        
        amplitudeValues=[]
        
        # handle as 1 channel voice
        # meaning that if 2-channels in use, then we converts left and rigth channels as average
        # because Robots will speak as mono until we have reason to speak as stereo
        
        i=0
        up_a = 0
        down_a = 0
        up_i = 0
        down_i = 0
        
        set_previous_up_a=False
        previous_up_a = 0
        set_previous_down_a=False
        previous_down_a = 0
        previous_up_i = 0
        previous_down_i = 0
 
        amplitudeValues.append(Playback.AmplitudeValue(amplitude=0, index=0))       
        #for a in data:
        while i < len(data):
            if self.channels > 1:
                sum=0
                for j in range(0,self.channels):
                    sum = sum + data[i]
                    i = i+1
                a = sum/self.channels
                f_original.write('{}\t{}\n'.format(i/2,a))
            else:
                a=data[i]
                i = i+1
            if wave_going_up:
                # highest point
                if a > 0 and a > up_a:
                    set_previous_up_a = True
                    up_a = a
                    up_i = i
                # if we are in candidate high point, then we know last half wave
                # from previous_up_i to previous_down_i
#                 if a > 0 and a < last_a:
                if a < last_a:
                    wave_going_up = False
                    wave_going = False
                    # if we are in the candidate high point, then we know last half wave
                    # we know now previous lowest point if not yet marked
                    if a > 0 and set_previous_down_a:
                        amplitudeValues.append(Playback.AmplitudeValue(amplitude=down_a, index=int(down_i/self.channels)))       
                        down_a = 0
                        set_previous_down_a = False
            else:
                # lowest point
                if a < 0 and a < down_a:
                    set_previous_down_a=True
                    down_a = a
                    down_i = i
                if a > last_a:
                    wave_going_up = True
                    wave_going = False
                    # if we are in the candidate low point, then we know last half wave
                    # we know now previous lowest point if not yet marked
                    if a < 0 and set_previous_up_a:
                        amplitudeValues.append(Playback.AmplitudeValue(amplitude=up_a, index=int(up_i/self.channels)))       
                        up_a = 0
                        set_previous_up_a = False
            last_a = a
                        
        return amplitudeValues

    '''    
    saw
    Converts sound to saw-waves,
    meaning that we find of high and low points of waves and simplify sound to stright lines
    between those up and down points to make sound Robot-like.
    
    Parameters
    kind    kind of output voice
    data    array of integers PCM voice
    Return  array of integers PCM voice
    
    
    '''
    def saw(self, kind, data):
        
        amplitudeValues=self.getAmplitudeValues(data=data)
        result_data=[]
        
                        
        # now we know all high and low points, Let us to make saw curve from it
        previousAmplitudeValue = None
        for amplitudeValue in amplitudeValues:
            if previousAmplitudeValue is not None:  
                step = float(previousAmplitudeValue.getAmplitude()-amplitudeValue.getAmplitude())/float(amplitudeValue.getIndex()-previousAmplitudeValue.getIndex())
                step_i=0
                for j in range(previousAmplitudeValue.getIndex(), amplitudeValue.getIndex()):
                    result_a = previousAmplitudeValue.getAmplitude() - (float(step_i) * step)
                    step_i = step_i+1
                    for si in range(self.channels):
                        result_data.append(int(result_a))
            previousAmplitudeValue = amplitudeValue
        #return data + result_data
        return result_data

    '''    
    sineWave
    Converts sound to sine-waves,
    meaning that we find of high and low points of waves and simplify sound to sine waves
    between those up and down points to make sound Robot-like.
    
    Parameters
    kind    kind of output voice
    data    array of integers PCM voice
    Return  array of integers PCM voice
    
    
    '''
    def sineWave(self, kind, data):
        
        amplitudeValues=self.getAmplitudeValues(data=data)
        result_data=[]
        
                        
        # now we know all high and low points, Let us to make sine curve from it
        previousAmplitudeValue = None
        previousPositiveAmplitudeValue = None
        previousNegativeAmplitudeValue = None
        for amplitudeValue in amplitudeValues:
            #check
            if previousAmplitudeValue is not None:
#                 if previousAmplitudeValue.getAmplitude() >= 0.0:
#                     assert(amplitudeValue.getAmplitude() < 0.0)
#                     assert(amplitudeValue.getIndex() > previousAmplitudeValue.getIndex())
#                 else:
#                     assert(amplitudeValue.getAmplitude() >= 0.0)
                #if we have two positive amplitude values
                # and between then negative amplitude value
                if amplitudeValue.getAmplitude() >= 0.0 and previousPositiveAmplitudeValue is not None and\
                   previousNegativeAmplitudeValue is not None:
                    # we can calculate mean of these amplitudes
                    meanAmplitude = (amplitudeValue.getAmplitude() + previousPositiveAmplitudeValue.getAmplitude() - previousNegativeAmplitudeValue.getAmplitude())/3.0
                    # and length of this sine wave
                    length = amplitudeValue.getIndex() - previousPositiveAmplitudeValue.getIndex()
#                 length = 2.5  # in seconds
#                 samplerate = 44100  # in Hz
#                 frequency = 440 #440  # an A4
                 
                    # pure voice
                    x = numpy.linspace(0, 2 * numpy.pi, length)
                    sinewave_data = numpy.sin(x)#.reshape((1, -1))
                    # get nd-array 0-1
                    # get intergers
                    for s in sinewave_data:
                        for si in range(self.channels):
                            result_data.append(s*meanAmplitude)
                            
                if amplitudeValue.getAmplitude() >= 0.0:
                    previousPositiveAmplitudeValue = amplitudeValue
                else:
                    previousNegativeAmplitudeValue = amplitudeValue
                
                    
                    # 
            previousAmplitudeValue = amplitudeValue
        #return data + result_data
        return result_data

#----------------------------------------------------------------------------
    
        
    def getPlaybackTime(self, datalen=None):
        if datalen == None:
            datalen = self.last_datalen
            
        return float(datalen)/(float(Settings.AUDIO_RATE*Settings.AUDIO_CHANNELS))
    
    def getRandom(base, randomMin, randomMax):
        return base + random.uniform(randomMin, randomMax)


if __name__ == "__main__":
    playback = Playback()
    playback.start()  