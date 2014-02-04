'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''
def enum(**enums):
    return type('Enum', (), enums)

class Command(object):
    
    CommandTypes = enum(Drive='D', Stop='S', Who='W', Azimuth='A', Picture='P', Capability='C', Unknown='U')
    Direction = enum(Input='I', Output='O')
   
    def __init__(self, string="",
                 number=-1, command = 'U', leftPower = 0.0, rightPower = 0.0, azimuth = 0.0, imageSize=0,
                 direction='I', capabilities = []):
        self.number = number
        self.command = command
        self.leftPower = leftPower
        self.rightPower = rightPower
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
                self.command = Command.CommandTypes.Unknown
                return
                
            print self.number
            if len(params) >= 2:
                command = params[1]
                if command == Command.CommandTypes.Drive:
                    self.command = Command.CommandTypes.Drive
                    if len(params) >= 3:
                        self.leftPower = float(params[2])
                        print str(self.leftPower)
                    if len(params) >= 4:
                        self.rightPower = float(params[3])
                        print str(self.rightPower)
                elif command == Command.CommandTypes.Azimuth:
                    self.command = Command.CommandTypes.Azimuth
                    if len(params) >= 3:
                        self.azimuth = float(params[2])
                        print str(self.azimuth)
                elif command == Command.CommandTypes.Picture:
                    self.command = Command.CommandTypes.Picture
                    if len(params) >= 3:
                        self.imageSize = int(params[2])
                        print str(self.imageSize)
                elif command == Command.CommandTypes.Capability:
                    self.command = Command.CommandTypes.Capability
                    if len(params) >= 3:
                        self.direction = params[2]
                        print str(self.direction)
                    if len(params) >= 4:
                        self.capabilities = params[3:]
                        print str(self.capabilities)
    
                elif command == Command.CommandTypes.Stop:
                    self.command = Command.CommandTypes.Stop
                elif command == Command.CommandTypes.Who:
                    self.command = Command.CommandTypes.Who
                else:
                    self.command = Command.CommandTypes.Unknown
                print self.command
            
    def __str__(self):
        if self.command == Command.CommandTypes.Drive:
            return str(self.number) + ' ' + self.command + ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.command == Command.CommandTypes.Azimuth:
            return str(self.number) + ' ' + self.command + ' ' + str(self.azimuth)
        elif self.command == Command.CommandTypes.Picture:
            return str(self.number) + ' ' + self.command + ' ' + str(self.imageSize)
        elif self.command == Command.CommandTypes.Capability:
            return str(self.number) + ' ' + self.command + ' ' + str(self.direction) +  ' ' + self.getStrCapabilities()
        elif self.command == Command.CommandTypes.Stop:
            return str(self.number) + ' ' + self.command
        elif self.command == Command.CommandTypes.Who:
            return str(self.number) + ' ' + self.command
        else:
            return str(self.number) + ' ' + self.command

    def setNumber(self, number):
        self.number = number
    def getNumber(self):
        return self.number
 
    def setCommand(self, command):
        self.command = command
    def getCommand(self):
        return self.command
       
    def setLeftPower(self, leftPower):
        self.leftPower = leftPower
    def getLeftPower(self):
        return self.leftPower
        
    def setRightPower(self, rightPower):
        self.rightPower = rightPower
    def getRightPower(self):
        return self.rightPower
    
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
    c=Command(string="12 D 0.97 0.56")
    print "str " + str(c)
    c=Command(string="13 S")
    print "str " + str(c)
    c=Command(string="13 W")
    print "str " + str(c)
    c=Command(string="14 A 0.75")
    print "str " + str(c)
    c=Command(string="15 P 12300")
    print "str " + str(c)
    c=Command(string="18 oho")
    print "str " + str(c)
    c=Command(string="hupsis oli")
    print "str " + str(c)
    
    c=Command(number=99, command = 'D', leftPower = 0.77, rightPower = 0.55)
    print "D str " + str(c)
    print "str(Command(str(c))) " + str(Command(string=str(c)))
    
    c=Command(number=100, command = 'A', azimuth = -0.85)
    print "A str " + str(c)
    print "str(Command(str(c))) " + str(Command(string=str(c)))

    c=Command(number=110, command = 'C', direction = 'O', capabilities = [Command.CommandTypes.Drive, Command.CommandTypes.Azimuth])
    print "C str " + str(c)
    print "str(Command(str(c))) " + str(Command(string=str(c)))
