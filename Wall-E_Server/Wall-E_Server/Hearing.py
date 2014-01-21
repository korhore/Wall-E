'''
Created on Jan 19, 2014

@author: reijo
'''

import alsaaudio
from threading import Thread
from Queue import Queue

from Ear import Ear



class Hearing(Thread):
    
    left = 'left'
    right = 'right'
    

    def __init__(self):
        Thread.__init__(self)
        
        self.queue = Queue()
        self.running = False

        self.left_ear = Ear(name=Hearing.left, card=alsaaudio.cards()[0], average=55.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        self.right_ear = Ear(name=Hearing.right, card=alsaaudio.cards()[1], average=680.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        
        self.left_sound = None
        self.right_sound = None
        
    def stop(self):
        self.left_ear.stop()
        self.right_ear.stop()
        self.running=False
        

    def run(self):
        print "Starting " + self.name
        
        self.left_ear.start()
        self.right_ear.start()
        self.running=True

        while self.running:
            sound=self.queue.get()
            print "Got sound from queue " + sound.get_name()  + " State " +  sound.get_str_state() + " start_time " + str(sound.get_start_time())  + " duration " + str(sound.get_duration())  + " volume_level " + str(sound.get_volume_level())
            # TODO process which ear hears sounds first
            self.process(sound)
 
    # TODO Logic           
    def process(self, sound):
        if sound.get_name() == Hearing.left:
            self.left_sound=sound
            if self.left_sound.get_duration() == 0.0:   # if start of left sound
                if self.right_sound == None:
                    print 'Left sound started, because no right sound'
                elif self.right_sound.get_start_time() > self.left_sound.get_start_time():
                    print "got Left sound but right was later"
                    if self.right_sound.get_start_time() - self.left_sound.get_start_time() < 0.2:
                        print "Have Left sound that have right sound in same sound"
                    else:
                        print "Have Right sound without left sound"
                else:
                    print "got left sound but right was before"
                    if self.left_sound.get_start_time() - self.right_sound.get_start_time() < 0.2:
                        print "Have Right sound that have left sound in same sound"
                    else:
                        print "Have Left sound without right sound"
                        
        else:
            self.right_sound=sound
            if self.right_sound.get_duration() == 0.0:   # if start of left sound
                if self.left_sound == None:
                    print 'Right sound started, because no left sound'
                elif self.left_sound.get_start_time() > self.right_sound.get_start_time():
                    print "got Right sound but left was later"
                    if self.left_sound.get_start_time() - self.right_sound.get_start_time() < 0.2:
                        print "Have Right sound that have left sound in same sound"
                    else:
                        print "Have Left sound without right sound"
                else:
                    print "got right sound but left was before"
                    if self.right_sound.get_start_time() - self.left_sound.get_start_time() < 0.2:
                        print "Have Left sound that have right sound in same sound"
                    else:
                        print "Have Right sound without left sound"
   
      
if __name__ == "__main__":
        #main()

        hearing=Hearing()
        hearing.start()
 
        print "__main__ exit"
        exit()
       
        
