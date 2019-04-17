'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

import time as systemTime
import traceback
from enum import Enum
import struct
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
 
    number=0                # sensation number for referencing
    
    CACHE_TIME = 60.0;       # cache sensation 600 seconds = 1 mins (may be changed)
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
    SensationType = enum(Drive='a', Stop='b', Who='c', HearDirection='d', Azimuth='e', Acceleration='f', Observation='g', PictureFilePath='h', PictureData='i', Calibrate='j', Capability='k', Unknown='l')
    Direction = enum(In='I', Out='O')
    Memory = enum(Sensory='S', Working='W', LongTerm='L' )

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
    PICTUREPATH="PictureFilePath"
    PICTUREDATA="PictureData"
    CALIBRATE="Calibrate"
    CAPABILITY="Capability"
    
    Directions={Direction.In: IN,
                Direction.Out: OUT}
    
    Memorys = {Memory.Sensory: SENSORY,
               Memory.Working: WORKING,
               Memory.LongTerm: LONG_TERM}
    SensationTypes={SensationType.Drive: DRIVE,
               SensationType.Stop: STOP,
               SensationType.Who: WHO,
                SensationType.HearDirection: HEARDIRECTION,
                SensationType.Azimuth: AZIMUTH,
                SensationType.Acceleration: ACCELERATION,
                SensationType.Observation: OBSERVATION,
                SensationType.PictureFilePath: PICTUREPATH,
                SensationType.PictureData: PICTUREDATA,
                SensationType.Calibrate: CALIBRATE,
                SensationType.Capability: CAPABILITY}
    
    def getDirectionStrings():
        return Sensation.Directions.values()
    def getMemoryStrings():
        return Sensation.Memorys.values()
    def getSensationTypeStrings():
        return Sensation.SensationTypes.values()

    
    def addToSensationMemory(sensation):
        # add new sensation
        Sensation.sensationMemory.append(sensation)
        
        # remove too old ones
        now = systemTime.time()
        if len(Sensation.sensationMemory) > 0:
            sensation = Sensation.sensationMemory[0]
            while len(Sensation.sensationMemory) > 0 and now - sensation.getTime() > Sensation.CACHE_TIME:
                del Sensation.sensationMemory[0]
                sensation = Sensation.sensationMemory[0]
                
    def getSensationFromSensationMemory(referenceNumber):
        if len(Sensation.sensationMemory) > 0:
            for reference in Sensation.sensationMemory:
                if reference.getNumber() == referenceNumber:
                    return reference
        return None
               
         
    def nextNumber():
       Sensation.number=Sensation.number+1
       return Sensation.number


    
