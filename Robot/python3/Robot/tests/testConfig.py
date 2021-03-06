'''
Created on 12.05.2020
Updated on 06.04.2021
@author: reijo.korhonen@gmail.com

test Config class
python3 -m unittest tests/testConfig.py


'''


import time as systemTime
import unittest
from Config import Config, Capabilities
from Sensation import Sensation

class ConfigTestCase(unittest.TestCase):
    
    TEST_INSTANCE =       'TestRobot'
    TEST_MAINNAMES =      ['TestRobot', 'OtherRobot']
    
    
    SET_1_1_LOCATIONS_1 = ['testLocation']
    SET_1_1_LOCATIONS_2 = ['Ubuntu']
    SET_1_2_LOCATIONS =   ['testLocation', 'Ubuntu']

    SET_2_1_LOCATIONS_1 = ['testLocation2']
    SET_2_1_LOCATIONS_2 = ['raspberry']
    SET_2_2_LOCATIONS =   ['testLocation2', 'raspberry']
    
    TEST_DIRECTION =    Sensation.RobotType.Muscle
    TEST_MEMORYTYPE =   Sensation.MemoryType.Working
    TEST_SENSATIONTYPE = Sensation.SensationType.Voice
    
    

    def setUp(self):
        # create config same way as Robot does it
        self.config = Config(instanceName=ConfigTestCase.TEST_INSTANCE,
                             instanceType=Sensation.InstanceType.Real,
                             level=0)
        self.config.setMainNames(mainNames=ConfigTestCase.TEST_MAINNAMES)
        self.assertEqual(self.config.getMainNames(), ConfigTestCase.TEST_MAINNAMES, "should be equal")

        # check that we reaally have locations as sections
        self.config.setLocations(locations=ConfigTestCase.SET_1_2_LOCATIONS)
        self.assertEqual(self.config.getLocations(), ConfigTestCase.SET_1_2_LOCATIONS, "should be equal")
        # check that we reaally have locations as sections
        for location in self.config.getLocations():
            self.assertTrue(self.config.has_section(location))

        
        self.capabilities = Capabilities(config=self.config)
        self.capabilities.setCapability(robotType=Sensation.RobotType.Sense,
                                        memoryType=Sensation.MemoryType.Sensory,
                                        sensationType=Sensation.SensationType.Voice,
                                        is_set = True)
        self.assertTrue(self.capabilities.hasCapability(
                                        robotType=Sensation.RobotType.Sense,
                                        memoryType=Sensation.MemoryType.Sensory,
                                        sensationType=Sensation.SensationType.Voice))
