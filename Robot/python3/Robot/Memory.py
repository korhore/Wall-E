'''
Created on 11.04.2020
Edited on 22.05.2020

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
#import random
import math
from PIL import Image as PIL_Image
import io
import psutil
import math
#import threading
#from Robot import LogLevel as LogLevel
# We cannot import Robot, because Robot import us,
# so we must duplicate Robot.LogLevel definition here
from enum import Enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


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
    psutilProcess = psutil.Process(os.getpid())                    # get pid of current process, so we can calculate Process memory usage
    # Robot settings"
    MemoryLogLevel = enum(Critical='a', Error='b', Normal='c', Detailed='d', Verbose='e')
    
    def __init__(self,
                robot,                          # owner robot
                maxRss,
                minAvailMem):
        self.robot = robot
        self.maxRss = maxRss
        self.minAvailMem =  minAvailMem
        self.sensationMemory=[]                 # Sensation cache
        
        self.presentItemSensations={}           # present item.name sensations
        self.sharedSensationHosts = []          # hosts with we have already shared our sensations



                                       
        self.memoryLock = ReadWriteLock() # for thread_dafe Sensation cache
        
    '''
    getters, setters
    '''
        
    def getRobot(self):
        return self.robot
    def setRobot(self, robot):
        self.robot = robot
   
    def getMaxRss(self):
        return self.maxRss
    def setMaxRss(self, maxRss):
        self.maxRss = maxRss
   
    def getMinAvailMem(self):
        return self.minAvailMem
    def setMinAvailMem(self, minAvailMem):
        self.minAvailMem = minAvailMem


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
                 memoryType=None,
                 robotType=Sensation.RobotType.Muscle,
                 who=None,
                 locations='',
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle robotType relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 filePath='',
                 data=b'',
                 image=None,
                 calibrateSensationType = Sensation.SensationType.Unknown,
                 capabilities = None,                                       # capabilities of sensorys, robotType what way sensation go
                 name='',                                                   # name of Item
                 score = 0.0,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence=Sensation.Presence.Unknown,                       # presence of Item
                 kind=Sensation.Kind.Normal,                                # Normal kind
                 firstAssociateSensation=None,                              # associated sensation first side
                 otherAssociateSensation=None,                              # associated Sensation other side
                 feeling = Sensation.Feeling.Neutral,              # feeling of association
                 positiveFeeling=False,                                     # change association feeling to more positive robotType if possible
                 negativeFeeling=False):                                    # change association feeling to more negative robotType if possible
        if sensation == None:             # not an update, create new one
            self.log(logStr="Create new sensation by pure parameters for {}".format(robot.getWho()), logLevel=Memory.MemoryLogLevel.Normal)
        else:
            self.log(logStr="Create new sensation by parameter sensation and parameters for {}".format(robot.getWho()), logLevel=Memory.MemoryLogLevel.Normal)
            
        sensation = Sensation(
                 memory=self,
                 associations =  associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 robotId=robot.getId(),
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 robotType=robotType,
                 who=who,
                 locations=locations,
                 leftPower = leftPower, rightPower = rightPower,                         # Walle motors state
                 azimuth = azimuth,                                             # Walle robotType relative to magnetic north pole
                 accelerationX=accelerationX, accelerationY=accelerationY, accelerationZ=accelerationZ,   # acceleration of walle, coordinates relative to walle
                 hearDirection = hearDirection,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection = observationDirection,observationDistance = observationDistance,        # Walle's observation of something, relative to Walle
                 filePath=filePath,
                 data=data,
                 image=image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name = name,
                 score = score,
                 presence = presence,
                 kind = kind,
                 firstAssociateSensation = firstAssociateSensation,
                 otherAssociateSensation = otherAssociateSensation,
                 feeling = feeling,
                 positiveFeeling = positiveFeeling,
                 negativeFeeling = negativeFeeling)
        # if bytes, then same Sensation can live in many memories
        # check if we have a copy and choose newer one and delete older one
        if bytes != None:
            oldSensation = self.getSensationFromSensationMemory(id=sensation.getId())
            if oldSensation is not None:
                if oldSensation.getTime() > sensation.getTime():
                    del sensation
                    sensation=oldSensation    # keep old sensation as it is
                else:
                    #update old sensation
                    Sensation.updateBaseFields(destination=oldSensation, source=sensation)
                    for associationIds in sensation.potentialAssociations:
                        associateSensation = self.getSensationFromSensationMemory(id=associationIds.getSensationId())
                        if associateSensation is not None:
                            oldSensation.associate(sensation=associateSensation,
                                                   time = associationIds.getTime(),
                                                   feeling = associationIds.getFeeling())
                    oldSensation.receivedFrom=sensation.receivedFrom
                    del sensation
                    sensation=oldSensation           # keep old updated sensation
                sensation.attach(robot=robot)        # always create sensation attached by creator
            else:                                    # this is new sensation, all values a valid,
                sensation.associations=[]            # clear list to contain normal associations found from potentialAssociations
                for associationIds in sensation.potentialAssociations:
                    associateSensation = self.getSensationFromSensationMemory(id=associationIds.getSensationId())
                    if associateSensation is not None:
                        sensation.associate(sensation=associateSensation,
                                            time = associationIds.getTime(),
                                            feeling = associationIds.getFeeling())
                sensation.potentialAssociations=[]                        # clear potential association listl
                sensation.attach(robot=robot)        # always create sensation attached by creator
                self.addToSensationMemory(sensation) # pure new sensation must be added to memory
        else:
            sensation.attach(robot=robot)   # always create sensation attached by creator
            self.addToSensationMemory(sensation) # pure new sensation must be added to memory

        if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemoryType() == Sensation.MemoryType.Working and\
               sensation.getRobotType() == Sensation.RobotType.Sense:
               self.tracePresents(sensation)
        # assign other than Feeling sensations
        if sensation.getSensationType() != Sensation.SensationType.Feeling:
            self.assign(sensation)
        
        return sensation
    
    '''
    Add new Sensation to Sensation cache
    use memory management to avoid too much memory using
    '''
    
    def addToSensationMemory(self, sensation):
        self.memoryLock.acquireWrite()  # thread_safe                                     
        self.forgetLessImportantSensations()        
        self.sensationMemory.append(sensation)        
        self.memoryLock.releaseWrite()  # thread_safe
        
    '''
    Change sensation's memory
    We need to remove internally this sensation from one cache list to another
    '''
       
    def setMemoryType(self, sensation, memoryType):
        if sensation.getMemoryType() != memoryType:
             self.memoryLock.acquireWrite()                 # thread_safe                                     
             sensation.memoryType = memoryType
             sensation.time = systemTime.time()             # if we change memoryType, this is new Sensation, NO keep times, association handles if associated later
             self.forgetLessImportantSensations()           # must forget here. because if not created, this is only place for LongTerm-Sensations to be removed from cache
             self.memoryLock.releaseWrite()  # thread_safe

    '''
    Assign just created sensation with other present Item sensations
    TODO Study if present presentItemSensations and present functionality
    should be moved from Robot to Memory
    '''
    def assign(self, sensation):
        self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='assign: sensation ' + systemTime.ctime(sensation.getTime()) +  ' ' + sensation.toDebugStr())
        #self.getMemory().getRobot().presentItemSensations can be changed
        #TODO logic can lead to infinite loop
        succeeded = False
        while not succeeded:
            try:
                for itemSensation in self.presentItemSensations.values():
                    if sensation is not itemSensation and\
                       sensation.getTime() >=  itemSensation.getTime():
                        # and len(itemSensation.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS: #removed limitation
                        self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='assign: itemSensation= ' +  itemSensation.toDebugStr() + ' sensation= ' + sensation.toDebugStr())
                        itemSensation.associate(sensation=sensation)
                    else:
                        self.log(logLevel=Memory.MemoryLogLevel.Detailed, logStr='assign: sensation ignored not newer than present itemSensation or sensation is present itemSensation= ' + itemSensation.toDebugStr() + ' sensation= ' + sensation.toDebugStr())
                succeeded = True
            except Exception as e:
                 self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='assign: ignored exception ' + str(e))
                 succeeded = True
        
    '''
    process Sensation
    We can handle Feeling-type sensation
    '''
    def process(self, sensation):
        self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='Memory process: sensation ' + systemTime.ctime(sensation.getTime()) +  ' ' + sensation.toDebugStr())
        
        if sensation.getSensationType() == Sensation.SensationType.Feeling and\
           sensation.getFirstAssociateSensation() is not None and\
           sensation.getOtherAssociateSensation() is not None:
            sensation.getFirstAssociateSensation().associate(sensation=sensation.getOtherAssociateSensation(), 
                                                             feeling = sensation.getFeeling(),
                                                             positiveFeeling = sensation.getPositiveFeeling(),
                                                             negativeFeeling = sensation.getNegativeFeeling())
            firstFeeling = sensation.getFirstAssociateSensation().getAssociationFeeling()
            otherFeeling = sensation.getOtherAssociateSensation().getAssociationFeeling()
            if abs(firstFeeling) > abs(otherFeeling):
                return firstFeeling
            return otherFeeling 
            
            self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='Memory process: Feeling between sensations')
        else:
            self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='Memory process: No Feeling between sensations, because not Feeling sensation or parameter sensation(s) are None(s)')
 
        return None
    '''
    get memory usage
    '''
    def getMemoryUsage():     
         #memUsage= resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0            
        return Memory.psutilProcess.memory_info().rss/(1024*1024)              # hope this works better
    
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

    def forgetLessImportantSensations(self):
        numNotForgettables=0

        # calibrate memorability        
        if (Memory.getMemoryUsage() > self.getMaxRss() or\
            Memory.getAvailableMemory() < self.getMinAvailMem()) and\
            self.min_cache_memorability < Memory.MAX_MIN_CACHE_MEMORABILITY:
            if self.min_cache_memorability >= Memory.NEAR_MAX_MIN_CACHE_MEMORABILITY:
                self.min_cache_memorability = self.min_cache_memorability + 0.01
            else:
                self.min_cache_memorability = self.min_cache_memorability + 0.1
        elif (Memory.getMemoryUsage() < self.getMaxRss() or\
              Memory.getAvailableMemory() > self.getMinAvailMem() )and\
            self.min_cache_memorability > Memory.MIN_MIN_CACHE_MEMORABILITY:
            if self.min_cache_memorability <= Memory.NEAR_MIN_MIN_CACHE_MEMORABILITY:
                self.min_cache_memorability = self.min_cache_memorability - 0.01
            else:
                self.min_cache_memorability = self.min_cache_memorability - 0.1
        
        # delete quickly last created Sensations that are not important
#        while len(memoryType) > 0 and memoryType[0].isForgettable() and memoryType[0].getMemorability() < self.min_cache_memorability:
        while len(self.sensationMemory) > 0 and self.sensationMemory[0].isForgettable() and self.sensationMemory[0].getMemorability() < self.min_cache_memorability:
            self.log(logStr='delete from sensation cache {}'.format(self.sensationMemory[0].toDebugStr()), logLevel=Memory.MemoryLogLevel.Normal)
            self.sensationMemory[0].delete()
            del self.sensationMemory[0]

        # if we are still using too much self.sensationMemory for Sensations, we should check all Sensations in the cache
        notForgettablesByRobot={}
        if Memory.getMemoryUsage() > self.getMaxRss() or\
           Memory.getAvailableMemory() < self.getMinAvailMem():
            i=0
            while i < len(self.sensationMemory) and\
                  (Memory.getMemoryUsage() > self.getMaxRss() or\
                   Memory.getAvailableMemory() < self.getMinAvailMem()):
                if self.sensationMemory[i].isForgettable():
                    if self.sensationMemory[i].getMemorability() < self.min_cache_memorability:
                        self.log(logStr='delete from sensation cache {}'.format(self.sensationMemory[i].toDebugStr()), logLevel=Memory.MemoryLogLevel.Normal)
                        self.sensationMemory[i].delete()
                        del self.sensationMemory[i]
                    else:
                        i=i+1
                else:
                    numNotForgettables += 1
                    for robot in self.sensationMemory[i].getAttachedBy():
                        if robot.getWho() not in notForgettablesByRobot:
                            notForgettablesByRobot[robot.getWho()] = []
                        notForgettablesByRobot[robot.getWho()].append(self.sensationMemory[i])
                    i=i+1
       
        self.log(logStr='Sensations cache for {} Total self.sensationMemory  usage {} MB available {} MB with Sensation.min_cache_memorability {}'.\
              format(len(self.sensationMemory),\
                     Memory.getMemoryUsage(), Memory.getAvailableMemory(), self.min_cache_memorability), logLevel=Memory.MemoryLogLevel.Normal)
        if numNotForgettables > 0:
            self.log(logStr='Sensations cache deletion skipped {} Not Forgottable Sensation'.format(numNotForgettables), logLevel=Memory.MemoryLogLevel.Normal)
            for robotName, notForgottableSensations in notForgettablesByRobot.items():
                self.log(logStr='Sensations cache Not Forgottable robot {} number {}'.format(robotName, len(notForgottableSensations)), logLevel=Memory.MemoryLogLevel.Detailed)
                for notForgottableSensation in notForgottableSensations:
                    self.log(logStr='Sensations cache Not Forgottable robot {} Sensation {}'.format(robotName, notForgottableSensation.toDebugStr()), logLevel=Memory.MemoryLogLevel.Verbose)
        #self.log(logStr='Memory usage for {} Sensations {} after {} MB'.format(len(self.sensationMemory), Sensation.getMemoryTypeString(sensation.getMemoryType()), Sensation.getMemoryUsage()-Sensation.startSensationMemoryUsageLevel), logLevel=Memory.MemoryLogLevel.Normal)

    '''
    sensation getters
    '''
    def getSensationFromSensationMemory(self, id):
        if id > 0.0:
            self.memoryLock.acquireRead()                  # read thread_safe
     
            for sensation in self.sensationMemory:
                if sensation.getId() == id:
                    self.memoryLock.releaseRead()  # read thread_safe
                    return sensation
            self.memoryLock.releaseRead()                  # read thread_safe
        return None

    def getSensationsFromSensationMemory(self, associationId):
        #self.memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        self.memoryLock.acquireRead()                  # read thread_safe
        for sensation in self.sensationMemory:
            if sensation.getId() == associationId or \
                associationId in sensation.getAssociationIds():
                if not sensation in sensations:
                    sensations.append(sensation)
        memoryLock.releaseRead()                  # read thread_safe
        return sensations
                     
    '''
    Get sensations from sensation memory that are set in capabilities
    
    Time window can be set separately min, max or both,
    from time min to time max, to get sensations that are happened at same moment.   
    '''  
    def getSensations(self, capabilities, timemin=None, timemax=None):
        self.memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        for sensation in self.sensationMemory:
            # accept sensations from all Locations #locations=[]) and
            if capabilities.hasCapability(robotType=sensation.getRobotType(),
                                          memoryType=sensation.getMemoryType(),
                                          sensationType=sensation.getSensationType()) and\
                (timemin is None or sensation.getTime() > timemin) and\
                (timemax is None or sensation.getTime() < timemax):
                sensations.append(sensation)
        self.memoryLock.releaseRead()                  # read thread_safe
        return sensations
    
    '''
    prevalence of item.name per Sensation.Sensationtype.
    TODO implement first flat memory, meaning that there will not be
    per MemoryType tables
    '''
    
    def getPrevalence(self, name, sensationType):
        prevalence = 0.1
        
        self.memoryLock.acquireRead()                  # read thread_safe
        for sensation in self.sensationMemory:
            if sensation.getSensationType() == Sensation.SensationType.Item and\
               sensation.getName() == name:
                for association in sensation.getAssociations():
                    associatedSensation = association.getSensation()
                    if associatedSensation.getSensationType() == sensationType:
                         prevalence += 1.0/association.getAge() # Age from Association TODO Study Sensation.getAge()
        self.memoryLock.releaseRead()                  # read thread_safe
        
        return prevalence
        
    
    '''
    Get best specified sensation from sensation memory by score
    
    Time window can be set seperatly min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    name:           optional, if SensationTypeis Item, name must be 'name'
    notName:        optional, if SensationTypeis Item, name must not be 'notName'    
    '''
    
    def getBestSensation( self,
                          sensationType,
                          timemin,
                          timemax,
                          robotType = Sensation.RobotType.Sense,
                          name = None,
                          notName = None,
                          associationSensationType = None,
                          associationDirection = Sensation.RobotType.Sense,
                          ignoredVoiceLens=[]):
        self.memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
            
        for sensation in self.sensationMemory:
            if sensation.getSensationType() == sensationType and\
               sensation.getRobotType() == robotType and\
               sensation.hasAssociationSensationType(associationSensationType=associationSensationType,
                                                     associationDirection = associationDirection,
                                                     ignoredVoiceLens=ignoredVoiceLens) and\
               (timemin is None or sensation.getTime() > timemin) and\
               (timemax is None or sensation.getTime() < timemax):
                if sensationType != Sensation.SensationType.Item or\
                   notName is None and sensation.getName() == name or\
                   name is None and sensation.getName() != notName or\
                   name is None and notName is None:
                    if bestSensation is None or\
                       sensation.getScore() > bestSensation.getScore():
                        bestSensation = sensation
                        self.log(logStr="getBestSensation " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getScore()), logLevel=Memory.MemoryLogLevel.Normal)
        self.memoryLock.releaseRead()                  # read thread_safe
        return bestSensation
    
    '''
    Get best connected sensation by score from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
    def getBestConnectedSensation( self,
                                   sensation,
                                   sensationType,
                                   name = None):
        self.memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        for association in self.getAssociations():
            associatedSensation= association.getSensation()
            if associatedSensation.getSensationType() == sensationType:
                if sensationType != Sensation.SensationType.Item or\
                   associatedSensation.getName() == name:
                    if bestSensation is None or\
                       associatedSensation.getScore() > bestSensation.getScore():
                        bestSensation = associatedSensation
        self.memoryLock.releaseRead()                  # read thread_safe
        return bestSensation
    
    
    '''
    Get most important sensation from sensation memory by feeling and score
    
    Time window can be set seperatly min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    name:           optional, if SensationTypeis Item, name must be 'name'
    notName:        optional, if SensationTypeis Item, name must not be 'notName'    
    '''
    
    def getMostImportantSensation( self,
                                   sensationType,
                                   timemin,
                                   timemax,
                                   robotType = Sensation.RobotType.Sense,
                                   name = None,
                                   notName = None,
                                   associationSensationType = None,
                                   associationDirection = Sensation.RobotType.Sense,
                                   ignoredSensations = [],
                                   ignoredVoiceLens = [],
                                   searchLength = 10):
