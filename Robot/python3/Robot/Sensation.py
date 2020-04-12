'''
Created on Feb 25, 2013
Edited on 12.04.2020

@author: Reijo Korhonen, reijo.korhonen@gmail.com
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

#def enum(**enums):
#    return type('Enum', (), enums)
LIST_SEPARATOR=':'

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# try unicode-escape instead of utf8 toavoid error with non ascii characters bytes
def StrToBytes(e):
    return e.encode('unicode-escape')

def bytesToStr(b):
    try:
        return b.decode('unicode-escape')
    except UnicodeDecodeError as e:
        print ('UnicodeDecodeError ' + str(e))
        return ''
    
def listToBytes(l):
    ret_s = ''
    if l is not None:
        i=0
        for s in l:
            if i == 0:
                ret_s = s
            else:
                ret_s += LIST_SEPARATOR + s
            i = i+1
    return StrToBytes(ret_s)
    
def bytesToList(b):
    #print('bytesToList b ' +str(b))

    ret_s = bytesToStr(b)
    #print('bytesToList ret_s ' +str(ret_s))
    return ret_s.split(LIST_SEPARATOR)

def strListToFloatList(l):
    ret_s = []
    if l is not None:
        for s in l:
            ret_s.append(float(s))
    return ret_s


def floatToBytes(f):
    return bytearray(struct.pack(Sensation.FLOAT_PACK_TYPE, f)) 

def bytesToFloat(b):
    return struct.unpack(Sensation.FLOAT_PACK_TYPE, b)[0]

'''
Sensation is something Robot senses
'''

class Sensation(object):
    VERSION=15          # version number to check, if we picle same version
                        # instances. Otherwise we get odd errors, with old
                        # version code instances

    SEARCH_LENGTH=10    # How many response voices we check
    # Association logging max-values                      
    ASSOCIATIONS_LOG_MAX_LEVEL =   10
    ASSOCIATIONS_LOG_MAX_PARENTS = 10           
    ASSOCIATIONS_MAX_ASSOCIATIONS = 50           

    IMAGE_FORMAT =      'jpeg'
    MODE =              'RGB'       # PIL_IMAGE mode, not used now, but this it is
    DATADIR =           'data'
    VOICE_FORMAT =      'wav'
    PICLE_FILENAME =    'Sensation.pkl'
    PATH_TO_PICLE_FILE = os.path.join(DATADIR, PICLE_FILENAME)
    LOWPOINT_NUMBERVARIANCE=-100.0
    HIGHPOINT_NUMBERVARIANCE=100.0
    
    SENSORY_LIVE_TIME =     120.0;       # sensory sensation lives 120 seconds = 2 mins (may be changed)
    WORKING_LIVE_TIME =     1200.0;       # cache sensation 600 seconds = 20 mins (may be changed)
    #LONG_TERM_LIVE_TIME =   3000.0;       # cache sensation 3000 seconds = 50 mins (may be changed)
    LONG_TERM_LIVE_TIME =   24.0*3600.0;  # cache sensation 24h (may be changed)
    ### Cleanup
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
    ### Cleanup
    #
    
    LENGTH_SIZE =       2   # Sensation as string can only be 99 character long
    LENGTH_FORMAT =     "{0:2d}"
    SEPARATOR =         '|'  # Separator between messages
    SEPARATOR_SIZE =    1  # Separator length
    
    ENUM_SIZE =         1
    ID_SIZE =           4
    BYTEORDER =         "little"
    FLOAT_PACK_TYPE =   "d"
    FLOAT_PACK_SIZE =   8
     
    # so many sensationtypes, that first letter is not good idea any more  
    SensationType = enum(Drive='a', Stop='b', Who='c', Azimuth='d', Acceleration='e', Observation='f', HearDirection='g', Voice='h', Image='i',  Calibrate='j', Capability='k', Item='l', Unknown='m')
    # Direction of a sensation. Example in Voice: In: Speaking,  Out: Hearing
    Direction = enum(In='I', Out='O')
    # Direction of a sensation transferring, used with Axon. Up: going up like fron AlsaMicroPhone to MainRobot, Down: going down from MainRobot to leaf Robots like AlsaPlayback
    TransferDirection = enum(Up='U', Down='D')
    # Presence of Item  
    Presence = enum(Entering='a', Present='b', Exiting='c', Absent='d', Unknown='e')

    MemoryType = enum(Sensory='S', Working='W', LongTerm='L' )
    #MemoryType = enum(Sensory='S', LongTerm='L' )
    Kind = enum(WallE='w', Eva='e', Normal='n')
    InstanceType = enum(Real='r', SubInstance='s', Virtual='v', Remote='e')
    Mode = enum(Normal='n', StudyOwnIdentity='t',Sleeping='l',Starting='s', Stopping='p', Interrupted='i')
# enum items as strings    
    IN="In"
    OUT="Out"
    SENSORY="Sensory"
    WORKING="Working"
    LONG_TERM="LongTerm"
    DRIVE="Drive"
    STOP="Stop"
    WHO="Who"
    AZIMUTH="Azimuth"
    ACCELERATION="Acceleration"
    OBSERVATION="Observation"
    HEARDIRECTION="HearDirection"
    VOICE="Voice"
    IMAGE="Image"
    CALIBRATE="Calibrate"
    CAPABILITY="Capability"
    ITEM="Item"
    UNKNOWN="Unknown"
    KIND="Kind"
    WALLE="Wall-E"
    EVA="Eva"
    NORMAL="Normal"
    REAL="Real"
    SUBINSTANCE="SubInstance"
    VIRTUAL="Virtual"
    REMOTE="Remote"
    NORMAL="Normal"
    STUDYOWNIDENTITY="StudyOwnIdentity"
    SLEEPING="Sleeping"
    STARTING="Starting"
    STOPPING="Stopping"
    INTERRUPTED="Interrupted"
    ENTERING="Entering"
    PRESENT="Present"
    EXITING="Exiting"
    ABSENT="Absent"

      
    Directions={Direction.In: IN,
                Direction.Out: OUT}
    DirectionsOrdered=(
                Direction.In,
                Direction.Out)
    
    MemoryTypes = {
               MemoryType.Sensory: SENSORY,
               MemoryType.Working: WORKING,
               MemoryType.LongTerm: LONG_TERM}
    MemoryTypesOrdered = (
               MemoryType.Sensory,
               MemoryType.Working,
               MemoryType.LongTerm)
    
    SensationTypes={
               SensationType.Drive: DRIVE,
               SensationType.Stop: STOP,
               SensationType.Who: WHO,
               SensationType.Azimuth: AZIMUTH,
               SensationType.Acceleration: ACCELERATION,
               SensationType.Observation: OBSERVATION,
               SensationType.HearDirection: HEARDIRECTION,
               SensationType.Voice: VOICE,
               SensationType.Image: IMAGE,
               SensationType.Calibrate: CALIBRATE,
               SensationType.Capability: CAPABILITY,
               SensationType.Item: ITEM,
               SensationType.Unknown: UNKNOWN}
    SensationTypesOrdered=(
               SensationType.Drive,
               SensationType.Stop,
               SensationType.Who,
               SensationType.Azimuth,
               SensationType.Acceleration,
               SensationType.Observation,
               SensationType.HearDirection,
               SensationType.Voice,
               SensationType.Image,
               SensationType.Calibrate,
               SensationType.Capability,
               SensationType.Item,
               SensationType.Unknown)
    
    Kinds={Kind.WallE: WALLE,
           Kind.Eva: EVA,
           Kind.Normal: NORMAL}
    InstanceTypes={InstanceType.Real: REAL,
                   InstanceType.SubInstance: SUBINSTANCE,
                   InstanceType.Virtual: VIRTUAL,
                   InstanceType.Remote: REMOTE}

    Modes={Mode.Normal: NORMAL,
           Mode.StudyOwnIdentity: STUDYOWNIDENTITY,
           Mode.Sleeping: SLEEPING,
           Mode.Starting: STARTING,
           Mode.Stopping: STOPPING,
           Mode.Interrupted: INTERRUPTED}
    
    Presences = {
           Presence.Entering: ENTERING,
           Presence.Present:  PRESENT,
           Presence.Exiting:  EXITING,
           Presence.Absent:   ABSENT,
           Presence.Unknown:  UNKNOWN}

    
    sensationMemorys={                      # Sensation caches
        MemoryType.Sensory:  [],                # short time Sensation cache
        MemoryType.Working:  [],                # middle time Sensation cache
        MemoryType.LongTerm: [] }               # long time Sensation cache

    sensationMemoryLiveTimes={             # Sensation cache times
        MemoryType.Sensory:  SENSORY_LIVE_TIME,
        MemoryType.Working:  WORKING_LIVE_TIME,
        MemoryType.LongTerm: LONG_TERM_LIVE_TIME }


                            # The idea is keep Sensation in runtime memory if
                            # there is a association for them for instance 10 mins
                            #
                            # After that we can produce higher level Sensations
                            # with memory attribute in higher level,
                            # Working or Memory, that association to basic
                            # memory level, that is Sensory level.
                            # That way we can produce meanings is higher level
                            # of low level sensations. For instance we can get
                            # a image (Sensory) and process it with tnsorFlow
                            # which classifies it as get words and get
                            # Working or Memory level Sensations that refers
                            # to the original hearing, a Image, meaning
                            # that robot has seen it at certain time.
                            # THigher level Sensation can be processed also and
                            # we can save original image in a file with
                            # its classified names. After that our robot
                            # knows how those classifies names look like,
                            # what is has seen. 
# 
#     '''
#     Lock class to protect all methods handling Sensation cache.
#     This from O'Reilly. We need read and write lock solution and this is it.
#     '''
#     
#     class ReadWriteLock:
#         """ A lock object that allows many simultaneous "read locks", but
#         only one "write lock." """
#     
#         def __init__(self):
#             self._read_ready = threading.Condition(threading.Lock(  ))
#             self._readers = 0
#     
#         def acquireRead(self):
#             """ Acquire a read lock. Blocks only if a thread has
#             acquired the write lock. """
#             self._read_ready.acquire(  )
#             try:
#                 self._readers += 1
#             finally:
#                 self._read_ready.release(  )
#     
#         def releaseRead(self):
#             """ Release a read lock. """
#             self._read_ready.acquire(  )
#             try:
#                 self._readers -= 1
#                 if not self._readers:
#                     self._read_ready.notifyAll(  )
#             finally:
#                 self._read_ready.release(  )
#     
#         def acquireWrite(self):
#             """ Acquire a write lock. Blocks until there are no
#             acquired read or write locks. """
#             self._read_ready.acquire(  )
#             while self._readers > 0:
#                 self._read_ready.wait(  )
#     
#         def releaseWrite(self):
#             """ Release a write lock. """
#             self._read_ready.release(  )    
    
    #memoryLock = threading.Lock() # for thread_dafe Sensation cache
    global memoryLock           # outside Sensation
    memoryLock = ReadWriteLock() # for thread_dafe Sensation cache
    
    def getDirectionString(direction):
        ret = Sensation.Directions.get(direction)
        return ret
    def getDirectionStrings():
        ret=[]
        for direction in Sensation.DirectionsOrdered:
            ret.append(Sensation.Directions[direction])
        return ret
        #return Sensation.Directions.values()
    
    def getMemoryTypeString(memoryType):
        ret = Sensation.MemoryTypes.get(memoryType)
        return ret
    def getMemoryTypeStrings():
        return Sensation.MemoryTypes.values()
    
    def getSensationTypeString(sensationType):
        return Sensation.SensationTypes.get(sensationType)
    def getSensationTypeStrings():
        return Sensation.SensationTypes.values()
    
    def getPresenceString(presence):
        return Sensation.Presences.get(presence)
    def getPresenceStrings():
        return Sensation.Presences.values()

    def getKindString(kind):
        return Sensation.Kinds.get(kind)
    def getKindStrings():
        return Sensation.Kinds.values()
    


    '''
    Add new Sensation to Sensation cache
    use memory management to avoid too much memoryType using
    '''
    
    def addToSensationMemory(sensation):
        memoryLock.acquireWrite()  # thread_safe                                     
        Sensation.forgetLessImportantSensations(sensation)        
        Sensation.sensationMemorys[sensation.getMemoryType()].append(sensation)        
        memoryLock.releaseWrite()  # thread_safe   
        
    '''
    get memoryType usage
    '''
    def getMemoryUsage():     
         #memUsage= resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0            
        return Sensation.process.memory_info().rss/(1024*1024)              # hope this works better
    
    '''
    get available memoryType
    '''
    def getAvailableMemory():
        return psutil.virtual_memory().available/(1024*1024)
        
    '''
    Forget sensations that are not important
    Other way we run out of memoryType very soon.
    
    This method is called from semaphore protected method, so we
    should not protect this
    '''

    def forgetLessImportantSensations(sensation):
        numNotForgettables=0
        memory = Sensation.sensationMemorys[sensation.getMemoryType()]

        # calibrate memorability        
        if (Sensation.getMemoryUsage() > Sensation.maxRss or\
            Sensation.getAvailableMemory() < Sensation.minAvailMem) and\
            Sensation.min_cache_memorability < Sensation.MAX_MIN_CACHE_MEMORABILITY:
            if Sensation.min_cache_memorability >= Sensation.NEAR_MAX_MIN_CACHE_MEMORABILITY:
                Sensation.min_cache_memorability = Sensation.min_cache_memorability + 0.01
            else:
                Sensation.min_cache_memorability = Sensation.min_cache_memorability + 0.1
        elif (Sensation.getMemoryUsage() < Sensation.maxRss or\
              Sensation.getAvailableMemory() > Sensation.minAvailMem )and\
            Sensation.min_cache_memorability > Sensation.MIN_MIN_CACHE_MEMORABILITY:
            if Sensation.min_cache_memorability <= Sensation.NEAR_MIN_MIN_CACHE_MEMORABILITY:
                Sensation.min_cache_memorability = Sensation.min_cache_memorability - 0.01
            else:
                Sensation.min_cache_memorability = Sensation.min_cache_memorability - 0.1
        
        # delete quickly last created Sensations that are not important
        while len(memory) > 0 and memory[0].isForgettable() and memory[0].getMemorability() < Sensation.min_cache_memorability:
            print('delete from sensation cache {}'.format(memory[0].toDebugStr()))
            memory[0].delete()
            del memory[0]

        # if we are still using too much memory for Sensations, we should check all Sensations in the cache
        notForgettables={}
        if Sensation.getMemoryUsage() > Sensation.maxRss or\
           Sensation.getAvailableMemory() < Sensation.minAvailMem:
            i=0
            while i < len(memory):
                if memory[i].isForgettable():
                    if memory[i].getMemorability() < Sensation.min_cache_memorability:
                        print('delete from sensation cache {}'.format(memory[i].toDebugStr()))
                        memory[i].delete()
                        del memory[i]
                    else:
                        i=i+1
                else:
                    numNotForgettables=numNotForgettables+1
                    for robot in memory[i].getAttachedBy():
                        if robot.getWho() not in notForgettables:
                            notForgettables[robot.getWho()] = 1
                        else:
                            notForgettables[robot.getWho()] = notForgettables[robot.getWho()]+1
                    i=i+1
       
