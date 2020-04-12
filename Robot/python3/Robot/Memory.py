'''
Created on 11.04.2020
Edited on 12.04.2020

@author: Reijo Korhonen, reijo.korhonen@gmail.com

Represent Memory functionality for one MainRobot and it its subrobots.
To remember you must also be able to forget.
'''

import sys
import os
import resource
import time as systemTime
from enum import Enum
import struct
import random
import math
from PIL import Image as PIL_Image
import io
import psutil
#import threading

try:
    import cPickle as pickle
#except ModuleNotFoundError:
except Exception as e:
#    print ("import cPickle as pickle error " + str(e))
    import pickle
    
from ReadWriteLock import ReadWriteLock

from Sensation import Sensation
 
    

class Memory(object):
    MIN_CACHE_MEMORABILITY = 0.1                            # starting value of min memorability in sensation cache
    min_cache_memorability = MIN_CACHE_MEMORABILITY          # current value min memorability in sensation cache
    MAX_MIN_CACHE_MEMORABILITY = 1.6                         # max value of min memorability in sensation cache we think application does something sensible
                                                             # Makes Sensory memoryType above 150s, which should be enough
    NEAR_MAX_MIN_CACHE_MEMORABILITY = 1.5                    # max value of min memorability in sensation cache we think application does something sensible
    MIN_MIN_CACHE_MEMORABILITY = 0.1                         # min value of min memorability in sensation cache we think application does everything well and no need to
                                                             # set min_cache_memorability lower
    NEAR_MIN_MIN_CACHE_MEMORABILITY = 0.2                    
    startSensationMemoryUsageLevel = 0.0                     # start memory usage level after creating first Sensation
    currentSensationMemoryUsageLevel = 0.0                   # current memory usage level when creating last Sensation
    maxRss = 384.0                                           # how much there is space for Sensation as maxim MainRobot sets this from its Config
    minAvailMem = 50.0                                       # how available momory must be left. MainRobot sets this from its Config
    process = psutil.Process(os.getpid())                    # get pid of current process, so we can calculate Process memory usage
    
    def __init__(self,
                robot,                             # owner robot
                maxRss,
                minAvailMem):
        self.robot = robot
        self.maxRss = maxRss
        self.minAvailMem =  minAvailMem
        self.sensationMemorys={                         # Sensation caches
                               Sensation.MemoryType.Sensory:  [],     # short time Sensation cache
                               Sensation.MemoryType.Working:  [],     # middle time Sensation cache
                               Sensation.MemoryType.LongTerm: [] }    # long time Sensation cache


                                       
        self.memoryLock = ReadWriteLock() # for thread_dafe Sensation cache
        
    '''
    getters, there is no need for settern
    '''
        
    def getRobot(self):
        return self.robot
    
    def getMaxRss(self):
        return self.maxRss
    
    def getMinAvailMem(self):
        return self.minAvailMem


    '''
    Constructor that takes care, that we have only one instance
    per Sensation per number
    
    This is needed if we want handle associations properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constructor
    '''
       
    def create(  self,
                 robot,                                                      # caller Robot, should be always given
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = Sensation.SensationType.Unknown,
                 memoryType=Sensation.MemoryType.Sensory,
                 direction=Sensation.Direction.In,
                 who=None,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 filePath='',
                 data=b'',
                 image=None,
                 calibrateSensationType = Sensation.SensationType.Unknown,
                 capabilities = None,                                       # capabilities of sensorys, direction what way sensation go
                 name='',                                                   # name of Item
                 presence=Sensation.Presence.Unknown,                                 # presence of Item
                 kind=Sensation.Kind.Normal):                                         # Normal kind
        if sensation == None:             # not an update, create new one
            print("Create new sensation by pure parameters for {}".format(robot.getWho()))
        else:
            print("Create new sensation by parameter sensation and parameters for {}".format(robot.getWho()))
            
        sensation = Sensation(
                 associations =  associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 robotId=robot.getId(),
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 direction=direction,
                 who=who,
                 leftPower = leftPower, rightPower = rightPower,                         # Walle motors state
                 azimuth = azimuth,                                             # Walle direction relative to magnetic north pole
                 accelerationX=accelerationX, accelerationY=accelerationY, accelerationZ=accelerationZ,   # acceleration of walle, coordinates relative to walle
                 hearDirection = hearDirection,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection = observationDirection,observationDistance = observationDistance,        # Walle's observation of something, relative to Walle
                 filePath=filePath,
                 data=data,
                 image=image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name=name,
                 presence=presence,
                 kind=kind)
        sensation.attach(robot=robot)   # always create sensation attached by creator
        self.addToSensationMemory(sensation)
        
        return sensation
    
    '''
    Add new Sensation to Sensation cache
    use memory management to avoid too much memory using
    '''
    
    def addToSensationMemory(self, sensation):
        self.memoryLock.acquireWrite()  # thread_safe                                     
        self.forgetLessImportantSensations(sensation)        
        self.sensationMemorys[sensation.getMemory()].append(sensation)        
        self.memoryLock.releaseWrite()  # thread_safe   
        
    '''
    get memory usage
    '''
    def getMemoryUsage():     
         #memUsage= resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0            
        return Memory.process.memory_info().rss/(1024*1024)              # hope this works better
    
    '''
    get available memory
    '''
    def getAvailableMemory():
        return psutil.virtual_memory().available/(1024*1024)
        
    '''
    Forget sensations that are not important
    Other way we run out of memory very soon.
    
    This method is called from semaphore protected method, so we
    should not protect this
    '''

    def forgetLessImportantSensations(self, sensation):
        numNotForgettables=0
        memoryType = self.sensationMemorys[sensation.getMemory()]

        # calibrate memorability        
        if (Memory.getMemoryUsage() > self.getMaxRss() or\
            Memory.getAvailableMemory() < self.getMinAvailMem()) and\
            self.min_cache_memorability < Memory.MAX_MIN_CACHE_MEMORABILITY:
            if self.min_cache_memorability >= Memory.NEAR_MAX_MIN_CACHE_MEMORABILITY:
                self.min_cache_memorability = self.min_cache_memorability + 0.01
            else:
                self.min_cache_memorability = self.min_cache_memorability + 0.1
        elif (Memory.getMemoryUsage() < self.getMaxRss() or\
              self.getAvailableMemory() > self.getMinAvailMem() )and\
            self.min_cache_memorability > Memory.MIN_MIN_CACHE_MEMORABILITY:
            if self.min_cache_memorability <= Memory.NEAR_MIN_MIN_CACHE_MEMORABILITY:
                self.min_cache_memorability = self.min_cache_memorability - 0.01
            else:
                self.min_cache_memorability = self.min_cache_memorability - 0.1
        
        # delete quickly last created Sensations that are not important
        while len(memoryType) > 0 and memoryType[0].isForgettable() and memoryType[0].getMemorability() < self.min_cache_memorability:
            print('delete from sensation cache {}'.format(memoryType[0].toDebugStr()))
            memoryType[0].delete()
            del memoryType[0]

        # if we are still using too much memoryType for Sensations, we should check all Sensations in the cache
        notForgettables={}
        if Memory.getMemoryUsage() > self.getMaxRss() or\
           Memory.getAvailableMemory() < self.getMinAvailMem():
            i=0
            while i < len(memoryType):
                if memoryType[i].isForgettable():
                    if memoryType[i].getMemorability() < self.min_cache_memorability:
                        print('delete from sensation cache {}'.format(memoryType[i].toDebugStr()))
                        memoryType[i].delete()
                        del memoryType[i]
                    else:
                        i=i+1
                else:
                    numNotForgettables=numNotForgettables+1
                    for robot in memoryType[i].getAttachedBy():
                        if robot.getWho() not in notForgettables:
                            notForgettables[robot.getWho()] = 1
                        else:
                            notForgettables[robot.getWho()] = notForgettables[robot.getWho()]+1
                    i=i+1
       
