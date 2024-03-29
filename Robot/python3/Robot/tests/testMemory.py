'''
Created on 12.04.2020
Updated on 15.01.2022
@author: reijo.korhonen@gmail.com

test Memory class
python3 -m unittest tests/testMemory.py


'''
import time as systemTime
import os
import unittest
from Sensation import Sensation
from Robot import Robot
from Communication import Communication
from Memory import Memory

#duplicated from Communication because not yet guessed how to import this from
# Communication.py
COMMUNICATION_INTERVAL=60.0     # time window to history 
                                # for sensations we communicate


class MemoryTestCase(unittest.TestCase):
    TEST_RUNS = 2
    SCORE=0.5
    SCORE2=0.8
    
    NEUTRAL_FEELING = Sensation.Feeling.Neutral
    NORMAL_FEELING = Sensation.Feeling.Good
    BETTER_FEELING = Sensation.Feeling.Happy
    TERRIFIED_FEELING = Sensation.Feeling.Terrified
    
    YOUNGER_LONGTERM_ITEM_NAME =    "younger LongTerm bytes_test"
    OLDER_LONGTERM_ITEM_NAME =      "older LongTerm bytes_test"
    MAINNAMES = ["MemoryTestCaseMainName"]
    OTHERMAINNAMES = ["OTHER_MemoryTestCaseMainName"]
    LOCATIONS = ["MemoryTestCaseLocation1", "MemoryTestCaseLocation2"]
    SEARCH_LENGTH=20                # How many response voices we check
    SCORE_1 = 0.1
    SCORE_2 = 0.2
    SCORE_3 = 0.3
    SCORE_4 = 0.4
    SCORE_5 = 0.5
    SCORE_6 = 0.6
    SCORE_7 = 0.7
    SCORE_8 = 0.8
    NAME='Wall-E'
    NAME2='Eva'
    
    SensationDirectory=[]
    SensationDataDirectory=[]
  
    '''
    Sensation constructor for test purposes
    
    Parameters are exactly same than in default constructor
    but some parameters are added to do the job is added
    
    robot           robot to do the job
    sensationName   name for this Sensation, so we can log created sensation
                    so we can tell content of Robot's memory and tell
                    if something goes wrong in tested Communication Rpbot's
                    expected logic
                    
    sensationNames and created sensations are added to SensationDirectory
    '''
       
    def createSensation(self,
                 robot,
                 sensationName,
                 log=True,
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 
                  # base field are by default None, so we know what fields are given and what not
                 sensationType = None,
                 memoryType = None,
                 robotType = None,
                 locations =  None,
                 mainNames = None,
                 leftPower = None, rightPower = None,                        # Walle motors state
                 azimuth = None,                                             # Walle robotType relative to magnetic north pole
                 x=None, y=None, z=None, radius=None,                        # location and acceleration of Robot
                 hearDirection = None,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection = None,observationDistance = None,     # Walle's observation of something, relative to Walle
                 filePath = None,
                 data = None,                                                # ALSA voice is string (uncompressed voice information)
                 image = None,                                               # Image internal representation is PIl.Image 
                 calibrateSensationType = None,
                 capabilities = None,                                        # capabilitis of sensorys, robotType what way sensation go
                 name = None,                                                # name of Item
                 score = None,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence = None,                                            # presence of Item
                 kind = None,                                                # kind (for instance voice)
                 firstAssociateSensation = None,                             # associated sensation first side
                 otherAssociateSensation = None,                             # associated Sensation other side
                 feeling = None,                                             # feeling of sensation or association
                 positiveFeeling = None,                                     # change association feeling to more positive robotType if possible
                 negativeFeeling = None):                                    # change association feeling to more negative robotType if possible
        
        sensation = robot.createSensation(
                 log=log,
                 robot=self,
                 associations = associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 robotType=robotType,
                 #robot=robot,
                 locations=locations,
                 mainNames = mainNames, #self.getMainNames(),
                 leftPower = leftPower, rightPower = rightPower,
                 azimuth = azimuth,
                 x=x, y = y, z = z, radius=radius,
                 hearDirection = hearDirection,
                 observationDirection = observationDirection, observationDistance = observationDistance,
                 filePath = filePath,
                 data = data,
                 image = image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name = name,
                 score = score,
                 presence = presence,
                 kind = kind,
                 firstAssociateSensation = firstAssociateSensation,
                 otherAssociateSensation = otherAssociateSensation,
                 feeling = feeling,
                 positiveFeeling=positiveFeeling,
                 negativeFeeling=negativeFeeling)
            
        # if we get mainNames. overwrite Robots given mainNames
        if mainNames != None and len(mainNames) > 0:
            sensation.setMainNames(mainNames)
        # associate to self.Wall_E_item_sensation so all created Sensations
        # can be found associated to self.Wall_E_item_sensation.name.
        sensation.associate(sensation=self.Wall_E_item_sensation, feeling=feeling)

        # add sensation to directory, so we can find it's name by ids
        # deprecated
        # self.addToSensationDirectory(name=sensationName, dataId=sensation.getDataId(), id=sensation.getId())
        
        return sensation
        


    '''
    deprecated
    '''    
    # def addToSensationDirectory(self, name, dataId, id=None):
    #     if id != None:
    #         self.SensationDirectory.append((id, name))
    #     self.SensationDataDirectory.append((dataId, name))
    #
    # def getSensationNameById(self, note, dataId=None,id=None):
    #     assert(dataId is not None or id is not None)
    #     if dataId is not None:
    #         for did, name in self.SensationDataDirectory:
    #             if did == dataId:
    #                 return '{} | dataId {} | name: {}'.format(note, dataId, name)
    #     if id is not None:
    #         for iid, name in self.SensationDataDirectory:
    #             if iid == id:
    #                 return '{} | dataId {} | name: {}'.format(note, id, name)
    #     if dataId is not None:
    #         return'{} | dataId {} | was not found'.format(note, dataId)
    #     return'{} | id {} | was not found'.format(note, id)
    #
    # def printSensationNameById(self, note, dataId=None,id=None):
    #     print('\n{}\n'.format(self.getSensationNameById(note=note, dataId=dataId, id=id)))

    '''
    Clean data directory from bi9nary files files.
    Test needs this so known sensations are only created
    '''  
    def CleanDataDirectory(self):
        # load sensation data from files
        print('CleanDataDirectory')
        if os.path.exists(Sensation.DATADIR):
            try:
                for filename in os.listdir(Sensation.DATADIR):
                    if filename.endswith('.'+Sensation.BINARY_FORMAT) or\
                       filename.endswith('.'+Sensation.VOICE_FORMAT) or\
                       filename.endswith('.'+Sensation.IMAGE_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print('os.remove(' + filepath + ') error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
            except Exception as e:
                    print('os.listdir error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
        

    def setUp(self):
        self.CleanDataDirectory()
        self.robot=Robot(mainRobot=None)
        self.robot.mainNames=self.MAINNAMES #MAINNAMES # set mainnames for test
        self.robot.locations=self.LOCATIONS
        self.memory = self.robot.getMemory()
        # To test, we should know what is in memory, 
        # we should clear Sensation memory from binary files loaded sensation
#         del self.memory.sensationMemory[:]
        
#         
#         self.sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
#                                                     name='test', score=MemoryTestCase.SCORE, present=True)
#         self.assertEqual(self.sensation.getMainNames(), self.MAINNAMES)
#         self.assertEqual(self.sensation.isPresent(), Sensation.Presence.Entering, "should be entering")
#         self.assertIsNot(self.sensation, None)
#         self.assertEqual(len(self.sensation.getAssociations()), 0)
#         Sensation.logAssociations(self.sensation)
        
    def tearDown(self):
#         self.sensation.delete()
#         del self.memory.sensationMemory[:]
#         del self.memory._presentItemSensations[:]
        del self.robot
        
    def testPresence(self):
        history_sensationTime = systemTime.time() -2*COMMUNICATION_INTERVAL

        self.dotestPresence(sensationType=Sensation.SensationType.Item,
                            robotType=Sensation.RobotType.Sense,
                            presentDict=self.memory._presentItemSensations,
                            name='test',
                            time = history_sensationTime,
                            shouldSucceed=False)
        # TOO implementation is missing.
        # Robot.name presence
#         for name in self.MAINNAMES:
#             self.dotestPresence(sensationType=Sensation.SensationType.Robot,
#                                 robotType=Sensation.RobotType.Communication,
#                                 presentDict=self.memory._presentRobotSensations,
#                                 name=name)
        self.dotestPresence(sensationType=Sensation.SensationType.Robot,
                            robotType=Sensation.RobotType.Communication,
                            presentDict=self.memory._presentRobotSensations,
                            name=None)
        
        self.dotestPresence(sensationType=Sensation.SensationType.Robot,
                            robotType=Sensation.RobotType.Communication,
                            presentDict=self.memory._presentRobotSensations,
                            name=None,
                            mainNames=MemoryTestCase.OTHERMAINNAMES)
        
      
        
    def dotestPresence(self, sensationType, robotType, presentDict, name, mainNames=None, time=None, shouldSucceed=True):
        #del self.memory.sensationMemory[:]
        
        
        enteringSensation = self.robot.createSensation(time=time,
                                                       associations=None,
                                                       sensationType=sensationType,
                                                       robotType=robotType,
                                                       memoryType=Sensation.MemoryType.Working,
                                                       name=name,
                                                       score=MemoryTestCase.SCORE,
                                                       present=True,
                                                       locations=self.LOCATIONS,
                                                       mainNames=mainNames)
        self.assertEqual(len(enteringSensation.getAssociations()), 0)
        Sensation.logAssociations(enteringSensation)

        if mainNames == None:
            self.assertEqual(enteringSensation.getMainNames(), self.MAINNAMES)
        else:
            self.assertEqual(enteringSensation.getMainNames(), mainNames)
        self.assertEqual(enteringSensation.getLocations(), self.LOCATIONS)
        self.assertTrue(enteringSensation.isPresent(), "should be prenent")
        self.assertIsNot(enteringSensation, None)
        if name != None:
            if shouldSucceed:
                for location in self.LOCATIONS:        
                    self.assertTrue(location in presentDict)
                    self.assertTrue(name in presentDict[location])
            else:
                for location in self.LOCATIONS:        
                    if location in presentDict:
                        self.assertFalse(name in presentDict[location])
                
        else:
            # With local Robot presence, there is no presence, because local robot is not present for itself
            if mainNames == None:
                for location in self.LOCATIONS:        
                    self.assertFalse(location in presentDict)
            else:
            # With remote Robot presence, there is presence
                for location in self.LOCATIONS:        
                    self.assertTrue(location in presentDict)
                    for mainName in mainNames:
                        self.assertTrue(mainName in presentDict[location])

        presentSensation = self.robot.createSensation(associations=None,
                                                      sensationType=sensationType,
                                                      robotType=robotType,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      name=name, score=MemoryTestCase.SCORE, present=True,
                                                      locations=self.LOCATIONS,
                                                      mainNames=mainNames)
        if mainNames == None:
            self.assertEqual(presentSensation.getMainNames(), self.MAINNAMES)
        else:
            self.assertEqual(presentSensation.getMainNames(), mainNames)
        self.assertEqual(enteringSensation.getLocations(), self.LOCATIONS)
        self.assertTrue(presentSensation.isPresent(), "should be present")
        self.assertIsNot(presentSensation, None)
        self.assertEqual(len(presentSensation.getAssociations()), 0)
        Sensation.logAssociations(presentSensation)

        if name != None:
            for location in self.LOCATIONS:        
                self.assertTrue(location in presentDict)
                self.assertTrue(name in presentDict[location])
        else:
            if mainNames == None:
                for location in self.LOCATIONS:        
                    self.assertFalse(location in presentDict)
            else:
                for location in self.LOCATIONS:        
                    self.assertTrue(location in presentDict)
                    for mainName in mainNames:
                        self.assertTrue(mainName in presentDict[location])

        # exitingSensation = self.robot.createSensation(associations=None,
        #                                               sensationType=sensationType,
        #                                               robotType=robotType,
        #                                               memoryType=Sensation.MemoryType.Working,
        #                                               name=name, score=MemoryTestCase.SCORE, presence=Sensation.Presence.Exiting,
        #                                               locations=self.LOCATIONS,
        #                                               mainNames=mainNames)
        # if mainNames == None:
        #     self.assertEqual(enteringSensation.getMainNames(), self.MAINNAMES)
        # else:
        #     self.assertEqual(enteringSensation.getMainNames(), mainNames)
        # self.assertEqual(enteringSensation.getLocations(), self.LOCATIONS)
        # self.assertEqual(exitingSensation.isPresent(), Sensation.Presence.Exiting, "should be Exiting")
        # self.assertIsNot(exitingSensation, None)
        # self.assertEqual(len(exitingSensation.getAssociations()), 0)
        # Sensation.logAssociations(exitingSensation)
        #
        # if name != None:
        #     for location in self.LOCATIONS:        
        #         self.assertTrue(location in presentDict)
        #         self.assertTrue(name in presentDict[location])
        # else:
        #     if mainNames == None:
        #         for location in self.LOCATIONS:        
        #             self.assertFalse(location in presentDict)
        #     else:
        #         for location in self.LOCATIONS:        
        #             self.assertTrue(location in presentDict)
        #             for mainName in mainNames:
        #                 self.assertTrue(mainName in presentDict[location])
        
        absentSensation = self.robot.createSensation(associations=None,
                                                     sensationType=sensationType,
                                                     robotType=robotType,
                                                     memoryType=Sensation.MemoryType.Working,
                                                     name=name, score=MemoryTestCase.SCORE, present=False,
                                                     locations=self.LOCATIONS,
                                                      mainNames=mainNames)
        if mainNames == None:
            self.assertEqual(enteringSensation.getMainNames(), self.MAINNAMES)
        else:
            self.assertEqual(enteringSensation.getMainNames(), mainNames)
        self.assertEqual(enteringSensation.getLocations(), self.LOCATIONS)
        self.assertFalse(absentSensation.isPresent(), "should be Absent")
        self.assertIsNot(absentSensation, None)
        self.assertEqual(len(absentSensation.getAssociations()), 0)
        Sensation.logAssociations(absentSensation)

        if name != None:
            for location in self.LOCATIONS:        
                self.assertTrue(location in presentDict)
                self.assertFalse(name in presentDict[location])
        else:
            if mainNames == None:
                for location in self.LOCATIONS:        
                    self.assertFalse(location in presentDict)
            else:
                for location in self.LOCATIONS:        
                    self.assertTrue(location in presentDict)
                    for mainName in mainNames:
                        self.assertFalse(mainName in presentDict[location])
        
    def test_Memorybility(self):
        sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                    name='test', score=MemoryTestCase.SCORE, present=True)
        self.assertEqual(sensation.getMainNames(), self.MAINNAMES)
        self.assertTrue(sensation.isPresent(), "should be present")
        self.assertIsNot(sensation, None)
        self.assertEqual(len(sensation.getAssociations()), 0)
        Sensation.logAssociations(sensation)
        
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working, name='Working_test',present=False)
        self.assertFalse(workingSensation.isPresent(), "should be Absent")
        self.assertIsNot(workingSensation, None)
        self.assertEqual(len(workingSensation.getAssociations()), 0)

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name='LongTerm',present=False)
        self.assertFalse(longTermSensation.isPresent(), "should be Absent")
        self.assertIsNot(longTermSensation, None)
        self.assertEqual(len(longTermSensation.getAssociations()), 0)

        print("\nSensory time now")
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working time now")
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("LongTerm time now")
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() > workingSensation.getMemorability(), 'now Sensory sensation must be more Memorability than Working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'now Working sensation must be more Memorability than LongTerm sensation')

        # set sensation to the past and look again  
        history_time = Sensation.sensationMemoryLiveTimes[sensation.getMemoryType()] * 0.5      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'half Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensation.getMemoryType()] * 0.8      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() < workingSensation.getMemorability(), 'near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensation.getMemoryType()] * 0.98      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() < workingSensation.getMemorability(), 'very near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'very near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.5      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'half working lifetime Working sensation must be more than zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'half working lifetime LongTerm sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.8      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
         # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.95      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very near working lifetime Working sensation must be less Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.98      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very very near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 1.05      
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.5     
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.98     
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'very very near long term lifetime Sensory sensation must still be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 1.02     
        sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType()) " + str(Sensation.getLiveTimeLeftRatio(time=sensation.getTime(), memoryType=sensation.getMemoryType())))
        print("sensation.getMemorability() " + str(sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=workingSensation.getTime(), memoryType=workingSensation.getMemoryType())))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(Sensation.getLiveTimeLeftRatio(time=longTermSensation.getTime(), memoryType=longTermSensation.getMemoryType())))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  == 0.0, 'beyond end long term lifetime Sensory sensation must be zero')
        
    '''
    deprecated
    
    Test importance
    
    We use Sensation.SensationType.Image in this test, because
    Memory keeps track of presence, so We get many instances of
    Sensation.SensationType.Item
    Anyway we are searching Images and Voices per Item.name
    and Importance, but newer Item-names 
    '''    

