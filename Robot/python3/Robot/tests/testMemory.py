'''
Created on 12.04.2020
Updated on 20.01.2021
@author: reijo.korhonen@gmail.com

test Memory class
python3 -m unittest tests/testMemory.py


'''
import time as systemTime
import os
import unittest
from Sensation import Sensation
from Robot import Robot
from Memory import Memory

class MemoryTestCase(unittest.TestCase):
    TEST_RUNS = 2
    SCORE=0.5
    SCORE2=0.8
    
    NORMAL_FEELING = Sensation.Feeling.Good
    BETTER_FEELING = Sensation.Feeling.Happy
    TERRIFIED_FEELING = Sensation.Feeling.Terrified
    
    YOUNGER_LONGTERM_ITEM_NAME =    "younger LongTerm bytes_test"
    OLDER_LONGTERM_ITEM_NAME =      "older LongTerm bytes_test"

    def setUp(self):
        self.CleanDataDirectory()
        self.robot=Robot(mainRobot=None)
        self.memory = self.robot.getMemory()
        # To test, we should know what is in memory, 
        # we should clear Sensation memory from binary files loaded sensation
        del self.memory.sensationMemory[:]
        
        
        self.sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                    name='test', score=MemoryTestCase.SCORE, presence=Sensation.Presence.Entering)
        self.assertEqual(self.sensation.getPresence(), Sensation.Presence.Entering, "should be entering")
        self.assertIsNot(self.sensation, None)
        self.assertEqual(len(self.sensation.getAssociations()), 0)
        Sensation.logAssociations(self.sensation)
        
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
                    if filename.endswith('.'+Sensation.BINARY_FORMAT):
                        filepath = os.path.join(Sensation.DATADIR, filename)
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print('os.remove(' + filepath + ') error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
            except Exception as e:
                    print('os.listdir error ' + str(e), logLevel=Memory.MemoryLogLevel.Normal)
        

    def tearDown(self):
        self.sensation.delete()
        
    def test_Memorybility(self):        
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working, name='Working_test',presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation, None)
        self.assertEqual(len(workingSensation.getAssociations()), 0)

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name='LongTerm',presence=Sensation.Presence.Absent)
        self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(longTermSensation, None)
        self.assertEqual(len(longTermSensation.getAssociations()), 0)

        print("\nSensory time now")
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working time now")
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("LongTerm time now")
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() > workingSensation.getMemorability(), 'now Sensory sensation must be more Memorability than Working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'now Working sensation must be more Memorability than LongTerm sensation')

        # set sensation to the past and look again  
        history_time = Sensation.sensationMemoryLiveTimes[self.sensation.getMemoryType()] * 0.5      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'half Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[self.sensation.getMemoryType()] * 0.8      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() < workingSensation.getMemorability(), 'near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[self.sensation.getMemoryType()] * 0.98      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() < workingSensation.getMemorability(), 'very near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'very near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.5      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'half working lifetime Working sensation must be more than zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'half working lifetime LongTerm sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.8      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
         # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.95      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very near working lifetime Working sensation must be less Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.98      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very very near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 1.05      
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.5     
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.98     
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'very very near long term lifetime Sensory sensation must still be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 1.02     
        self.sensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("Working history time " + str(history_time))
        print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  == 0.0, 'beyond end long term lifetime Sensory sensation must be zero')
        
    '''
    Test importance
    
    We use Sensation.SensationType.Image in this test, because
    Memory keeps track of presence, so We get many instances of
    Sensation.SensationType.Item
    Anyway we are searching Images and Voices per Item.name
    and Importance, but newer Item-names 
    '''    

    def test_Importance(self):        
        print("\ntest_Importance")
        
        
        #memoryType=Sensation.MemoryType.Sensory
        sensorySensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory,
                                                      name='Working_Importance_test', score=MemoryTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertIsNot(sensorySensation, None)
        self.assertEqual(sensorySensation.getPresence(), Sensation.Presence.Present, "should be present")
        self.assertEqual(len(sensorySensation.getAssociations()), 0) # variates
        sensorySensation.associate(sensation=self.sensation,
                                   feeling=MemoryTestCase.NORMAL_FEELING)
        Sensation.logAssociations(sensorySensation)
        self.assertEqual(len(sensorySensation.getAssociations()), 1)
        sensoryAssociation = self.sensation.getAssociation(sensation=sensorySensation)
        self.assertIsNot(sensoryAssociation, None)
        
        self.do_test_Importance(sensation=sensorySensation, association=sensoryAssociation)
        
        #memoryType=Sensation.MemoryType.Working
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=MemoryTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertIsNot(workingSensation, None)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Present, "should be present")
        self.assertEqual(len(workingSensation.getAssociations()), 0) # variates
        workingSensation.associate(sensation=self.sensation,
                                   feeling=MemoryTestCase.NORMAL_FEELING)
        Sensation.logAssociations(workingSensation)
        self.assertEqual(len(workingSensation.getAssociations()), 1)
        workingAssociation = self.sensation.getAssociation(sensation=workingSensation)
        self.assertIsNot(workingAssociation, None)
        
        self.do_test_Importance(sensation=workingSensation, association=workingAssociation)

        #memoryType=Sensation.MemoryType.LongTerm
        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.LongTerm,
                                                      name='LongTerm_Importance_test', score=MemoryTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertIsNot(longTermSensation, None)
        self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Present, "should be present")
        #self.assertEqual(len(longTermSensation.getAssociations()), 0) # variates
        longTermSensation.associate(sensation=self.sensation,
                                   feeling=MemoryTestCase.NORMAL_FEELING)
        Sensation.logAssociations(longTermSensation)
        self.assertEqual(len(longTermSensation.getAssociations()), 1) # variates
        longTermAssociation = self.sensation.getAssociation(sensation=longTermSensation)
        self.assertIsNot(longTermAssociation, None)
        
        self.do_test_Importance(sensation=longTermSensation, association=longTermAssociation)
        longTermSensation.delete()# remove associations
        self.assertEqual(len(longTermSensation.getAssociations()), 0)

    '''
        Communication uses Sensation.getImportance() so it is most important to test
        TODO Study parameters getImportance(self, positive=True, negative=False, absolute=False)
        default is positive=True and it is fine for Communication use to find best positive choice
        Assosiation.getImportance() is curiosite    
    '''   
    def do_test_Importance(self, sensation, association):        
        print("\ndo_test_Importance")

        # Normal feeling
        association.setFeeling(feeling=MemoryTestCase.NORMAL_FEELING)
        print("MemoryTestCase.NORMAL_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > 0.0, "association importance must greater than zero")
        print("MemoryTestCase.NORMAL_FEELING sensation.getImportance() " + str(sensation.getImportance()))
        self.assertTrue(sensation.getImportance() > 0.0, "sensation now importance must greater than zero")
        normalAssociationImportance = association.getImportance()
        normalSensationImportance = sensation.getImportance()
 
        #Compare Normal and Better feelings importance of Sensations
        association.setFeeling(feeling=MemoryTestCase.BETTER_FEELING)
        betterAssociationImportance = association.getImportance()
        betterSensationImportance = sensation.getImportance()
        
        print("MemoryTestCase.BETTER_FEELING betterAssociationImportance {}".format(betterAssociationImportance))
        print("MemoryTestCase.BETTER_FEELING betterSensationImportance {}".format(betterSensationImportance))
        self.assertTrue(betterAssociationImportance > normalAssociationImportance, "better feeling association importance must greater than normal feeling")
        self.assertTrue(betterSensationImportance > normalSensationImportance, "better feeling sensation now importance must greater than normal feeling")
        
        #Compare Terrified with Normal and Better feelings importance of Sensations    
        association.setFeeling(feeling=MemoryTestCase.TERRIFIED_FEELING)
        terrifiedAssociationImportance = association.getImportance()
        terrifiedSensationImportance = sensation.getImportance()
        
        print("MemoryTestCase.TERRIFIED_FEELING terrifiedAssociationImportance {}".format(terrifiedAssociationImportance))
        print("MemoryTestCase.TERRIFIED_FEELING terrifiedSensationImportance {}".format(terrifiedSensationImportance))
        self.assertTrue(terrifiedAssociationImportance < normalAssociationImportance, "terrified feeling association importance must smaller than normal feeling")
        self.assertTrue(terrifiedAssociationImportance < betterAssociationImportance, "terrified feeling association importance must smaller than better feeling")
        self.assertTrue(terrifiedSensationImportance < normalAssociationImportance, "terrified feeling sensation now importance must smaller than normal feeling")
        self.assertTrue(terrifiedSensationImportance < betterSensationImportance, "terrified feeling sensation now importance must smaller than better feeling")
       
        # set sensation more to the past and look again
        history_time = Sensation.sensationMemoryLiveTimes[sensation.getMemoryType()] * 0.5      
        sensation.setTime(systemTime.time() - history_time)
        association.setTime(systemTime.time() - history_time)
        
        # terrified
        historyTerrifiedAssociationImportance = association.getImportance()
        historyTerrifiedSensationImportance = sensation.getImportance()
        print("historyTerrifiedAssociationImportance {}".format(historyTerrifiedAssociationImportance))
        print("historyTerrifiedSensationImportance {}".format(historyTerrifiedSensationImportance))
        self.assertTrue(historyTerrifiedAssociationImportance < betterAssociationImportance, "terrified feeling association importance must smaller than better feeling")
        self.assertTrue(historyTerrifiedAssociationImportance < normalAssociationImportance, "terrified feeling association importance must smaller than normal feeling")
        self.assertTrue(historyTerrifiedSensationImportance < normalAssociationImportance, "terrified feeling sensation now importance must smaller than normal feeling")
        self.assertTrue(historyTerrifiedSensationImportance < betterSensationImportance, "terrified feeling sensation now importance must smaller than better feeling")

        # history importance of Sensations should be higher than current because it is negative
        # and when time has been going on, things don't feel so terrified that they were, when happened 
        self.assertTrue(terrifiedAssociationImportance == historyTerrifiedAssociationImportance, "history terrified feeling association importance must smaller than current normal feeling")
        self.assertTrue(terrifiedSensationImportance < historyTerrifiedSensationImportance, "history terrified feeling sensation importance must smaller than current normal feeling")
 
        # Normal       
        #Compare Normal and history Better feelings importance of Sensations, history better should still be better
        association.setFeeling(feeling=MemoryTestCase.NORMAL_FEELING)
        # must set time back to history
        association.setTime(systemTime.time() - history_time)
        sensation.setTime(systemTime.time() - history_time)
        # test
        historyNormalAssociationImportance = association.getImportance()
        historyNormaSensationImportance = sensation.getImportance()
        print("historyNormalAssociationImportance {}".format(historyNormalAssociationImportance))
        print("historyNormaSensationImportance {}".format(historyNormaSensationImportance))
        
        self.assertTrue(normalAssociationImportance == historyNormalAssociationImportance, "history and current association importances are equal")
        self.assertTrue(normalSensationImportance > historyNormaSensationImportance, "history importance is lower than current one.")
        self.assertTrue(historyTerrifiedSensationImportance < historyNormaSensationImportance, "history terrified importance is lower than normal history one.")
        self.assertTrue(historyTerrifiedSensationImportance < normalSensationImportance, "history terrified importance is lower than normal current one.")

        # Better      
        #Compare Normal and history Better feelings importance of Sensations, history better should still be better
        association.setFeeling(feeling=MemoryTestCase.BETTER_FEELING)
        # must set time back to history
        association.setTime(systemTime.time() - history_time)
        sensation.setTime(systemTime.time() - history_time)
        # test
        historyBetterAssociationImportance = association.getImportance()
        historyBetterWorkingSensationImportance = sensation.getImportance()
        self.assertTrue(betterAssociationImportance == historyBetterAssociationImportance, "history and current association importances are equal")
        self.assertTrue(betterSensationImportance > historyBetterWorkingSensationImportance, "history importance is lower than current one.")
        self.assertTrue(historyTerrifiedSensationImportance < historyBetterWorkingSensationImportance, "history terrified importance is lower than Better history one.")
        self.assertTrue(historyTerrifiedSensationImportance < betterSensationImportance, "history terrified importance is lower than normal current one.")
        self.assertTrue(historyNormaSensationImportance < historyBetterAssociationImportance, "history normal importance is lower than history normal one.")       


    def test_AddAssociations(self):
        for i in range(MemoryTestCase.TEST_RUNS):
            self.do_test_AddAssociation()

        
    def do_test_AddAssociation(self):
        # test this test
        self.assertEqual(self.sensation.getScore(), MemoryTestCase.SCORE)
        
        # when we create sensation=self.sensation, other parameters can't be used
        addSensation = self.robot.createSensation(associations=None, sensation=self.sensation)
        self.assertIsNot(addSensation, None)
        addSensation.setName(name='connect_test')
        self.assertEqual(addSensation.getName(), 'connect_test', "should be \'connect_test\' ")
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        
        self.assertEqual(addSensation.getMemoryType(), Sensation.MemoryType.Working, "should be Sensation.MemoryType.Working")
        addSensation.setPresence(presence=Sensation.Presence.Present)
        self.assertEqual(addSensation.getPresence(), Sensation.Presence.Present, "should be present")
        
        addSensation.setName('connect_test')
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        addSensation.save()    # this is worth to save its data
        associationNumber = len(self.sensation.getAssociations())
        #print('\nlogAssociations 2: test_AddAssociation')
        Sensation.logAssociations(addSensation)
        
        self.sensation.associate(sensation=addSensation,
                                 feeling=MemoryTestCase.NORMAL_FEELING)

        self.assertEqual(len(self.sensation.getAssociations()), associationNumber+1)
        self.assertEqual(self.sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), MemoryTestCase.NORMAL_FEELING)

        # test bytes        
        bytes=self.sensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesSensation != None, "fromBytesSensation should be created")
        self.assertTrue(fromBytesSensation == self.sensation, "fromBytesSensation should be equal")
       
        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        
        # test bytes        
        bytes=addSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)

        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(self.sensation), MemoryTestCase.NORMAL_FEELING)
       
        # TODO rest if the test

        #print('\nlogAssociations 5: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        # again, should not add association twice
        self.sensation.addAssociation(Sensation.Association(self_sensation=self.sensation,
                                                            sensation=addSensation,
#                                                            score=MemoryTestCase.SCORE2,
                                                            feeling=MemoryTestCase.TERRIFIED_FEELING))
        self.assertEqual(len(self.sensation.getAssociations()), associationNumber+1)
        self.assertEqual(self.sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), MemoryTestCase.TERRIFIED_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), MemoryTestCase.TERRIFIED_FEELING)

        #print('\nlogAssociations 6: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        
        # better feeling
        addAssociation = addSensation.getAssociation(self.sensation)
        self.assertIsNot(addAssociation, None)

        # change feeling in association        
        addAssociation.setFeeling(MemoryTestCase.BETTER_FEELING)
        # and it should be changed in both way association in both ways
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), MemoryTestCase.BETTER_FEELING)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), MemoryTestCase.BETTER_FEELING)

    def test_Feeling(self):
        for i in range(MemoryTestCase.TEST_RUNS):
            self.do_test_Feeling()

        
    def do_test_Feeling(self):
        # test this test
        self.assertEqual(self.sensation.getScore(), MemoryTestCase.SCORE)
        
        # when we create sensation=self.sensation, other parameters can't be used
        addSensation = self.robot.createSensation(associations=None, sensation=self.sensation)
        self.assertIsNot(addSensation, None)
        
        addSensation.setName(name='connect_test')
        self.assertEqual(addSensation.getName(), 'connect_test', "should be \'connect_test\' ")
        
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        self.assertEqual(addSensation.getMemoryType(), Sensation.MemoryType.Working, "should be Sensation.MemoryType.Working")
        
        addSensation.setPresence(presence=Sensation.Presence.Present)
        self.assertEqual(addSensation.getPresence(), Sensation.Presence.Present, "should be present")
        
        addSensation.setName('connect_test')
        self.memory.setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        addSensation.save()    # this is worth to save its data
        associationNumber = len(self.sensation.getAssociations())
        #print('\nlogAssociations 2: test_AddAssociation')
        Sensation.logAssociations(addSensation)
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=self.sensation, otherAssociateSensation=addSensation,
                                                      feeling=MemoryTestCase.NORMAL_FEELING)
        self.memory.process(sensation=feelingSensation)
        

        self.assertEqual(len(self.sensation.getAssociations()), associationNumber+1)
        self.assertEqual(self.sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), MemoryTestCase.NORMAL_FEELING)

        # test bytes        
        bytes=self.sensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesSensation != None, "fromBytesSensation should be created")
        self.assertTrue(fromBytesSensation == self.sensation, "fromBytesSensation should be equal")
       
        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(addSensation), MemoryTestCase.NORMAL_FEELING)
        
        
        # test bytes        
        bytes=addSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)

        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(self.sensation), MemoryTestCase.NORMAL_FEELING)
       
        # TODO rest if the test

        #print('\nlogAssociations 5: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        # again, should not add association twice