#    list(Memory)
#     class Memory(Enum):
#         Sensory='S',
#         Working='W',
#         LongTerm='L'
       
    def __init__(self,
                 string="",
                 bytes=None,
                 time=None,
                 number=None,
                 referenceNumber=None,
                 reference=None,
                 sensationType = SensationType.Unknown,
                 memory=Memory.Sensory,
                 direction=Direction.In,
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 imageSize=0,                                               # when image is transferred we use size of it technically in transmission
                 calibrateSensationType = SensationType.Unknown,
                 capabilities = []):                         # capabilitis of sensorys, direction what way sensation go
        self.time=time
        if self.time == None:
            self.time = systemTime.time()
        self.number = number
        if self.number == None:
            self.number = Sensation.nextNumber()
            
        self.reference=reference
        if self.reference != None:
            self.referenceNumber = reference.getNumber()
        else:
            self.referenceNumber=referenceNumber
            if self.referenceNumber != None:
                self.reference = Sensation.getSensationFromSensationMemory(self.referenceNumber)
            
        self.sensationType = sensationType
        self.memory = memory
        self.direction = direction
        self.leftPower = leftPower
        self.rightPower = rightPower
        self.hearDirection = hearDirection
        self.azimuth = azimuth
        self.accelerationX = accelerationX
        self.accelerationY = accelerationY
        self.accelerationZ = accelerationZ
        self.observationDirection = observationDirection
        self.observationDistance = observationDistance
        self.imageSize = imageSize
        self.calibrateSensationType = calibrateSensationType
        self.capabilities = capabilities
       
        params = string.split()
        #print params
        if len(params) >= 4:
            try:
                self.number = int(params[0])
                self.memory = params[1]
                self.direction = params[2]
            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
                return
  
            try:              
                #print self.number
                if len(params) >= 4:
                    sensationType = params[3]
                    if sensationType == Sensation.SensationType.Drive:
                        self.sensationType = Sensation.SensationType.Drive
                        if len(params) >= 5:
                            self.leftPower = float(params[4])
                            #print str(self.leftPower)
                        if len(params) >= 6:
                            self.rightPower = float(params[5])
                            #print str(self.rightPower)
                    elif sensationType == Sensation.SensationType.HearDirection:
                        self.sensationType = Sensation.SensationType.HearDirection
                        if len(params) >= 5:
                            self.hearDirection = float(params[4])
                            #print str(self.hearDirection)
                    elif sensationType == Sensation.SensationType.Azimuth:
                        self.sensationType = Sensation.SensationType.Azimuth
                        if len(params) >= 5:
                            self.azimuth = float(params[4])
                            #print str(self.azimuth)
                    elif sensationType == Sensation.SensationType.Acceleration:
                        self.sensationType = Sensation.SensationType.Acceleration
                        if len(params) >= 7:
                            self.accelerationX = float(params[4])
                            self.accelerationY = float(params[5])
                            self.accelerationZ = float(params[6])
                            #print str(self.accelerationX) + ' ' + str(self.accelerationY) + ' ' + str(self.accelerationZ)
                    elif sensationType == Sensation.SensationType.Observation:
                        self.sensationType = Sensation.SensationType.Observation
                        if len(params) >= 6:
                            self.observationDirection = float(params[4])
                            self.observationDistance = float(params[5])
                            #print str(self.observationDirection) + ' ' + str(self.observationDistance)
                    elif sensationType == Sensation.SensationType.PictureFilePath:
                        self.sensationType = Sensation.SensationType.PictureFilePath
                        if len(params) >= 5:
                            self.imageSize = int(params[4])
                            #print str(self.imageSize)
                    elif sensationType == Sensation.SensationType.PictureData:
                        self.sensationType = Sensation.SensationType.PictureData
                        if len(params) >= 5:
                            self.imageSize = int(params[4])
                            #print str(self.imageSize)
                    elif sensationType == Sensation.SensationType.Calibrate:
                        self.sensationType = Sensation.SensationType.Calibrate
                        if len(params) >= 5:
                            self.calibrateSensationType = params[4]
                            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                                if len(params) >= 6:
                                    self.hearDirection = float(params[5])
                            print(("Calibrate hearDirection " + str(self.hearDirection)))
                    elif sensationType == Sensation.SensationType.Capability:
                        self.sensationType = Sensation.SensationType.Capability
                        if len(params) >= 5:
                            self.capabilities = params[4:]
                            #print str(self.capabilities)
        
                    elif sensationType == Sensation.SensationType.Stop:
                        self.sensationType = Sensation.SensationType.Stop
                    elif sensationType == Sensation.SensationType.Who:
                        self.sensationType = Sensation.SensationType.Who
                    else:
                        self.sensationType = Sensation.SensationType.Unknown
                    #print self.sensationType
            except (ValueError):
                print((traceback.format_exc()))
                self.sensationType = Sensation.SensationType.Unknown

        #print params
        if bytes != None:
            try:
                l=len(bytes)
                i=0
                self.number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
                #print("number " + str(number))
                i += Sensation.NUMBER_SIZE
                
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
                elif self.sensationType is Sensation.SensationType.PictureFilePath:
                    self.imageSize =int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER)
                    i += Sensation.NUMBER_SIZE
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
                    self.capabilities = bytesToStr(bytes[i:l+1])

            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
               
        Sensation.addToSensationMemory(self)
        Sensation.getSensationTypeStrings() # test

                 
    def __str__(self):
        if self.sensationType == Sensation.SensationType.Drive:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensationType == Sensation.SensationType.HearDirection:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.hearDirection)
        elif self.sensationType == Sensation.SensationType.Azimuth:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.azimuth)
        elif self.sensationType == Sensation.SensationType.Acceleration:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.accelerationX)+ ' ' + str(self.accelerationY) + ' ' + str(self.accelerationZ)
        elif self.sensationType == Sensation.SensationType.Observation:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.observationDirection)+ ' ' + str(self.observationDistance)
        elif self.sensationType == Sensation.SensationType.PictureFilePath:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.imageSize)
        elif self.sensationType == Sensation.SensationType.PictureData:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + str(self.imageSize)
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + self.calibrateSensationType + ' ' + str(self.hearDirection)
            else:
                return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType + ' ' + self.getStrCapabilities()
        elif self.sensationType == Sensation.SensationType.Stop:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
        elif self.sensationType == Sensation.SensationType.Who:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType
        else:
            return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + self.sensationType

    def bytes(self):
        b = self.number.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
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
        elif self.sensationType == Sensation.SensationType.PictureFilePath:
            b +=  self.imageSize.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        elif self.sensationType == Sensation.SensationType.PictureData:
            b +=  self.imageSize.to_bytes(Sensation.NUMBER_SIZE, Sensation.BYTEORDER)
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                b += StrToBytes(self.calibrateSensationType) + floatToBytes(self.hearDirection)
#             else:
#                 return str(self.number) + ' ' + self.memory + ' ' + self.direction + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            b += StrToBytes(self.getStrCapabilities())
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
    
    def setReference(self, reference):
        self.reference = reference
    def getReference(self):
        return self.reference

    def setReferenceNumber(self, referenceNumber):
        self.referenceNumber = referenceNumber
    def getReference(self):
        return self.referenceNumber
 
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

        
if __name__ == '__main__':
    # TODO Correct these
