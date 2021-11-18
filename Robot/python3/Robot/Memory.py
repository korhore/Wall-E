'''
Created on 11.04.2020
Edited on 09.11.2021

@author: Reijo Korhonen, reijo.korhonen@gmail.com

Represent Memory functionality for one MainRobot and it its subrobots.
To remember you must also be able to forget.
'''

import sys
import os
import time as systemTime
from enum import Enum
import struct
import math
from PIL import Image as PIL_Image
import io
import psutil
import math
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
# TODO cannot import Robot or GLOBAL_LOCATION
#from Robot import GLOBAL_LOCATION
 
    

class Memory(object):
    GLOBAL_LOCATION = 'global'       
    MIN_CACHE_MEMORABILITY = 0.1                            # starting value of min memorability in sensation cache
    min_cache_memorability = MIN_CACHE_MEMORABILITY          # current value min memorability in sensation cache
    #MAX_MIN_CACHE_MEMORABILITY = 1.6                         # max value of min memorability in sensation cache we think application does something sensible
                                                             # Makes Sensory memoryType above 150s, which should be enough
    #NEAR_MAX_MIN_CACHE_MEMORABILITY = 1.5                    # max value of min memorability in sensation cache we think application does something sensible
    MIN_MIN_CACHE_MEMORABILITY = 0.1                         # min value of min memorability in sensation cache we think application does everything well and no need to
                                                             # set min_cache_memorability lower
    NEAR_MIN_MIN_CACHE_MEMORABILITY = 0.2                    
    startSensationMemoryUsageLevel = 0.0                     # start memory usage level after creating first Sensation
    currentSensationMemoryUsageLevel = 0.0                   # current memory usage level when creating last Sensation
    maxRss = 384.0                                           # how much there is space for Sensation as maxim MainRobot sets this from its Config
    minAvailMem = 50.0                                       # how available momory must be left. MainRobot sets this from its Config
    psutilProcess = psutil.Process(os.getpid())              # get pid of current process, so we can calculate Process memory usage
    MAX_FORGETFAILURES = 256                                 # for test 2, set higher
    # Robot settings"
    MemoryLogLevel = enum(No=-1, Critical=0, Error=1, Normal=2, Detailed=3, Verbose=4)
   
    def __init__(self,
                robot,                          # owner robot
                maxRss,
                minAvailMem):
        self.robot = robot
        self.maxRss = maxRss
        self.minAvailMem =  minAvailMem
        self.sensationMemory=[]                 # Sensation cache
        
        self._presentItemSensations={}          # present SensationType.Item.name sensations
        self._presentRobotSensations={}         # present SensationType.Robot.name sensations
        self.sharedSensationHosts = []          # hosts with we have already shared our sensations NOTE not used, logic removed or idea is not yet implemented?
                                                # NOTE sharedSensationHosts is used in Robot do don't remove this variable
                                       
        self.memoryLock = ReadWriteLock()       # for thread_safe Sensation cache
        
        self.maxMinCacheMemorability = Sensation.getMaxMinCacheMemorability()
        self.nearMaxMinCacheMemorability = self.maxMinCacheMemorability - Memory.MIN_MIN_CACHE_MEMORABILITY
        
        self.initialMemoryRssUsage = Memory.getMemoryRssUsage()
        self.initialAvailableMemory = Memory.getAvailableMemory()
        
        self.lastForgetSucceeded = True
        self.forgetFailures = 0
        self.lastMemoryRssUsage = self.initialMemoryRssUsage
        self.lastAvailableMemory = self.initialAvailableMemory
        
        
        
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
                 log=False,
                 associations = None,
                 sensation=None,
                 bytes=None,
                 binaryFilePath=None,
                 id=None,
                 #originalSensationId=None,
                 time=None,
                 receivedFrom=[],
                 # base field are by default None, so we know what fields are given and what not
                 sensationType = None,
                 memoryType = None,
                 robotType = None,
                 locations =  None,
                 #isCommunication = None,
                 mainNames = None,
                 leftPower = None, rightPower = None,                        # Walle motors state
                 azimuth = None,                                             # Walle robotType relative to magnetic north pole
                 x=None, y=None, z=None, radius=None,                        # location and acceleration of Robot
                 hearDirection = None,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection = None,observationDistance = None,     # Walle's observation of something, relative to Walle
                 filePath = None,
                 data = None,                                                # ALSA voice is string (uncompressed voice information)
                 image = None,                                               # Image internal representation is PIl.Image 
                 calibrateSensationType = None,
                 capabilities = None,                                        # capabilitis of sensorys, robotType what way sensation go
                 name = None,                                                # name of Item
                 score = None,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence = None,                                            # presence of Item
                 kind = None,                                                # kind (for instance voice)
                 firstAssociateSensation = None,                             # associated sensation first side
                 otherAssociateSensation = None,                             # associated Sensation other side
                 feeling = None,                                             # feeling of sensation or association
                 positiveFeeling = None,                                     # change association feeling to more positive robotType if possible
                 negativeFeeling = None,                                     # change association feeling to more negative robotType if possible
                 robotState = None):  