#         self.assertEqual(self.capabilities.toString(), self.config.getCapabilities().toString(), "should be equal")
#         self.assertEqual(self.capabilities, self.config.getCapabilities(), "should be equal")

        
    def tearDown(self):
        del self.capabilities
        del self.config
        
    def testHasCapability(self):
        # in fonfig file should be
        self.assertTrue(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                         memoryType = Sensation.MemoryType.Sensory,
                                                         sensationType = Sensation.SensationType.Image))

        self.capabilities.setCapability(robotType=Sensation.RobotType.Sense,
                                        memoryType = Sensation.MemoryType.Sensory,
                                        sensationType = Sensation.SensationType.Voice,
                                        is_set = False)
        self.assertFalse(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                         memoryType = Sensation.MemoryType.Sensory,
                                                         sensationType = Sensation.SensationType.Voice))

        self.capabilities.setCapability(robotType=Sensation.RobotType.Sense,
                                        memoryType = Sensation.MemoryType.Sensory,
                                        sensationType = Sensation.SensationType.Voice,
                                        is_set = True)
        self.assertTrue(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                        memoryType = Sensation.MemoryType.Sensory,
                                                        sensationType = Sensation.SensationType.Voice))
        
        self.capabilities.setCapability(robotType=Sensation.RobotType.All,
                                  memoryType = Sensation.MemoryType.All,
                                  sensationType = Sensation.SensationType.All,
                                  is_set = False)
        self.assertTrue(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                        memoryType = Sensation.MemoryType.Sensory,
                                                        sensationType = Sensation.SensationType.Voice))
        
        
        self.capabilities.setCapability(robotType=Sensation.RobotType.Sense,
                                  memoryType = Sensation.MemoryType.Sensory,
                                  sensationType = Sensation.SensationType.Voice,
                                  is_set = False)
        self.capabilities.setCapability(robotType=Sensation.RobotType.Sense,
                                        memoryType = Sensation.MemoryType.Sensory,
                                        sensationType = Sensation.SensationType.Image,
                                        is_set = False)
        self.assertFalse(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                         memoryType = Sensation.MemoryType.Sensory,
                                                         sensationType = Sensation.SensationType.Voice))        
        self.assertFalse(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                         memoryType = Sensation.MemoryType.Sensory,
                                                         sensationType = Sensation.SensationType.Image))        
        self.capabilities.setCapability(robotType=Sensation.RobotType.All,
                                        memoryType = Sensation.MemoryType.All,
                                        sensationType = Sensation.SensationType.All,
                                        is_set = True)
        self.assertTrue(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                        memoryType = Sensation.MemoryType.Sensory,
                                                        sensationType = Sensation.SensationType.Voice))        
        self.assertTrue(self.capabilities.hasCapability(robotType=Sensation.RobotType.Sense,
                                                        memoryType = Sensation.MemoryType.Sensory,
                                                        sensationType = Sensation.SensationType.Image))        
        
    def testConfig(self):
        # methods that has set
        self.config.setActivityAvegageLevel(section=ConfigTestCase.SET_1_2_LOCATIONS[0], activityLevelAverage=Config.ACTIVITY_LEVEL_AVERAGE_DEFAULT+1)
        self.assertEqual(self.config.getActivityAvegageLevel(section=ConfigTestCase.SET_1_2_LOCATIONS[0]), Config.ACTIVITY_LEVEL_AVERAGE_DEFAULT+1)
        self.assertEqual(self.config.getActivityAvegageLevel(section=ConfigTestCase.SET_1_2_LOCATIONS[1]), Config.ACTIVITY_LEVEL_AVERAGE_DEFAULT)

        self.config.setMicrophoneVoiceAvegageLevel(section=ConfigTestCase.SET_1_2_LOCATIONS[0], voiceLevelAverage=Config.MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT+1)
        self.assertEqual(self.config.getMicrophoneVoiceAvegageLevel(section=ConfigTestCase.SET_1_2_LOCATIONS[0]), Config.MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT+1)
        self.assertEqual(self.config.getMicrophoneVoiceAvegageLevel(section=ConfigTestCase.SET_1_2_LOCATIONS[1]), Config.MICROPHONE_VOICE_LEVEL_AVERAGE_DEFAULT)
       

    '''
    Config bytes does not copy capabilities
    TODO check test
    '''       
    def testConfigBytes(self):
        print("testConfigBytes 1: self.config " + self.config.toString())
        b=self.config.toBytes()
        
        # create copy and change it, capabilities differ
        fromBytesConfig = Config(instanceName=ConfigTestCase.TEST_INSTANCE,
                                 instanceType=Sensation.InstanceType.Real,
                                 level=0)    # should get another copy
        #capabilities = Capabilities(config=fromBytesConfig)
        # exact copy created same way, than self.config
        print("testConfigBytes 2: self.config " + self.config.toString())
        print("testConfigBytes 3: fromBytes   " + fromBytesConfig.toString())
        self.compareConfig('self.config, fromBytesConfig', self.config, fromBytesConfig)
        
        self.assertEqual(fromBytesConfig, self.config, "should be equal")
        
        fromBytesConfig.fromBytes(b=b)  # this sets itself
        print("testConfigBytes 4: fromBytes   " + fromBytesConfig.toString())
        self.compareConfig('self.config, fromBytesConfig', self.config, fromBytesConfig)
        self.assertEqual(fromBytesConfig, self.config, "should now be equal")
        
        #capabilities = Capabilities(config=fromBytesConfig)

        fromBytesConfigBytes = fromBytesConfig.toBytes()
        self.assertEqual(fromBytesConfigBytes, b, "should be equal")
        
        
    def compareConfig(self, logStr, firstConfig, secondConfig):
        if firstConfig.instanceName != secondConfig.instanceName:
            print (logStr + " instanceName differs " +  firstConfig.instanceName + ' '+ secondConfig.instanceName)
        if firstConfig.instanceType != secondConfig.instanceType:
            print (logStr +" instanceType differs " +  str(firstConfig.instanceType) + ' '+ str(secondConfig.instanceType))
        if firstConfig.level != secondConfig.level:
            print (logStr + " level differs " +  str(firstConfig.level) + ' '+ str(secondConfig.level))
#         if firstConfig.getLocations() != secondConfig.getLocations():
#             print (logStr + " getLocations() differs " +  str(firstConfig.getLocations()) + ' '+ str(secondConfig.getLocations()))
#         else:
#             print (logStr + " getLocations() equal " +  str(firstConfig.getLocations()) + ' '+ str(secondConfig.getLocations()))

