'''
Created on Apr 28, 201

@author: reijo.korhonen@gmail.com

    config file is on level by sections, but we need three level by host
    - Direction
    - Menory
    - Capability
    
    Implementation sets these level in option names likes this
    in_sensory_drive = False
    
    Default configutation is False for all capabilities in all levels
    In 'LOCALHOST' sections localhost those capabilities can be set True
    that have hardware for those.
    
    Remote hosts can have their own capabilities and
    they have their own sections for them.

    
    
'''
import os
from configparser import ConfigParser
from configparser import MissingSectionHeaderError,NoSectionError,NoOptionError
from Sensation import Sensation
from _ast import Or

from Config import Config


class Capabilities():

    
    def __init__(self, bytes=None):
        if bytes == None:
            self.config = Config()
            bytes=self.config.toBytes()

        self.fromBytes(bytes=bytes)

    
    '''
    external or local host capabilities to given capability section
    section name is normally hosts ip-address as text, if given
    if section is not given, we get local capabilities
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
                    is_set=self.config.intToBool(bytes[i])
#                     if is_set:
#                         print (str(direction) + str(memory) + str(capability) + ': TRUE')
                    capabilitys[capability] = is_set
#                     print ('i ' + str(i) + ': ' + str(bytes[i]) + ' ' + str(is_set))
                    i=i+1

    '''
    external or local host capabilities to given capability section
    section name is normally hosts ip-address as text, if given
    if section is not given, we get local capabilities
    '''
    def hasCapanility(self, direction, memory, sensationType):
        return self.directions[direction][memory][sensationType]
 

if __name__ == '__main__':
    cwd = os.getcwd()
    print('cwd ' + cwd)

    capabilities = Capabilities()
    
    #test
    for direction, directionStr in Sensation.Directions.items():
        for memory, memoryStr in Sensation.Memorys.items():
            for capability, capabilityStr in Sensation.SensationTypes.items():
                is_set = capabilities.hasCapanility(direction, memory, capability)
                if is_set:
                    print (str(directionStr) + ' ' + str(memoryStr) + ' ' + str(capabilityStr) + ': True') # +\
                       #str(capabilities.hasCapanility(direction, memory, capability)))
    
 