#        print('Sensations cache for {} {} {} {} {} {} Total memory usage {} MB with Sensation.min_cache_memorability {}'.\
        print('Sensations cache for {} {} {} {} {} {} Total memory  usage {} MB available {} MB with Sensation.min_cache_memorability {}'.\
              format(Sensation.getMemoryTypeString(Sensation.MemoryType.Sensory), len(Sensation.sensationMemorys[Sensation.MemoryType.Sensory]),\
                     Sensation.getMemoryTypeString(Sensation.MemoryType.Working), len(Sensation.sensationMemorys[Sensation.MemoryType.Working]),\
                     Sensation.getMemoryTypeString(Sensation.MemoryType.LongTerm), len(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm]),\
                     Sensation.getMemoryUsage(), Sensation.getAvailableMemory(), Sensation.min_cache_memorability))
        if numNotForgettables > 0:
            print('Sensations cache deletion skipped {} Not Forgottable Sensation'.format(numNotForgettables))
            for robotName, notForgottableNumber in notForgettables.items():
                print ('Sensations cache Not Forgottable robot {} number {}'.format(robotName, notForgottableNumber))
        #print('Memory usage for {} Sensations {} after {} MB'.format(len(memory), Sensation.getMemoryTypeString(sensation.getMemoryType()), Sensation.getMemoryUsage()-Sensation.startSensationMemoryUsageLevel))
         
    '''
    Association is a association between two sensations
    There is score and time when used, so we cab calculate strength of this association.
    Association can be only with Long Term and Work Memory Sensations, because Sensory
    sensations don't live that long.
    Work Memory Associations can't be save but Long Term Memory Association can.
    Owner is nor mentioned, so we have only one sensation in one association
    Association are identical in both sides, so reverse Association is found
    in connected Sensation.
    '''
        
    class Association(object):
        Terrified='Terrified' 
        Afraid='Afraid'
        Disappointed='Disappointed'
        Worried='Worried'
        Neutral='Neutral'
        Normal='Normal'
        Good='Good'
        Happy='Happy'
        InLove='InLove'
        # Feeling, Feelings can be positive or negative, stronger or weaker
        Feeling = enum(Terrified=-5, Afraid=-3, Disappointed=-2, Worried=-1, Neutral=0, Normal=1, Good=2, Happy=3, InLove=5)
        Feelings = {
            Feeling.Terrified : Terrified,
            Feeling.Afraid : Afraid,
            Feeling.Disappointed : Disappointed,
            Feeling.Worried : Worried,
            Feeling.Neutral : Neutral,
            Feeling.Normal : Normal,
            Feeling.Good : Good,
            Feeling.Happy : Happy,
            Feeling.InLove : InLove
        }
        
        def __init__(self,
                     self_sensation,                        # this side of Association
                     sensation,                             # sensation to connect
                     time=None,                             # last used
                     score = 0.0,                           # score of association, used at least with item, float
                     feeling = Feeling.Neutral,             # feeling of association two sensations
                     two_sided = True):                     # do we make path side of the association, default is True
                                                            # stronger feeling make us (and robots) to remember association
                                                            # longer than neutral associations
                                                            # our behaver (and) robots has to goal to get good feelings
                                                            # and avoid negative ones
                                                            # first usage of feeling is wit Communication-Robot, make it
                                                            # classify Voices with good feeling when it gets responses
                                                            # and feel CVoice use with bad feeling, if it does not
                                                            # get a response
            self.time = time
            if self.time == None:
                self.time = systemTime.time()
            self.self_sensation = self_sensation
            self.sensation = sensation
            self.score = score
            self.feeling = feeling
#             if two_sided:
#                 # other part
#                 association = self.getAssociation(self.sensation)
#                 # for some reason we find this association at other side
#                 if association is not None:
#                     association.time = self.time
#                     association.score = self.score
#                     association.feeling = self.feeling
#                 else: # normal case, make association of other side looking to us
#                     association = Association (sensation = self.self_sensation,
#                                                time=self.time,                             
#                                                score = self.score,                           
#                                                feeling = self.feeling,             
#                                                two_sided = False)
#                     sensation.associatons.append(association)

