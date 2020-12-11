'''
Created on 13.07.2019
Updated on 13.07.2020

@author: reijo.korhonen@gmail.com

This class is test class fot Muscle-type robot

'''

from Robot import Robot
from Sensation import Sensation
from Config import Config




class Muscle(Robot):
        

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
        print("We are in Muscle, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss = maxRss,
                       minAvailMem = minAvailMem,
                       location=location,
                       config=config)


        self.running=False

        
        
    '''
    We can't sense
    We are Muscle type Robot
    '''        
    def canSense(self):
        return False
     
 
