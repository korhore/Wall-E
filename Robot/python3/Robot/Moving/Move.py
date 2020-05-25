'''
Created on Jan 19, 2014

@author: reijo.korhonen@gmail.com
'''

import sys
from threading import Thread
from threading import Timer
from queue import Queue
import math
import time

from .Romeo import Romeo
#from Romeo import Romeo
#if 'Sensation' not in sys.modules:
#    from Sensation import Sensation
from Sensation import Sensation

#from Config import Config



class Move(Thread):
    """
    Move implements moving of the robot
    """
    
    debug = False
    log = True
    MOVE_STOPPED = 0
    
 

    def __init__(self, in_queue, out_queue):
        Thread.__init__(self)
        
        self.name='Move'
        self.in_queue = in_queue
        self.out_queue = out_queue
        #self.config = config
       
        self.running = False
        self.canRun = True  # TODO from config
        self.view_status = Move.MOVE_STOPPED
        self.reported = False
        self.reported_timing = False
        self.reported_level = False
        self.reported_single = False
        self.report_time=time.time()
       
        self.romeo = None
            
        

        if self.canRun:
            self.romeo = Romeo(id=self.view_ear_id, name=self.view_ear_name, queue=self.view_queue) #'Set') # card=alsaaudio.cards()[1]
        else:
            print("run 'sudo python SetUpEars.py' to set up microphones to enable Move")

        
    def stop(self):
        if self.canRun:
            self.romeo.stop()
        self.running=False

    def isRunning(self):
        return self.running

    def setOn(self, on):
        self.romeo.setOn(on)
       

    def run(self):
        if self.canRun:
            if Move.log:
                print("Starting " + self.name)
            
            self.romeo.start()
            self.running=True
    
            while self.running:
                view=self.view_queue.get()
                if Move.debug:
                    print("Got view from view_queue " + self.view_ear_name  +   "file_path " + view.get_file_path())
                # TODO process which romeo hears views first
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
        sensation=Sensation(sensationType = Sensation.SensationType.ImageFilePath, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, imageFilePath=view.get_file_path())
        self.report_queue.put(sensation)


def stop():
        print('do Moveing.stop()')
        moving.stop()
        print('done moving.stop()')
            
       
if __name__ == "__main__":
        #main()
        Move.debug = False
        Move.log = True
        
        report_queue = Queue()


        moving=See(report_queue)
        moving.start()
        t = Timer(12.0, stop)
        t.start() # after 30 seconds,Romeo will be stopped

        while moving.isRunning():
            sensation=report_queue.get()
            #if See.debug:
            print("--> Got view_position from report_queue, sensation " + time.ctime(sensation.getTime()) + " " + str(sensation))
 
        print("__main__ exit")
        exit()
       
        
