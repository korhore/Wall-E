'''
Created on Feb 25, 2013
Edited on 22.05.2020

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
#from builtins import True
#import threading

try:
    import cPickle as pickle
#except ModuleNotFoundError:
except Exception as e:
#    print ("import cPickle as pickle error " + str(e))
    import pickle
    
#def enum(**enums):
#    return type('Enum', (), enums)
LIST_SEPARATOR=':'

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


'''
Sensation is something Robot senses
'''

class Sensation(object):
    VERSION=16          # version number to check, if we picle same version
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
    MIN_SCORE = 0.1                                          # min score all Sensations have score > 0 to get Memorability. This is lower than detected Item.name

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
    TRUE_AS_BYTE  =     b'\x01'
    FALSE_AS_BYTE  =    b'\x00'
    TRUE_AS_INT  =      1
    FALSE_AS_INR  =     0
    TRUE_AS_STR  =      'T'
    FALSE_AS_STR  =     'F'
     
    # so many sensationtypes, that first letter is not good idea any more  
    SensationType = enum(Drive='a', Stop='b', Who='c', Azimuth='d', Acceleration='e', Observation='f', HearDirection='g', Voice='h', Image='i',  Calibrate='j', Capability='k', Item='l', Feeling='m', Unknown='n')
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
    FEELING="Feeling"
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
               SensationType.Feeling: FEELING,
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
               SensationType.Feeling,
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

     # Sensation cache times
    sensationMemoryLiveTimes={
        MemoryType.Sensory:  SENSORY_LIVE_TIME,
        MemoryType.Working:  WORKING_LIVE_TIME,
        MemoryType.LongTerm: LONG_TERM_LIVE_TIME }
    
    # Feeling
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
    
    # byte conversions
    # try unicode-escape instead of utf8 toavoid error with non ascii characters bytes
    def strToBytes(e):
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
        return Sensation.strToBytes(ret_s)
        
    def bytesToList(b):
        #print('bytesToList b ' +str(b))
    
        ret_s = Sensation.bytesToStr(b)
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
    
    def booleanToBytes(boolean):
        if boolean:
            return Sensation.TRUE_AS_BYTE
        return Sensation.FALSE_AS_BYTE
    
    def bytesToBoolean(b):
        if b == Sensation.TRUE_AS_BYTE:
            return True
        return False
    def intToBoolean(i):
        if i == Sensation.TRUE_AS_INT:
            return True
        return False

    
    #helpers
        
    def getDirectionString(direction):
        ret = Sensation.Directions.get(direction)
        return ret
    def getDirectionStrings():
        return Sensation.Directions.values()
    
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

    def getFeelingString(feeling):
        if feeling == None:
            return ""
        return Sensation.Feelings.get(feeling)
    def getFeelingStrings():
        return Sensation.Feelings.values()
        
    '''
    get memory usage
    '''
    def getMemoryUsage():     
         #memUsage= resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0            
        return Sensation.process.memory_info().rss/(1024*1024)              # hope this works better
    
    '''
    get available memory
    '''
    def getAvailableMemory():
        return psutil.virtual_memory().available/(1024*1024)
    
        
    def strArrayToStr(sArray):
        retS = ''
        for s in sArray:
            if len(retS) == 0:
                retS=s
            else:
                retS += ' ' + s
        return retS
    
    def strToStrArray(s):
        return s.split(' ')
    
         
    '''
    Association is a association between two sensations
    There is time when used, so we cab calculate strength of this association.
    Association can be only with Long Term and Work Memory Sensations, because Sensory
    sensations don't live that long.
    Work Memory Associations can't be save but Long Term Memory Association can.
    Owner is nor mentioned, so we have only one sensation in one association
    Association are identical in both sides, so reverse Association is found
    in connected Sensation.
    '''
        
    class Association(object):
        
        def __init__(self,
                     self_sensation,                        # this side of Association
                     sensation,                             # sensation to connect
                     feeling,                               # feeling of association two sensations
                     time=None):                            # last used
#                     feeling = Sensation.Feeling.Neutral):  # feeling of association two sensations
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
            self.feeling = feeling

        def getTime(self):
            return self.time
    
        def setTime(self, time = None):
            if time == None:
                time = systemTime.time()
            self.time = time
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            association.time = time
            
        def Age(self):
            return systemTime.time() - self.getTime()
     
        def getSelfSensation(self):
            return self.self_sensation
        
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
                association.feeling = self.feeling
        '''
    
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
        def changeFeeling(self, positive=False, negative=False, otherPart=False):
            # this part
            self.doChangeFeeling(association=self, positive=positive, negative=negative)
            if otherPart:
                association = self.sensation.getAssociation(self.self_sensation)
                if association is not None:
                    self.doChangeFeeling(association=association, positive=positive, negative=negative)

        '''
        helper association Change feeling to more positive or negative way
        '''    
        def doChangeFeeling(self, association, positive=False, negative=False):
            if positive or not negative: # must be positive
                if association.feeling == Sensation.Feeling.Terrified:
                    association.feeling = Sensation.Feeling.Afraid
                elif association.feeling == Sensation.Feeling.Afraid:
                    association.feeling = Sensation.Feeling.Disappointed
                elif association.feeling == Sensation.Feeling.Disappointed:
                    association.feeling = Sensation.Feeling.Worried
                elif association.feeling == Sensation.Feeling.Worried:
                    association.feeling = Sensation.Feeling.Neutral
                elif association.feeling == Sensation.Feeling.Neutral:
                    association.feeling = Sensation.Feeling.Normal
                elif association.feeling == Sensation.Feeling.Normal:
                    association.feeling = Sensation.Feeling.Good
                elif association.feeling == Sensation.Feeling.Good:
                    association.feeling = Sensation.Feeling.Happy
                elif association.feeling == Sensation.Feeling.Happy:
                    association.feeling = Sensation.Feeling.InLove
            else:
                if association.feeling == Sensation.Feeling.Afraid:
                    association.feeling = Sensation.Feeling.Terrified
                elif association.feeling == Sensation.Feeling.Disappointed:
                    association.feeling = Sensation.Feeling.Afraid
                elif association.feeling == Sensation.Feeling.Worried:
                    association.feeling = Sensation.Feeling.Disappointed
                elif association.feeling == Sensation.Feeling.Neutral:
                    association.feeling = Sensation.Feeling.Worried
                elif association.feeling == Sensation.Feeling.Normal:
                    association.feeling = Sensation.Feeling.Neutral
                elif association.feeling == Sensation.Feeling.Good:
                    association.feeling = Sensation.Feeling.Normal
                elif association.feeling == Sensation.Feeling.Happy:
                    association.feeling = Sensation.Feeling.Good
                elif association.feeling == Sensation.Feeling.InLove:
                    association.feeling = Sensation.Feeling.Happy

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
                return float(self.feeling+1) * (1.0 + self.self_sensation.getScore())
            return float(self.feeling-1) * (1.0 + self.self_sensation.getScore())
        

    '''
    AssociationSensationIds is a association between two sensations ids
    It is helper class to save information of real association with sensations
    '''
        
    class AssociationSensationIds(object):
        
        def __init__(self,
                     sensation_id,                          # sensation_id to connect
                     feeling,                               # feeling of association two sensation_ids
                     time=None):                            # last used
            self.time = time
            if self.time == None:
                self.time = systemTime.time()
            self.sensation_id = sensation_id
            self.feeling = feeling

        def getTime(self):
            return self.time
    
        def setTime(self, time = None):
            if time == None:
                time = systemTime.time()
            self.time = time
             
        def getSensationId(self):
            return self.sensation_id
    
        def getFeeling(self):
            return self.feeling
    
        def setFeeling(self, feeling):
            self.feeling = feeling
        

    '''
    default constructor for Sensation
    '''       
    def __init__(self,
                 memory,
                 robotId,                                                    # robot id (should be always given)
                 associations=None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = SensationType.Unknown,
                 memoryType=None,
                 direction=Direction.Out,
                 who=None,
                 locations=[],
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
                 score = 0.0,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence = Presence.Unknown,                               # presence of Item
                 kind=Kind.Normal,                                          # kind (for instance voice)
                 firstAssociateSensation = None,                            # associated sensation first side
                 otherAssociateSensation = None,                            # associated Sensation other side
                 associateFeeling = Feeling.Neutral,                        # feeling of association
                 positiveFeeling=False,                                     # change association feeling to more positive direction if possible
                 negativeFeeling=False):                                    # change association feeling to more negative direction if possible
                                       
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
                           feeling=association.feeling)
        self.potentialAssociations = [] # does not have init value in creation,
                                        # but is always empty in creation

        # associations are always both way
        if sensation is not None:   # copy constructor
            # associate makes both sides
            Sensation.updateBaseFields(destination=self, source=sensation)
            for association in sensation.associations:
                self.associate(sensation=association.sensation,
                               time=association.time,
                               feeling=association.feeling)
                
            self.receivedFrom=sensation.receivedFrom
            self.sensationType = sensation.sensationType
            if memoryType == None:
                self.memoryType = sensation.memoryType
            else:
                self.memoryType = memoryType
                
            # We have here put values from sensation, but we should
            # also set values that are overwritten
            # and we don't know them exactly
            # so we don't set then, but code should use set methods itself explicitly

        else:                
            self.sensationType = sensationType
            if memoryType == None:
                self.memoryType = Sensation.MemoryType.Sensory
            else:
                self.memoryType = memoryType
            self.direction = direction
            self.who = who
            self.locations = locations
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
            self.score = score
            self.presence = presence
            self.kind = kind
            self.firstAssociateSensation = firstAssociateSensation
            self.otherAssociateSensation = otherAssociateSensation
            self.associateFeeling = associateFeeling
            self.positiveFeeling = positiveFeeling
            self.negativeFeeling = negativeFeeling

            self.attachedBy = []
           
            # associate makes both sides
            for association in associations:
                self.associate(sensation=association.sensation,
                               time=association.time,
                               feeling=association.feeling)
           
            if receivedFrom == None:
                receivedFrom=[]
            self.receivedFrom=[]
            self.addReceivedFrom(receivedFrom)

        if bytes != None:
            try:
                l=len(bytes)
                i=0
