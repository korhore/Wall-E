'''
Created on 28.04.2018

@author: reijo.korhonen@gmail.com

Internal implementation of capabilities set on three levels
direction, memory, capability

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
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        for direction, _ in Sensation.Directions.items():
            memorys={}
            self.directions[direction] = memorys
            for memory, _ in Sensation.Memorys.items():
                capabilitys={}
                memorys[memory] = capabilitys
                for capability, _ in Sensation.SensationTypes.items():
                    is_set=Config.intToBool(b=bytes[i])
#                     if is_set:
#                         print (str(direction) + str(memory) + str(capability) + ': TRUE')
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
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        for direction, _ in Sensation.Directions.items():
            memorys={}
            self.directions[direction] = memorys
            for memory, _ in Sensation.Memorys.items():
                capabilitys={}
                memorys[memory] = capabilitys
                for capability, _ in Sensation.SensationTypes.items():
                    is_set=Config.charToBool(string[i])
#                     if is_set:
#                         print (str(direction) + str(memory) + str(capability) + ': TRUE')
                    capabilitys[capability] = is_set
#                     print ('i ' + str(i) + ': ' + str(bytes[i]) + ' ' + str(is_set))
                    i=i+1

    '''
    Getter to get if single capability is set
    '''
    def hasCapanility(self, direction, memory, sensationType):
        return self.directions[direction][memory][sensationType]
 
    '''
    Setter to get if single capability is set
    '''
    def setCapanility(self, direction, memory, sensationType, is_set):
        self.directions[direction][memory][sensationType] = is_set
        
        
'''
test
'''
def test(name, capabilities):
    for direction, directionStr in Sensation.Directions.items():
        for memory, memoryStr in Sensation.Memorys.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                is_set = capabilities.hasCapanility(direction, memory, capability)
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
        for memory, memoryStr in Sensation.Memorys.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapanility(direction, memory, capability, True)
    test(name="Set all True", capabilities=capabilities)

     # set all False 
    print ("Set all False")
    for direction, directionStr in Sensation.Directions.items():
        for memory, memoryStr in Sensation.Memorys.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapanility(direction, memory, capability, False)
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
