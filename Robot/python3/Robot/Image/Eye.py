'''
Created on Feb 24, 2013

@author: reijo
'''

import sys
import time
import getopt

from threading import Thread
from threading import Timer
from queue import Queue
isPiCamera=True
try:
    from picamera import PiCamera
except ImportError:
    isPiCamera=False

#from Walle.Sensation import Sensation
#from .Sensation import Sensation
#from Walle.Hearing.View import View
#from .View import View
from .View import View

class Eye(Thread):

    log = True
    SLEEP_TIME=2

    def __init__(self, id, name, queue):
        Thread.__init__(self)
        self.id=id
        self.name=name
        self.queue=queue
        self.running=False
        self.on=False
        if isPiCamera:
            self.camera = PiCamera()
        
        self.debug_time=time.time()

       
    def stop(self):
        print('do Eye.stop()')
        self.running=False
        
    def isRunning(self):
        return self.running

    def setOn(self, on):
        self.on = on
 
   
    def run(self):
        if not self.running:
            self.running = True
            self.on=True
            print("Starting " + self.name)
            
            len=0
    
            while self.running:
                # blocking read data from device
                #print "reading " + self.name
                if isPiCamera:
                    timestamp=time.time()
                    file_path='images/{0}.jpg'.format(timestamp)
                    self.camera.capture(file_path)
                    
                    view = View(id=timestamp, file_path=file_path)
                    self.queue.put(view)
                    time.sleep(Eye.SLEEP_TIME)
                else:
                    from os import walk

                    f = []
                    for (dirpath, dirnames, filenames) in walk('images'):
                        f.extend(filenames)
                        break
                    for filename in filenames:
                        timestamp=time.time()
                        view = View(id=timestamp, file_path=dirpath+"/"+filename)
                        self.queue.put(view)
                    self.stop()
    
    
            print("Exiting " + self.name)

def stop():
        print('do eye.stop()')
        eye.stop()
        print('done eye.stop()')

def main():
        print('main()')
        #signal.signal(signal.SIGINT, signal_handler)
        
        eye=Eye(id="camera",name = "Raspberry pi Camera") #'Set') # card=alsaaudio.cards()[1]
        eye.start()      

        t = Timer(60.0, stop)
        t.start() # after 30 seconds, Eye will be stopped

if __name__ == "__main__":
        #main()
        queue=Queue()

        eye=Eye(id="camera",name = "Raspberry pi Camera", queue=queue) 
        eye.start()
        

        t = Timer(12.0, stop)
        t.start() # after 30 seconds,Eye will be stopped
        
        while eye.isRunning():
            view=queue.get()
            print("Got view from queue")
        
        print("__main__ exit")
        exit()