#                yougestTime=0.0

                self.robotId = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.id = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.time = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                yougestTime=self.time
                i += Sensation.FLOAT_PACK_SIZE

                self.memoryType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("memoryType " + str(memoryType))
                i += Sensation.ENUM_SIZE
                
                self.sensationType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("sensationType " + str(sensationType))
                i += Sensation.ENUM_SIZE
                
                self.direction = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("direction " + str(direction))
                i += Sensation.ENUM_SIZE
                                    
                location_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                #print("location_size " + str(location_size))
                i += Sensation.ID_SIZE
                self.locations = Sensation.strToStrArray(Sensation.bytesToStr(bytes[i:i+location_size]))
                i += location_size
                
                if self.sensationType is Sensation.SensationType.Drive:
                    self.leftPower = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.rightPower = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.HearDirection:
                    self.hearDirection = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Azimuth:
                    self.azimuth = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Acceleration:
                    self.accelerationX = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.accelerationY = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.accelerationZ = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Observation:
                    self.observationDirection = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.observationDistance = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif self.sensationType is Sensation.SensationType.Voice:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("filePath_size " + str(filePath_size))
                    i += Sensation.ID_SIZE
                    self.filePath =Sensation.bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("data_size " + str(data_size))
                    i += Sensation.ID_SIZE
                    self.data = bytes[i:i+data_size]
                    i += data_size
                    self.kind = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                elif self.sensationType is Sensation.SensationType.Image:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("filePath_size " + str(filePath_size))
                    i += Sensation.ID_SIZE
                    self.filePath =Sensation.bytesToStr(bytes[i:i+filePath_size])
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
                    self.calibrateSensationType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                    if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                        self.hearDirection = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
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
                    self.name =Sensation.bytesToStr(bytes[i:i+name_size])
                    i += name_size
                                        
                    self.score = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    self.presence = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                elif self.sensationType is Sensation.SensationType.Feeling:
                    firstAssociateSensation_id=Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.firstAssociateSensation = memory.getSensationFromSensationMemory(id=firstAssociateSensation_id)
                    
                    otherAssociateSensation_id=Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    self.otherAssociateSensation = memory.getSensationFromSensationMemory(id=otherAssociateSensation_id)
                    
                    self.associateFeeling = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER, signed=True)
                    i += Sensation.ID_SIZE
                    
                    self.positiveFeeling =  Sensation.intToBoolean(bytes[i])
                    i += Sensation.ENUM_SIZE
                    
                    self.negativeFeeling = Sensation.intToBoolean(bytes[i])
                    i += Sensation.ENUM_SIZE
                    
                association_id = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                print("association_id " + str(association_id))
                i += Sensation.ID_SIZE
                for j in range(association_id):
                    sensation_id = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
               
                    time = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                    if time > yougestTime:
