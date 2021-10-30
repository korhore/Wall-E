'''
Created on 21.09.2019
Updated on 30.10.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory for hearing,
implemented by alsaaudio or by SoundDevice and need usb-microphone as hardware

'''
import time
import numpy
import math

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation
from AlsaAudio import Settings

# prefer AlsaAidio before SoundDevice
IsAlsaAudio=True
#IsAlsaAudio=False

if IsAlsaAudio:
    try:
        print("Microphone import alsaaudio")
        import alsaaudio
        from AlsaAudio import AlsaAudioNeededSettings
    except ImportError as e:
        print("Microphone import alsaaudio error " + str(e))
        IsAlsaAudio=False

if not IsAlsaAudio:
    try:
        print("Microphone import sounddevice as sd")
        import sounddevice as sd
    except ImportError as e:
        print("Microphone import sounddevice as sd error " + str(e))





class Microphone(Robot):
    """
     Implementation for out Voice sensation at Sensory level
     using ALSA-library or SoundDevice-library and usb-microphone hardware
     
     Produces voices connected to present Item.names
    """
        
    SENSITIVITY=1.25
    AVERAGE_PERIOD=100.0                # used as period in seconds
    SHORT_AVERAGE_PERIOD=1.0            # used as period in seconds
    
    DEBUG_INTERVAL=60.0
    SLEEP_TIME=3.0                     # if nothing to do, sleep
    DURATION = 1.0                     # record 1.5 sec
    VOIVELENGTHMINIMUN = 2.0           # accept voices, that are at least this long, not just click/click etc. something that are propable something a person says,
    SILENCEMAXIMUM = 1.0               # duration how long silence we should hear until a single sound stops
    VOIVECONCATENATETRYES = 3          # accept voices, that are at least this long, not just click/click etc. something that are propable something a person says,
        


    def __init__(self,
                 mainRobot,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        print("We are in Microphone, not Robot")
        Robot.__init__(self,
                       mainRobot=mainRobot,
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
        if not IsAlsaAudio:
            if len(self.device) > 0:
                sd.default.device = self.device
            else:
                self.device = sd.default.device
            sd.default.samplerate = Settings.AUDIO_RATE
            sd.default.channels = self.config.getMicrophoneChannels()
            sd.default.dtype = Settings.AUDIO_CONVERSION_FORMAT
               
                
        
        #self.channels=Settings.AUDIO_CHANNELS
        self.channels=self.config.getMicrophoneChannels()
        self.sensitivity=Microphone.SENSITIVITY
        self.rate = Settings.AUDIO_RATE
        self.average=self.config.getMicrophoneVoiceAvegageLevel()
        self.average_devider = float(self.rate) * Microphone.AVERAGE_PERIOD
        self.short_average=self.average
        self.short_average_devider = float(self.rate) * Microphone.SHORT_AVERAGE_PERIOD
        
        self.voice = False
        self.start_time=0.0
        self.logged = False
        


        if IsAlsaAudio:
            self.inp = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, device=self.device)
            # Set attributes: Stereo, 44100 Hz, 16 bit little endian samples
            self.inp.setchannels(self.channels)
            self.inp.setrate(self.rate)
            self.inp.setformat(AlsaAudioNeededSettings.AUDIO_FORMAT)
            self.inp.setperiodsize(Settings.AUDIO_PERIOD_SIZE)
 
            self.log('cardname ' + self.inp.cardname())
        else:
            self.log('device ' + str(self.device))
            self.rawInputStream = sd.RawInputStream(samplerate=Settings.AUDIO_RATE, channels=self.channels, dtype=Settings.AUDIO_CONVERSION_FORMAT)#'int16')
            

        self.running=False
        self.on=False
        
        self.debug_time=time.time()

        # buffer variables for voice        
        self.voice_data=None
        self.voice_l=0
        # buffer variables for silence        
        self.silence_data=None
        self.silence_l=0

        self.robotState = None
        
    def run(self):
        self.log(" run robot robot " + self.getName() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))
        
        self.informRobotState(robotState = Sensation.RobotState.MicrophoneSensing)
       
        # starting other threads/senders/capabilities
        
        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