# TODO next method can't work
    
        def getTime(self):
            return self.time
    
        def setTime(self, time = None):
            if time == None:
                time = systemTime.time()
            self.time = time
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            association.time = time
     
        def getSensation(self):
            return self.sensation

        ''''
        setSensation is tricky
        We should first remove old Association from Association.sensation
        and add this new Association
        so for now this is not allowed, but should be done explicit way
        
        def setSensation(self, sensation):
            self.sensation = sensation
            # other part
            association = self.getAssociation(self.sensation)
            if association is None:
               self.sensation.addAssociation(self) 
            else:
                association.time = self.time
                association.score = self.score
                association.feeling = self.feeling
        '''
             
        def getScore(self):
            return self.score
    
        def setScore(self, score):
            self.score = score
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            association.score = score

        def getFeeling(self):
            return self.feeling
    
        def setFeeling(self, feeling):
            self.feeling = feeling
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            if association is not None:
                association.feeling = feeling
        
        '''
        Change feeling to more positive or negative way
        '''    
        def changeFeeling(self, positive=True, negative=False):
            # this part
            self.doChangeFeeling(association=self, positive=positive, negative=negative)
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            if association is not None:
                self.doChangeFeeling(association=association, positive=positive, negative=negative)

        '''
        helper association Change feeling to more positive or negative way
        '''    
        def doChangeFeeling(self, association, positive=True, negative=False):
            if positive or not negative: # must be positive
                if association.feeling == association.Feeling.Terrified:
                    association.feeling = association.Feeling.Afraid
                elif association.feeling == association.Feeling.Afraid:
                    association.feeling = association.Feeling.Disappointed
                elif association.feeling == association.Feeling.Disappointed:
                    association.feeling = association.Feeling.Worried
                elif association.feeling == association.Feeling.Worried:
                    association.feeling = association.Feeling.Neutral
                elif association.feeling == association.Feeling.Neutral:
                    association.feeling = association.Feeling.Normal
                elif association.feeling == association.Feeling.Normal:
                    association.feeling = association.Feeling.Good
                elif association.feeling == association.Feeling.Good:
                    association.feeling = association.Feeling.Happy
                elif association.feeling == association.Feeling.Happy:
                    association.feeling = association.Feeling.InLove
            else:
                if association.feeling == association.Feeling.Afraid:
                    association.feeling = association.Feeling.Terrified
                elif association.feeling == association.Feeling.Disappointed:
                    association.feeling = association.Feeling.Afraid
                elif association.feeling == association.Feeling.Worried:
                    association.feeling = association.Feeling.Disappointed
                elif association.feeling == association.Feeling.Neutral:
                    association.feeling = association.Feeling.Worried
                elif association.feeling == association.Feeling.Normal:
                    association.feeling = association.Feeling.Neutral
                elif association.feeling == association.Feeling.Good:
                    association.feeling = association.Feeling.Normal
                elif association.feeling == association.Feeling.Happy:
                    association.feeling = association.Feeling.Good
                elif association.feeling == association.Feeling.InLove:
                    association.feeling = association.Feeling.Happy

        '''
        How important this association is.
        
        Pleasant most important Associations get high positive value,
        unpleasant most important Association get high negative value and
        meaningless Association get value near zero.
        
        Uses now Feeling as main factor and score as minor factor.
        Should use also time, so old Associations are not so important than
        new ones.
       '''
        def getImportance(self):
            if self.feeling >= 0:
                return float(self.feeling+1) * (1.0 + self.score)
            return float(self.feeling-1) * (1.0 + self.score)

    '''
    default constructor for Sensation
    '''
       
    def __init__(self,
                 robotId,                                                    # robot id (should be always given)
                 associations=None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = SensationType.Unknown,
                 memoryType=MemoryType.Sensory,
                 direction=Direction.Out,
                 who=None,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 filePath='',
                 data=b'',                                                  # ALSA voice is string (uncompressed voice information)
                 image=None,                                                # Image internal representation is PIl.Image 
                 calibrateSensationType = SensationType.Unknown,
                 capabilities = None,                                       # capabilitis of sensorys, direction what way sensation go
                 name = '',                                                 # name of Item
                 presence = Presence.Unknown,                               # presence of Item
                 kind=Kind.Normal):                                         # kind (for instance voice)
                                       
        from Config import Capabilities
        self.time=time
        if self.time == None:
            self.time = systemTime.time()

        self.robotId = robotId
        self.id = id
        if self.id == None:
            self.id = Sensation.getNextId()
            
        self.attachedBy = []
        self.associations =[]
        if  associations == None:
            associations = []
        # associate makes both sides
        for association in associations:
            self.associate(sensation=association.sensation,
                           time=association.time,
                           score=association.score,
                           feeling=association.feeling)

        # associations are always both way
        if sensation is not None:   # copy constructor
            # associate makes both sides
            for association in sensation.associations:
                self.associate(sensation=association.sensation,
                               time=association.time,
                               score=association.score,
                               feeling=association.feeling)
                
            self.receivedFrom=sensation.receivedFrom
            self.sensationType = sensation.sensationType
            self.memoryType = sensation.memoryType
            self.direction = sensation.direction
            self.who = sensation.who
            self.leftPower = sensation.leftPower
            self.rightPower = sensation.rightPower
            self.hearDirection = sensation.hearDirection
            self.azimuth = sensation.azimuth
            self.accelerationX = sensation.accelerationX
            self.accelerationY = sensation.accelerationY
            self.accelerationZ = sensation.accelerationZ
            self.observationDirection = sensation.observationDirection
            self.observationDistance = sensation.observationDistance
            self.filePath = sensation.filePath
            self.data = sensation.data
            self.image = sensation.image
            self.calibrateSensationType = sensation.calibrateSensationType
            self.capabilities = sensation.capabilities
            self.name = sensation.name
            self.presence = sensation.presence
            self.kind = sensation.kind
            #self.attachedBy = sensation.attachedBy # keep self.attachedBy independent of original Sensation to be copied
            
            # We have here put values from sensation, but we should
            # also set values that are overwritten
            # and we don't know them exactly
            # so we don't set then, but code should use set methods itself explicitly

        else:                
            self.sensationType = sensationType
            self.memoryType = memoryType
            self.direction = direction
            self.who = who
            self.leftPower = leftPower
            self.rightPower = rightPower
            self.hearDirection = hearDirection
            self.azimuth = azimuth
            self.accelerationX = accelerationX
            self.accelerationY = accelerationY
            self.accelerationZ = accelerationZ
            self.observationDirection = observationDirection
            self.observationDistance = observationDistance
            self.filePath = filePath
            self.data = data
            self.image = image
            self.calibrateSensationType = calibrateSensationType
            self.capabilities = capabilities
            self.name = name
            self.presence = presence
            self.kind = kind
            self.attachedBy = []
           
            # associate makes both sides
            for association in associations:
                self.associate(sensation=association.sensation,
                               time=association.time,
                               score=association.score,
                               feeling=association.feeling)
           
            if receivedFrom == None:
                receivedFrom=[]
            self.receivedFrom=[]
            self.addReceivedFrom(receivedFrom)

        if bytes != None:
            try:
                l=len(bytes)
                i=0

                self.robotId = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.id = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE

                self.memoryType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("memoryType " + str(memoryType))
                i += Sensation.ENUM_SIZE
                
                self.sensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("sensationType " + str(sensationType))
                i += Sensation.ENUM_SIZE
                
                self.direction = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("direction " + str(direction))
                i += Sensation.ENUM_SIZE
                
                if self.sensationType is Sensation.SensationType.Drive:
                    self.leftPower = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.rightPower = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.HearDirection:
                    self.hearDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Azimuth:
                    self.azimuth = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Acceleration:
                    self.accelerationX = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.accelerationY = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.accelerationZ = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Observation:
                    self.observationDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.observationDistance = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Voice:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("filePath_size " + str(filePath_size))
                    i += Sensation.ID_SIZE
                    self.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("data_size " + str(data_size))
                    i += Sensation.ID_SIZE
                    self.data = bytes[i:i+data_size]
                    i += data_size
                    self.kind = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                elif self.sensationType is Sensation.SensationType.Image:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("filePath_size " + str(filePath_size))
                    i += Sensation.ID_SIZE
                    self.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("data_size " + str(data_size))
                    i += Sensation.ID_SIZE
                    if data_size > 0:
                        self.image = PIL_Image.open(io.BytesIO(bytes[i:i+data_size]))
                    else:
                        self.image = None
                    i += data_size
                elif self.sensationType is Sensation.SensationType.Calibrate:
                    self.calibrateSensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                    if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                        self.hearDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Capability:
                    capabilities_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("capabilities_size " + str(capabilities_size))
                    i += Sensation.ID_SIZE
                    self.capabilities = Capabilities(bytes=bytes[i:i+capabilities_size])
                    i += capabilities_size
                elif self.sensationType is Sensation.SensationType.Item:
                    name_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("name_size " + str(name_size))
                    i += Sensation.ID_SIZE
                    self.name =bytesToStr(bytes[i:i+name_size])
                    i += name_size
                    self.presence = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                    
                association_id = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                print("association_id " + str(association_id))
                i += Sensation.ID_SIZE
                for j in range(association_id):
                    sensation_id=bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
               
                    time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                
                    score = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    feeling = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER, signed=True)
                    i += Sensation.ID_SIZE

                    sensation=Sensation.getSensationFromSensationMemory(id=sensation_id)
                    if sensation is not None:
                        # associate makes both sides
                        self.associate(sensation=sensation,
                                       time=time,
                                       score=score,
                                       feeling=feeling)
                
            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
                
           #  at the end receivedFrom (list of words)
            receivedFrom_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
            #print("receivedFrom_size " + str(receivedFrom_size))
            i += Sensation.ID_SIZE
            self.receivedFrom=bytesToList(bytes[i:i+receivedFrom_size])
            i += receivedFrom_size

               
        Sensation.addToSensationMemory(self)

    '''
    Constructor that takes care, that we have only one instance
    per Sensation per number
    
    This is needed if we want handle associations properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constructor
    '''
       
    def create(  robot,                                                      # caller Robot, should be always given
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = SensationType.Unknown,
                 memoryType=MemoryType.Sensory,
                 direction=Direction.In,
                 who=None,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 filePath='',
                 data=b'',
                 image=None,
                 calibrateSensationType = SensationType.Unknown,
                 capabilities = None,                                       # capabilities of sensorys, direction what way sensation go
                 name='',                                                   # name of Item
                 presence=Presence.Unknown,                                 # presence of Item
                 kind=Kind.Normal):                                         # Normal kind
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
        
        return sensation