#     s=Sensation(string="12 S I D 0.97 0.56")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#         
#     s=Sensation(string="13 S I S")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     s=Sensation(string="13 S I W")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     s=Sensation(string="14 S I H -0.75")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     s=Sensation(string="15 S I A 0.75")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     s=Sensation(string="15 W I O 0.75 3.75")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     s=Sensation(string="16 S I P 12300")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     s=Sensation(string="17 S I C H -0.75")
#     print(("str s  " + str(s)))
#     print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
#     b=s.bytes()
#     s2=Sensation(bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s == s2))
#     
#     
#     
#     
#     
#     
#     
#     
#     s=Sensation(string="18 oho")
#     print("str " + str(s))
#     s=Sensation(string="hupsis oli")
#     print("str " + str(s))
    
    s_Drive=Sensation(sensationType = Sensation.SensationType.Drive, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("str s  " + str(s_Drive)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Drive))))
    b=s_Drive.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Drive == s2))
    
    s_Stop=Sensation(sensationType = Sensation.SensationType.Stop, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("str s  " + str(s_Stop)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Stop))))
    b=s_Stop.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Stop == s2))
    
    s_Who=Sensation(sensationType = Sensation.SensationType.Who, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In)
    print(("str s  " + str(s_Who)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Who))))
    b=s_Who.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Who == s2))
    
    s_HearDirection=Sensation(referenceNumber=s_Drive.getNumber(), sensationType = Sensation.SensationType.HearDirection, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s_HearDirection)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_HearDirection))))
    b=s_HearDirection.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_HearDirection == s2))

    s_Azimuth=Sensation(referenceNumber=s_HearDirection.getNumber(), sensationType = Sensation.SensationType.Azimuth, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("str s  " + str(s_Azimuth)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Azimuth))))
    b=s_Azimuth.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Azimuth == s2))

    s_Acceleration=Sensation(reference=s_Azimuth, sensationType = Sensation.SensationType.Acceleration, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("str s  " + str(s_Acceleration)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Acceleration))))
    b=s_Acceleration.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Acceleration == s2))

    s_Observation=Sensation(reference=s_Acceleration, sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Working, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("str s  " + str(s_Observation)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Observation))))
    b=s_Observation.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Observation == s2))

    s_PictureFilePath=Sensation(reference=s_Acceleration, sensationType = Sensation.SensationType.PictureFilePath, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageSize=1024)
    print(("str s  " + str(s_PictureFilePath)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_PictureFilePath))))
    b=s_PictureFilePath.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_PictureFilePath == s2))

    s_PictureData=Sensation(reference=s_Acceleration, sensationType = Sensation.SensationType.PictureData, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, imageSize=1024)
    print(("str s  " + str(s_PictureData)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_PictureData))))
    b=s_PictureData.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_PictureData == s2))

    s_Calibrate=Sensation(reference=s_Observation, sensationType = Sensation.SensationType.Calibrate, memory = Sensation.Memory.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s_Calibrate)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Calibrate))))
    b=s_Calibrate.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Calibrate == s2))

    s_Capability=Sensation(reference=s_Calibrate, sensationType = Sensation.SensationType.Capability, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    print(("str s  " + str(s_Capability)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s_Capability))))
    b=s_Capability.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s_Capability == s2))
    
    bytes = s_Capability.bytes()
    l=len(bytes)
    print("len(bytes) " + str(l))
    i=0
    number = int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER) 
    print("number " + str(number))
    i += Sensation.NUMBER_SIZE
    
    memory = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
    #memory = bytesToStr(bytes[4:])
    print("memory " + str(memory))
    i += Sensation.ENUM_SIZE
    
    sensationType = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
    print("sensationType " + str(sensationType))
    i += Sensation.ENUM_SIZE
    
    direction = bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
    print("direction " + str(direction))
    i += Sensation.ENUM_SIZE
    
    capabilities = bytesToStr(bytes[i:l+1])
    print("capabilities " + str(capabilities))
    i = l

    print("bytes " + str(bytes))
