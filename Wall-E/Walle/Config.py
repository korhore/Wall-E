'''
Created on Apr 28, 2014

@author: reijo


    Configuration file looks like this
    [DEFAULT]
        [Direction]
            [In]
                [Memory]
                    [Sensory]
                         Drive=False
                         Stop=False}
                    [Working]
                        Drive=False
                        Stop=False}
                    [LongTerm]
                        Drive=False
                        Stop=False}
            [Out]
                [Memory]
                    [Sensory]
                         Drive=False
                         Stop=False}
                    [Working]
                        Drive=False
                        Stop=False}
                    [LongTerm]
                        Drive=False
                        Stop=False}
 
    Make dicts with keys, values of Drextions, Memory, Capabilities
    so we get this kind one level section,
    Sections will be  hosts available, but will we need more than localhost,
    Other hosts can be got by Sensations.
    
    In_Sensory_Drive=False
    In_Sensory_Stop=False

    In_Working_Drive=False
    In_Working_Stop=False
   
    In_LongTerm_Drive=False
    In_LongTerm_Stop=False
    
    [Microphones]
    left = Set
    right = Set_1
    calibrating_zero = 0.131151809437
    calibrating_factor = 3.54444800648
    
    
'''
import os
#import sys
from configparser import ConfigParser
from configparser import MissingSectionHeaderError,NoSectionError,NoOptionError
from Sensation import Sensation
from _ast import Or

# TODO relative
CONFIG_FILE_PATH = '/home/reijo/git/Wall-E/Wall-E/Walle/etc/Walle.cfg'

class Config(ConfigParser):

    # Configuratioon Section and Option names
    Capabilities =  'Capabilities' 
    Memory =        'Memory'
    Microphones = 'Microphones'   
    left = 'left'
    right = 'right'
    calibrating_factor = 'calibrating_factor'
    calibrating_zero = 'calibrating_zero'

    DEFAULT_SECTION="DEFAULT"

    TRUE="True"
    FALSE="False"
    
    TRUE_ENCODED=b'\x01'
    FALSE_ENCODED=b'\x00'
     
    def __init__(self):
        ConfigParser.__init__(self)
        