#         if sensation is not None:             # not an update, create new one
#             print("Sensation.create Create new sensation instance of this sensation")
#             newSensation =  Sensation(associations=associations, sensation=sensation)
#             newSensation.setTime(systemTime.time())
#             return newSensation
# 
#         if bytes != None:               # if bytes, we get id there
#             id = bytesToFloat(bytes[0:Sensation.FLOAT_PACK_SIZE])
#  
#         sensation = None          
#         if id != None: # newer uswd try to find existing sensation by id 
#             sensation = Sensation.getSensationFromSensationMemory(id)
# 
#             
#         if sensation == None:             # not an update, create new one
#             print("Create new sensation by pure parameters")
#             return Sensation(
#                  bytes=bytes,
#                  id=id,
#                  time=time,
#                  associations=associations,
#                  receivedFrom=receivedFrom,
#                  sensationType = sensationType,
#                  memoryType=memoryType,
#                  direction=direction,
#                  leftPower = leftPower, rightPower = rightPower,                         # Walle motors state
#                  azimuth = azimuth,                                             # Walle direction relative to magnetic north pole
#                  accelerationX=accelerationX, accelerationY=accelerationY, accelerationZ=accelerationZ,   # acceleration of walle, coordinates relative to walle
#                  hearDirection = hearDirection,                                       # sound direction heard by Walle, relative to Walle
#                  observationDirection = observationDirection,observationDistance = observationDistance,        # Walle's observation of something, relative to Walle
#                  filePath=filePath,
#                  data=data,
#                  image=image,
#                  calibrateSensationType = calibrateSensationType,
#                  capabilities = capabilities,
#                  name=name)
#  
#         # TODO OOPS newer reach this code, but what is meaning of this. Maybe nothing
#         # We newer want to update existing sensation this way, so we can safely
#         # remove this code
#                    
#         print("Update existing sensation")
#         # update existing one    
#         sensation.time=time
#         if sensation.time == None:
#             sensation.time = systemTime.time()
# 
#         # associations are always both way
#         if associations == None:
#             associations=[]
#         sensation.associations=[]
#         # associate makes both sides
#         for association in associations:
#             sensation.associate(sensation=association.sensation,
#                                 time=association.time,
#                                 score=association.score,
#                                 feeling=association.feeling)
#                 
#         if receivedFrom == None:
#             receivedFrom=[]
#         sensation.receivedFrom=[]
#         sensation.addReceivedFrom(receivedFrom)
#                 
#         sensation.sensationType = sensationType
#         sensation.memoryType = memoryType
#         sensation.direction = direction
#         sensation.leftPower = leftPower
#         sensation.rightPower = rightPower
#         sensation.hearDirection = hearDirection
#         sensation.azimuth = azimuth
#         sensation.accelerationX = accelerationX
#         sensation.accelerationY = accelerationY
#         sensation.accelerationZ = accelerationZ
#         sensation.observationDirection = observationDirection
#         sensation.observationDistance = observationDistance
#         sensation.filePath = filePath
#         sensation.data = data
#         sensation.image = image
#         sensation.calibrateSensationType = calibrateSensationType
#         sensation.capabilities = capabilities
#         sensation.name=name
# 
#         if bytes != None:
#             try:
#                 l=len(bytes)
#                 i=0
#  
#                 sensation.id = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                 i += Sensation.FLOAT_PACK_SIZE
#                    
#                 sensation.time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                 i += Sensation.FLOAT_PACK_SIZE
#                 
#                 sensation.memoryType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
#                 #print("memoryType " + str(memoryType))
#                 i += Sensation.ENUM_SIZE
#                     
#                 sensation.sensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
#                 #print("sensationType " + str(sensationType))
#                 i += Sensation.ENUM_SIZE
#                     
#                 sensation.direction = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
#                 #print("direction " + str(direction))
#                 i += Sensation.ENUM_SIZE
#                     
#                 if sensation.sensationType is Sensation.SensationType.Drive:
#                     sensation.leftPower = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                     sensation.rightPower = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                 elif sensation.sensationType is Sensation.SensationType.HearDirection:
#                     sensation.hearDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                 elif sensation.sensationType is Sensation.SensationType.Azimuth:
#                     sensation.azimuth = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                 elif sensation.sensationType is Sensation.SensationType.Acceleration:
#                     sensation.accelerationX = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                     sensation.accelerationY = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                     sensation.accelerationZ = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                 elif sensation.sensationType is Sensation.SensationType.Observation:
#                     sensation.observationDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                     sensation.observationDistance = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                 elif sensation.sensationType is Sensation.SensationType.Voice:
#                     filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                     print("filePath_size " + str(filePath_size))
#                     i += Sensation.ID_SIZE
#                     sensation.filePath = bytesToStr(bytes[i:i+filePath_size])
#                     i += filePath_size
#                     data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                     print("data_size " + str(data_size))
#                     i += Sensation.ID_SIZE
#                     sensation.data = bytes[i:i+data_size]
#                     i += data_size
#                 elif sensation.sensationType is Sensation.SensationType.Image:
#                     filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                     print("filePath_size " + str(filePath_size))
#                     i += Sensation.ID_SIZE
#                     sensation.filePath =bytesToStr(bytes[i:i+filePath_size])
#                     i += filePath_size
#                     data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                     print("data_size " + str(data_size))
#                     i += Sensation.ID_SIZE
#                     if data_size > 0:
#                         sensation.image = PIL_Image.open(io.BytesIO(bytes[i:i+data_size]))
#                     else:
#                         sensation.image = None
#                     i += data_size
#                 elif sensation.sensationType is Sensation.SensationType.Calibrate:
#                     sensation.calibrateSensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
#                     i += Sensation.ENUM_SIZE
#                     if sensation.calibrateSensationType == Sensation.SensationType.HearDirection:
#                         sensation.hearDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                         i += Sensation.FLOAT_PACK_SIZE
#                 elif sensation.sensationType is Sensation.SensationType.Capability:
#                     capabilities_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                     print("capabilities_size " + str(capabilities_size))
#                     i += Sensation.ID_SIZE
#                     sensation.capabilities = Capabilities(bytes=bytes[i:i+capabilities_size])
#                     i += capabilities_size
#                 elif sensation.sensationType is Sensation.SensationType.Item:
#                     name_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                     print("name_size " + str(name_size))
#                     i += Sensation.ID_SIZE
#                     sensation.name =bytesToStr(bytes[i:i+name_size])
#                     i += name_size
#                         
#                 association_id = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                 print("association_id " + str(association_id))
#                 i += Sensation.ID_SIZE
#                 for j in range(association_id):
#                     sensation_id=bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                
#                     time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                 
#                     score = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                     i += Sensation.FLOAT_PACK_SIZE
#                     
#                     feeling = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER)
#                     i += Sensation.ID_SIZE
# 
#                     connected_sensation=Sensation.getSensationFromSensationMemory(id=sensation_id)
#                     if connected_sensation is not None:
#                         # associate makes both sides
#                         sensation.associate(sensation=connected_sensation,
#                                             time=time,
#                                             score=score,
#                                             feeling=feeling)
#                 
#                  #  at the end receivedFros (list of words)
#                 receivedFrom_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
#                 print("receivedFrom_size " + str(receivedFrom_size))
#                 i += Sensation.ID_SIZE
#                 sensation.receivedFrom = bytesToList(bytes[i:i+receivedFrom_size])
#                 i += receivedFrom_size
#     
#             except (ValueError):
#                 sensation.sensationType = Sensation.SensationType.Unknown
                       
        return sensation
    
    def __cmp__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
            print('__cmp__ self.id == other.id ' +  str(self.id) + ' == ' + str(other.id) + ' ' + str(self.id == other.id))
            return self.id == other.id
        else:
            print('__cmp__ other is not Sensation')
            return False
 
    def getNextId():
        return systemTime.time()+random.uniform(Sensation.LOWPOINT_NUMBERVARIANCE, Sensation.HIGHPOINT_NUMBERVARIANCE)

#     def nextId(self):
#         return self.getTime()+random.uniform(Sensation.LOWPOINT_NUMBERVARIANCE, Sensation.HIGHPOINT_NUMBERVARIANCE)
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
#            print('__eq__ self.id == other.id ' +  str(self.id) + ' == ' + str(other.id) + ' ' + str(self.id == other.id))
            return self.id == other.id
        else:
