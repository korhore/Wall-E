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
import signal
import socket


import daemon
import lockfile


class Ear(Thread):
    

    def __init__(self, card='default', channels=1, rate=44100, format=alsaaudio.PCM_FORMAT_S16_LE, average=0.0):
        Thread.__init__(self)
        self.card=card
        print 'str(alsaaudio.cards())' + str(alsaaudio.cards())
        self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, card)
        print self.inp.cardname()
        #self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

        # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
        self.inp.setchannels(channels)
        self.inp.setrate(rate)
        self.inp.setformat(format)
        self.inp.setperiodsize(32) #160
        
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
        sum=0.0
        n=1.0
        
        try:
            aaa = numpy.fromstring(data, dtype='<i2')
        except (ValueError):
            return "ValueError"
# TODO floating root mean square neliojuuri ((n-1) * avererage*average + a*a)
        for a in aaa:
            squrare_a = float(a) * float(a)
            self.average = math.sqrt(( (self.average * self.average * (self.average_devider - 1.0))  + squrare_a)/self.average_devider)
            self.short_average = math.sqrt(( (self.short_average * self.short_average * (self.short_average_devider - 1.0))  + squrare_a)/self.short_average_devider)
            if a > maxim:
                maxim = a
            if a < minim:
                minim = a
            if self.voice:
                if self.short_average <= 2.0 * self.average:
                   self.stop_time =time.time()
                   print self.card + " voice stopped at " + time.ctime() + ' ' + str(self.stop_time) +  ' ' + str(self.stop_time-self.start_time) + ' ' + str(sum/n/self.average) + ' ' + str(self.short_average) + ' ' + str(self.average)
                   self.voice = False
                else:
                   sum += self.short_average
                   n+=1.0
            else:
                if self.short_average > 2.0 * self.average:
                   self.start_time = time.time()
                   print self.card + " voice started at " + time.ctime() + ' ' + str(self.start_time) + ' ' + str(self.short_average) + ' ' + str(self.average)
                   self.voice = True
                   sum=self.short_average
                   n=1.0

        print self.card + " averages " + str(self.short_average) + ' ' + str(self.average)
 
        return str(minim) + ' - ' + str(maxim) + ' ' + str(self.average)
    
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
        ear1=Ear(card=alsaaudio.cards()[0], average=55.0) #'Set') # card=alsaaudio.cards()[1]
        ear1.start()
        ear2=Ear(card=alsaaudio.cards()[1],  average=680.0) # card=alsaaudio.cards()[1]
        ear2.start()
        

        t = Timer(12.0, stop)
        t.start() # after 30 seconds, "hello, world" will be printed
        
        print "__main__ exit"
        exit()



