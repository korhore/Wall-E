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
        self.sensationMemorys[sensation.getMemoryType()].append(sensation)        
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
        memoryType = self.sensationMemorys[sensation.getMemoryType()]

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
              format(Sensation.getMemoryTypeString(Sensation.MemoryType.Sensory), len(self.sensationMemorys[Sensation.MemoryType.Sensory]),\
                     Sensation.getMemoryTypeString(Sensation.MemoryType.Working), len(self.sensationMemorys[Sensation.MemoryType.Working]),\
                     Sensation.getMemoryTypeString(Sensation.MemoryType.LongTerm), len(self.sensationMemorys[Sensation.MemoryType.LongTerm]),\
                     Memory.getMemoryUsage(), Memory.getAvailableMemory(), self.min_cache_memorability))
        if numNotForgettables > 0:
            print('Sensations cache deletion skipped {} Not Forgottable Sensation'.format(numNotForgettables))
            for robotName, notForgottableNumber in notForgettables.items():
                print ('Sensations cache Not Forgottable robot {} number {}'.format(robotName, notForgottableNumber))
        #print('Memory usage for {} Sensations {} after {} MB'.format(len(memoryType), Sensation.getMemoryTypeString(sensation.getMemoryType()), Sensation.getMemoryUsage()-Sensation.startSensationMemoryUsageLevel))

    '''
    sensation getters
    '''
    def getSensationFromSensationMemory(self, id):
        self.memoryLock.acquireRead()                  # read thread_safe
 
        for key, sensationMemory in self.sensationMemorys.items():
            if len(self.sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getId() == id:
                        self.memoryLock.releaseRead()  # read thread_safe
                        return sensation
        self.memoryLock.releaseRead()                  # read thread_safe
        return None

    def getSensationsFromSensationMemory(self, associationId):
        self.memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        for key, sensationMemory in self.sensationMemorys.items():
            if len(sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getId() == associationId or \
                       associationId in sensation.getAssociationIds():
                        if not sensation in sensations:
                            sensations.append(sensation)
        memoryLock.releaseRead()                  # read thread_safe
        return sensations
                     
    '''
    Get sensations from sensation memory that are set in capabilities
    
    Time window can be set seperatly min, max or both,
    from time min to time max, to get sensations that are happened at same moment.   
    '''  
    def getSensations(self, capabilities, timemin=None, timemax=None):
        self.memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        for key, sensationMemory in self.sensationMemorys.items():
            for sensation in sensationMemory:
                if capabilities.hasCapability(direction=sensation.getDirection(),
                                              memoryType=sensation.getMemoryType(),
                                              sensationType=sensation.getSensationType()) and\
                   (timemin is None or sensation.getTime() > timemin) and\
                   (timemax is None or sensation.getTime() < timemax):
                    sensations.append(sensation)
        self.memoryLock.releaseRead()                  # read thread_safe
        return sensations
    
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
                          direction = Sensation.Direction.Out,
                          name = None,
                          notName = None,
                          associationSensationType = None,
                          associationDirection = Sensation.Direction.Out,
                          ignoredVoiceLens=[]):
        self.memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        for key, sensationMemory in self.sensationMemorys.items():
            for sensation in sensationMemory:
                if sensation.getSensationType() == sensationType and\
                   sensation.getDirection() == direction and\
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
                            print("getBestSensation " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getScore()))
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
                                   direction = Sensation.Direction.Out,
                                   name = None,
                                   notName = None,
                                   associationSensationType = None,
                                   associationDirection = Sensation.Direction.Out,
                                   ignoredSensations = [],
                                   ignoredVoiceLens = [],
                                   searchLength = 10):
#                                   searchLength = Sensation.SEARCH_LENGTH):
        self.memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        bestAssociation = None
        bestAssociationSensation = None
        # TODO starting with best score is not a good idea
        # if best scored item.name has only bad voices, we newer can get
        # good voices
        found_candidates=0
        for key, sensationMemory in self.sensationMemorys.items():
            if found_candidates >= searchLength:
                break
            for sensation in sensationMemory:
                if sensation not in ignoredSensations and\
                   sensation.getSensationType() == sensationType and\
                   sensation.getDirection() == direction and\
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
                            if bestAssociationSensationImportance is None or\
                                bestAssociationSensationImportance < association.getSensation().getImportance():
                                bestAssociationSensationImportance = association.getSensation().getImportance()
                                bestSensation = sensation
                                bestAssociation = association
                                bestAssociationSensation = association.getSensation()
                                #print("getMostImportantSensation found " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()))
                                #print("getMostImportantSensation found bestAssociationSensation candidate " + bestAssociationSensation.toDebugStr() + ' ' + str(bestAssociationSensationImportance))
                                found_candidates +=1
                                if found_candidates >= searchLength:
                                    break
                    if found_candidates >= searchLength:
                        break
        if bestSensation == None:
            print("getMostImportantSensation did not find any")
        else:
            print("getMostImportantSensation bestSensation {} {}".format(bestSensation.toDebugStr(),str(bestSensation.getImportance())))
            print("getMostImportantSensation found bestAssociationSensation {} {}".format(bestAssociationSensation.toDebugStr(),str(bestAssociationSensationImportance)))            
                        
                        
                        