# commented out, we can get unfinite loop with log with getLocation, which uses Sensation.        
#         if log:
#             if sensation == None:             # not an update, create new one
#                 self.log(logStr="Create new sensation by pure parameters for {}".format(robot.getName()), logLevel=Memory.MemoryLogLevel.Normal)
#             else:
#                 self.log(logStr="Create new sensation by parameter sensation and parameters for {}".format(robot.getName()), logLevel=Memory.MemoryLogLevel.Normal)
            
        sensation = Sensation(
                 memory=self,
                 associations =  associations,
                 sensation=sensation,
                 bytes=bytes,
                 binaryFilePath=binaryFilePath,
                 id=id,
                 #originalSensationId=originalSensationId,
                 robotId=robot.getId(),
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 robotType=robotType,
                 robot=robot,
                 locations=locations,
                 #isCommunication=isCommunication,
                 mainNames=mainNames,
                 leftPower = leftPower, rightPower = rightPower,                         # Walle motors state
                 azimuth = azimuth,                                                      # Walle robotType relative to magnetic north pole
                 x=x, y=y, z=z, radius=radius,                                           # location and acceleration of Robot
                 hearDirection = hearDirection,                                          # sound robotType heard by Walle, relative to Walle
                 observationDirection = observationDirection,
                 observationDistance = observationDistance,                              # Walle's observation of something, relative to Walle
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
                 negativeFeeling = negativeFeeling,
                 robotState = robotState)
        # if bytes, then same Sensation can live in many memories
        # check if we have a copy and choose newer one and delete older one
        if bytes != None and binaryFilePath == None:
            oldSensation = self.getSensationFromSensationMemory(id=sensation.getId())
            if oldSensation is not None:
                if oldSensation.getTime() > sensation.getTime():
                    del sensation
                    sensation=oldSensation    # keep old sensation as it is
                else:
                    #update old sensation
                    Sensation.updateBaseFields(destination=oldSensation, source=sensation,
                                               #originalSensationId = originalSensationId,
                                               sensationType=sensationType,
                                               memoryType=memoryType,
                                               robotType=robotType,
                                               robot=robot,
                                               locations=locations,
                                               #isCommunication=isCommunication,
                                               mainNames=mainNames,
                                               leftPower=leftPower,rightPower=rightPower,                   # Walle motors state
                                               azimuth=azimuth,                                             # Walle robotType relative to magnetic north pole
                                               x=x, y=y, z=z, radius=radius,                                # location and acceleration of Robot
                                               hearDirection=hearDirection,                                 # sound robotType heard by Walle, relative to Walle
                                               observationDirection=observationDirection,
                                               observationDistance=observationDistance,                     # Walle's observation of something, relative to Walle
                                               filePath=filePath,
                                               data=data,                                                   # ALSA voice is string (uncompressed voice information)
                                               image=image,                                                 # Image internal representation is PIl.Image 
                                               calibrateSensationType=calibrateSensationType,
                                               capabilities=capabilities,                                   # capabilitis of sensorys, robotType what way sensation go
                                               name=name,                                                   # name of Item
                                               score=score,                                                 # used at least with item to define how good was the detection 0.0 - 1.0
                                               presence=presence,                                           # presence of Item
                                               kind=kind,                                                   # kind (for instance voice)
                                               firstAssociateSensation=firstAssociateSensation,             # associated sensation first side
                                               otherAssociateSensation=otherAssociateSensation,             # associated Sensation other side
                                               feeling=feeling,                                             # feeling of sensation or association
                                               positiveFeeling=positiveFeeling,                             # change association feeling to more positive robotType if possible
                                               negativeFeeling=negativeFeeling,
                                               robotState = robotState)                                       
                                               
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
               self.tracePresentItems(sensation=sensation, name = sensation.getName(), presentDict=self._presentItemSensations)
        elif sensation.getSensationType() == Sensation.SensationType.Robot and sensation.getMemoryType() == Sensation.MemoryType.Working and\
             sensation.getRobotType() == Sensation.RobotType.Communication: # and\
            if sensation.getMainNames() != self.getRobot().getMainNames():        # ignore if mainNames is from us.
               self.tracePresentItems(sensation=sensation, names = sensation.getMainNames(), presentDict=self._presentRobotSensations)
        # assign other than Feeling sensations
        if sensation.getSensationType() != Sensation.SensationType.Feeling:
            self.assign(log = log, sensation=sensation)
        
        return sensation
    
    '''
    Add new Sensation to Sensation cache
    use memory management to avoid too much memory using.
    
    If Stop, don't try to release more memory or add to SensationMemory
    this is temporary Sensation we should be able to stop with this memory
    and it can be impossible to get more so stopping can stop,
    so app does not stop.
    
    parameters
    sensation                        added sensation
    isForgetLessImportantSensations  default True, but in some test we need to
                                     set this feature False some all
                                     Sensations will be kept in Memory
                                     until implicitly deleted.
    
    '''
    
    def addToSensationMemory(self, sensation, isForgetLessImportantSensations = True):
        if sensation.getSensationType() != Sensation.SensationType.Stop:                                   
            self.memoryLock.acquireWrite()  # thread_safe
            if isForgetLessImportantSensations:
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
    '''
    def assign(self, sensation, log=False):
        if log:
            self.log(logLevel=Memory.MemoryLogLevel.Detailed, logStr='assign: sensation ' + systemTime.ctime(sensation.getTime()) +  ' ' + sensation.toDebugStr())
        #self.getMemory().getRobot().presentItemSensations can be changed
        #TODO logic can lead to infinite loop
        succeeded = False
        while not succeeded:
            try:
                for location in self._presentItemSensations.keys():
                    for itemSensation in self._presentItemSensations[location].values():
                        if sensation is not itemSensation and\
                           sensation.getTime() >=  itemSensation.getTime():
                            # and len(itemSensation.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS: #removed limitation
                            if log:
                                self.log(logLevel=Memory.MemoryLogLevel.Detailed, logStr='assign: location:' + location + ' itemSensation= ' +  itemSensation.toDebugStr() + ' sensation= ' + sensation.toDebugStr())
                            itemSensation.associate(sensation=sensation)
                        else:
                            self.log(logLevel=Memory.MemoryLogLevel.Detailed, logStr='assign: location:' + location + ' sensation ignored not newer than present itemSensation or sensation is present itemSensation= ' + itemSensation.toDebugStr() + ' sensation= ' + sensation.toDebugStr())
                succeeded = True
            except Exception as e:
                if log:
                    self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr='assign: ignored exception ' + str(e))
                succeeded = True
        
    '''
    process Sensation
    We can handle Feeling-type sensation
    
    Deprecated. All functionality will be moved to Communication
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
    def getMemoryRssUsage():     
         #memUsage= resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0            
        return Memory.psutilProcess.memory_info().rss/(1024*1024)              # hope this works better
    
    '''
    get memory usage per Sensation
    '''
    def getMemoryRssUsagePerSensation(self): 
        if len(self.sensationMemory) > 0:
            return 1024.0*(Memory.getMemoryRssUsage()-self.initialMemoryRssUsage)/len(self.sensationMemory)
        return 0
    
    
    '''
    get available memory
    '''
    def getAvailableMemory():
        return psutil.virtual_memory().available/(1024*1024)

    '''
    get memory usage per Sensation calculated by available memory
    '''
    def getUsedAvailableMemoryPerSensation(self):
        if len(self.sensationMemory) > 0:
            return 1024.0*(self.initialAvailableMemory - Memory.getAvailableMemory())/len(self.sensationMemory)
        return 0
        
    '''
    Forget sensations that are not important
    Other way we run out of memory very soon.
    
    This method is called from semaphore protected method, so we
    should not protect this
    '''

    def forgetLessImportantSensations(self):
        numNotForgettables=0
        if self.lastForgetSucceeded:
            self.lastMemoryRssUsage = Memory.getMemoryRssUsage()
            self.lastAvailableMemory = Memory.getAvailableMemory()
            self.forgetFailures=0
        triedToForget = False
        numOfForgetted = 0

        # calibrate memorability        
        if self.isLowMemory():
            # if lowmemory and memorability is lower than max limit
            # add Memorability a little
            if self.min_cache_memorability < self.maxMinCacheMemorability:
                self.min_cache_memorability = self.min_cache_memorability + 0.1
            # but if memorability is over max limit, it should be added soon to high
            # before we run out of memory
            else:
                self.min_cache_memorability = self.min_cache_memorability + 1.0
        else:
            # if we are higher than Max limit, we can make it fast lower
            if self.min_cache_memorability > self.maxMinCacheMemorability:
                self.min_cache_memorability = self.min_cache_memorability - 1.0
            # under max limit and over near min limit, lower it normal way
            elif self.min_cache_memorability > Memory.NEAR_MIN_MIN_CACHE_MEMORABILITY:
                self.min_cache_memorability = self.min_cache_memorability - 0.1
            #  near min limit, lower it little by little, so will go just under min
            elif self.min_cache_memorability > Memory.MIN_MIN_CACHE_MEMORABILITY:
               self.min_cache_memorability = self.min_cache_memorability - 0.01
        
        # delete quickly last created Sensations that are not important
#        while len(memoryType) > 0 and memoryType[0].isForgettable() and memoryType[0].getMemorability() < self.min_cache_memorability:
        while len(self.sensationMemory) > 0 and self.sensationMemory[0].isForgettable() and self.sensationMemory[0].getMemorability(allAssociations=True) < self.min_cache_memorability:
            triedToForget = True
            self.log(logStr='delete from sensation cache [0] {}'.format(self.sensationMemory[0].toDebugStr()), logLevel=Memory.MemoryLogLevel.Normal)
            self.sensationMemory[0].delete()
            del self.sensationMemory[0]
            numOfForgetted = numOfForgetted+1

        # if we are still using too much self.sensationMemory for Sensations, we should check all Sensations in the cache
        notForgettablesByRobot={}
        notForgettablesByRobotBySensationType={}
            
        if self.isLowMemory():
            i=0
            while i < len(self.sensationMemory) and self.isLowMemory():
                if self.sensationMemory[i].isForgettable():