#         voice_data=None
#         voice_l=0
        if not IsAlsaAudio:
            self.rawInputStream.start()

        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                # interrupt voice and put it to parent for processing
                self.putVoiceToParent()

                transferDirection, sensation = self.getAxon().get(robot=self)
                self.log(logLevel=Robot.LogLevel.Verbose, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
#                 if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemoryType() == Sensation.MemoryType.Working and\
#                    sensation.getRobotType(robotMainNames=self.getMainNames()) == Sensation.RobotType.Sense: 
#                     self.tracePresents(sensation)
#                 else:
                self.informRobotState(robotState = Sensation.RobotState.MicrophoneDisabled)
                self.process(transferDirection=transferDirection, sensation=sensation)
                sensation.detach(robot=self)
                self.informRobotState(robotState = Sensation.RobotState.MicrophoneSensing)
            else:
                if self.getMemory().hasItemsPresence(): # listen is we have items that can speak
                    if not self.logged:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr=self.getMemory().itemsPresenceToStr() + " items speaking, sense")
                        self.logged = True
                    self.sense()
                else:
                    self.logged = False
#                     # TODO as a test we sense
                    #self.log(logLevel=Robot.LogLevel.Verbose, logStr=str(len(self.getMemory().presentItemSensations)) + " items NOT speaking, sense anyway")
                    self.sense()
                    #self.log(logLevel=Robot.LogLevel.Normal, logStr="no items speaking, sleeping " + str(Microphone.SLEEP_TIME))
                    #time.sleep(Microphone.SLEEP_TIME)
                    

        self.log("Stopping Microphone")
        self.mode = Sensation.Mode.Stopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)")
        self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)
        self.informRobotState(robotState = Sensation.RobotState.MicrophoneDisabled)
        
        if not IsAlsaAudio:
            self.rawInputStream.stop()
        
       
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
        if IsAlsaAudio:
            l, data = self.inp.read() # l int, data bytes
            if l > 0:
                # collect voice data as long we hear a voice and send it then
                if self.analyzeNumpyData(l, data, Settings.AUDIO_CONVERSION_FORMAT):
                    if self.voice_data is None:
                        self.voice_data = data
                        self.voice_l = l
                    else:
                        # if we have silence in the middle the sound add it to final sound
                        if not self.silence_data is None:
                            self.voice_data += self.silence_data
                            self.voice_l += self.silence_l                            
                            self.silence_data = None
                            self.silence_l = 0
                        self.voice_data += data
                        self.voice_l += l
                    self.silence_data = None
                    self.silence_l = 0
                # if we have a started voice and now a silence
                elif not self.voice_data is None:
                    if self.silence_data is None:
                        self.silence_data = data
                        self.silence_l = l
                    else:
                        self.silence_data += data
                        self.silence_l += l
                    # if silence is long enough to stop a voice
                    if self.getPlaybackTime(self.getVoiceDataLength(self.silence_data)) >= self.SILENCEMAXIMUM:
                        self.putVoiceToParent()
                        self.silence_data = None
                        self.silence_l = 0

        else:
            # TODO Voice play length calculation mayh be broken, we need new methods for raw_data
            buf, overflowed  = self.rawInputStream.read(int(self.DURATION * sd.default.samplerate * self.channels))
            data = bytes(buf)
    
            if not overflowed and len(data) > 0:
                 # collect silence data as long we hear a voice and send it then
                if self.analyzeRawData(data):
                    if self.voice_data is None:
                        self.voice_data = data
                        self.voice_l = len(data)
                    else:
                        self.voice_data += data
                        self.voice_l += len(data)
                    self.silence_data = None
                    self.silence_l = 0
                # if we have a started voice and now a silence
                elif not self.voice_data is None:
                    if self.silence_data is None:
                        self.silence_data = data
                        self.silence_l = l
                    else:
                        self.silence_data += data
                        self.silence_l += len(data)
                    # if silence is long enough to stop a voice
                    if self.getPlaybackTime(self.getVoiceDataLength(self.silence_data)) >= self.SILENCEMAXIMUM:
                        self.putVoiceToParent()
                        self.silence_data = None
                        self.silence_l = 0

    def putVoiceToParent(self):
        if self.voice_data is not None:
            # If we have a voice that is longer than just a click etc.
            if self.getPlaybackTime(self.getVoiceDataLength(self.voice_data)) >= self.VOIVELENGTHMINIMUN:
                # put robotType out (heard voice) to the parent Axon going up to main Robot
                # connected to present Item.names
                voiceSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
                                                       data=self.getVoiceData(data=self.voice_data, dtype=Settings.AUDIO_CONVERSION_FORMAT), locations=self.getLocations())
                self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: voice from " + self.getMemory().itemsPresenceToStr())
                for itemSensation in self.getMemory().getAllPresentItemSensations():
                    itemSensation.associate(sensation=voiceSensation)
    #            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: self.getParent().getAxon().put(robot=self, sensation)")
    #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)
                self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: route(transferDirection=Sensation.TransferDirection.Direct, sensation=voiceSensation {}s voice".format(self.getPlaybackTime(self.getVoiceDataLength(self.voice_data))))
                self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=voiceSensation)
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: rejected too short {}s voice".format(self.getPlaybackTime(self.getVoiceDataLength(self.voice_data))))
                
            self.voice_data=None
            self.voice_l=0
            self.silence_data = None
            self.silence_l = 0
        
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
        
        numpy version 
        '''
        
    def analyzeNumpyData(self, l, data, dtype):
#        self.log("analyzeNumpyData")      
        minim=9999
        maxim=-9999
       
        try:
            aaa = numpy.fromstring(data, dtype=dtype)
        except (ValueError):
            self.log("analyzeNumpyData numpy.fromstring(data, dtype=dtype: ValueError")      
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
            if time.time() > self.debug_time + Microphone.DEBUG_INTERVAL:
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
        Analyze voice sample

        raw data version
        
        TODO Seems only difference with analyzeNumpyData is that we get fixed dtype=Settings.AUDIO_CONVERSION_FORMAT
             but we get array of arrays
        '''
    def analyzeRawData(self, data):

        # convert to int array        
        try:
            aaa = numpy.fromstring(data, dtype=Settings.AUDIO_CONVERSION_FORMAT)
        except (ValueError):
            self.log("analyzeRawData numpy.fromstring(data, dtype=Settings.AUDIO_CONVERSION_FORMAT: ValueError")      
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
            if time.time() > self.debug_time + Microphone.DEBUG_INTERVAL:
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
                    self.start_time = time.time() - (float(len(aaa)-i)/self.rate) # arrays of arrays, so /self.channels # sound's start time is when we got sound data minus slots that are not in the sound
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
    but we can have mono-microphones that produce 1-channels data,
    which is set in config file to be known,
    so only conversion supported now is 1-channel to 2-channels
    '''
    
    
    def getVoiceData(self, data, dtype):
        if IsAlsaAudio and self.channels == 1 and Settings.AUDIO_CHANNELS == 2:
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
 
    '''
    get read data length to expected voice format
    We expect output to be PC; 2-channels,
    but we can have mono-microphones that produce 1-channel getPlaybackTimes data,
    which is set in config file to be known,
    so only conversion supported now is 1-channel to 2-channels
    '''
    
    
    def getVoiceDataLength(self, data):
        if IsAlsaAudio and self.channels == 1 and Settings.AUDIO_CHANNELS == 2:
            return 2*len(data)
        
        return len(data)

    '''
    Inform in what robotState this Robot is to other Robots
    '''   
    def informRobotState(self, robotState):
        if self.robotState != robotState: 
            self.robotState = robotState
            robotStateSensation = self.createSensation(associations=None,
                                                       sensationType=Sensation.SensationType.RobotState,
                                                       memoryType=Sensation.MemoryType.Sensory,
                                                       robotState=robotState,
                                                       locations=self.getLocations())
            self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=robotStateSensation)

    '''
    How long sound this is in seconds
    '''
    
    def getPlaybackTime(self, datalen):
        return float(datalen)/(float(Settings.AUDIO_RATE*Settings.AUDIO_CHANNELS))


if __name__ == "__main__":
    microphone = Microphone()
    microphone.start()  