'''
Created on Jan 19, 2014

@author: reijo
'''




class Sound():
    
    START=0
    CONTINUE=1
    STOP=2
    

    def __init__(self, name, state, start_time=0.0, duration=0.0, volume_level=0.0):
        self.name=name
        self.state=state
        self.start_time=start_time
        self.duration=duration
        self.volume_level=volume_level
        
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
        
    def get_state(self):
        return self.state
    def get_str_state(self):
        if self.state == Sound.START:
            return 'Start'
        elif self.state == Sound.CONTINUE:
            return 'Continue'
        return 'Stop'
    
    def set_state(self, state):
        self.state = state
        
    def get_start_time(self):
        return self.start_time
    def set_start_time(self, start_time):
        self.start_time = start_time
        
    def get_duration(self):
        return self.duration
    def set_duration(self, duration):
        self.duration=duration
        
    def get_volume_level(self):
        return self.volume_level
    def set_volume_level(self, volume_level):
        self.volume_level=volume_level
  