'''
Created on Jan 19, 2014

@author: reijo
'''

import alsaaudio
from threading import Thread
from Queue import Queue

from Ear import Ear
from Sound import Sound



class Hearing(Thread):
    
    SOUND_LIMIT=0.2
    
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
        self.is_sound = False
       
        self.ear = [None]*Hearing.LEN_EARS

        self.ear[Hearing.LEFT] = Ear(id=Hearing.LEFT, name=Hearing.ear_names[Hearing.LEFT], card=alsaaudio.cards()[0], average=55.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        self.ear[Hearing.RIGHT] = Ear(id=Hearing.RIGHT, name=Hearing.ear_names[Hearing.RIGHT], card=alsaaudio.cards()[1], average=680.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        
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
            print "Got sound from queue " + Hearing.ear_names[sound.get_id()]  + " State " +  sound.get_str_state() + " start_time " + str(sound.get_start_time())  + " duration " + str(sound.get_duration())  + " volume_level " + str(sound.get_volume_level())
            # TODO process which ear hears sounds first
            self.process(sound)
 
    # TODO Logic           
    def process(self, sound):
        id=sound.get_id()
        self.sound[id]=sound
        other=self.other(id)
        other_sound=self.sound[other]
        change=False
        if not self.is_sound:
            if sound.get_state() == Sound.START:
                print "process START sound from " + Hearing.ear_names[id]
                if other_sound.get_start_time() > sound.get_start_time():
                    print "process sound other has later start time"
                    if other_sound.get_start_time() - sound.get_start_time() < Hearing.SOUND_LIMIT:
                        print "in same sound with other sound, sound state keeps same"
                    else:
                        print "Too old sound, not with other, sound state keeps same"
                else:
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

        hearing=Hearing()
        hearing.start()
 
        print "__main__ exit"
        exit()
       
        