#        cwd = os.getcwd()
#        print("cwd " + cwd)

        #Read config        
        self.read(CONFIG_FILE_PATH)
 
        # If we don't have default section or Capsbilities section make it.
        # It will be a template if some capabilities will be set on                          
        if not self.has_section(Config.DEFAULT_SECTION) or \
           not self.has_section(Config.Capabilities):
                self.createDefaultSection()
 
        # if we have microphones, read config for them    
        if self.canHear():   
            try:                
                left_card = self.get(Config.Microphones, Config.left)
                if left_card == None:
                    print('left_card == None')
                    self.canRun = False
                right_card = self.get(Config.Microphones, Config.right)
                if right_card == None:
                    print('right_card == None')
                    self.canRun = False
                try:
                    self.calibrating_zero = self.getfloat(Config.Microphones, Config.calibrating_zero)
                except self.NoOptionError:
                    self.calibrating_zero = 0.0
                try:
                    self.calibrating_factor = self.getfloat(Config.Microphones, Config.calibrating_factor)
                except self.NoOptionError:
                    self.calibrating_factor = 1.0
                    
            except MissingSectionHeaderError as e:
                    print('Microphones  configparser.MissingSectionHeaderError ' + str(e))
                    self.canRun = False
            except NoSectionError as e:
                    print('Microphones  configparser.NoSectionError ' + str(e))
                    self.canRun = False
            except NoOptionError as e:
                    print('Microphones  configparser.NoOptionError ' + str(e))
                    self.canRun = False
            except Exception as e:
                    print('Microphones configparser exception ' + str(e))
                    self.canRun = False

    '''
    localhost capaliliys to bytes
    '''
    def toBytes(self):
        b=b''
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    #iscab=self.getboolean(Config.Capabilities, option)
                    #b_iscab= bytes(iscab,'utf-8')
                    #b += bytes(self.getboolean(Config.Capabilities, option))
                    b2 = b + self.boolToByte(self.getboolean(Config.Capabilities, option))
                    b=b2
        print("toBytes " + str(len(b)))
        return b
 
     
    '''
    Helper function to convert boolean to one byte
    '''
    def boolToByte(self, boolean):
        if boolean:
            ret = Config.TRUE_ENCODED
        else:
            ret = Config.FALSE_ENCODED
        return ret
 
    '''
    Helper function to convert one byte to boolean
    '''
    def byteToBool(self, b):
        if b == Config.TRUE_ENCODED:
            return True
        return False

    '''
    Helper function to convert boolean to config file String
    '''
    def boooleanToString(self, bool):
        if bool:
            return Config.TRUE
        
        return Config.FALSE

    
    '''
    external or local host capabilities to given capability section
    section name is normally hosts ip-address as text, if given
    if section is not given, we get local capabilities
    '''
    def fromBytes(self, b, section=Capabilities):
        print("fromBytes " + str(len(b)))
        i=0
        changes=False
        if not self.has_section(section):
            try:
                self.add_section(section)
                changes=True

            except MissingSectionHeaderError as e:
                    print('self.add_section ' + section + ' configparser.MissingSectionHeaderError ' + str(e))
            except NoSectionError as e:
                    print('eslf.add_section ' + section + ' configparser.NoSectionError ' + str(e))
            except NoOptionError as e:
                    print('self.add_section ' + section + ' configparser.NoOptionError ' + str(e))
            except Exception as e:
                    print('self.add_section ' + section + ' exception ' + str(e))
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    is_set=self.byteToBool(b[i])
                    try:
                        if not self.has_option(section, option):
                            self.set(section, option, self.boooleanToString(is_set))
                            changes=True
                        else:
                            was_set = self.getboolean(section, option)
                            if is_set != was_set:
                                self.set(section, option, self.boooleanToString(is_set))
                                changes=True
                    except Exception as e:
                        print('self.set(' + section+', option, self.FALSE) exception ' + str(e))

        if changes:
            try:
                configfile = open(CONFIG_FILE_PATH, 'w')
                self.write(configfile)
                configfile.close()
            except Exception as e:
                print('self.write(configfile) ' + str(e))

    def createDefaultSection(self):
        changes=False
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    try:
                        if not self.has_option(self.DEFAULT_SECTION, option):
                            self.set(self.DEFAULT_SECTION, option, self.FALSE)
                            changes=True
                    except Exception as e:
                        print('self.set(self.DEFAULT_SECTION, option, self.FALSE) exception ' + str(e))
                        
        if not self.has_section(Config.Capabilities):
            try:
                self.add_section(Config.Capabilities)
                changes=True

            except MissingSectionHeaderError as e:
                    print('self.add_section configparser.MissingSectionHeaderError ' + str(e))
            except NoSectionError as e:
                    print('eslf.add_section configparser.NoSectionError ' + str(e))
            except NoOptionError as e:
                    print('self.add_section configparser.NoOptionError ' + str(e))
            except Exception as e:
                    print('self.add_section exception ' + str(e))

        if changes:
            try:
                configfile = open(CONFIG_FILE_PATH, 'w')
                self.write(configfile)
                configfile.close()
            except Exception as e:
                print('self.write(configfile) ' + str(e))
                
        try:
            can=self.canHear()
            print('self.canHear() ' + str(can))
        except Exception as e:
            print('self.canHear() ' + str(e))
            
        try:
            can=self.canMove()
            print('self.canMove() ' + str(can))
        except Exception as e:
            print('self.canMove() ' + str(e))
        try:
            can=self.canSee()
            print('self.canSee() ' + str(can))
        except Exception as e:
            print('self.canSee() ' + str(e))

 
    # what capabilities we have TODO
    def getOptionName(self, directionStr,memoryStr,capabilityStr):
        return directionStr+'_'+memoryStr+'_'+capabilityStr

    def hasCapability(self, directionStr,memoryStr,capabilityStr, section=Capabilities):
        option=self.getOptionName(directionStr,memoryStr,capabilityStr)
        return self.getboolean(section, option)

             
    def canHear(self):
        return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                  Sensation.getMemoryString(Sensation.Memory.Sensory),
                                  Sensation.getSensationTypeString(Sensation.SensationType.HearDirection))
    
    def canMove(self):
       return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.Drive))

    def canSee(self):
       return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.PictureFilePath)) \
                                 and \
              self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.PictureData))


if __name__ == "__main__":
    config = Config()
    b=config.toBytes()
    config.fromBytes(b=b,section="test")
 

