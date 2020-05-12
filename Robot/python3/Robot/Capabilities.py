'''
Created on 28.04.2018

@author: reijo.korhonen@gmail.com

Internal implementation of capabilities set on three levels
direction, memoryType, capability

Can be initialized from bytes, string, config or default config for localhost

    
    
'''
import sys
import os
from Sensation import Sensation
if 'Config' not in sys.modules:
    from Config import Config


class Capabilities():

    
    def __init__(self, string=None, bytes=None, config=None):
        if string is not None:
            self.fromString(string=string)
        else:            
            if bytes == None:
                if config is None:
                    self.config = Config()
                else:
                    self.config= config
                bytes=self.config.toBytes()
    
            self.fromBytes(bytes=bytes)

    
    '''
    Initiated from bytes
    '''
    def fromBytes(self, bytes=None):
        if bytes == None:
            bytes=self.config.toBytes()
        self.directions={}
        i=0
        # create three level dictionary about capabilitys by direction, by memoryType, by sensation type
        for direction, _ in Sensation.Directions.items():
            memorys={}
            self.directions[direction] = memorys
            for memoryType, _ in Sensation.MemoryTypes.items():
                capabilitys={}
                memorys[memoryType] = capabilitys
                for capability, _ in Sensation.SensationTypes.items():
                    is_set=Config.intToBool(b=bytes[i])
#                     if is_set:
#                         print (str(direction) + str(memoryType) + str(capability) + ': TRUE')
                    capabilitys[capability] = is_set
#                     print ('i ' + str(i) + ': ' + str(bytes[i]) + ' ' + str(is_set))
                    i=i+1
    '''
    Initiated from String
    '''
    def fromString(self, string=None):
        if string == None:
            string=self.config.toString()
        self.directions={}
        i=0
        # create three level dictionary about capabilitys by direction, by memoryType, by sensation type
        for direction, _ in Sensation.Directions.items():
            memorys={}
            self.directions[direction] = memorys
            for memoryType, _ in Sensation.MemoryTypes.items():
                capabilitys={}
                memorys[memoryType] = capabilitys
                for capability, _ in Sensation.SensationTypes.items():
                    is_set=Config.charToBool(string[i])
#                     if is_set:
#                         print (str(direction) + str(memoryType) + str(capability) + ': TRUE')
                    capabilitys[capability] = is_set
#                     print ('i ' + str(i) + ': ' + str(bytes[i]) + ' ' + str(is_set))
                    i=i+1

    '''
    Getter to get if single capability is set
    in location this Capabilities set has
    '''
    def hasCapability(self, direction, memoryType, sensationType, locations):
        if self.isInLocations(locations):
            return self.directions[direction][memoryType][sensationType]
        return False
    
    '''
    Is one or more location is one of this Capabilitues set location
    in location this Capabilities set has
    '''
    def isInLocations(self, locations):
        if len(locations) == 0: # no location requirement
            return True
        for location in locations:
            if location in self.getLocations():
                return True
        return False
 
    '''
    Setter to get if single capability is set
    '''
    def setCapability(self, direction, memoryType, sensationType, is_set):
        self.directions[direction][memoryType][sensationType] = is_set
        
        
'''
test
'''
def test(name, capabilities):
    for direction, directionStr in Sensation.Directions.items():
        for memoryType, memoryStr in Sensation.MemoryTypes.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                is_set = capabilities.hasCapability(direction, memoryType, capability, [])
                if is_set:
                    print (name + ": " + str(directionStr) + ' ' + str(memoryStr) + ' ' + str(capabilityStr) + ': True')



if __name__ == '__main__':
    cwd = os.getcwd()
    print('cwd ' + cwd)

    capabilities = Capabilities()
    
    #test
    test(name="default", capabilities=capabilities)
 
    # set all True 
    print ("Set all True")
    for direction, directionStr in Sensation.Directions.items():
        for memoryType, memoryStr in Sensation.MemoryTypes.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapability(direction, memoryType, capability, True)
    test(name="Set all True", capabilities=capabilities)

     # set all False 
    print ("Set all False")
    for direction, directionStr in Sensation.Directions.items():
        for memoryType, memoryStr in Sensation.MemoryTypes.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapability(direction, memoryType, capability, False)
    test(name="Set all False", capabilities=capabilities)

    config=Config()
    capabilities=Capabilities(config=config)
    test("default config", capabilities)
    
    bytes=config.toBytes(section="bytes")                
    capabilities=Capabilities(bytes=bytes)
    test("bytes", capabilities)

    string=config.toString()                
    capabilities = Capabilities(string=string)
    test("string", capabilities)