#     def re_test_Importance(self):        
#         print("\ntest_Importance")
#         
#         
#         #memoryType=Sensation.MemoryType.Sensory
#         sensorySensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory,
#                                                       name='Working_Importance_test', score=MemoryTestCase.SCORE, present=True)
#         self.assertIsNot(sensorySensation, None)
#         self.assertEqual(sensorySensation.getPresence(), Sensation.Presence.Present, "should be present")
#         self.assertEqual(len(sensorySensation.getAssociations()), 0) # variates
#         sensorySensation.associate(sensation=self.sensation,
#                                    feeling=MemoryTestCase.NORMAL_FEELING)
#         Sensation.logAssociations(sensorySensation)
#         self.assertEqual(len(sensorySensation.getAssociations()), 1)
#         sensoryAssociation = self.sensation.getAssociation(sensation=sensorySensation)
#         self.assertIsNot(sensoryAssociation, None)
#         
#         self.do_test_Importance(sensation=sensorySensation, association=sensoryAssociation)
#         
#         #memoryType=Sensation.MemoryType.Working
#         workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Working,
#                                                       name='Working_Importance_test', score=MemoryTestCase.SCORE, present=True)
#         self.assertIsNot(workingSensation, None)
#         self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Present, "should be present")
#         self.assertEqual(len(workingSensation.getAssociations()), 0) # variates
#         workingSensation.associate(sensation=self.sensation,
#                                    feeling=MemoryTestCase.NORMAL_FEELING)
#         Sensation.logAssociations(workingSensation)
#         self.assertEqual(len(workingSensation.getAssociations()), 1)
#         workingAssociation = self.sensation.getAssociation(sensation=workingSensation)
#         self.assertIsNot(workingAssociation, None)
#         
#         self.do_test_Importance(sensation=workingSensation, association=workingAssociation)
# 
#         #memoryType=Sensation.MemoryType.LongTerm
#         longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.LongTerm,
#                                                       name='LongTerm_Importance_test', score=MemoryTestCase.SCORE, present=True)
#         self.assertIsNot(longTermSensation, None)
#         self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Present, "should be present")
#         #self.assertEqual(len(longTermSensation.getAssociations()), 0) # variates
#         longTermSensation.associate(sensation=self.sensation,
#                                    feeling=MemoryTestCase.NORMAL_FEELING)
#         Sensation.logAssociations(longTermSensation)
#         self.assertEqual(len(longTermSensation.getAssociations()), 1) # variates
#         longTermAssociation = self.sensation.getAssociation(sensation=longTermSensation)
#         self.assertIsNot(longTermAssociation, None)
#         
#         self.do_test_Importance(sensation=longTermSensation, association=longTermAssociation)
#         longTermSensation.delete()# remove associations
#         self.assertEqual(len(longTermSensation.getAssociations()), 0)
# 
#     '''
#         Communication uses Sensation.getImportance() so it is most important to test
#         TODO Study parameters getImportance(self, positive=True, negative=False, absolute=False)
#         default is positive=True and it is fine for Communication use to find best positive choice
#         Assosiation.getImportance() is curiosite    
#     '''   
#     def do_test_Importance(self, sensation, association):        
#         print("\ndo_test_Importance")
# 
#         # Normal feeling
#         association.setFeeling(feeling=MemoryTestCase.NORMAL_FEELING)
#         print("MemoryTestCase.NORMAL_FEELING association.getImportance() " + str(association.getImportance()))
#         self.assertTrue(association.getImportance() > 0.0, "association importance must greater than zero")
#         print("MemoryTestCase.NORMAL_FEELING sensation.getImportance() " + str(sensation.getImportance()))
#         self.assertTrue(sensation.getImportance() > 0.0, "sensation now importance must greater than zero")
#         normalAssociationImportance = association.getImportance()
#         normalSensationImportance = sensation.getImportance()
#  
#         #Compare Normal and Better feelings importance of Sensations
#         association.setFeeling(feeling=MemoryTestCase.BETTER_FEELING)
#         betterAssociationImportance = association.getImportance()
#         betterSensationImportance = sensation.getImportance()
#         
#         print("MemoryTestCase.BETTER_FEELING betterAssociationImportance {}".format(betterAssociationImportance))
#         print("MemoryTestCase.BETTER_FEELING betterSensationImportance {}".format(betterSensationImportance))
#         self.assertTrue(betterAssociationImportance > normalAssociationImportance, "better feeling association importance must greater than normal feeling")
#         self.assertTrue(betterSensationImportance > normalSensationImportance, "better feeling sensation now importance must greater than normal feeling")
#         
#         #Compare Terrified with Normal and Better feelings importance of Sensations    
#         association.setFeeling(feeling=MemoryTestCase.TERRIFIED_FEELING)
#         terrifiedAssociationImportance = association.getImportance()
#         terrifiedSensationImportance = sensation.getImportance()
#         
#         print("MemoryTestCase.TERRIFIED_FEELING terrifiedAssociationImportance {}".format(terrifiedAssociationImportance))
#         print("MemoryTestCase.TERRIFIED_FEELING terrifiedSensationImportance {}".format(terrifiedSensationImportance))
#         self.assertTrue(terrifiedAssociationImportance < normalAssociationImportance, "terrified feeling association importance must smaller than normal feeling")
#         self.assertTrue(terrifiedAssociationImportance < betterAssociationImportance, "terrified feeling association importance must smaller than better feeling")
#         self.assertTrue(terrifiedSensationImportance < normalAssociationImportance, "terrified feeling sensation now importance must smaller than normal feeling")
#         self.assertTrue(terrifiedSensationImportance < betterSensationImportance, "terrified feeling sensation now importance must smaller than better feeling")
#        
#         # set sensation more to the past and look again
#         history_time = Sensation.sensationMemoryLiveTimes[sensation.getMemoryType()] * 0.5      
#         sensation.setTime(systemTime.time() - history_time)
#         association.setTime(systemTime.time() - history_time)
#         
#         # terrified
#         historyTerrifiedAssociationImportance = association.getImportance()
#         historyTerrifiedSensationImportance = sensation.getImportance()
#         print("historyTerrifiedAssociationImportance {}".format(historyTerrifiedAssociationImportance))
#         print("historyTerrifiedSensationImportance {}".format(historyTerrifiedSensationImportance))
#         self.assertTrue(historyTerrifiedAssociationImportance < betterAssociationImportance, "terrified feeling association importance must smaller than better feeling")
#         self.assertTrue(historyTerrifiedAssociationImportance < normalAssociationImportance, "terrified feeling association importance must smaller than normal feeling")
#         self.assertTrue(historyTerrifiedSensationImportance < normalAssociationImportance, "terrified feeling sensation now importance must smaller than normal feeling")
#         self.assertTrue(historyTerrifiedSensationImportance < betterSensationImportance, "terrified feeling sensation now importance must smaller than better feeling")
# 
#         # history importance of Sensations should be higher than current because it is negative
#         # and when time has been going on, things don't feel so terrified that they were, when happened 
#         self.assertTrue(terrifiedAssociationImportance == historyTerrifiedAssociationImportance, "history terrified feeling association importance must smaller than current normal feeling")
#         self.assertTrue(terrifiedSensationImportance < historyTerrifiedSensationImportance, "history terrified feeling sensation importance must smaller than current normal feeling")
#  
#         # Normal       
#         #Compare Normal and history Better feelings importance of Sensations, history better should still be better
#         association.setFeeling(feeling=MemoryTestCase.NORMAL_FEELING)
#         # must set time back to history
#         association.setTime(systemTime.time() - history_time)
#         sensation.setTime(systemTime.time() - history_time)
#         # test
#         historyNormalAssociationImportance = association.getImportance()
#         historyNormaSensationImportance = sensation.getImportance()
#         print("historyNormalAssociationImportance {}".format(historyNormalAssociationImportance))
#         print("historyNormaSensationImportance {}".format(historyNormaSensationImportance))
#         
#         self.assertTrue(normalAssociationImportance == historyNormalAssociationImportance, "history and current association importances are equal")
#         self.assertTrue(normalSensationImportance > historyNormaSensationImportance, "history importance is lower than current one.")
#         self.assertTrue(historyTerrifiedSensationImportance < historyNormaSensationImportance, "history terrified importance is lower than normal history one.")
#         self.assertTrue(historyTerrifiedSensationImportance < normalSensationImportance, "history terrified importance is lower than normal current one.")
# 
#         # Better      
#         #Compare Normal and history Better feelings importance of Sensations, history better should still be better
#         association.setFeeling(feeling=MemoryTestCase.BETTER_FEELING)
#         # must set time back to history
#         association.setTime(systemTime.time() - history_time)
#         sensation.setTime(systemTime.time() - history_time)
#         # test
#         historyBetterAssociationImportance = association.getImportance()
#         historyBetterWorkingSensationImportance = sensation.getImportance()
#         self.assertTrue(betterAssociationImportance == historyBetterAssociationImportance, "history and current association importances are equal")
#         self.assertTrue(betterSensationImportance > historyBetterWorkingSensationImportance, "history importance is lower than current one.")
#         self.assertTrue(historyTerrifiedSensationImportance < historyBetterWorkingSensationImportance, "history terrified importance is lower than Better history one.")
#         self.assertTrue(historyTerrifiedSensationImportance < betterSensationImportance, "history terrified importance is lower than normal current one.")
#         self.assertTrue(historyNormaSensationImportance < historyBetterAssociationImportance, "history normal importance is lower than history normal one.")       


    def test_AddAssociations(self):
        sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                    name='test', score=MemoryTestCase.SCORE, present=True)
        self.assertEqual(sensation.getMainNames(), self.MAINNAMES)
        self.assertTrue(sensation.isPresent(),  "should be present")
        self.assertIsNot(sensation, None)
        self.assertEqual(len(sensation.getAssociations()), 0)
        Sensation.logAssociations(sensation)
        

        # We can run do_test_AddAssociation omce, because present items associations are copied from one present item no next item
        #when presence will remain, but present state changes (entering,prenent, exiting)        
        # for i in range(MemoryTestCase.TEST_RUNS):
        #     self.do_test_AddAssociation(sensation)
        self.do_test_AddAssociation(sensation)

        
    def do_test_AddAssociation(self, sensation):
        # test this test
        self.assertEqual(sensation.getScore(), MemoryTestCase.SCORE)
        
        # when we create sensation=sensation, other parameters can't be used
        addSensation = self.robot.createSensation(associations=None, sensation=sensation)
        self.assertIsNot(addSensation, None)
        addSensation.setName(name='connect_test')
        self.assertEqual(addSensation.getName(), 'connect_test', "should be \'connect_test\' ")
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        
        self.assertEqual(addSensation.getMemoryType(), Sensation.MemoryType.Working, "should be Sensation.MemoryType.Working")
        addSensation.setPresent(present=True)
        self.assertTrue(addSensation.isPresent(), "should be present")
        
        addSensation.setName('connect_test')
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        addSensation.save()    # this is worth to save its data
        associationNumber = len(sensation.getAssociations())
        #print('\nlogAssociations 2: test_AddAssociation')
        Sensation.logAssociations(addSensation)
        
        sensation.associate(sensation=addSensation,
                                 feeling=MemoryTestCase.NORMAL_FEELING)

        self.assertEqual(len(sensation.getAssociations()), associationNumber+1)
        self.assertEqual(sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(sensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(sensation), MemoryTestCase.NORMAL_FEELING)

        # test bytes        
        bytes=sensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesSensation != None, "fromBytesSensation should be created")
        self.assertTrue(fromBytesSensation == sensation, "fromBytesSensation should be equal")
       
        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        
        # test bytes        
        bytes=addSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)

        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        # TODO if we copy present item connections from old renent item, then we can't test like this,
        # But should feelings be transferred by bytes? 
        self.assertEqual(fromBytesSensation.getAssociationFeeling(sensation), MemoryTestCase.NORMAL_FEELING)
       
        # TODO rest if the test

        #print('\nlogAssociations 5: test_AddAssociation')
        Sensation.logAssociations(sensation)
        # again, should not add association twice
        sensation.addAssociation(Sensation.Association(self_sensation=sensation,
                                                            sensation=addSensation,
#                                                            score=MemoryTestCase.SCORE2,
                                                            feeling=MemoryTestCase.TERRIFIED_FEELING))
        self.assertEqual(len(sensation.getAssociations()), associationNumber+1)
        self.assertEqual(sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(sensation.getAssociationFeeling(addSensation), MemoryTestCase.TERRIFIED_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(sensation), MemoryTestCase.TERRIFIED_FEELING)

        #print('\nlogAssociations 6: test_AddAssociation')
        Sensation.logAssociations(sensation)
        
        # better feeling
        addAssociation = addSensation.getAssociation(sensation)
        self.assertIsNot(addAssociation, None)

        # change feeling in association        
        addAssociation.setFeeling(MemoryTestCase.BETTER_FEELING)
        # and it should be changed in both way association in both ways
        self.assertEqual(sensation.getAssociationFeeling(addSensation), MemoryTestCase.BETTER_FEELING)
        self.assertEqual(addSensation.getAssociationFeeling(sensation), MemoryTestCase.BETTER_FEELING)
        
    '''
    Test auto association
    Test that when we have Item.name present,
    then Voice and Image sensations are associated to it, when created in
    short time window enough
    '''
        
    def test_AutoAssociations(self):
        name='test'
        
        # For a voice
        itemSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                   name=name, score=MemoryTestCase.SCORE, present=True,
                                                   locations=self.LOCATIONS)
        self.assertIsNot(itemSensation, None)
        self.assertEqual(itemSensation.getMainNames(), self.MAINNAMES)
        self.assertTrue(itemSensation.isPresent(), "should be present")
        self.assertEqual(len(itemSensation.getAssociations()), 0)
        Sensation.logAssociations(itemSensation)
        
        locations = itemSensation.getLocations()
        self.assertTrue(len(locations) > 0)
        
        for location in locations:
            self.assertTrue(itemSensation is self.memory._presentItemSensations[location][name])
        
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory,
                                                    locations=self.LOCATIONS)
        self.assertIsNot(voiceSensation, None)
        self.assertEqual(voiceSensation.getMainNames(), self.MAINNAMES)
        self.assertEqual(len(voiceSensation.getAssociations()), 1)
        self.assertEqual(len(itemSensation.getAssociations()), 1)
        Sensation.logAssociations(voiceSensation)
        
        # For a Image
        # NOTE, when simplyfied presence, this will not update presence
        # itemSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
        #                                            name=name, score=MemoryTestCase.SCORE, present=True,
        #                                            locations=self.LOCATIONS)
        # self.assertIsNot(itemSensation, None)
        # self.assertEqual(itemSensation.getMainNames(), self.MAINNAMES)
        # self.assertTrue(itemSensation.isPresent(), "should be present")
        # self.assertEqual(len(itemSensation.getAssociations()), 1)
        # self.assertEqual(len(itemSensation.getAssociations()), i)
        # Sensation.logAssociations(itemSensation)
        #
        # locations = itemSensation.getLocations()
        # self.assertTrue(len(locations) > 0)
        #
        # for location in locations:
        #     self.assertTrue(itemSensation is self.memory._presentItemSensations[location][name])
        # # new itemSensation should nor contaim old itemSensation associations
        # self.assertEqual(len(itemSensation.getAssociations()), 1)
        # self.assertEqual(len(voiceSensation.getAssociations()), 2)

        
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory,
                                                    locations=self.LOCATIONS)
        self.assertIsNot(imageSensation, None)
        self.assertEqual(imageSensation.getMainNames(), self.MAINNAMES)
        self.assertEqual(len(imageSensation.getAssociations()), 1)
        self.assertEqual(len(itemSensation.getAssociations()), 2)
        Sensation.logAssociations(imageSensation)


    def test_Feeling(self):
        for i in range(MemoryTestCase.TEST_RUNS):
            self.do_test_Feeling()

        
    def do_test_Feeling(self):
        # test this test
        sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                    name='test', score=MemoryTestCase.SCORE, present=True)
        self.assertEqual(sensation.getMainNames(), self.MAINNAMES)
        self.assertTrue(sensation.isPresent(), "should be present")
        self.assertIsNot(sensation, None)
        self.assertTrue(len(sensation.getAssociations()) in (0,1)) # 0/1?
        Sensation.logAssociations(sensation)
                
        self.assertEqual(sensation.getScore(), MemoryTestCase.SCORE)
        
        # when we create sensation=sensation, other parameters can't be used
        addSensation = self.robot.createSensation(associations=None, sensation=sensation)
        self.assertIsNot(addSensation, None)
        
        addSensation.setName(name='connect_test')
        self.assertEqual(addSensation.getName(), 'connect_test', "should be \'connect_test\' ")
        
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        self.assertEqual(addSensation.getMemoryType(), Sensation.MemoryType.Working, "should be Sensation.MemoryType.Working")
        
        addSensation.setPresent(present=True)
        self.assertTrue(addSensation.isPresent(), "should be present")
        
        addSensation.setName('connect_test')
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        addSensation.save()    # this is worth to save its data
        associationNumber = len(sensation.getAssociations())
        #print('\nlogAssociations 2: test_AddAssociation')
        Sensation.logAssociations(addSensation)
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=sensation, otherAssociateSensation=addSensation,
                                                      feeling=MemoryTestCase.NORMAL_FEELING)
        self.memory.process(sensation=feelingSensation)
        

        self.assertEqual(len(sensation.getAssociations()), associationNumber+1)
        self.assertEqual(sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(sensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(sensation), MemoryTestCase.NORMAL_FEELING)

        # test bytes        
        bytes=sensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesSensation != None, "fromBytesSensation should be created")
        self.assertTrue(fromBytesSensation == sensation, "fromBytesSensation should be equal")
       
        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        
        # test bytes        
        bytes=addSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)

        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(sensation), MemoryTestCase.NORMAL_FEELING)
       
        # TODO rest if the test

        #print('\nlogAssociations 5: test_AddAssociation')
        Sensation.logAssociations(sensation)
        # again, should not add association twice