#                    if self.sensationMemory[i].getMemorability(allAssociations=True) < self.min_cache_memorability:
                    if self.sensationMemory[i].getMemorability(allAssociations = self.min_cache_memorability < self.maxMinCacheMemorability) < self.min_cache_memorability:
                        triedToForget = True
                        # We cannot log this often, because, when memory is low and we release sensation, This is logged very often.
                        # self.log(logStr='delete from sensation cache [{}] {}'.format(i, self.sensationMemory[i].toDebugStr()), logLevel=Memory.MemoryLogLevel.Normal)
                        self.sensationMemory[i].delete()
                        del self.sensationMemory[i]
                        numOfForgetted = numOfForgetted+1
                    else:
                        i=i+1
                else:
                    numNotForgettables += 1
                    for robot in self.sensationMemory[i].getAttachedBy():
                        if robot.getName() not in notForgettablesByRobot:
                            notForgettablesByRobot[robot.getName()] = []
                            notForgettablesByRobotBySensationType[robot.getName()] = {}
                        if self.sensationMemory[i].getSensationType() not in notForgettablesByRobotBySensationType[robot.getName()]:
                            notForgettablesByRobotBySensationType[robot.getName()][self.sensationMemory[i].getSensationType()] = []
                        notForgettablesByRobot[robot.getName()].append(self.sensationMemory[i])
                        notForgettablesByRobotBySensationType[robot.getName()][self.sensationMemory[i].getSensationType()].append(self.sensationMemory[i])
                    i=i+1
       
        self.log(logStr='Sensations cache for {} Total self.sensationMemory total rss usage {} MB per sensation rss usage {} KB available total {} MB sensation usage {} KB with Sensation.min_cache_memorability {}'.\
              format(len(self.sensationMemory),\
                     Memory.getMemoryRssUsage(), self.getMemoryRssUsagePerSensation(), Memory.getAvailableMemory(), self.getUsedAvailableMemoryPerSensation(), self.min_cache_memorability), logLevel=Memory.MemoryLogLevel.Normal)
        if numNotForgettables > 0:
            self.log(logStr='Sensations cache deletion skipped {} Not Forgottable Sensation'.format(numNotForgettables), logLevel=Memory.MemoryLogLevel.Normal)
            if Memory.MemoryLogLevel.Detailed <= self.getLogLevel():
                for robotName, notForgottableSensations in notForgettablesByRobot.items():
                    self.log(logStr='Sensations cache Not Forgottable robot {} number {}'.format(robotName, len(notForgottableSensations)), logLevel=Memory.MemoryLogLevel.Detailed)
                    for notForgottableSensation in notForgottableSensations:
                        self.log(logStr='Sensations cache Not Forgottable robot {} Sensation {}'.format(robotName, notForgottableSensation.toDebugStr()), logLevel=Memory.MemoryLogLevel.Verbose)
                for robotName, notForgettablesByRobotBySensationTypes in notForgettablesByRobotBySensationType.items():
                    for sensationType, notForgettablesByRobotBySensationType in notForgettablesByRobotBySensationTypes.items():
                        self.log(logStr='Sensations cache Not Forgottable robot {} SensationType {} number {}'.format(robotName, Sensation.getSensationTypeString(sensationType), len(notForgettablesByRobotBySensationType)), logLevel=Memory.MemoryLogLevel.Detailed)
        #self.log(logStr='Memory usage for {} Sensations {} after {} MB'.format(len(self.sensationMemory), Sensation.getMemoryTypeString(sensation.getMemoryType()), Sensation.getMemoryRssUsage()-Sensation.startSensationMemoryUsageLevel), logLevel=Memory.MemoryLogLevel.Normal)
        if triedToForget:
            if Memory.getMemoryRssUsage() < self.lastMemoryRssUsage or\
               Memory.getAvailableMemory() > self.lastAvailableMemory:
                self.lastForgetSucceeded = True
                self.forgetFailures = 0
            else:
                self.lastForgetSucceeded = False
                self.forgetFailures =  self.forgetFailures +1
                if self.forgetFailures > Memory.MAX_FORGETFAILURES:
                    self.log(logStr='stopping because Sensations cache for {} Too much failures {} Total self.sensationMemory total rss usage {} MB per sensation rss usage {} KB available total {} MB sensation usage {} KB with Sensation.min_cache_memorability {}'.\
                          format(self.forgetFailures, len(self.sensationMemory),\
                                 Memory.getMemoryRssUsage(), self.getMemoryRssUsagePerSensation(), Memory.getAvailableMemory(), self.getUsedAvailableMemoryPerSensation(), self.min_cache_memorability), logLevel=Memory.MemoryLogLevel.Normal)
                    self.getRobot().stop()
                else:
                    self.log(logStr='Sensations cache for forgetFailures {}, but try continues'.format(self.forgetFailures))
        else:
            self.lastForgetSucceeded = True
            self.forgetFailures = 0

    '''
    Is Memory low
    '''
    def isLowMemory(self):
        # We cannot log this often, because, when memory is low and we release sensation, This is logged very often.
        if Memory.getMemoryRssUsage() > self.getMaxRss():
            #self.log(logStr='Sensations cache for isLowMemory Memory.getMemoryRssUsage() {} > self.getMaxRss() {}'.format(Memory.getMemoryRssUsage(), self.getMaxRss()))
            return True
        if Memory.getAvailableMemory() < self.getMinAvailMem():
            #self.log(logStr='Sensations cache for isLowMemory Memory.getAvailableMemory() {} < self.getMinAvailMem() {}'.format(Memory.getAvailableMemory(), self.getMinAvailMem()))
            return True
        return False

    '''
    sensation getter
    by Sensation id
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

                     
    '''
    TODO What we really wan't to share?
    Get sensations from sensation memory that are set in capabilities
    # or are common shared sensation (Sensationtype Robot, when we are present to others)
    
    Time window can be set separately min, max or both,
    from time min to time max, to get sensations that are happened at same moment.   
    '''  
    def getSensations(self, capabilities, sensationtypes, timemin=None, timemax=None):
        self.memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        for sensation in self.sensationMemory:
            # accept sensations from all Locations #location='') and
            # also common sensations, that don't have capability (Sensationtype.Robot)
            if sensation.getSensationType() in sensationtypes and\
              (capabilities.hasCapability(robotType=sensation.getRobotType(),
                                          memoryType=sensation.getMemoryType(),
                                          sensationType=sensation.getSensationType())) and\
                (timemin is None or sensation.getTime() > timemin) and\
                (timemax is None or sensation.getTime() < timemax):
                sensations.append(sensation)
        self.memoryLock.releaseRead()                  # read thread_safe
        return sensations
    
    '''
    prevalence of item.name per Sensation.SensationType.
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
    deprecated
    
    Get best specified sensation from sensation memory by score
    
    Time window can be set separately min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    name:           optional, if SensationTypeis Item, name must be 'name'
    notName:        optional, if SensationTypeis Item, name must not be 'notName'    
    '''
    
#     def getBestSensation( self,
#                           sensationType,
#                           timemin,
#                           timemax,
#                           robotType = Sensation.RobotType.Sense,
#                           name = None,
#                           notName = None,
#                           associationSensationType = None,
#                           associationDirection = Sensation.RobotType.Sense,
#                           ignoredVoiceLens=[]):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         bestSensation = None
#             
#         for sensation in self.sensationMemory:
#             if sensation.getSensationType() == sensationType and\
#                sensation.getRobotType() == robotType and\
#                sensation.hasAssociationSensationType(associationSensationType=associationSensationType,
#                                                      associationDirection = associationDirection,
#                                                      ignoredVoiceLens=ignoredVoiceLens) and\
#                (timemin is None or sensation.getTime() > timemin) and\
#                (timemax is None or sensation.getTime() < timemax):
#                 if sensationType != Sensation.SensationType.Item or\
#                    notName is None and sensation.getName() == name or\
#                    name is None and sensation.getName() != notName or\
#                    name is None and notName is None:
#                     if bestSensation is None or\
#                        sensation.getScore() > bestSensation.getScore():
#                         bestSensation = sensation
#                         self.log(logStr="getBestSensation " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getScore()), logLevel=Memory.MemoryLogLevel.Normal)
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return bestSensation
    
    '''
    deprecated
    
    Get best connected sensation by score from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
#     def getBestConnectedSensation( self,
#                                    sensation,
#                                    sensationType,
#                                    name = None):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         bestSensation = None
#         for association in self.getAssociations():
#             associatedSensation= association.getSensation()
#             if associatedSensation.getSensationType() == sensationType:
#                 if sensationType != Sensation.SensationType.Item or\
#                    associatedSensation.getName() == name:
#                     if bestSensation is None or\
#                        associatedSensation.getScore() > bestSensation.getScore():
#                         bestSensation = associatedSensation
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return bestSensation
    
    
    '''
    deprecated
    Get most important sensation from sensation memory by feeling and score
    
    Time window can be set seperatly min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    name:           optional, if SensationTypeis Item, name must be 'name'
    notName:        optional, if SensationTypeis Item, name must not be 'notName'    
    '''
    
