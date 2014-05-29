#!/usr/bin/python -tt
# Copyright (c) 2012, Fabian Affolter <fabian@affolter-engineering.ch>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the pyfirmata team nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import time
import signal
import pyfirmata
from pyfirmata import SERVO
from time import sleep
from Sensation import Sensation


PORT = '/dev/ttyACM0'

E1 = 5   # M1 Speed Control
E2 = 6   # M2 Speed Control
M1 = 4   # M1 Direction Control
M2 = 7   # M2 Direction Control

SPEED = 80       # low speed, can be up to 255
TURN_SPEED = 80  # low speed, was 100, can be up to 255
 
 
# Buttons

BUTTON_SENSOR = 7
#BUTTON_SENSOR = 6
LED = 13
NUM_KEYS = 5

MSGS = [
  "Move forward ",
  "Turn Right    ",
  "Move backward",
  "Turn Right   ",
  "Stop         "]

ADC_KEY_VAL = [
  30, 150, 360, 535, 760 ]




def main():
    print("main start" )
# ignore first sigterm
    #signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    
    print("create Romeo" )
    romeo = Romeo()
    
    #start romeo here
    romeo.pin_high(LED)
    romeo.advance (SPEED,SPEED)
    romeo.read_button()
    print("sleep(5)" )
    time.sleep(5)
    romeo.read_button()
    romeo.stop()
    romeo.pin_low(LED)
  
    # delete all
    print("del romeo" )
    del romeo

    print("main end" )

 


class Romeo:
    MINPOWER=0.60
 
    def __init__(self):
 
        # TODO from arduino not ready definiton of romeo
        # analog 6 -> 7    
        self.romeoLayout = {
        'digital' : tuple(x for x in range(14)),
        'analog' : tuple(x for x in range(BUTTON_SENSOR+1)),
        'pwm' : (3, 5, 6, 9, 10, 11),
        'use_ports' : True,
        'disabled' : (0, 1) # Rx, Tx, Crystal
        }
        
        self.pin = LED #2
        self.port = PORT
        
        self.adc_key_in = 0
        self.key = -1
        self.oldkey = -1

        self.board = pyfirmata.Board(port=self.port, layout=self.romeoLayout)
        print("Connected to " + PORT)
        print "Setting up the connection to the board ..."
        self.it = pyfirmata.util.Iterator(self.board)
        self.it.start()
        print "Start iterator ..."
        #for i in range(4,7):
        #    self.board.analog[i].pinMode(i,self.board.OUTPUT)
        
        self.e1 = self.board.get_pin('d:5:o');  # M1 Speed Control 's:5:o'
        self.e1.mode=pyfirmata.PWM              # Set to power mode
        self.m1 = self.board.get_pin('d:4:o');  # M1 Direction Control
        self.e2 = self.board.get_pin('d:6:o');  # M2 Speed Control s:6:o'
        self.e2.mode=pyfirmata.PWM              # Set to power mode
        self.m2 = self.board.get_pin('d:7:o');  # M2 Direction Control
       
        self.board.analog[BUTTON_SENSOR].enable_reporting()
            
    def __del__(self):
        print "del it and board ..."
        self.board.pass_time(1)
        self.board.exit()
        del self.it
        del self.board

        
    def show_aboutdialog(self, *args):
        self.aboutdialog.run()
        self.aboutdialog.hide()

#    def quit(self, *args):
#        Gtk.main_quit()

    def pin_high(self, pin):
        self.board.digital[int(self.pin)].write(1)
        
    def pin_low(self, pin):
        self.board.digital[int(self.pin)].write(0)

    def on_spin_changed(self, spin):
        self.pin = self.spinbutton.get_text()
        
    def advance(self, a,b):         #Move forward
        print "advance" + str(a) + " " + str(b)
        #analogWrite (E1,a);      //PWM Speed Control
        #self.board.analog[E1].write(a) 
        #self.e1.write(float(a)/255.0) 
        self.e1.write(1.0)
        #digitalWrite(M1,HIGH);  
        #self.board.digital[M1].write(1) 
        self.m1.write(1) 
        #analogWrite (E2,b);   
        #self.board.analog[E2].write(b) 
        self.e2.write(b) 
        #digitalWrite(M2,HIGH);
        #self.board.digital[M2].write(1)
        self.m2.write(1)
        
    def stop(self):         #stop
        print "stop"
#        self.board.digital[M1].write(0) 
        self.m1.write(0) 
