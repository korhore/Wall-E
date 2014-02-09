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
                 number=-1, sensation = 'U', leftPower = 0.0, rightPower = 0.0, hear = 0.0, azimuth = 0.0, imageSize=0,
                 direction='I', capabilities = []):
        self.number = number
        self.sensation = sensation
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
                self.sensation = Sensation.SensationTypes.Unknown
                return
                
            print self.number
            if len(params) >= 2:
                sensation = params[1]
                if sensation == Sensation.SensationTypes.Drive:
                    self.sensation = Sensation.SensationTypes.Drive
                    if len(params) >= 3:
                        self.leftPower = float(params[2])
                        print str(self.leftPower)
                    if len(params) >= 4:
                        self.rightPower = float(params[3])
                        print str(self.rightPower)
                elif sensation == Sensation.SensationTypes.Hear:
                    self.sensation = Sensation.SensationTypes.Hear
                    if len(params) >= 3:
                        self.hear = float(params[2])
                        print str(self.hear)
                elif sensation == Sensation.SensationTypes.Azimuth:
                    self.sensation = Sensation.SensationTypes.Azimuth
                    if len(params) >= 3:
                        self.azimuth = float(params[2])
                        print str(self.azimuth)
                elif sensation == Sensation.SensationTypes.Picture:
                    self.sensation = Sensation.SensationTypes.Picture
                    if len(params) >= 3:
                        self.imageSize = int(params[2])
                        print str(self.imageSize)
                elif sensation == Sensation.SensationTypes.Capability:
                    self.sensation = Sensation.SensationTypes.Capability
                    if len(params) >= 3:
                        self.direction = params[2]
                        print str(self.direction)
                    if len(params) >= 4:
                        self.capabilities = params[3:]
                        print str(self.capabilities)
    
                elif sensation == Sensation.SensationTypes.Stop:
                    self.sensation = Sensation.SensationTypes.Stop
                elif sensation == Sensation.SensationTypes.Who:
                    self.sensation = Sensation.SensationTypes.Who
                else:
                    self.sensation = Sensation.SensationTypes.Unknown
                print self.sensation
            
    def __str__(self):
        if self.sensation == Sensation.SensationTypes.Drive:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensation == Sensation.SensationTypes.Hear:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.hear)
        elif self.sensation == Sensation.SensationTypes.Azimuth:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.azimuth)
        elif self.sensation == Sensation.SensationTypes.Picture:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.imageSize)
        elif self.sensation == Sensation.SensationTypes.Capability:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.direction) +  ' ' + self.getStrCapabilities()
        elif self.sensation == Sensation.SensationTypes.Stop:
            return str(self.number) + ' ' + self.sensation
        elif self.sensation == Sensation.SensationTypes.Who:
            return str(self.number) + ' ' + self.sensation
        else:
            return str(self.number) + ' ' + self.sensation

    def setNumber(self, number):
        self.number = number
    def getNumber(self):
        return self.number
 
    def setSensation(self, sensation):
        self.sensation = sensation
    def getSensation(self):
        return self.sensation
       
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
    
    c=Sensation(number=99, sensation = 'D', leftPower = 0.77, rightPower = 0.55)
    print "D str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
    
    c=Sensation(number=100, sensation = 'H', hear = 0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=101, sensation = 'A', azimuth = -0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=102, sensation = 'C', direction = 'O', capabilities = [Sensation.SensationTypes.Drive, Sensation.SensationTypes.Hear, Sensation.SensationTypes.Azimuth])
    print "C str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
