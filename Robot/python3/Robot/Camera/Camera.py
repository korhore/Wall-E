'''
Created on 22.09.2020
Updated on 25.11.2021

@author: reijo.korhonen@gmail.com

Camera is Sense type Robot
that produces Image-sensations from default camera

This works fine at least Windows-laptops with tiny cameras with 640x480 pixels
with OpenCV-library (cv2)
Linux/Ubuntu is not tested yet.

It works also with raspberry with picamera-library.
Robot detects installed libraries and that way chooses what library it uses.

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

# prefer picamera before cv2
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
    Raspberry-camera is supported for Raspberry and for Linuc and Windows
    we support and 
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
    
    
    DATADIR =           'data'
    COMPARE_SQUARES =   20
    SLEEP_TIME =        10
    COLORS =            3
    CHANGE_RANGE =      2000000 #int(1500000/COLORS)
  
    def __init__(self,
                 mainRobot,
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
                       mainRobot=mainRobot,
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
            pass
#             self.camera = picamera.PiCamera()
#             self.camera.rotation = 180
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

#         if IsPiCamera:
#             #self.camera.start_preview()
#             # Camera warm-up time
#             time.sleep(self.SLEEP_TIME)

        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                transferDirection, sensation = self.getAxon().get(robot=self)
                self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
                self.process(transferDirection=transferDirection, sensation=sensation)
            else:
                self.sense()
                
        self.log("Stopping Camera")
        self.mode = Sensation.Mode.Stopping
        if IsPiCamera:
            pass
#             self.camera.close()
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
        self.log(logLevel=Robot.LogLevel.Normal, logStr="sense threadSafeForgetLessImportantSensations")
        self.getMemory().threadSafeForgetLessImportantSensations()
        image = None
        if IsPiCamera:
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense camera = picamera.PiCamera()")
            camera = picamera.PiCamera()
            camera.rotation = 180
            #camera warm-up time
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense time.sleep(self.SLEEP_TIME)")
            time.sleep(self.SLEEP_TIME)
            
            stream = io.BytesIO()
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense camera.capture")
            camera.capture(stream, format=Sensation.IMAGE_FORMAT)
            #self.camera.stop_preview()
            stream.seek(0)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense image = PIL_Image.open(stream)")
            image = PIL_Image.open(stream)
            # if we don't close picamera, we will get out of memory ?   
#             self.log(logLevel=Robot.LogLevel.Normal, logStr="sense camera.close()")
#             camera.close()
#             # Finally try to delete all memory we have used, even if it should not be needed
#             del camera
#             camera = None
#             del stream
#             stream = None
#             del camera
#             camera = None
#             self.log(logLevel=Robot.LogLevel.Normal, logStr="sense camera = None")
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense self.camera.read()")      
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

        # if there are changes from previous image or if we have have item presences, that start presence, we check this image for presence changes
        # giving it for analyse for a Robot that is dedicated for that, TensorfloeClassification now.          
#        if image and (self.isChangedImage(image) or self.getMemory().hasPendingPresentItemChanges()):
        # Try without using Memory, can be locking problem
        # anyway, line above caused weird and hardly detected and corrected out of memory problem in raspberry
        if image and self.isChangedImage(image):
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense is change")
#             self.log("sense self.getParent().getAxon().put(robot=self, sensation)")
            # put robotType out (seen image) to the parent Axon going up to main Robot
            sensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense,
                                              image=image, locations=self.getLocations())
#            sensation.save()
#             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense: route(transferDirection=Sensation.TransferDirection.Direct, sensation=sensation")
            self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=sensation)
        else:
             self.log(logLevel=Robot.LogLevel.Normal, logStr="sense no change")
#         if IsPiCamera:
#             self.camera.start_preview()
#             # Camera warm-up time
        # Finally try to delete all memory we have used, even if it should not be needed
        del image
        image = None
        
        self.log(logLevel=Robot.LogLevel.Normal, logStr="sense time.sleep(self.SLEEP_TIME)")
        time.sleep(self.SLEEP_TIME)
        if IsPiCamera:
            # if we don't close picamera, we will get out of memory ?   
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense camera.close()")
            camera.close()
            # Finally try to delete all memory we have used, even if it should not be needed
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense del camera")
            del camera
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense camera = None")
            camera = None
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense del stream")
            del stream
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense stream = None")
            stream = None
            self.log(logLevel=Robot.LogLevel.Normal, logStr="sense end")


    '''
    compare image to previous one
    '''
           
    def isChangedImage(self, image):
        if self.lastImage is None:
            self.lastImage = image
            self.log("isChangedImage self.lastImage is None" )
            return True
        else:
            self.log("isChangedImage")
            # calculate histogram change by squares color
            # we simply multiply color byt ins pixel count so we get roughly
            # how dark this square is
            y_size = image.size[1]/self.COMPARE_SQUARES
            x_size = image.size[0]/self.COMPARE_SQUARES
            change = 0
#             self.log("isChangedImage 1")
            changes = []
#             self.log("isChangedImage 2")
            for i in range(0,Camera.COLORS):
#                 self.log("isChangedImage 3 {}".format(i))
                changes.append(0)
#                 self.log("isChangedImage 4 {}".format(i))
                
#             self.log("isChangedImage 5")
            for y in range(0,self.COMPARE_SQUARES):
#                 self.log("isChangedImage for y {}".format(y))
                for x in range(0,self.COMPARE_SQUARES):
#                     self.log("isChangedImage for x {}".format(x))
                    box = (x*x_size, y*y_size, (x+1)*x_size, (y+1)*y_size)
                    region = image.crop(box)
                    histogram = region.histogram()
                    last_region = self.lastImage.crop(box)
                    last_histogram = last_region.histogram()
                    sum=0
                    last_sum=0

                   # TODO Why we multiply with i?
                    #    sum = sum+i*histogram[i]
                    #    last_sum = last_sum+i*last_histogram[i]
                    colorLen = int(len(histogram)/Camera.COLORS)
#                    self.log("isChangedImage colorLen {}".format(colorLen))
#                    self.log("isChangedImage for i in range(0,Camera.COLORS {})".format(Camera.COLORS))
                    for i in range(0,Camera.COLORS):
#                         self.log("isChangedImage 6")
 #                       self.log("isChangedImage for i {}".format(i))
#                        self.log("isChangedImage  for j in range(0,colorLen {})".format(colorLen))
                        color_sum=0
                        last_color_sum=0
#                         self.log("isChangedImage 7")
                        for j in range(0,colorLen):
#                             self.log("isChangedImage 8")
#                            self.log("isChangedImage for j {}".format(j))
                            sum += j*histogram[i*colorLen +j]
                            last_sum += j*last_histogram[i*colorLen +j]
                            color_sum += j*histogram[i*colorLen +j]
                            last_color_sum += j*last_histogram[i*colorLen +j]
#                         self.log("isChangedImage 9")
                        changes[i] += abs(color_sum - last_color_sum)
#                         self.log("isChangedImage 10")
#                     self.log("isChangedImage 11")
                    change += abs(sum-last_sum)
#                     self.log("isChangedImage 12")
#                    self.log("isChangedImage change now {}".format(change ))

            self.log("isChangedImage final change  {}  change > self.CHANGE_RANGE {}".format(change, change > self.CHANGE_RANGE))
            for i in range(0,Camera.COLORS):
                self.log("isChangedImage final change by color {}  change > self.CHANGE_RANGE/Camera.COLORS {}".format(changes[i], changes[i] > self.CHANGE_RANGE/Camera.COLORS))
            if change > self.CHANGE_RANGE:
                self.lastImage = image
                return True
            return False
      

if __name__ == "__main__":
    camera = Camera()
    camera.start()  