#        self.board.digital[M2].write(0) 
        self.m2.write(0) 
        
    # Convert ADC value to key number
    def get_key(self, inp):
        for k in range(NUM_KEYS):
            if inp < ADC_KEY_VAL[k]:
                return k
             
        return -1 # No valid key pressed
    
    def read_button(self):
        print "Press some button"
        self.adc_key_in = self.board.analog[BUTTON_SENSOR].read() #read the value from the sensor
        i=0
        while (self.adc_key_in == None) and i < 10:
            print "self.board.analog[BUTTON_SENSOR].read() == None"
            time.sleep(0.50)                # wait for debounce time
            self.adc_key_in = self.board.analog[BUTTON_SENSOR].read() #read the value from the sensor
            i=i+1

        if self.adc_key_in == None:
            print "No value in analog " + str(BUTTON_SENSOR)
        else:      
            #get the key */
            self.key = self.get_key(self.adc_key_in) # convert into key press
            if self.key != self.oldkey:         # if keypress is detected
                time.sleep(0.050)                # wait for debounce time
                self.adc_key_in = self.board.analog[BUTTON_SENSOR].read()    # read the value from the sensor 
                self.key = self.get_key(self.adc_key_in)    # convert into key press
                if self.key != self.oldkey:       
                    self.oldkey = self.key
                    if self.key >= 0:
                        print self.adc_key_in
                        print MSGS[self.key]
            
                        if self.key == 0: #Move Forward
                            pass
                            # advance (SPEED,SPEED);   //move forward in max speed
                        elif self.key == 2: #Move Backward
                            pass
                            # back_off (SPEED,SPEED);   //move back in max speed
                        elif self.key == 1: #Turn Left
                            pass
                            # turn_L (TURN_SPEED,TURN_SPEED);
                        elif self.key == 3: #Turn Right
                            pass
                            # turn_R (TURN_SPEED,TURN_SPEED);
                        else:
                            pass
                            # stop();
            else:
                pass
              # stop();

    def processSensation(self, sensation):         #Move forward
        print "Romeo.processSensation number " + str(sensation.getNumber()) + " Sensation " + sensation.getSensationType() + " getLeftPower " + str(sensation.getLeftPower()) + " getRightPower " + str(sensation.getRightPower())
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            print "Romeo.processSensation Sensation.SensationType.Drive"
            #TODO Can't get anything else to worh, than motor is 1.0
            # other way it is stopped
            if sensation.getLeftPower() >= Romeo.MINPOWER:
                print "Romeo.processSensation Sensation.SensationType.Drive 1 Left " + str(sensation.getLeftPower())
                self.e2.write(sensation.getLeftPower())
                self.m2.write(1)
                print "Romeo.processSensation Sensation.SensationType.Drive self.e2.read() " + str(self.e2.read())
            elif sensation.getLeftPower() <= -Romeo.MINPOWER:
                print "Romeo.processSensation Sensation.SensationType.Drive -1 Left " + str(-sensation.getLeftPower())
                self.e2.write(-sensation.getLeftPower())
                self.m2.write(-1)
                print "Romeo.processSensation Sensation.SensationType.Drive self.e2.read() " + str(self.e2.read())
            else:
                print "Romeo.processSensation Sensation.SensationType.Drive Left 0 0"
                self.e2.write(0.0)
                self.m2.write(0)

            if sensation.getRightPower() >= Romeo.MINPOWER:
                print "Romeo.processSensation Sensation.SensationType.Drive 1 Right " + str(sensation.getRightPower())
                self.e1.write(sensation.getRightPower())
                self.m1.write(1)
                print "Romeo.processSensation Sensation.SensationType.Drive self.e2.read() " + str(self.e2.read())
            elif sensation.getRightPower() <= -Romeo.MINPOWER:
                print "Romeo.processSensation Sensation.SensationType.Drive -1 Right " + str(-sensation.getRightPower())
                self.e1.write(-sensation.getRightPower())
                self.m1.write(-1)
                print "Romeo.processSensation Sensation.SensationType.Drive self.e2.read() " + str(self.e2.read())
            else:
                print "Romeo.processSensation Sensation.SensationType.Drive 0 Right 0"
                self.e1.write(0.0)
                self.m1.write(0)

 
        
        return sensation, ""

    def test(self):
        print "Romeo.test 1"
        self.board.digital[E1].mode = SERVO
        self.e2.mode = SERVO
        for i in range(0,180):
            self.board.digital[E1].write(i)
            self.board.digital[M1].write(1)
            self.e2.write(i)
            self.board.digital[M2].write(1)
            sleep(0.015)
        for i in range(180,1,-1):
            self.board.digital[E1].write(i)
            self.board.digital[M1].write(-1)
            self.e2.write(i)
            self.board.digital[M2].write(-1)
            sleep(0.015)
        print "Romeo.test 1 end"
        
    def test2(self):
        print "Romeo.test 2"
        self.e1.mode = SERVO
        self.e2.mode = SERVO
        for i in range(0,255):
            self.e1.write(i)
            self.m1.write(1)
            self.e2.write(i)
            self.m2.write(1)
            sleep(0.015)
        for i in range(255,1,-1):
            self.e1.write(i)
            self.m1.write(-1)
            self.e2.write(i)
            self.m2.write(-1)
            sleep(0.015)
        print "Romeo.test 2 end"

if __name__ == '__main__':
    main()
