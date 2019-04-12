'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

import time
import traceback
from enum import Enum
import struct


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
    
    LENGTH_SIZE=2   # Sensation as string can only be 99 character long
    LENGTH_FORMAT = "{0:2d}"
    SEPARATOR='|'  # Separator between messages
    SEPARATOR_SIZE=1  # Separator length
    
    ENUM_SIZE=1
    NUMBER_SIZE=4
    BYTEORDER="little"
    FLOAT_PACK_TYPE="d"
    FLOAT_PACK_SIZE=8
   
    SensationType = enum(Drive='D', Stop='S', Who='W', HearDirection='H', Azimuth='A', Acceleration='G', Observation='O', Picture='P', Calibrate='C', Capability='1', Unknown='U')
    Direction = enum(In='I', Out='O')
    Memory = enum(Sensory='S', Working='W', LongTerm='L' )
    
#    list(Memory)
#     class Memory(Enum):
#         Sensory='S',
#         Working='W',
#         LongTerm='L'
       
    def __init__(self,
                 string="",
                 bytes=None,
                 number=-1,
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
        self.time = time.time()
        self.number = number
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
                    elif sensationType == Sensation.SensationType.Picture:
                        self.sensationType = Sensation.SensationType.Picture
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
                elif self.sensationType is Sensation.SensationType.Picture:
                    self.imageSize =int.from_bytes(bytes[i:i+Sensation.NUMBER_SIZE-1], Sensation.BYTEORDER)
                    i += Sensation.NUMBER_SIZE
                    # TODO real image
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
        elif self.sensationType == Sensation.SensationType.Picture:
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
        elif self.sensationType == Sensation.SensationType.Picture:
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
    s=Sensation(string="12 S I D 0.97 0.56")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
        
    s=Sensation(string="13 S I S")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(string="13 S I W")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(string="14 S I H -0.75")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(string="15 S I A 0.75")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(string="15 W I O 0.75 3.75")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(string="16 S I P 12300")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(string="17 S I C H -0.75")
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    
    
    
    
    
    
    
    s=Sensation(string="18 oho")
    print("str " + str(s))
    s=Sensation(string="hupsis oli")
    print("str " + str(s))
    
    s=Sensation(number=99, sensationType = 'D', memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, leftPower = 0.77, rightPower = 0.55)
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    s=Sensation(number=100, sensationType = 'H', memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))

    s=Sensation(number=101, sensationType = 'A', memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, azimuth = -0.85)
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))

    s=Sensation(number=102, sensationType = 'G', memory = Sensation.Memory.Sensory, direction = Sensation.Direction.In, accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))

    s=Sensation(number=103, sensationType = Sensation.SensationType.Observation, memory = Sensation.Memory.Working, direction = Sensation.Direction.In, observationDirection= -0.85, observationDistance=-3.75)
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))

    s=Sensation(number=104, sensationType = 'C', memory = Sensation.Memory.Sensory, calibrateSensationType = 'H', direction = Sensation.Direction.In, hearDirection = 0.85)
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))

    s=Sensation(number=10500, sensationType = '1', memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    print(("str s  " + str(s)))
    print("str(Sensation(str(s))) " + str(Sensation(string=str(s))))
    b=s.bytes()
    s2=Sensation(bytes=b)
    print(("str s2 " + str(s2)))
    print(str(s == s2))
    
    bytes = s.bytes()
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
