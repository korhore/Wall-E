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


from Sensation import Sensation


'''
Just a dummy base class for moving
'''

class MoveDevice(Thread):
 
    def __init__(self, in_queue, out_queue):
        print("MoveDevice.__init__")
        Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.exist = True
        
    def exists(self):
        return self.exist

    def run(self):
        if self.canRun:
            if MoveDevice.log:
                print("Starting " + self.name)
            
            self.eye.start()
            self.running=True
    
            while self.running:
                view=self.view_queue.get()
                if MoveDevice.debug:
                    print("Got view from view_queue " + self.view_ear_name  +   "file_path " + view.get_file_path())
                # TODO process which eye hears views first
                self.process(view)
        else:
            print("Can not start " + self.name)
            print("run 'sudo python SetUpEars.py' to set up microphones to enable Hearing")
 

    # needed
    def processSensation(self, sensation):         #Move forward
        print("MoveDevice.processSensation number " + str(sensation.getNumber()) + " Sensation " + sensation.getSensationType() + " getLeftPower " + str(sensation.getLeftPower()) + " getRightPower " + str(sensation.getRightPower()))
        
        return sensation