# TODO Don't know if ever used, so implementation and test is commented out           
#         if firstConfig.getCapabilities().toString() != secondConfig.getCapabilities().toString():
#             print (logStr + " getCapabilities().toString() differs " + firstConfig.getCapabilities().toString() + ' '+ secondConfig.getCapabilities().toString())
#         else:
#            print (logStr + " getCapabilities().toString() equal " +  firstConfig.getCapabilities().toString() + ' '+ secondConfig.getCapabilities().toString())
# 
#         if firstConfig.getCapabilities() != secondConfig.getCapabilities():
#             print (logStr + " getCapabilities() differs " + firstConfig.getCapabilities().toString() + ' '+ secondConfig.getCapabilities().toString())
#         else:
#            print (logStr + " getCapabilities() equal " +  firstConfig.getCapabilities().toString() + ' '+ secondConfig.getCapabilities().toString())
            

    def testCapabilitiesBytes(self):
        self.assertTrue(self.capabilities.hasCapability(
                                        robotType=Sensation.RobotType.Sense,
                                        memoryType=Sensation.MemoryType.Sensory,
                                        sensationType=Sensation.SensationType.Voice))

        b = self.capabilities.toBytes()
        print('capabilities.toBytes  ' + str(b))
        
        fromBytesCabalities = Capabilities(bytes=b, config=self.config)
        fromBytesCabalitiesBytes=fromBytesCabalities.toBytes()
        self.assertEqual(fromBytesCabalitiesBytes, b, "should be equal")
        self.assertTrue(fromBytesCabalities.hasCapability(
                                        robotType=Sensation.RobotType.Sense,
                                        memoryType=Sensation.MemoryType.Sensory,
                                        sensationType=Sensation.SensationType.Voice))
        self.assertEqual(self.capabilities.directions, fromBytesCabalities.directions)
        
        #again
        fromBytesCabalities = Capabilities(bytes=fromBytesCabalitiesBytes, config=self.config)
        fromBytesCabalitiesBytes=fromBytesCabalities.toBytes()
        self.assertEqual(fromBytesCabalitiesBytes, b, "should be equal")
        self.assertTrue(fromBytesCabalities.hasCapability(
                                        robotType=Sensation.RobotType.Sense,
                                        memoryType=Sensation.MemoryType.Sensory,
                                        sensationType=Sensation.SensationType.Voice))
        self.assertEqual(self.capabilities.directions, fromBytesCabalities.directions)
      
        #change Locations
#         fromBytesCabalities.setLocations(ConfigTestCase.SET_1_1_LOCATIONS_1)
#         fromBytesCabalitiesBytes=fromBytesCabalities.toBytes()
#         self.assertNotEqual(fromBytesCabalitiesBytes, b, "should NOT be equal")
#         #should get equal byes, when same changed locations
#         fromBytesCabalities = Capabilities(bytes=fromBytesCabalitiesBytes, config=self.config)
#         fromBytesCabalitiesBytes2=fromBytesCabalities.toBytes()
#         self.assertEqual(fromBytesCabalitiesBytes, fromBytesCabalitiesBytes2, "should be equal")


    def testCapabilitiesString(self):
        s = self.capabilities.toString()
        print('capabilities.toString  ' + s)
        
        fromStringCabalities = Capabilities(string=s, config=self.config)
        fromStringCabalitiesString = fromStringCabalities.toString()
        self.assertEqual(fromStringCabalitiesString, s, "should be equal")
        
        #again
        fromStringCabalities = Capabilities(string=fromStringCabalitiesString, config=self.config)
        fromStringCabalitiesString = fromStringCabalities.toString()
        self.assertEqual(fromStringCabalitiesString, s, "should be equal")
        
        #change Locations
        # test removed, this will fail, because not implrmrntrf properly
#         fromStringCabalities.setLocations(ConfigTestCase.SET_1_1_LOCATIONS_1)
#         fromStringCabalitiesString=fromStringCabalities.toString()
#         self.assertNotEqual(fromStringCabalitiesString, s, "should NOT be equal")
#         #should get equal byes, when same changed locations
#         fromStringCabalities = Capabilities(bytes=fromStringCabalitiesString, config=self.config)
#         fromStringCabalitiesString2=fromStringCabalities.toString()
#         self.assertEqual(fromStringCabalitiesString, fromStringCabalitiesString2, "should be equal")

    '''
    capabilities don't have locations property.
    Config has its
    Robot has it.
    This test is deprecated
    '''
        

    def deprecatedtestLocations(self):
        #  single location from set 1 for capabilities
