'''
Created on 22.09.2020
Updated on 22.09.2020

@author: reijo.korhonen@gmail.com

Camera is Sense type Robot
that produces Image-sensations from default camera

This works fine at least Windows-laptops with tiny cameras with 640x480 pixels
with OpenCV-library (cv2)
Linux/Ubuntu is not tested yet.

It works also with raspberry with picamera-library

'''

import os
import time
import io
import time
import math

from PIL import Image as PIL_Image

from Robot import  Robot
from Config import Config, Capabilities
from Sensation import Sensation

# prefer AlsaAidio before SoundDevice
IsPiCamera=True
#IsPiCamera=False

if IsPiCamera:
    try:
        print("Camera import picamera")
        import picamera
    except ImportError as e:
        print("Camera import picamera error " + str(e))
        IsPiCamera=False

if not IsPiCamera:
    try:
        print("Camera import cv2")
        import cv2
    except ImportError as e:
        print("Camera import cv2 error " + str(e))




class Camera(Robot):
    '''    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    TODO above implementation is mostly for Hearing Sensory and
    Moving Sensory and should be move to those implementations.  
    '''
    
    
    DATADIR='data'
    COMPARE_SQUARES=20
    CHANGE_RANGE=1000000
    SLEEP_TIME=5
  
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        print("We are in Camera, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss =  maxRss,
                       minAvailMem = minAvailMem,
                       location = location,
                       config = config)
        

          
        # from settings
        if IsPiCamera:
            self.camera = picamera.PiCamera()
            self.camera.rotation = 180
        else:
            self.camera = cv2.VideoCapture(0)   # we use default camera found
            
        self.lastImage = None

        self.running=False
        self.debug_time=time.time()
        
    def run(self):
        self.log(" Starting robot robot " + self.getName() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal

        if IsPiCamera:
            self.camera.start_preview()
            # Camera warm-up time
            time.sleep(self.SLEEP_TIME)

        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                transferDirection, sensation = self.getAxon().get()
                self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
                self.process(transferDirection=transferDirection, sensation=sensation)
            else:
                self.sense()
                
        self.log("Stopping Camera")
        self.mode = Sensation.Mode.Stopping
        if IsPiCamera:
            self.camera.close()
        else:
            self.camera.release() 
            
       
        self.log("run ALL SHUT DOWN")
        
    '''
    We can sense
    We are Sense type Robot
    '''        
    def canSense(self):
        return True 
     
    '''
    We can sense
    We are Sense type Robot
    '''        
    def sense(self):
        image = None
        if IsPiCamera:
            stream = io.BytesIO()
            self.camera.capture(stream, format=Sensation.IMAGE_FORMAT)
            self.camera.stop_preview()
            stream.seek(0)
            image = PIL_Image.open(stream)
        else:
            self.log("sense self.camera.read()")      
            ret, frame = self.camera.read()
            if ret:
                #cv2.IMREAD_COLOR
                #self.log("sense colorImage = cv2.cvtColor(frame, cv2.COLOR_BGR2COLOR)")      
                #colorImage = cv2.cvtColor(frame, cv2.COLOR_BGR2COLOR)
                #self.log("sense gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)")      
                #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # gray type is numpu.ndarray
                self.log("sense image = PIL_Image.fromarray(frame)")      
                image = PIL_Image.fromarray(frame)
            
        if image and self.isChangedImage(image):
            self.log("sense self.getParent().getAxon().put(robot=self, sensation)")
            # put robotType out (seen image) to the parent Axon going up to main Robot
            sensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
                                              image=image, locations=self.getLocations())
#            sensation.save()
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
        else:
             self.log("sense no change")
        if IsPiCamera:
            self.camera.start_preview()
            # Camera warm-up time
        time.sleep(self.SLEEP_TIME)


    '''
    compare image to previous one
    '''
           
    def isChangedImage(self, image):
        if self.lastImage is None:
            self.lastImage = image
            return True
        else:
            # calculate histogram change by squares color
            # we simply multiply color byt ins pixel count so we get roughly
            # how dark this square is
            y_size = image.size[1]/self.COMPARE_SQUARES
            x_size = image.size[0]/self.COMPARE_SQUARES
            change = 0
            for y in range(0,self.COMPARE_SQUARES):
                for x in range(0,self.COMPARE_SQUARES):
                    box = (x*x_size, y*y_size, (x+1)*x_size, (y+1)*y_size)
                    region = image.crop(box)
                    histogram = region.histogram()
                    last_region = self.lastImage.crop(box)
                    last_histogram = last_region.histogram()
                    sum=0
                    last_sum=0
                    for i in range(0,len(histogram)):
                        sum = sum+i*histogram[i]
                        last_sum = last_sum+i*last_histogram[i]
                    change = change + abs(sum-last_sum)

            self.log("isChangedImage final change " + str(change) + ' change > self.CHANGE_RANGE '+ str(change > self.CHANGE_RANGE))
            if change > self.CHANGE_RANGE:
                self.lastImage = image
                return True
            return False
      

if __name__ == "__main__":
    camera = Camera()
    camera.start()  