#                                   searchLength = Sensation.SEARCH_LENGTH):
        self.memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        bestAssociation = None
        bestAssociationSensation = None
        if name == None:
            prevalence = 0.1
        else:
            prevalence = self.getPrevalence(name=name, sensationType=sensationType)
        
        # TODO starting with best score is not a good idea
        # if best scored item.name has only bad voices, we newer can get
        # good voices
        found_candidates=0
        for sensation in self.sensationMemory:
            if sensation not in ignoredSensations and\
               sensation.getSensationType() == sensationType and\
               sensation.getRobotType() == robotType and\
               sensation.hasAssociationSensationType(associationSensationType=associationSensationType,
                                                     associationDirection = associationDirection,
                                                     ignoredSensations=ignoredSensations,
                                                     ignoredVoiceLens=ignoredVoiceLens) and\
                                                     (timemin is None or sensation.getTime() > timemin) and\
                                                     (timemax is None or sensation.getTime() < timemax):
                if sensationType != Sensation.SensationType.Item or\
                   notName is None and sensation.getName() == name or\
                   name is None and sensation.getName() != notName or\
                   name is None and notName is None:
                    bestAssociationSensationImportance = None 
                    for association in sensation.getAssociationsbBySensationType(associationSensationType=associationSensationType,
                                                                                 associationDirection = associationDirection,
                                                                                 ignoredSensations=ignoredSensations,
                                                                                 ignoredVoiceLens=ignoredVoiceLens):
                        importance = prevalence * association.getSensation().getImportance() # use prevalence and inportance to get prevalence based importance
                        if bestAssociationSensationImportance is None or\
                           bestAssociationSensationImportance < importance:
                            bestAssociationSensationImportance = importance
                            bestSensation = sensation
                            bestAssociation = association
                            bestAssociationSensation = association.getSensation()
                            #self.log(logStr="getMostImportantSensation found " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()), logLevel=Memory.MemoryLogLevel.Normal)
                            #self.log(logStr="getMostImportantSensation found bestAssociationSensation candidate " + bestAssociationSensation.toDebugStr() + ' ' + str(bestAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)
                            found_candidates +=1
                            if found_candidates >= searchLength:
                                break
                if found_candidates >= searchLength:
                    break
        if bestSensation == None:
            self.log(logStr="getMostImportantSensation did not find any", logLevel=Memory.MemoryLogLevel.Normal)
        else:
            self.log(logStr="getMostImportantSensation bestSensation {} {}".format(bestSensation.toDebugStr(),str(bestSensation.getImportance())), logLevel=Memory.MemoryLogLevel.Normal)
            self.log(logStr="getMostImportantSensation found bestAssociationSensation {} {}".format(bestAssociationSensation.toDebugStr(),str(bestAssociationSensationImportance)), logLevel=Memory.MemoryLogLevel.Normal)            
                        
                        
                        