#     def getMostImportantSensation( self,
#                                    sensationType,
#                                    timemin,
#                                    timemax,
#                                    robotTypes = [Sensation.RobotType.Sense,Sensation.RobotType.Communication],
#                                    name = None,
#                                    notName = None,
#                                    associationSensationType = None,
#                                    associationDirections = [Sensation.RobotType.Sense,Sensation.RobotType.Communication],
#                                    ignoredDataIds = [],
#                                    ignoredVoiceLens = [],
#                                    searchLength = 10):
# #                                   searchLength = Sensation.SEARCH_LENGTH):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         bestSensation = None
#         bestAssociation = None
#         bestAssociationSensation = None
#         if name == None:
#             prevalence = 0.1
#         else:
#             prevalence = self.getPrevalence(name=name, sensationType=sensationType)
#         
#         # TODO starting with best score is not a good idea
#         # if best scored item.name has only bad voices, we newer can get
#         # good voices
#         found_candidates=0
#         for sensation in self.sensationMemory:
#             if sensation not in ignoredDataIds and\
#                sensation.getSensationType() == sensationType and\
#                sensation.getRobotType() in robotTypes and\
#                sensation.hasAssociationSensationType(associationSensationTypes=associationSensationTypes,
#                                                      associationDirection = associationDirection,
#                                                      ignoredDataIds=ignoredDataIds,
#                                                      ignoredVoiceLens=ignoredVoiceLens) and\
#                                                      (timemin is None or sensation.getTime() > timemin) and\
#                                                      (timemax is None or sensation.getTime() < timemax):
#                 if sensationType != Sensation.SensationType.Item or\
#                    notName is None and sensation.getName() == name or\
#                    name is None and sensation.getName() != notName or\
#                    name is None and notName is None:
#                     bestAssociationSensationImportance = None 
#                     for association in sensation.getAssociationsBySensationType(associationSensationTypes=associationSensationType,
#                                                                                  associationDirection = associationDirection,
#                                                                                  ignoredDataIds=ignoredDataIds,
#                                                                                  ignoredVoiceLens=ignoredVoiceLens):
#                         importance = prevalence * association.getSensation().getImportance() # use prevalence and inportance to get prevalence based importance
#                         if bestAssociationSensationImportance is None or\
#                            bestAssociationSensationImportance < importance:
#                             bestAssociationSensationImportance = importance
#                             bestSensation = sensation
#                             bestAssociation = association
#                             bestAssociationSensation = association.getSensation()
#                             #self.log(logStr="getMostImportantSensation found " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()), logLevel=Memory.MemoryLogLevel.Normal)
#                             #self.log(logStr="getMostImportantSensation found bestAssociationSensation candidate " + bestAssociationSensation.toDebugStr() + ' ' + str(bestAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)
#                             found_candidates +=1
#                             if found_candidates >= searchLength:
#                                 break
#                 if found_candidates >= searchLength:
#                     break
#         if bestSensation == None:
#             self.log(logStr="getMostImportantSensation did not find any", logLevel=Memory.MemoryLogLevel.Normal)
#         else:
#             self.log(logStr="getMostImportantSensation bestSensation {} {}".format(bestSensation.toDebugStr(),str(bestSensation.getImportance())), logLevel=Memory.MemoryLogLevel.Normal)
#             self.log(logStr="getMostImportantSensation found bestAssociationSensation {} {}".format(bestAssociationSensation.toDebugStr(),str(bestAssociationSensationImportance)), logLevel=Memory.MemoryLogLevel.Normal)            
#                         
#                         
#                         
# # old logic
# #                         if bestSensation is None or\
# #                            sensation.getImportance() > bestSensation.getImportance():
# #                             bestSensation = sensation
# #                             self.log(logStr="getMostImportantSensation found candidate " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()), logLevel=Memory.MemoryLogLevel.Normal)
# #         if bestSensation is not None:
# #             self.log(logStr="getMostImportantSensation found " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()), logLevel=Memory.MemoryLogLevel.Normal)
# #             bestAssociationSensationImportance = None 
# #             for association in bestSensation.getAssociationsBySensationType(associationSensationType=associationSensationType, ignoredDataIds=ignoredDataIds, ignoredVoiceLens=ignoredVoiceLens):
# #                 if bestAssociationSensationImportance is None or\
# #                     bestAssociationSensationImportance < association.getSensation().getImportance():
# #                     bestAssociationSensationImportance = association.getSensation().getImportance()
# #                     bestAssociation = association
# #                     bestAssociationSensation = association.getSensation()
# #                     self.log(logStr="getMostImportantSensation found bestAssociationSensation candidate " + bestAssociationSensation.toDebugStr() + ' ' + str(bestAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)
# #         else:
# #             self.log(logStr="getMostImportantSensation did not find any", logLevel=Memory.MemoryLogLevel.Normal)
#             
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return bestSensation, bestAssociation, bestAssociationSensation

    '''
    deprecated
    
    Get best specified sensation from sensation memory by score
    
    Time window can be set separately min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    name:           optional, if SensationTypeis Item, name must be 'name'
    notName:        optional, if SensationTypeis Item, name must not be 'notName'    
    '''
    