#         sensation.addAssociation(Sensation.Association(self_sensation=sensation,
#                                                             sensation=addSensation,
# #                                                            score=MemoryTestCase.SCORE2,
#                                                             feeling=MemoryTestCase.TERRIFIED_FEELING))
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=sensation, otherAssociateSensation=addSensation,
                                                      feeling=MemoryTestCase.TERRIFIED_FEELING)
        self.memory.process(sensation=feelingSensation)
        
        self.assertEqual(len(sensation.getAssociations()), associationNumber+1)
        self.assertEqual(sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(sensation.getAssociationFeeling(addSensation), MemoryTestCase.TERRIFIED_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(sensation), MemoryTestCase.TERRIFIED_FEELING)

        #print('\nlogAssociations 6: test_AddAssociation')
        Sensation.logAssociations(sensation)
        
        # better feeling
        addAssociation = addSensation.getAssociation(sensation)
        self.assertIsNot(addAssociation, None)

        # change feeling in association        
#         addAssociation.setFeeling(MemoryTestCase.BETTER_FEELING)
        # and it should be changed in both way association in both ways
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=sensation, otherAssociateSensation=addSensation,
                                                      feeling=MemoryTestCase.BETTER_FEELING)
        self.memory.process(sensation=feelingSensation)

        self.assertEqual(sensation.getAssociationFeeling(addSensation), MemoryTestCase.BETTER_FEELING)
        self.assertEqual(addSensation.getAssociationFeeling(sensation), MemoryTestCase.BETTER_FEELING)

    def test_Bytes(self):        
        print("\ntest_Bytes")
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working, name='Working_Importance_test',present=True, receivedFrom=[])
        self.assertTrue(workingSensation != None, "should be created")
        numberofInstances=0
        for sensation in self.robot.getMemory().sensationMemory:
            if sensation.getId() == workingSensation.getId():
                numberofInstances = numberofInstances+1
        self.assertEqual(numberofInstances, 1, "in Memory should be 1 workingSensation instance before testing bytes")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertEqual(fromBytesWorkingSensation, workingSensation, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getId(), workingSensation.getId(), "should be equal")
        self.assertEqual(self.robot.getMemory().getSensationFromSensationMemory(fromBytesWorkingSensation.getId()).getId(), workingSensation.getId(), "should be equal")
        # TODO Feeling
        numberofInstances=0
        for sensation in self.robot.getMemory().sensationMemory:
            if sensation.getId() == workingSensation.getId():
                numberofInstances = numberofInstances+1
        self.assertEqual(numberofInstances, 1, "in Memory should still be 1 workingSensation instance after creating sensation from bytes")
                

        receivedFrom=['127.0.0.1', '192.168.0.0.1', '10.0.0.1']
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working, name='Working_Importance_test',present=True, receivedFrom=receivedFrom)
        self.assertTrue(workingSensation != None, "should be created")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertTrue(fromBytesWorkingSensation == workingSensation, "should be equal")
        self.assertTrue(fromBytesWorkingSensation.getReceivedFrom() == receivedFrom, "should be equal")

        data=b'\x01\x02'
        locations='testLocation'
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=locations, kind=Sensation.Kind.Eva)

        self.assertFalse(voiceSensation.isForgettable(), "should be False, until detached")
        voiceSensation.detach(robot=self.robot)
        self.assertTrue(voiceSensation.isForgettable(), "should be True after detach")

        self.assertTrue(voiceSensation.getKind() == Sensation.Kind.Eva, "should be equal")
        bytes=voiceSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesVoiceSensation = self.robot.createSensation(bytes=bytes)
        
        
        self.assertEqual(voiceSensation, fromBytesVoiceSensation, "should be equal")
        self.assertEqual(voiceSensation.getKind(), fromBytesVoiceSensation.getKind(), "should be equal")
        self.assertEqual(voiceSensation.getData(), fromBytesVoiceSensation.getData(), "should be equal")
        self.assertEqual(voiceSensation.getLocations(), fromBytesVoiceSensation.getLocations(), "should be equal")
       
        self.assertFalse(fromBytesVoiceSensation.isForgettable(), "should be False, until detached")
        fromBytesVoiceSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesVoiceSensation.isForgettable(), "should be True after detach")
 
        # Image
        
        locations='testLocation2'
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory, data=data, locations=locations, kind=Sensation.Kind.Eva)

        self.assertFalse(imageSensation.isForgettable(), "should be False, until detached")
        imageSensation.detach(robot=self.robot)
        self.assertTrue(imageSensation.isForgettable(), "should be True after detach")

        bytes=imageSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesImageSensation = self.robot.createSensation(bytes=bytes)

        self.assertTrue(imageSensation == fromBytesImageSensation, "should be equal")
        self.assertTrue(imageSensation.getImage() == fromBytesImageSensation.getImage(), "should be equal") # empty image, not given in creation, TODO
        self.assertTrue(imageSensation.getLocations() == fromBytesImageSensation.getLocations(), "should be equal")
        
        self.assertFalse(fromBytesImageSensation.isForgettable(), "should be False, until detached")
        fromBytesImageSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesImageSensation.isForgettable(), "should be True after detach")

        # Normal Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      feeling=MemoryTestCase.NORMAL_FEELING)
        bytes=feelingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesFeelingSensation = self.robot.createSensation(bytes=bytes)
                
        self.assertTrue(feelingSensation == fromBytesFeelingSensation, "should be equal")
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromBytesFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromBytesFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getFeeling() == fromBytesFeelingSensation.getFeeling(), "should be equal")        
        self.assertEqual(fromBytesFeelingSensation.getFeeling(), MemoryTestCase.NORMAL_FEELING, "should be equal")        
        
        self.assertFalse(fromBytesFeelingSensation.isForgettable(), "should be False, until detached")
        fromBytesFeelingSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesFeelingSensation.isForgettable(), "should be True after detach")
 
        # Better Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      positiveFeeling=True)
        bytes=feelingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesFeelingSensation = self.robot.createSensation(bytes=bytes)
                
        self.assertTrue(feelingSensation == fromBytesFeelingSensation, "should be equal")
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromBytesFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromBytesFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getPositiveFeeling(), "should be True")        
        self.assertFalse(feelingSensation.getNegativeFeeling(), "should be False")        
        #self.assertTrue(feelingSensation.getFeeling() == MemoryTestCase.NORMAL_FEELING, "should be equal")        
        self.assertTrue(fromBytesFeelingSensation.getPositiveFeeling(), "should be True")        
        self.assertFalse(fromBytesFeelingSensation.getNegativeFeeling(), "should be False")        
        
        # Worse Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      negativeFeeling=True)
        self.assertFalse(feelingSensation.isForgettable(), "should be False, until detached")

        bytes=feelingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesFeelingSensation = self.robot.createSensation(bytes=bytes)
                
        self.assertTrue(feelingSensation == fromBytesFeelingSensation, "should be equal")
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromBytesFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromBytesFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertFalse(feelingSensation.getPositiveFeeling(), "should be False")        
        self.assertTrue(feelingSensation.getNegativeFeeling(), "should be True") 
        
        self.assertFalse(fromBytesFeelingSensation.getPositiveFeeling(), "should be False")        
        self.assertTrue(fromBytesFeelingSensation.getNegativeFeeling(), "should be True")        
               
        #self.assertTrue(feelingSensation.getFeeling() == MemoryTestCase.NORMAL_FEELING, "should be equal")        

        self.assertFalse(fromBytesFeelingSensation.isForgettable(), "should be False, until detached")
        fromBytesFeelingSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesFeelingSensation.isForgettable(), "should be True after detach")
        
        # Test that younger LongTerm sensation overwrites younger Sensation
        youngerLongTermSensation = self.robot.createSensation(time = systemTime.time()+10.0,
                                                              associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.YOUNGER_LONGTERM_ITEM_NAME,present=True, receivedFrom=receivedFrom)
        self.assertTrue(youngerLongTermSensation != None, "should be created")
        self.assertTrue(youngerLongTermSensation.getTime() > systemTime.time(), "should be younger than present")

        olderLongTermSensation = self.robot.createSensation(time = systemTime.time()-10.0,
                                                              associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.OLDER_LONGTERM_ITEM_NAME,present=True, receivedFrom=receivedFrom)
        self.assertTrue(olderLongTermSensation != None, "should be created")
        self.assertTrue(olderLongTermSensation.getTime() <  systemTime.time(), "should be older than present")
        
        # make same id so we have two copies of same Sensation
        olderLongTermSensation.setId(youngerLongTermSensation.getId())
        self.assertEqual(olderLongTermSensation,  youngerLongTermSensation, "should be kept equal")

        # try update older with younger, should succeed
        bytes=youngerLongTermSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromByteslongTermSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromByteslongTermSensation != None, "should be created")
        self.assertTrue(fromByteslongTermSensation == youngerLongTermSensation, "should be equal")
        self.assertTrue(fromByteslongTermSensation.getReceivedFrom() == receivedFrom, "should be equal")
        #but item name should come from newer one
        self.assertEqual(fromByteslongTermSensation.getName(),  youngerLongTermSensation.getName(), "name should be from younger")

        # try update younger with older
        bytes=olderLongTermSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromByteslongTermSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromByteslongTermSensation != None, "should be created")
        self.assertTrue(fromByteslongTermSensation == olderLongTermSensation, "should be equal")
        self.assertTrue(fromByteslongTermSensation.getReceivedFrom() == receivedFrom, "should be equal")
        #but item name should come from newer one
        self.assertEqual(fromByteslongTermSensation.getName(),  youngerLongTermSensation.getName(), "name should be from younger")
        
        # same test, but keep sensation same exactly same but change association time to get younger and older sensation
        # make same id so we have two copies of same Sensation
        # at this point we have only one copy os sensation in memory
        # make new older sensation and association to it
        # make associations to younger one
        
        olderVoiceSensation = self.robot.createSensation(#time = systemTime.time()-5.0,
                                                         associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=locations, kind=Sensation.Kind.Eva)
        olderLongTermSensation = self.robot.createSensation(#time = systemTime.time()-10.0,
                                                            associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.OLDER_LONGTERM_ITEM_NAME,present=True, receivedFrom=receivedFrom)
        self.assertTrue(olderLongTermSensation != None, "should be created")
        self.assertTrue(olderLongTermSensation.getTime() <  systemTime.time(), "should be older than present")
        
        olderLongTermSensation.associate(sensation=olderVoiceSensation,
                                         feeling=MemoryTestCase.NORMAL_FEELING)
        self.assertTrue(len(olderLongTermSensation.getAssociations()) in [1,2]) # variates
        olderAssociation = olderLongTermSensation.getAssociation(sensation=olderVoiceSensation)
        self.assertTrue(olderAssociation.getTime() <  systemTime.time(), "should be older than present")

        # create now younger sensation and association
        youngerVoiceSensation = self.robot.createSensation(#time = systemTime.time()-2.0,
                                                           associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=locations, kind=Sensation.Kind.Eva)
        youngerLongTermSensation = self.robot.createSensation(#time = systemTime.time()-1.0,
                                                              associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.OLDER_LONGTERM_ITEM_NAME,present=True, receivedFrom=receivedFrom)
        self.assertTrue(youngerLongTermSensation != None, "should be created")
        self.assertTrue(youngerLongTermSensation.getTime() <  systemTime.time(), "should be older than present")
        
        youngerLongTermSensation.associate(sensation=youngerVoiceSensation,
                                          feeling=MemoryTestCase.NORMAL_FEELING)
        self.assertTrue(len(youngerLongTermSensation.getAssociations()) in [1,2]) # variates
        youngerAssociation = youngerLongTermSensation.getAssociation(sensation=youngerVoiceSensation)
        self.assertTrue(youngerAssociation.getTime() <  systemTime.time(), "should be older than present")
        
        #compare times
        self.assertTrue(olderAssociation.getTime() <  youngerLongTermSensation.getTime(), "older {} should be older than younger {}".format(olderAssociation.getTime(), youngerLongTermSensation.getTime()))
        self.assertTrue(olderAssociation.getTime() <  youngerAssociation.getTime(), "older {} should be older than younger {}".format(olderAssociation.getTime(), youngerAssociation.getTime()))
        
        # manipulate sensation ids and times same
        # make same id so we have two copies of same Sensation
        olderLongTermSensation.setId(youngerLongTermSensation.getId())
        self.assertEqual(olderLongTermSensation,  youngerLongTermSensation, "should be kept equal")
        olderLongTermSensation.time = youngerLongTermSensation.time
        
        # try update older with younger, should succeed
        bytes=youngerLongTermSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromByteslongTermSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromByteslongTermSensation != None, "should be created")
        self.assertTrue(fromByteslongTermSensation == youngerLongTermSensation, "should be equal")
        self.assertTrue(fromByteslongTermSensation.getReceivedFrom() == receivedFrom, "should be equal")
        #but item name should come from newer one
        self.assertEqual(fromByteslongTermSensation.getName(),  youngerLongTermSensation.getName(), "name should be from younger")
        
        self.assertTrue(len(fromByteslongTermSensation.getAssociations()) in [2, 3]) # variates 3#2 # now old one + new one TODO is this OK
        fromBytesAssociation = fromByteslongTermSensation.getAssociation(sensation=youngerVoiceSensation)
        self.assertEqual(youngerAssociation.getSensation(),fromBytesAssociation.getSensation(), "should be equal")


        # ready to test
        # try update younger with older, nothing should happen
        bytes=olderLongTermSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromByteslongTermSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromByteslongTermSensation != None, "should be created")
        self.assertTrue(fromByteslongTermSensation == olderLongTermSensation, "should be equal")
        self.assertTrue(fromByteslongTermSensation.getReceivedFrom() == receivedFrom, "should be equal")
        #but item name should come from newer one
        self.assertEqual(fromByteslongTermSensation.getName(),  youngerLongTermSensation.getName(), "name should be from younger")
        
        self.assertTrue(len(fromByteslongTermSensation.getAssociations()) in [2, 3]) # variates 3  # 2# now old one + new one TODO is this OK
        fromBytesAssociation = fromByteslongTermSensation.getAssociation(sensation=youngerVoiceSensation)
        self.assertEqual(youngerAssociation.getSensation(),fromBytesAssociation.getSensation(), "should be equal")
               

        print("\ntest_Bytes DONE")
        
