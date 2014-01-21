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

import SocketServer
from Command import Command
from Romeo import Romeo
from subprocess import call
from threading import Thread
from threading import Timer
from Queue import Queue
import signal
import socket


import daemon
import lockfile

from Sound import *

class Ear(Thread):
    

    def __init__(self, name, queue, card='default', channels=1, rate=44100, format=alsaaudio.PCM_FORMAT_S16_LE, average=0.0, sensitivity=2.0):
        Thread.__init__(self)
        self.card=card
        self.name=name
        self.sensitivity=sensitivity
        self.rate = float(rate)
        print 'str(alsaaudio.cards())' + str(alsaaudio.cards())
        self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, card)
        print self.inp.cardname()
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
        self.stop_time=0.0
        
        self.running=True
        
    def stop(self):
        self.running=False


    def values_bytes(self, data, dtype):
        minim=9999
        maxim=-9999
        # todo remove
        #self.sum=0.0
        #self.n=1.0
        
        try:
            aaa = numpy.fromstring(data, dtype='<i2')
        except (ValueError):
            return "ValueError"
# TODO floating root mean square neliojuuri ((n-1) * avererage*average + a*a)
        i=0
        for a in aaa:
            square_a = float(a) * float(a)
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + square_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + square_a)/self.short_average_devider)
            if a > maxim:
                maxim = a
            if a < minim:
                minim = a
            if self.voice:
                if self.short_average <= self.sensitivity * self.average:
                   self.stop_time = time.time() - (float(i)/(self.rate))
                   self.sound.set_duration(time.time() - self.sound.get_start_time())
                   self.sound.set_volume_level(math.sqrt(self.square_sum/self.n)/self.average)
                   self.queue.put(self.sound)
                   #print self.card + " voice stopped at " + time.ctime() + ' ' + str(self.stop_time) +  ' ' + str(self.stop_time-self.start_time) + ' ' + str(self.sum/self.n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average)
                   self.voice = False
                else:
                   self.sum += self.short_average
                   self.square_sum += square_a
                   self.n+=1.0
            else:
                if self.short_average > self.sensitivity * self.average:
                   self.start_time = time.time() - (float(i)/(self.rate)) # sound's start time is when we got sound data minus slots that are not in the sound
                   self.sound = Sound(name=self.name, start_time=self.start_time)
                   self.queue.put(self.sound)
                   #print self.card + " voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average)
                   self.voice = True
                   self.sum=self.short_average
                   self.n=1.0
                   self.square_sum = square_a
                   
            i += 1

        #print self.card + " averages " + str(self.short_average) + ' ' + str(self.average)
 
        #return str(minim) + ' - ' + str(maxim) + ' ' + str(self.average)
    
    def run(self):
        print "Starting " + self.name
        
        loops = 1500
        len=0

        while self.running:
            # Read data from device
            l, data = self.inp.read()
            #has_data=False;
      
            if l > 0:
                len += l
                self.values_bytes(data, '<i2')
                #print "Card:" + self.card + ' l: ' +  str(l) + ' len: ' + str(len)
                #print "Card:" + self.card + ' min and max: ' +  self.values_bytes(data, '<i2')
                ##has_data = True
                loops -= 1
                time.sleep(.001)


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
        t.start() # after 30 seconds, "hello, world" will be printed

if __name__ == "__main__":
        #main()
        queue=Queue()

        ear1=Ear(card=alsaaudio.cards()[0], average=55.0, queue=queue) #'Set') # card=alsaaudio.cards()[1]
        ear1.start()
        ear2=Ear(card=alsaaudio.cards()[1],  average=680.0 , queue=queue) # card=alsaaudio.cards()[1]
        ear2.start()
        

        t = Timer(12.0, stop)
        t.start() # after 30 seconds, "hello, world" will be printed
        
        while(True):
            sound=queue.get()
            print "Got sound from queue"
        
        print "__main__ exit"
        exit()