#     def getBestSensation( self,
#                           sensationType,
#                           timemin,
#                           timemax,
#                           robotType = Sensation.RobotType.Sense,
#                           name = None,
#                           notName = None,
#                           associationSensationType = None,
#                           associationDirection = Sensation.RobotType.Sense,
#                           ignoredVoiceLens=[]):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         bestSensation = None
#             
#         for sensation in self.sensationMemory:
#             if sensation.getSensationType() == sensationType and\
#                sensation.getRobotType() == robotType and\
#                sensation.hasAssociationSensationType(associationSensationType=associationSensationType,
#                                                      associationDirection = associationDirection,
#                                                      ignoredVoiceLens=ignoredVoiceLens) and\
#                (timemin is None or sensation.getTime() > timemin) and\
#                (timemax is None or sensation.getTime() < timemax):
#                 if sensationType != Sensation.SensationType.Item or\
#                    notName is None and sensation.getName() == name or\
#                    name is None and sensation.getName() != notName or\
#                    name is None and notName is None:
#                     if bestSensation is None or\
#                        sensation.getScore() > bestSensation.getScore():
#                         bestSensation = sensation
#                         self.log(logStr="getBestSensation " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getScore()), logLevel=Memory.MemoryLogLevel.Normal)
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return bestSensation
    
    '''
    deprecated
    
    Get best connected sensation by score from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
#     def getBestConnectedSensation( self,
#                                    sensation,
#                                    sensationType,
#                                    name = None):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         bestSensation = None
#         for association in self.getAssociations():
#             associatedSensation= association.getSensation()
#             if associatedSensation.getSensationType() == sensationType:
#                 if sensationType != Sensation.SensationType.Item or\
#                    associatedSensation.getName() == name:
#                     if bestSensation is None or\
#                        associatedSensation.getScore() > bestSensation.getScore():
#                         bestSensation = associatedSensation
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return bestSensation

    '''
    Get most important communication sensations from sensation memory by feeling and score
    by Item.name
    
    returns
    
    Time window can be set separately min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    parameters
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    robotType       type of Robot (Sensation.RobotType.Sense or Sensation.RobotType.Muscle)
    name:           optional, if SensationTypeis Item, name must be 'name'
    ignoredDataIds: array of ignored Sensation Ids, used to avoid same Sensation
                       to be used in one conversation
    ignoredVoiceLens: same voice can be found in many voice Sensations.
                      used to avoid same voice, because it is rare that two different voices have exactly same length
    ignoredImageLens: same image can be found in many image Sensations.
                      used to avoid same image, because it is rare that two different images have exactly same length
    
    return
    itemSensation
    voiceSensation
    voiceAssociation
    imageSensation
    imageAssociation
      
    '''
    
    def getMostMemorableSensations( self,
                                   itemSensations,
                                   robotMainNames,
                                   robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                   associationSensationType = None,
                                   ignoredDataIds = [],
                                   searchLength = 10):
#                                   searchLength = Sensation.SEARCH_LENGTH):
        self.memoryLock.acquireRead()                  # read thread_safe
        Memory.Memory = None
        itemSensation = None
        voiceSensation = None
        voiceAssociation = None
        imageSensation = None
        imageAssociation = None
        names=[]
        if sensations != None:
            for sensation in itemSensations:
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    names.append(sensation.getName())
        
        # TODO starting with best score is not a good idea
        # if best scored item.name has only bad voices, we newer can get
        # good voices
        found_voice_candidates=0
               #self.getMainNamesRobotType(robotType=sensation.getRobotType(), robotMainNames=mainNames, sensationMainNames=sensation.getMainNames()) == robotType and\
        for sensation in self.sensationMemory:
            if sensation.getDataId() not in ignoredDataIds and\
               sensation.getSensationType() == Sensation.SensationType.Item and\
               sensation.getName() in names and\
               sensation.getRobotType() in robotTypes and\
               sensation.hasAssociationSensationType(associationSensationType = Sensation.SensationType.Voice,
                                                     associationDirections = robotTypes,
                                                     ignoredDataIds = ignoredDataIds,
                                                     robotMainNames = robotMainNames):
# Enable this, when test is corrected
#                sensation.hasAssociationSensationType(associationSensationType=Sensation.SensationType.Image,
#                                                      associationDirection = robotType,
#                                                      ignoredDataIds=ignoredDataIds,
#                                                      ignoredImageLens=ignoredImageLens) and\
                bestVoiceAssociationSensationImportance = None 
                for association in sensation.getAssociationsBySensationType(associationSensationType=Sensation.SensationType.Voice,
                                                                            associationDirections = robotTypes,
                                                                            ignoredDataIds = ignoredDataIds,
                                                                            robotMainNames = robotMainNames):
                    importance = prevalence * association.getSensation().getImportance() # use prevalence and importance to get prevalence based importance
                    if bestVoiceAssociationSensationImportance is None or\
                       bestVoiceAssociationSensationImportance < importance:
                        bestVoiceAssociationSensationImportance = importance
                        itemSensation = sensation
                        voiceAssociation = association
                        voiceSensation = association.getSensation()
                        found_voice_candidates +=1
                        if found_voice_candidates >= searchLength:
                            break
            if found_voice_candidates >= searchLength:
                break

        # TODO find independently nest image until we will find a way how to find best image assosiated both item and voice
        found_image_candidates=0
        for sensation in self.sensationMemory:
            if sensation.getDataId() not in ignoredDataIds and\
               sensation.getSensationType() == Sensation.SensationType.Item and\
               sensation.getName() == name and\
               sensation.getRobotType() in robotTypes and\
               sensation.hasAssociationSensationType(associationSensationType = Sensation.SensationType.Image,
                                                     associationDirections = robotTypes,
                                                     ignoredDataIds = ignoredDataIds,
                                                     robotMainNames = robotMainNames) and\
               (timemin is None or sensation.getTime() > timemin) and\
               (timemax is None or sensation.getTime() < timemax):

                bestImageAssociationSensationImportance = None 
                for association in sensation.getAssociationsBySensationType(associationSensationType=Sensation.SensationType.Image,
                                                                             associationDirections = robotTypes,
                                                                             ignoredDataIds = ignoredDataIds,
                                                                             robotMainNames = robotMainNames):
                    importance = prevalence * association.getSensation().getImportance() # use prevalence and importance to get prevalence based importance
                    if bestImageAssociationSensationImportance is None or\
                       bestImageAssociationSensationImportance < importance:
                        bestImageAssociationSensationImportance = importance
                        #itemSensation = sensation
                        imageAssociation = association
                        imageSensation = association.getSensation()
                        found_image_candidates +=1
                        if found_image_candidates >= searchLength:
                            break
            if found_image_candidates >= searchLength:
                break
        
        
        
        if itemSensation == None:
            self.log(logStr="getMostImportantSensation did not find any", logLevel=Memory.MemoryLogLevel.Normal)
        else:
            self.log(logStr="getMostImportantSensation itemSensation {} {}".format(itemSensation.toDebugStr(),str(itemSensation.getImportance())), logLevel=Memory.MemoryLogLevel.Normal)
        if voiceSensation != None:
            self.log(logStr="getMostImportantSensation found voiceSensation {} {}".format(voiceSensation.toDebugStr(),bestVoiceAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)            
        if imageSensation != None:
            self.log(logStr="getMostImportantSensation found imageSensation {} {}".format(imageSensation.toDebugStr(),bestImageAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)            
                                    
        if itemSensation is not None:
            assert itemSensation.getDataId() not in ignoredDataIds
        if voiceSensation is not None:
            assert voiceSensation.getDataId() not in ignoredDataIds

        self.memoryLock.releaseRead()                  # read thread_safe
        return itemSensation, voiceSensation, voiceAssociation, imageSensation, imageAssociation
    
    
    '''
    deprecated 
    Get most important communication sensations from sensation memory by feeling and score
    by Item.name
    
    returns
    
    Time window can be set seperatly min, max or both,
    from time min to time max, to get sensations that are happened at same moment.
    
    parameters
    
    sensationType:  SensationType
    timemin:        minimum time
    timemax:        maximun time
    robotType       type of Robot (Sensation.RobotType.Sense or Sensation.RobotType.Muscle)
    name:           optional, if SensationTypeis Item, name must be 'name'
    ignoredDataIds: array of ignored Sensation Ids, used to avoid same Sensation
                       to be used in one conversation
    ignoredVoiceLens: same voice can be found in many voice Sensations.
                      used to avoid same voice, because it is rare that two different voices have exactly same length
    ignoredImageLens: same image can be found in many image Sensations.
                      used to avoid same image, because it is rare that two different images have exactly same length
    
    return
    itemSensation
    voiceSensation
    voiceAssociation
    imageSensation
    imageAssociation
      
    '''
    
#     def getMostImportantCommunicationSensations( self,
#                                    timemin,
#                                    timemax,
#                                    robotMainNames,
#                                    robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
#                                    name = None,
#                                    notName = None,
#                                    associationSensationType = None,
#                                    #associationDirection = Sensation.RobotType.Sense,
#                                    ignoredDataIds = [],
#                                    searchLength = 10):
# #                                   searchLength = Sensation.SEARCH_LENGTH):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         Memory.Memory = None
#         itemSensation = None
#         voiceSensation = None
#         voiceAssociation = None
#         imageSensation = None
#         imageAssociation = None
#         if name == None:
#             prevalence = 0.1
#         else:
#             prevalence = self.getPrevalence(name=name, sensationType=Sensation.SensationType.Item)
#         
#         # TODO starting with best score is not a good idea
#         # if best scored item.name has only bad voices, we newer can get
#         # good voices
#         found_voice_candidates=0
#                #self.getMainNamesRobotType(robotType=sensation.getRobotType(), robotMainNames=mainNames, sensationMainNames=sensation.getMainNames()) == robotType and\
#         for sensation in self.sensationMemory:
#             if sensation.getDataId() not in ignoredDataIds and\
#                sensation.getSensationType() == Sensation.SensationType.Item and\
#                sensation.getName() == name and\
#                sensation.getRobotType() in robotTypes and\
#                sensation.hasAssociationSensationType(associationSensationType = Sensation.SensationType.Voice,
#                                                      associationDirections = robotTypes,
#                                                      ignoredDataIds = ignoredDataIds,
#                                                      robotMainNames = robotMainNames) and\
#                (timemin is None or sensation.getTime() > timemin) and\
#                (timemax is None or sensation.getTime() < timemax):
# # Enable this, when test is corrected
# #                sensation.hasAssociationSensationType(associationSensationType=Sensation.SensationType.Image,
# #                                                      associationDirection = robotType,
# #                                                      ignoredDataIds=ignoredDataIds,
# #                                                      ignoredImageLens=ignoredImageLens) and\
#                 bestVoiceAssociationSensationImportance = None 
#                 for association in sensation.getAssociationsBySensationType(associationSensationType=Sensation.SensationType.Voice,
#                                                                             associationDirections = robotTypes,
#                                                                             ignoredDataIds = ignoredDataIds,
#                                                                             robotMainNames = robotMainNames):
#                     importance = prevalence * association.getSensation().getImportance() # use prevalence and importance to get prevalence based importance
#                     if bestVoiceAssociationSensationImportance is None or\
#                        bestVoiceAssociationSensationImportance < importance:
#                         bestVoiceAssociationSensationImportance = importance
#                         itemSensation = sensation
#                         voiceAssociation = association
#                         voiceSensation = association.getSensation()
#                         found_voice_candidates +=1
#                         if found_voice_candidates >= searchLength:
#                             break
#             if found_voice_candidates >= searchLength:
#                 break
# 
#         # TODO find independently nest image until we will find a way how to find best image assosiated both item and voice
#         found_image_candidates=0
#         for sensation in self.sensationMemory:
#             if sensation.getDataId() not in ignoredDataIds and\
#                sensation.getSensationType() == Sensation.SensationType.Item and\
#                sensation.getName() == name and\
#                sensation.getRobotType() in robotTypes and\
#                sensation.hasAssociationSensationType(associationSensationType = Sensation.SensationType.Image,
#                                                      associationDirections = robotTypes,
#                                                      ignoredDataIds = ignoredDataIds,
#                                                      robotMainNames = robotMainNames) and\
#                (timemin is None or sensation.getTime() > timemin) and\
#                (timemax is None or sensation.getTime() < timemax):
# 
#                 bestImageAssociationSensationImportance = None 
#                 for association in sensation.getAssociationsBySensationType(associationSensationType=Sensation.SensationType.Image,
#                                                                              associationDirections = robotTypes,
#                                                                              ignoredDataIds = ignoredDataIds,
#                                                                              robotMainNames = robotMainNames):
#                     importance = prevalence * association.getSensation().getImportance() # use prevalence and importance to get prevalence based importance
#                     if bestImageAssociationSensationImportance is None or\
#                        bestImageAssociationSensationImportance < importance:
#                         bestImageAssociationSensationImportance = importance
#                         #itemSensation = sensation
#                         imageAssociation = association
#                         imageSensation = association.getSensation()
#                         found_image_candidates +=1
#                         if found_image_candidates >= searchLength:
#                             break
#             if found_image_candidates >= searchLength:
#                 break
#         
#         
#         
#         if itemSensation == None:
#             self.log(logStr="getMostImportantSensation did not find any", logLevel=Memory.MemoryLogLevel.Normal)
#         else:
#             self.log(logStr="getMostImportantSensation itemSensation {} {}".format(itemSensation.toDebugStr(),str(itemSensation.getImportance())), logLevel=Memory.MemoryLogLevel.Normal)
#         if voiceSensation != None:
#             self.log(logStr="getMostImportantSensation found voiceSensation {} {}".format(voiceSensation.toDebugStr(),bestVoiceAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)            
#         if imageSensation != None:
#             self.log(logStr="getMostImportantSensation found imageSensation {} {}".format(imageSensation.toDebugStr(),bestImageAssociationSensationImportance), logLevel=Memory.MemoryLogLevel.Normal)            
#                                     
#         if itemSensation is not None:
#             assert itemSensation.getDataId() not in ignoredDataIds
#         if voiceSensation is not None:
#             assert voiceSensation.getDataId() not in ignoredDataIds
# 
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return itemSensation, voiceSensation, voiceAssociation, imageSensation, imageAssociation

# deprecated   
#     '''
#     Reverse robotType in foreign mainNames
#     '''
#     def getMainNamesRobotType(self, robotType, robotMainNames, sensationMainNames):
#         if self.isInMainNames(robotMainNames=robotMainNames, sensationMainNames=sensationMainNames):
#             return robotType
#         if robotType == Sensation.RobotType.Muscle:
#             return Sensation.RobotType.Sense
#         return Sensation.RobotType.Muscle
#     
#     '''
#     Is this Robot at least in one of mainNames
#     '''
#     def isInMainNames(self, robotMainNames, sensationMainNames):
#         if sensationMainNames is None or len(sensationMainNames) == 0 or\
#            robotMainNames is None or len(robotMainNames) == 0:
#             return True
#         
#         for mainName in robotMainNames:
#             if mainName in sensationMainNames:
#                  return True            
#         return False

    '''
    
    deprecated
    Get most important connected sensation by feeling and score from this specified Sensation
    Not used now
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
#     def getMostImportantConnectedSensation( self,
#                                             sensation,
#                                             sensationType,
#                                             name = None):
#         self.memoryLock.acquireRead()                  # read thread_safe
#         bestSensation = None
#         for association in sensation.getAssociations():
#             associatedSensation= association.getSensation()
#             if associatedSensation.getSensationType() == sensationType:
#                 if sensationType != Sensation.SensationType.Item or\
#                    associatedSensation.getName() == name:
#                     if bestSensation is None or\
#                        associatedSensation.getImportance() > bestSensation.getImportance():
#                         bestSensation = associatedSensation
#         self.memoryLock.releaseRead()                  # read thread_safe
#         return bestSensation

    '''
    save all LongTerm Memory sensation instances and data permanently
    so they can be loaded, when running app again
    '''  
    def saveLongTermMemory(self):
        # save sensations that are memorable to a file
        # there can be LOngTerm sensations in Sensation.sensationMemorys[Sensation.MemoryType.Sensory]
        # because it is allowed to change memoryType rtpe after sensation is created
        # save sensation instances
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)

        self.memoryLock.acquireRead()                  # read thread_safe
        i=0
        while i < len(self.sensationMemory):
            self.sensationMemory[i].attachedBy = []
            if self.sensationMemory[i].getMemoryType() == Sensation.MemoryType.LongTerm and\
               self.sensationMemory[i].getMemorability(allAssociations=True) >  Sensation.MIN_CACHE_MEMORABILITY:
#                 # remove connection to Robot
#                 # Robot is Thread and cannot be dumped
#                 self.sensationMemory[i].detachAll()
#                 self.sensationMemory[i].robot= None

                #self.sensationMemory[i].save()
                i=i+1
            else:
                # association to non saved Sensation will be removed
                self.sensationMemory[i].delete()
                del self.sensationMemory[i]
               
        # save sensation instances
        for sensation in self.sensationMemory:
            sensation.save()
#             
#             self.sensationMemory[i].attachedBy = []
#             if self.sensationMemory[i].getMemoryType() == Sensation.MemoryType.LongTerm and\
#                self.sensationMemory[i].getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY:
#                 # remove connection to Robot
#                 # Robot is Thread and cannot be dumped
#                 self.sensationMemory[i].detachAll()
#                 self.sensationMemory[i].robot= None
# 
#                 #self.sensationMemory[i].save()
#                 i=i+1
#  
#             
#         try:
#             with open(Sensation.PATH_TO_PICLE_FILE, "wb") as file:
#                 try:
#                     pickler = pickle.Pickler(file, -1)
#                     pickler.dump(Sensation.VERSION)
#                     pickler.dump(self.sensationMemory)
#                     #print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm])))
#                     self.log(logStr='saveLongTermMemory dumped {} sensations'.format(len(self.sensationMemory)), logLevel=Memory.MemoryLogLevel.Normal)
#                 except IOError as e:
#                     self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) IOError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
#                 except pickle.PickleError as e:
#                     self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PickleError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
#                 except pickle.PicklingError as e:
#                     self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PicklingError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
# 
#                 finally:
#                     file.close()
#         except Exception as e:
#                 self.log(logStr="saveLongTermMemory open(fileName, wb) as file error " + str(e), logLevel=Memory.MemoryLogLevel.Error)
        self.memoryLock.releaseRead()                  # read thread_safe

    '''
    load LongTerm MemoryType sensation instances
    '''  
#     def loadLongTermMemory(self):
#         # load sensation data from files
#         if os.path.exists(Sensation.DATADIR):
#             # find binary files
#             
#             
#             self.memoryLock.acquireWrite()                  # write thread_safe
#             try:
#                 with open(Sensation.PATH_TO_PICLE_FILE, "rb") as file:
#                     try:
#                         # TODO correct later
#                         # whole Memory
#                         #Sensation.sensationMemorys[Sensation.MemoryType.LongTerm] = \
#                         version = pickle.load(file)
#                         if version == Sensation.VERSION:
#                             self.sensationMemory = pickle.load(file)
#                             self.log(logStr='loaded {} sensations'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
#                             i=0
#                             while i < len(self.sensationMemory):
#                                 if  self.sensationMemory[i].getMemorability() <  Sensation.MIN_CACHE_MEMORABILITY:
#                                     self.log(logStr='delete sensation {} {} with too low memorability {}'.format(i, self.sensationMemory[i].toDebugStr(), self.sensationMemory[i].getMemorability()), logLevel=Memory.MemoryLogLevel.Normal)
#                                     self.sensationMemory[i].delete()
#                                     del self.sensationMemory[i]
#                                 else:
#                                     i=i+1
#                             self.log(logStr='after load and verification {}'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
#                             #print ('{} after load and verification {}'.format(Sensation.getMemoryTypeString(self.sensationMemory), len(self.sensationMemory)))
#                         else:
#                             self.log(logStr="Sensation could not be loaded. because Sensation cache version {} does not match current sensation version {}".format(version,Sensation.VERSION), logLevel=Memory.MemoryLogLevel.Normal)
# # OOPS Commented out, this is mesh
# #         # save sensation instances
# #         if not os.path.exists(Sensation.DATADIR):
# #             os.makedirs(Sensation.DATADIR)
# #             
# #         try:
# #             with open(Sensation.PATH_TO_PICLE_FILE, "wb") as file:
# #                 try:
# #                     pickler = pickle.Pickler(file, -1)
# #                     pickler.dump(Sensation.VERSION)
# #                     pickler.dump(self.sensationMemory)
# #                     #print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm])))
# #                     self.log(logStr='saveLongTermMemory dumped {} sensations'.format(len(self.sensationMemory)), logLevel=Memory.MemoryLogLevel.Normal)
# # tionMemory[i].getMemorability() <  Sensation.MIN_CACHE_MEMORABILITY:
# #                                     self.log(logStr='delete sensation {} {} with too low memorability {}'.format(i, self.sensationMemory[i].toDebugStr(), self.sensationMemory[i].getMemorability()), logLevel=Memory.MemoryLogLevel.Normal)
# #                                     self.sensationMemory[i].delete()
# #                                     del self.sensationMemory[i]
# #                                 else:
# #                                     i=i+1
# #                             self.log(logStr='after load and verification {}'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
# #                             #print ('{} after load and verification {}'.format(Sensation.getMemoryTypeString(self.sensationMemory), len(self.sensationMemory)))
# #                         else:
# #                             self.log(logStr="Sensation could not be loaded. because Sensation cache version {} does not match current sensation version {}".format(version,Sensation.VERSION), logLevel=Memory.MemoryLogLevel.Normal)
# #                     except IOError as e:
# #                         self.log(logStr="pickle.load(file) error " + str(e), logLevel=Memory.MemoryLogLevel.Error)
# #                     except pickle.PickleError as e:
# #                         self.log(logStr='pickle.load(file) PickleError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
# #                     except pickle.PicklingError as e:
# #                         self.log(logStr='pickle.load(file) PicklingError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
# #                     except Exception as e:
# #                         self.log(logStr='pickle.load(file) Exception ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
#                     finally:
#                         file.close()
# 
#                     except Exception as e:
#                         self.log(logStr='with open(' + Sensation.PATH_TO_PICLE_FILE + ',"rb") as file error ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
#                         self.memoryLock.releaseWrite()                  # write thread_safe

    '''  
    save all LongTerm Memory sensation instances and data permanently
    so they can be loaded, when running app again
    '''  
    def saveLongTermMemoryToBinaryFiles(self):
        # save sensations that are memorable to a file
        # there can be LOngTerm sensations in Sensation.sensationMemorys[Sensation.MemoryType.Sensory]
        # because it is allowed to change memoryType rtpe after sensation is created
        self.memoryLock.acquireRead()                  # read thread_safe
        i=0
        savedSensation = 0
        deletedSensations = 0
        while i < len(self.sensationMemory):
            self.sensationMemory[i].attachedBy = []
            if self.sensationMemory[i].getMemoryType() == Sensation.MemoryType.LongTerm and\
               self.sensationMemory[i].getSensationType() != Sensation.SensationType.Unknown and\
               self.sensationMemory[i].getMemorability(allAssociations=True) >  Sensation.MIN_CACHE_MEMORABILITY:
                # remove connection to Robot
                # Robot is Thread and cannoc be dumped
                self.sensationMemory[i].detachAll()
                self.sensationMemory[i].robot= None

                self.sensationMemory[i].save()
                savedSensation = savedSensation+1
                i=i+1
            else:
                self.sensationMemory[i].delete()
                del self.sensationMemory[i]
                deletedSensations = deletedSensations+1
        self.log(logStr="saveLongTermMemoryToBinaryFiles saved {}, deleted {} sensation".format(savedSensation,  deletedSensations))
               
#         # save sensation instances
#         if not os.path.exists(Sensation.DATADIR):
#             os.makedirs(Sensation.DATADIR)
#             
#         try:
#             with open(Sensation.PATH_TO_PICLE_FILE, "wb") as file:
#                 try:
#                     pickler = pickle.Pickler(file, -1)
#                     pickler.dump(Sensation.VERSION)
#                     pickler.dump(self.sensationMemory)
#                     #print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm])))
#                     self.log(logStr='saveLongTermMemory dumped {} sensations'.format(len(self.sensationMemory)), logLevel=Memory.MemoryLogLevel.Normal)
#                 except IOError as e:
#                     self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) IOError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
#                 except pickle.PickleError as e:
#                     self.log(logStr='pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PickleError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
#                 except pickle.PicklingError as e:
#                     self.log(logStr='pickler.dump(Sensat        savedSensation = 0
#ion.sensationMemorys[MemoryType.LongTerm]) PicklingError ' + str(e), logLevel=Memory.MemoryLogLevel.Error)
# 
#                 finally:
#                     file.close()
#         except Exception as e:
#                 self.log(logStr="saveLongTermMemory open(fileName, wb) as file error " + str(e), logLevel=Memory.MemoryLogLevel.Error)
        self.memoryLock.releaseRead()                  # read thread_safe

    '''
    load LongTerm MemoryType sensation instances
    '''  
    def loadLongTermMemoryFromBinaryFiles(self):
        # load sensation data from files
        if os.path.exists(Sensation.DATADIR):
            #self.memoryLock.acquireWrite()                  # write thread_safe
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    # There can be image or voice files not any more needed
                    if filename.endswith('.'+Sensation.BINARY_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        # create Sensation
                        sensation= self.create(robot=self.getRobot(), binaryFilePath=filepath)
                        # make forgettable
                        sensation.detach(robot=self.getRobot())
            except Exception as e:
                    self.log(logStr='os.listdir error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
                
            self.log(logStr='loadLongTermMemoryFromBinaryFiles loaded {} sensations'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
            i=0
            while i < len(self.sensationMemory):
                if self.sensationMemory[i].getMemorability(allAssociations=True) <  Sensation.MIN_CACHE_MEMORABILITY or\
                   self.sensationMemory[i].getSensationType() == Sensation.SensationType.Unknown:
                    self.log(logStr='loadLongTermMemoryFromBinaryFiles delete sensation {} {} with too low memorability {}'.format(i, self.sensationMemory[i].toDebugStr(), self.sensationMemory[i].getMemorability(allAssociations=True)), logLevel=Memory.MemoryLogLevel.Normal)
                    self.sensationMemory[i].delete()
                    del self.sensationMemory[i]
                else:
                    i=i+1
            self.log(logStr='loadLongTermMemoryFromBinaryFiles after load and verification {}'.format(str(len(self.sensationMemory))), logLevel=Memory.MemoryLogLevel.Normal)
             #print ('{} after load and verification {}'.format(Sensation.getMemoryTypeString(self.sensationMemory), len(self.sensationMemory)))
            #self.memoryLock.releaseWrite()                  # write thread_safe
 
    '''
    Clean data directory from data files, that are not connected to any sensation.
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
                       filename.endswith('.'+Sensation.VOICE_FORMAT) or\
                       filename.endswith('.'+Sensation.BINARY_FORMAT):
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
            if sensation.getFilePath(sensationType=ensation.SensationType.All) == filepath:
                return True
        return False

