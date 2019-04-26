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

CONFIG_FILE_PATH = 'etc/Walle.cfg'

class Config(ConfigParser):

    # Configuratioon Section and Option names
    LOCALHOST =         'localhost' 
    MEMORY =            'memory'
#    Microphones =       'MICROPHONES' 
    HOSTS =             'hosts' 
    WHO =               'who' 
    MICROPHONE_LEFT =              'microphone_left'
    MICROPHONE_RIGHT =             'microphone_right'
    MICROPHONE_CALIBRATING_FACTOR ='microphone_calibrating_factor'
    MICROPHONE_CALIBRATING_ZERO =  'microphone_calibrating_zero'

    DEFAULT_SECTION =   'DEFAULT'

    TRUE=               'True'
    FALSE=              'False'
    NONE=               'None'
    EMPTY=              ''
    ZERO=               '0.0'
  
    TRUE_ENCODED =      b'\x01'
    FALSE_ENCODED =     b'\x00'
     
    def __init__(self):
        ConfigParser.__init__(self)
        
        #Read config        
        self.read(CONFIG_FILE_PATH)
 
        # If we don't have default section or Capsbilities section make it.
        # It will be a template if some capabilities will be set on                          
        if not self.has_section(Config.DEFAULT_SECTION) or \
           not self.has_section(Config.LOCALHOST):
                self.createDefaultSection()
 
        # if we have microphones, read config for them    
        if self.canHear():   
            try:                
                left_card = self.get(Config.LOCALHOST, Config.LEFT)
                if left_card == None:
                    print('left_card == None')
                    self.canRun = False
                right_card = self.get(Config.LOCALHOST, Config.RIGHT)
                if right_card == None:
                    print('right_card == None')
                    self.canRun = False
                try:
                    self.calibrating_zero = self.getfloat(Config.LOCALHOST, Config.MICROPHONE_CALIBRATING_ZERO)
                except self.NoOptionError:
                    self.calibrating_zero = 0.0
                try:
                    self.calibrating_factor = self.getfloat(Config.LOCALHOST, Config.MICROPHONE_CALIBRATING_FACTOR)
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
    TODO to its own class
    '''
    def toBytes(self, section=LOCALHOST):
        b=b''
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    #iscab=self.getboolean(Config.LOCALHOST, option)
                    #b_iscab= bytes(iscab,'utf-8')
                    #b += bytes(self.getboolean(Config.LOCALHOST, option))
                    is_set=self.getboolean(section, option)
#                     if is_set:
#                         print('toBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    b2 = b + self.boolToByte(is_set)
                    b=b2
#         print('toBytes section ' + section + ' '+ str(len(b)))
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
    Helper function to convert int to boolean
    '''
    def intToBool(self, b):
        return b != 0

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
    def fromBytes(self, b, section=LOCALHOST):
#         print('fromBytes ' + str(len(b)))
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
                        if not self.has_option(Config.DEFAULT_SECTION, option):
                            self.set(self.DEFAULT_SECTION, option, self.FALSE)
                            changes=True
                    except Exception as e:
                        print('self.set(self.DEFAULT_SECTION, option, self.FALSE) exception ' + str(e))
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT):
                self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT, Config.Config.EMPTY) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.WHO):
                self.set(Config.DEFAULT_SECTION,Config.WHO, Config.LOCALHOST)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.WHO, Config.Config.WHO) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.HOSTS):
                self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.LOCALHOST, Config.Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE_RIGHT):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_RIGHT, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_RIGHT, Config.Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_ZERO):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_ZERO, Config.ZERO)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_ZERO, Config.ZERO) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_FACTOR):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_FACTOR, Config.ZERO)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_FACTOR, Config.ZERO) exception ' + str(e))

        
        
        if not self.has_section(Config.LOCALHOST):
            try:
                self.add_section(Config.LOCALHOST)
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
                
#         try:
#             can=self.canHear()
#             print('self.canHear() ' + str(can))
#         except Exception as e:
#             print('self.canHear() ' + str(e))
#             
#         try:
#             can=self.canMove()
#             print('self.canMove() ' + str(can))
#         except Exception as e:
#             print('self.canMove() ' + str(e))
#         try:
#             can=self.canSee()
#             print('self.canSee() ' + str(can))
#         except Exception as e:
#             print('self.canSee() ' + str(e))

 
    # what capabilities we have TODO
    def getOptionName(self, directionStr,memoryStr,capabilityStr):
        return directionStr+'_'+memoryStr+'_'+capabilityStr

    def hasCapability(self, directionStr,memoryStr,capabilityStr, section=LOCALHOST):
        option=self.getOptionName(directionStr,memoryStr,capabilityStr)
        return self.getboolean(section, option)

             
    def canHear(self, host=LOCALHOST):
        return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                  Sensation.getMemoryString(Sensation.Memory.Sensory),
                                  Sensation.getSensationTypeString(Sensation.SensationType.HearDirection),
                                  section=host)
    
    def canMove(self, host=LOCALHOST):
       return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.Drive),
                                 section=host)

    def canSee(self, host=LOCALHOST):
       return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.ImageFilePath),
                                 section=host) \
                                 and \
              self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.PictureData),
                                 section=host)

# TODO microphones, different memory levels

if __name__ == '__main__':
    cwd = os.getcwd()
    print('cwd ' + cwd)

    config = Config()
    b=config.toBytes()
    config.fromBytes(b=b,section='test')
 