#         self.capabilities.setLocations(ConfigTestCase.SET_1_1_LOCATIONS_1)
        self.capabilities.setCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE,
                                        is_set= True)
        # test test
        self.assertTrue(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_1_1_LOCATIONS_1),
                                                        "should be True")
        # change to other single location
#         self.capabilities.setLocations(ConfigTestCase.SET_1_1_LOCATIONS_2)
        self.assertFalse(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                         locations=ConfigTestCase.SET_1_1_LOCATIONS_1),
                                                        "should be False")
        #  double location for capabilities
#         self.capabilities.setLocations(ConfigTestCase.SET_1_2_LOCATIONS)
        self.capabilities.setCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE,
                                        is_set= True)
        # test test
        self.assertTrue(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_1_1_LOCATIONS_1),
                                                        "should be True")
        # change to other single location
        self.assertTrue(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_1_1_LOCATIONS_2),
                                                        "should be True")
        # change to first single location in other set
        self.assertFalse(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_2_1_LOCATIONS_1),
                                                        "should be False")
        # change to other single location in other set
        self.assertFalse(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_2_1_LOCATIONS_2),
                                                        "should be False")
        
################################################################################################        
        # change capabilities location to single location from set 2
        #  single location from set 2 for capabilities
#         self.capabilities.setLocations(ConfigTestCase.SET_2_1_LOCATIONS_1)
        self.capabilities.setCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE,
                                        is_set= True)
        # test test
        self.assertTrue(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_2_1_LOCATIONS_1),
                                                        "should be True")
        # change to other single location
#         self.capabilities.setLocations(ConfigTestCase.SET_2_1_LOCATIONS_2)
        self.assertFalse(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_2_1_LOCATIONS_1),
                                                        "should be False")
        #  double location for capabilities
#         self.capabilities.setLocations(ConfigTestCase.SET_2_2_LOCATIONS)
        self.capabilities.setCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE,
                                        is_set= True)
        # test test
        self.assertTrue(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_2_1_LOCATIONS_1),
                                                        "should be True")
        # change to other single location
        self.assertTrue(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_2_1_LOCATIONS_2),
                                                        "should be True")
        # change to first single location in first set
        self.assertFalse(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_1_1_LOCATIONS_1),
                                                        "should be False")
        # change to other single location in other set
        self.assertFalse(self.capabilities.hasCapability(robotType=ConfigTestCase.TEST_DIRECTION,
                                                        memoryType=ConfigTestCase.TEST_MEMORYTYPE,
                                                        sensationType=ConfigTestCase.TEST_SENSATIONTYPE),
#                                                        locations=ConfigTestCase.SET_1_1_LOCATIONS_2),
                                                        "should be False")
        
        # change capabilities location to single location from set 2
       
if __name__ == '__main__':
    unittest.main()


