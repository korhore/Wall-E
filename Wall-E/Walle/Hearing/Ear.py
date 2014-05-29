'''
Created on Feb 24, 2013

@author: reijo
'''

import sys
import time
import getopt
import alsaaudio
import numpy
import math

from threading import Thread
from threading import Timer
from Queue import Queue

from Walle.Sensation import Sensation
from Walle.Hearing.Sound import Sound

class Ear(Thread):

    log = True

    def __init__(self, id, name, queue, card='default', channels=1, rate=44100, format=alsaaudio.PCM_FORMAT_S16_LE,
                 average=0.0, sensitivity=2.0):
        Thread.__init__(self)
        self.id=id
        self.name=name
        self.card=card
        self.sensitivity=sensitivity
        self.rate = float(rate)
        #print 'str(alsaaudio.cards())' + str(alsaaudio.cards())
        self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, card)
        print name + ' card ' + self.inp.cardname()
        #self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

        # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
        self.inp.setchannels(channels)
        self.inp.setrate(rate)
        self.inp.setformat(format)
        self.inp.setperiodsize(32) #160
        
        self.queue=queue
 
        self.average=average;
        self.average_devider = float(rate) * 10.0
        self.short_average=average;
        self.short_average_devider = 2000.0
        self.voice = False
        self.start_time=0.0
        #self.stop_time=0.0
        
        self.running=False
        self.on=False
        
        self.debug_time=time.time()

       
    def stop(self):
        self.running=False
        
    def setOn(self, on):
        self.on = on
 

    def values_bytes(self, data, dtype):
        minim=9999
        maxim=-9999
       
        try:
            aaa = numpy.fromstring(data, dtype='<i2')
        except (ValueError):
            return "ValueError"
        
        i=0
        for a in aaa:
            square_a = float(a) * float(a)
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
            if Ear.log and time.time() > self.debug_time + 60.0:
            #if Hearing.Hearing.log:
            #if time.time() > self.debug_time + 6.0:
                print "Ear " + self.name + " time.time() " + time.ctime(time.time()) + ' self.debug_time ' + time.ctime(self.debug_time)
                print "Ear " + self.name + " average " + str(self.average) + ' short_average ' + str(self.short_average)
                self.debug_time = time.time()
            
            if a > maxim:
                maxim = a
            if a < minim:
                minim = a
            if self.voice:
                if self.short_average <= self.sensitivity * self.average:
                   #duration=self.n/self.rate
                   #self.stop_time = self.start_time + duration
                   self.sound.set_duration(self.n/self.rate)
                   self.sound.set_volume_level(math.sqrt(self.square_sum/self.n)/self.average)
                   self.sound.set_state(Sound.STOP)
                   self.queue.put(self.sound)
                   #print self.name + " voice stopped at " + time.ctime() + ' ' + str(self.sum/self.n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average)
                   self.voice = False
                else:
                   self.sum += self.short_average
                   self.square_sum += square_a
                   self.n+=1.0
            else:
                if self.short_average > self.sensitivity * self.average:
                   self.start_time = time.time() - (float(len(aaa)-i)/self.rate) # sound's start time is when we got sound data minus slots that are not in the sound
                   self.sound = Sound(id=self.id, state=Sound.START, start_time=self.start_time)
                   self.queue.put(self.sound)
                   #print self.name + " voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average)
                   self.voice = True
                   self.sum=self.short_average
                   self.n=1.0
                   self.square_sum = square_a
                   
            i += 1
            
        if self.voice:
            #duration=self.n/self.rate
#            self.stop_time = self.start_time + duration
            self.sound.set_duration(self.n/self.rate)
            self.sound.set_volume_level(math.sqrt(self.square_sum/self.n)/self.average)
            self.sound.set_state(Sound.CONTINUE)
            self.queue.put(self.sound)

   
    def run(self):
        if not self.running:
            self.running = True
            self.on=True
            print "Starting " + self.name
            
            len=0
    
            while self.running:
                # blocking read data from device
                #print "reading " + self.name
                l, data = self.inp.read()
                #print "read " + self.name + " " + str(l)
          
                if self.on and self.running and l > 0:
                    len += l
                    self.values_bytes(data, '<i2')
    
    
            print "Exiting " + self.name

def stop():
        ear1.stop()
        ear2.stop()

def main():
        print 'main()'
        #signal.signal(signal.SIGINT, signal_handler)
        
        print 'str(alsaaudio.cards())' + str(alsaaudio.cards())
    
        ear1=Ear(card=alsaaudio.cards()[0]) #'Set') # card=alsaaudio.cards()[1]
        ear1.start()
        ear2=Ear(card=alsaaudio.cards()[1]) # card=alsaaudio.cards()[1]
        ear2.start()
        

        t = Timer(60.0, stop)
        t.start() # after 30 seconds, Ear will be stopped

if __name__ == "__main__":
        #main()
        queue=Queue()

        ear1=Ear(card=alsaaudio.cards()[0], average=55.0, queue=queue) #'Set') # card=alsaaudio.cards()[1]
        ear1.start()
        ear2=Ear(card=alsaaudio.cards()[1],  average=680.0 , queue=queue) # card=alsaaudio.cards()[1]
        ear2.start()
        

        t = Timer(12.0, stop)
        t.start() # after 30 seconds,Ear will be stopped
        
        while(True):
            sound=queue.get()
            print "Got sound from queue"
        
        print "__main__ exit"
        exit()



