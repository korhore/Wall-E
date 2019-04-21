'''
Created on Jan 19, 2014

@author: reijo
'''

import sys
from threading import Thread
from threading import Timer
from queue import Queue
import math
import time

from .Eye import Eye
#from Eye import Eye
#if 'Sensation' not in sys.modules:
#    from Sensation import Sensation
from Sensation import Sensation

#from Config import Config



class See(Thread):
    """
    See produces visual information with camera device
    """
    
    debug = False
    log = True
    VIEW_STOPPED = 0
    
 

    def __init__(self, report_queue):
        Thread.__init__(self)
        
        self.name='See'
        self.report_queue = report_queue
        #self.config = config
       
        self.view_queue = Queue()
        self.running = False
        self.canRun = True
        self.view_status = See.VIEW_STOPPED
        self.reported = False
        self.reported_timing = False
        self.reported_level = False
        self.reported_single = False
        self.report_time=time.time()
       
        self.eye = None
        
        self.view_ear_id = "camera"
        self.view_ear_name = "Rapberry PI camera"
        self.number=0
        
        

        if self.canRun:
            self.eye = Eye(id=self.view_ear_id, name=self.view_ear_name, queue=self.view_queue) #'Set') # card=alsaaudio.cards()[1]
        else:
            print("run 'sudo python SetUpEars.py' to set up microphones to enable See")

        
    def stop(self):
        if self.canRun:
            self.eye.stop()
        self.running=False

    def isRunning(self):
        return self.running

    def setOn(self, on):
        self.eye.setOn(on)
       

    def run(self):
        if self.canRun:
            if See.log:
                print("Starting " + self.name)
            
            self.eye.start()
            self.running=True
    
            while self.running:
                view=self.view_queue.get()
                if See.debug:
                    print("Got view from view_queue " + self.view_ear_name  +   "file_path " + view.get_file_path())
                # TODO process which eye hears views first
                self.process(view)
        else:
            print("Can not start " + self.name)
            print("run 'sudo python SetUpEars.py' to set up microphones to enable Hearing")

    # TODO Logic           
    def process(self, view):
        id=view.get_id()
        print(str(id) + " Processing " + view.get_file_path())
        sensation = Sensation()
        self.number = self.number+1
        sensation=Sensation(sensationType = Sensation.SensationType.ImageFilePath, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageFilePath=view.get_file_path())
        self.report_queue.put(sensation)


def stop():
        print('do seeing.stop()')
        seeing.stop()
        print('done seeing.stop()')
            
       
if __name__ == "__main__":
        #main()
        See.debug = False
        See.log = True
        
        report_queue = Queue()


        seeing=See(report_queue)
        seeing.start()
        t = Timer(12.0, stop)
        t.start() # after 30 seconds,Eye will be stopped

        while seeing.isRunning():
            sensation=report_queue.get()
            #if See.debug:
            print("--> Got view_position from report_queue, sensation " + time.ctime(sensation.getTime()) + " " + str(sensation))
 
        print("__main__ exit")
        exit()
       
        
