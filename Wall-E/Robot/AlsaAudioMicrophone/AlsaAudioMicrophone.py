'''
Created on 01.05.2019
Updated on 01.05.2019

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
        #self.outp = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, self.device)
        #self.heard_voice=''
        self.log('cardname ' + self.inp.cardname())
        #self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

        # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
        self.inp.setchannels(self.channels)
        self.inp.setrate(self.rate)
        self.inp.setformat(self.format)
        self.inp.setperiodsize(2048) #32 160
        
  
        #self.stop_time=0.0
        
        self.running=False
        self.on=False
        
        self.debug_time=time.time()
        
#     def run(self):
#         if not self.running:
#             self.running = True
#             self.on=True
#             print("Starting " + self.name)
#             
#             len=0
#     
#             while self.running:
#                 # blocking read data from device
#                 #print "reading " + self.name
#                 l, data = self.inp.read()
#                 #print "read " + self.name + " " + str(l)
#           
#                 if self.on and self.running and l > 0:
#                     len += l
#                     self.analyzeData(data, '<i2')

    def run(self):
        self.log(" Starting robot who " + self.config.getWho() + " kind " + self.config.getKind() + " instance " + self.config.getInstance())      
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.data=None
        self.l=0
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        previous_data=None
        while self.running:
            # blocking read data from device
            #print "reading " + self.name
            l, data = self.inp.read() # l int, data bytes
            if l > 0:
                #sensation = self.analyzeData(l, data, self.CONVERSION_FORMAT)
                if self.analyzeData(l, data, self.CONVERSION_FORMAT):
                   self.log("self.outAxon.put(sensation)")
                   sensation = Sensation.create(sensationType = Sensation.SensationType.VoiceData, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, voiceSize=self.l, voiceData=data)
                   self.outAxon.put(sensation)

        self.mode = Sensation.Mode.Stopping
        self.log("Stopping AlsaAudioMicrophone")
        self.log("self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)")
        self.config.setMicrophoneVoiceAvegageLevel(voiceLevelAverage=self.average)
    

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log("run ALL SHUT DOWN")
        
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
#            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a))/self.average_devider
#            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a))/self.short_average_devider
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
            if time.time() > self.debug_time + 10.0:
            #if Hearing.Hearing.log:
            #if time.time() > self.debug_time + 6.0:
                self.log("time.time() " + time.ctime(time.time()) + ' self.debug_time ' + time.ctime(self.debug_time))
                self.log("average " + str(self.average) + ' short_average ' + str(self.short_average))
                self.debug_time = time.time()
            
            if a > maxim:
                maxim = a
            if a < minim:
                minim = a
            if self.voice:
                if self.data is None:
                    self.data=a
                else:
                    self.data += a
                self.l += 1
                if self.short_average <= self.sensitivity * self.average:
                    # check indents
                   #duration=self.n/self.rate
                   #self.stop_time = self.start_time + duration
#                    self.sound.set_duration(self.n/self.rate)
#                    self.sound.set_volume_level(math.sqrt(self.square_sum/self.n)/self.average)
#                    self.sound.set_state(Sound.STOP)
#                    self.queue.put(self.sound)
                   self.log("voice stopped at " + time.ctime() + ' ' + str(self.sum/self.n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average))
                   self.voice = False
                   
                   sensation = Sensation.create(sensationType = Sensation.SensationType.VoiceData, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, voiceSize=self.l, voiceData=self.data)
                   self.data = None
                   self.l = 0
                   #  for testing purposes playback, what we heard
                   #self.outp.write(self.heard_voice)
                   #self.heard_voice=''

                else:
                   self.sum += self.short_average
                   self.square_sum += square_a
                   self.n+=1.0
                   voice_items +=1
            else:
                if self.short_average > self.sensitivity * self.average:
                   self.start_time = time.time() - (float(len(aaa)-i)/self.rate) # sound's start time is when we got sound data minus slots that are not in the sound
#                    self.sound = Sound(id=self.id, state=Sound.START, start_time=self.start_time)
#                    self.queue.put(self.sound)
                   self.log( "voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average))
                   self.voice = True
                   self.sum=self.short_average
                   self.n=1.0
                   self.square_sum = square_a
                   #self.heard_voice = data # or +=
                   if self.data is None:
                        self.data=data
                   else:
                       self.data += data
                   self.l += l
                   voice_items +=1
                  
            i += 1
        
 #       return sensation  
        return  float(voice_items)/length >= 0.5
#        if self.voice:
#            #duration=self.n/self.rate
#            self.stop_time = self.start_time + duration
#             self.sound.set_duration(self.n/self.rate)
#             self.sound.set_volume_level(math.sqrt(self.square_sum/self.n)/self.average)
#             self.sound.set_state(Sound.CONTINUE)
#             self.queue.put(self.sound)
  

    '''    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    TODO above implementation is mostly for Hearing Sensory and
    Moving Sensory and should be move to those implementations.
    
    '''
            
            
    def process(self, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + str(sensation))      
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            self.log('process: Sensation.SensationType.Drive')      
        elif sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')      
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Who:
            print (self.name + ": Robotserver.process Sensation.SensationType.Who")
            
        # TODO study what capabilities out subrobots have ins put sensation to them
        elif self.config.canHear() and sensation.getSensationType() == Sensation.SensationType.HearDirection:
            self.log('process: SensationType.HearDirection')      
             #inform external senses that we remember now hearing          
            self.out_axon.put(sensation)
            self.hearing_angle = sensation.getHearDirection()
            if self.calibrating:
                self.log("process: Calibrating hearing_angle " + str(self.hearing_angle) + " calibrating_angle " + str(self.calibrating_angle))      
            else:
                self.observation_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
                self.log("process: create Sensation.SensationType.Observation")
                observation = Sensation(sensationType = Sensation.SensationType.Observation,
                                        memory=Memory.Work,
                                        observationDirection= self.observation_angle,
                                        observationDistance=Robot.DEFAULT_OBSERVATION_DISTANCE,
                                        reference=sensation)
                # process internally
                self.log("process: put Observation to in_axon")
                self.inAxon.put(observation)
                
                #process by remote robotes
                # mark hearing sensation to be processed to set direction out of memory, we forget it
                sensation.setDirection(Sensation.Direction.Out)
                observation.setDirection(Sensation.Direction.Out)
                #inform external senses that we don't remember hearing any more           
                self.log("process: put HearDirection to out_axon")
                self.out_axon.put(sensation)
                # seems that out_axon is handled when observation is processed internally here
                #self.log("process: put Observation to out_axon")
                #self.out_axon.put(observation)
        elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
            if not self.calibrating:
                self.log('process: Sensation.SensationType.Azimuth')      
                #inform external senses that we remember now azimuth          
                #self.out_axon.put(sensation)
                self.azimuth = sensation.getAzimuth()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Observation:
            if not self.calibrating:
                self.log('process: Sensation.SensationType.Observation')      
                #inform external senses that we remember now observation          
                self.observation_angle = sensation.getObservationDirection()
                self.turn()
                self.log("process: put Observation to out_axon")
                sensation.setDirection(Sensation.Direction.Out)
                self.out_axon.put(sensation)
        elif sensation.getSensationType() == Sensation.SensationType.ImageFilePath:
            self.log('process: Sensation.SensationType.ImageFilePath')      
        elif sensation.getSensationType() == Sensation.SensationType.Calibrate:
            self.log('process: Sensation.SensationType.Calibrate')      
            if sensation.getMemory() == Sensation.Memory.Working:
                if sensation.getDirection() == Sensation.Direction.In:
                    self.log('process: asked to start calibrating mode')      
                    self.calibrating = True
                else:
                    self.log('process: asked to stop calibrating mode')      
                    self.calibrating = False
                # ask external senses to to set same calibrating mode          
                self.out_axon.put(sensation)
            elif sensation.getMemory() == Sensation.Memory.Sensory:
                if self.config.canHear() and self.calibrating:
                    if self.turning_to_object:
                        print (self.name + ": Robotserver.process turning_to_object, can't start calibrate activity yet")
                    else:
                        # allow requester to start calibration activaties
                        if sensation.getDirection() == Sensation.Direction.In:
                            self.log('process: asked to start calibrating activity')      
                            self.calibrating_angle = sensation.getHearDirection()
                            self.hearing.setCalibrating(calibrating=True, calibrating_angle=self.calibrating_angle)
                            sensation.setDirection(Sensation.Direction.In)
                            self.log('process: calibrating put HearDirection to out_axon')      
                            self.out_axon.put(sensation)
                            #self.calibratingTimer = Timer(Robot.ACTION_TIME, self.stopCalibrating)
                            #self.calibratingTimer.start()
                        else:
                            self.log('process: asked to stop calibrating activity')      
                            self.hearing.setCalibrating(calibrating=False, calibrating_angle=self.calibrating_angle)
                            #self.calibratingTimer.cancel()
                else:
                    self.log('process: asked calibrating activity WITHOUT calibrate mode, IGNORED')      


        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            self.log('process: Sensation.SensationType.Capability')      
        elif sensation.getSensationType() == Sensation.SensationType.Unknown:
            self.log('process: Sensation.SensationType.Unknown')
 
        # Just put sensation to our parent            
        self.outAxon.put(sensation)    

if __name__ == "__main__":
    alsaAudioMicrophone = AlsaAudioMicrophone()
    alsaAudioMicrophone.start()  