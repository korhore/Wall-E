'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

import time as systemTime
import traceback
from enum import Enum
import struct
import random
#from distlib.resources import cache
#from _ast import If
#from builtins import None


#def enum(**enums):
#    return type('Enum', (), enums)

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def StrToBytes(e):
    return e.encode('utf8')

def bytesToStr(b):
    return b.decode('utf8')

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
                            # a picture (Sensory) and process it with tnsorFlow
                            # which classifies it as get words and get
                            # Working or Memory level Sensations that refers
                            # to the original hearing, a picture, meaning
                            # that robot has seen it at certain time.
                            # THigher level Sensation can be processed also and
                            # we can save original picture in a file with
                            # its classified names. After that our robot
                            # knows how those classifies names look like,
                            # what is has seen. 
 
    #number=0                # sensation number for referencing
    LOWPOINT_NUMBERVARIANCE=-100.0
    HIGHPOINT_NUMBERVARIANCE=100.0
    
    CACHE_TIME = 600.0;       # cache sensation 600 seconds = 10 mins (may be changed)
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
    SensationType = enum(Drive='a', Stop='b', Who='c', HearDirection='d', Azimuth='e', Acceleration='f', Observation='g', ImageFilePath='h', PictureData='i', Calibrate='j', Capability='k', Unknown='l')
    Direction = enum(In='I', Out='O')
    Memory = enum(Sensory='S', Working='W', LongTerm='L' )
    Kind = enum(WallE='w', Eva='e', Other='o')
    Instance = enum(Real='r', SubInstance='s', Virtual='v')
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
    HEARDIRECTION="HearDirection"
    AZIMUTH="Azimuth"
    ACCELERATION="Acceleration"
    OBSERVATION="Observation"
    IMAGEFILEPATH="ImageFilePath"
    PICTUREDATA="PictureData"
    CALIBRATE="Calibrate"
    CAPABILITY="Capability"
    KIND="Kind"
    WALLE="Wall-E"
    EVA="Eva"
    OTHER="Other"
    REAL="Real"
    SUBINSTANCE="SubInstance"
    VIRTUAL="Virtual"
    NORMAL="Normal"
    STUDYOWNIDENTITY="StudyOwnIdentity"
    SLEEPING="Sleeping"
    STARTING="Starting"
    STOPPING="Stopping"
      
    Directions={Direction.In: IN,
                Direction.Out: OUT}
    
    Memorys = {Memory.Sensory: SENSORY,
               Memory.Working: WORKING,
               Memory.LongTerm: LONG_TERM}
    SensationTypes={
               SensationType.Drive: DRIVE,
               SensationType.Stop: STOP,
               SensationType.Who: WHO,
               SensationType.HearDirection: HEARDIRECTION,
               SensationType.Azimuth: AZIMUTH,
               SensationType.Acceleration: ACCELERATION,
               SensationType.Observation: OBSERVATION,
               SensationType.ImageFilePath: IMAGEFILEPATH,
               SensationType.PictureData: PICTUREDATA,
               SensationType.Calibrate: CALIBRATE,
               SensationType.Capability: CAPABILITY}
    Kinds={Kind.WallE: WALLE,
           Kind.Eva: EVA,
           Kind.Other: OTHER}
    Instances={Instance.Real: REAL,
               Instance.SubInstance: SUBINSTANCE,
               Instance.Virtual: VIRTUAL}
    Modes={Mode.Normal: NORMAL,
           Mode.StudyOwnIdentity: STUDYOWNIDENTITY,
           Mode.Sleeping: SLEEPING,
           Mode.Starting: STARTING,
           Mode.Stopping: STOPPING }
    
    def getDirectionString(direction):
        ret = Sensation.Directions.get(direction)
        return ret
    def getDirectionStrings():
        return Sensation.Directions.values()
    
    def getMemoryString(memory):
        ret = Sensation.Memorys.get(memory)
        return ret
    def getMemoryStrings():
        return Sensation.Memorys.values()
    
    def getSensationTypeString(sensationType):
        ret = Sensation.SensationTypes.get(sensationType)
        return Sensation.SensationTypes.get(sensationType)
    def getSensationTypeStrings():
        return Sensation.SensationTypes.values()

    
    def addToSensationMemory(sensation):
        # add new sensation
        Sensation.sensationMemory.append(sensation)
        
        # remove too old ones
        now = systemTime.time()
        while len(Sensation.sensationMemory) > 0 and now - Sensation.sensationMemory[0].getTime() > Sensation.CACHE_TIME:
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
                 string=None,
                 bytes=None,
                 time=None,
                 number=None,
                 references=[],
                 sensationType = SensationType.Unknown,
                 memory=Memory.Sensory,
                 direction=Direction.In,
                 who=None,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 imageFilePath=None,
                 imageSize=0,                                               # when image is transferred we use size of it technically in transmission
                 calibrateSensationType = SensationType.Unknown,
                 capabilities = []):                         # capabilitis of sensorys, direction what way sensation go
        self.time=time
        if self.time == None:
            self.time = systemTime.time()
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
        if references == None:
            references=[]
        self.references=[]
        self.addReferences(references)
            
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
        self.imageFilePath = imageFilePath
        self.imageSize = imageSize
        self.calibrateSensationType = calibrateSensationType
        self.capabilities = capabilities

        if string != None:    
            params = string.split()
            #print params
            if len(params) >= 4:
                try:
                    self.number = float(params[0])
                    self.memory = params[1]
                    self.direction = params[2]
                    self.sensationType = params[3]
                    last_param=4
                except (ValueError):
                    self.sensationType = Sensation.SensationType.Unknown
                    return
      
                try:              
                    #print self.number
                    if len(params) >= 4:
                        sensationType = params[3]
                        if self.sensationType == Sensation.SensationType.Drive:
                            if len(params) >= 5:
                                self.leftPower = float(params[4])
                                #print str(self.leftPower)
                                last_param=5
                            if len(params) >= 6:
                                self.rightPower = float(params[5])
                                last_param=6
                                #print str(self.rightPower)
                        elif self.sensationType == Sensation.SensationType.HearDirection:
                            if len(params) >= 5:
                                self.hearDirection = float(params[4])
                                last_param=5
                                #print str(self.hearDirection)
                        elif self.sensationType == Sensation.SensationType.Azimuth:
                            if len(params) >= 5:
                                self.azimuth = float(params[4])
                                last_param=5
                                #print str(self.azimuth)
                        elif self.sensationType == Sensation.SensationType.Acceleration:
                            if len(params) >= 7:
                                self.accelerationX = float(params[4])
                                self.accelerationY = float(params[5])
                                self.accelerationZ = float(params[6])
                                last_param=7
                                #print str(self.accelerationX) + ' ' + str(self.accelerationY) + ' ' + str(self.accelerationZ)
                        elif self.sensationType == Sensation.SensationType.Observation:
                            if len(params) >= 6:
                                self.observationDirection = float(params[4])
                                self.observationDistance = float(params[5])
                                last_param=6
                                #print str(self.observationDirection) + ' ' + str(self.observationDistance)
                        elif self.sensationType == Sensation.SensationType.ImageFilePath:
                            if len(params) >= 5:
                                self.imageFilePath = params[4]
                                last_param=5
                        elif self.sensationType == Sensation.SensationType.PictureData:
                            if len(params) >= 5:
                                self.imageSize = int(params[4])
                                last_param=5
                                #print str(self.imageSize)
                        elif self.sensationType == Sensation.SensationType.Calibrate:
                            if len(params) >= 5:
                                self.calibrateSensationType = params[4]
                                last_param=5
                                if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                                    if len(params) >= 6:
                                        self.hearDirection = float(params[5])
                                        last_param=6
                                print(("Calibrate hearDirection " + str(self.hearDirection)))
                        elif self.sensationType == Sensation.SensationType.Capability:
                            if len(params) >= 5:
                                # TODO uncode string of params
                                self.capabilities = params[4]
                                last_param=5
                                #print str(self.capabilities)
            
    #                     elif self.sensationType == Sensation.SensationType.Stop:
    #                         self.sensationType = Sensation.SensationType.Stop
    #                     elif self.sensationType == Sensation.SensationType.Who:
    #                         self.sensationType = Sensation.SensationType.Who
    #                     else:
    #                         self.sensationType = Sensation.SensationType.Unknown
                        #print self.sensationType
    
                        if len(params) >= last_param:
                                # TODO uncode string of params
                            str_reference_numbers = params[last_param:]
                            reference_numbers=[]
                            for str_reference_number in str_reference_numbers:
                                print("reference number:"  + str_reference_number)
                                reference_numbers.append(float(str_reference_number))
                            self.addReferenceNumbers(reference_numbers)
    
                except (ValueError):
                    print((traceback.format_exc()))
                    self.sensationType = Sensation.SensationType.Unknown

        #print params
        if bytes != None:
            try:
                l=len(bytes)
                i=0
                #self.number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                #print("number " + str(number))
                #i += Sensation.NUMBER_SIZE
                self.number = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
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
                elif self.sensationType is Sensation.SensationType.ImageFilePath:
                    imageFilePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("imageFilePath_size " + str(imageFilePath_size))
                    i += Sensation.NUMBER_SIZE
                    self.imageFilePath =bytesToStr(bytes[i:i+imageFilePath_size])
                    i += imageFilePath_size
                    # TODO real image
                elif self.sensationType is Sensation.SensationType.PictureData:
                    self.imageSize =int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER)
                    i += Sensation.NUMBER_SIZE
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
                    self.capabilities = bytesToStr(bytes[i:i+capabilities_size])
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
        #Sensation.getSensationTypeStrings() # test

    '''
    Constructor that take care, that we have only one instace
    per Sensation per number
    
    This is needed if we want handle references properly.
    It is not allowed to have many instances of same Sensation,
    because it brakes sensation associations.
    
    Parameters are exactly same than in default constsructor
    '''
       
    def create(  string=None,
                 bytes=None,
                 time=None,
                 number=None,
                 references=[],
                 sensationType = SensationType.Unknown,
                 memory=Memory.Sensory,
                 direction=Direction.In,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 imageFilePath=None,
                 imageSize=0,                                               # when image is transferred we use size of it technically in transmission
                 calibrateSensationType = SensationType.Unknown,
                 capabilities = []):                                        # capabilitis of sensorys, direction what way sensation go
        
        if string != None:              # if string we get number there
            params = string.split()
            number = float(params[0])
        if bytes != None:               # if bytes, we get number there
            number = bytesToFloat(bytes[0:Sensation.FLOAT_PACK_SIZE])
 
        sensation = None                # try to find existing sensation by number           
        if number != None:
            sensation = Sensation.getSensationFromSensationMemory(number)

            
        if sensation == None:             # not an update, create new one
            print("Create new sensation")
            return Sensation(string=string,
                 bytes=bytes,
                 time=time,
                 number=number,
                 references=references,
                 sensationType = sensationType,
                 memory=memory,
                 direction=direction,
                 leftPower = leftPower, rightPower = rightPower,                         # Walle motors state
                 azimuth = azimuth,                                             # Walle direction relative to magnetic north pole
                 accelerationX=accelerationX, accelerationY=accelerationY, accelerationZ=accelerationZ,   # acceleration of walle, coordinates relative to walle
                 hearDirection = hearDirection,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection = observationDirection,observationDistance = observationDistance,        # Walle's observation of something, relative to Walle
                 imageFilePath=imageFilePath,
                 imageSize=imageSize,                                               # when image is transferred we use size of it technically in transmission
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities)
            
        print("Update existing sensation")
        # update existing one    
        sensation.time=time
        if sensation.time == None:
            sensation.time = systemTime.time()

        # references are always both way
        if references == None:
            references=[]
        sensation.references=[]
        sensation.addReferences(references)
                
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
        sensation.imageFilePath = imageFilePath
        sensation.imageSize = imageSize
        sensation.calibrateSensationType = calibrateSensationType
        sensation.capabilities = capabilities
          
        if string != None:    
            params = string.split()
            #print params
            if len(params) >= 4:
                try:
                    sensation.number = float(params[0])
                    sensation.memory = params[1]
                    sensation.direction = params[2]
                    sensation.sensationType = params[3]
                    last_param=4
                except (ValueError):
                    sensation.sensationType = Sensation.SensationType.Unknown
                    return
        
                try:              
                    #print sensation.number
                    if len(params) >= 4:
                        sensationType = params[3]
                        if sensation.sensationType == Sensation.SensationType.Drive:
                            if len(params) >= 5:
                                sensation.leftPower = float(params[4])
                                #print str(sensation.leftPower)
                                last_param=5
                            if len(params) >= 6:
                                sensation.rightPower = float(params[5])
                                last_param=6
                                #print str(sensation.rightPower)
                        elif sensation.sensationType == Sensation.SensationType.HearDirection:
                            if len(params) >= 5:
                                sensation.hearDirection = float(params[4])
                                last_param=5
                                #print str(sensation.hearDirection)
                        elif sensation.sensationType == Sensation.SensationType.Azimuth:
                            if len(params) >= 5:
                                sensation.azimuth = float(params[4])
                                last_param=5
                                #print str(sensation.azimuth)
                        elif sensation.sensationType == Sensation.SensationType.Acceleration:
                            if len(params) >= 7:
                                sensation.accelerationX = float(params[4])
                                sensation.accelerationY = float(params[5])
                                sensation.accelerationZ = float(params[6])
                                last_param=7
                                #print str(sensation.accelerationX) + ' ' + str(sensation.accelerationY) + ' ' + str(sensation.accelerationZ)
                        elif sensation.sensationType == Sensation.SensationType.Observation:
                            if len(params) >= 6:
                                sensation.observationDirection = float(params[4])
                                sensation.observationDistance = float(params[5])
                                last_param=6
                                #print str(sensation.observationDirection) + ' ' + str(sensation.observationDistance)
                        elif sensation.sensationType == Sensation.SensationType.ImageFilePath:
                            if len(params) >= 5:
                                sensation.imageFilePath = params[4]
                                last_param=5
                        elif sensation.sensationType == Sensation.SensationType.PictureData:
                            if len(params) >= 5:
                                sensation.imageSize = int(params[4])
                                last_param=5
                                #print str(sensation.imageSize)
                        elif sensation.sensationType == Sensation.SensationType.Calibrate:
                            if len(params) >= 5:
                                sensation.calibrateSensationType = params[4]
                                last_param=5
                                if sensation.calibrateSensationType == Sensation.SensationType.HearDirection:
                                    if len(params) >= 6:
                                        sensation.hearDirection = float(params[5])
                                        last_param=6
                                print(("Calibrate hearDirection " + str(sensation.hearDirection)))
                        elif sensation.sensationType == Sensation.SensationType.Capability:
                            if len(params) >= 5:
                                # TODO uncode string of params
                                sensation.capabilities = params[4]
                                last_param=5
                                #print str(sensation.capabilities)
            
        #                     elif sensation.sensationType == Sensation.SensationType.Stop:
        #                         sensation.sensationType = Sensation.SensationType.Stop
        #                     elif sensation.sensationType == Sensation.SensationType.Who:
        #                         sensation.sensationType = Sensation.SensationType.Who
        #                     else:
        #                         sensation.sensationType = Sensation.SensationType.Unknown
                            #print sensation.sensationType
        
                        if len(params) >= last_param:
                                # TODO uncode string of params
                            str_reference_numbers = params[last_param:]
                            reference_numbers=[]
                            for str_reference_number in str_reference_numbers:
                                print("reference number:"  + str_reference_number)
                                reference_numbers.append(float(str_reference_number))
                            sensation.addReferenceNumbers(reference_numbers)
        
                except (ValueError):
                    print((traceback.format_exc()))
                    sensation.sensationType = Sensation.SensationType.Unknown
    
        #print params
        if bytes != None:
            try:
                l=len(bytes)
                i=0
                #sensation.number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                #print("number " + str(number))
                #i += Sensation.NUMBER_SIZE
                sensation.number = bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
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
                elif sensation.sensationType is Sensation.SensationType.ImageFilePath:
                    imageFilePath_size = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                    print("imageFilePath_size " + str(imageFilePath_size))
                    i += Sensation.NUMBER_SIZE
                    sensation.imageFilePath =bytesToStr(bytes[i:i+imageFilePath_size])
                    i += imageFilePath_size
                    # TODO real image
                elif sensation.sensationType is Sensation.SensationType.PictureData:
                    sensation.imageSize =int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER)
                    i += Sensation.NUMBER_SIZE
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
                    sensation.capabilities = bytesToStr(bytes[i:i+capabilities_size])
                    i += capabilities_size
                        
                reference_number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                print("reference_number " + str(reference_number))
                i += Sensation.NUMBER_SIZE
                referenceNumbers=[]
                for j in range(reference_number):
                    referenceNumbers.append(bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE]))
                    i += Sensation.FLOAT_PACK_SIZE
                sensation.addReferenceNumbers(referenceNumbers)
    
     
    
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
        s=str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
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
        elif self.sensationType == Sensation.SensationType.ImageFilePath:
            s += ' ' + self.imageFilePath
        elif self.sensationType == Sensation.SensationType.PictureData:
            s += ' ' + str(self.imageSize)
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                s += ' ' + self.calibrateSensationType + ' ' + str(self.hearDirection)
            else:
                s = str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' +  Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            s +=  ' ' + self.getStrCapabilities()
            
