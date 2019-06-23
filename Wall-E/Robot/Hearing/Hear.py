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
import configparser

#from Walle.Hearing.Ear import Ear
from .Ear import Ear
#from Walle.Hearing.Sound import Sound
from .Sound import Sound
#from SoundPosition import SoundPosition
from .SoundPosition import SoundPosition
if 'Sensation' not in sys.modules:
    from Sensation import Sensation
#from Walle.Sensation import Sensation
from Config import Config



class Hear(Thread):
    """
    Hears produces location information of sounds, are they coming from left or right and what is angle.
    
    Hearing is bases on two Ears implemented physically with microphones positioning same way than man's ears.
    Ears produces sounds with volume and timing information.
    
    Theory says, that man knows location of sound 1) from timing. Sound must go longer way to that ear that is in longer way, so 
    if left ear is nearer, we hear sound first in that ear. We implement this.
    
    Unfortunately Raspberry Pi with two microphones and threading python platform is not fast enough for this, I'm afraid.
    Sound goes 340 m/s and if I can give 20cm difference of microphones, his means that faster sound is only
    0.2 m / 340 m/s = 0.000588235 seconds timing difference. That time we have for several thread changes and processing.
    This module is used to guide a robot implemented as Arduino device, so Raspberry Pi processor have another duties also.
    
    So we must do also something second best. This goes with thery, man uses this also as second way to locate by hearing.
    We will also think that if only one microphone hears a sound,
    sound comes on that direction. If there are two sounds in left and right ear, we will analyse level of sound
    and get angle of sound from that power line.
    
    There is also 3) way to analyse sound direction, use HRTF = head-related transfer function, but we will pass this.
    
    Technically we analyse sound, when we have heard it some time or it has lasted.
    """
    
    debug = False
    log = True
    
    SENSITIVITY = 1.75
    AVERAGE=55.0
    AVERAGE_SECS=10.0
    RATE=44100
    SHORT_AVERAGE_DEVIDER = 2000.0
    
    SOUND_STOPPED = 0
    SOUND_ONE_EAR = 1
    SOUND_TWO_EAR = 2
    
    SOUND_ONE_EAR_REPORT_LIMIT = 60.0

    
     
    EAR_DISTANCE = 0.25 # 0.25 m
    SOUND_SPEED = 340.0 # 340 m/s in ear
    SOUND_LIMIT=EAR_DISTANCE/SOUND_SPEED # time of sound to travel distance of ears

    ACCURACYFACTOR = math.pi * 5.0/180.0

    Microphones = 'Microphones'   
    left = 'left'
    right = 'right'
    calibrating_factor = 'calibrating_factor'
    calibrating_zero = 'calibrating_zero'

    
    LEFT = 0
    RIGHT = 1
    LEN_EARS=2
    
    CALIBRATING_DEVIDER = 20.0
    
    
    ear_names = [left, right]

    def __init__(self, report_queue):
        Thread.__init__(self)
        
        self.name='Hear'
        self.report_queue = report_queue
        
        self.sound_queue = Queue()
        self.running = False
        self.canRun = True
        self.sound_status = Hear.SOUND_STOPPED
        self.reported = False
        self.reported_timing = False
        self.reported_level = False
        self.reported_single = False
        self.report_time=time.time()
        self.angle = 0.0
        self.reported_angle = 0.0
        self.id=Hear.LEFT
        #self.is_sound = False
        self.is_sound = [False]*Hear.LEN_EARS
       
        self.ear = [None]*Hear.LEN_EARS
        
        self.sound_ear_id = Hear.LEFT
        self.sound = [None]*Hear.LEN_EARS
        self.sound[Hear.LEFT] = Sound(id=Hear.LEFT)
        self.sound[Hear.RIGHT] = Sound(id=Hear.RIGHT)
        self.number=0
        
        self.calibrating = False
        self.calibrating_angle = 0.0
        self.calibrating_factor = 1.0
        self.calibrating_zero = 0.0

        
        self.config = configparser.RawConfigParser()
        try:
            self.config.read(CONFIG_FILE_PATH)
            left_card = self.config.get(Hear.Microphones, Hear.left)
            if left_card == None:
                print('left_card == None')
                self.canRun = False
            right_card = self.config.get(Hear.Microphones, Hear.right)
            if right_card == None:
                print('right_card == None')
                self.canRun = False
            try:
                self.calibrating_zero = self.config.getfloat(Hear.Microphones, Hear.calibrating_zero)
            except configparser.NoOptionError:
                self.calibrating_zero = 0.0
            try:
                self.calibrating_factor = self.config.getfloat(Hear.Microphones, Hear.calibrating_factor)
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
            self.ear[Hear.LEFT] = Ear(id=Hear.LEFT, name=Hear.ear_names[Hear.LEFT], card=left_card, average=Hear.AVERAGE, sensitivity=Hear.SENSITIVITY, queue=self.sound_queue) #'Set') # card=alsaaudio.cards()[1]
            self.ear[Hear.RIGHT] = Ear(id=Hear.RIGHT, name=Hear.ear_names[Hear.RIGHT], card=right_card, average=Hear.AVERAGE, sensitivity=Hear.SENSITIVITY, queue=self.sound_queue) #'Set') # card=alsaaudio.cards()[2]
        else:
            print("run 'sudo python SetUpEars.py' to set up microphones to enable Hear")

        
    def stop(self):
        if self.canRun:
            self.ear[Hear.LEFT].stop()
            self.ear[Hear.RIGHT].stop()
        self.running=False

    def setOn(self, on):
        self.ear[Hear.LEFT].setOn(on)
        self.ear[Hear.RIGHT].setOn(on)
       

    def run(self):
        if self.canRun:
            if Hear.log:
                print("Starting " + self.name)
            
            self.ear[Hear.LEFT].start()
            self.ear[Hear.RIGHT].start()
            self.running=True
    
            while self.running:
                sound=self.sound_queue.get()
                if Hear.debug:
                    print("Got sound from sound_queue " + Hear.ear_names[sound.get_id()]  + " State " +  sound.get_str_state() + " start_time " + str(sound.get_start_time())  + " duration " + str(sound.get_duration())  + " volume_level " + str(sound.get_volume_level()))
                # TODO process which ear hears sounds first
                self.process(sound)
        else:
            print("Can not start " + self.name)
            print("run 'sudo python SetUpEars.py' to set up microphones to enable Hearing")

    # TODO Logic           
    def process(self, sound):
        id=sound.get_id()
        other=self.other(id)
      
        if sound.get_state() == Sound.START:
            self.sound[id]=sound
            self.reported = False       # report after sound start
            self.reported_timing = False
            self.reported_level = False
            self.reported_single = False
            self.is_sound[id] = True
            if  self.is_sound[other]:
                self.sound_status = Hear.SOUND_TWO_EAR
                if Hear.debug:
                    print("Sound status two ear sound")
            else:
                self.sound_status = Hear.SOUND_ONE_EAR
                self.id = id        # remember initial ear hears sound first
                if Hear.debug:
                    print("Sound status one ear sound")
       # if stop or continue and sound has lasted SOUND_LIMIT
        if sound.get_state() == Sound.STOP or (sound.get_state() == Sound.CONTINUE and sound.get_duration() > Hear.SOUND_LIMIT):
            other_sound=self.sound[other]
            left_sound = self.sound[Hear.LEFT]
            right_sound = self.sound[Hear.RIGHT]
            change=False
            
            # if there is not yet sound from another ear, sound comes from this ear's direction
            # but we can't be sure, that another sound comes, so we must wait
            #
            # TODO Only got Sound from left/Right  No other sound, no direction
            # TODO Maybe one ear logic should be ignored before stop of sound, to make logic more simple
            # because if one ear sound is reported, two ear sound newer even gets change
            if self.sound_status == Hear.SOUND_ONE_EAR:
                #print "Sound from " + Hear.ear_names[id] + " No other sound, no direction, other sound stopped " + str( sound.get_start_time() - other_sound.get_stop_time())
                if sound.get_start_time() - other_sound.get_stop_time() < Hear.SOUND_LIMIT:
                    if self.debug:
                        print("Sound from " + Hear.ear_names[id] + " No other sound, but other sound just stopped " + str( sound.get_start_time() - other_sound.get_stop_time()))
                    if self.debug:
                        print("Sound status two ear sound")
                    if self.calibrating:
                        self.calibrate_level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                    self.angle = self.level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                    if self.debug:
                        print("Sound from " + Hear.ear_names[id] + " direction by volume level " + str(left_sound.get_volume_level()) + ' ' + str(right_sound.get_volume_level()) + " degrees " + str (self.angle))
                    #self.report_queue.put(SoundPosition(time=self.sound[self.id].get_start_time(), angle=self.angle, type=Hear.SOUND_TWO_EAR))
                    self.reported_level = True
                    self.report()
                else:  
                    if self.debug:
                        print("Sound from " + Hear.ear_names[id] + " No other sound, no direction, other sound stopped " + str( sound.get_start_time() - other_sound.get_stop_time()))
                    self.angle = self.single_sound_to_degrees(self.is_sound[Hear.LEFT], self.is_sound[Hear.RIGHT])
                    if self.debug:
                        print("Sound from " + Hear.ear_names[id] + " single " + str(self.is_sound[Hear.LEFT]) + ' ' + str(self.is_sound[Hear.RIGHT]) + " degrees " + str (self.angle))
                    #self.report_queue.put(SoundPosition(self.angle))
            elif math.fabs(other_sound.get_start_time() - sound.get_start_time()) < Hear.SOUND_LIMIT:
                if not self.reported_timing: # timing is reported always once per sound, even if by level is reported
                    self.angle = self.timing_to_degrees(left_sound.get_start_time(), right_sound.get_start_time())
                    #self.report_queue.put(SoundPosition(time=self.sound[self.id].get_start_time(), angle=self.angle, type=Hear.SOUND_TWO_EAR))
                    self.reported_timing = True
                    self.report()
                    if self.debug or self.log:
                        print("Sound direction by TIMING reported from " + Hear.ear_names[id] + " has other sound, direction by timing " + str(other_sound.get_start_time() - sound.get_start_time()) + " degrees " + str (self.angle))
                else:
                    if self.debug:
                        print("Sound direction by timing already reported from " + Hear.ear_names[id] + " has other sound, direction by timing " + str(other_sound.get_start_time() - sound.get_start_time()) + " degrees " + str (self.angle))

            else:
                # TODO Two eard sound is not needed to calculate yet, here it is calcilated for debug purposes, remove this
                self.angle = self.level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                if Hear.debug:
                    print("Sound direction by volume level no reported yet from " + Hear.ear_names[id] + ' ' + str(left_sound.get_volume_level()) + ' ' + str(right_sound.get_volume_level()) + " degrees " + str (self.angle))
                #self.report_queue.put(SoundPosition(self.angle))
                #self.reported = True
                   
        if sound.get_state() == Sound.STOP:
            # report one ear sound only rarely, wait better two ear sounds to come
            if (not self.reported) and ((self.sound_status == Hear.SOUND_TWO_EAR) or ((time.time() - self.report_time) > Hear.SOUND_ONE_EAR_REPORT_LIMIT)):
                if self.calibrating:
                    self.calibrate_level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                    self.angle = self.level_to_degrees(left_sound.get_volume_level(), right_sound.get_volume_level())
                if Hear.debug:
                    print("Sound reported delayed from " + Hear.ear_names[id] + ' ' + str(left_sound.get_volume_level()) + ' ' + str(right_sound.get_volume_level()) + " degrees " + str (self.angle))
                #self.report_queue.put(SoundPosition(time=self.sound[self.id].get_start_time(), angle=self.angle, type=self.sound_status))
                self.reported_level = True
                self.report()
            else:
                if Hear.debug:
                    print("Sound stopped self.reported " + str(self.reported) + " self.sound_status " + str(self.sound_status) + " (time.time() - self.report_time) " + str((time.time() - self.report_time)))
                   
                
            self.is_sound[id] = False
            
            if self.sound_status == Hear.SOUND_TWO_EAR:
                self.sound_status = Hear.SOUND_ONE_EAR
                if Hear.debug:
                    print("Sound status one ear sound")
            else:
                self.sound_status = Hear.SOUND_STOPPED
                if Hear.debug:
                    print("Sound status stopped sound")


            
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
                self.calibrating_factor = (((Hear.CALIBRATING_DEVIDER - 1.0) * self.calibrating_factor) + calibrating_factor)/Hear.CALIBRATING_DEVIDER
                print("Hearing calibrate_level_to_degrees new self.calibrating_factor " + str(self.calibrating_factor))
                with open(CONFIG_FILE_PATH, 'wb') as configfile:
                    self.config.set(Hear.Microphones, Hear.calibrating_factor, self.calibrating_factor)
                    self.config.write(configfile)

            else:
                print("Hearing calibrate_level_to_degrees self.calibrating_zero " + str(self.calibrating_zero))
                calibrating_zero = rightlevel - leftlevel
                print("Hearing calibrate_level_to_degrees candidate calibrating_zero " + str(calibrating_zero))
                self.calibrating_zero = (((Hear.CALIBRATING_DEVIDER - 1.0) * self.calibrating_zero) + calibrating_zero)/Hear.CALIBRATING_DEVIDER
                print("Hearing calibrate_level_to_degrees new self.calibrating_zero " + str(self.calibrating_zero))
                with open(CONFIG_FILE_PATH, 'wb') as configfile:
                    self.config.set(Hear.Microphones, Hear.calibrating_zero, self.calibrating_zero)
                    self.config.write(configfile)
           

    def timing_to_degrees(self, lefttime, righttime):
        t = ((lefttime - righttime)*Hear.SOUND_SPEED)/Hear.EAR_DISTANCE
        if t < -0.5:
            t = -0.5
        if t > 0.5:
            t = 0.5
            
        return math.acos(t)
    
    def single_sound_to_degrees(self, is_left_sound, is_right_sound):
        if is_left_sound and is_right_sound:
            return 0.0
        if (not is_left_sound) and (not is_right_sound):
            return 0.0
        if is_left_sound:
            return -45.0 * math.pi/180.0
        return 45.0 * math.pi/180.0



 
    def analyse(self, sound):
        id=sound.get_id()
        self.sound[id]=sound
        other=self.other(id)
        other_sound=self.sound[other]
        change=False
        if not self.is_sound[id]:
            if sound.get_state() == Sound.START:
                if Hear.debug:
                    print("process START sound from " + Hear.ear_names[id])
                if other_sound.get_start_time() > sound.get_start_time():
                    if Hear.debug:
                        print("process sound other has later start time")
                    if other_sound.get_start_time() - sound.get_start_time() < Hear.SOUND_LIMIT:
                        if Hear.debug:
                            print("in same sound with other sound, sound state keeps same")
                    else:
                        if Hear.debug:
                            print("Too old sound, not with other, sound state keeps same")
                else:
                    if Hear.debug:
                        print("process this sound was later")
                    if sound.get_start_time() - other_sound.get_stop_time() < Hear.SOUND_LIMIT:
                        if Hear.debug:
                            print("This sound start is close to other sound stop, continue previous sounds")
                        self.is_sound = True
                        change=True
                    else:
                        if Hear.debug:
                            print("This sound start is NOT close to other sound stop, start sounds")
                        self.sound_ear_id = id
                        self.is_sound = True
                        change=True
                         
        elif sound.get_state() == Sound.STOP:
            if Hear.debug:
                print("process STOP sound from " + Hear.ear_names[id])
            if self.sound_ear_id == id:
                if Hear.debug:
                    print("This sound stops")
                self.is_sound = False
                change=True
            else:
                if Hear.debug:
                    print("Other sound stops, sound state keeps same")
                
        if change:
            if self.is_sound:
                if Hear.debug:
                    print("SOUND STARTED ON " + Hear.ear_names[self.sound_ear_id])
            else:
                if Hear.debug:
                    print("SOUND STOPPED ON " + Hear.ear_names[self.sound_ear_id])

    def other(self, id):
        return (id+1) % Hear.LEN_EARS
    
    def report(self):
        if math.fabs(self.angle - self.reported_angle) > Hear.ACCURACYFACTOR:
            if Hear.debug:
                print("Hearing report " + str(self.angle))
            self.number = self.number+1
            self.report_queue.put(Sensation(connections=[], number=self.number, sensationType=Sensation.SensationType.HearDirection, hearDirection = self.angle))
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
        Hear.debug = False
        Hear.log = True
        
        if Hear.log:
            print(str(alsaaudio.cards()))
        report_queue = Queue()


        hearing=Hear(report_queue)
        hearing.start()
        while True:
            sensation=report_queue.get()
            #if Hear.debug:
            print("--> Got sound_position from report_queue, sensation " + time.ctime(sensation.getTime()) + " " + str(sensation))
 
        print("__main__ exit")
        exit()
       
        
