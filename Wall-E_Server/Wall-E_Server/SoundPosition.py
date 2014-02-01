'''
Created on Feb 1, 2014

@author: reijo
'''




class SoundPosition():
    
    # SoundPosition.START cant be used in init
    def __init__(self, time, angle, type):
        self.time=time
        self.angle=angle
        self.type=type
        
    def get_time(self):
        return self.time
    def set_time(self, time):
        self.time = time
        
    def get_angle(self):
        return self.angle
    def set_angle(self, angle):
        self.angle = angle

    def get_type(self):
        return self.type
    def set_type(self, type):
        self.type = type
