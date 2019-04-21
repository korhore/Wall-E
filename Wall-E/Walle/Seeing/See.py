'''
Created on Jan 19, 2014

@author: reijo
'''

import sys
import alsaaudio
from threading import Thread
from queue import Queue
import math
import time

from Config import Config



class See(Thread):
    """
    See produces visual information with camera device
    """
    
    debug = False
    log = True
    
    SENSITIVITY = 1.75
    AVERAGE=55.0
    AVERAGE_SECS=10.0
    RATE=44100
    SHORT_AVERAGE_DEVIDER = 2000.0
    
    IMAGE_STOPPED = 0
    IMAGE_ONE_EYE = 1
    IMAGE_TWO_EYE = 2
    
    IMAGE_ONE_EYE_REPORT_LIMIT = 60.0

    
     
    EYE_DISTANCE = 0.25 # 0.25 m
    IMAGE_SPEED = 340.0 # 340 m/s in eye
    IMAGE_LIMIT=EYE_DISTANCE/IMAGE_SPEED # time of image to travel distance of ears

    ACCURACYFACTOR = math.pi * 5.0/180.0

    Microphones = 'Microphones'   
    left = 'left'
    right = 'right'
    calibrating_factor = 'calibrating_factor'
    calibrating_zero = 'calibrating_zero'

    
    LEFT = 0
    RIGHT = 1
    LEN_EYES=2
    
    CALIBRATING_DEVIDER = 20.0
    
    
    ear_names = [left, right]

    def __init__(self, report_queue):
        Thread.__init__(self)
        
        self.name='See'
        self.report_queue = report_queue
        
        self.image_queue = Queue()
        self.running = False
        self.canRun = True
        self.image_status = See.IMAGE_STOPPED
        self.reported = False
        self.reported_timing = False
        self.reported_level = False
        self.reported_single = False
        self.report_time=time.time()
        self.angle = 0.0
        self.reported_angle = 0.0
        self.id=See.LEFT
        #self.is_image = False
        self.is_image = [False]*See.LEN_EYES
       
        self.eye = [None]*See.LEN_EYES
        
        self.image_ear_id = See.LEFT
        self.image = [None]*See.LEN_EYES
        self.image[See.LEFT] = Sound(id=See.LEFT)
        self.image[See.RIGHT] = Sound(id=See.RIGHT)
        self.number=0
        
        self.calibrating = False
        self.calibrating_angle = 0.0
        self.calibrating_factor = 1.0
        self.calibrating_zero = 0.0

        
        self.config = configparser.RawConfigParser()
        try:
            self.config.read(CONFIG_FILE_PATH)
            left_card = self.config.get(See.Microphones, See.left)
            if left_card == None:
                print('left_card == None')
                self.canRun = False
            right_card = self.config.get(See.Microphones, See.right)
            if right_card == None:
                print('right_card == None')
                self.canRun = False
            try:
                self.calibrating_zero = self.config.getfloat(See.Microphones, See.calibrating_zero)
            except configparser.NoOptionError:
                self.calibrating_zero = 0.0
            try:
                self.calibrating_factor = self.config.getfloat(See.Microphones, See.calibrating_factor)
            except configparser.NoOptionError:
                self.calibrating_factor = 1.0
                
        except configparser.MissingSectionHeaderError:
                print('ConfigParser.MissingSectionHeaderError')
                self.canRun = False
        except configparser.NoSectionError:
                print('ConfigParser.NoSectionError')
                self.canRun = False
        except configparser.NoOptionError:
                print('ConfigParser.NoOptionError')
                self.canRun = False
        except :
                print('ConfigParser exception')
                self.canRun = False


        if self.canRun:
            self.eye[See.LEFT] = Ear(id=See.LEFT, name=See.ear_names[See.LEFT], card=left_card, average=See.AVERAGE, sensitivity=See.SENSITIVITY, queue=self.image_queue) #'Set') # card=alsaaudio.cards()[1]
            self.eye[See.RIGHT] = Ear(id=See.RIGHT, name=See.ear_names[See.RIGHT], card=right_card, average=See.AVERAGE, sensitivity=See.SENSITIVITY, queue=self.image_queue) #'Set') # card=alsaaudio.cards()[2]
        else:
            print("run 'sudo python SetUpEars.py' to set up microphones to enable See")

        
    def stop(self):
        if self.canRun:
            self.eye[See.LEFT].stop()
            self.eye[See.RIGHT].stop()
        self.running=False

    def setOn(self, on):
        self.eye[See.LEFT].setOn(on)
        self.eye[See.RIGHT].setOn(on)
       

    def run(self):
        if self.canRun:
            if See.log:
                print("Starting " + self.name)
            
            self.eye[See.LEFT].start()
            self.eye[See.RIGHT].start()
            self.running=True
    
            while self.running:
                image=self.image_queue.get()
                if See.debug:
                    print("Got image from image_queue " + See.ear_names[image.get_id()]  + " State " +  image.get_str_state() + " start_time " + str(image.get_start_time())  + " duration " + str(image.get_duration())  + " volume_level " + str(image.get_volume_level()))
                # TODO process which eye hears images first
                self.process(image)
        else:
            print("Can not start " + self.name)
            print("run 'sudo python SetUpEars.py' to set up microphones to enable Hearing")

    # TODO Logic           
    def process(self, image):
        id=image.get_id()
        other=self.other(id)
      
        if image.get_state() == Sound.START:
            self.image[id]=image
            self.reported = False       # report after image start
            self.reported_timing = False
            self.reported_level = False
            self.reported_single = False
            self.is_image[id] = True
            if  self.is_image[other]:
                self.image_status = See.IMAGE_TWO_EYE
                if See.debug:
                    print("Sound status two eye image")
            else:
                self.image_status = See.IMAGE_ONE_EYE
                self.id = id        # remember initial eye hears image first
                if See.debug:
                    print("Sound status one eye image")
       # if stop or continue and image has lasted IMAGE_LIMIT
        if image.get_state() == Sound.STOP or (image.get_state() == Sound.CONTINUE and image.get_duration() > See.IMAGE_LIMIT):
            other_image=self.image[other]
            left_image = self.image[See.LEFT]
            right_image = self.image[See.RIGHT]
            change=False
            
            # if there is not yet image from another eye, image comes from this eye's direction
            # but we can't be sure, that another image comes, so we must wait
            #
            # TODO Only got Sound from left/Right  No other image, no direction
            # TODO Maybe one eye logic should be ignored before stop of image, to make logic more simple
            # because if one eye image is reported, two eye image newer even gets change
            if self.image_status == See.IMAGE_ONE_EYE:
                #print "Sound from " + See.ear_names[id] + " No other image, no direction, other image stopped " + str( image.get_start_time() - other_image.get_stop_time())
                if image.get_start_time() - other_image.get_stop_time() < See.IMAGE_LIMIT:
                    if self.debug:
                        print("Sound from " + See.ear_names[id] + " No other image, but other image just stopped " + str( image.get_start_time() - other_image.get_stop_time()))
                    if self.debug:
                        print("Sound status two eye image")
                    if self.calibrating:
                        self.calibrate_level_to_degrees(left_image.get_volume_level(), right_image.get_volume_level())
                    self.angle = self.level_to_degrees(left_image.get_volume_level(), right_image.get_volume_level())
                    if self.debug:
                        print("Sound from " + See.ear_names[id] + " direction by volume level " + str(left_image.get_volume_level()) + ' ' + str(right_image.get_volume_level()) + " degrees " + str (self.angle))
                    #self.report_queue.put(SoundPosition(time=self.image[self.id].get_start_time(), angle=self.angle, type=See.IMAGE_TWO_EYE))
                    self.reported_level = True
                    self.report()
                else:  
                    if self.debug:
                        print("Sound from " + See.ear_names[id] + " No other image, no direction, other image stopped " + str( image.get_start_time() - other_image.get_stop_time()))
                    self.angle = self.single_image_to_degrees(self.is_image[See.LEFT], self.is_image[See.RIGHT])
                    if self.debug:
                        print("Sound from " + See.ear_names[id] + " single " + str(self.is_image[See.LEFT]) + ' ' + str(self.is_image[See.RIGHT]) + " degrees " + str (self.angle))
                    #self.report_queue.put(SoundPosition(self.angle))
            elif math.fabs(other_image.get_start_time() - image.get_start_time()) < See.IMAGE_LIMIT:
                if not self.reported_timing: # timing is reported always once per image, even if by level is reported
                    self.angle = self.timing_to_degrees(left_image.get_start_time(), right_image.get_start_time())
                    #self.report_queue.put(SoundPosition(time=self.image[self.id].get_start_time(), angle=self.angle, type=See.IMAGE_TWO_EYE))
                    self.reported_timing = True
                    self.report()
                    if self.debug or self.log:
                        print("Sound direction by TIMING reported from " + See.ear_names[id] + " has other image, direction by timing " + str(other_image.get_start_time() - image.get_start_time()) + " degrees " + str (self.angle))
                else:
                    if self.debug:
                        print("Sound direction by timing already reported from " + See.ear_names[id] + " has other image, direction by timing " + str(other_image.get_start_time() - image.get_start_time()) + " degrees " + str (self.angle))

            else:
                # TODO Two eard image is not needed to calculate yet, here it is calcilated for debug purposes, remove this
                self.angle = self.level_to_degrees(left_image.get_volume_level(), right_image.get_volume_level())
                if See.debug:
                    print("Sound direction by volume level no reported yet from " + See.ear_names[id] + ' ' + str(left_image.get_volume_level()) + ' ' + str(right_image.get_volume_level()) + " degrees " + str (self.angle))
                #self.report_queue.put(SoundPosition(self.angle))
                #self.reported = True
                   
        if image.get_state() == Sound.STOP:
            # report one eye image only rarely, wait better two eye images to come
            if (not self.reported) and ((self.image_status == See.IMAGE_TWO_EYE) or ((time.time() - self.report_time) > See.IMAGE_ONE_EYE_REPORT_LIMIT)):
                if self.calibrating:
                    self.calibrate_level_to_degrees(left_image.get_volume_level(), right_image.get_volume_level())
                    self.angle = self.level_to_degrees(left_image.get_volume_level(), right_image.get_volume_level())
                if See.debug:
                    print("Sound reported delayed from " + See.ear_names[id] + ' ' + str(left_image.get_volume_level()) + ' ' + str(right_image.get_volume_level()) + " degrees " + str (self.angle))
                #self.report_queue.put(SoundPosition(time=self.image[self.id].get_start_time(), angle=self.angle, type=self.image_status))
                self.reported_level = True
                self.report()
            else:
                if See.debug:
                    print("Sound stopped self.reported " + str(self.reported) + " self.image_status " + str(self.image_status) + " (time.time() - self.report_time) " + str((time.time() - self.report_time)))
                   
                
            self.is_image[id] = False
            
            if self.image_status == See.IMAGE_TWO_EYE:
                self.image_status = See.IMAGE_ONE_EYE
                if See.debug:
                    print("Sound status one eye image")
            else:
                self.image_status = See.IMAGE_STOPPED
                if See.debug:
                    print("Sound status stopped image")


            
    def level_to_degrees(self, leftlevel, rightlevel):
        if leftlevel == 0.0:
            return 45.0 * math.pi/180.0
        if rightlevel == 0.0:
            return -45.0 * math.pi/180.0
        
        t = self.calibrating_factor * (self.calibrating_zero + rightlevel - leftlevel)/max(leftlevel,rightlevel)
        if t < -1.0:
            t = -1.0
        if t > 1.0:
            t = 1.0
            
        return math.asin(t)

    def calibrate_level_to_degrees(self, leftlevel, rightlevel):
        if (leftlevel != 0.0) and (rightlevel != 0.0):
            if (self.calibrating_angle != 0.0) and ((self.calibrating_zero + rightlevel - leftlevel) != 0.0):
                print("Hearing calibrate_level_to_degrees self.calibrating_factor " + str(self.calibrating_factor))
                calibrating_factor = self.calibrating_angle * max(leftlevel,rightlevel)/(self.calibrating_zero + rightlevel - leftlevel)
                print("Hearing calibrate_level_to_degrees candidate calibrating_factor " + str(calibrating_factor))
                self.calibrating_factor = (((See.CALIBRATING_DEVIDER - 1.0) * self.calibrating_factor) + calibrating_factor)/See.CALIBRATING_DEVIDER
                print("Hearing calibrate_level_to_degrees new self.calibrating_factor " + str(self.calibrating_factor))
                with open(CONFIG_FILE_PATH, 'wb') as configfile:
                    self.config.set(See.Microphones, See.calibrating_factor, self.calibrating_factor)
                    self.config.write(configfile)

            else:
                print("Hearing calibrate_level_to_degrees self.calibrating_zero " + str(self.calibrating_zero))
                calibrating_zero = rightlevel - leftlevel
                print("Hearing calibrate_level_to_degrees candidate calibrating_zero " + str(calibrating_zero))
                self.calibrating_zero = (((See.CALIBRATING_DEVIDER - 1.0) * self.calibrating_zero) + calibrating_zero)/See.CALIBRATING_DEVIDER
                print("Hearing calibrate_level_to_degrees new self.calibrating_zero " + str(self.calibrating_zero))
                with open(CONFIG_FILE_PATH, 'wb') as configfile:
                    self.config.set(See.Microphones, See.calibrating_zero, self.calibrating_zero)
                    self.config.write(configfile)
           

    def timing_to_degrees(self, lefttime, righttime):
        t = ((lefttime - righttime)*See.IMAGE_SPEED)/See.EYE_DISTANCE
        if t < -0.5:
            t = -0.5
        if t > 0.5:
            t = 0.5
            
        return math.acos(t)
    
    def single_image_to_degrees(self, is_left_image, is_right_image):
        if is_left_image and is_right_image:
            return 0.0
        if (not is_left_image) and (not is_right_image):
            return 0.0
        if is_left_image:
            return -45.0 * math.pi/180.0
        return 45.0 * math.pi/180.0



 
    def analyse(self, image):
        id=image.get_id()
        self.image[id]=image
        other=self.other(id)
        other_image=self.image[other]
        change=False
        if not self.is_image[id]:
            if image.get_state() == Sound.START:
                if See.debug:
                    print("process START image from " + See.ear_names[id])
                if other_image.get_start_time() > image.get_start_time():
                    if See.debug:
                        print("process image other has later start time")
                    if other_image.get_start_time() - image.get_start_time() < See.IMAGE_LIMIT:
                        if See.debug:
                            print("in same image with other image, image state keeps same")
                    else:
                        if See.debug:
                            print("Too old image, not with other, image state keeps same")
                else:
                    if See.debug:
                        print("process this image was later")
                    if image.get_start_time() - other_image.get_stop_time() < See.IMAGE_LIMIT:
                        if See.debug:
                            print("This image start is close to other image stop, continue previous images")
                        self.is_image = True
                        change=True
                    else:
                        if See.debug:
                            print("This image start is NOT close to other image stop, start images")
                        self.image_ear_id = id
                        self.is_image = True
                        change=True
                         
        elif image.get_state() == Sound.STOP:
            if See.debug:
                print("process STOP image from " + See.ear_names[id])
            if self.image_ear_id == id:
                if See.debug:
                    print("This image stops")
                self.is_image = False
                change=True
            else:
                if See.debug:
                    print("Other image stops, image state keeps same")
                
        if change:
            if self.is_image:
                if See.debug:
                    print("IMAGE STARTED ON " + See.ear_names[self.image_ear_id])
            else:
                if See.debug:
                    print("IMAGE STOPPED ON " + See.ear_names[self.image_ear_id])

    def other(self, id):
        return (id+1) % See.LEN_EYES
    
    def report(self):
        if math.fabs(self.angle - self.reported_angle) > See.ACCURACYFACTOR:
            if See.debug:
                print("Hearing report " + str(self.angle))
            self.number = self.number+1
            self.report_queue.put(Sensation(number=self.number, sensationType=Sensation.SensationType.HearDirection, hearDirection = self.angle))
            self.reported_angle = self.angle
            self.reported = True
            self.report_time=time.time()
            if self.log:
                if self.reported_timing:
                    print("Sound by TIMING, angle " + str(self.angle))
                if self.reported_level:
                    print("Sound by LEVEL, angle " + str(self.angle))

    def setCalibrating(self, calibrating, calibrating_angle):
        self.calibrating = calibrating
        self.calibrating_angle = calibrating_angle
 
      
if __name__ == "__main__":
        #main()
        See.debug = False
        See.log = True
        
        if See.log:
            print(str(alsaaudio.cards()))
        report_queue = Queue()


        hearing=See(report_queue)
        hearing.start()
        while True:
            sensation=report_queue.get()
            #if See.debug:
            print("--> Got image_position from report_queue, sensation " + time.ctime(sensation.getTime()) + " " + str(sensation))
 
        print("__main__ exit")
        exit()
       
        