#            print('__eq__ other is not Sensation')
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

                 
    def __str__(self):
        s=str(self.robotId) + ' ' + str(self.id) + ' ' + str(self.time) + ' ' + self.memoryType + ' ' + self.direction + ' ' + self.sensationType
        if self.sensationType == Sensation.SensationType.Drive:
            s +=  ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensationType == Sensation.SensationType.HearDirection:
            s +=  ' ' + str(self.hearDirection)
        elif self.sensationType == Sensation.SensationType.Azimuth:
            s += ' ' + str(self.azimuth)
        elif self.sensationType == Sensation.SensationType.Acceleration:
            s +=  ' ' + str(self.accelerationX)+ ' ' + str(self.accelerationY) + ' ' + str(self.accelerationZ)
        elif self.sensationType == Sensation.SensationType.Observation:
            s += ' ' + str(self.observationDirection)+ ' ' + str(self.observationDistance)
        elif self.sensationType == Sensation.SensationType.Voice:
            #don't write binary data to sring any more
            s += ' ' + self.filePath# + ' ' + bytesToStr(self.data)
            s +=  ' ' + self.kind
        elif self.sensationType == Sensation.SensationType.Image:
            s += ' ' + self.filePath# + ' ' +  bytesToStr(self.data)
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                s += ' ' + self.calibrateSensationType + ' ' + str(self.hearDirection)
            else:
                s = str(self.robotId) + ' ' + str(self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' +  Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            s +=  ' ' + self.getCapabilities().toString()
        elif self.sensationType == Sensation.SensationType.Item:
            s +=  ' ' + self.name
            s +=  ' ' + self.presence
           
#         elif self.sensationType == Sensation.SensationType.Stop:
#             pass
#         elif self.sensationType == Sensation.SensationType.Who:
#             pass
#         else:
#             pass

#        # at the end associations (ids)
        s += ' '
        i=0
        for association in self.associations:
            if i == 0:
                 s += str(association.getSensation().getId())
            else:
                s += LIST_SEPARATOR + str(association.getSensation().getId())
            i = i+1
#        # at the end receivedFrom
        s += ' '
        i=0
        for host in self.receivedFrom:
            if i == 0:
                 s += host
            else:
                s += LIST_SEPARATOR + host
            i = i+1
            
        return s

    '''
    Printable string
    '''
    def toDebugStr(self):
        # we can't make yet printable bytes, but as a debug purposes, it is rare neended
#         if self.sensationType == Sensation.SensationType.Voice or self.sensationType == Sensation.SensationType.Image :
#             s=str(self.robotId) + ' ' + str(self.id) + ' ' + str(self.time) + ' ' + str(self.association_time) + ' ' + Sensation.getMemoryTypeString(self.memoryType) + ' ' + Sensation.getDirectionString(self.direction) + ' ' + Sensation.getSensationTypeString(self.sensationType)
#         else:
#             s=self.__str__()
        s = systemTime.ctime(self.time) + ' ' + str(self.robotId) + ' ' + str(self.id) + ' ' + Sensation.getMemoryTypeString(self.memoryType) + ' ' + Sensation.getDirectionString(self.direction) + ' ' + Sensation.getSensationTypeString(self.sensationType)
        if self.sensationType == Sensation.SensationType.Voice:
            s = s + ' ' + Sensation.getKindString(self.kind)
        elif self.sensationType == Sensation.SensationType.Item:
            s = s + ' ' + self.name + ' ' + Sensation.getPresenceString(self.presence)
        return s

    def bytes(self):
#        b = self.id.to_bytes(Sensation.ID_SIZE, byteorder=Sensation.BYTEORDER)
        b = floatToBytes(self.robotId)
        b += floatToBytes(self.id)
        b += floatToBytes(self.time)
        b += StrToBytes(self.memoryType)
        b += StrToBytes(self.sensationType)
        b += StrToBytes(self.direction)

        if self.sensationType == Sensation.SensationType.Drive:
            b += floatToBytes(self.leftPower) + floatToBytes(self.rightPower)
        elif self.sensationType == Sensation.SensationType.HearDirection:
            b +=  floatToBytes(self.hearDirection)
        elif self.sensationType == Sensation.SensationType.Azimuth:
            b +=  floatToBytes(self.azimuth)
        elif self.sensationType == Sensation.SensationType.Acceleration:
            b +=  floatToBytes(self.accelerationX) + floatToBytes(self.accelerationY) + floatToBytes(self.accelerationZ)
        elif self.sensationType == Sensation.SensationType.Observation:
            b +=  floatToBytes(self.observationDirection) + floatToBytes(self.observationDistance)
        elif self.sensationType == Sensation.SensationType.Voice:
            bfilePath =  StrToBytes(self.filePath)
            filePath_size=len(bfilePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b += bfilePath
            
            data_size=len(self.data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  self.data
            b +=  StrToBytes(self.kind)
        elif self.sensationType == Sensation.SensationType.Image:
            filePath_size=len(self.filePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  StrToBytes(self.filePath)
            stream = io.BytesIO()
            if self.image is None:
                data = b''
            else:
                self.image.save(fp=stream, format=Sensation.IMAGE_FORMAT)
                data=stream.getvalue()
            data_size=len(data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  data
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                b += StrToBytes(self.calibrateSensationType) + floatToBytes(self.hearDirection)
#             else:
#                 return str(self.robotId) + ' ' + self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            bytes = self.getCapabilities().toBytes()
            capabilities_size=len(bytes)
            print("capabilities_size " + str(capabilities_size))
            b += capabilities_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b += bytes
        elif self.sensationType == Sensation.SensationType.Item:
            name_size=len(self.name)
            b +=  name_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  StrToBytes(self.name)
            b +=  StrToBytes(self.presence)
            
        #  at the end associations (ids)
        association_id=len(self.associations)
        b +=  association_id.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        for j in range(association_id):
            b +=  floatToBytes(self.associations[j].getSensation().getId())
            b +=  floatToBytes(self.associations[j].getTime())
            b +=  floatToBytes(self.associations[j].getScore())
            b +=  (self.associations[j].getFeeling()).to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER, signed=True)
       #  at the end receivedFrom (list of words)
        blist = listToBytes(self.receivedFrom)
        #print(' blist ' +str(blist))
        blist_size=len(blist)
        b +=  blist_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        b += blist
        

# all other done
#         elif self.sensationType == Sensation.SensationType.Stop:
#             return str(self.robotId) + ' ' +str(self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' + self.sensationType
#         elif self.sensationType == Sensation.SensationType.Who:
#             return str(self.robotId) + ' ' +str(self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' + self.sensationType
#         else:
#             return str(self.robotId) + ' ' +str(self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' + self.sensationType
        
        return b


    def getTime(self):
        return self.time

    def setTime(self, time = None):
        if time == None:
            time = systemTime.time()
        self.time = time

    '''
    Get latest time, when this Sensation was used
    '''
    def getLatestTime(self):
        latest_time=self.time
        for association in self.associations:
            # TODO we could also recursive check all associations when one was latest used, but ...
            if association.getTime() > latest_time:
                latest_time=association.getTime()
        return latest_time
    
    '''
    How much livetime as a ratio there is left (1.0 -> 0.0) for this sensation
    
    Note, that when Sensation is referenced, used its reference-time is renewed
    and it get full livetime again    
    '''
    def getLiveTimeLeftRatio(self):
        liveTimeLeftRatio = \
                (Sensation.sensationMemoryLiveTimes[self.getMemoryType()] - (systemTime.time()-self.getLatestTime())) / \
                Sensation.sensationMemoryLiveTimes[self.getMemoryType()]
        if liveTimeLeftRatio < 0.0:
            liveTimeLeftRatio = 0.0
            
        return liveTimeLeftRatio
        
    
    '''
    Memorability of this Sensation
        
    Memorability goes down by time. We use logarithm and Memory type
    Sensory Sensations have very high Memorability when Sensation has low age
    but memorability goes down in very short time.
    Here we use log10(livetimeratio left)
        
    LongTerm Sensation have low memorability when the are created,
    but memorability goes down with a long time.
    Here we use ln(livetimeratio left)

       '''
    def getMemorability(self):
        try:
            if self.getMemoryType() == Sensation.MemoryType.Sensory:
                memorability =  10.0 * (math.log10(10.0 + 10.0 * self.getLiveTimeLeftRatio()) -1.0)
            elif self.getMemoryType() == Sensation.MemoryType.Working:
                memorability =  math.e * (math.log(math.e + math.e * self.getLiveTimeLeftRatio()) - 1.0)
            else:
                #memorability =  0.5 * math.e * (math.log(math.e + math.e * self.getLiveTimeLeftRatio()) - 1.0)
                memorability =  math.e * (math.log10(10.0 + 10.0 * self.getLiveTimeLeftRatio()) -1.0)
        except Exception as e:
            #print("getMemorability error " + str(e))
            memorability = 0.0
        if memorability < 0.0:
             memorability = 0.0
           
        return memorability

    
    # TODO Association time logic is different
    
#     def setAssociationTime(self, parents=None, association_time = None):
#         if association_time == None:
#             association_time = systemTime.time()
#         self.association_time = association_time
#         if parents is None:
#             parents=[]
#         parents.append(self)
#         for association in self.associations:
# #            association.setAssociationTime(association_time)
# #            TODO comes infinite loop
# #            Below works, if we have refenece as a star
#             if parents is None or association not in  parents:
#                 association.setAssociationTime(parents=parents, association_time=association_time)


    def setId(self, id):
        self.id = id
    def getId(self):
        return self.id
    
    def setRobotId(self, robotId):
        self.robotId = robotId
    

# Cant do this. Look addAssociations. But this is not used    
#     def setAssociations(self, associations):
#         self.associations = associations
#         time = systemTime.time()
#         for association in self.associations:
#             association.time = time
        
    '''
    for debugging reasons log what associations there is in our Long Term Memory
    '''  
    def logAssociations(sensation):
        if sensation.getSensationType() is Sensation.SensationType.Item:
            print('Associations: ' + sensation.getName())
            parents=[sensation]
            parents = Sensation.logSensationAssociations(level=1, parents=parents, associations=sensation.getAssociations())
            print('Associations: ' + sensation.getName() + ' >= ' + str(len(parents )-1) + ' associations')


    '''
    for debugging reasons log what associations there is in our Lng Term Memory
    '''  
    def logSensationAssociations(level, parents, associations):
#         tag=''
#         for i in range(0,level):
#             tag=tag+'-'
        tag=str(level)+': '
        for association in associations:
            sensation = association.getSensation()
            if sensation not in parents:
                if sensation.getSensationType() is Sensation.SensationType.Item:
                    print(tag + ' Item: ' + sensation.getName() + ' ' + str(len(parents )))
                else:
                    print(tag + Sensation.SensationTypes[sensation.getSensationType()] + ' ' + str(len(parents )))
                parents.append(sensation)
 
                if level < Sensation.ASSOCIATIONS_LOG_MAX_LEVEL and len(parents) < Sensation.ASSOCIATIONS_LOG_MAX_PARENTS:            
                    parents = Sensation.logSensationAssociations(level=level+1, parents=parents, associations=sensation.getAssociations())
        return parents

    
    '''
    Add single association
    Associations are always two sided, but not referencing to self
    So this method should always be called twice. Look associate -helper method!
    '''
    def addAssociation(self, association):
        # this side
        time = systemTime.time()
        if association.getSensation() != self and \
           not self.isConnected(association):
            #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
            self.associations.append(association)
            association.time = time
        # other side
# temporary test
#         other_association = Sensation.Association(self_sensation=association.getSensation(),
#                                                   sensation=self,
#                                                   time=association.getTime(),
#                                                   score=association.getScore(),
#                                                   feeling=association.getFeeling(),
#                                                   two_sided=False)
#         if not other_association.getSensation().isConnected(association):
#             #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
#             association.getSensation().associations.append(other_association)
#             other_association.time = time
        
        
            ## TODO howto do reverse association
            #association.getSensation().addAssociation(Sensation.Association(self_sensation=, sensation=self))
            
    '''
    Helper function to create Association and add it 
    '''
    def associate(self,
                  sensation,                             # sensation to connect
                  time=None,                             # last used
                  score = 0.0,                           # score of association, used at least with item, float
                  feeling = Association.Feeling.Neutral):             # feeling of association two sensations
#                  two_sided = True):                     # do we make path side of the association, default is True
# TODO self_sensation can be removed, it was bad idea
        self.addAssociation(Sensation.Association(self_sensation = self,
                                                  sensation = sensation,
                                                  time = time,
                                                  score = score,
                                                  feeling = feeling))
#                                       two_sided = two_sided))

        sensation.addAssociation(Sensation.Association(self_sensation = sensation,
                                                       sensation = self,
                                                       time = time,
                                                       score = score,
                                                       feeling = feeling))

    
    '''
    Is this Sensation in this Association already connected
    '''
    def isConnected(self, association):
        #print('isConnected ' + self.toDebugStr() + ' has ' + str(len(self.associations)) + ' associations')
        is_connected = False
        for asso in self.associations:
            if asso.getSensation() == association.getSensation():
                is_connected = True
                #print('isConnected ' + self.toDebugStr() + ' found association to ' + con.getSensation().toDebugStr() + ' == ' + association.getSensation().toDebugStr() + ' ' + str(is_connected))
                break
        #print('isConnected ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr() + ' ' + str(is_connected))
        return is_connected
 
    '''
    get Association by Sensation
    '''
    def getAssociation(self, sensation):
        for association in self.associations:
            if sensation == association.getSensation():
                return association
        return None
       
    '''
    Add many associations
    '''
    def addAssociations(self, associations):
        for association in associations:
            self.associate( sensation = association.sensation,
                            time = association.time,
                            score = association.score,
                            feeling = association.feeling)

    def getAssociations(self):
# don't set time, if just gets reference, but not known if even used
#         time = systemTime.time()
#         for association in self.associations:
#             association.time = time
        return self.associations
    
    '''
    remove associations from this sensation connected to sensation given as parameter
    '''
    def removeAssociation(self, sensation):
        #i=0
        for association in self.associations:
            if association.getSensation() == sensation:
#                print("self.associations.remove(association)")
                self.associations.remove(association)
#                 del self.associations[i]
#             else:
#                 i=i+1
        #other side
#        i=0
        for association in sensation.associations:
            if association.getSensation() == self:
#                print("sensation.associations.remove(association)")
                sensation.associations.remove(association)
#                 del sensation.associations[i]
#             else:
#                 i=i+1

    def getAssociationIds(self):
        associationIds=[]
        for association in self.associations:
            associationIds.append(association.getSensation().getId())
        return associationIds
 
    def getScore(self):
        score = 0.0
        # one level associations
        best_association = None
        for association in self.associations:
            if association.getScore() > score:
                score = association.getScore()
                best_association = association
        if best_association is not None:
            best_association.time = systemTime.time()
            
        return score
    
    def getFeeling(self):
        feeling = Sensation.Association.Feeling.Neutral
        # one level associations
        best_association = None
        for association in self.associations:
            if abs(association.getFeeling()) > abs(feeling):
                feeling = association.getFeeling()
                best_association = association
        if best_association is not None:
            best_association.time = systemTime.time()
            
        return feeling
    
    def getImportance(self, positive=True, negative=False, absolute=False):
        if positive:
            importance = Sensation.Association.Feeling.Terrified
        if negative:
             importance = Sensation.Feeling.InLove
        if absolute:
            importance = 0.0
        # one level associations
        best_association = None
        for association in self.associations:
            if positive:
                if association.getImportance() > importance:
                    importance = association.getImportance()
                    best_association = association
            if negative:
                if association.getImportance() < importance:
                    importance= association.getImportance()
                    best_association = association
            if absolute:
                if abs(association.getImportance()) > abs(importance):
                    importance = association.getImportance()
                    best_association = association
        if best_association is not None:
            best_association.time = systemTime.time()
            
        return self.getMemorability() * importance

    '''
    Add many associations by association ids
    associations and associations to then are found from association cache
    
    REMOVED, implicit imp+lementation!
    '''
#     def addAssociationIds(self, associationIds):
#         for associationId in associationIds:
#             associations = Sensation.getSensationsFromSensationMemory(associationId)
#             self.addAssociations(associations)

    '''
    Has sensation association to other Sensation
    which SensationType is 'associationSensationType'
    '''
    def hasAssociationSensationType(self, associationSensationType,
                                    associationDirection = Direction.Out,
                                    ignoredSensations=[],
                                    ignoredVoiceLens=[]):
        has=False
        for association in self.associations:
            if association.getSensation().getSensationType() == associationSensationType and\
               association.getSensation().getDirection() == associationDirection and\
               association.getSensation() not in ignoredSensations and\
               len(association.getSensation().getData()) not in ignoredVoiceLens:
                has=True
                break       
        return has
     
    '''
    Get sensation association to other Sensation
    which SensationType is 'associationSensationType'
    '''
    def getAssociationsbBySensationType(self, associationSensationType,
                                        associationDirection = Direction.Out,
                                        ignoredSensations=[],
                                        ignoredVoiceLens=[]):
        associations=[]
        for association in self.associations:
            if association.getSensation().getSensationType() == associationSensationType and\
               association.getSensation().getDirection() == associationDirection and\
               association.getSensation() not in ignoredSensations and\
               len(association.getSensation().getData()) not in ignoredVoiceLens:
                associations.append(association)
        return associations
    def setReceivedFrom(self, receivedFrom):
        self.receivedFrom = receivedFrom
        
    '''
    Add single receivedFrom
    '''
    def addReceived(self, host):
        if host not in self.receivedFrom:
            self.receivedFrom.append(host)
         
    '''
    Add many receiveds
    '''
    def addReceivedFrom(self, receivedFrom):
        for host in receivedFrom:
            self.addReceived(host)

    def getReceivedFrom(self):
        return self.receivedFrom
    
    '''
    returns True, if this Sensation is received from this host
    Method is uded to avoid sendinmg Senation back fron some host, even if
    if has been originally setn from this host. This situation causes
    circulating Senastions for ever between hosts that have same capability to handle
    same Senastion type with same Memory level, so we must avoid it.
    
    Still it in allowed to process same senmsation type sensations with different
    menory level in different hosts, so we mustset self.receivedFrom, when we
    chage SEnsations menory level (or copy sensation to different meemory level.
    '''
    def isReceivedFrom(self, host):
        return host in self.receivedFrom
           
    def setSensationType(self, sensationType):
        self.sensationType = sensationType
    def getSensationType(self):
        return self.sensationType
       
    def setMemory(self, memoryType):
        if self.getMemoryType() != memoryType:
            memoryLock.acquireWrite()  # thread_safe                                     
            oldMemoryCache = Sensation.sensationMemorys[self.getMemoryType()]
            try:
                # remove from current menmory type cache and add to a new one
                oldMemoryCache.remove(self)
            except ValueError as e:
                print("oldMemoryCache.remove(self) error " + str(e))
                print("where self == " + self.toDebugStr())
                
            self.memoryType = memoryType
            #self.time = systemTime.time()   # if we change memoryType, this is new Sensation, NO keep times, association handles if associated later
            Sensation.forgetLessImportantSensations(self) # muat forget here. because if not created, this is only place fot Longerm-Senasations to be removed from cache
            Sensation.sensationMemorys[memoryType].append(self)
            memoryLock.releaseWrite()  # thread_safe   
           
# OOPS, we can't forget AWnasations at this point, because logic can need some other Sensations
#         
#         memoryLock.acquire()  # thread_safe                             
#         Sensation.forgetLessImportantSensations(sensation=self)
#         memoryLock.release()  # thread_safe                             

    def getMemoryType(self):
        return self.memoryType
       
    def setDirection(self, direction):
        self.direction = direction
    def getDirection(self):
        return self.direction
    
    def setWho(self, who):
        self.who = who
    def getWho(self):
        return self.who
        

       
    def setLeftPower(self, leftPower):
        self.leftPower = leftPower
    def getLeftPower(self):
        return self.leftPower
        
    def setRightPower(self, rightPower):
        self.rightPower = rightPower
    def getRightPower(self):
        return self.rightPower
    
    def setHearDirection(self, hearDirection):
        self.hearDirection = hearDirection
    def getHearDirection(self):
        return self.hearDirection

    def setAzimuth(self, azimuth):
        self.azimuth = azimuth
    def getAzimuth(self):
        return self.azimuth

    def setAccelerationX(self, accelerationX):
        self.accelerationX = accelerationX
    def getAccelerationX(self):
        return self.accelerationX
    def setAccelerationY(self, accelerationY):
        self.accelerationY = accelerationY
    def getAccelerationY(self):
        return self.accelerationY
    def setAccelerationZ(self, accelerationZ):
        self.accelerationZ = accelerationZ
    def getAccelerationZ(self):
        return self.accelerationZ

    def setObservationDirection(self, observationDirection):
        self.observationDirection = observationDirection
    def getObservationDirection(self):
        return self.observationDirection
    def setObservationDistance(self, observationDistance):
        self.observationDistance = observationDistance
    def getObservationDistance(self):
        return self.observationDistance

    def setData(self, data):
        self.data = data        
    def getData(self):
        return self.data
    
    def setImage(self, image):
        self.image = image        
    def getImage(self):
        return self.image
    
    def setFilePath(self, filePath):
        self.filePath = filePath       
    def getFilePath(self):
        return self.filePath
   
    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
    def getCapabilities(self):
        return self.capabilities

    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name

    def setPresence(self, presence):
        self.presence = presence
    def getPresence(self):
        return self.presence

    def setKind(self, kind):
        self.kind = kind
    def getKind(self):
        return self.kind

    '''
        Attach a Sensation to be used by a Robot so, that
        it is not removed from Sensation cache until detached
        
        Parameters
        robot    robot that attach this Sensation
    '''    
    def attach(self, robot):
        if robot not in self.attachedBy:
            self.attachedBy.append(robot)
    '''
        Detach a Sensation 
        
        Parameters
        robot    robot that detach this Sensation
    '''
    def detach(self, robot):
        if robot in self.attachedBy:
            self.attachedBy.remove(robot)

    '''
    get attached Robots
    '''            
    def getAttachedBy(self):
        return self.attachedBy
            
    '''
        is Sensation forgettable
    '''
            
    def isForgettable(self):
        return len(self.attachedBy) == 0

    '''
    save sensation data permanently
    '''  
    def save(self):
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)
            
        if self.getSensationType() == Sensation.SensationType.Image:       
            fileName = Sensation.DATADIR + '/' + '{}'.format(self.getId()) + \
                       '.' +  Sensation.IMAGE_FORMAT
            self.setFilePath(fileName)
            try:
                if not os.path.exists(fileName):
                    try:
                        with open(fileName, "wb") as f:
                            try:
                                self.getImage().save(f)
                            except IOError as e:
                                print("self.getImage().save(f)) error " + str(e))
                            finally:
                                f.close()
                    except Exception as e:
                        print('os.path.exists(' + fileName + ') error ' + str(e))
            except Exception as e:
                print("open(fileName, wb) as f error " + str(e))
        elif self.getSensationType() == Sensation.SensationType.Voice:       
            fileName = Sensation.DATADIR + '/' + '{}'.format(self.getId()) + \
                       '.' +  Sensation.VOICE_FORMAT
            self.setFilePath(fileName)
            try:
                if not os.path.exists(fileName):
                    try:
                        with open(fileName, "wb") as f:
                            try:
                                f.write(self.getData())
                            except IOError as e:
                                print("f.write(self.getData()) error " + str(e))
                            finally:
                                f.close()
                    except Exception as e:
                            print("open(fileName, wb) as f error " + str(e))
            except Exception as e:
                print("open(fileName, wb) as f error " + str(e))
     
    '''
    delete sensation data permanently
    but sensation will be remained to be deteted dy del
    You should call first 'sensation.delte()' and right a way 'del sensation'
    '''  
    def delete(self):
        for association in self.getAssociations():
            association.getSensation().removeAssociation(self)

        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)

        # first delete files this sensation has created            
        if self.getSensationType() == Sensation.SensationType.Image or \
           self.getSensationType() == Sensation.SensationType.Voice:
            if os.path.exists(self.getFilePath()): 
                try:
                    os.remove(self.getFilePath())
                except Exception as e:
                    print("os.remove(self.getFilePath() error " + str(e))
                    
    '''
    sensation getters
    '''
    def getSensationFromSensationMemory(id):
        memoryLock.acquireRead()                  # read thread_safe
 
        for key, sensationMemory in Sensation.sensationMemorys.items():
            if len(sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getId() == id:
                        memoryLock.releaseRead()  # read thread_safe
                        return sensation
        memoryLock.releaseRead()                  # read thread_safe
        return None

    def getSensationsFromSensationMemory(associationId):
        memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        for key, sensationMemory in Sensation.sensationMemorys.items():
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
    def getSensations(capabilities, timemin=None, timemax=None):
        memoryLock.acquireRead()                  # read thread_safe
        sensations=[]
        for key, sensationMemory in Sensation.sensationMemorys.items():
            for sensation in sensationMemory:
                if capabilities.hasCapability(direction=sensation.getDirection(),
                                              memoryType=sensation.getMemoryType(),
                                              sensationType=sensation.getSensationType()) and\
                   (timemin is None or sensation.getTime() > timemin) and\
                   (timemax is None or sensation.getTime() < timemax):
                    sensations.append(sensation)
        memoryLock.releaseRead()                  # read thread_safe
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
    
    def getBestSensation( sensationType,
                          timemin,
                          timemax,
                          direction = Direction.Out,
                          name = None,
                          notName = None,
                          associationSensationType = None,
                          associationDirection = Direction.Out,
                          ignoredVoiceLens=[]):
        memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        for key, sensationMemory in Sensation.sensationMemorys.items():
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
        memoryLock.releaseRead()                  # read thread_safe
        return bestSensation
    
    '''
    Get best connected sensation by score from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
    def getBestConnectedSensation( self,
                                   sensationType,
                                   name = None):
        memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        for association in self.getAssociations():
            sensation= association.getSensation()
            if sensation.getSensationType() == sensationType:
                if sensationType != Sensation.SensationType.Item or\
                   sensation.getName() == name:
                    if bestSensation is None or\
                       sensation.getScore() > bestSensation.getScore():
                        bestSensation = sensation
        memoryLock.releaseRead()                  # read thread_safe
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
    
    def getMostImportantSensation( sensationType,
                                   timemin,
                                   timemax,
                                   direction = Direction.Out,
                                   name = None,
                                   notName = None,
                                   associationSensationType = None,
                                   associationDirection = Direction.Out,
                                   ignoredSensations = [],
                                   ignoredVoiceLens = [],
                                   searchLength = 10):
#                                   searchLength = Sensation.SEARCH_LENGTH):
        memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        bestAssociation = None
        bestAssociationSensation = None
        # TODO starting with best score is not a good idea
        # if best scored item.name has only bad voices, we newer can get
        # good voices
        found_candidates=0
        for key, sensationMemory in Sensation.sensationMemorys.items():
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
            
        memoryLock.releaseRead()                  # read thread_safe
        return bestSensation, bestAssociation, bestAssociationSensation

    '''
    Get most important connected sensation by feeling and score from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
    def getMostImportantConnectedSensation( self,
                                            sensationType,
                                            name = None):
        memoryLock.acquireRead()                  # read thread_safe
        bestSensation = None
        for association in self.getAssociations():
            sensation= association.getSensation()
            if sensation.getSensationType() == sensationType:
                if sensationType != Sensation.SensationType.Item or\
                   sensation.getName() == name:
                    if bestSensation is None or\
                       sensation.getImportance() > bestSensation.getImportance():
                        bestSensation = sensation
        memoryLock.releaseRead()                  # read thread_safe
        return bestSensation

    '''
    save all LongTerm Memory sensation instances and data permanently
    so they can be loaded, when running app again
    '''  
    def saveLongTermMemory():
        # save sensations that are memorable to a file
        # there can be LOngTerm sensations in Sensation.sensationMemorys[Sensation.MemoryType.Sensory]
        # because it is allowed to change memoryType rtpe after sensation is created
        memoryLock.acquireRead()                  # read thread_safe
        for sensation in Sensation.sensationMemorys[Sensation.MemoryType.LongTerm]:
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
                    pickler.dump(Sensation.sensationMemorys[Sensation.MemoryType.LongTerm])
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
        memoryLock.releaseRead()                  # read thread_safe

    '''
    load LongTerm MemoryType sensation instances
    '''  
    def loadLongTermMemory():
        # load sensation data from files
        if os.path.exists(Sensation.DATADIR):
            memoryLock.acquireWrite()                  # write thread_safe
            try:
                with open(Sensation.PATH_TO_PICLE_FILE, "rb") as f:
                    try:
                        # TODO correct later
                        # whole Memory
                        #Sensation.sensationMemorys[Sensation.MemoryType.LongTerm] = \
                        version = pickle.load(f)
                        if version == Sensation.VERSION:
                            Sensation.sensationMemorys[Sensation.MemoryType.LongTerm] = pickle.load(f)
                            for key, sensationMemory in Sensation.sensationMemorys.items():
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
            memoryLock.releaseWrite()                  # write thread_safe
 
    '''
    Clean data directory fron data files, that are not connected to any sensation.
    '''  
    def CleanDataDirectory():
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
            memoryLock.acquireRead()                  # read thread_safe
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    # There can be image or voice files not any more needed
                    if filename.endswith('.'+Sensation.IMAGE_FORMAT) or\
                       filename.endswith('.'+Sensation.VOICE_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        if not Sensation.hasOwner(filepath):
                            print('os.remove(' + filepath + ')')
                            try:
                                os.remove(filepath)
                            except Exception as e:
                                print('os.remove(' + filepath + ') error ' + str(e))
            except Exception as e:
                    print('os.listdir error ' + str(e))
            memoryLock.releaseRead()                  # read thread_safe
            
    '''
    hasOwner is called from methos protected by semaphore
    so we should not protect this method
    '''        
                    
    def hasOwner(filepath):
        for key, sensationMemory in Sensation.sensationMemorys.items():
            if len(sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getSensationType() == Sensation.SensationType.Image or\
                       sensation.getSensationType() == Sensation.SensationType.Voice:
                        if sensation.getFilePath() == filepath:
                            return True
        return False
            
    
       
if __name__ == '__main__':

# testing
# create need a Robot as a parameter, so these test don't work until fixed
# TODO fromString(Sensation.toString) -tests are deprecated
# Sensation data in transferred by menory or by byte with tcp
# and str form is for debugging purposes
# Most importand sensations are now voice and image and string form does not handle
# parameters any more. Can be fixed if im plementing parameter type in string
# but it mo more vice to concentrate to byte tranfer for str test will be removed soon.

    from Config import Config, Capabilities
    config = Config()
    capabilities = Capabilities(config=config)
    
    s_Drive=Sensation(associations=[], sensationType = Sensation.SensationType.Drive, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print("str s  " + str(s_Drive))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getId())
    b=s_Drive.bytes()
    # TODO should s2 be here really association to s, same instance? maybe
    s2=Sensation(associations=[], bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getId())
    print("str s2 " + str(s2))
    print(str(s_Drive == s2))
    
    #test with create
    print("test with create")
    s_Drive_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Drive, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("Sensation.create: str s  " + str(s_Drive_create)))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getId())
    b=s_Drive_create.bytes()
    # TODO should s2 be here really association to s, same instance? maybe
    s2=Sensation.create(associations=[], bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getId())
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create:" + str(s_Drive_create == s2))
    print()

    
    s_Stop=Sensation(associations=[], sensationType = Sensation.SensationType.Stop, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In)
    print("str s  " + str(s_Stop))
    b=s_Stop.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Stop == s2))

    #test with create
    print("test with create")
    s_Stop_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Stop, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Stop_create)))
    b=s_Stop_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Stop_create == s2))
    print()
    
    s_Who=Sensation(associations=[], sensationType = Sensation.SensationType.Who, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In)
    print("str s  " + str(s_Who))
    b=s_Who.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Who == s2))
    
    #test with create
    print("test with create")
    s_Who_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Who, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Who_create)))
    b=s_Who_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Who_create == s2))
    print()

 
    # TODO
    # We can't  test this way any more, because SEnsation we create cant be used until it is created  