#         elif self.sensationType == Sensation.SensationType.Stop:
#             pass
#         elif self.sensationType == Sensation.SensationType.Who:
#             pass
#         else:
#             pass

#        # TODO at the end references (numbers)
        for reference in self.references:
            s +=  ' ' + str(reference.getNumber())
        return s

    def bytes(self):
#        b = self.number.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
        b = floatToBytes(self.number)
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
        # TODO send real picture
        elif self.sensationType == Sensation.SensationType.ImageFilePath:
            imageFilePath_size=len(self.imageFilePath)
            b +=  imageFilePath_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b +=  StrToBytes(self.imageFilePath)
        elif self.sensationType == Sensation.SensationType.PictureData:
            b +=  self.imageSize.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                b += StrToBytes(self.calibrateSensationType) + floatToBytes(self.hearDirection)
#             else:
#                 return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            capabilities_size=len(self.getStrCapabilities())
            b += capabilities_size.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
            b += StrToBytes(self.getStrCapabilities())
            
        # TODO at the end references (numbers)
        reference_number=len(self.references)
        b +=  reference_number.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        for j in range(reference_number):
            b +=  floatToBytes(self.references[j].getNumber())

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

    
    def setNumber(self, number):
        self.number = number
    def getNumber(self):
        return self.number
    
    def setReferences(self, references):
        self.references = references
    '''
    Add single reference
    References are alwaystwo sided, but not referencing to self
    '''
    def addReference(self, reference):
        if reference is not self and \
           reference not in self.references:
            self.references.append(reference)
            reference.addReference(self)
    '''
    Add many referencew
    '''
    def addReferences(self, references):
        for reference in references:
            self.addReference(reference)

    def getReferences(self):
        return self.references

    def getReferenceNumbers(self):
        referenceNumbers=[]
        for reference in self.references:
            referenceNumbers.append(reference.getNumber())
        return referenceNumbers
 
    '''
    Add many references by reference numbers
    refernces and references to then are found from reference cache
    '''
    def addReferenceNumbers(self, referenceNumbers):
        for referenceNumber in referenceNumbers:
            references = Sensation.getSensationsFromSensationMemory(referenceNumber)
            self.addReferences(references)
            
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

    def setImageSize(self, imageSize):
        self.imageSize = imageSize
    def getImageSize(self):
        return self.imageSize
    

    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
    def getCapabilities(self):
        return self.capabilities
    
    def setStrCapabilities(self, string):
        #str_capabilities = string.split()
        self.capabilities=[]
        for capability in string:
            self.capabilities.add(capability)
        self.capabilities = capabilities
    def getStrCapabilities(self):
        capabilities = ""
        for capability in self.capabilities:
            capabilities += str(capability)
        return capabilities
    
    def hasCapability(self, directionStr,memoryStr,capabilityStr):
        if self.getSensationType() == SensationType.Capability:
            option=self.getOptionName(directionStr,memoryStr,capabilityStr)
            return self.getboolean(section, option)
        return False


        