# old logic
#                         if bestSensation is None or\
#                            sensation.getImportance() > bestSensation.getImportance():
#                             bestSensation = sensation
#                             print("getMostImportantSensation found candidate " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()))
#         if bestSensation is not None:
#             print("getMostImportantSensation found " + bestSensation.toDebugStr() + ' ' + str(bestSensation.getImportance()))
#             bestAssociationSensationImportance = None 
#             for association in bestSensation.getAssociationsbBySensationType(associationSensationType=associationSensationType, ignoredSensations=ignoredSensations, ignoredVoiceLens=ignoredVoiceLens):
#                 if bestAssociationSensationImportance is None or\
#                     bestAssociationSensationImportance < association.getSensation().getImportance():
#                     bestAssociationSensationImportance = association.getSensation().getImportance()
#                     bestAssociation = association
#                     bestAssociationSensation = association.getSensation()
#                     print("getMostImportantSensation found bestAssociationSensation candidate " + bestAssociationSensation.toDebugStr() + ' ' + str(bestAssociationSensationImportance))
#         else:
#             print("getMostImportantSensation did not find any")
            
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
        for sensation in self.sensationMemorys[Sensation.MemoryType.LongTerm]:
            sensation.attachedBy = []
            if sensation.getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY and\
                sensation.getMemoryType() == Sensation.MemoryType.LongTerm:
                sensation.attachedBy = [] # clear references to Robots
                                          # they are not valid wlen loaded and they cannoc be dumped
                sensation.save()
            else:
                sensation.delete()
               
        # save sensation instances
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)
            
        try:
            with open(Sensation.PATH_TO_PICLE_FILE, "wb") as f:
                try:
                    pickler = pickle.Pickler(f, -1)
                    pickler.dump(Sensation.VERSION)
                    pickler.dump(self.sensationMemorys[Sensation.MemoryType.LongTerm])
                    #print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm])))
                    print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.MemoryType.Sensory])))
                except IOError as e:
                    print('pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) IOError ' + str(e))
                except pickle.PickleError as e:
                    print('pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PickleError ' + str(e))
                except pickle.PicklingError as e:
                    print('pickler.dump(Sensation.sensationMemorys[MemoryType.LongTerm]) PicklingError ' + str(e))

                finally:
                    f.close()
        except Exception as e:
                print("open(fileName, wb) as f error " + str(e))
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
                            self.sensationMemorys[Sensation.MemoryType.LongTerm] = pickle.load(f)
                            for key, sensationMemory in self.sensationMemorys.items():
                                print ('{} loaded {}'.format(Sensation.getMemoryTypeString(key), str(len(sensationMemory))))
                                i=0
                                while i < len(sensationMemory):
                                    if  sensationMemory[i].getMemorability() <  Sensation.MIN_CACHE_MEMORABILITY:
                                        print('delete sensationMemory[{}] with too low memorability {}'.format(i,sensationMemory[i].getMemorability()))
                                        sensationMemory[i].delete()
                                        # TODO we should delete this also from but how?
                                        del sensationMemory[i]
                                    else:
                                        i=i+1
                                print ('{} after load and verification {}'.format(Sensation.getMemoryTypeString(key), str(len(sensationMemory))))
                                #print ('{} after load and verification {}'.format(Sensation.getMemoryTypeString(sensationMemory), len(sensationMemory)))
                        else:
                            print("Sensation could not be loaded. because Sensation cache version {} does not mach current sensation version {}".format(version,Sensation.VERSION))
                    except IOError as e:
                        print("pickle.load(f) error " + str(e))
                    except pickle.PickleError as e:
                        print('pickle.load(f) PickleError ' + str(e))
                    except pickle.PicklingError as e:
                        print('pickle.load(f) PicklingError ' + str(e))
                    except Exception as e:
                        print('pickle.load(f) Exception ' + str(e))
                    finally:
                        f.close()
            except Exception as e:
                    print('with open(' + Sensation.PATH_TO_PICLE_FILE + ',"rb") as f error ' + str(e))
            self.memoryLock.releaseWrite()                  # write thread_safe
 
    '''
    Clean data directory fron data files, that are not connected to any sensation.
    '''  
    def CleanDataDirectory(self):
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
            self.memoryLock.acquireRead()                  # read thread_safe
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    # There can be image or voice files not any more needed
                    if filename.endswith('.'+Sensation.IMAGE_FORMAT) or\
                       filename.endswith('.'+Sensation.VOICE_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        if not self.hasOwner(filepath):
                            print('os.remove(' + filepath + ')')
                            try:
                                os.remove(filepath)
                            except Exception as e:
                                print('os.remove(' + filepath + ') error ' + str(e))
            except Exception as e:
                    print('os.listdir error ' + str(e))
            self.memoryLock.releaseRead()                  # read thread_safe
            
    '''
    hasOwner is called from methos protected by semaphore
    so we should not protect this method
    '''        
                    
    def hasOwner(self, filepath):
        for key, sensationMemory in self.sensationMemorys.items():
            if len(sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getSensationType() == Sensation.SensationType.Image or\
                       sensation.getSensationType() == Sensation.SensationType.Voice:
                        if sensation.getFilePath() == filepath:
                            return True
        return False
   