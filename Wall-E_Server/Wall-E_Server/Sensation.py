'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''
def enum(**enums):
    return type('Enum', (), enums)

class Sensation(object):
    
    SensationTypes = enum(Drive='D', Stop='S', Who='W', Hear='H', Azimuth='A', Picture='P', Capability='C', Unknown='U')
    Direction = enum(Input='I', Output='O')
   
    def __init__(self, string="",
                 number=-1, sensationType = 'U', leftPower = 0.0, rightPower = 0.0, hear = 0.0, azimuth = 0.0, imageSize=0,
                 direction='I', capabilities = []):
        self.number = number
        self.sensationType = sensationType
        self.leftPower = leftPower
        self.rightPower = rightPower
        self.hear = hear
        self.azimuth = azimuth
        self.imageSize = imageSize
        self.direction = direction
        self.capabilities = capabilities
       
        params = string.split()
        print params
        if len(params) >= 1:
            try:
                self.number = int(params[0])
            except (ValueError):
                self.sensationType = Sensation.SensationTypes.Unknown
                return
                
            print self.number
            if len(params) >= 2:
                sensationType = params[1]
                if sensationType == Sensation.SensationTypes.Drive:
                    self.sensationType = Sensation.SensationTypes.Drive
                    if len(params) >= 3:
                        self.leftPower = float(params[2])
                        print str(self.leftPower)
                    if len(params) >= 4:
                        self.rightPower = float(params[3])
                        print str(self.rightPower)
                elif sensationType == Sensation.SensationTypes.Hear:
                    self.sensationType = Sensation.SensationTypes.Hear
                    if len(params) >= 3:
                        self.hear = float(params[2])
                        print str(self.hear)
                elif sensationType == Sensation.SensationTypes.Azimuth:
                    self.sensationType = Sensation.SensationTypes.Azimuth
                    if len(params) >= 3:
                        self.azimuth = float(params[2])
                        print str(self.azimuth)
                elif sensationType == Sensation.SensationTypes.Picture:
                    self.sensationType = Sensation.SensationTypes.Picture
                    if len(params) >= 3:
                        self.imageSize = int(params[2])
                        print str(self.imageSize)
                elif sensationType == Sensation.SensationTypes.Capability:
                    self.sensationType = Sensation.SensationTypes.Capability
                    if len(params) >= 3:
                        self.direction = params[2]
                        print str(self.direction)
                    if len(params) >= 4:
                        self.capabilities = params[3:]
                        print str(self.capabilities)
    
                elif sensationType == Sensation.SensationTypes.Stop:
                    self.sensationType = Sensation.SensationTypes.Stop
                elif sensationType == Sensation.SensationTypes.Who:
                    self.sensationType = Sensation.SensationTypes.Who
                else:
                    self.sensationType = Sensation.SensationTypes.Unknown
                print self.sensationType
            
    def __str__(self):
        if self.sensationType == Sensation.SensationTypes.Drive:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensationType == Sensation.SensationTypes.Hear:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.hear)
        elif self.sensationType == Sensation.SensationTypes.Azimuth:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.azimuth)
        elif self.sensationType == Sensation.SensationTypes.Picture:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.imageSize)
        elif self.sensationType == Sensation.SensationTypes.Capability:
            return str(self.number) + ' ' + self.sensationType + ' ' + str(self.direction) +  ' ' + self.getStrCapabilities()
        elif self.sensationType == Sensation.SensationTypes.Stop:
            return str(self.number) + ' ' + self.sensationType
        elif self.sensationType == Sensation.SensationTypes.Who:
            return str(self.number) + ' ' + self.sensationType
        else:
            return str(self.number) + ' ' + self.sensationType

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
    
    def setHear(self, hear):
        self.hear = hear
    def getHear(self):
        return self.hear

    def setAzimuth(self, azimuth):
        self.azimuth = azimuth
    def getAzimuth(self):
        return self.azimuth

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
    c=Sensation(string="16 P 12300")
    print "str " + str(c)
    c=Sensation(string="17 oho")
    print "str " + str(c)
    c=Sensation(string="hupsis oli")
    print "str " + str(c)
    
    c=Sensation(number=99, sensationType = 'D', leftPower = 0.77, rightPower = 0.55)
    print "D str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
    
    c=Sensation(number=100, sensationType = 'H', hear = 0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=101, sensationType = 'A', azimuth = -0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=102, sensationType = 'C', direction = 'O', capabilities = [Sensation.SensationTypes.Drive, Sensation.SensationTypes.Hear, Sensation.SensationTypes.Azimuth])
    print "C str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
