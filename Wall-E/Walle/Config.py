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

    def __init__(self):
        ConfigParser.__init__(self)
        
        cwd = os.getcwd()
        print("cwd " + cwd)

#        config_file=open(CONFIG_FILE_PATH,"r")
#        self.read(config_file)
        
        self.read(CONFIG_FILE_PATH)
        print(str(self.sections()))


                            
        #left_card = self.get(Config.Capabilities, Config.Memory)
 
        # TODO configure Hearing after capabilities configuration
        # if we have Hearing capability set       
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
                print('configparser.MissingSectionHeaderError ' + str(e))
                self.canRun = False
        except NoSectionError as e:
                print('configparser.NoSectionError ' + str(e))
                self.canRun = False
        except NoOptionError as e:
                print('configparser.NoOptionError ' + str(e))
                self.canRun = False
        except Exception as e:
                print('configparser exception ' + str(e))
                self.canRun = False

 
        # TODO make autoconfig here  
        
        try:
#            if not self.has_section(Config.DEFAULT_SECTION):
#                self.createDefaultSection()
            self.createDefaultSection()
            
        except MissingSectionHeaderError as e:
                print('configparser.MissingSectionHeaderError ' + str(e))
                self.canRun = False
        except NoSectionError as e:
                print('configparser.NoSectionError ' + str(e))
                self.canRun = False
        except NoOptionError as e:
                print('configparser.NoOptionError ' + str(e))
                self.canRun = False
        except Exception as e:
                print('configparser exception ' + str(e))
                self.canRun = False

    def createDefaultSection(self):
        changes=False
        for direction in Sensation.getDirectionStrings():
            for memory in Sensation.getMemoryStrings():
                for capability in Sensation.getSensationTypeStrings():
                    option=self.getOptionName(direction,memory,capability)
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
                    print('configparser.MissingSectionHeaderError ' + str(e))
            except NoSectionError as e:
                    print('configparser.NoSectionError ' + str(e))
            except NoOptionError as e:
                    print('configparser.NoOptionError ' + str(e))
            except Exception as e:
                    print('configparser exception ' + str(e))

        if changes:
            try:
                configfile = open(CONFIG_FILE_PATH, 'w')
                self.write(configfile)
                configfile.close()
            except Exception as e:
                print('self.write(configfile) ' + str(e))
 
    # what capabilities we have TODO
    def getOptionName(self, direction,memory,capability):
        return direction+'_'+memory+'_'+capability

    def hasCapability(self, direction,memory,capability):
        return self.getboolean(Config.Capabilities, self.getOptionName(direction,memory,capability))

             
    def canHear(self):
        return False
    
    def canMove(self):
        return False