#                        yougestTime=time
                    i += Sensation.FLOAT_PACK_SIZE
                
                    feeling = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER, signed=True)
                    i += Sensation.ID_SIZE

                    # should not associate yet, but let Memory choose if we use this instance of
                    # sensation with its associations or keep old instance, if we already have a copy
                    # of sensation with this id in our memory
                    self.potentialAssociations.append(Sensation.AssociationSensationIds(sensation_id=sensation_id,
                                                                                        time=time,
                                                                                        feeling=feeling))                
            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
                
           #  at the end receivedFrom (list of words)
            receivedFrom_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
            #print("receivedFrom_size " + str(receivedFrom_size))
            i += Sensation.ID_SIZE
            self.receivedFrom=Sensation.bytesToList(bytes[i:i+receivedFrom_size])
            i += receivedFrom_size
            
            # TODO Decide here is we should return this sensation or a copy of old one
            # but should we check it here or elsewhere
            
    '''
    update base fields
    '''
    def updateBaseFields(source, destination):
        destination.sensationType = source.sensationType
        destination.memoryType = source.memoryType
        destination.direction = source.direction
        destination.who = source.who
        destination.locations = source.locations
        destination.leftPower = source.leftPower
        destination.rightPower = source.rightPower
        destination.hearDirection = source.hearDirection
        destination.azimuth = source.azimuth
        destination.accelerationX = source.accelerationX
        destination.accelerationY = source.accelerationY
        destination.accelerationZ = source.accelerationZ
        destination.observationDirection = source.observationDirection
        destination.observationDistance = source.observationDistance
        destination.filePath = source.filePath
        destination.data = source.data
        destination.image = source.image
        destination.calibrateSensationType = source.calibrateSensationType
        destination.capabilities = source.capabilities
        destination.name = source.name
        destination.score = source.score
        destination.presence = source.presence
        destination.kind = source.kind
        destination.firstAssociateSensation = source.firstAssociateSensation
        destination.otherAssociateSensation = source.otherAssociateSensation
        destination.associateFeeling = source.associateFeeling
        destination.positiveFeeling = source.positiveFeeling
        destination.negativeFeeling = source.negativeFeeling


    
    def __cmp__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
            print('__cmp__ self.id == other.id ' +  str(self.id) + ' == ' + str(other.id) + ' ' + str(self.id == other.id))
            return self.id == other.id
        else:
            print('__cmp__ other is not Sensation')
            return False
 
    def getNextId():
        return Sensation.getRandom(base=systemTime.time(), randomMin=Sensation.LOWPOINT_NUMBERVARIANCE, randomMax=Sensation.HIGHPOINT_NUMBERVARIANCE)

    def getRandom(base, randomMin, randomMax):
        return base + random.uniform(randomMin, randomMax)
        
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
        s=str(self.robotId) + ' ' + str(self.id) + ' ' + str(self.time) + ' ' + self.memoryType + ' ' + self.direction + ' ' + self.sensationType+ ' ' + self.getLocationsStr()
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
            s += ' ' + self.filePath + ' ' + self.kind
        elif self.sensationType == Sensation.SensationType.Image:
            s += ' ' + self.filePath
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                s += ' ' + self.calibrateSensationType + ' ' + str(self.hearDirection)
            else:
                s = str(self.robotId) + ' ' + str(self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' +  Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            s +=  ' ' + self.getCapabilities().toString()
        elif self.sensationType == Sensation.SensationType.Item:
            s +=  ' ' + self.name
            s +=  ' ' + str(self.score)
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
        s = systemTime.ctime(self.time) + ':' + str(self.robotId) + ':' + str(self.id) + ':' + Sensation.getMemoryTypeString(self.memoryType) + ':' + Sensation.getDirectionString(self.direction) + ':' + Sensation.getSensationTypeString(self.sensationType)+ ':' + self.getLocationsStr()+ ':'
        if self.sensationType == Sensation.SensationType.Voice:
            s = s + ':' + Sensation.getKindString(self.kind)
#         elif self.sensationType == Sensation.SensationType.Image:
#             s = s + ':' + self.getLocationsStr()
        elif self.sensationType == Sensation.SensationType.Item:
            s = s + ':' + self.name + ':' + str(self.score) + ':' + Sensation.getPresenceString(self.presence)
        elif self.sensationType == Sensation.SensationType.Feeling:
            if self.getPositiveFeeling():
                s = s + ':positiveFeeling'
            if self.getNegativeFeeling():
                s = s + ':negativeFeeling'
            else:
                s = s + ':' + Sensation.getFeelingString(self.getAssociateFeeling())
            
        return s

    def bytes(self):
#        b = self.id.to_bytes(Sensation.ID_SIZE, byteorder=Sensation.BYTEORDER)
        b = Sensation.floatToBytes(self.robotId)
        b += Sensation.floatToBytes(self.id)
        b += Sensation.floatToBytes(self.time)
        b += Sensation.strToBytes(self.memoryType)
        b += Sensation.strToBytes(self.sensationType)
        b += Sensation.strToBytes(self.direction)
        
        location_size=len(self.getLocationsStr())
        b +=  location_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        b +=  Sensation.strToBytes(self.getLocationsStr())

        if self.sensationType is Sensation.SensationType.Drive:
            b += Sensation.floatToBytes(self.leftPower) + Sensation.floatToBytes(self.rightPower)
        elif self.sensationType is Sensation.SensationType.HearDirection:
            b +=  Sensation.floatToBytes(self.hearDirection)
        elif self.sensationType is Sensation.SensationType.Azimuth:
            b +=  Sensation.floatToBytes(self.azimuth)
        elif self.sensationType is Sensation.SensationType.Acceleration:
            b +=  Sensation.floatToBytes(self.accelerationX) + Sensation.floatToBytes(self.accelerationY) + Sensation.floatToBytes(self.accelerationZ)
        elif self.sensationType is Sensation.SensationType.Observation:
            b +=  Sensation.floatToBytes(self.observationDirection) + Sensation.floatToBytes(self.observationDistance)
        elif self.sensationType is Sensation.SensationType.Voice:
            bfilePath =  Sensation.strToBytes(self.filePath)
            filePath_size=len(bfilePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b += bfilePath
            
            data_size=len(self.data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  self.data
            b +=  Sensation.strToBytes(self.kind)
        elif self.sensationType is Sensation.SensationType.Image:
            filePath_size=len(self.filePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  Sensation.strToBytes(self.filePath)
            stream = io.BytesIO()
            if self.image is None:
                data = b''
            else:
                self.image.save(fp=stream, format=Sensation.IMAGE_FORMAT)
                data=stream.getvalue()
            data_size=len(data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  data
        elif self.sensationType is Sensation.SensationType.Calibrate:
            if self.calibrateSensationType is Sensation.SensationType.HearDirection:
                b += Sensation.strToBytes(self.calibrateSensationType) + Sensation.floatToBytes(self.hearDirection)
#             else:
#                 return str(self.robotId) + ' ' + self.id) + ' ' + self.memoryType + ' ' + self.direction + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType is Sensation.SensationType.Capability:
            bytes = self.getCapabilities().toBytes()
            capabilities_size=len(bytes)
            print("capabilities_size " + str(capabilities_size))
            b += capabilities_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b += bytes
        elif self.sensationType is Sensation.SensationType.Item:
            name_size=len(self.name)
            b +=  name_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  Sensation.strToBytes(self.name)
            b +=  Sensation.floatToBytes(self.score)
            b +=  Sensation.strToBytes(self.presence)
        elif self.sensationType is Sensation.SensationType.Feeling:
            b +=  Sensation.floatToBytes(self.getFirstAssociateSensation().getId())
            b +=  Sensation.floatToBytes(self.getOtherAssociateSensation().getId())
            b +=  self.getAssociateFeeling().to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER, signed=True)
            b +=  Sensation.booleanToBytes(self.getPositiveFeeling())
            b +=  Sensation.booleanToBytes(self.getNegativeFeeling())
           
        #  at the end associations (ids)
        association_id=len(self.associations)
        b +=  association_id.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        for j in range(association_id):
            b +=  Sensation.floatToBytes(self.associations[j].getSensation().getId())
            b +=  Sensation.floatToBytes(self.associations[j].getTime())
            b +=  (self.associations[j].getFeeling()).to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER, signed=True)
       #  at the end receivedFrom (list of words)
        blist = Sensation.listToBytes(self.receivedFrom)
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
            if self.getSensationType() == Sensation.SensationType.Feeling:   ## Feeling is functional Sensation
                memorability = 0.0
            elif self.getMemoryType() == Sensation.MemoryType.Sensory:
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


    def setId(self, id):
        self.id = id
    def getId(self):
        return self.id
    
    def setRobotId(self, robotId):
        self.robotId = robotId
            
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
        if association.getSensation() != self:
            oldAssociation = association.getSelfSensation().getAssociation(association.getSensation())
            if oldAssociation: #update old assiciation
                oldAssociation.setFeeling(association.getFeeling())
                oldAssociation.setTime(association.getTime())
            else:                             # create new association
                #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
                self.associations.append(association)
            
    '''
    Helper function to update or create an Association
    '''
    def associate(self,
                  sensation,                                    # sensation to connect
                  time=None,                                    # last used
                  feeling = Feeling.Neutral,                    # feeling of association two sensations
                  positiveFeeling = False,                      # change association feeling to more positive direction if possible
                  negativeFeeling = False):                     # change association feeling to more negativee direction if possible
#         self.addAssociation(Sensation.Association(self_sensation = self,
#                                                   sensation = sensation,
#                                                   time = time,
#                                                   feeling = feeling))
# 
#         sensation.addAssociation(Sensation.Association(self_sensation = sensation,
#                                                        sensation = self,
#                                                        time = time,
#                                                        feeling = feeling))
        self.upsertAssociation(self_sensation = self,
                               sensation = sensation,
                               time=time,
                               feeling = feeling,
                               positiveFeeling = positiveFeeling,
                               negativeFeeling = negativeFeeling)

        sensation.upsertAssociation(self_sensation = sensation,
                                    sensation = self,
                                    time=time,
                                    feeling = feeling,
                                    positiveFeeling = positiveFeeling,
                                    negativeFeeling = negativeFeeling)

    '''
    Helper function to update or create one side of Association
    '''
    def upsertAssociation(self,
                          self_sensation,                               # sensation
                          sensation,                                    # sensation to connect
                          time=None,                                    # last used
                          feeling = Feeling.Neutral,                    # feeling of association two sensations
                          positiveFeeling = False,                      # change association feeling to more positive direction if possible
                          negativeFeeling = False):                     # change association feeling to more negativee direction if possible
        # this side
        if time == None:
            time = systemTime.time()
        if self_sensation != sensation:
            oldAssociation = self_sensation.getAssociation(sensation)
            if oldAssociation: #update old assiciation
                if positiveFeeling:
                    oldAssociation.changeFeeling(positive=True)
                elif negativeFeeling:
                    oldAssociation.changeFeeling(negative=True)
                else:
                    oldAssociation.setFeeling(feeling)
                
                oldAssociation.setTime(time)
            else:                             # create new association
                #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
                self_sensation.associations.append(Sensation.Association(self_sensation = self,
                                                  sensation = sensation,
                                                  time = time,
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
                            feeling = association.feeling)

    def getAssociations(self):
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

    '''
    get sensations feeling
    
    if we gibe other sensation as parameter, we get exact feeling between them
    if other sennsation is not given, we get  best or worst feeling of oll association this sensation has
    '''    
    def getFeeling(self, sensation=None):
        feeling = Sensation.Feeling.Neutral
        if sensation:
            association = self.getAssociation(sensation=sensation)
            if association:
                feeling = association.getFeeling()
                association.time = systemTime.time()
        else:
            # one level associations
            best_association = None
            for association in self.associations:
                if abs(association.getFeeling()) > abs(feeling):
                    feeling = association.getFeeling()
                    best_association = association
            if best_association is not None:
                best_association.time = systemTime.time()
            
        return feeling
    
    # TODO Stidy logic    
    def getImportance(self, positive=True, negative=False, absolute=False):
        if positive:
            importance = Sensation.Feeling.Terrified
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
        if len(host) > 0 and host not in self.receivedFrom:
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
        
    def setLocations(self, locations):
        self.locations = locations
    def getLocations(self):
        return self.locations
    def getLocationsStr(self):
        #from Config import strArrayToStr
        return Sensation.strArrayToStr(self.locations)
      
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

    def setScore(self, score):
        self.score = score
    '''
    get highest score of associared  sensations
    '''    
    def getScore(self):
        score = Sensation.MIN_SCORE
        if self.score > score:
            score = self.score
        for association in self.getAssociations():
            # study only direct associations scores
            if association.getSensation().score > score:
                score = association.getSensation().score

        return score

    def setPresence(self, presence):
        self.presence = presence
    def getPresence(self):
        return self.presence

    def setKind(self, kind):
        self.kind = kind
    def getKind(self):
        return self.kind
    
    def setFirstAssociateSensation(self, firstAssociateSensation):
        self.firstAssociateSensation = firstAssociateSensation
    def getFirstAssociateSensation(self):
        return self.firstAssociateSensation
    
    def setOtherAssociateSensation(self, otherAssociateSensation):
        self.otherAssociateSensation = otherAssociateSensation
    def getOtherAssociateSensation(self):
        return self.otherAssociateSensation

    def setAssociateFeeling(self, associateFeeling):
        self.associateFeeling = associateFeeling
    def getAssociateFeeling(self):
        return self.associateFeeling
    
    def setPositiveFeeling(self, positiveFeeling):
        self.positiveFeeling = positiveFeeling
    def getPositiveFeeling(self):
        return self.positiveFeeling
    
    def setNegativeFeeling(self, negativeFeeling):
        self.negativeFeeling = negativeFeeling
    def getNegativeFeeling(self):
        return self.negativeFeeling
    

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
            fileName = '{}/{}.{}'.format(Sensation.DATADIR, self.getId(),\
                                         Sensation.IMAGE_FORMAT)
            self.setFilePath(fileName)
            try:
                if not os.path.exists(fileName):
                    try:
                        with open(fileName, "wb") as f:
                            try:
                                self.getImage().save(f)
                            except IOError as e:
                                print("self.getImage().save(f)) error {}".format(str(e)))
                            finally:
                                f.close()
                    except Exception as e:
                        print("Sensation.save Image open({}), wb) as f error {}".format(fileName, str(e)))
            except Exception as e:
                print('os.path.exists({}) error {}'.format(fileName, str(e)))
        elif self.getSensationType() == Sensation.SensationType.Voice:       
            fileName = '{}/{}.{}'.format(Sensation.DATADIR,self.getId(),Sensation.VOICE_FORMAT)
            self.setFilePath(fileName)
            try:
                if not os.path.exists(fileName):
                    try:
                        with open(fileName, 'wb') as f:
                            try:
                                f.write(self.getData())
                            except IOError as e:
                                print("f.write(self.getData()) error {}".format(str(e)))
                            finally:
                                f.close()
                    except Exception as e:
                        print("Sensation.save Voice1 open({}), wb) as f error {}".format(fileName, str(e)))
            except Exception as e:
                print("Sensation.save Voice2 not os.path.exists({}) error {}".format(fileName, str(e)))
     
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
    
   