#  
    def test_SaveLoadToBinaryFiles(self):
        print("\ntest_SaveLoadToBinaryFiles\n")
        sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name='test', score=MemoryTestCase.SCORE, present=True)
         
         
        originalSensations=[]
        for s in self.memory.sensationMemory:
            if s.getMemoryType() == Sensation.MemoryType.LongTerm and\
               s.getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY:
                originalSensations.append(s)
 
        self.memory.saveLongTermMemoryToBinaryFiles()
        del self.memory.sensationMemory[:]
         
        self.memory.loadLongTermMemoryFromBinaryFiles()
         
        self.assertEqual(len(self.memory.sensationMemory),len(originalSensations), "should load same amount Sensations")
        i=0
        while i < len(self.memory.sensationMemory):
            j=0
            found=False
            while j < len(self.memory.sensationMemory) and not found:
                if self.memory.sensationMemory[i] == originalSensations[j]:
                    found=True
                    self.assertEqual(self.memory.sensationMemory[i],originalSensations[j], "loaded sensation {} must be same than dumped one {}".format(i,j))
                else:
                    j = j+1
            self.assertTrue(found, "original sensation {} was not found in loaded ones".format(i))
            i=i+1

    '''
    Test masterItems-functionality
    
    Note: Now, when we call sensation.delete(), it is not enough to remove fron sensation memory, so
          we must explicitly call deleteFromMasterItems from memory.
          Robots must use Memory.deleteFromSensationMemory, when they wan't to delete a Sensation
    '''
    def testMasterItems(self):
        
        ##################################
        #
        # direct inner implementation test
        #
        #=================================

        # unique name        
        name1 ='unique_name'
        self.assertFalse(name1 in self.memory.masterItems)
        sensation1 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name=name1, score=MemoryTestCase.SCORE, present=True)
        self.assertTrue(sensation1 in self.memory.sensationMemory)
        self.assertTrue(name1 in self.memory.masterItems)
        self.assertTrue(sensation1 in self.memory.masterItems[name1])
        self.assertEqual(len(self.memory.masterItems[name1]), 1)

        # name with many sensations
        name2='test'
        sensation2 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name=name2, score=MemoryTestCase.SCORE, present=True)
        self.assertTrue(name2 in self.memory.masterItems)
        self.assertEqual(len(self.memory.masterItems[name2]), 1)
                        
        sensation3 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name=name2, score=MemoryTestCase.SCORE, present=True)
        self.assertTrue(sensation3 in self.memory.sensationMemory)
        self.assertTrue(name2 in self.memory.masterItems)
        self.assertTrue(sensation2 in self.memory.masterItems[name2])
        self.assertTrue(sensation3 in self.memory.masterItems[name2])
        self.assertEqual(len(self.memory.masterItems[name2]),2)

        sensation3.delete()
        self.memory.deleteFromMasterItems(sensation=sensation3)
        self.assertEqual(len(self.memory.masterItems[name2]),1)
        self.assertTrue(name2 in self.memory.masterItems)

        sensation2.delete()
        self.memory.deleteFromMasterItems(sensation=sensation2)
        self.assertFalse(name2 in self.memory.masterItems)

        sensation1.delete()
        self.memory.deleteFromMasterItems(sensation=sensation1)
        self.assertFalse(name1 in self.memory.masterItems)


        ##################################
        #
        # test how Robots create ans delete Sensations
        # We should get exactly same results
        #
        #=================================

        # unique name        
        name1 ='unique_name'
        self.assertFalse(name1 in self.memory.masterItems)
        sensation1 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name=name1, score=MemoryTestCase.SCORE, present=True)
        self.assertTrue(sensation1 in self.memory.sensationMemory)
        self.assertTrue(name1 in self.memory.masterItems)
        self.assertTrue(sensation1 in self.memory.masterItems[name1])
        self.assertEqual(len(self.memory.masterItems[name1]), 1)

        # name with many sensations
        name2='test'
        sensation2 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name=name2, score=MemoryTestCase.SCORE, present=True)
        self.assertTrue(name2 in self.memory.masterItems)
        self.assertEqual(len(self.memory.masterItems[name2]), 1)
                        
        sensation3 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name=name2, score=MemoryTestCase.SCORE, present=True)
        self.assertTrue(sensation3 in self.memory.sensationMemory)
        self.assertTrue(name2 in self.memory.masterItems)
        self.assertTrue(sensation2 in self.memory.masterItems[name2])
        self.assertTrue(sensation3 in self.memory.masterItems[name2])
        self.assertEqual(len(self.memory.masterItems[name2]),2)

        self.memory.deleteFromSensationMemory(sensation=sensation3)
        self.assertEqual(len(self.memory.masterItems[name2]),1)
        self.assertTrue(name2 in self.memory.masterItems)

        self.memory.deleteFromSensationMemory(sensation=sensation2)
        self.assertFalse(name2 in self.memory.masterItems)

        self.memory.deleteFromSensationMemory(sensation=sensation1)
        self.assertFalse(name1 in self.memory.masterItems)

        
if __name__ == '__main__':
    unittest.main()

 