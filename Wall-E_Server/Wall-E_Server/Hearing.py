'''
Created on Jan 19, 2014

@author: reijo
'''

import alsaaudio
from threading import Thread
from Queue import Queue
import math
import time

from Ear import Ear
from Sound import Sound
from SoundPosition import SoundPosition



class Hearing(Thread):
    """
    Hears produces location information of sounds, are they coming from left or right and what is angle.
    
    Hearing is bases on two Ears implemented physically with microphones positioning same way than man's ears.
    Ears produces sounds with volume and timing information.
    
    Theory says, that man knows location of sound 1) from timing. Sound must go longer way to that ear that is in longer way, so 
    if left ear is nearer, we hear sound first in that ear. We implement this.
    
    Unfortunately Raspberry Pi with two microphones and threading python platform is not fast enough for this, I'm afraid.
    Sound goes 340 m/s and if I can give 20cm difference of microphones, his means that faster sound is only
    0.2 m / 340 m/s = 0.000588235 seconds timing difference. That time we have for several thread changes and processing.
    This module is used to guide a robot implemented as Arduino device, so Raspberry Pi processor have another duties also.
    
    So we must do also something second best. This goes with thery, man uses this also as second way to locate by hearing.
    We will also think that if only one microphone hears a sound,
    sound comes on that direction. If there are two sounds in left and right ear, we will analyse level of sound
    and get angle of sound from that power line.
    
    There is also 3) way to analyse sound direction, use HRTF = head-related transfer function, but we will pass this.
    
    Technically we analyse sound, when we have heard it some time or it has lasted.
    """
    
    debug = False
    log = True
    
    SOUND_STOPPED = 0
    SOUND_ONE_EAR = 1
    SOUND_TWO_EAR = 2
    
    SOUND_ONE_EAR_REPORT_LIMIT = 60.0

    
     
    EAR_DISTANCE = 0.20 # 0.2 m
    SOUND_SPEED = 340.0 # 340 m/s in ear
    SOUND_LIMIT=EAR_DISTANCE/SOUND_SPEED # time of sound to travel distance of ears
   
    left = 'left'
    right = 'right'
    
    LEFT = 0
    RIGHT = 1
    LEN_EARS=2
    
    
    ear_names = ['left', 'right']

    def __init__(self, report_queue):
        Thread.__init__(self)
        
        self.report_queue = report_queue
        
        self.sound_queue = Queue()
        self.running = False
        self.sound_status = Hearing.SOUND_STOPPED
        self.reported = False
        self.reported_timing = False
        self.reported_level = False
        self.reported_single = False
        self.report_time=time.time()
        self.angle = 0.0
        self.id=Hearing.LEFT
        #self.is_sound = False
        self.is_sound = [False]*Hearing.LEN_EARS
       
        self.ear = [None]*Hearing.LEN_EARS

        self.ear[Hearing.LEFT] = Ear(id=Hearing.LEFT, name=Hearing.ear_names[Hearing.LEFT], card='Set', average=55.0, sensitivity=1.5, queue=self.sound_queue) #'Set') # card=alsaaudio.cards()[1]
 #       self.ear[Hearing.RIGHT] = Ear(id=Hearing.RIGHT, name=Hearing.ear_names[Hearing.RIGHT], card='U0x46d0x8b2', average=680.0, sensitivity=1.5, queue=self.sound_queue) #'Set') # card=alsaaudio.cards()[2]
        self.ear[Hearing.RIGHT] = Ear(id=Hearing.RIGHT, name=Hearing.ear_names[Hearing.RIGHT], card='Set_1', average=55.0, sensitivity=1.5, queue=self.sound_queue) #'Set') # card=alsaaudio.cards()[2]
        
        self.sound_ear_id = Hearing.LEFT
        self.sound = [None]*Hearing.LEN_EARS
        self.sound[Hearing.LEFT] = Sound(id=Hearing.LEFT);
        self.sound[Hearing.RIGHT] = Sound(id=Hearing.RIGHT);
        
    def stop(self):
        self.ear[Hearing.LEFT].stop()
        self.ear[Hearing.RIGHT].stop()
        self.running=False
        

    def run(self):
        print "Starting " + self.name
        
        self.ear[Hearing.LEFT].start()
        self.ear[Hearing.RIGHT].start()
        self.running=True

        while self.running:
            sound=self.sound_queue.get()
            if Hearing.debug:
                print "Got sound from sound_queue " + Hearing.ear_names[sound.get_id()]  + " State " +  sound.get_str_state() + " start_time " + str(sound.get_start_time())  + " duration " + str(sound.get_duration())  + " volume_level " + str(sound.get_volume_level())
            # TODO process which ear hears sounds first
            self.process(sound)
 
    # TODO Logic           
    def process(self, sound):
        id=sound.get_id()
        other=self.other(id)
      
        if sound.get_state() == Sound.START:
            self.sound[id]=sound
            self.reported = False       # report after sound start
            self.reported_timing = False
            self.reported_level = False
            self.reported_single = False
            self.is_sound[id] = True
            if  self.is_sound[other]:
                self.sound_status = Hearing.SOUND_TWO_EAR
                print "Sound status two ear sound"
            else:
                self.sound_status = Hearing.SOUND_ONE_EAR
                self.id = id        # remember initial ear hears sound first
                print "Sound status one ear sound"
       # if stop or continue and sound has lasted SOUND_LIMIT
        if sound.get_state() == Sound.STOP or (sound.get_state() == Sound.CONTINUE and sound.get_duration() > Hearing.SOUND_LIMIT):
            other_sound=self.sound[other]
            left_sound = self.sound[Hearing.LEFT]
            right_sound = self.sound[Hearing.RIGHT]
            change=False
            
            # if there is not yet sound from another ear, sound comes from this ear's direction
            # but we can't be sure, that another sound comes, so we must wait
            #
            # TODO Only got Sound from left/Right  No other sound, no direction
            if self.sound_status == Hearing.SOUND_ONE_EAR:
                #print "Sound from " + Hearing.ear_names[id] + " No other sound, no direction, other sound stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
                if sound.get_start_time() - other_sound.get_stop_time() < Hearing.SOUND_LIMIT:
                    if self.debug:
                        print "Sound from " + Hearing.ear_names[id] + " No other sound, but other sound just stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
                    if self.debug:
                        print "Sound status two ear sound"
                    self.angle = self.level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                    if self.debug:
                        print "Sound from " + Hearing.ear_names[id] + " direction by volume level " + str(left_sound.get_volume_level()) + ' ' + str(right_sound.get_volume_level()) + " degrees " + str (self.angle)
                    self.report_queue.put(SoundPosition(time=self.sound[self.id].get_start_time(), angle=self.angle, type=Hearing.SOUND_TWO_EAR))
                    self.reported = True
                    self.reported_level = True
                    self.report_time=time.time()
                else:  
                    if self.debug:
                        print "Sound from " + Hearing.ear_names[id] + " No other sound, no direction, other sound stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
                    self.angle = self.single_sound_to_degrees(self.is_sound[Hearing.LEFT], self.is_sound[Hearing.RIGHT])
                    if self.debug:
                        print "Sound from " + Hearing.ear_names[id] + " single " + str(self.is_sound[Hearing.LEFT]) + ' ' + str(self.is_sound[Hearing.RIGHT]) + " degrees " + str (self.angle)
                    #self.report_queue.put(SoundPosition(self.angle))
            elif math.fabs(other_sound.get_start_time() - sound.get_start_time()) < Hearing.SOUND_LIMIT:
                if not self.reported_timing: # ting is repoted always once per sound, even if by level is reported
                    self.angle = self.timing_to_degrees(left_sound.get_start_time(), right_sound.get_start_time())
                    self.report_queue.put(SoundPosition(time=self.sound[self.id].get_start_time(), angle=self.angle, type=Hearing.SOUND_TWO_EAR))
                    self.reported = True
                    self.reported_timing = True
                    self.report_time=time.time()
                    if self.debug:
                        print "Sound direction by timing reported from " + Hearing.ear_names[id] + " has other sound, direction by timing " + str(other_sound.get_start_time() - sound.get_start_time()) + " degrees " + str (self.angle)
                else:
                    if self.debug:
                        print "Sound direction by timing already reported from " + Hearing.ear_names[id] + " has other sound, direction by timing " + str(other_sound.get_start_time() - sound.get_start_time()) + " degrees " + str (self.angle)

            else:
                self.angle = self.level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                print "Sound direction by volume level no reported yet from " + Hearing.ear_names[id] + ' ' + str(left_sound.get_volume_level()) + ' ' + str(right_sound.get_volume_level()) + " degrees " + str (self.angle)
                #self.report_queue.put(SoundPosition(self.angle))
                #self.reported = True
                   
        if sound.get_state() == Sound.STOP:
            # report one ear sound only rarely, wait better two ear sounds to come
            if (not self.reported) and ((self.sound_status == Hearing.SOUND_TWO_EAR) or ((time.time() - self.report_time) > Hearing.SOUND_ONE_EAR_REPORT_LIMIT)):
                print "Sound reported delayed from " + Hearing.ear_names[id] + ' ' + str(left_sound.get_volume_level()) + ' ' + str(right_sound.get_volume_level()) + " degrees " + str (self.angle)
                self.report_queue.put(SoundPosition(time=self.sound[self.id].get_start_time(), angle=self.angle, type=self.sound_status))
                self.reported = True
                self.reported_level = True
                self.report_time=time.time()
            else:
                print "Sound stopped self.reported " + str(self.reported) + " self.sound_status " + str(self.sound_status) + " (time.time() - self.report_time) " + str((time.time() - self.report_time))
                   
                
            self.is_sound[id] = False
            
            if self.sound_status == Hearing.SOUND_TWO_EAR:
                self.sound_status = Hearing.SOUND_ONE_EAR
                print "Sound status one ear sound"
            else:
                self.sound_status = Hearing.SOUND_STOPPED
                print "Sound status stopped sound"


            
    def level_to_degrees(self, leftlevel, rightlevel):
        if leftlevel == 0.0:
            return 45.0
        if rightlevel == 0.0:
            return -45.0

        t = (rightlevel-  leftlevel)/max(leftlevel,rightlevel)
        if t < -1.0:
            t = -1.0
        if t > 1.0:
            t = 1.0
            
        return math.degrees(math.asin(t))

    def timing_to_degrees(self, lefttime, righttime):
        t = ((lefttime - righttime)*Hearing.SOUND_SPEED)/Hearing.EAR_DISTANCE
        if t < -0.5:
            t = -0.5
        if t > 0.5:
            t = 0.5
            
        return math.degrees(math.acos(t))
    
    def single_sound_to_degrees(self, is_left_sound, is_right_sound):
        if is_left_sound and is_right_sound:
            return 0.0
        if (not is_left_sound) and (not is_right_sound):
            return 0.0
        if is_left_sound:
            return -45.0
        return 45.0



 
    def analyse(self, sound):
        id=sound.get_id()
        self.sound[id]=sound
        other=self.other(id)
        other_sound=self.sound[other]
        change=False
        if not self.is_sound[id]:
            if sound.get_state() == Sound.START:
                if Hearing.debug:
                    print "process START sound from " + Hearing.ear_names[id]
                if other_sound.get_start_time() > sound.get_start_time():
                    print "process sound other has later start time"
                    if other_sound.get_start_time() - sound.get_start_time() < Hearing.SOUND_LIMIT:
                        print "in same sound with other sound, sound state keeps same"
                    else:
                        print "Too old sound, not with other, sound state keeps same"
                else:
                    if Hearing.debug:
                        print "process this sound was later"
                    if sound.get_start_time() - other_sound.get_stop_time() < Hearing.SOUND_LIMIT:
                        print "This sound start is close to other sound stop, continue previous sounds"
                        self.is_sound = True
                        change=True
                    else:
                        print "This sound start is NOT close to other sound stop, start sounds"
                        self.sound_ear_id = id
                        self.is_sound = True
                        change=True
                         
        elif sound.get_state() == Sound.STOP:
            print "process STOP sound from " + Hearing.ear_names[id]
            if self.sound_ear_id == id:
                print "This sound stops"
                self.is_sound = False
                change=True
            else:
                print "Other sound stops, sound state keeps same"
                
        if change:
            if self.is_sound:
                print "SOUND STARTED ON " + Hearing.ear_names[self.sound_ear_id]
            else:
                print "SOUND STOPPED ON " + Hearing.ear_names[self.sound_ear_id]

    def other(self, id):
        return (id+1) % Hearing.LEN_EARS   
      
if __name__ == "__main__":
        #main()
        
        print str(alsaaudio.cards())
        report_queue = Queue()


        hearing=Hearing(report_queue)
        hearing.start()
        while True:
            sound_position=report_queue.get()
            #if Hearing.debug:
            print "--> Got sound_position from report_queue, time " + time.ctime(sound_position.get_time()) + " angle " + str(sound_position.get_angle()) + " type " + str(sound_position.get_type())
 
        print "__main__ exit"
        exit()
       
        