# 
# 
#         self.robot=Robot()
#         self.memory = self.robot.getMemory()
#         
#         
#         self.sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
#                                                     name='test', score=MemoryTestCase.SCORE, presence=Sensation.Presence.Entering)
#         self.assertIs(self.sensation.getPresence(), Sensation.Presence.Entering, "should be entering")
#         self.assertIsNot(self.sensation, None)
#         self.assertIs(len(self.sensation.getAssociations()), 0)
#         #print('\nlogAssociations 1: setUp')
#         Sensation.logAssociations(self.sensation)
# 
# if __name__ == '__main__':
#     from Sensation import Sensation
#     cwd = os.getcwd()
#     print('cwd ' + cwd)
#     
#     # config
# 
#     config = Config()
#     b=config.toBytes()
#     config.fromBytes(b=b,section='bytes')
# 
#     string = config.toString()
#     config.fromString(string=string,section='string')
#     
#     instanceType= config.getInstanceType()
#     print('InstanceType ' + str(instanceType))
#  
#     kind= config.getKind()
#     print('Kind ' + str(kind))
#     
#     subInstanceNames = config.getSubInstanceNames()
#     print('subInstanceNames ' + str(subInstanceNames))
# 
#     remoteSubInstanceNames = config.getRemoteSubInstanceNames()
#     print('remoteSubInstanceNames ' + str(remoteSubInstanceNames))
# 
#     virtualInstanceNames = config.getVirtualInstanceNames()
#     print('VirtualInstanceNames ' + str(virtualInstanceNames))
#     
#     hostNames = config.getHostNames()
#     print('HostNames ' + str(hostNames))
# 
#     locations = config.getLocations()
#     print('Locations ' + str(locations))
# 
#     print(config.getCapabilities().toDebugString('Capabilities from config'))
#     test(name="Capabilities from config", capabilities=config.getCapabilities())
#    
#     #capabilities
#     print('')
#     locations=['testLocation']
#     capabilities = Capabilities(config=config)
#     test(name="Capabilities(config=config)", capabilities=capabilities)
#     capabilities.setCapability(robotType = Sensation.RobotType.Muscle,
#                                memoryType = Sensation.MemoryType.Sensory,
#                                sensationType = Sensation.SensationType.Voice,
#                                is_set = True)
#     test(name="Voice set", capabilities=capabilities)
#    
#     b = capabilities.toBytes()
#     print('capabilities.toBytes  ' + str(b))
#     test(name="before toBytes(fromBytes)", capabilities=capabilities)
#     capabilities.fromBytes(bytes=b)
#     test(name="after toBytes(fromBytes)", capabilities=capabilities)
#     b2 = capabilities.toBytes()
#     print('capabilities.toBytes2 ' + str(b))
#     print ('should be b == b2 True ', str(b==b2))
#     
#     capabilities2 = Capabilities(bytes=b, config=config)
#     test(name="capabilities original", capabilities=capabilities)
#     test(name="capabilities2 from bytes", capabilities=capabilities2)
#     b2 = capabilities2.toBytes()
#     print('b2 ' + str(b))
#     print ('should be b == b2 True ', str(b==b2))
#     print ('should be capabilities == capabilities2 True ', str(capabilities==capabilities2))
#     capabilities.toDebugString('capabilities')
#     capabilities2.toDebugString('capabilities2')
# 
#     
#     string = capabilities.toString()
#     print('string  ' + string)
#     capabilities.fromString(string=string)
#     string2 = capabilities.toString()
#     print('string2 ' + string2)
#     print ('should be string == string2 True ', str(string == string2))
#     
#     test(name="original", capabilities=capabilities)
#     capabilities2 = Capabilities(deepCopy=capabilities, config=config)
#     test(name="deepCopy", capabilities=capabilities2)
#     print ('should be deepCopy capabilities  == capabilities2 True ', str(capabilities == capabilities2))
#     capabilities.toDebugString('capabilities')
#     capabilities2.toDebugString('capabilities2')
# 
#     
#     #test
#     test(name="capabilities", capabilities=capabilities)
#     test(name="capabilities2", capabilities=capabilities2)
#  
#     # set all True 
#     print ("Set all True")
#     for robotType, directionStr in Sensation.Directions.items():
#         for memoryType, memoryStr in Sensation.MemoryTypes.items():
#             for sensationType, capabilityStr in Sensation.SensationTypes.items():
#                 capabilities.setCapability(robotType, memoryType, sensationType, True)
#     test(name="Set all True", capabilities=capabilities)
#     capabilities.And(other=capabilities2)
#     test(name="Set all True capabilities And capabilities2", capabilities=capabilities)
# 
#     for robotType, directionStr in Sensation.Directions.items():
#         for memoryType, memoryStr in Sensation.MemoryTypes.items():
#             for sensationType, capabilityStr in Sensation.SensationTypes.items():
#                 capabilities.setCapability(robotType, memoryType, sensationType, True)
#     capabilities.Or(other=capabilities2)
#     test(name="Set all True capabilities Or capabilities2", capabilities=capabilities)
# 
#      # set all False 
#     print ("Set all False")
#     for robotType, directionStr in Sensation.Directions.items():
#         for memoryType, memoryStr in Sensation.MemoryTypes.items():
#             for sensationType, capabilityStr in Sensation.SensationTypes.items():
#                 capabilities.setCapability(robotType, memoryType, sensationType, False)
#     test(name="Set all False", capabilities=capabilities)
#     capabilities.Or(other=capabilities2)
#     test(name="Set all False Or capabilities2", capabilities=capabilities)
# 
#     #config=Config()
#     capabilities=Capabilities(config=config)
#     test("default config", capabilities)
#     
#     bytes=config.toBytes(section="bytes")                
#     capabilities=Capabilities(bytes=bytes, config=config)
#     test("bytes", capabilities)
# 
#     string=config.toString()                
#     capabilities = Capabilities(string=string, config=config)
#     test("string", capabilities)
# 


