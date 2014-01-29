'''
Created on Jan 19, 2014

@author: reijo
'''

import alsaaudio
from threading import Thread
from Queue import Queue
import math

from Ear import Ear
from Sound import Sound



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
    
    SOUND_LIMIT=0.5 # 0.2
    
    EAR_DISTANCE = 0.20
    SOUND_SPEED = 340.0
    
    left = 'left'
    right = 'right'
    
    LEFT = 0
    RIGHT = 1
    LEN_EARS=2
    
    
    ear_names = ['left', 'right']

    def __init__(self):
        Thread.__init__(self)
        
        self.queue = Queue()
        self.running = False
        #self.is_sound = False
        self.is_sound = [False]*Hearing.LEN_EARS
       
        self.ear = [None]*Hearing.LEN_EARS

        self.ear[Hearing.LEFT] = Ear(id=Hearing.LEFT, name=Hearing.ear_names[Hearing.LEFT], card='Set', average=55.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        self.ear[Hearing.RIGHT] = Ear(id=Hearing.RIGHT, name=Hearing.ear_names[Hearing.RIGHT], card='U0x46d0x8b2', average=680.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[2]
        
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
            sound=self.queue.get()
            if Hearing.debug:
                print "Got sound from queue " + Hearing.ear_names[sound.get_id()]  + " State " +  sound.get_str_state() + " start_time " + str(sound.get_start_time())  + " duration " + str(sound.get_duration())  + " volume_level " + str(sound.get_volume_level())
            # TODO process which ear hears sounds first
            self.process(sound)
 
    # TODO Logic           
    def process(self, sound):
        id=sound.get_id()
        self.sound[id]=sound
       
        if sound.get_state() == Sound.START:
            self.is_sound[id] = True
       # if stop or continue and sound has lasted SOUND_LIMIT
        if sound.get_state() == Sound.STOP or (sound.get_state() == Sound.CONTINUE and sound.get_duration() > Hearing.SOUND_LIMIT):
            other=self.other(id)
            other_sound=self.sound[other]
            left_sound = self.sound[LEFT]
            right_sound = self.sound[RIGHT]
            change=False
            
            # if there is no sound in another ear, sound comes from this ear's direction
            # TODO Only got Sound from left/Right  No other sound, no direction
            if not self.is_sound[other]:
                #print "Sound from " + Hearing.ear_names[id] + " No other sound, no direction, other sound stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
                if sound.get_start_time() - other_sound.get_stop_time() < Hearing.SOUND_LIMIT:
                    print "Sound from " + Hearing.ear_names[id] + " No other sound, but other sound just stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
                    if other_sound.get_volume_level() > 0.0:
                        a = math.degrees(math.acos(left_sound.get_volume_level() - right_sound.get_volume_level()))
                        print "Sound from " + Hearing.ear_names[id] + " direction by volume level " + str(sound.get_volume_level()/other_sound.get_volume_level()) + " degrees " + str (a)
                    else:
                        print "Sound from " + Hearing.ear_names[id] + " direction by volume level, but other level is zero, this direction"
                else:  
                    print "Sound from " + Hearing.ear_names[id] + " No other sound, no direction, other sound stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
            elif sound.get_start_time() <  other_sound.get_start_time():
                print "Sound from " + Hearing.ear_names[id] + " This sound started before the other one, we can calculate direction"
                if other_sound.get_start_time() - sound.get_start_time() < Hearing.SOUND_LIMIT:
                    # cos(a) = sound difference * sound speed/ microphone distance
                    a = math.degrees(math.acos((left_sound.get_start_time() - right_sound.get_start_time())*SOUND_SPEED/EAR_DISTANCE))
                    print "Sound from " + Hearing.ear_names[id] + " direction by timing " + str(other_sound.get_start_time() - sound.get_start_time()) + " degrees " + str (a)


                else:
                    if other_sound.get_volume_level() > 0.0:
                        a = math.degrees(math.acos(left_sound.get_volume_level() - right_sound.get_volume_level()))
                        print "Sound from " + Hearing.ear_names[id] + " direction by volume level " + str(sound.get_volume_level()/other_sound.get_volume_level()) + " degrees " + str (a)
                    else:
                        print "Sound from " + Hearing.ear_names[id] + " direction by volume level, but other level is zero, this direction"
                    
            else:        
                print "Sound from " + Hearing.ear_names[id] + " Other sound started after than this, we can calculate direction"
                if sound.get_start_time() - other_sound.get_start_time() < Hearing.SOUND_LIMIT:
                    print "Sound from " + Hearing.ear_names[other] + " direction by timing " + str(sound.get_start_time() - other_sound.get_start_time())
                    a = math.degrees(math.acos((left_sound.get_start_time() - right_sound.get_start_time())*SOUND_SPEED/EAR_DISTANCE))
                    print "Sound from " + Hearing.ear_names[other] + " direction by timing " + str(other_sound.get_start_time() - sound.get_start_time()) + " degrees " + str (a)
                else:
                    if sound.get_volume_level() > 0.0:
                        print "Sound from " + Hearing.ear_names[other] + " direction by volume level " + str(other_sound.get_volume_level()/sound.get_volume_level())
                    else:
                        print "Sound from " + Hearing.ear_names[other] + " direction by volume level, but this level is zero, other direction"
                    
        if sound.get_state() == Sound.STOP:
            self.is_sound[id] = False

 
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

        hearing=Hearing()
        hearing.start()
 
        print "__main__ exit"
        exit()
       
        
