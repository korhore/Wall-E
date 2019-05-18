'''
Created on 28.04.2019
Edited 18.05.2019

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
# NOTE Cannot import Sensation normal way, or either by sy6s.modules,
# because we have cross references
# We ddont want to put Sensation to this file (file would become huge),
# but keep it independent, so we use permethod import, when needed
#
# if 'Sensation' not in sys.modules:
#     from Sensation import Sensation

class Config(ConfigParser):

    ETC_DIRECTORY =    'etc'
    CONFIG_FILE_PATH = 'etc/Robot.cfg'
    DEFAULT_INSTANCE = 'Robot'
    MAIN_INSTANCE =    'MainRobot'
   
    
    # Configuratioon Section and Option names
    LOCALHOST =         'localhost' 
    MEMORY =            'memory'
#    Microphones =       'MICROPHONES' 
    WHO =               'Who' 
    WALLE =             'Wall-E'
    KIND =              "Kind"
    INSTANCE =          "Instance"
    VIRTUALINSTANCES =  "Virtualinstances"
    SUBINSTANCES =      "Subinstances"
    HOSTS =             "Hosts"
    IDENTITYS =         "Identitys"

    MICROPHONE =                   'microphone'
    MICROPHONE_VOICE_LEVEL_AVERAGE = 'microphone_voice_average_level'
    MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT = '300.0'
    MICROPHONE_LEFT =              'microphone_left'
    MICROPHONE_RIGHT =             'microphone_right'
    MICROPHONE_CALIBRATING_FACTOR ='microphone_calibrating_factor'
    MICROPHONE_CALIBRATING_ZERO =  'microphone_calibrating_zero'
    
    PLAYBACK =          'playback'

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
     
#    def __init__(self, config_file_path=CONFIG_FILE_PATH,
    def __init__(self,
                 instanceName=None,
                 instanceType=None,
                 level=0):
        from Sensation import Sensation
        ConfigParser.__init__(self)
        self.instanceName=instanceName
        self.instanceType=instanceType
        self.level=level+1
        self.is_changes=False # do we gave chanhes to save

        print("Config level " + str(self.level) + 
              " instanceType " + str(self.instanceType) )
       
        if  self.instanceName is None:
            self.instanceName = Config.DEFAULT_INSTANCE
            directory = '.'
        else:
            directory = instanceName
            if not os.path.exists(directory):
                print('os.makedirs ' + directory)
                os.makedirs(directory)
                
        etc_directory = directory +'/' + Config.ETC_DIRECTORY
        if not os.path.exists(etc_directory):
            print('os.makedirs ' + etc_directory)
            os.makedirs(etc_directory)
            
        self.config_file_path = directory + '/' + Config.CONFIG_FILE_PATH
        
        print("Config instanceName " + self.instanceName +
              " level " + str(self.level) + ' ' + self.config_file_path + 
              " instanceType " + str(self.instanceType) +
              " config_file_path " + self.config_file_path)

        
        #Read config        
        if os.path.exists(self.config_file_path):
            self.read(self.config_file_path)
 
        # If we don't have default section or Capsbilities section make it.
        # It will be a template if some capabilities will be set on
        # TODO should we update config file anway, if there are changes in
        # capabilities etc.                         
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
                    
         # handle subInstances (senses, muscles)
         # for two levels
        if self.level <= 3:
            for instanceName in self.getVirtualInstanceNames():
                config=Config(instanceName=instanceName,
                              instanceType=Sensation.InstanceType.Virtual,
                              level=self.level)
                
            for instanceName in self.getSubInstanceNames():
                config=Config(instanceName=instanceName,
                              instanceType=Sensation.InstanceType.SubInstance,
                              level=self.level)
#             self.handleSubInstances(is_virtualInstance=False,
#                                     is_subInstance=False)
# 
#             # handle virtual instanceNames
#             self.handleSubInstances(is_virtualInstance=True)

                     
                    
                    
    def handleSubInstances(self, instanceType):
        instanceNames=[]
        if instanceType == Sensation.InstanceType.Virtual:
            instanceNames=self.getVirtualInstanceNames()
        elif instanceType == Sensation.InstanceType.SubInstance:
            instanceNames=self.getSubInstanceNames()

        # relational subdirectory for virtual instanceName
        for instanceName in instanceNames:
            print('Handle  instanceName ' + instanceName)
            if instanceType == Sensation.InstanceType.Virtual:
                directory = self.VIRTUALINSTANCES+'/'+instanceName
            else:
                directory = instanceName
            if not os.path.exists(directory):
                print('os.makedirs ' + directory)
                os.makedirs(directory)
            config_file_path=directory + '/' + Config.CONFIG_FILE_PATH
            etc_directory = directory +'/etc'
            
            # relational subdirectory for virtual instanceName
            if not os.path.exists(etc_directory):
                print('os.makedirs ' + etc_directory)
                os.makedirs(etc_directory)
            #finallu create or update default config file for virtual instanceName 
            print('Config(' + config_file_path +')')
            # TODO Here we should make onlt onle level morem because otherwise we get
            #endless loop
            config = Config(config_file_path=config_file_path, level=self.level)
           # finally set default that this is virtual instanceName
            #changes = False
            if instanceType == Sensation.InstanceType.Virtual:                
                try:
                    instanceName = config.get(Config.DEFAULT_SECTION, Config.INSTANCE)
                    if instanceName != Sensation.VIRTUAL:          
                        config.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL)
                        self.is_changes=True
                except Exception as e:
                        print('config.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL) exception ' + str(e))
            else:
                try:
                    instanceName = config.get(Config.DEFAULT_SECTION, Config.INSTANCE)
                    if instanceName != Sensation.SUBINSTANCE:          
                        config.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.SUBINSTANCE)
                        self.is_changes=True
                except Exception as e:
                        print('config.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL) exception ' + str(e))
               
            if self.is_changes:
                try:
                    configfile = open(config_file_path, 'w')
                    config.write(configfile)
                    configfile.close()
                except Exception as e:
                    print('config.write(configfile) ' + str(e))

    def getConfigFilePath(self):
        return self.config_file_path
                    
    def getIdentityDirPath(self, kind):
        from Sensation import Sensation
        return self.IDENTITYS +'/'+ Sensation.Kinds[kind]

                
    def getVirtualinstanceConfigFilePath(self, virtualinstance):
        return virtualinstance + '/' + Config.CONFIG_FILE_PATH
        
    def getSubinstanceConfigFilePath(self, instanceName):
        return instanceName + '/' + Config.CONFIG_FILE_PATH

                
            

    '''
    localhost capaliliys to bytes
    '''
    def toBytes(self, section=LOCALHOST):
        from Sensation import Sensation
        b=b''
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    option=self.getOptionName(direction,memory,sensationType)
                    is_set=self.getboolean(section, option)
#                    if is_set:
#                         print('toBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    b = b + Config.boolToByte(is_set)
#         print('toBytes section ' + section + ' '+ str(len(b)))
        return b
 
    '''
    localhost capalilitys to String
    '''
    def toString(self, section=LOCALHOST):
        from Sensation import Sensation
        string=''
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    option=self.getOptionName(direction,memory,sensationType)
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
    b can be int, string (one char) or byte
    '''
    def byteToBool(b):
        if isinstance(b, int):
            return b != 0
        if isinstance(b, string):
            return b != Config.FALSE_CHAR
        return b != Config.FALSE_ENCODED
    '''
    Helper function to convert int to boolean
    '''
    def intToBool(b):
        return b != 0

    '''
    Helper function to convert boolean to config file String (one char)
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
        from Sensation import Sensation
#         print('fromBytes ' + str(len(b)))
        i=0
        #changes=False
        if not self.has_section(section):
            try:
                self.add_section(section)
                self.is_changes=True

            except MissingSectionHeaderError as e:
                    print('self.add_section ' + section + ' configparser.MissingSectionHeaderError ' + str(e))
            except NoSectionError as e:
                    print('eslf.add_section ' + section + ' configparser.NoSectionError ' + str(e))
            except NoOptionError as e:
                    print('self.add_section ' + section + ' configparser.NoOptionError ' + str(e))
            except Exception as e:
                    print('self.add_section ' + section + ' exception ' + str(e))
        # capabilities from b bytes to options
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    option=self.getOptionName(direction,memory,sensationType)
                    is_set=Config.byteToBool(b[i])
                    i=i+1
#                    if is_set:
#                         print('fromBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    try:
                        if not self.has_option(section, option):
                            self.set(section, option, Config.boolToString(is_set))
                            self.is_changes=True
                        else:
                            was_set = self.getboolean(section, option)
                            if is_set != was_set:
                                self.set(section, option, Config.boolToString(is_set))
                                self.is_changes=True
                    except Exception as e:
                        print('self.set(' + section+', option, self.FALSE) exception ' + str(e))

        self.commit()

    '''
    commit changes
    '''
    def commit(self):
        if self.is_changes:
            try:
                configfile = open(self.config_file_path, 'w')
                self.write(configfile)
                configfile.close()
                self.is_changes=False
            except Exception as e:
                print('self.write(configfile) ' + str(e))
        
    '''
    external or local host capabilities to given capability section
    section name is normally hosts ip-address as text, if given
    if section is not given, we get local capabilities
    '''
    def fromString(self, string, section=LOCALHOST):
        from Sensation import Sensation
#         print('fromBytes ' + str(len(b)))
        i=0
        #changes=False
        if not self.has_section(section):
            try:
                self.add_section(section)
                self.is_changes=True

            except MissingSectionHeaderError as e:
                    print('self.add_section ' + section + ' configparser.MissingSectionHeaderError ' + str(e))
            except NoSectionError as e:
                    print('eslf.add_section ' + section + ' configparser.NoSectionError ' + str(e))
            except NoOptionError as e:
                    print('self.add_section ' + section + ' configparser.NoOptionError ' + str(e))
            except Exception as e:
                    print('self.add_section ' + section + ' exception ' + str(e))
        # capabilities from string to options
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    option=self.getOptionName(direction,memory,sensationType)
                    is_set=Config.charToBool(string[i])
                    i=i+1
#                    if is_set:
#                         print('fromBytes ' + directionStr + ' ' + memoryStr + ' ' + capabilityStr + ': True')
                    try:
                        if not self.has_option(section, option):
                            self.set(section, option, Config.boolToString(is_set))
                            self.is_changes=True
                        else:
                            was_set = self.getboolean(section, option)
                            if is_set != was_set:
                                self.set(section, option, Config.boolToString(is_set))
                                self.is_changes=True
                    except Exception as e:
                        print('self.set(' + section+', option, self.FALSE) exception ' + str(e))

        self.commit()

    def createDefaultSection(self):
        #changes=False
        from Sensation import Sensation
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    option=self.getOptionName(direction,memory,sensationType)
                    try:
                        if not self.has_option(Config.DEFAULT_SECTION, option):
                            self.set(self.DEFAULT_SECTION, option, self.FALSE)
                            self.is_changes=True
                    except Exception as e:
                        print('self.set(self.DEFAULT_SECTION, option, self.FALSE) exception ' + str(e))
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.WHO):
                self.set(Config.DEFAULT_SECTION,Config.WHO, Sensation.WALLE)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.WHO, Config.WHO) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.KIND):
                self.set(Config.DEFAULT_SECTION,Config.KIND, Sensation.WALLE)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.KIND, Sensation.WALLE) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.INSTANCE):
                self.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.REAL)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.KIND, Sensation.WALLE) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.HOSTS):
                self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.HOSTS, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.SUBINSTANCES):
                if self.level == 1:
                    self.set(Config.DEFAULT_SECTION,Config.SUBINSTANCES, Config.DEFAULT_SUBINSTANCES)
                else:
                    self.set(Config.DEFAULT_SECTION,Config.SUBINSTANCES, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.SUBINSTANCES, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.VIRTUALINSTANCES):
                self.set(Config.DEFAULT_SECTION,Config.VIRTUALINSTANCES, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.VIRTUALINSTANCES, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE):
                self.set(Config.DEFAULT_SECTION, Config.MICROPHONE, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE, Config.EMPTY) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE_VOICE_LEVEL_AVERAGE):
                self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_VOICE_LEVEL_AVERAGE, Config.MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_VOICE_LEVEL_AVERAGE, Config.MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT) ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT):
                self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_LEFT, Config.EMPTY) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.MICROPHONE_RIGHT):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_RIGHT, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.MICROPHONE_RIGHT, Config.EMPTY) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_ZERO):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_ZERO, Config.ZERO)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_ZERO, Config.ZERO) exception ' + str(e))

        try:                
            if not self.has_option(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_FACTOR):
                self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_FACTOR, Config.ZERO)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION,Config.MICROPHONE_CALIBRATING_FACTOR, Config.ZERO) exception ' + str(e))
            
        try:                
            if not self.has_option(Config.DEFAULT_SECTION, Config.PLAYBACK):
                self.set(Config.DEFAULT_SECTION, Config.PLAYBACK, Config.EMPTY)
                self.is_changes=True
        except Exception as e:
            print('self.set(Config.DEFAULT_SECTION, Config.PLAYBACK, Config.EMPTY) exception ' + str(e))
            
        if self.instanceType == Sensation.InstanceType.Virtual:                
            try:
                instanceName = self.get(Config.DEFAULT_SECTION, Config.INSTANCE)
                if instanceName != Sensation.VIRTUAL:          
                    self.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL)
                    self.is_changes=True
            except Exception as e:
                    print('self.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL) exception ' + str(e))
        if self.instanceType == Sensation.InstanceType.SubInstance:                
            try:
                instanceName = self.get(Config.DEFAULT_SECTION, Config.INSTANCE)
                if instanceName != Sensation.SUBINSTANCE:          
                    self.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.SUBINSTANCE)
                    self.is_changes=True
            except Exception as e:
                    print('self.set(Config.DEFAULT_SECTION,Config.INSTANCE, Sensation.VIRTUAL) exception ' + str(e))
        
        
        if not self.has_section(Config.LOCALHOST):
            try:
                self.add_section(Config.LOCALHOST)
                self.is_changes=True

            except MissingSectionHeaderError as e:
                    print('self.add_section configparser.MissingSectionHeaderError ' + str(e))
            except NoSectionError as e:
                    print('eslf.add_section configparser.NoSectionError ' + str(e))
            except NoOptionError as e:
                    print('self.add_section configparser.NoOptionError ' + str(e))
            except Exception as e:
                    print('self.add_section exception ' + str(e))

        self.commit()
                
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
    def getOptionName(self, direction,memory,sensationType):
        from Sensation import Sensation
        return Sensation.getDirectionString(direction)+'_'+Sensation.getMemoryString(memory)+'_'+ Sensation.getSensationTypeString(sensationType)

    def hasCapability(self, direction,memory,sensationType, section=LOCALHOST):
        option=self.getOptionName(direction,memory,sensationType)
        return self.getboolean(section, option)

             
    def getSubInstanceNames(self, section=LOCALHOST):
        self.subInstanceNames=[]
        subInstanceNames = self.get(section=section, option=self.SUBINSTANCES)
        if subInstanceNames != None and len(subInstanceNames) > 0:
            self.subInstanceNames = subInstanceNames.split()
            
        return self.subInstanceNames

    def getVirtualInstanceNames(self, section=LOCALHOST):
        self.virtualInstanceNames=[]
        virtualInstanceNames = self.get(section=section, option=self.VIRTUALINSTANCES)
        if virtualInstanceNames != None and len(virtualInstanceNames) > 0:
            self.virtualInstanceNames = virtualInstanceNames.split()
            
        return self.virtualInstanceNames
    
    def getHostNames(self, section=LOCALHOST):
        self.hostNames=[]
        hostNames = self.get(section=section, option=self.HOSTS)
        if hostNames != None and len(hostNames) > 0:
            self.hostNames = hostNames.split()
            
        return self.hostNames
    
    def getWho(self, section=LOCALHOST):
        who = self.get(section=section, option=self.WHO)
        return who


    def getKind(self, section=LOCALHOST):
        from Sensation import Sensation
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

    def getInstanceType(self, section=LOCALHOST):
        from Sensation import Sensation
        instanceType = Sensation.InstanceType.Real
        instanceName = self.get(section=section, option=self.INSTANCE)
        if instanceName != None and len(instanceName) > 0:
            if instanceName == Sensation.InstanceTypes[Sensation.InstanceType.Real]:
                instanceType = Sensation.InstanceType.Real
            if instanceName == Sensation.InstanceTypes[Sensation.InstanceType.SubInstance]:
                instanceType = Sensation.InstanceType.SubInstance
            else:
                instanceType = Sensation.InstanceType.Virtual
          
        return instanceType
    
    def getMicrophone(self, section=LOCALHOST):
        try:
            return self.get(section=section, option=self.MICROPHONE)
        except Exception as e:
            print('self.get(section=section, option=self.MICROPHONE) ' + str(e))
            return None

    def getMicrophoneVoiceAvegageLevel(self, section=LOCALHOST):
        try:
            return self.getfloat(section=section, option=self.MICROPHONE_VOICE_LEVEL_AVERAGE)
        except Exception as e:
            print('self.getfloat(section=section, option=self.MICROPHONE_VOICE_LEVEL_AVERAGE)' + str(e))
            return None
        
    def setMicrophoneVoiceAvegageLevel(self, section=LOCALHOST, voiceLevelAverage=MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT, commit=True):
        try:
            self.set(section=section, option=self.MICROPHONE_VOICE_LEVEL_AVERAGE, value=str(voiceLevelAverage))
            self.is_changes = True
        except Exception as e:
            print('self.set(section=section, option=self.MICROPHONE_VOICE_LEVEL_AVERAGE, value=str(voiceLevelAverage))' + str(e))
        if commit:
            self.commit()

    def getMicrophone(self, section=LOCALHOST):
        try:
            return self.get(section=section, option=self.MICROPHONE)
        except Exception as e:
            print('self.get(section=section, option=self.MICROPHONE) ' + str(e))
            return None

    def getPlayback(self, section=LOCALHOST):
        try:
            return self.get(section=section, option=self.PLAYBACK)
        except Exception as e:
            print('self.get(section=section, option=self.PLAYBACK) ' + str(e))
            return None
        
    def getCapabilities(self, section=LOCALHOST):
        bytes=self.toBytes(section=section)
        return Capabilities(bytes=bytes)

    def canHear(self, section=LOCALHOST):
        from Sensation import Sensation
        return self.hasCapability(Sensation.Direction.In,
                                  Sensation.Memory.Sensory,
                                  Sensation.SensationType.HearDirection,
                                  section=section)
    
    def canMove(self, section=LOCALHOST):
        from Sensation import Sensation
        return self.hasCapability(Sensation.Direction.In,
                                 Sensation.Memory.Sensory,
                                 Sensation.SensationType.Drive,
                                 section=section)

    def canSee(self, section=LOCALHOST):
        from Sensation import Sensation
        return self.hasCapability(Sensation.Direction.In,
                                 Sensation.Memory.Sensory,
                                 Sensation.SensationType.ImageFilePath,
                                 section=section) \
                                 and \
              self.hasCapability(Sensation.Direction.In,
                                 Sensation.Memory.Sensory,
                                 Sensation.SensationType.ImageData,
                                 section=section)



class Capabilities():
    
    def __init__(self,
                 string=None,
                 bytes=None,
                 config=None,
                 Or =None,
                 And=None,
                 deepCopy=None):
        if string is not None:
            self.fromString(string=string)
        elif Or is not None:
            self.Or(Or)
        elif And is not None:
            self.And(And)
        elif deepCopy is not None:
            self.deepCopy(deepCopy)
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
        from Sensation import Sensation
        if bytes == None:
            bytes=self.config.toBytes()
        self.directions={}
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        i=0
        for direction in Sensation.DirectionsOrdered:
            memorys={}
            self.directions[direction] = memorys
            for memory in Sensation.MemorysOrdered:
                capabilitys={}
                memorys[memory] = capabilitys
                for sensationType in Sensation.SensationTypesOrdered:
                    is_set=Config.byteToBool(b=bytes[i])
#                     if is_set:
#                         print (str(direction) + str(memory) + str(sensationType) + ': TRUE')
                    capabilitys[sensationType] = is_set
#                     print ('i ' + str(i) + ': ' + str(bytes[i]) + ' ' + str(is_set))
                    i=i+1
    '''
    to bytes
    '''
    def toBytes(self):
        from Sensation import Sensation
        bytes=b''
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    bytes += Config.boolToByte(self.directions[direction][memory][sensationType])
        return bytes
    
    '''
    Initiated from String
    '''
    def fromString(self, string=None):
        from Sensation import Sensation
        if string == None:
            string=self.config.toString()
        self.directions={}
        i=0
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        for direction in Sensation.DirectionsOrdered:
            memorys={}
            self.directions[direction] = memorys
            for memory in Sensation.MemorysOrdered:
                capabilitys={}
                memorys[memory] = capabilitys
                for sensationType in Sensation.SensationTypesOrdered:
                    is_set=Config.charToBool(string[i])
#                     if is_set:
#                         print (str(direction) + str(memory) + str(capability) + ': TRUE')
                    capabilitys[sensationType] = is_set
#                     print ('i ' + str(i) + ': ' + str(bytes[i]) + ' ' + str(is_set))
                    i=i+1
    '''
    to String
    '''
    def toString(self):
        from Sensation import Sensation
        string=''
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    string += Config.boolToChar(self.directions[direction][memory][sensationType])
        return string

    '''
    to debug String
    '''
    def toDebugString(self, name=''):
        from Sensation import Sensation
        string= "\n" + name + ":\n"
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    if self.directions[direction][memory][sensationType]:
                        string += Sensation.getDirectionString(direction) + ' ' + Sensation.getMemoryString(memory) + ' ' + Sensation.getSensationTypeString(sensationType) + ': True\n'
        return string


    '''
    Getter to get if single capability is set
    '''
    def hasCapanility(self, direction, memory, sensationType):
        return self.directions[direction][memory][sensationType]
 
    '''
    Setter to set if single capability is set
    '''
    def setCapability(self, direction, memory, sensationType, is_set):
        self.directions[direction][memory][sensationType] = is_set

    '''
    return capabilities that are true, is this one has a capability or other has it
    '''
    def Or(self, other):
        #self.test("Or before", other)
        from Sensation import Sensation
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    self.directions[direction][memory][sensationType] = \
                        self.directions[direction][memory][sensationType] or \
                        other.directions[direction][memory][sensationType]
        #self.test("Or after", other)
        
    '''
    return capabilities that are true, is this one has a capability and other has it
    '''
    def And(self, other):
        #self.test("And before", other)
        from Sensation import Sensation
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    self.directions[direction][memory][sensationType] = \
                        self.directions[direction][memory][sensationType] and \
                        other.directions[direction][memory][sensationType]
        #self.test("And after", other)
                    
    '''
    return deep copy of capabilities
    '''
    def deepCopy(self, capabilities):
        from Sensation import Sensation
        self.directions={}
        # create three level dictionary about capabilitys by direction, by memory, by sensation type
        for direction in Sensation.DirectionsOrdered:
            memorys={}
            self.directions[direction] = memorys
            for memory in Sensation.MemorysOrdered:
                capabilitys={}
                memorys[memory] = capabilitys
                for sensationType in Sensation.SensationTypesOrdered:
#                     #capabilitys[sensationType] = \
#                         #capabilities.directions[direction][memory][sensationType]
#                         print("deepCopy direction " + str(direction) + " memory " + str(memory) + " sensationType " + str(sensationType))
#                         directionDict=capabilities.directions[direction]
#                         mem=directionDict[memory]
#                         sens=mem[sensationType]
#                         capabilitys[sensationType] = sens
                        capabilitys[sensationType] = capabilities.directions[direction][memory][sensationType]
        
#         for direction in list(Sensation.Direction):
#             memorys={}
#             self.directions[direction] = memorys
#             for memory in list(Sensation.Memory):
#                 capabilitys={}
#                 memorys[memory] = capabilitys
#                 for sensationType in list(Sensation.SensationType):
#                     #capabilitys[sensationType] = \
#                         #capabilities.directions[direction][memory][sensationType]
#                         print("deepCopy direction " + str(direction) + " memory " + str(memory) + " sensationType " + str(sensationType))
#                         direction=capabilities.directions[direction]
#                         mem=direction[memory]
#                         sens=mem[sensationType]
        
        
    '''
    test
    '''
    def test(self, name, capabilities=None):
        from Sensation import Sensation
        if capabilities is not None:
            for direction in Sensation.DirectionsOrdered:
                for memory in Sensation.MemorysOrdered:
                    for sensationType in Sensation.SensationTypesOrdered:
                        is_set = capabilities.hasCapanility(direction, memory, sensationType)
                        if is_set:
                            print (name + " capabilities : " + Sensation.getDirectionString(direction) + ' ' + Sensation.getMemoryString(memory) + ' ' + Sensation.getSensationTypeString(sensationType) + ': True')
        for direction in Sensation.DirectionsOrdered:
            for memory in Sensation.MemorysOrdered:
                for sensationType in Sensation.SensationTypesOrdered:
                    is_set = self.hasCapanility(direction, memory, sensationType)
                    if is_set:
                        print (name + " self : " + Sensation.getDirectionString(direction) + ' ' + Sensation.getMemoryString(memory) + ' ' + Sensation.getSensationTypeString(sensationType) + ': True')

'''
test
'''
def test(name, capabilities):
    from Sensation import Sensation
    some_set=False
    for direction in Sensation.DirectionsOrdered:
        for memory in Sensation.MemorysOrdered:
            for sensationType in Sensation.SensationTypesOrdered:
                is_set = capabilities.hasCapanility(direction, memory, sensationType)
                if is_set:
                    print (name + ": " + Sensation.getDirectionString(direction) + ' ' + Sensation.getMemoryString(memory) + ' ' + Sensation.getSensationTypeString(sensationType) + ': True')
                    some_set=True
    if not some_set:
        print (name + ": ALL FALSE")



if __name__ == '__main__':
    from Sensation import Sensation
    cwd = os.getcwd()
    print('cwd ' + cwd)
    
    # config

    config = Config()
    b=config.toBytes()
    config.fromBytes(b=b,section='bytes')

    string = config.toString()
    config.fromString(string=string,section='string')
    
    instanceType= config.getInstanceType()
    print('InstanceType ' + str(instanceType))
 
    kind= config.getKind()
    print('Kind ' + str(kind))
    
    subInstanceNames = config.getSubInstanceNames()
    print('subInstanceNames ' + str(subInstanceNames))

    virtualInstanceNames = config.getVirtualInstanceNames()
    print('VirtualInstanceNames ' + str(virtualInstanceNames))
    
    hostNames = config.getHostNames()
    print('HostNames ' + str(hostNames))

    hostNames = config.getHostNames()
    print(config.getCapabilities().toDebugString('Capabilities from config'))
   
    #capabilities
    print('')

    capabilities = Capabilities(config=config)
    test(name="Capabilities(config=config)", capabilities=capabilities)
    capabilities.setCapability(direction=Sensation.Direction.In, memory=Sensation.Memory.Sensory, sensationType=Sensation.SensationType.VoiceData, is_set=True)
    test(name="VoiceData set", capabilities=capabilities)
   
    b = capabilities.toBytes()
    print('capabilities.toBytes  ' + str(b))
    test(name="before toBytes(fromBytes)", capabilities=capabilities)
    capabilities.fromBytes(bytes=b)
    test(name="after toBytes(fromBytes)", capabilities=capabilities)
    b2 = capabilities.toBytes()
    print('capabilities.toBytes2 ' + str(b))
    print ('should be b == b2 True ', str(b==b2))
    
    capabilities2 = Capabilities(bytes=b)
    test(name="capabilities original", capabilities=capabilities)
    test(name="capabilities2 from bytes", capabilities=capabilities2)
    b2 = capabilities2.toBytes()
    print('b2 ' + str(b))
    print ('should be b == b2 True ', str(b==b2))
    print ('should be capabilities == capabilities2 True ', str(capabilities==capabilities2))
    capabilities.toDebugString('capabilities')
    capabilities2.toDebugString('capabilities2')

    
    string = capabilities.toString()
    print('string  ' + string)
    capabilities.fromString(string=string)
    string2 = capabilities.toString()
    print('string2 ' + string2)
    print ('should be string == string2 True ', str(string == string2))
    
    test(name="original", capabilities=capabilities)
    capabilities2 = Capabilities(deepCopy=capabilities)
    test(name="deepCopy", capabilities=capabilities2)
    print ('should be deepCopy capabilities  == capabilities2 True ', str(capabilities == capabilities2))
    capabilities.toDebugString('capabilities')
    capabilities2.toDebugString('capabilities2')

    
    #test
    test(name="capabilities", capabilities=capabilities)
    test(name="capabilities2", capabilities=capabilities2)
 
    # set all True 
    print ("Set all True")
    for direction, directionStr in Sensation.Directions.items():
        for memory, memoryStr in Sensation.Memorys.items():
            for sensationType, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapability(direction, memory, sensationType, True)
    test(name="Set all True", capabilities=capabilities)
    capabilities.And(other=capabilities2)
    test(name="Set all True capabilities And capabilities2", capabilities=capabilities)

    for direction, directionStr in Sensation.Directions.items():
        for memory, memoryStr in Sensation.Memorys.items():
            for sensationType, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapability(direction, memory, sensationType, True)
    capabilities.Or(other=capabilities2)
    test(name="Set all True capabilities Or capabilities2", capabilities=capabilities)

     # set all False 
    print ("Set all False")
    for direction, directionStr in Sensation.Directions.items():
        for memory, memoryStr in Sensation.Memorys.items():
            for sensationType, capabilityStr in Sensation.SensationTypes.items():
                capabilities.setCapability(direction, memory, sensationType, False)
    test(name="Set all False", capabilities=capabilities)
    capabilities.Or(other=capabilities2)
    test(name="Set all False Or capabilities2", capabilities=capabilities)

    #config=Config()
    capabilities=Capabilities(config=config)
    test("default config", capabilities)
    
    bytes=config.toBytes(section="bytes")                
    capabilities=Capabilities(bytes=bytes)
    test("bytes", capabilities)

    string=config.toString()                
    capabilities = Capabilities(string=string)
    test("string", capabilities)