#     '''
#     Presence
#     '''
#     def tracePresents(self, sensation):
#         # present means pure Present, all other if handled not present
#         # if present sensations must come in order
#         if sensation.getName() in self.presentItemSensations and\
#            sensation.getTime() > self.presentItemSensations[sensation.getName()].getTime(): 
# 
#             if sensation.getPresence() == Sensation.Presence.Entering or\
#                sensation.getPresence() == Sensation.Presence.Present or\
#                sensation.getPresence() == Sensation.Presence.Exiting:
#                 self.presentItemSensations[sensation.getName()] = sensation
#                 self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())
#             else:
#                 del self.presentItemSensations[sensation.getName()]
#                 self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Absent " + sensation.getName())
#         # accept only sensation items that are not present, but not not in order ones
#         # absent sensations don't have any mean at this case
#         elif (sensation.getName() not in self.presentItemSensations) and\
#              (sensation.getPresence() == Sensation.Presence.Entering or\
#                sensation.getPresence() == Sensation.Presence.Present or\
#                sensation.getPresence() == Sensation.Presence.Exiting):
#                 self.presentItemSensations[sensation.getName()] = sensation
#                 self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Entering, Present or Exiting " + sensation.getName())
    '''
    Presence
    '''
    def tracePresentItems(self, 
                          sensation,
                          presentDict,
                          name = None,
                          names = None):
        # present means pure Present, all other if handled not present
        # if present sensations must come in order
        locations = sensation.getLocations()
        if locations == None or len(locations) == 0:
            locations = [''] 
        for location in locations:
            if name != None:
                self.tracePresentsByLocation(sensation,
                                             location = location,
                                             presentDict = presentDict,
                                             name = name)
            if names != None:
                for n in names:
                    self.tracePresentsByLocation(sensation,
                                                 location = location,
                                                 presentDict = presentDict,
                                                 name = n)

    '''
    Presence by location
    '''
    def tracePresentsByLocation(self,
                                sensation,
                                location,
                                presentDict,
                                name):
        # present means pure Present, all other if handled not present
        # if present sensations must come in order
        if not location in presentDict:
            presentDict[location] = {}
        if name in presentDict[location] and\
           sensation.getTime() > presentDict[location][name].getTime(): 

            if sensation.getPresence() in [ Sensation.Presence.Entering,\
                                            Sensation.Presence.Present,\
                                            Sensation.Presence.Exiting]:
                presentDict[location][name] = sensation
                self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="update Entering, Present or Exiting " + name)
            else:
                del presentDict[location][name]
                self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="Absent " + name)
        # accept only sensation items that are not present, but not not in order ones
        # absent sensations don't have any mean at this case
        elif (name not in presentDict[location]) and\
             (sensation.getPresence() in [ Sensation.Presence.Entering,\
                                           Sensation.Presence.Present,\
                                           Sensation.Presence.Exiting]):
                presentDict[location][name] = sensation
                self.log(logLevel=Memory.MemoryLogLevel.Normal, logStr="new Entering, Present or Exiting " + name)
                
    '''
    have we Item presence in some location or locations.
    '''

    def hasItemsPresence(self, location=None, locations=None):
        return self.hasPresence(presentDict=self._presentItemSensations, location=location, locations=locations)

    '''
    have we Robot presence in some location
    '''

    def hasRobotsPresence(self, location=None, locations=None):
        return self.hasPresence(presentDict=self._presentRobotSensations, location=location, locations=locations)

    '''
    have we presence in some location
    global location is ignored
    '''

    def hasPresence(self, presentDict, location=None, locations=None):
        if location is None and locations is None:
            locations = presentDict.keys()
        elif location and locations is None:
            locations = [location]
        for location in locations:
            if location and location in presentDict:
                if (location != Memory.GLOBAL_LOCATION) and (len(presentDict[location].items()) > 0):
                    return True
        return False

    '''
    Do we have Item presence changes, that are pending,
    meaning that they are in Entering or Exiting
    in some locations
    '''
    def hasPendingPresentItemChanges(self, location=None):
        if location is None:
            locations = self._presentItemSensations.keys()
        else:
            locations = [location]
            
        for location in locations:
            if location != Memory.GLOBAL_LOCATION:
                for _, itemSensation in self._presentItemSensations[location].items():
                    if itemSensation.getPresence() in [ Sensation.Presence.Entering,\
                                                        Sensation.Presence.Exiting]:
                        return True
        return False
   
    '''
    return human readable string of presence items in all locations
    '''
    def itemsPresenceToStr(self, location=None):
        return self.presenceToStr(presentDict=self._presentItemSensations, location=location)
    
    '''
    return human readable string of presence Robots in all locations
    '''
    def robotsPresenceToStr(self, location=None):
        return self.presenceToStr(presentDict=self._presentRobotSensations, location=location)
    

    '''
    return human readable string of presence items in all locations
    '''
    def presenceToStr(self, presentDict, location=None):
        if location and location in presentDict:
            namesStr='['+location + ':'
            for name, sensation in presentDict[location].items():
                namesStr = namesStr + ' ' + name
            return namesStr

        allLocationnamesStr=''
        isFirst=True
        for location in presentDict.keys():
            namesStr='['+location + ':'
            for name, sensation in presentDict[location].items():
                if isFirst:
                    namesStr = namesStr + name
                    isFirst=False
                else:
                    namesStr = namesStr + '|' + name
            allLocationnamesStr += namesStr + ']'
        return allLocationnamesStr
    
    '''
    get Item presence sensations in a location
    '''
    def getPresentItemSensations(self, location):
        return self.getPresentSensations(presentDict=self._presentItemSensations, location=location)

    '''
    get Robot presence sensations in a location
    '''
    def getPresentRobotSensations(self, location):
        return self.getPresentSensations(presentDict=self._presentRobotSensations, location=location)

    '''
    get presence sensations in a location
    '''
    def getPresentSensations(self, presentDict, location):
        if location == None :
            location = ''
        if not location in presentDict:
            presentDict[location] = {}
            return []
        return presentDict[location].items()

    '''
    get Item presence sensations in a location
    '''
