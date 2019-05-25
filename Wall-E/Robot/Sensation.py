'''
Created on Feb 25, 2013
Edited on 25.05.2019

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

import sys
import time as systemTime
from enum import Enum
import struct
import random
from PIL import Image as PIL_Image
import io

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


class Sensation(object):
    sensationMemory=[]      # short time Sensation cache
                            # The idea is keep Sensation in runtime memory if
                            # there is a reference for them for instance 10 mins
                            #
                            # After that we can produce higher level Sensations
                            # with memory attribute in higher level,
                            # Working or Memory, that reference to basic
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
 
    #number=0                # sensation number for referencing
    FORMAT='jpeg'
    MODE='RGB'
    LOWPOINT_NUMBERVARIANCE=-100.0
    HIGHPOINT_NUMBERVARIANCE=100.0
    
    CACHE_TIME = 300.0;       # cache sensation 300 seconds = 5 mins (may be changed)
    LENGTH_SIZE=2   # Sensation as string can only be 99 character long
    LENGTH_FORMAT = "{0:2d}"
    SEPARATOR='|'  # Separator between messages
    SEPARATOR_SIZE=1  # Separator length
    
    ENUM_SIZE=1
    NUMBER_SIZE=4
    BYTEORDER="little"
    FLOAT_PACK_TYPE="d"
    FLOAT_PACK_SIZE=8
 
    # so many sensationtypes, that first letter is not good idea any more  
    SensationType = enum(Drive='a', Stop='b', Who='c', Azimuth='d', Acceleration='e', Observation='f', HearDirection='g', Voice='h', Image='i',  Calibrate='j', Capability='k', Unknown='l')
    Direction = enum(In='I', Out='O')
    Memory = enum(Sensory='S', Working='W', LongTerm='L' )
    Kind = enum(WallE='w', Eva='e', Other='o')
    InstanceType = enum(Real='r', SubInstance='s', Virtual='v', Remote='e')
    Mode = enum(Normal='n', StudyOwnIdentity='i',Sleeping='l',Starting='s', Stopping='p')
# enum items as strings    
    IN="In"
    OUT="Out"
    MEMORY_SECTION="Memory"
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
      
    Directions={Direction.In: IN,
                Direction.Out: OUT}
    DirectionsOrdered=(
                Direction.In,
                Direction.Out)
    
    Memorys = {Memory.Sensory: SENSORY,
               Memory.Working: WORKING,
               Memory.LongTerm: LONG_TERM}
    MemorysOrdered = (
               Memory.Sensory,
               Memory.Working,
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
           Mode.Stopping: STOPPING }
    
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
        Sensation.sensationMemory.append(sensation)
        
        # remove too old ones
        now = systemTime.time()
        # TODO When use reference_time, then it is possible that
        # at the start there is much referenced sensation, and after that
        # there are less referenced, that keep in the memory too long time.
        # Maybe this is not a big problem. This simple implementation keeps
        # sensation creation efficient
        while len(Sensation.sensationMemory) > 0 and now - Sensation.sensationMemory[0].getReferenceTime() > Sensation.CACHE_TIME:
            print('delete from sensation cache ' + str(sensation.getNumber()))
            del Sensation.sensationMemory[0]
                
    def getSensationFromSensationMemory(number):
        if len(Sensation.sensationMemory) > 0:
            for sensation in Sensation.sensationMemory:
                if sensation.getNumber() == number:
                    return sensation
        return None

    def getSensationsFromSensationMemory(referenceNumber):
        sensations=[]
        if len(Sensation.sensationMemory) > 0:
            for sensation in Sensation.sensationMemory:
                if sensation.getNumber() == referenceNumber or \
                   referenceNumber in sensation.getReferenceNumbers():
                    if not sensation in sensations:
                        sensations.append(sensation)
        return sensations
               
         
#     def nextNumber():
#        Sensation.number=Sensation.number+1
#        return Sensation.number


    
#    list(Memory)
#     class Memory(Enum):
#         Sensory='S',
#         Working='W',
#         LongTerm='L'

    '''
    default constructor
    '''
       
    def __init__(self,
                 sensation=None,
                 bytes=None,
                 number=None,
                 time=None,
                 reference_time=None,
                 references=[],
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
                 capabilities = None):                         # capabilitis of sensorys, direction what way sensation go
        from Config import Capabilities
        self.time=time
        self.reference_time = reference_time
        if self.time == None:
            self.time = systemTime.time()
        if self.reference_time == None:
            self.reference_time = self.time

        self.number = number
        if self.number == None:
            self.number = self.nextNumber()
            
#         if self.references != None:
#             self.referenceNumbers = references.getNumber()
#         else:
#             self.referenceNumbers=referenceNumbers
#             if self.referenceNumbers != None:
#                 self.references = Sensation.getSensationFromSensationMemory(self.referenceNumbers)

        # references are always both way
        if sensation is not None:   # copy contructor
            self.references=sensation.references
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
        else:
            # references are always both way
            if references == None:
                references=[]
            self.references=[]
            self.addReferences(references)
           
            if receivedFrom == None:
                receivedFrom=[]
            self.receivedFrom=[]
            self.addReceivedFrom(receivedFrom)

                
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

        if bytes != None:
            try:
                l=len(bytes)
                i=0

                self.number = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                self.reference_time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
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
                    print("filePath_size " + str(filePath_size))
                    i += Sensation.NUMBER_SIZE
                    self.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("data_size " + str(data_size))
                    i += Sensation.NUMBER_SIZE
                    self.data = bytes[i:i+data_size]
                    i += data_size
                elif self.sensationType is Sensation.SensationType.Image:
                    filePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("filePath_size " + str(filePath_size))
                    i += Sensation.NUMBER_SIZE
                    self.filePath =bytesToStr(bytes[i:i+filePath_size])
                    i += filePath_size
                    data_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("data_size " + str(data_size))
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
                    
                reference_number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                print("reference_number " + str(reference_number))
                i += Sensation.NUMBER_SIZE
                referenceNumbers=[]
                for j in range(reference_number):
                    referenceNumbers.append(bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE]))
                    i += Sensation.FLOAT_PACK_SIZE
                self.addReferenceNumbers(referenceNumbers)

 

            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
               
        Sensation.addToSensationMemory(self)

    '''
    Constructor that take care, that we have only one instance
    per Sensation per number
    
    This is needed if we want handle references properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constructor
    '''
       
    def create(  sensation=None,
                 bytes=None,
                 number=None,
                 time=None,
                 reference_time=None,
                 references=[],
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
                 capabilities = None):                                        # capabilitis of sensorys, direction what way sensation go
        
        if sensation is not None:             # not an update, create new one
            print("Create new sensation instance this one ")
            return Sensation(sensation=sensation)

        if bytes != None:               # if bytes, we get number there
            number = bytesToFloat(bytes[0:Sensation.FLOAT_PACK_SIZE])
 
        sensation = None                # try to find existing sensation by number           
        if number != None:
            sensation = Sensation.getSensationFromSensationMemory(number)

            
        if sensation == None:             # not an update, create new one
            print("Create new sensation")
            return Sensation(
                 bytes=bytes,
                 number=number,
                 time=time,
                 reference_time=reference_time,
                 references=references,
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
                 capabilities = capabilities)
            
        print("Update existing sensation")
        # update existing one    
        sensation.time=time
        if sensation.time == None:
            sensation.time = systemTime.time()
        sensation.reference_time = systemTime.time()

        # references are always both way
        if references == None:
            references=[]
        sensation.references=[]
        sensation.addReferences(references)
                
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
          
        if bytes != None:
            try:
                l=len(bytes)
                i=0
 
                sensation.number = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                   
                sensation.time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                i += Sensation.FLOAT_PACK_SIZE
                
                sensation.reference_time = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
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
                        
                reference_number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                print("reference_number " + str(reference_number))
                i += Sensation.NUMBER_SIZE
                referenceNumbers=[]
                for j in range(reference_number):
                    referenceNumbers.append(bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE]))
                    i += Sensation.FLOAT_PACK_SIZE
                sensation.addReferenceNumbers(referenceNumbers)
                
                 #  at the end receivedFros (list of words)
                receivedFrom_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                print("receivedFrom_size " + str(receivedFrom_size))
                i += Sensation.NUMBER_SIZE
                sensation.receivedFrom = bytesToList(bytes[i:i+receivedFrom_size])
                i += receivedFrom_size
    
            except (ValueError):
                sensation.sensationType = Sensation.SensationType.Unknown
                       
        return sensation

    def nextNumber(self):
        return self.getTime()+random.uniform(Sensation.LOWPOINT_NUMBERVARIANCE, Sensation.HIGHPOINT_NUMBERVARIANCE)
        LOWPOINT_NUMBERVARIANCE=-100.0
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
            return self.number == other.number
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

                 
    def __str__(self):
        s=str(self.number) + ' ' + str(self.time) + ' ' + str(self.reference_time) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
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
            
#         elif self.sensationType == Sensation.SensationType.Stop:
#             pass
#         elif self.sensationType == Sensation.SensationType.Who:
#             pass
#         else:
#             pass

#        # at the end references (numbers) TODO
        s += ' '
        i=0
        for reference in self.references:
            if i == 0:
                 s += str(reference.getNumber())
            else:
                s += LIST_SEPARATOR + str(reference.getNumber())
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
        if self.sensationType == Sensation.SensationType.Voice or self.sensationType == Sensation.SensationType.Image :
            s=str(self.number) + ' ' + str(self.time) + ' ' + str(self.reference_time) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
        else:
            s=self.__str__()
        return s

    def bytes(self):
#        b = self.number.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
        b = floatToBytes(self.number)
        b += floatToBytes(self.time)
        b += floatToBytes(self.reference_time)
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
        # TODO send real image
        elif self.sensationType == Sensation.SensationType.Image:
            filePath_size=len(self.filePath)
            b +=  filePath_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b +=  StrToBytes(self.filePath)
            stream = io.BytesIO()
            if self.image is None:
                data = b''
            else:
                self.image.save(fp=stream, format=Sensation.FORMAT)
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
            
        #  at the end references (numbers)
        reference_number=len(self.references)
        b +=  reference_number.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        for j in range(reference_number):
            b +=  floatToBytes(self.references[j].getNumber())
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

    def getReferenceTime(self):
        return self.reference_time
    
    def setReferenceTime(self, reference_time = None):
        if reference_time == None:
            reference_time = systemTime.time()
        self.reference_time = reference_time
        for reference in self.references:
#            reference.setReferenceTime(reference_time)
#            TODO comes infinite loop
#            Below works, if we have refenece as a star
            reference.reference_time = reference_time


    def setNumber(self, number):
        self.number = number
    def getNumber(self):
        return self.number
    
    def setReferences(self, references):
        self.references = references
        self.setReferenceTime()
        
    '''
    Add single reference
    References are always two sided, but not referencing to self
    '''
    def addReference(self, reference):
        if reference is not self and \
           reference not in self.references:
            self.references.append(reference)
            reference.addReference(self)
        self.setReferenceTime()
        
    '''
    Add many referencew
    '''
    def addReferences(self, references):
        for reference in references:
            self.addReference(reference)

    def getReferences(self):
        self.setReferenceTime()
        return self.references

    def getReferenceNumbers(self):
        self.setReferenceTime()
        referenceNumbers=[]
        for reference in self.references:
            referenceNumbers.append(reference.getNumber())
            reference.reference_time = self.reference_time
        return referenceNumbers
 
    '''
    Add many references by reference numbers
    refernces and references to then are found from reference cache
    '''
    def addReferenceNumbers(self, referenceNumbers):
        for referenceNumber in referenceNumbers:
            references = Sensation.getSensationsFromSensationMemory(referenceNumber)
            self.addReferences(references)
        self.setReferenceTime()
  
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
    
    s_Drive=Sensation(sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print("str s  " + str(s_Drive))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getNumber())
    b=s_Drive.bytes()
    # TODO should s2 be here really reference to s, same instance? maybe
    s2=Sensation(bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getNumber())
    print("str s2 " + str(s2))
    print(str(s_Drive == s2))
    
    #test with create
    print("test with create")
    s_Drive_create=Sensation.create(sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("Sensation.create: str s  " + str(s_Drive_create)))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getNumber())
    b=s_Drive_create.bytes()
    # TODO should s2 be here really reference to s, same instance? maybe
    s2=Sensation.create(bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getNumber())
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create:" + str(s_Drive_create == s2))
    print()

    
    s_Stop=Sensation(sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print("str s  " + str(s_Stop))
    b=s_Stop.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Stop == s2))

    #test with create
    print("test with create")
    s_Stop_create=Sensation.create(sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Stop_create)))
    b=s_Stop_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Stop_create == s2))
    print()
    
    s_Who=Sensation(sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print("str s  " + str(s_Who))
    b=s_Who.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Who == s2))
    
    #test with create
    print("test with create")
    s_Who_create=Sensation.create(sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Who_create)))
    b=s_Who_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Who_create == s2))
    print()

    
    s_HearDirection=Sensation(references=[s_Drive], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s_HearDirection)))
    b=s_HearDirection.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_HearDirection == s2))

    #test with create
    print("test with create")
    s_HearDirection_create=Sensation.create(references=[s_Drive_create], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("Sensation.create: str s  " + str(s_HearDirection_create)))
    b=s_HearDirection_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_HearDirection_create == s2))
    print()

    s_Azimuth=Sensation(references=[s_HearDirection], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("str s  " + str(s_Azimuth)))
    b=s_Azimuth.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Azimuth == s2))

    #test with create
    print("test with create")
    s_Azimuth_create=Sensation.create(references=[s_Who_create], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("Sensation.create: str s  " + str(s_Azimuth_create)))
    b=s_Azimuth_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Azimuth_create == s2))
    print()

    s_Acceleration=Sensation(references=[s_HearDirection,s_Azimuth], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("str s  " + str(s_Acceleration)))
    b=s_Acceleration.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Acceleration == s2))

    #test with create
    print("test with create")
    s_Acceleration_create=Sensation.create(references=[s_HearDirection_create,s_Azimuth_create], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("Sensation.create: str s  " + str(s_Acceleration_create)))
    b=s_Acceleration_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " +str(s_Acceleration_create == s2))
    print()

    
    s_Observation=Sensation(references=[s_HearDirection,s_Azimuth,s_Acceleration], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Working, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("str s  " + str(s_Observation)))
    b=s_Observation.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Observation == s2))

    #test with create
    print("test with create")
    s_Observation_create=Sensation.create(references=[s_HearDirection_create,s_Azimuth_create,s_Acceleration_create],  receivedFrom=['localhost', 'raspberry', 'virtualWalle',  'remoteWalle'], sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Working, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("Sensation.create: str s  " + str(s_Observation_create)))
    b=s_Observation_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Observation_create == s2))
    print()
    
    # voice
    s_VoiceFilePath=Sensation(references=[s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print("str s  " + str(s_VoiceFilePath))
    b=s_VoiceFilePath.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_VoiceFilePath == s2))

    #test with create
    print("test with create")
    s_VoiceFilePath_create=Sensation.create(references=[s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print(("Sensation.create: str s  " + str(s_VoiceFilePath_create)))
    b=s_VoiceFilePath_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_VoiceFilePath_create == s2))
    print()

    s_VoiceData=Sensation(references=[s_VoiceFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, data=b'\x01\x02\x03\x04\x05')
    print(("str s  " + str(s_VoiceData)))
    b=s_VoiceData.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_VoiceData == s2))

    #test with create
    print("test with create")
    s_VoiceData_create=Sensation.create(references=[s_VoiceFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In,  data=b'\x01\x02\x03\x04\x05')
    print(("Sensation.create: str s  " + str(s_VoiceData_create)))
    b=s_VoiceData_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " +str(s_VoiceData_create == s2))
    print()
    
    # image    
    s_ImageFilePath=Sensation(references=[s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print(("str s  " + str(s_ImageFilePath)))
    b=s_ImageFilePath.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_ImageFilePath == s2))

    #test with create
    print("test with create")
    s_ImageFilePath_create=Sensation.create(references=[s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, filePath="my/own/path/to/file")
    print(("Sensation.create: str s  " + str(s_ImageFilePath_create)))
    b=s_ImageFilePath_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_ImageFilePath_create == s2))
    print()

    s_ImageData=Sensation(references=[s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
    print("str s  " + str(s_ImageData))
    b=s_ImageData.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_ImageData == s2))

    #test with create
    print("test with create")
    s_ImageData_create=Sensation.create(references=[s_ImageFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
    print("Sensation.create: str s  " + str(s_ImageData_create))
    b=s_ImageData_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " +str(s_ImageData_create == s2))
    print()

    s_Calibrate=Sensation(references=[s_ImageData,s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print("str s  " + str(s_Calibrate))
    b=s_Calibrate.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Calibrate == s2))

    #test with create
    print("test with create")
    s_Calibrate_create=Sensation.create(references=[s_ImageData_create,s_ImageFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print("Sensation.create: str s  " + str(s_Calibrate_create))
    b=s_Calibrate_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Calibrate_create == s2))
    print()

#    s_Capability=Sensation(references=[s_Calibrate,s_VoiceData,s_VoiceFilePath,s_ImageData,s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    s_Capability=Sensation(references=[s_Calibrate,s_VoiceData,s_VoiceFilePath,s_ImageData,s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = capabilities)
    print(("str s  " + str(s_Capability)))
    b=s_Capability.bytes()
    s2=Sensation(bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Capability == s2))
    
     #test with create
    print("test with create")
    s_Capability_create=Sensation.create(references=[s_Calibrate_create,s_VoiceData_create,s_VoiceFilePath_create,s_ImageData_create,s_ImageFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = capabilities)
    print(("Sensation.create: str s  " + str(s_Capability_create)))
    b=s_Capability_create.bytes()
    s2=Sensation.create(bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Capability_create == s2))
   