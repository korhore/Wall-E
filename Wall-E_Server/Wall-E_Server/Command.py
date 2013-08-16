'''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''
def enum(**enums):
    return type('Enum', (), enums)

class Command(object):
    
    CommandTypes = enum(Drive='D', Stop='S', Who='W', Picture='P', Unknown='U')
    
    def __init__(self, string="",
                 number=-1, command = 'U', leftPower = 0.0, rightPower = 0.0, imageSize=0):
        self.number = number
        self.command = command
        self.leftPower = leftPower
        self.rightPower = rightPower
        self.imageSize = imageSize
        
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
                elif command == Command.CommandTypes.Picture:
                    self.command = Command.CommandTypes.Picture
                    if len(params) >= 3:
                        self.imageSize = int(params[2])
                        print str(self.imageSize)
    
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
        if self.command == Command.CommandTypes.Picture:
            return str(self.number) + ' ' + self.command + ' ' + str(self.imageSize)
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
    
    def setImageSize(self, imageSize):
        self.imageSize = imageSize
    def getImageSize(self):
        return self.imageSize

        
if __name__ == '__main__':
    c=Command(string="12 D 0.97 0.56")
    print "str " + str(c)
    c=Command(string="13 S")
    print "str " + str(c)
    c=Command(string="13 W")
    print "str " + str(c)
    c=Command(string="14 P 12300")
    print "str " + str(c)
    c=Command(string="18 oho")
    print "str " + str(c)
    c=Command(string="hupsis oli")
    print "str " + str(c)
    c=Command(number=99, command = 'D', leftPower = 0.77, rightPower = 0.55)
    print "str " + str(c)
    print "str(Command(str(c))) " + str(Command(str(c)))