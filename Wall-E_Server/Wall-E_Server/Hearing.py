'''
Created on Jan 19, 2014

@author: reijo
'''

import alsaaudio
from threading import Thread
from Queue import Queue

from Ear import Ear



class Hearing(Thread):
    

    def __init__(self):
        Thread.__init__(self)
        
        self.queue=Queue()
        self.running=False

        self.left_ear=Ear(name='left', card=alsaaudio.cards()[0], average=55.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        self.right_ear=Ear(name='right', card=alsaaudio.cards()[1], average=680.0, sensitivity=1.5, queue=self.queue) #'Set') # card=alsaaudio.cards()[1]
        
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
            print "Got sound from queue " + sound.get_name()  + " start_time " + str(sound.get_start_time())  + " duration " + str(sound.get_duration())  + " volume_level " + str(sound.get_volume_level())
            # TODO process which ear hears sounds first

      
if __name__ == "__main__":
        #main()

        hearing=Hearing()
        hearing.start()
 
        print "__main__ exit"
        exit()
       
        