#        print('Sensations cache for {} {} {} {} {} {} Total memoryType usage {} MB with Sensation.min_cache_memorability {}'.\
        print('Sensations cache for {} {} {} {} {} {} Total memoryType  usage {} MB available {} MB with Sensation.min_cache_memorability {}'.\
              format(Sensation.getMemoryString(Sensation.MemoryType.Sensory), len(self.sensationMemorys[Sensation.MemoryType.Sensory]),\
                     Sensation.getMemoryString(Sensation.MemoryType.Working), len(self.sensationMemorys[Sensation.MemoryType.Working]),\
                     Sensation.getMemoryString(Sensation.MemoryType.LongTerm), len(self.sensationMemorys[Sensation.MemoryType.LongTerm]),\
                     Memory.getMemoryUsage(), Memory.getAvailableMemory(), self.min_cache_memorability))
        if numNotForgettables > 0:
            print('Sensations cache deletion skipped {} Not Forgottable Sensation'.format(numNotForgettables))
            for robotName, notForgottableNumber in notForgettables.items():
                print ('Sensations cache Not Forgottable robot {} number {}'.format(robotName, notForgottableNumber))
        #print('Memory usage for {} Sensations {} after {} MB'.format(len(memoryType), Sensation.getMemoryString(sensation.getMemory()), Sensation.getMemoryUsage()-Sensation.startSensationMemoryUsageLevel))

   