#     def getPresentSensations(self, location):
#         if location == None :
#             location = ''
#         if not location in self._presentItemSensations:
#             self._presentItemSensations[location] = {}
#             return []
#         return self._presentItemSensations[location].items()

    '''
    get Item presence sensations in all location,
    but only one sensation per Item.name
    This is helper function to ne compatible with old implementation when we don't care about locations.
    This method can be removed
    '''
    def getAllPresentItemSensations(self):
        itemSensations = []
        names=[]
        for location in self._presentItemSensations.keys():
            if location != Memory.GLOBAL_LOCATION:
                for name, itemSensation in self._presentItemSensations[location].items():
                    if name not in names:
                        names.append(name)
                        itemSensations.append(itemSensation)
        return itemSensations
 
    '''
    get Robot presence sensations in a location
    '''
    def getPresentRobotSensations(self, location):
        if location == None :
            location = ''
        if not location in self._presentRobotSensations:
            self._presentRobotSensations[location] = {}
            return []
        return self._presentRobotSensations[location].items()

    '''
    get Robot presence sensations in all location,
    but only one sensation per Robot.name
    This is helper function to ne compatible with old implementation when we don't care about locations.
    This method can be removed
    '''
    def getAllPresentRobotSensations(self):
        robotSensations = []
        names=[]
        for location in self._presentRobotSensations.keys():
            for name, robotSensation in self._presentRobotSensations[location].items():
                if name not in names:
                    names.append(name)
                    robotSensations.append(robotSensation)
        return robotSensations

    '''
    log
    '''
    
    def log(self, logStr, logLevel=MemoryLogLevel.Normal):
        # should test, if we have initiated Robot enough
        if hasattr(self.getRobot(), 'selfSensation') and\
           self.getRobot().logLevel != Memory.MemoryLogLevel.No:
            self.getRobot().log(logStr=logStr, logLevel=logLevel)
            
    def getLogLevel(self):
        # should test, if we have initiated Robot enough
        if hasattr(self.getRobot(), 'selfSensation'):
            return self.getRobot().getLogLevel()
        return Memory.MemoryLogLevel.No
    
