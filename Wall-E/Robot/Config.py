'''
Created on 28.042019

@author: reijo.korhonen@gmail.com

Config

    config file is on level by sections, but we need three level by host
    - Direction
    - Memory
    - Capability
    
    Implementation sets these level in option names likes this
    in_sensory_drive = False
    
    Default configutation is False for all capabilities in all levels
    In 'LOCALHOST' sections localhost those capabilities can be set True
    that have hardware for those.
    
    Remote hosts can have their own capabilities and
    they have their own sections for them.

    
    
Capabilities

Internal implementation of capabilities set on three levels
direction, memory, capability

Can be initialized from bytes, string, config or default config for localhost

    
    
'''

import sys
import os
from configparser import ConfigParser
from configparser import MissingSectionHeaderError,NoSectionError,NoOptionError
from Sensation import Sensation

class Config(ConfigParser):

    CONFIG_FILE_PATH = 'etc/Robot.cfg'
    
    # Configuratioon Section and Option names
    LOCALHOST =         'localhost' 
    MEMORY =            'memory'
#    Microphones =       'MICROPHONES' 
    HOSTS =             'hosts' 
    WHO =               'Who' 
    WALLE =             'Wall-E'
    KIND =              "Kind"
    INSTANCE =          "Instance"
    VIRTUALINSTANCES =  "Virtualinstances"
    SUBINSTANCES =      "Subinstances"
    IDENTITYS =         "Identitys"

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
    DEFAULT_SUBINSTANCES=  'Seeing Hearing Moving'
  
    TRUE_ENCODED =      b'\x01'
    FALSE_ENCODED =     b'\x00'
    
    TRUE_CHAR =         'T'
    FALSE_CHAR =        'F'
     
    def __init__(self, config_file_path=CONFIG_FILE_PATH, level=0):
        ConfigParser.__init__(self)
        self.config_file_path = config_file_path
        self.level=level+1
        print("Config level " + str(self.level) + ' ' + self.config_file_path)
        
        #Read config        
        self.read(self.config_file_path)
 
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
 
        # handle identitys
        if not os.path.exists(self.IDENTITYS):
            os.makedirs(self.IDENTITYS)
        for kind, kindstr in Sensation.Kinds.items():
            dir = self.getIdentityDirPath(kind)
            if not os.path.exists(dir):
                os.makedirs(dir)
                    
         # for one level
        if self.level <= 1:
            # handle subInstances (senses, muscles)
            self.handleSubInstances(is_virtualInstance=False)

            # handle virtual instances
            if not os.path.exists(self.VIRTUALINSTANCES):
                os.makedirs(self.VIRTUALINSTANCES)
            self.handleSubInstances(is_virtualInstance=True)

                     
                    
                    
    def handleSubInstances(self, is_virtualInstance):
        if is_virtualInstance:
            instances=self.getVirtualInstances()
        else:
            instances=self.getSubInstances()

        # relational subdirectory for virtual instance
        for instance in instances:
            print('Handle  instance ' + instance)
            if is_virtualInstance:
                directory = self.VIRTUALINSTANCES+'/'+instance
            else:
                directory = instance
            if not os.path.exists(directory):
                print('os.makedirs ' + directory)
                os.makedirs(directory)
            config_file_path=directory + '/' + Config.CONFIG_FILE_PATH
            etc_directory = directory +'/etc'
            
            # relational subdirectory for virtual instance
            if not os.path.exists(etc_directory):
                print('os.makedirs ' + etc_directory)
                os.makedirs(etc_directory)
            #finallu create or update default config file for virtual instance 
            print('Config(' + config_file_path +')')
            # TODO Here we should make onlt onle level morem because otherwise we get
            #endless loop
            config = Config(config_file_path=config_file_path, level=self.level)
           # finally set default that this is virtual instance
            changes = False
            if is_virtualInstance:                
                instances=self.getSubInstances()
                try:
                    instance = config.get(Config.DEFAULT_SECTION, Config.INSTANCE)
                    if instance != Sensation.VIRTUAL:          
                        config.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL)
                        changes=True
                except Exception as e:
                        print('config.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL) exception ' + str(e))
            if changes:
                try:
                    configfile = open(config_file_path, 'w')
                    config.write(configfile)
                    configfile.close()
                except Exception as e:
                    print('config.write(configfile) ' + str(e))

                    
    def getIdentityDirPath(self, kind):
        return self.IDENTITYS +'/'+ Sensation.Kinds[kind]

                
    def getVirtualinstanceConfigFilePath(self, virtualinstance):
        return self.VIRTUALINSTANCES +'/'+virtualinstance + '/' + Config.CONFIG_FILE_PATH
        
    def getSubinstanceConfigFilePath(self, instance):
        return instance + '/' + Config.CONFIG_FILE_PATH

                
            

    '''
    localhost capaliliys to bytes
    '''
    def toBytes(self, section=LOCALHOST):
        b=b''
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    is_set=self.getboolean(section, option)
#                    if is_set:
#                         print('toBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    b = b + Config.boolToByte(is_set)
#         print('toBytes section ' + section + ' '+ str(len(b)))
        return b
 
    '''
    localhost capaliliys to String
    '''
    def toString(self, section=LOCALHOST):
        string=''
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    is_set=self.getboolean(section, option)
#                    if is_set:
#                         print('toString ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    string = string + Config.boolToChar(is_set)
        return string
    
    '''
    Helper function to convert boolean to one byte
    '''
    def boolToByte(boolean):
        if boolean:
            ret = Config.TRUE_ENCODED
        else:
            ret = Config.FALSE_ENCODED
        return ret
 
    '''
    Helper function to convert one byte to boolean
    '''
    def byteToBool(b):
        if b == Config.TRUE_ENCODED:
            return True
        return False

    '''
    Helper function to convert int to boolean
    '''
    def intToBool(b):
        return b != 0

    '''
    Helper function to convert boolean to config file String
    '''
    def boolToString(bool):
        if bool:
            return Config.TRUE
        
        return Config.FALSE
    
    '''
    Helper function to convert boolean to one char
    '''
    def boolToChar(bool):
        if bool:
            ret = Config.TRUE_CHAR
        else:
            ret = Config.FALSE_CHAR
        return ret
 
    '''
    Helper function to convert one char to boolean
    '''
    def charToBool(b):
        if b == Config.TRUE_CHAR:
            return True
        return False


    
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
        # capabilities from b bytes to options
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    is_set=Config.intToBool(b[i])
                    i=i+1