# old logic
#                         if bestSensation is None or\
#                            sensation.getImportance() > bestSensation.getImportance():
#                             bestSensation = sensation
#                             self.log(logStr="getMostImportantSensation found candidate " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()), logLevel=Memory.MemoryLogLevel.Normal)
#         if bestSensation is not None:
#             self.log(logStr="getMostImportantSensation found " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()), logLevel=Memory.MemoryLogLevel.Normal)
#             bestAssociationSensationImportance = None 
#             for association in bestSensation.getAssociationsbBySensationType(associationSensationType=associationSensationType, ignoredSensations=ignoredSensations, ignoredVoiceLens=ignoredVoiceLens):
#                 if bestAssociationSensationImportance is None or\
#                     bestAssociationSensationImportance < association.getSensation().getImportance():
#                     bestAssociationSensationImportance = association.getSensation().getImportance()
#                     bestAssociation = association
#                     bestAssociationSensation = association.getSensation()
#                     self.log(logStr="getMostImportantSensation found bestAssociationSensation candidate " + bestAssociationSensation.toDebugStr() + ' ' + str(bestAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)
#         else:
#             self.log(logStr="getMostImportantSensation did not find any", logLevel=Memory.MemoryLogLevel.Normal)
            
        self.memoryLock.releaseRead()                  # read thread_safe
        return bestSensation, bestAssociation, bestAssociationSensation

    '''
    Get most important connected sensation by feeling and score from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
    def getMostImportantConnectedSensation( self,
                                            sensation,
                                            sensationType,
                                            name = None):
        self.memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        for association in sensation.getAssociations():
            associatedSensation= association.getSensation()
            if associatedSensation.getSensationType() == sensationType:
                if sensationType != Sensation.SensationType.Item or\
                   associatedSensation.getName() == name:
                    if bestSensation is None or\
                       associatedSensation.getImportance() > bestSensation.getImportance():
                        bestSensation = associatedSensation
        memoryLock.releaseRead()                  # read thread_safe
        return bestSensation

    '''
    save all LongTerm Memory sensation instances and data permanently
    so they can be loaded, when running app again
    '''  
    def saveLongTermMemory(self):
        # save sensations that are memorable to a file
        # there can be LOngTerm sensations in Sensation.sensationMemorys[Sensation.MemoryType.Sensory]
        # because it is allowed to change memoryType rtpe after sensation is created
        self.memoryLock.acquireRead()                  # read thread_safe
        i=0
        while i < len(self.sensationMemory):
            self.sensationMemory[i].attachedBy = []
            if self.sensationMemory[i].getMemoryType() == Sensation.MemoryType.LongTerm and\
               self.sensationMemory[i].getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY:
                self.sensationMemory[i].attachedBy = [] # clear references to Robots
                                          # they are not valid wlen loaded and they cannoc be dumped
                self.sensationMemory[i].save()
                i=i+1
            else:
                self.sensationMemory[i].delete()
                del self.sensationMemory[i]
               
        # save sensation instances
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)
            
        try:
            with open(Sensation.PATH_TO_PICLE_FILE, "wb") as f:
                try:
                    pickler = pickle.Pickler(f, -1)
                    pickler.dump(Sensation.VERSION)
                    pickler.dump(self.sensationMemory)
                    #print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm])))
                    self.log(logStr='saveLongTermMemory dumped {} sensations'.format(len(self.sensationMemory)), logLevel=Memory.MemoryLogLevel.Normal)
                except IOError as e:
                    self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) IOError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
                except pickle.PickleError as e:
                    self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PickleError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
                except pickle.PicklingError as e:
                    self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PicklingError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)

                finally:
                    f.close()
        except Exception as e:
                self.log(logStr="saveLongTermMemory open(fileName, wb) as f error " + str(e), logLevel=Memory.MemoryLogLevel.Error)
        self.memoryLock.releaseRead()                  # read thread_safe

    '''
    load LongTerm MemoryType sensation instances
    '''  
    def loadLongTermMemory(self):
        # load sensation data from files
        if os.path.exists(Sensation.DATADIR):
            self.memoryLock.acquireWrite()                  # write thread_safe
            try:
                with open(Sensation.PATH_TO_PICLE_FILE, "rb") as f:
                    try:
                        # TODO correct later
                        # whole Memory
                        #Sensation.sensationMemorys[Sensation.MemoryType.LongTerm] = \
                        version = pickle.load(f)
                        if version == Sensation.VERSION:
                            self.sensationMemory = pickle.load(f)
                            self.log(logStr='loaded {} sensations'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
                            i=0
                            while i < len(self.sensationMemory):
                                if  self.sensationMemory[i].getMemorability() <  Sensation.MIN_CACHE_MEMORABILITY:
                                    self.log(logStr='delete sensation {} {} with too low memorability {}'.format(i, self.sensationMemory[i].toDebugStr(), self.sensationMemory[i].getMemorability()), logLevel=Memory.MemoryLogLevel.Normal)
                                    self.sensationMemory[i].delete()
                                    del self.sensationMemory[i]
                                else:
                                    i=i+1
                            self.log(logStr='after load and verification {}'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
                            #print ('{} after load and verification {}'.format(Sensation.getMemoryTypeString(self.sensationMemory), len(self.sensationMemory)))
                        else:
                            self.log(logStr="Sensation could not be loaded. because Sensation cache version {} does not match current sensation version {}".format(version,Sensation.VERSION), logLevel=Memory.MemoryLogLevel.Normal)
                    except IOError as e:
                        self.log(logStr="pickle.load(f) error " + str(e), logLevel=Memory.MemoryLogLevel.Error)
                    except pickle.PickleError as e:
                        self.log(logStr='pickle.load(f) PickleError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
                    except pickle.PicklingError as e:
                        self.log(logStr='pickle.load(f) PicklingError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
                    except Exception as e:
                        self.log(logStr='pickle.load(f) Exception ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
                    finally:
                        f.close()
            except Exception as e:
                    self.log(logStr='with open(' + Sensation.PATH_TO_PICLE_FILE + ',"rb") as f error ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
            self.memoryLock.releaseWrite()                  # write thread_safe
 
    '''
    Clean data directory fron data files, that are not connected to any sensation.
    '''  
    def CleanDataDirectory(self):
        # load sensation data from files
        self.log(logStr='CleanDataDirectory', logLevel=Memory.MemoryLogLevel.Normal)
        if os.path.exists(Sensation.DATADIR):
            self.memoryLock.acquireRead()                  # read thread_safe
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    # There can be image or voice files not any more needed
                    if filename.endswith('.'+Sensation.IMAGE_FORMAT) or\
                       filename.endswith('.'+Sensation.VOICE_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        if not self.hasOwner(filepath):
                            self.log(logStr='os.remove(' + filepath + ')', logLevel=Memory.MemoryLogLevel.Normal)
                            try:
                                os.remove(filepath)
                            except Exception as e:
                                self.log(logStr='os.remove(' + filepath + ') error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
            except Exception as e:
                    self.log(logStr='os.listdir error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
            self.memoryLock.releaseRead()                  # read thread_safe
            
    '''
    hasOwner is called from methos protected by semaphore
    so we should not protect this method
    '''        
                    
    def hasOwner(self, filepath):
        for sensation in self.sensationMemory:
            if sensation.getSensationType() == Sensation.SensationType.Image or\
                sensation.getSensationType() == Sensation.SensationType.Voice:
                if sensation.getFilePath() == filepath:
                    return True
            return False

    '''
    Presence
    '''
    def tracePresents(self, sensation):
        # present means pure Present, all other if handled not present
        # if present sensations must come in order
        if sensation.getName() in self.presentItemSensations and\
           sensation.getTime() > self.presentItemSensations[sensation.getName()].getTime(): 

            if sensation.getPresence() == Sensation.Presence.Entering or\
               sensation.getPresence() == Sensation.Presence.Present or\
               sensation.getPresence() == Sensation.Presence.Exiting:
                self.presentItemSensations[sensation.getName()] = sensation
                self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())
            else:
                del self.presentItemSensations[sensation.getName()]
                self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Absent " + sensation.getName())
        # accept only sensation items that are not present, but not not in order ones
        # absent sensations don't have any mean at this case
        elif (sensation.getName() not in self.presentItemSensations) and\
             (sensation.getPresence() == Sensation.Presence.Entering or\
               sensation.getPresence() == Sensation.Presence.Present or\
               sensation.getPresence() == Sensation.Presence.Exiting):
                self.presentItemSensations[sensation.getName()] = sensation
                self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())

    def presenceToStr(self):
        namesStr=''
        for name, sensation in self.presentItemSensations.items():
            namesStr = namesStr + ' ' + name
        return namesStr
    
    '''
    log
    '''
    
    def log(self, logStr, logLevel=MemoryLogLevel.Normal):
        self.getRobot().log(logStr=logStr, logLevel=logLevel)
    
   