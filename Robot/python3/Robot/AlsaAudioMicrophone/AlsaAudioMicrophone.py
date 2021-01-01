'''
Created on 01.05.2019
Updated on 10.04.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory for hearing,
implemented by alsaaudio and need usb-microphone as hardware

'''
import time
import alsaaudio
import numpy
import math

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from AlsaAudio import Settings
from AlsaAudio import AlsaAudioNeededSettings




class AlsaAudioMicrophone(Robot):
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
        print("We are in AlsaAudioMicrophone, not Robot")
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
        self.device= self.config.getMicrophone()
        #self.channels=Settings.AUDIO_CHANNELS
        self.channels=self.config.getMicrophoneChannels()
        self.sensitivity=AlsaAudioMicrophone.SENSITIVITY
        self.rate = Settings.AUDIO_RATE
        self.format = AlsaAudioNeededSettings.AUDIO_FORMAT
        self.average=self.config.getMicrophoneVoiceAvegageLevel()
        self.average_devider = float(self.rate) * AlsaAudioMicrophone.AVERAGE_PERIOD
        self.short_average=self.average
        self.short_average_devider = float(self.rate) * AlsaAudioMicrophone.SHORT_AVERAGE_PERIOD
        
        self.voice = False
        self.start_time=0.0
        self.logged = False

        self.inp = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, device=self.device)
        # Set attributes: Stereo, 44100 Hz, 16 bit little endian samples
        self.inp.setchannels(self.channels)
        self.inp.setrate(self.rate)
        self.inp.setformat(self.format)
        self.inp.setperiodsize(Settings.AUDIO_PERIOD_SIZE)
 
        self.log('cardname ' + self.inp.cardname())

        self.running=False
        self.on=False
        
        self.debug_time=time.time()

        # buffer variables for voice        
        self.voice_data=None
        self.voice_l=0

        
    def run(self):
        self.log(" run robot robot " + self.getName() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
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
                # interrupt voice and put it to parent for processing
                self.putVoiceToParent()

                transferDirection, sensation = self.getAxon().get()
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
#                 if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemoryType() == Sensation.MemoryType.Working and\
#                    sensation.getRobotType(robotMainNames=self.getMainNames()) == Sensation.RobotType.Sense: 
#                     self.tracePresents(sensation)
#                 else:
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
#                     # TODO as a test we sense
                    #self.log(logLevel=Robot.LogLevel.Verbose, logStr=str(len(self.getMemory().presentItemSensations)) + " items NOT speaking, sense anyway")
                    #self.sense()
                    #self.log(logLevel=Robot.LogLevel.Normal, logStr="no items speaking, sleeping " + str(AlsaAudioMicrophone.SLEEP_TIME))
                    #time.sleep(AlsaAudioMicrophone.SLEEP_TIME)
                    

        self.log("Stopping AlsaAudioMicrophone")
        self.mode = Sensation.Mode.Stopping
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
        #print "reading " + self.name
        l, data = self.inp.read() # l int, data bytes
        if l > 0:
            # collect voice data as long we hear a voice and send it then
            if self.analyzeData(l, data, Settings.AUDIO_CONVERSION_FORMAT):
                if self.voice_data is None:
                    self.voice_data = data
                    self.voice_l = l
                else:
                    self.voice_data += data
                    self.voice_l += l
            else:
                self.putVoiceToParent()

    def putVoiceToParent(self):
        if self.voice_data is not None:
            # put robotType out (heard voice) to the parent Axon going up to main Robot
            # connected to present Item.names
            voiceSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
                                                   data=self.getVoiceData(data=self.voice_data, dtype=Settings.AUDIO_CONVERSION_FORMAT), locations=self.getLocations())
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
            return False
 
        # we don't care about channels
        # because we are calculating averages
        # and channels are decided to be even each other      
        voice_items=0
        i=0
        for a in aaa:
            square_a = float(a) * float(a)
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
            if time.time() > self.debug_time + AlsaAudioMicrophone.DEBUG_INTERVAL:
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
                   self.start_time = time.time() - (float(len(aaa)-i)/self.rate)/self.channels # sound's start time is when we got sound data minus slots that are not in the sound
                   self.log(logLevel=Robot.LogLevel.Detailed, logStr="voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average))
                   self.voice = True
                   self.sum=self.short_average
                   self.n=1.0
                   self.square_sum = square_a
            i += 1
       
        return  float(voice_items)/float(len(aaa)) >= 0.5
    
    '''
    Convert read data to expected voice format
    We expect output to be PC; 2-channels,
    but we can have mono-mictophones that produce 1-channels data,
    which is ser in config file to be known,
    so only conversion supported now i 1-channel to 2-channels
    '''
    
    
    def getVoiceData(self, data, dtype):
        if self.channels == 1 and Settings.AUDIO_CHANNELS == 2:
            try:
                aaa = numpy.fromstring(data, dtype=dtype)
            except (ValueError):
                self.log("getVoiceData numpy.fromstring(data, dtype=dtype: ValueError")      
                return None
            
            ret_data=[]
            for a in aaa:
                ret_data.append(a)
                ret_data.append(a)
                
            try:
                return(numpy.array(ret_data,Settings.AUDIO_CONVERSION_FORMAT).tobytes())
            except (ValueError):
                self.log("getVoiceData numpy.array(ret_data,Settings.AUDIO_CONVERSION_FORMAT).tobytes(): ValueError")      
                return None
        
        return data
    
  
            


if __name__ == "__main__":
    alsaAudioMicrophone = AlsaAudioMicrophone()
    alsaAudioMicrophone.start()  