#         self.sensation.addAssociation(Sensation.Association(self_sensation=self.sensation,
#                                                             sensation=addSensation,
# #                                                            score=MemoryTestCase.SCORE2,
#                                                             feeling=MemoryTestCase.TERRIFIED_FEELING))
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=self.sensation, otherAssociateSensation=addSensation,
                                                      feeling=MemoryTestCase.TERRIFIED_FEELING)
        self.memory.process(sensation=feelingSensation)
        
        self.assertEqual(len(self.sensation.getAssociations()), associationNumber+1)
        self.assertEqual(self.sensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), MemoryTestCase.TERRIFIED_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), MemoryTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), MemoryTestCase.TERRIFIED_FEELING)

        #print('\nlogAssociations 6: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        
        # better feeling
        addAssociation = addSensation.getAssociation(self.sensation)
        self.assertIsNot(addAssociation, None)

        # change feeling in association        
#         addAssociation.setFeeling(MemoryTestCase.BETTER_FEELING)
        # and it should be changed in both way association in both ways
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=self.sensation, otherAssociateSensation=addSensation,
                                                      feeling=MemoryTestCase.BETTER_FEELING)
        self.memory.process(sensation=feelingSensation)

        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), MemoryTestCase.BETTER_FEELING)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), MemoryTestCase.BETTER_FEELING)

    def test_Bytes(self):        
        print("\ntest_Bytes")
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working, name='Working_Importance_test',presence=Sensation.Presence.Present, receivedFrom=[])
        self.assertTrue(workingSensation != None, "should be created")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertEqual(fromBytesWorkingSensation, workingSensation, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getId(), workingSensation.getId(), "should be equal")
        self.assertEqual(self.robot.getMemory().getSensationFromSensationMemory(fromBytesWorkingSensation.getId()).getId(), workingSensation.getId(), "should be equal")
        # TODO Feeling
        

        receivedFrom=['127.0.0.1', '192.168.0.0.1', '10.0.0.1']
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working, name='Working_Importance_test',presence=Sensation.Presence.Present, receivedFrom=receivedFrom)
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
                                                              associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.YOUNGER_LONGTERM_ITEM_NAME,presence=Sensation.Presence.Present, receivedFrom=receivedFrom)
        self.assertTrue(youngerLongTermSensation != None, "should be created")
        self.assertTrue(youngerLongTermSensation.getTime() > systemTime.time(), "should be younger than present")

        olderLongTermSensation = self.robot.createSensation(time = systemTime.time()-10.0,
                                                              associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.OLDER_LONGTERM_ITEM_NAME,presence=Sensation.Presence.Present, receivedFrom=receivedFrom)
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
                                                            associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.OLDER_LONGTERM_ITEM_NAME,presence=Sensation.Presence.Present, receivedFrom=receivedFrom)
        self.assertTrue(olderLongTermSensation != None, "should be created")
        self.assertTrue(olderLongTermSensation.getTime() <  systemTime.time(), "should be older than present")
        
        olderLongTermSensation.associate(sensation=olderVoiceSensation,
                                         feeling=MemoryTestCase.NORMAL_FEELING)
        self.assertEqual(len(olderLongTermSensation.getAssociations()), 2) # variates
        olderAssociation = olderLongTermSensation.getAssociation(sensation=olderVoiceSensation)
        self.assertTrue(olderAssociation.getTime() <  systemTime.time(), "should be older than present")

        # create now younger sensation and association
        youngerVoiceSensation = self.robot.createSensation(#time = systemTime.time()-2.0,
                                                           associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=locations, kind=Sensation.Kind.Eva)
        youngerLongTermSensation = self.robot.createSensation(#time = systemTime.time()-1.0,
                                                              associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm, name=self.OLDER_LONGTERM_ITEM_NAME,presence=Sensation.Presence.Present, receivedFrom=receivedFrom)
        self.assertTrue(youngerLongTermSensation != None, "should be created")
        self.assertTrue(youngerLongTermSensation.getTime() <  systemTime.time(), "should be older than present")
        
        youngerLongTermSensation.associate(sensation=youngerVoiceSensation,
                                          feeling=MemoryTestCase.NORMAL_FEELING)
        self.assertEqual(len(youngerLongTermSensation.getAssociations()), 2) # variates
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
        
        self.assertEqual(len(fromByteslongTermSensation.getAssociations()), 3) # 3#2 # now old one + new one TODO is this OK
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
        
        self.assertEqual(len(fromByteslongTermSensation.getAssociations()), 3)# 3  # 2# now old one + new one TODO is this OK
        fromBytesAssociation = fromByteslongTermSensation.getAssociation(sensation=youngerVoiceSensation)
        self.assertEqual(youngerAssociation.getSensation(),fromBytesAssociation.getSensation(), "should be equal")
               

        print("\ntest_Bytes DONE")
        
    def re_test_Picleability(self):
        print("\ntest_Picleability\n")
        
        originalSensations=[]
        for sensation in self.memory.sensationMemory:
            if sensation.getMemoryType() == Sensation.MemoryType.LongTerm and\
               sensation.getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY:
                originalSensations.append(sensation)

        self.memory.saveLongTermMemory()
        del self.memory.sensationMemory[:]
        
        self.memory.loadLongTermMemory()
        
        self.assertEqual(len(self.memory.sensationMemory),len(originalSensations), "should load same amount Sensations")
        i=0
        while i < len(self.memory.sensationMemory):
            self.assertEqual(self.memory.sensationMemory[i],originalSensations[i], "loaded sensation must be same than dumped one")
            i=i+1
 
    def test_SaveLoadToBinaryFiles(self):
        print("\ntest_SaveLoadToBinaryFiles\n")
        sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                name='test', score=MemoryTestCase.SCORE, presence=Sensation.Presence.Entering)
        
        
        originalSensations=[]
        for sensation in self.memory.sensationMemory:
            if sensation.getMemoryType() == Sensation.MemoryType.LongTerm and\
               sensation.getMemorability() >  Sensation.MIN_CACHE_MEMORABILITY:
                originalSensations.append(sensation)

        self.memory.saveLongTermMemoryToBinaryFiles()
        del self.memory.sensationMemory[:]
        
        self.memory.loadLongTermMemoryFromBinaryFiles()
        
        self.assertEqual(len(self.memory.sensationMemory),len(originalSensations), "should load same amount Sensations")
        i=0
        while i < len(self.memory.sensationMemory):
            self.assertEqual(self.memory.sensationMemory[i],originalSensations[i], "loaded sensation must be same than dumped one")
            i=i+1
        
if __name__ == '__main__':
    unittest.main()

 