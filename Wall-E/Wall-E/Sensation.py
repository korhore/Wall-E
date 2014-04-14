'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

import time

def enum(**enums):
    return type('Enum', (), enums)

class Sensation(object):
    
    LENGTH_SIZE=2   # Sensation as string can only be 99 character long
    SEPARATOR='\r'  # Separator between messages
    SEPARATOR_SIZE=1  # Separator length
   
    SensationType = enum(Drive='D', Stop='S', Who='W', HearDirection='H', Azimuth='A', Acceleration='G', Observation='O', Picture='P', Capability='C', Unknown='U')
    Direction = enum(Input='I', Output='O')
       
    def __init__(self, string="",
                 number=-1, sensationType = 'U',
                 leftPower = 0.0, rightPower = 0.0,                         # Walle motors state
                 azimuth = 0.0,                                             # Walle direction relative to magnetic north pole
                 accelerationX=0.0, accelerationY=0.0, accelerationZ=0.0,   # acceleration of walle, coordinates relative to walle
                 hearDirection = 0.0,                                       # sound direction heard by Walle, relative to Walle
                 observationDirection= 0.0,observationDistance=-1.0,        # Walle's observation of something, relative to Walle
                 imageSize=0,                                               # when image is transferred we use size of it technically in transmission
                 direction='I', capabilities = []):                         # capabilitis of sensorys, direction what way sensation go
        self.time = time.time()
        self.number = number
        self.sensationType = sensationType
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
        self.direction = direction
        self.capabilities = capabilities
       
        params = string.split()
        print params
        if len(params) >= 1:
            try:
                self.number = int(params[0])
            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
                return
                
            print self.number
            if len(params) >= 2:
                sensationType = params[1]
                if sensationType == Sensation.SensationType.Drive:
                    self.sensationType = Sensation.SensationType.Drive
                    if len(params) >= 3:
                        self.leftPower = float(params[2])
                        print str(self.leftPower)
                    if len(params) >= 4:
                        self.rightPower = float(params[3])
                        print str(self.rightPower)
                elif sensationType == Sensation.SensationType.HearDirection:
                    self.sensationType = Sensation.SensationType.HearDirection
                    if len(params) >= 3:
                        self.hearDirection = float(params[2])
                        print str(self.hearDirection)
                elif sensationType == Sensation.SensationType.Azimuth:
                    self.sensationType = Sensation.SensationType.Azimuth
                    if len(params) >= 3:
                        self.azimuth = float(params[2])
                        print str(self.azimuth)
                elif sensationType == Sensation.SensationType.Acceleration:
                    self.sensationType = Sensation.SensationType.Acceleration
                    if len(params) >= 5:
                        self.accelerationX = float(params[2])
                        self.accelerationY = float(params[3])
                        self.accelerationZ = float(params[4])
                        print str(self.accelerationX) + ' ' + str(self.accelerationY) + ' ' + str(self.accelerationZ)
                elif sensationType == Sensation.SensationType.Observation:
                    self.sensationType = Sensation.SensationType.Observation
                    if len(params) >= 4:
                        self.observationDirection = float(params[2])
                        self.observationDistance = float(params[3])
                        print str(self.observationDirection) + ' ' + str(self.observationDistance)
                elif sensationType == Sensation.SensationType.Picture:
                    self.sensationType = Sensation.SensationType.Picture
                    if len(params) >= 3:
                        self.imageSize = int(params[2])
                        print str(self.imageSize)
                elif sensationType == Sensation.SensationType.Capability:
                    self.sensationType = Sensation.SensationType.Capability
                    if len(params) >= 3:
                        self.direction = params[2]
                        print str(self.direction)
                    if len(params) >= 4:
                        self.capabilities = params[3:]
                        print str(self.capabilities)
    
                elif sensationType == Sensation.SensationType.Stop:
                    self.sensationType = Sensation.SensationType.Stop
                elif sensationType == Sensation.SensationType.Who:
                    self.sensationType = Sensation.SensationType.Who
                else:
                    self.sensationType = Sensation.SensationType.Unknown
                print self.sensationType
            
    def __str__(self):
        if self.sensationType == Sensation.SensationType.Drive:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensationType == Sensation.SensationType.HearDirection:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.hearDirection)
        elif self.sensationType == Sensation.SensationType.Azimuth:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.azimuth)
        elif self.sensationType == Sensation.SensationType.Acceleration:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.accelerationX)+ ' ' + str(self.accelerationY) + ' ' + str(self.accelerationZ)
        elif self.sensationType == Sensation.SensationType.Observation:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.observationDirection)+ ' ' + str(self.observationDistance)
        elif self.sensationType == Sensation.SensationType.Picture:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.imageSize)
        elif self.sensationType == Sensation.SensationType.Capability:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.direction) +  ' ' + self.getStrCapabilities()
        elif self.sensationType == Sensation.SensationType.Stop:
            return str(self.number) + ' ' + self.sensationType
        elif self.sensationType == Sensation.SensationType.Who:
            return str(self.number) + ' ' + self.sensationType
        else:
            return str(self.number) + ' ' + self.sensationType

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
    def getCmageSize(self):
        return self.capabilities
    def setStrCapabilities(self, string):
        str_capabilities = string.split()
        self.capabilities=[]
        for capability in str_capabilities:
            self.capabilities.add(capability)
        self.capabilities = capabilities
    def getStrCapabilities(self):
        capabilities = ""
        for capability in self.capabilities:
            capabilities += ' ' + str(capability)
        return capabilities

        
if __name__ == '__main__':
    c=Sensation(string="12 D 0.97 0.56")
    print "str " + str(c)
    c=Sensation(string="13 S")
    print "str " + str(c)
    c=Sensation(string="13 W")
    print "str " + str(c)
    c=Sensation(string="14 H -0.75")
    print "str " + str(c)
    c=Sensation(string="15 A 0.75")
    print "str " + str(c)
    c=Sensation(string="15 O 0.75 3.75")
    print "str " + str(c)
    c=Sensation(string="16 P 12300")
    print "str " + str(c)
    c=Sensation(string="17 oho")
    print "str " + str(c)
    c=Sensation(string="hupsis oli")
    print "str " + str(c)
    
    c=Sensation(number=99, sensationType = 'D', leftPower = 0.77, rightPower = 0.55)
    print "D str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
    
    c=Sensation(number=100, sensationType = 'H', hearDirection = 0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=101, sensationType = 'A', azimuth = -0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=102, sensationType = 'G', accelerationX = -0.85, accelerationY = 2.33, accelerationZ = -0.085)
    print "G str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=103, sensationType = Sensation.SensationType.Observation, observationDirection= -0.85, observationDistance=-3.75)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=104, sensationType = 'C', direction = 'O', capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
    print "C str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
