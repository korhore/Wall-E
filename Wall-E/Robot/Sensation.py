'''
Created on Feb 25, 2013
Edited on 07.07.2019

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

import sys
import os
import time as systemTime
from enum import Enum
import struct
import random
from PIL import Image as PIL_Image
import io
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
            if len(ret_s) > 0:
                if i == 0:
                    ret_s = s
                else:
                    ret_s += LIST_SEPARATOR + str(s)
                i = i+1
            else:
                ret_s = s
    return StrToBytes(ret_s)
    
def bytesToList(b):
    ret_s = bytesToStr(b)
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
    VERSION=5           # version number to check, if we picle same version
                        # instances. Otherwise we get odd errors, with old
                        # version code instances

    # Association logging max-values                      
    ASSOCIATIONS_LOG_MAX_LEVEL =   10
    ASSOCIATIONS_LOG_MAX_PARENTS = 10           
    ASSOCIATIONS_MAX_ASSOCIATIONS = 50           

 
    #number=0                # sensation number for referencing
    IMAGE_FORMAT =      'jpeg'
    MODE =              'RGB'       # PIL_IMAGE mode, not used now, but this it is
    DATADIR =           'data'
    VOICE_FORMAT =      'wav'
    PICLE_FILENAME =    'Sensation.pkl'
    PATH_TO_PICLE_FILE = os.path.join(DATADIR, PICLE_FILENAME)
    LOWPOINT_NUMBERVARIANCE=-100.0
    HIGHPOINT_NUMBERVARIANCE=100.0
    
    SENSORY_CACHE_TIME =        300.0;       # cache sensation 300 seconds = 5 mins (may be changed)
    #WORKING_CACHE_TIME =        600.0;       # cache sensation 600 seconds = 10 mins (may be changed)
    LONG_TERM_CACHE_TIME =        3000.0;       # cache sensation 3000 seconds = 50 mins (may be changed)
    LENGTH_SIZE =       2   # Sensation as string can only be 99 character long
    LENGTH_FORMAT =     "{0:2d}"
    SEPARATOR =         '|'  # Separator between messages
    SEPARATOR_SIZE =    1  # Separator length
    
    ENUM_SIZE =         1
    NUMBER_SIZE =       4
    BYTEORDER =         "little"
    FLOAT_PACK_TYPE =   "d"
    FLOAT_PACK_SIZE =   8
 
    # so many sensationtypes, that first letter is not good idea any more  
    SensationType = enum(Drive='a', Stop='b', Who='c', Azimuth='d', Acceleration='e', Observation='f', HearDirection='g', Voice='h', Image='i',  Calibrate='j', Capability='k', Item='l', Unknown='m')
    # Direction of a sensation. Example in Voice: In: Speaking,  Out: Hearing
    Direction = enum(In='I', Out='O')
    # Direction of a sensation transferring, used with Axon. Up: going up like fron AlsaMicroPhone to MainRobot, Down: going down from MainRobot to leaf Robots like AlsaPlayback
    TransferDirection = enum(Up='U', Down='D')

    #Memory = enum(Sensory='S', Working='W', LongTerm='L' )
    Memory = enum(Sensory='S', LongTerm='L' )
    Kind = enum(WallE='w', Eva='e', Other='o')
    InstanceType = enum(Real='r', SubInstance='s', Virtual='v', Remote='e')
    Mode = enum(Normal='n', StudyOwnIdentity='t',Sleeping='l',Starting='s', Stopping='p', Interrupted='i')
# enum items as strings    
    IN="In"
    OUT="Out"
    MEMORY_SECTION="Memory"
    SENSORY="Sensory"
    #WORKING="Working"
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
    OTHER="Other"
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
      
    Directions={Direction.In: IN,
                Direction.Out: OUT}
    DirectionsOrdered=(
                Direction.In,
                Direction.Out)
    
    Memorys = {Memory.Sensory: SENSORY,
               #Memory.Working: WORKING,
               Memory.LongTerm: LONG_TERM}
    MemorysOrdered = (
               Memory.Sensory,
               #Memory.Working,
               Memory.LongTerm)
    
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
           Kind.Other: OTHER}
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
    
    sensationMemorys={                      # Sensation caches
        Memory.Sensory:  [],                # short time Sensation cache
        #Memory.Working:  [],                # middle time Sensation cache
        Memory.LongTerm: [] }               # long time Sensation cache

    sensationMemoryCacheTimes={             # Sensation cache times
        Memory.Sensory:  SENSORY_CACHE_TIME,
        #Memory.Working:  WORKING_CACHE_TIME, 
        Memory.LongTerm: LONG_TERM_CACHE_TIME }


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

    
    def getDirectionString(direction):
        ret = Sensation.Directions.get(direction)
        return ret
    def getDirectionStrings():
        ret=[]
        for direction in Sensation.DirectionsOrdered:
            ret.append(Sensation.Directions[direction])
        return ret
        #return Sensation.Directions.values()
    
    def getMemoryString(memory):
        ret = Sensation.Memorys.get(memory)
        return ret
    def getMemoryStrings():
        return Sensation.Memorys.values()
    
    def getSensationTypeString(sensationType):
        return Sensation.SensationTypes.get(sensationType)
    def getSensationTypeStrings():
        return Sensation.SensationTypes.values()

    
    def addToSensationMemory(sensation):
        # add new sensation
        memory = Sensation.sensationMemorys[sensation.getMemory()]
        cacheTime = Sensation.sensationMemoryCacheTimes[sensation.getMemory()]
        memory.append(sensation)
        
        # remove too old ones
        now = systemTime.time()
        # TODO When use association_time, then it is possible that
        # at the start there is much connected sensation, and after that
        # there are less connected, that keep in the memory too long time.
        # Maybe this is not a big problem. This simple implementation keeps
        # sensation creation efficient
        while len(memory) > 0 and now - memory[0].getLatestTime() > cacheTime:
            print('delete from sensation cache ' + sensation.toDebugStr())
            memory[0].delete()
            del memory[0]
                
         
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
        
        # Feeling, Feelings can be positive or negative, stronger or weaker
        Feeling = enum(Terrified=-5, Afraid=-3, Disappointed=-2, Worried=-1, Neutral=0, Normal=1, Good=2, Happy=3, InLove=5)
        
        def __init__(self,
                     sensation,                             # sensation to connect
                     time=None,                             # last used
                     score = 0.0,                           # score of association, used at least with item, float
                     feeling = Feeling.Neutral):            # feeling of association two sensations
                                                            # stronger feeling make us (and robots) to remember association
                                                            # longer than neutral associations
                                                            # our behaver (and) robots has to goal to get good feelings
                                                            # and avoid negative ones
                                                            # first usage of feeling is wit Communication-Robot, make it
                                                            # classify Voices with good feeling when it gets responses
                                                            # and feel CVoice use with bad feeling, if it does not
                                                            # get a rsponse
            self.time=time
            if self.time == None:
                self.time = systemTime.time()
            self.sensation = sensation
            self.score = score
            self.feeling = feeling
    
        def getTime(self):
            return self.time
    
        def setTime(self, time = None):
            if time == None:
                time = systemTime.time()
            self.time = time
     
        def getSensation(self):
            return self.sensation
    
        def setSensation(self, sensation):
             self.sensation = sensation
             
        def getScore(self):
            return self.score
    
        def setScore(self, score):
             self.score = score

        def getFeeling(self):
            return self.feeling
    
        def setFeeling(self, feeling):
             self.feeling = feeling


    '''
    default constructor for Sensation
    '''
       
    def __init__(self,
                 associations,                                             # don't allow default association, because wrong association will be linked, not copied, study this
                 sensation=None,
                 bytes=None,
                 number=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = SensationType.Unknown,
                 memory=Memory.Sensory,
                 direction=Direction.In,
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
                 name = ''):                                                # name of Item
                                                 
        from Config import Capabilities
        self.time=time
        if self.time == None:
            self.time = systemTime.time()

        self.number = number
        if self.number == None:
            self.number = self.nextNumber()
        self.associations=associations

        # associations are always both way
        if sensation is not None:   # copy constructor
            self.associations=sensation.associations
            self.receivedFrom=sensation.receivedFrom
            self.sensationType = sensation.sensationType
            self.memory = sensation.memory
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


        else:                
            self.sensationType = sensationType
            self.memory = memory
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
            
            # associations are always both way
            if associations == None:
                associations=[]
            self.addAssociations(associations)
           
            if receivedFrom == None:
                receivedFrom=[]
            self.receivedFrom=[]
            self.addReceivedFrom(receivedFrom)

        if bytes != None:
            try:
                l=len(bytes)
                i=0

                self.number = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE

                self.memory = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("memory " + str(memory))
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
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    #print("filePath_size " + str(filePath_size))
                    i += Sensation.NUMBER_SIZE
                    self.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    #print("data_size " + str(data_size))
                    i += Sensation.NUMBER_SIZE
                    self.data = bytes[i:i+data_size]
                    i += data_size
                elif self.sensationType is Sensation.SensationType.Image:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    #print("filePath_size " + str(filePath_size))
                    i += Sensation.NUMBER_SIZE
                    self.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    #print("data_size " + str(data_size))
                    i += Sensation.NUMBER_SIZE
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
                    capabilities_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("capabilities_size " + str(capabilities_size))
                    i += Sensation.NUMBER_SIZE
                    self.capabilities = Capabilities(bytes=bytes[i:i+capabilities_size])
                    i += capabilities_size
                elif self.sensationType is Sensation.SensationType.Item:
                    name_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("name_size " + str(name_size))
                    i += Sensation.NUMBER_SIZE
                    self.name =bytesToStr(bytes[i:i+name_size])
                    i += name_size
                    
                association_number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                #print("association_number " + str(association_number))
                i += Sensation.NUMBER_SIZE
                for j in range(association_number):
                    sensation_number=bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
               
                    time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                
                    score = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    feeling = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER)
                    i += Sensation.NUMBER_SIZE

                    sensation=Sensation.getSensationFromSensationMemory(number=sensation_number)
                    if sensation is not None:
                        self.addAssociation(Sensation.Association(sensation=sensation,time=time,score=score, feeling=feeling))
                
            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
               
        Sensation.addToSensationMemory(self)

    '''
    Constructor that takes care, that we have only one instance
    per Sensation per number
    
    This is needed if we want handle associations properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constructor
    '''
       
    def create(  associations,                                             # don't allow default associations
                 sensation=None,
                 bytes=None,
                 number=None,
                 time=None,
                 receivedFrom=[],
                 sensationType = SensationType.Unknown,
                 memory=Memory.Sensory,
                 direction=Direction.In,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 filePath='',
                 data=b'',
                 image=None,
                 calibrateSensationType = SensationType.Unknown,
                 capabilities = None,                                       # capabilitis of sensorys, direction what way sensation go
                 name=''):                                                  # name of Item
                                                 
        
        if sensation is not None:             # not an update, create new one
            print("Sensation.create Create new sensation instance of this sensation")
            return Sensation(associations=associations, sensation=sensation)

        if bytes != None:               # if bytes, we get number there
            number = bytesToFloat(bytes[0:Sensation.FLOAT_PACK_SIZE])
 
        sensation = None                # try to find existing sensation by number           
        if number != None:
            sensation = Sensation.getSensationFromSensationMemory(number)

            
        if sensation == None:             # not an update, create new one
            print("Create new sensation of parameters")
            return Sensation(
                 bytes=bytes,
                 number=number,
                 time=time,
                 associations=associations,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memory=memory,
                 direction=direction,
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
                 name=name)
            
        print("Update existing sensation")
        # update existing one    
        sensation.time=time
        if sensation.time == None:
            sensation.time = systemTime.time()

        # associations are always both way
        if associations == None:
            associations=[]
        sensation.associations=[]
        sensation.addAssociations(associations)
                
        if receivedFrom == None:
            receivedFrom=[]
        sensation.receivedFrom=[]
        sensation.addReceivedFrom(receivedFrom)
                
        sensation.sensationType = sensationType
        sensation.memory = memory
        sensation.direction = direction
        sensation.leftPower = leftPower
        sensation.rightPower = rightPower
        sensation.hearDirection = hearDirection
        sensation.azimuth = azimuth
        sensation.accelerationX = accelerationX
        sensation.accelerationY = accelerationY
        sensation.accelerationZ = accelerationZ
        sensation.observationDirection = observationDirection
        sensation.observationDistance = observationDistance
        sensation.filePath = filePath
        sensation.data = data
        sensation.image = image
        sensation.calibrateSensationType = calibrateSensationType
        sensation.capabilities = capabilities
        sensation.name=name

        if bytes != None:
            try:
                l=len(bytes)
                i=0
 
                sensation.number = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                   
                sensation.time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                sensation.memory = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("memory " + str(memory))
                i += Sensation.ENUM_SIZE
                    
                sensation.sensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("sensationType " + str(sensationType))
                i += Sensation.ENUM_SIZE
                    
                sensation.direction = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                #print("direction " + str(direction))
                i += Sensation.ENUM_SIZE
                    
                if sensation.sensationType is Sensation.SensationType.Drive:
                    sensation.leftPower = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    sensation.rightPower = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif sensation.sensationType is Sensation.SensationType.HearDirection:
                    sensation.hearDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif sensation.sensationType is Sensation.SensationType.Azimuth:
                    sensation.azimuth = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif sensation.sensationType is Sensation.SensationType.Acceleration:
                    sensation.accelerationX = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    sensation.accelerationY = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    sensation.accelerationZ = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif sensation.sensationType is Sensation.SensationType.Observation:
                    sensation.observationDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    sensation.observationDistance = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                elif sensation.sensationType is Sensation.SensationType.Voice:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("filePath_size " + str(filePath_size))
                    i += Sensation.NUMBER_SIZE
                    sensation.filePath = bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("data_size " + str(data_size))
                    i += Sensation.NUMBER_SIZE
                    sensation.data = bytes[i:i+data_size]
                    i += data_size
                elif sensation.sensationType is Sensation.SensationType.Image:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("filePath_size " + str(filePath_size))
                    i += Sensation.NUMBER_SIZE
                    sensation.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("data_size " + str(data_size))
                    i += Sensation.NUMBER_SIZE
                    if data_size > 0:
                        sensation.image = PIL_Image.open(io.BytesIO(bytes[i:i+data_size]))
                    else:
                        sensation.image = None
                    i += data_size
                elif sensation.sensationType is Sensation.SensationType.Calibrate:
                    sensation.calibrateSensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    i += Sensation.ENUM_SIZE
                    if sensation.calibrateSensationType == Sensation.SensationType.HearDirection:
                        sensation.hearDirection = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                elif sensation.sensationType is Sensation.SensationType.Capability:
                    capabilities_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("capabilities_size " + str(capabilities_size))
                    i += Sensation.NUMBER_SIZE
                    sensation.capabilities = Capabilities(bytes=bytes[i:i+capabilities_size])
                    i += capabilities_size
                elif sensation.sensationType is Sensation.SensationType.Item:
                    name_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("name_size " + str(name_size))
                    i += Sensation.NUMBER_SIZE
                    sensation.name =bytesToStr(bytes[i:i+name_size])
                    i += name_size
                        
                association_number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                print("association_number " + str(association_number))
                i += Sensation.NUMBER_SIZE
                for j in range(association_number):
                    sensation_number=bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
               
                    time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                
                    score = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    feeling = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER)
                    i += Sensation.NUMBER_SIZE

                    connected_sensation=Sensation.getSensationFromSensationMemory(number=sensation_number)
                    if connected_sensation is not None:
                        sensation.addAssociation(Sensation.Association(sensation=connected_sensation, time=time, score=score, feeling=feeling))
                
                 #  at the end receivedFros (list of words)
                receivedFrom_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                print("receivedFrom_size " + str(receivedFrom_size))
                i += Sensation.NUMBER_SIZE
                sensation.receivedFrom = bytesToList(bytes[i:i+receivedFrom_size])
                i += receivedFrom_size
    
            except (ValueError):
                sensation.sensationType = Sensation.SensationType.Unknown
                       
        return sensation
    
    def __cmp__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
            print('__cmp__ self.number == other.number ' +  str(self.number) + ' == ' + str(other.number) + ' ' + str(self.number == other.number))
            return self.number == other.number
        else:
            print('__cmp__ other is not Sensation')
            return False
 
    def nextNumber(self):
        return self.getTime()+random.uniform(Sensation.LOWPOINT_NUMBERVARIANCE, Sensation.HIGHPOINT_NUMBERVARIANCE)
        LOWPOINT_NUMBERVARIANCE=-100.0
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
#            print('__eq__ self.number == other.number ' +  str(self.number) + ' == ' + str(other.number) + ' ' + str(self.number == other.number))
            return self.number == other.number
        else:
#            print('__eq__ other is not Sensation')
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

                 
    def __str__(self):
        s=str(self.number) + ' ' + str(self.time) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
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
        elif self.sensationType == Sensation.SensationType.Image:
            s += ' ' + self.filePath# + ' ' +  bytesToStr(self.data)
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                s += ' ' + self.calibrateSensationType + ' ' + str(self.hearDirection)
            else:
                s = str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' +  Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            s +=  ' ' + self.getCapabilities().toString()
        elif self.sensationType == Sensation.SensationType.Item:
            s +=  ' ' + self.name
           
#         elif self.sensationType == Sensation.SensationType.Stop:
#             pass
#         elif self.sensationType == Sensation.SensationType.Who:
#             pass
#         else:
#             pass

#        # at the end associations (numbers) TODO
        s += ' '
        i=0
        for association in self.associations:
            if i == 0:
                 s += str(association.getSensation().getNumber())
            else:
                s += LIST_SEPARATOR + str(association.getSensation().getNumber())
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
#             s=str(self.number) + ' ' + str(self.time) + ' ' + str(self.association_time) + ' ' + Sensation.getMemoryString(self.memory) + ' ' + Sensation.getDirectionString(self.direction) + ' ' + Sensation.getSensationTypeString(self.sensationType)
#         else:
#             s=self.__str__()
        s = systemTime.ctime(self.time) + ' ' + str(self.number) + ' ' + Sensation.getMemoryString(self.memory) + ' ' + Sensation.getDirectionString(self.direction) + ' ' + Sensation.getSensationTypeString(self.sensationType)
        if self.sensationType == Sensation.SensationType.Item:
            s = s + ' ' + self.name
        return s

    def bytes(self):
#        b = self.number.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
        b = floatToBytes(self.number)
        b += floatToBytes(self.time)
        b += StrToBytes(self.memory)
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
            b +=  filePath_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b += bfilePath
            
            data_size=len(self.data)
            b +=  data_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b +=  self.data
        elif self.sensationType == Sensation.SensationType.Image:
            filePath_size=len(self.filePath)
            b +=  filePath_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b +=  StrToBytes(self.filePath)
            stream = io.BytesIO()
            if self.image is None:
                data = b''
            else:
                self.image.save(fp=stream, format=Sensation.IMAGE_FORMAT)
                data=stream.getvalue()
            data_size=len(data)
            b +=  data_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b +=  data
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                b += StrToBytes(self.calibrateSensationType) + floatToBytes(self.hearDirection)
#             else:
#                 return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            bytes = self.getCapabilities().toBytes()
            capabilities_size=len(bytes)
            print("capabilities_size " + str(capabilities_size))
            b += capabilities_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b += bytes
        elif self.sensationType == Sensation.SensationType.Item:
            name_size=len(self.name)
            b +=  name_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b +=  StrToBytes(self.name)
            
        #  at the end associations (numbers)
        association_number=len(self.associations)
        b +=  association_number.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        for j in range(association_number):
            b +=  floatToBytes(self.associations[j].getSensation().getNumber())
            b +=  floatToBytes(self.associations[j].getTime())
            b +=  floatToBytes(self.associations[j].getScore())
            b +=  self.associations[j].getFeeling().to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
       #  at the end receivedFrom (list of words)
        blist = listToBytes(self.receivedFrom)
        blist_size=len(blist)
        b +=  blist_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        b += blist
        

# all other done
#         elif self.sensationType == Sensation.SensationType.Stop:
#             return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
#         elif self.sensationType == Sensation.SensationType.Who:
#             return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
#         else:
#             return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
        
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


    def setNumber(self, number):
        self.number = number
    def getNumber(self):
        return self.number
    
    def setAssociations(self, associations):
        self.associations = associations
        time = systemTime.time()
        for association in self.associations:
            association.time = time
        
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
    '''
    def addAssociation(self, association):
        time = systemTime.time()
        if association.getSensation() != self and \
           not self.isConnected(association):
            #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
            self.associations.append(association)
            association.time = time
            ## TODO howto do reverse association
            #association.getSensation().addAssociation(Sensation.Association(sensation=self))
    '''
    Is this Sensation in this Association already connected
    '''
    def isConnected(self, association):
        #print('isConnected ' + self.toDebugStr() + ' has ' + str(len(self.associations)) + ' associations')
        is_connected = False
        for con in self.associations:
            if con.getSensation() == association.getSensation():
                is_connected = True
                #print('isConnected ' + self.toDebugStr() + ' found association to ' + con.getSensation().toDebugStr() + ' == ' + association.getSensation().toDebugStr() + ' ' + str(is_connected))
                break
        #print('isConnected ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr() + ' ' + str(is_connected))
        return is_connected
        
    '''
    Add many associations
    '''
    def addAssociations(self, associations):
        for association in associations:
            self.addAssociation(association)

    def getAssociations(self):
        time = systemTime.time()
        for association in self.associations:
            association.time = time
        return self.associations
    
    '''
    remove associations from this sensation connected to sensation given as parameter
    '''
    def removeAssociation(self, sensation):
        i=0
        for association in self.associations:
            if association.getSensation() == sensation:
                del self.associations[i]
            else:
                i=i+1

    def getAssociationNumbers(self):
        associationNumbers=[]
        time = systemTime.time()
        for association in self.associations:
            associationNumbers.append(association.getSesation().getNumber())
            association.time = time
        return associationNumbers
 
    def getScore(self):
        score = 0.0
        time = systemTime.time()
        # one level associations
        for association in self.associations:
            if association.getScore() > score:
                score = association.getScore()
                association.time = time
        return score
    
    '''
    Add many associations by association numbers
    associations and associations to then are found from association cache
    '''
    def addAssociationNumbers(self, associationNumbers):
        for associationNumber in associationNumbers:
            associations = Sensation.getSensationsFromSensationMemory(associationNumber)
            self.addAssociations(associations)

    '''
    Has sensation association to other Sensation
    which SensationType is 'associationSensationType'
    '''
    def hasAssociationSensationType(self, associationSensationType):
        has=False
        for association in self.associations:
            if association.getSensation().getSensationType() == associationSensationType:
                has=True
                break       
        return has
     
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
       
    def setMemory(self, memory):
        self.memory = memory
    def getMemory(self):
        return self.memory
       
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

    '''
    save sensation data permanently
    '''  
    def save(self):
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)
            
        if self.getSensationType() == Sensation.SensationType.Image:       
            fileName = Sensation.DATADIR + '/' + '{}'.format(self.getNumber()) + \
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
            fileName = Sensation.DATADIR + '/' + '{}'.format(self.getNumber()) + \
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
    def getSensationFromSensationMemory(number):
        for key, sensationMemory in Sensation.sensationMemorys.items():
            if len(sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getNumber() == number:
                        return sensation
        return None

    def getSensationsFromSensationMemory(associationNumber):
        sensations=[]
        for key, sensationMemory in Sensation.sensationMemorys.items():
            if len(sensationMemory) > 0:
                for sensation in sensationMemory:
                    if sensation.getNumber() == associationNumber or \
                       associationNumber in sensation.getAssociationNumbers():
                        if not sensation in sensations:
                            sensations.append(sensation)
        return sensations
                     
    '''
    Get sensations from sensation memory that are set in capabilities
    
    Time window can be set seperatly min, max or both,
    from time min to time max, to get sensations that are happened at same moment.   
    '''  
    def getSensations(capabilities, timemin=None, timemax=None):
        sensations=[]
        for key, sensationMemory in Sensation.sensationMemorys.items():
            for sensation in sensationMemory:
                if capabilities.hasCapability(direction=sensation.getDirection(),
                                              memory=sensation.getMemory(),
                                              sensationType=sensation.getSensationType()) and\
                   (timemin is None or sensation.getTime() > timemin) and\
                   (timemax is None or sensation.getTime() < timemax):
                    sensations.append(sensation)
        return sensations
    
    '''
    Get best specified sensation from sensation memory
    
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
                          name = None,
                          notName = None,
                          associationSensationType = None):
        bestSensation = None
        for key, sensationMemory in Sensation.sensationMemorys.items():
            for sensation in sensationMemory:
                if sensation.getSensationType() == sensationType and\
                   sensation.hasAssociationSensationType(associationSensationType=associationSensationType) and\
                   (timemin is None or sensation.getTime() > timemin) and\
                   (timemax is None or sensation.getTime() < timemax):
                    if sensationType != Sensation.SensationType.Item or\
                       notName is None and sensation.getName() == name or\
                       name is None and sensation.getName() != notName or\
                       name is None and notName is None:
                        if bestSensation is None or\
                           sensation.getScore() > bestSensation.getScore():
                            bestSensation = sensation
        return bestSensation
    
    '''
    Get best connected sensation from this specified Sensation
   
    sensationType:  SensationType
    name:           optional, if SensationTypeis Item, name must be 'name'
    '''
    def getBestConnectedSensation( self,
                                   sensationType,
                                   name = None):
        bestSensation = None
        for association in self.getAssociations():
            sensation= association.getSensation()
            if sensation.getSensationType() == sensationType:
                if sensationType != Sensation.SensationType.Item or\
                   sensation.getName() == name:
                    if bestSensation is None or\
                       sensation.getScore() > bestSensation.getScore():
                        bestSensation = sensation
        return bestSensation
    
    


    '''
    save all LongTerm Memory sensation instances and data permanently
    so they can be loaded, when running app again
    '''  
    def saveLongTermMemory():
        # save sensation data to files
        for sensation in Sensation.sensationMemorys[Sensation.Memory.LongTerm]:
            sensation.save()
        # save sensation instances
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)
            
        try:
            with open(Sensation.PATH_TO_PICLE_FILE, "wb") as f:
                try:
                    pickler = pickle.Pickler(f, -1)
                    pickler.dump(Sensation.sensationMemorys[Sensation.Memory.LongTerm])
                    print ('saveLongTermMemory dumped ' + str(len(Sensation.sensationMemorys[Sensation.Memory.LongTerm])))
                except IOError as e:
                    print('pickler.dump(Sensation.sensationMemorys[Memory.LongTerm]) error ' + str(e))
                finally:
                    f.close()
        except Exception as e:
                print("open(fileName, wb) as f error " + str(e))

    '''
    load LongTerm Memory sensation instances
    '''  
    def loadLongTermMemory():
        # load sensation data from files
        if os.path.exists(Sensation.DATADIR):
            try:
                with open(Sensation.PATH_TO_PICLE_FILE, "rb") as f:
                    try:
                        Sensation.sensationMemorys[Sensation.Memory.LongTerm] = \
                            pickle.load(f)
                        print ('loadLongTermMemory loaded ' + str(len(Sensation.sensationMemorys[Sensation.Memory.LongTerm])))
                        i=0
                        while i < len(Sensation.sensationMemorys[Sensation.Memory.LongTerm]):
                            if Sensation.sensationMemorys[Sensation.Memory.LongTerm][i].VERSION != Sensation.VERSION: # if dumped code version and current code version is not same
                                print('del Sensation.sensationMemorys[Sensation.Memory.LongTerm]['+str(i)+'] with Sensation version ' + str(Sensation.sensationMemorys[Sensation.Memory.LongTerm][i].VERSION))
                                del Sensation.sensationMemorys[Sensation.Memory.LongTerm][i]
                            else:
                                i=i+1
                        print ('LongTermMemory after load and verification ' + str(len(Sensation.sensationMemorys[Sensation.Memory.LongTerm])))
                    except IOError as e:
                        print("pickle.load(f) error " + str(e))
                    finally:
                        f.close()
            except Exception as e:
                    print('with open(' + 'Sensation.PATH_TO_PICLE_FILE, "rb")  as f error ' + str(e))
 
    '''
    Clean data directory fron data files, that are not connected to any sensation.
    '''  
    def CleanDataDirectory():
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
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
# TODO fromString(Sensation.toString) -tests are deprecated
# Sensation data in transferred by menory or by byte with tcp
# and str form is for debugging purposes
# Most importand sensations are now voice and image and string form does not handle
# parameters any more. Can be fixed if im plementing parameter type in string
# but it mo more vice to concentrate to byte tranfer for str test will be removed soon.

    from Config import Config, Capabilities
    config = Config()
    capabilities = Capabilities(config=config)
    
    s_Drive=Sensation(associations=[], sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print("str s  " + str(s_Drive))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getNumber())
    b=s_Drive.bytes()
    # TODO should s2 be here really association to s, same instance? maybe
    s2=Sensation(associations=[], bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getNumber())
    print("str s2 " + str(s2))
    print(str(s_Drive == s2))
    
    #test with create
    print("test with create")
    s_Drive_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("Sensation.create: str s  " + str(s_Drive_create)))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getNumber())
    b=s_Drive_create.bytes()
    # TODO should s2 be here really association to s, same instance? maybe
    s2=Sensation.create(associations=[], bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getNumber())
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create:" + str(s_Drive_create == s2))
    print()

    
    s_Stop=Sensation(associations=[], sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print("str s  " + str(s_Stop))
    b=s_Stop.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Stop == s2))

    #test with create
    print("test with create")
    s_Stop_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Stop_create)))
    b=s_Stop_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Stop_create == s2))
    print()
    
    s_Who=Sensation(associations=[], sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print("str s  " + str(s_Who))
    b=s_Who.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Who == s2))
    
    #test with create
    print("test with create")
    s_Who_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Who_create)))
    b=s_Who_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Who_create == s2))
    print()

    
    s_HearDirection=Sensation(associations=[Sensation.Association(sensation=s_Drive)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s_HearDirection)))
    b=s_HearDirection.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_HearDirection == s2))

    #test with create
    print("test with create")
    s_HearDirection_create=Sensation.create(associations=[Sensation.Association(sensation=s_Drive_create)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("Sensation.create: str s  " + str(s_HearDirection_create)))
    b=s_HearDirection_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_HearDirection_create == s2))
    print()

    s_Azimuth=Sensation(associations=[Sensation.Association(sensation=s_HearDirection)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("str s  " + str(s_Azimuth)))
    b=s_Azimuth.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Azimuth == s2))

    #test with create
    print("test with create")
    s_Azimuth_create=Sensation.create(associations=[Sensation.Association(sensation=s_Who_create)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("Sensation.create: str s  " + str(s_Azimuth_create)))
    b=s_Azimuth_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Azimuth_create == s2))
    print()

    s_Acceleration=Sensation(associations=[Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("str s  " + str(s_Acceleration)))
    b=s_Acceleration.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Acceleration == s2))

    #test with create
    print("test with create")
    s_Acceleration_create=Sensation.create(associations=[Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create)], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("Sensation.create: str s  " + str(s_Acceleration_create)))
    b=s_Acceleration_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " +str(s_Acceleration_create == s2))
    print()

    
    s_Observation=Sensation(associations=[Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("str s  " + str(s_Observation)))
    b=s_Observation.bytes()
    s2=Sensation(associations=[], bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Observation == s2))

    #test with create
    print("test with create")
    s_Observation_create=Sensation.create(associations=[Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)],  receivedFrom=['localhost', 'raspberry', 'virtualWalle',  'remoteWalle'], sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("Sensation.create: str s  " + str(s_Observation_create)))
    b=s_Observation_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Observation_create == s2))
    print()
    
    # voice
    s_VoiceFilePath=Sensation(associations=[Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print("str s  " + str(s_VoiceFilePath))
    b=s_VoiceFilePath.bytes()
    s2=Sensation(associations=[], bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_VoiceFilePath == s2))

    #test with create
    print("test with create")
    s_VoiceFilePath_create=Sensation.create(associations=[Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print(("Sensation.create: str s  " + str(s_VoiceFilePath_create)))
    b=s_VoiceFilePath_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_VoiceFilePath_create == s2))
    print()

    s_VoiceData=Sensation(associations=[Sensation.Association(sensation=s_VoiceFilePath),Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, data=b'\x01\x02\x03\x04\x05')
    print(("str s  " + str(s_VoiceData)))
    b=s_VoiceData.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_VoiceData == s2))

    #test with create
    print("test with create")
    s_VoiceData_create=Sensation.create(associations=[Sensation.Association(sensation=s_VoiceFilePath_create),Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In,  data=b'\x01\x02\x03\x04\x05')
    print(("Sensation.create: str s  " + str(s_VoiceData_create)))
    b=s_VoiceData_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " +str(s_VoiceData_create == s2))
    print()
    
    # image    
    s_ImageFilePath=Sensation(associations=[Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print(("str s  " + str(s_ImageFilePath)))
    b=s_ImageFilePath.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_ImageFilePath == s2))

    #test with create
    print("test with create")
    s_ImageFilePath_create=Sensation.create(associations=[Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print(("Sensation.create: str s  " + str(s_ImageFilePath_create)))
    b=s_ImageFilePath_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_ImageFilePath_create == s2))
    print()

    s_ImageData=Sensation(associations=[Sensation.Association(sensation=s_ImageFilePath),Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
    print("str s  " + str(s_ImageData))
    b=s_ImageData.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_ImageData == s2))

    #test with create
    print("test with create")
    s_ImageData_create=Sensation.create(associations=[Sensation.Association(sensation=s_ImageFilePath_create),Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
    print("Sensation.create: str s  " + str(s_ImageData_create))
    b=s_ImageData_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " +str(s_ImageData_create == s2))
    print()

    s_Calibrate=Sensation(associations=[Sensation.Association(sensation=s_ImageData),Sensation.Association(sensation=s_ImageFilePath),Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print("str s  " + str(s_Calibrate))
    b=s_Calibrate.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Calibrate == s2))

    #test with create
    print("test with create")
    s_Calibrate_create=Sensation.create(associations=[Sensation.Association(sensation=s_ImageData_create),Sensation.Association(sensation=s_ImageFilePath_create),Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print("Sensation.create: str s  " + str(s_Calibrate_create))
    b=s_Calibrate_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Calibrate_create == s2))
    print()

#    s_Capability=Sensation(associations=[s_Calibrate,s_VoiceData,s_VoiceFilePath,s_ImageData,s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    s_Capability=Sensation(associations=[Sensation.Association(sensation=s_Calibrate),Sensation.Association(sensation=s_VoiceData),Sensation.Association(sensation=s_VoiceFilePath),Sensation.Association(sensation=s_ImageData),Sensation.Association(sensation=s_ImageFilePath),Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = capabilities)
    print(("str s  " + str(s_Capability)))
    b=s_Capability.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Capability == s2))
    
     #test with create
    print("test with create")
    s_Capability_create=Sensation.create(associations=[Sensation.Association(sensation=s_Calibrate_create),Sensation.Association(sensation=s_VoiceData_create),Sensation.Association(sensation=s_VoiceFilePath_create),Sensation.Association(sensation=s_ImageData_create),Sensation.Association(sensation=s_ImageFilePath_create),Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = capabilities)
    print(("Sensation.create: str s  " + str(s_Capability_create)))
    b=s_Capability_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Capability_create == s2))
    
    # item
    
    s_Item=Sensation(associations=[Sensation.Association(sensation=s_Calibrate),Sensation.Association(sensation=s_VoiceData),Sensation.Association(sensation=s_VoiceFilePath),Sensation.Association(sensation=s_ImageData),Sensation.Association(sensation=s_ImageFilePath),Sensation.Association(sensation=s_Observation),Sensation.Association(sensation=s_HearDirection),Sensation.Association(sensation=s_Azimuth),Sensation.Association(sensation=s_Acceleration)], sensationType = Sensation.SensationType.Item, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, name='person')
    print(("str s  " + str(s_Item)))
    b=s_Item.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Item == s2))
    
     #test with create
    print("test with create")
    s_Item_create=Sensation.create(associations=[Sensation.Association(sensation=s_Calibrate_create),Sensation.Association(sensation=s_VoiceData_create),Sensation.Association(sensation=s_VoiceFilePath_create),Sensation.Association(sensation=s_ImageData_create),Sensation.Association(sensation=s_ImageFilePath_create),Sensation.Association(sensation=s_Observation_create),Sensation.Association(sensation=s_HearDirection_create),Sensation.Association(sensation=s_Azimuth_create),Sensation.Association(sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Item, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, name='person')
    print(("Sensation.create: str s  " + str(s_Item_create)))
    b=s_Item_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Item_create == s2))
    
   