if __name__ == '__main__':
# testing
    
    s_Drive=Sensation(sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("str s  " + str(s_Drive)))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getNumber())
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Drive))))
    b=s_Drive.bytes()
    # TODO should s2 be here really reference to s, same instance? maybe
    s2=Sensation(bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive.getNumber())
    print(("str s2 " + str(s2)))
    print(str(s_Drive == s2))
    
    #test with create
    print("test with create")
    s_Drive_create=Sensation.create(sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("Sensation.create: str s  " + str(s_Drive_create)))
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getNumber())
    print("Sensation.Create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Drive_create))))
    b=s_Drive_create.bytes()
    # TODO should s2 be here really reference to s, same instance? maybe
    s2=Sensation.create(bytes=b)
    sensations=Sensation.getSensationsFromSensationMemory(s_Drive_create.getNumber())
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create:" + str(s_Drive_create == s2))
    print()

    
    s_Stop=Sensation(sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("str s  " + str(s_Stop)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Stop))))
    b=s_Stop.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Stop == s2))

    #test with create
    print("test with create")
    s_Stop_create=Sensation.create(sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Stop_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Stop_create))))
    b=s_Stop_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_Stop_create == s2))
    print()
    
    s_Who=Sensation(sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("str s  " + str(s_Who)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Who))))
    b=s_Who.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Who == s2))
    
    #test with create
    print("test with create")
    s_Who_create=Sensation.create(sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("Sensation.create: str s  " + str(s_Who_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Who_create))))
    b=s_Who_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_Who_create == s2))
    print()

    
    s_HearDirection=Sensation(references=[s_Drive], sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s_HearDirection)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_HearDirection))))
    b=s_HearDirection.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_HearDirection == s2))

    #test with create
    print("test with create")
    s_HearDirection_create=Sensation.create(references=[s_Drive_create], sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("Sensation.create: str s  " + str(s_HearDirection_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_HearDirection_create))))
    b=s_HearDirection_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_HearDirection_create == s2))
    print()

    s_Azimuth=Sensation(references=[s_HearDirection], sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("str s  " + str(s_Azimuth)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Azimuth))))
    b=s_Azimuth.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Azimuth == s2))

    #test with create
    print("test with create")
    s_Azimuth_create=Sensation.create(references=[s_Who_create], sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("Sensation.create: str s  " + str(s_Azimuth_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Azimuth_create))))
    b=s_Azimuth_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_Azimuth_create == s2))
    print()

    s_Acceleration=Sensation(references=[s_HearDirection,s_Azimuth], sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("str s  " + str(s_Acceleration)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Acceleration))))
    b=s_Acceleration.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Acceleration == s2))

    #test with create
    print("test with create")
    s_Acceleration_create=Sensation.create(references=[s_HearDirection_create,s_Azimuth_create], sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("Sensation.create: str s  " + str(s_Acceleration_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Acceleration_create))))
    b=s_Acceleration_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " +str(s_Acceleration_create == s2))
    print()

    
    s_Observation=Sensation(references=[s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Working, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("str s  " + str(s_Observation)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Observation))))
    b=s_Observation.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Observation == s2))

    #test with create
    print("test with create")
    s_Observation_create=Sensation.create(references=[s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Working, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("Sensation.create: str s  " + str(s_Observation_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Observation_create))))
    b=s_Observation_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_Observation_create == s2))
    print()

    
    s_PictureFilePath=Sensation(references=[s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.ImageFilePath, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageFilePath="my/own/path/to/file")
    print(("str s  " + str(s_PictureFilePath)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_PictureFilePath))))
    b=s_PictureFilePath.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_PictureFilePath == s2))

    #test with create
    print("test with create")
    s_PictureFilePath_create=Sensation.create(references=[s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.ImageFilePath, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageFilePath="my/own/path/to/file")
    print(("Sensation.create: str s  " + str(s_PictureFilePath_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_PictureFilePath_create))))
    b=s_PictureFilePath_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_PictureFilePath_create == s2))
    print()

    s_PictureData=Sensation(references=[s_PictureFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.PictureData, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageSize=1024)
    print(("str s  " + str(s_PictureData)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_PictureData))))
    b=s_PictureData.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_PictureData == s2))

    #test with create
    print("test with create")
    s_PictureData_create=Sensation.create(references=[s_PictureFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.PictureData, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageSize=1024)
    print(("Sensation.create: str s  " + str(s_PictureData_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_PictureData_create))))
    b=s_PictureData_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " +str(s_PictureData_create == s2))
    print()

    s_Calibrate=Sensation(references=[s_PictureData,s_PictureFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s_Calibrate)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Calibrate))))
    b=s_Calibrate.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Calibrate == s2))

    #test with create
    print("test with create")
    s_Calibrate_create=Sensation.create(references=[s_PictureData_create,s_PictureFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("Sensation.create: str s  " + str(s_Calibrate_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Calibrate_create))))
    b=s_Calibrate_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_Calibrate_create == s2))
    print()

    s_Capability=Sensation(references=[s_Calibrate,s_PictureData,s_PictureFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    print(("str s  " + str(s_Capability)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Capability))))
    b=s_Capability.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Capability == s2))
    
     #test with create
    print("test with create")
    s_Capability_create=Sensation.create(references=[s_Calibrate_create,s_PictureData_create,s_PictureFilePath_create,s_Observation_create,s_HearDirection_create,s_Azimuth_create,s_Acceleration_create], sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    print(("Sensation.create: str s  " + str(s_Capability_create)))
    print("Sensation.create: str(Sensation(str(s))) " + str(Sensation.create(string=str(s_Capability_create))))
    b=s_Capability_create.bytes()
    s2=Sensation.create(bytes=b)
    print(("Sensation.create: str s2 " + str(s2)))
    print("Sensation.create: " + str(s_Capability_create == s2))
   