#     s_HearDirection=Sensation(associations=[Sensation.Association(self_sensation=s_HearDirection, sensation=s_Drive)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
#     print(("str s  " + str(s_HearDirection)))
#     b=s_HearDirection.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_HearDirection == s2))
# 
#     #test with create
#     print("test with create")
#     s_HearDirection_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_HearDirection_create, sensation=s_Drive_create)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
#     print(("Sensation.create: str s  " + str(s_HearDirection_create)))
#     b=s_HearDirection_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_HearDirection_create == s2))
#     print()
# 
#     s_Azimuth=Sensation(associations=[Sensation.Association(self_sensation=s_Azimuth, sensation=s_HearDirection)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
#     print(("str s  " + str(s_Azimuth)))
#     b=s_Azimuth.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Azimuth == s2))
# 
#     #test with create
#     print("test with create")
#     s_Azimuth_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Azimuth_create, sensation=s_Who_create)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
#     print(("Sensation.create: str s  " + str(s_Azimuth_create)))
#     b=s_Azimuth_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Azimuth_create == s2))
#     print()
# 
#     s_Acceleration=Sensation(associations=[Sensation.Association(self_sensation=s_Acceleration, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Acceleration, sensation=s_Azimuth)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Acceleration, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
#     print(("str s  " + str(s_Acceleration)))
#     b=s_Acceleration.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Acceleration == s2))
# 
#     #test with create
#     print("test with create")
#     s_Acceleration_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Acceleration_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Acceleration_create, sensation=s_Azimuth_create)], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Acceleration, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
#     print(("Sensation.create: str s  " + str(s_Acceleration_create)))
#     b=s_Acceleration_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " +str(s_Acceleration_create == s2))
#     print()
# 
#     
#     s_Observation=Sensation(associations=[Sensation.Association(self_sensation=s_Observation, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Observation, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Observation, sensation=s_Acceleration)], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Observation, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
#     print(("str s  " + str(s_Observation)))
#     b=s_Observation.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s_Observation == s2))
# 
#     #test with create
#     print("test with create")
#     s_Observation_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Observation_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Observation_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Observation_create, sensation=s_Acceleration_create)],  receivedFrom=['localhost', 'raspberry', 'virtualWalle',  'remoteWalle'], sensationType = Sensation.SensationType.Observation, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
#     print(("Sensation.create: str s  " + str(s_Observation_create)))
#     b=s_Observation_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Observation_create == s2))
#     print()
#     
#     # voice
#     s_VoiceFilePath=Sensation(associations=[Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_Observation),Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_HearDirection),Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_Azimuth),Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
#     print("str s  " + str(s_VoiceFilePath))
#     b=s_VoiceFilePath.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s_VoiceFilePath == s2))
# 
#     #test with create
#     print("test with create")
#     s_VoiceFilePath_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
#     print(("Sensation.create: str s  " + str(s_VoiceFilePath_create)))
#     b=s_VoiceFilePath_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_VoiceFilePath_create == s2))
#     print()
# 
#     s_VoiceData=Sensation(associations=[Sensation.Association(self_sensation=s_VoiceData, sensation=s_VoiceFilePath),Sensation.Association(self_sensation=s_VoiceData, sensation=s_Observation),Sensation.Association(self_sensation=s_VoiceData, sensation=s_HearDirection),Sensation.Association(self_sensation=s_VoiceData, sensation=s_Azimuth),Sensation.Association(self_sensation=s_VoiceData, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, data=b'\x01\x02\x03\x04\x05')
#     print(("str s  " + str(s_VoiceData)))
#     b=s_VoiceData.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_VoiceData == s2))
# 
#     #test with create
#     print("test with create")
#     s_VoiceData_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_VoiceFilePath_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In,  data=b'\x01\x02\x03\x04\x05')
#     print(("Sensation.create: str s  " + str(s_VoiceData_create)))
#     b=s_VoiceData_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " +str(s_VoiceData_create == s2))
#     print()
#     
#     # image    
#     s_ImageFilePath=Sensation(associations=[Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_Observation),Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_HearDirection),Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_Azimuth),Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
#     print(("str s  " + str(s_ImageFilePath)))
#     b=s_ImageFilePath.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_ImageFilePath == s2))
# 
#     #test with create
#     print("test with create")
#     s_ImageFilePath_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
#     print(("Sensation.create: str s  " + str(s_ImageFilePath_create)))
#     b=s_ImageFilePath_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_ImageFilePath_create == s2))
#     print()
# 
#     s_ImageData=Sensation(associations=[Sensation.Association(self_sensation=s_ImageData, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_ImageData, sensation=s_Observation),Sensation.Association(self_sensation=s_ImageData, sensation=s_HearDirection),Sensation.Association(self_sensation=s_ImageData, sensation=s_Azimuth),Sensation.Association(self_sensation=s_ImageData, sensation=s_Acceleration)], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
#     print("str s  " + str(s_ImageData))
#     b=s_ImageData.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_ImageData == s2))
# 
#     #test with create
#     print("test with create")
#     s_ImageData_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_ImageData_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.In, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
#     print("Sensation.create: str s  " + str(s_ImageData_create))
#     b=s_ImageData_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " +str(s_ImageData_create == s2))
#     print()
# 
#     s_Calibrate=Sensation(associations=[Sensation.Association(self_sensation=s_Calibrate, sensation=s_ImageData),Sensation.Association(self_sensation=s_Calibrate, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_Calibrate, sensation=s_Observation),Sensation.Association(self_sensation=s_Calibrate, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Calibrate, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Calibrate, sensation=s_Acceleration)], sensationType = Sensation.SensationType.Calibrate, memoryType = Sensation.MemoryType.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
#     print("str s  " + str(s_Calibrate))
#     b=s_Calibrate.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Calibrate == s2))
# 
#     #test with create
#     print("test with create")
#     s_Calibrate_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_ImageData_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Calibrate, memoryType = Sensation.MemoryType.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
#     print("Sensation.create: str s  " + str(s_Calibrate_create))
#     b=s_Calibrate_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Calibrate_create == s2))
#     print()
# 
# #    s_Capability=Sensation(associations=[s_Calibrate,s_VoiceData,s_VoiceFilePath,s_ImageData,s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Capability, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
#     s_Capability=Sensation(associations=[Sensation.Association(self_sensation=s_Capability, sensation=s_Calibrate),Sensation.Association(self_sensation=s_Capability, sensation=s_VoiceData),Sensation.Association(self_sensation=s_Capability, sensation=s_VoiceFilePath),Sensation.Association(self_sensation=s_Capability, sensation=s_ImageData),Sensation.Association(self_sensation=s_Capability, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_Capability, sensation=s_Observation),Sensation.Association(self_sensation=s_Capability, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Capability, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Capability, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, capabilities = capabilities)
#     print(("str s  " + str(s_Capability)))
#     b=s_Capability.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Capability == s2))
#     
#      #test with create
#     print("test with create")
#     s_Capability_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Capability_create, sensation=s_Calibrate_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_VoiceData_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_VoiceFilePath_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_ImageData_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, capabilities = capabilities)
#     print(("Sensation.create: str s  " + str(s_Capability_create)))
#     b=s_Capability_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Capability_create == s2))
#     
#     # item
#     
#     s_Item=Sensation(associations=[Sensation.Association(self_sensation=s_Item, sensation=s_Calibrate),Sensation.Association(self_sensation=s_Item, sensation=s_VoiceData),Sensation.Association(self_sensation=s_Item, sensation=s_VoiceFilePath),Sensation.Association(self_sensation=s_Item, sensation=s_ImageData),Sensation.Association(self_sensation=s_Item, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_Item, sensation=s_Observation),Sensation.Association(self_sensation=s_Item, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Item, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Item, sensation=s_Acceleration)], sensationType = Sensation.SensationType.Item, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, name='person')
#     print(("str s  " + str(s_Item)))
#     b=s_Item.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Item == s2))
#     
#      #test with create
#     print("test with create")
#     s_Item_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Item_create, sensation=s_Calibrate_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_VoiceData_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_VoiceFilePath_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_ImageData_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Item, memoryType = Sensation.MemoryType.Sensory, direction = Sensation.Direction.Out, name='person')
#     print(("Sensation.create: str s  " + str(s_Item_create)))
#     b=s_Item_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Item_create == s2))
    
   