#                    if is_set:
#                         print('fromBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    try:
                        if not self.has_option(section, option):
                            self.set(section, option, Config.boolToString(is_set))
                            changes=True
                        else:
                            was_set = self.getboolean(section, option)
                            if is_set != was_set:
                                self.set(section, option, Config.boolToString(is_set))
                                changes=True
                    except Exception as e:
                        print('self.set(' + section+', option, self.FALSE) exception ' + str(e))

        if changes:
            try:
                configfile = open(self.config_file_path, 'w')
                self.write(configfile)
                configfile.close()
            except Exception as e:
                print('self.write(configfile) ' + str(e))

    '''
    external or local host capabilities to given capability section
    section name is normally hosts ip-address as text, if given
    if section is not given, we get local capabilities
    '''
    def fromString(self, string, section=LOCALHOST):
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
        # capabilities from string to options
        for directionStr in Sensation.getDirectionStrings():
            for memoryStr in Sensation.getMemoryStrings():
                for capabilityStr in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(directionStr,memoryStr,capabilityStr)
                    is_set=Config.charToBool(string[i])
                    i=i+1
#                    if is_set:
#                         print('fromBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    try:
                        if not self.has_option(section, option):
                            self.set(section, option, Config.boolToString(is_set))
                            changes=True
                        else:
                            was_set = self.getboolean(section, option)
                            if is_set != was_set:
                                self.set(section, option, Config.boolToString(is_set))
                                changes=True
                    except Exception as e:
                        print('self.set(' + section+', option, self.FALSE) exception ' + str(e))

        if changes:
            try:
                configfile = open(self.config_file_path, 'w')
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
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT, Config.EMPTY) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.WHO):
                self.set(Config.DEFAULT_SECTION,Config.WHO, Sensation.WALLE)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.WHO, Config.WHO) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.KIND):
                self.set(Config.DEFAULT_SECTION,Config.KIND, Sensation.WALLE)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.KIND, Sensation.WALLE) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.INSTANCE):
                self.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.REAL)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.KIND, Sensation.WALLE) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.HOSTS):
                self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.SUBINSTANCES):
                if self.level == 1:
                    self.set(Config.DEFAULT_SECTION,Config.SUBINSTANCES, Config.DEFAULT_SUBINSTANCES)
                else:
                    self.set(Config.DEFAULT_SECTION,Config.SUBINSTANCES, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.VIRTUALINSTANCES):
                self.set(Config.DEFAULT_SECTION,Config.VIRTUALINSTANCES, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE_RIGHT):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_RIGHT, Config.EMPTY)
                changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_RIGHT, Config.EMPTY) exception ' + str(e))

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
                configfile = open(self.config_file_path, 'w')
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

             
    def getSubInstances(self, section=LOCALHOST):
        self.subInstances=[]
        subInstances = self.get(section=section, option=self.SUBINSTANCES)
        if subInstances != None and len(subInstances) > 0:
            self.subInstances = subInstances.split()
            
        return self.subInstances

    def getVirtualInstances(self, section=LOCALHOST):
        self.virtualInstances=[]
        virtualInstances = self.get(section=section, option=self.VIRTUALINSTANCES)
        if virtualInstances != None and len(virtualInstances) > 0:
            self.virtualInstances = virtualInstances.split()
            
        return self.virtualInstances
    
    def getWho(self, section=LOCALHOST):
        who = self.get(section=section, option=self.WHO)
        return who


    def getKind(self, section=LOCALHOST):
        self.kind = Sensation.Kind.WallE
        kind = self.get(section=section, option=self.KIND)
        if kind != None and len(kind) > 0:
            if kind == Sensation.Kinds[Sensation.Kind.WallE]:
                self.kind = Sensation.Kind.WallE
            elif kind == Sensation.Kinds[Sensation.Kind.Eva]:
                self.kind = Sensation.Kind.Eva
            else:
                self.kind = Sensation.Kind.Other
        return self.kind

    def getInstance(self, section=LOCALHOST):
        self.instance = Sensation.Instance.Real
        instance = self.get(section=section, option=self.INSTANCE)
        if instance != None and len(instance) > 0:
            if instance == Sensation.Instances[Sensation.Instance.Real]:
                self.instance = Sensation.Instance.Real
            else:
                self.instance = Sensation.Instance.Virtual
          
        return self.instance
    
    def getCapabilities(self, section=LOCALHOST):
        bytes=self.toBytes(section=section)
        return Capabilities(bytes=bytes)

    def canHear(self, section=LOCALHOST):
        return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                  Sensation.getMemoryString(Sensation.Memory.Sensory),
                                  Sensation.getSensationTypeString(Sensation.SensationType.HearDirection),
                                  section=section)
    
    def canMove(self, section=LOCALHOST):
       return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.Drive),
                                 section=section)

    def canSee(self, section=LOCALHOST):
       return self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.ImageFilePath),
                                 section=section) \
                                 and \
              self.hasCapability(Sensation.getDirectionString(Sensation.Direction.In),
                                 Sensation.getMemoryString(Sensation.Memory.Sensory),
                                 Sensation.getSensationTypeString(Sensation.SensationType.PictureData),
                                 section=section)



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
    
    # config

    config = Config()
    b=config.toBytes()
    config.fromBytes(b=b,section='bytes')

    string=config.toString()
    config.fromString(string=string,section='string')
    
    instance= config.getInstance()
    print('Instance ' + str(instance))
 
    kind= config.getKind()
    print('Kind ' + str(kind))
    
    subInstances=  config.getsubInstances()
    print('subInstances ' + str(subInstances))

    virtualInstances=  config.getVirtualInstances()
    print('VirtualInstances ' + str(virtualInstances))
    

    
    #capabilities

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



