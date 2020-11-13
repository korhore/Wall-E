'''
Created on 21.09.2020
Updated on 13.33.2020

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

    NUMBER_OF_BANDS = 256.0   
    FREQUENCY_BAND_WIDTH = (256.0-85.0)/NUMBER_OF_BANDS
    AMPLITUDE_BAND_WIDTH = 2.0*NORMALIZED_VOICE_LEVEL/NUMBER_OF_BANDS
    AVERAGE_PERIOD=0.01               # used as period in seconds


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
        self.device= self.config.getPlayback()
        self.channels=Settings.AUDIO_CHANNELS
        self.rate = Settings.AUDIO_RATE
        if IsAlsaAudio:
            self.format = AlsaAudioNeededSettings.AUDIO_FORMAT
        
        self.last_datalen=0
        self.last_write_time = systemTime.time()
        self.last_dataid=None
        
        self.average_devider = float(self.rate * self.channels) * Playback.AVERAGE_PERIOD
       
        
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
                   
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
        # we can speak, but only if sensation is new enough
        elif self.ok and self.running and sensation.getSensationType() == Sensation.SensationType.Voice and sensation.getRobotType() == Sensation.RobotType.Muscle:
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
                    
                    aaa = self.voCode(kind=sensation.getKind(), data=aaa)
                    

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
    
    def voCode(self, kind, data):
        
        # OOPSA data is bytes, not array
        
        duration = 0.0
        frequency = 0.0
        amplitude = 0.0
        
        last_duration = 0.0
        last_frequency = 0.0
        last_amplitude = 0.0
        last_a = 0.0
        wave_going_up = True
        wave_going = True
        
        #random
#         step_length = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
#         frequency_random_multiplier = Sensation.getRandom(base=speed, randomMin=-(self.NORMAL_SPEAK_SPEED/7.0), randomMax=+(self.NORMAL_SPEAK_SPEED/7))
#         step_point = 0.0    # where we are in source as float
#         ind_step_point = 0  # in which table index we are
        result_data=[]
        component_period_length = 0
        wave_period_length = 0
        
        for a in data:
            square_a = float(a) * float(a)
            amplitude = math.sqrt(( (amplitude * amplitude * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            wave_period_length = wave_period_length+1
            if wave_going_up:
                if a < last_a:
                    wave_going_up = False
                    wave_going = False
            else:
                 if a > last_a:
                    wave_going_up = True
                    wave_going = False
            last_a = a
                   
            if not wave_going:
                f = (float(self.rate) * float(self.channels))/(float(wave_period_length) * 2.0)
                frequency = (frequency * (self.average_devider - 1.0)  + f)/self.average_devider
                wave_going = True
                wave_period_length = 0

            component_period_length = component_period_length +1
            if abs(amplitude-last_amplitude) > self.AMPLITUDE_BAND_WIDTH or\
               abs(frequency-last_frequency) > self.FREQUENCY_BAND_WIDTH:
                
               # TODO generate synthetized voice

                duration = float(component_period_length) / (float(self.rate) * float(self.channels)) # seconds
                last_frequency = frequency
                last_amplitude = amplitude
                self.log(logLevel=Robot.LogLevel.Normal, logStr='voCode: component_period_length {} duration {} frequency {} amplitude {}'.format(component_period_length, duration, frequency, amplitude))
                component_period_length = 0
                            
        return data
    
        
    def getPlaybackTime(self, datalen=None):
        if datalen == None:
            datalen = self.last_datalen
            
        return float(datalen)/(float(Settings.AUDIO_RATE*Settings.AUDIO_CHANNELS))
    
    def getRandom(base, randomMin, randomMax):
        return base + random.uniform(randomMin, randomMax)


if __name__ == "__main__":
    playback = Playback()
    playback.start()  