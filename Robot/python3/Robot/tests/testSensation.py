'''
Created on 10.06.2019
Updated on 01.01.2021
@author: reijo.korhonen@gmail.com

test Sensation class
python3 -m unittest tests/testSensation.py


'''
import time as systemTime
import unittest
from Sensation import Sensation#, booleanToBytes, bytesToBoolean
from Robot import Robot

class SensationTestCase(unittest.TestCase):
    TEST_RUNS = 2
    SCORE=0.5
    SCORE2=0.8
    
    NORMAL_FEELING = Sensation.Feeling.Good
    BETTER_FEELING = Sensation.Feeling.Happy
    TERRIFIED_FEELING = Sensation.Feeling.Terrified

    MAINNAMES_1 =          ['Wall-E_MainName']
    MAINNAMES_2 =          ['Eva_MainName']

    SET_1_1_LOCATIONS_1 = ['testLocation']
    SET_1_1_LOCATIONS_2 = ['Ubuntu']
    SET_1_2_LOCATIONS =   ['testLocation', 'Ubuntu']
    
    LOCATION_1_NAME =     'testLocation'
    LOCATION_1_X =        1.0
    LOCATION_1_Y =        2.0
    LOCATION_1_Z =        3.0
    LOCATION_1_RADIUS =   4.0
    
    LOCATION_2_NAME =     'Ubuntu'
    LOCATION_2_X =        11.0
    LOCATION_2_Y =        12.0
    LOCATION_2_Z =        13.0
    LOCATION_2_RADIUS =   14.0

    RECEIVEDFROM =        ['127.0.0.1', '192.168.0.0.1', '10.0.0.1']
    

    def setUp(self):
        self.robot=Robot()
        self.sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                    name='test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Entering)
        self.assertEqual(self.sensation.getPresence(), Sensation.Presence.Entering, "should be entering")
        self.assertIsNot(self.sensation, None)
        self.assertEqual(len(self.sensation.getAssociations()), 0)
        #print('\nlogAssociations 1: setUp')
        Sensation.logAssociations(self.sensation)
        
        self.feeling = SensationTestCase.NORMAL_FEELING

    def tearDown(self):
        self.sensation.delete()
        
    def test_Memorybility(self):
        print('\ntest_Memorybility')
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation, None)
        self.assertEqual(len(workingSensation.getAssociations()), 0)

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                       name='LongTerm', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(longTermSensation, None)
        self.assertEqual(len(longTermSensation.getAssociations()), 0) # 2 sensations are associated each other if they are Exiting, changed to Absent
                                                                      # to west they should not, but be independent to get memorability of each other
                                                                      # lets do some violance to separate them.

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

        # test Feeling, it is not worth to remember after processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability() == 0.0, 'feelingSensation sensation must be zero')

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
        
        # test Feeling, it is not worth to remember aftered processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability()  == 0.0, 'feelingSensation sensation must be zero')
        
    '''
    Same Memorability test, but here we use Location(s) implemented as Sensation also
    Final version will be location parameter removed
    '''
             
    def test_MemorybilitySensationLocation(self):
        print('\ntest_MemorybilitySensationLocation')
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation, None)
        self.assertEqual(len(workingSensation.getAssociations()), 0)

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                       name='LongTerm', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
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

        # test Feeling, it is not worth to remember after processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        locationSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability() == 0.0, 'feelingSensation sensation must be zero')

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
        
        # test Feeling, it is not worth to remember aftered processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability()  == 0.0, 'feelingSensation sensation must be zero')
        

    def test_Importance(self):        
        print("\ntest_Importance")
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Present, "should be present")
        self.assertIsNot(workingSensation, None)
        self.assertEqual(len(workingSensation.getAssociations()), 0)
        workingSensation.associate(sensation=self.sensation,
                                    feeling=SensationTestCase.NORMAL_FEELING)
        Sensation.logAssociations(workingSensation)
        self.assertEqual(len(workingSensation.getAssociations()), 1)
        association = self.sensation.getAssociation(sensation=workingSensation)
        self.assertIsNot(association, None)
        print("SensationTestCase.NORMAL_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > 0.0, "association importance must greater than zero")
        print("SensationTestCase.NORMAL_FEELING workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() > 0.0, "sensation now importance must greater than zero")
        
        previousAssociationImportance = association.getImportance()
        previousWorkingSensationImportance = workingSensation.getImportance()
        association.setFeeling(feeling=SensationTestCase.BETTER_FEELING)
        print("SensationTestCase.BETTER_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > previousAssociationImportance, "better feeling association importance must greater than worse feeling")
        print("SensationTestCase.BETTER_FEELING workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() > previousWorkingSensationImportance, "better feeling sensation now importance must greater than worse feeling")
        
        previousAssociationImportance = association.getImportance()
        previousWorkingSensationImportance = workingSensation.getImportance()
        association.setFeeling(feeling=SensationTestCase.TERRIFIED_FEELING)
        print("feeling=SensationTestCase.TERRIFIED_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() < previousAssociationImportance, "terrified feeling association importance must smaller than any other feeling")
        print("feeling=SensationTestCase.TERRIFIED_FEELING workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() < previousWorkingSensationImportance, "terrified feeling sensation now importance must smaller than any other feeling")
       
        previousAssociationImportance = association.getImportance()
        previousWorkingSensationImportance = workingSensation.getImportance()
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.5      
        workingSensation.setTime(systemTime.time() - history_time)
        association.setTime(systemTime.time() - history_time)
        print("[workingSensation.getMemoryType()] * 0.5 workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() > previousWorkingSensationImportance, "terrified feeling sensation must be more positive when time goes on")

    def test_AddAssociations(self):
        print('\ntest_AddAssociations')
        for i in range(SensationTestCase.TEST_RUNS):
            self.do_test_AddAssociation()

        
    def do_test_AddAssociation(self):
        # test this test
        self.assertEqual(self.sensation.getScore(), SensationTestCase.SCORE)
        
        # when we create sensation=self.sensation, other parameters can't be used
        addSensation = self.robot.createSensation(associations=None, sensation=self.sensation)
        self.assertIsNot(addSensation, None)
        addSensation.setName(name='connect_test')
        self.assertEqual(addSensation.getName(), 'connect_test', "should be \'connect_test\' ")
        self.robot.getMemory().setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        self.assertEqual(addSensation.getMemoryType(), Sensation.MemoryType.Working, "should be Sensation.MemoryType.Working")
        addSensation.setPresence(presence=Sensation.Presence.Present)
        self.assertEqual(addSensation.getPresence(), Sensation.Presence.Present, "should be present")
        
        addSensation.setName('connect_test')
        self.robot.getMemory().setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
        addSensation.save()    # this is worth to save its data
        associationNumber = len(self.sensation.getAssociations())
        #print('\nlogAssociations 2: test_AddAssociation')
        Sensation.logAssociations(addSensation)
        
        self.sensation.associate(sensation=addSensation,
                                 feeling=self.feeling)
#         addAssociation = Sensation.Association(self_sensation=self.sensation,
#                                                sensation=addSensation,
#                                                score=SensationTestCase.SCORE,
#                                                feeling=self.feeling)
#         
# 
#         self.sensation.addAssociation(addAssociation)
#         #print('\nlogAssociations 3: test_AddAssociation')
#         Sensation.logAssociations(self.sensation)
#         #print('\nlogAssociations 4: test_AddAssociation')
#         Sensation.logAssociations(addSensation)
        
        #for association in self.sensation.getAssociations():
            #print ('self.sensation association ' + str(dir(association)))
        #for association in addSensation.getAssociations():
            #print ('addSensation association ' + str(dir(association)))

        self.assertEqual(len(self.sensation.getAssociations()), associationNumber+1)
        self.assertEqual(self.sensation.getScore(), SensationTestCase.SCORE)
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), self.feeling)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), SensationTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), self.feeling)

        # test bytes        
        bytes=self.sensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesSensation != None, "fromBytesSensation should be created")
        self.assertTrue(fromBytesSensation == self.sensation, "fromBytesSensation should be equal")
       
        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), SensationTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(addSensation), self.feeling)
        
        
        # test bytes        
        bytes=addSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesSensation = self.robot.createSensation(bytes=bytes)

        self.assertEqual(len(fromBytesSensation.getAssociations()), associationNumber+1)
        self.assertEqual(fromBytesSensation.getScore(), SensationTestCase.SCORE)
        self.assertEqual(fromBytesSensation.getAssociationFeeling(self.sensation), self.feeling)
       
        # TODO rest if the test

        #print('\nlogAssociations 5: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        # again, should not add association twise
        self.sensation.addAssociation(Sensation.Association(self_sensation=self.sensation,
                                                            sensation=addSensation,
                                                            feeling=SensationTestCase.TERRIFIED_FEELING))
        self.assertEqual(len(self.sensation.getAssociations()), associationNumber+1)
        self.assertEqual(self.sensation.getScore(), SensationTestCase.SCORE)
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), SensationTestCase.TERRIFIED_FEELING)
        
        self.assertEqual(len(addSensation.getAssociations()), associationNumber+1)
        self.assertEqual(addSensation.getScore(), SensationTestCase.SCORE)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), SensationTestCase.TERRIFIED_FEELING)

        #print('\nlogAssociations 6: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        
        # better feeling
        self.feeling = SensationTestCase.BETTER_FEELING
        addAssociation = addSensation.getAssociation(self.sensation)
        self.assertIsNot(addAssociation, None)

        # change feeling in association        
        addAssociation.setFeeling(self.feeling)
        # and it should be changed in both way association in both ways
        self.assertEqual(self.sensation.getAssociationFeeling(addSensation), self.feeling)
        self.assertEqual(addSensation.getAssociationFeeling(self.sensation), self.feeling)

    def test_Bytes(self):        
        print("\ntest_Bytes")
        self.robot.setMainNames(SensationTestCase.MAINNAMES_1)
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_2_LOCATIONS)
        self.assertEqual(SensationTestCase.MAINNAMES_1, workingSensation.getMainNames(), "should be equal")
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertEqual(fromBytesWorkingSensation, workingSensation, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getMainNames(), workingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")
        
        workingSensation.setLocations(locations = SensationTestCase.SET_1_1_LOCATIONS_1)
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_1_LOCATIONS_1, "should be equal")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertEqual(fromBytesWorkingSensation, workingSensation, "should be equal")
        self.assertEqual(SensationTestCase.MAINNAMES_1, fromBytesWorkingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getMainNames(), workingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_1_LOCATIONS_1, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")
       
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=SensationTestCase.RECEIVEDFROM)
        self.assertTrue(workingSensation != None, "should be created")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertTrue(fromBytesWorkingSensation == workingSensation, "should be equal")
        self.assertTrue(fromBytesWorkingSensation.getReceivedFrom() == SensationTestCase.RECEIVEDFROM, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")

        # Voice
        
        data=b'\x01\x02'
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)

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
        self.assertEqual(fromBytesVoiceSensation.getDataId(), voiceSensation.getDataId(), "should be equal")
        self.assertTrue(voiceSensation.isOriginal(), "voiceSensation should be original")
        self.assertTrue(fromBytesVoiceSensation.isOriginal(), "fromBytesVoiceSensation should be original")
        
        self.assertFalse(fromBytesVoiceSensation.isForgettable(), "should be False, until detached")
        fromBytesVoiceSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesVoiceSensation.isForgettable(), "should be True after detach")

        # Image
        
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory, data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)

        self.assertFalse(imageSensation.isForgettable(), "should be False, until detached")
        imageSensation.detach(robot=self.robot)
        self.assertTrue(imageSensation.isForgettable(), "should be True after detach")

        bytes=imageSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesImageSensation = self.robot.createSensation(bytes=bytes)

        self.assertTrue(imageSensation == fromBytesImageSensation, "should be equal")
        self.assertTrue(imageSensation.getImage() == fromBytesImageSensation.getImage(), "should be equal") # empty image, not given in creation, TODO
        self.assertTrue(imageSensation.getLocations() == fromBytesImageSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesImageSensation.getDataId(), imageSensation.getDataId(), "should be equal")
        self.assertTrue(imageSensation.isOriginal(), "imageSensation should be original")
        self.assertTrue(fromBytesImageSensation.isOriginal(), "fromBytesImageSensation should be original")
        
        self.assertFalse(fromBytesImageSensation.isForgettable(), "should be False, until detached")
        fromBytesImageSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesImageSensation.isForgettable(), "should be True after detach")

        # Normal Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      feeling=SensationTestCase.NORMAL_FEELING)
        bytes=feelingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesFeelingSensation = self.robot.createSensation(bytes=bytes)
                
        self.assertTrue(feelingSensation == fromBytesFeelingSensation, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromBytesFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromBytesFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getFeeling() == fromBytesFeelingSensation.getFeeling(), "should be equal")        
        self.assertEqual(fromBytesFeelingSensation.getFeeling(), SensationTestCase.NORMAL_FEELING, "should be equal")        
        self.assertEqual(fromBytesFeelingSensation.getDataId(), feelingSensation.getDataId(), "should be equal")
        self.assertTrue(feelingSensation.isOriginal(), "feelingSensation should be original")
        self.assertTrue(fromBytesFeelingSensation.isOriginal(), "fromBytesFeelingSensation should be original")
        
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
        self.assertEqual(fromBytesFeelingSensation.getDataId(), feelingSensation.getDataId(), "should be equal")
        self.assertTrue(feelingSensation.isOriginal(), "feelingSensation should be original")
        self.assertTrue(fromBytesFeelingSensation.isOriginal(), "fromBytesFeelingSensation should be original")
        
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromBytesFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromBytesFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getPositiveFeeling(), "should be True")        
        self.assertFalse(feelingSensation.getNegativeFeeling(), "should be False")        
        #self.assertTrue(feelingSensation.getFeeling() == SensationTestCase.NORMAL_FEELING, "should be equal")        
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
        self.assertEqual(fromBytesFeelingSensation.getDataId(), feelingSensation.getDataId(), "should be equal")
        self.assertTrue(feelingSensation.isOriginal(), "feelingSensation should be original")
        self.assertTrue(fromBytesFeelingSensation.isOriginal(), "fromBytesFeelingSensation should be original")
        
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromBytesFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromBytesFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertFalse(feelingSensation.getPositiveFeeling(), "should be False")        
        self.assertTrue(feelingSensation.getNegativeFeeling(), "should be True") 
        
        self.assertFalse(fromBytesFeelingSensation.getPositiveFeeling(), "should be False")        
        self.assertTrue(fromBytesFeelingSensation.getNegativeFeeling(), "should be True")        
               
        #self.assertTrue(feelingSensation.getFeeling() == SensationTestCase.NORMAL_FEELING, "should be equal")        

        self.assertFalse(fromBytesFeelingSensation.isForgettable(), "should be False, until detached")
        fromBytesFeelingSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesFeelingSensation.isForgettable(), "should be True after detach")
        
        # Feeling is property of every SensationType
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_1_LOCATIONS_2,
                                                      feeling=SensationTestCase.NORMAL_FEELING)
        self.assertTrue(workingSensation != None, "should be created")
# many location is deprecated as property
#         self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
#         bytes=workingSensation.bytes()
#         self.assertTrue(bytes != None, "should be get bytes")
#         fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
#         self.assertTrue(fromBytesWorkingSensation != None, "should be created")
#         self.assertEqual(fromBytesWorkingSensation, workingSensation, "should be equal")
#         self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
#         self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
#         self.assertEqual(fromBytesWorkingSensation.getFeeling(), SensationTestCase.NORMAL_FEELING, "should be equal")
       
        # Image
        
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory,
                                                    data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva,
                                                    feeling=SensationTestCase.BETTER_FEELING)
        self.assertEqual(imageSensation.getFeeling(), SensationTestCase.BETTER_FEELING, "should be equal")

        self.assertFalse(imageSensation.isForgettable(), "should be False, until detached")
        imageSensation.detach(robot=self.robot)
        self.assertTrue(imageSensation.isForgettable(), "should be True after detach")

        bytes=imageSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesImageSensation = self.robot.createSensation(bytes=bytes)

        self.assertTrue(imageSensation == fromBytesImageSensation, "should be equal")
        self.assertEqual(fromBytesImageSensation.getDataId(), imageSensation.getDataId(), "should be equal")
        self.assertTrue(imageSensation.isOriginal(), "imageSensation should be original")
        self.assertTrue(fromBytesImageSensation.isOriginal(), "fromBytesImageSensation should be original")
        
        self.assertTrue(imageSensation.getImage() == fromBytesImageSensation.getImage(), "should be equal") # empty image, not given in creation, TODO
        self.assertTrue(imageSensation.getLocations() == fromBytesImageSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesImageSensation.getFeeling(), SensationTestCase.BETTER_FEELING, "should be equal")
        
        self.assertFalse(fromBytesImageSensation.isForgettable(), "should be False, until detached")
        fromBytesImageSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesImageSensation.isForgettable(), "should be True after detach")

        # Voice
        
        data=b'\x01\x02'
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data,
                                                    locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva,
                                                    feeling=SensationTestCase.TERRIFIED_FEELING)
        self.assertEqual(voiceSensation.getFeeling(), SensationTestCase.TERRIFIED_FEELING, "should be equal")

        self.assertFalse(voiceSensation.isForgettable(), "should be False, until detached")
        voiceSensation.detach(robot=self.robot)
        self.assertTrue(voiceSensation.isForgettable(), "should be True after detach")

        self.assertTrue(voiceSensation.getKind() == Sensation.Kind.Eva, "should be equal")
        bytes=voiceSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromBytesVoiceSensation = self.robot.createSensation(bytes=bytes)
        
        self.assertEqual(voiceSensation, fromBytesVoiceSensation, "should be equal")
        self.assertEqual(fromBytesVoiceSensation.getDataId(), voiceSensation.getDataId(), "should be equal")
        self.assertTrue(voiceSensation.isOriginal(), "voiceSensation should be original")
        self.assertTrue(fromBytesVoiceSensation.isOriginal(), "fromBytesVoiceSensation should be original")
        
        self.assertEqual(voiceSensation.getKind(), fromBytesVoiceSensation.getKind(), "should be equal")
        self.assertEqual(voiceSensation.getData(), fromBytesVoiceSensation.getData(), "should be equal")
        self.assertEqual(voiceSensation.getLocations(), fromBytesVoiceSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesVoiceSensation.getFeeling(), SensationTestCase.TERRIFIED_FEELING, "should be equal")
        
        self.assertFalse(fromBytesVoiceSensation.isForgettable(), "should be False, until detached")
        fromBytesVoiceSensation.detach(robot=self.robot)
        self.assertTrue(fromBytesVoiceSensation.isForgettable(), "should be True after detach")
        
        # Location
        
        # Location 1
        
        locationSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Location, memoryType=Sensation.MemoryType.Sensory,
                                                    x = SensationTestCase.LOCATION_1_X,
                                                    y = SensationTestCase.LOCATION_1_Y,
                                                    z = SensationTestCase.LOCATION_1_Z,
                                                    radius = SensationTestCase.LOCATION_1_RADIUS,
                                                    name = SensationTestCase.LOCATION_1_NAME)
        self.assertEqual(locationSensation.getX(), SensationTestCase.LOCATION_1_X, "should be equal")
        self.assertEqual(locationSensation.getY(), SensationTestCase.LOCATION_1_Y, "should be equal")
        self.assertEqual(locationSensation.getZ(), SensationTestCase.LOCATION_1_Z, "should be equal")
        self.assertEqual(locationSensation.getRadius(), SensationTestCase.LOCATION_1_RADIUS, "should be equal")
        self.assertEqual(locationSensation.getName(), SensationTestCase.LOCATION_1_NAME, "should be equal")

        self.assertFalse(locationSensation.isForgettable(), "should be False, until detached")
        locationSensation.detach(robot=self.robot)
        self.assertTrue(locationSensation.isForgettable(), "should be True after detach")

        bytes=locationSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromByteslocationSensation = self.robot.createSensation(bytes=bytes)
        
        self.assertEqual(locationSensation, fromByteslocationSensation, "should be equal")
        self.assertEqual(locationSensation.getX(), fromByteslocationSensation.getX(), "should be equal")
        self.assertEqual(locationSensation.getY(), fromByteslocationSensation.getY(), "should be equal")
        self.assertEqual(locationSensation.getZ(), fromByteslocationSensation.getZ(), "should be equal")
        self.assertEqual(locationSensation.getRadius(), fromByteslocationSensation.getRadius(), "should be equal")
        self.assertEqual(locationSensation.getName(), fromByteslocationSensation.getName(), "should be equal")
        self.assertEqual(fromByteslocationSensation.getDataId(), locationSensation.getDataId(), "should be equal")
        self.assertTrue(locationSensation.isOriginal(), "locationSensation should be original")
        self.assertTrue(fromByteslocationSensation.isOriginal(), "fromByteslocationSensation should be original")
        
        self.assertFalse(fromByteslocationSensation.isForgettable(), "should be False, until detached")
        fromByteslocationSensation.detach(robot=self.robot)
        self.assertTrue(fromByteslocationSensation.isForgettable(), "should be True after detach")
        
        # Location 2
        
        locationSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Location, memoryType=Sensation.MemoryType.Sensory,
                                                    x = SensationTestCase.LOCATION_2_X,
                                                    y = SensationTestCase.LOCATION_2_Y,
                                                    z = SensationTestCase.LOCATION_2_Z,
                                                    radius = SensationTestCase.LOCATION_2_RADIUS,
                                                    name = SensationTestCase.LOCATION_2_NAME)
        self.assertEqual(locationSensation.getX(), SensationTestCase.LOCATION_2_X, "should be equal")
        self.assertEqual(locationSensation.getY(), SensationTestCase.LOCATION_2_Y, "should be equal")
        self.assertEqual(locationSensation.getZ(), SensationTestCase.LOCATION_2_Z, "should be equal")
        self.assertEqual(locationSensation.getRadius(), SensationTestCase.LOCATION_2_RADIUS, "should be equal")
        self.assertEqual(locationSensation.getName(), SensationTestCase.LOCATION_2_NAME, "should be equal")

        self.assertFalse(locationSensation.isForgettable(), "should be False, until detached")
        locationSensation.detach(robot=self.robot)
        self.assertTrue(locationSensation.isForgettable(), "should be True after detach")

        bytes=locationSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        fromByteslocationSensation = self.robot.createSensation(bytes=bytes)
        
        self.assertEqual(locationSensation, fromByteslocationSensation, "should be equal")
        self.assertEqual(locationSensation.getDataId(), fromByteslocationSensation.getDataId(), "should be equal")

        self.assertEqual(locationSensation.getX(), fromByteslocationSensation.getX(), "should be equal")
        self.assertEqual(locationSensation.getY(), fromByteslocationSensation.getY(), "should be equal")
        self.assertEqual(locationSensation.getZ(), fromByteslocationSensation.getZ(), "should be equal")
        self.assertEqual(locationSensation.getRadius(), fromByteslocationSensation.getRadius(), "should be equal")
        self.assertEqual(locationSensation.getName(), fromByteslocationSensation.getName(), "should be equal")
        self.assertEqual(fromByteslocationSensation.getDataId(), locationSensation.getDataId(), "should be equal")
        self.assertTrue(locationSensation.isOriginal(), "locationSensation should be original")
        self.assertTrue(fromByteslocationSensation.isOriginal(), "fromByteslocationSensation should be original")
        
        self.assertFalse(fromByteslocationSensation.isForgettable(), "should be False, until detached")
        fromByteslocationSensation.detach(robot=self.robot)
        self.assertTrue(fromByteslocationSensation.isForgettable(), "should be True after detach")

        print("\ntest_Bytes DONE")
        
    def test_Copy(self):        
        print("\ntest_Copy")
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_2_LOCATIONS)
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        fromWorkingSensation = self.robot.createSensation(sensation=workingSensation)
        self.assertTrue(fromWorkingSensation != None, "should be created")
        self.assertNotEqual(fromWorkingSensation, workingSensation, "should not be equal")
        self.assertEqual(fromWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        self.assertEqual(fromWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertFalse(fromWorkingSensation.isOriginal(), "fromWorkingSensation should be copy")
        
        workingSensation.setLocations(locations = SensationTestCase.SET_1_1_LOCATIONS_1)
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_1_LOCATIONS_1, "should be equal")
        fromWorkingSensation = self.robot.createSensation(sensation=workingSensation)
        self.assertTrue(fromWorkingSensation != None, "should be created")
        self.assertNotEqual(fromWorkingSensation, workingSensation, "should not be equal")
        self.assertEqual(fromWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromWorkingSensation.getLocations(), SensationTestCase.SET_1_1_LOCATIONS_1, "should be equal")
        self.assertEqual(fromWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertFalse(fromWorkingSensation.isOriginal(), "fromWorkingSensation should be copy")
       
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=SensationTestCase.RECEIVEDFROM)
        self.assertTrue(workingSensation != None, "should be created")
        fromWorkingSensation = self.robot.createSensation(sensation=workingSensation)
        self.assertTrue(fromWorkingSensation != None, "should be created")
        self.assertNotEqual(fromWorkingSensation, workingSensation, "should not be equal")
        self.assertTrue(fromWorkingSensation.getReceivedFrom() == SensationTestCase.RECEIVEDFROM, "should be equal")
        self.assertEqual(fromWorkingSensation.getDataId(), workingSensation.getDataId(), "should be equal")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertFalse(fromWorkingSensation.isOriginal(), "fromWorkingSensation should be copy")

        # Voice
        
        data=b'\x01\x02'
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)

        self.assertFalse(voiceSensation.isForgettable(), "should be False, until detached")
        voiceSensation.detach(robot=self.robot)
        self.assertTrue(voiceSensation.isForgettable(), "should be True after detach")

        self.assertTrue(voiceSensation.getKind() == Sensation.Kind.Eva, "should be equal")
        fromVoiceSensation = self.robot.createSensation(sensation=voiceSensation)
        
        self.assertNotEqual(voiceSensation, fromVoiceSensation, "should not be equal")
        self.assertEqual(voiceSensation.getKind(), fromVoiceSensation.getKind(), "should be equal")
        self.assertEqual(voiceSensation.getData(), fromVoiceSensation.getData(), "should be equal")
        self.assertEqual(voiceSensation.getLocations(), fromVoiceSensation.getLocations(), "should be equal")
        self.assertEqual(fromVoiceSensation.getDataId(), voiceSensation.getDataId(), "should be equal")
        self.assertTrue(voiceSensation.isOriginal(), "voiceSensation should be original")
        self.assertFalse(fromVoiceSensation.isOriginal(), "fromVoiceSensation should be copy")
       
        self.assertFalse(fromVoiceSensation.isForgettable(), "should be False, until detached")
        fromVoiceSensation.detach(robot=self.robot)
        self.assertTrue(fromVoiceSensation.isForgettable(), "should be True after detach")

        # Image
        
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory, data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)

        self.assertFalse(imageSensation.isForgettable(), "should be False, until detached")
        imageSensation.detach(robot=self.robot)
        self.assertTrue(imageSensation.isForgettable(), "should be True after detach")

        fromImageSensation = self.robot.createSensation(sensation=imageSensation)

        self.assertTrue(imageSensation == imageSensation, "should be equal")
        self.assertTrue(imageSensation.getImage() == imageSensation.getImage(), "should be equal") # empty image, not given in creation, TODO
        self.assertTrue(imageSensation.getLocations() == imageSensation.getLocations(), "should be equal")
        self.assertEqual(fromImageSensation.getDataId(), imageSensation.getDataId(), "should be equal")
        self.assertTrue(imageSensation.isOriginal(), "imageSensation should be original")
        self.assertFalse(fromImageSensation.isOriginal(), "fromImageSensation should be copy")
        
        self.assertFalse(fromImageSensation.isForgettable(), "should be False, until detached")
        fromImageSensation.detach(robot=self.robot)
        self.assertTrue(fromImageSensation.isForgettable(), "should be True after detach")

        # Normal Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      feeling=SensationTestCase.NORMAL_FEELING)
        fromFeelingSensation = self.robot.createSensation(sensation=feelingSensation)
                
        self.assertFalse(feelingSensation == fromFeelingSensation, "should not be equal")
        self.assertEqual(fromFeelingSensation.getDataId(), feelingSensation.getDataId(), "should be equal")
        self.assertTrue(feelingSensation.isOriginal(), "imageSensation should be original")
        self.assertFalse(fromFeelingSensation.isOriginal(), "fromImageSensation should be copy")
        
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getFeeling() == fromFeelingSensation.getFeeling(), "should be equal")        
        self.assertEqual(fromFeelingSensation.getFeeling(), SensationTestCase.NORMAL_FEELING, "should be equal")        
        
        self.assertFalse(fromFeelingSensation.isForgettable(), "should be False, until detached")
        fromFeelingSensation.detach(robot=self.robot)
        self.assertTrue(fromFeelingSensation.isForgettable(), "should be True after detach")
 
        # Better Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      positiveFeeling=True)
        fromFeelingSensation = self.robot.createSensation(sensation=feelingSensation)
                
        self.assertFalse(feelingSensation == fromFeelingSensation, "should not be equal")
        self.assertEqual(fromFeelingSensation.getDataId(), feelingSensation.getDataId(), "should be equal")
        self.assertTrue(feelingSensation.isOriginal(), "imageSensation should be original")
        self.assertFalse(fromFeelingSensation.isOriginal(), "fromImageSensation should be copy")
        
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getPositiveFeeling(), "should be True")        
        self.assertFalse(feelingSensation.getNegativeFeeling(), "should be False")        
        #self.assertTrue(feelingSensation.getFeeling() == SensationTestCase.NORMAL_FEELING, "should be equal")        
        self.assertTrue(fromFeelingSensation.getPositiveFeeling(), "should be True")        
        self.assertFalse(fromFeelingSensation.getNegativeFeeling(), "should be False")        
        
        # Worse Feeling
        
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=workingSensation, otherAssociateSensation=voiceSensation,
                                                      negativeFeeling=True)
        self.assertFalse(feelingSensation.isForgettable(), "should be False, until detached")

        fromFeelingSensation = self.robot.createSensation(sensation=feelingSensation)
                
        self.assertFalse(feelingSensation == fromFeelingSensation, "should not be equal")
        self.assertEqual(fromFeelingSensation.getDataId(), feelingSensation.getDataId(), "should be equal")
        self.assertTrue(feelingSensation.isOriginal(), "imageSensation should be original")
        self.assertFalse(fromFeelingSensation.isOriginal(), "fromImageSensation should be copy")
        
        self.assertTrue(feelingSensation.getFirstAssociateSensation() == fromFeelingSensation.getFirstAssociateSensation(), "should be equal")
        self.assertTrue(feelingSensation.getOtherAssociateSensation() == fromFeelingSensation.getOtherAssociateSensation(), "should be equal")
        self.assertFalse(feelingSensation.getPositiveFeeling(), "should be False")        
        self.assertTrue(feelingSensation.getNegativeFeeling(), "should be True") 
        
        self.assertFalse(fromFeelingSensation.getPositiveFeeling(), "should be False")        
        self.assertTrue(fromFeelingSensation.getNegativeFeeling(), "should be True")        
               
        #self.assertTrue(feelingSensation.getFeeling() == SensationTestCase.NORMAL_FEELING, "should be equal")        

        self.assertFalse(fromFeelingSensation.isForgettable(), "should be False, until detached")
        fromFeelingSensation.detach(robot=self.robot)
        self.assertTrue(fromFeelingSensation.isForgettable(), "should be True after detach")
        
        # Feeling is property of every SensationType
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_1_LOCATIONS_2,
                                                      feeling=SensationTestCase.NORMAL_FEELING)
        self.assertTrue(workingSensation != None, "should be created")
# many location is deprecated as property
#         self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
#         bytes=workingSensation.bytes()
#         self.assertTrue(bytes != None, "should be get bytes")
#         fromWorkingSensation = self.robot.createSensation(bytes=bytes)
#         self.assertTrue(fromWorkingSensation != None, "should be created")
#         self.assertEqual(fromWorkingSensation, workingSensation, "should be equal")
#         self.assertEqual(fromWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
#         self.assertEqual(fromWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
#         self.assertEqual(fromWorkingSensation.getFeeling(), SensationTestCase.NORMAL_FEELING, "should be equal")
       
        # Image
        
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory,
                                                    data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva,
                                                    feeling=SensationTestCase.BETTER_FEELING)
        self.assertEqual(imageSensation.getFeeling(), SensationTestCase.BETTER_FEELING, "should be equal")

        self.assertFalse(imageSensation.isForgettable(), "should be False, until detached")
        imageSensation.detach(robot=self.robot)
        self.assertTrue(imageSensation.isForgettable(), "should be True after detach")

        fromImageSensation = self.robot.createSensation(sensation=imageSensation)

        self.assertFalse(imageSensation == fromImageSensation, "should not be equal")
        self.assertEqual(fromImageSensation.getDataId(), imageSensation.getDataId(), "should be equal")
        
        self.assertTrue(imageSensation.getImage() == fromImageSensation.getImage(), "should be equal") # empty image, not given in creation, TODO
        self.assertTrue(imageSensation.getLocations() == fromImageSensation.getLocations(), "should be equal")
        self.assertEqual(fromImageSensation.getFeeling(), SensationTestCase.BETTER_FEELING, "should be equal")
        
        self.assertFalse(fromImageSensation.isForgettable(), "should be False, until detached")
        fromImageSensation.detach(robot=self.robot)
        self.assertTrue(fromImageSensation.isForgettable(), "should be True after detach")

        # Voice
        
        data=b'\x01\x02'
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data,
                                                    locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva,
                                                    feeling=SensationTestCase.TERRIFIED_FEELING)
        self.assertEqual(voiceSensation.getFeeling(), SensationTestCase.TERRIFIED_FEELING, "should be equal")

        self.assertFalse(voiceSensation.isForgettable(), "should be False, until detached")
        voiceSensation.detach(robot=self.robot)
        self.assertTrue(voiceSensation.isForgettable(), "should be True after detach")

        self.assertTrue(voiceSensation.getKind() == Sensation.Kind.Eva, "should be equal")
        fromVoiceSensation = self.robot.createSensation(sensation=voiceSensation)
        
        self.assertNotEqual(voiceSensation, fromVoiceSensation, "should be equal")
        self.assertEqual(fromVoiceSensation.getDataId(), voiceSensation.getDataId(), "should be equal")
        self.assertTrue(voiceSensation.isOriginal(), "voiceSensation should be original")
        self.assertFalse(fromVoiceSensation.isOriginal(), "fromVoiceSensation should be copy")
        
        self.assertEqual(voiceSensation.getKind(), fromVoiceSensation.getKind(), "should be equal")
        self.assertEqual(voiceSensation.getData(), fromVoiceSensation.getData(), "should be equal")
        self.assertEqual(voiceSensation.getLocations(), fromVoiceSensation.getLocations(), "should be equal")
        self.assertEqual(fromVoiceSensation.getFeeling(), SensationTestCase.TERRIFIED_FEELING, "should be equal")
        
        self.assertFalse(fromVoiceSensation.isForgettable(), "should be False, until detached")
        fromVoiceSensation.detach(robot=self.robot)
        self.assertTrue(fromVoiceSensation.isForgettable(), "should be True after detach")
        
        # Location
        
        # Location 1
        
        locationSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Location, memoryType=Sensation.MemoryType.Sensory,
                                                    x = SensationTestCase.LOCATION_1_X,
                                                    y = SensationTestCase.LOCATION_1_Y,
                                                    z = SensationTestCase.LOCATION_1_Z,
                                                    radius = SensationTestCase.LOCATION_1_RADIUS,
                                                    name = SensationTestCase.LOCATION_1_NAME)
        self.assertEqual(locationSensation.getX(), SensationTestCase.LOCATION_1_X, "should be equal")
        self.assertEqual(locationSensation.getY(), SensationTestCase.LOCATION_1_Y, "should be equal")
        self.assertEqual(locationSensation.getZ(), SensationTestCase.LOCATION_1_Z, "should be equal")
        self.assertEqual(locationSensation.getRadius(), SensationTestCase.LOCATION_1_RADIUS, "should be equal")
        self.assertEqual(locationSensation.getName(), SensationTestCase.LOCATION_1_NAME, "should be equal")

        self.assertFalse(locationSensation.isForgettable(), "should be False, until detached")
        locationSensation.detach(robot=self.robot)
        self.assertTrue(locationSensation.isForgettable(), "should be True after detach")

        fromLocationSensation  = self.robot.createSensation(sensation=locationSensation )
        
        self.assertNotEqual(locationSensation, fromLocationSensation, "should not be equal")
        self.assertEqual(locationSensation.getX(), fromLocationSensation.getX(), "should be equal")
        self.assertEqual(locationSensation.getY(), fromLocationSensation.getY(), "should be equal")
        self.assertEqual(locationSensation.getZ(), fromLocationSensation.getZ(), "should be equal")
        self.assertEqual(locationSensation.getRadius(), fromLocationSensation.getRadius(), "should be equal")
        self.assertEqual(locationSensation.getName(), fromLocationSensation.getName(), "should be equal")
        self.assertEqual(fromLocationSensation.getDataId(), locationSensation.getDataId(), "should be equal")
        self.assertTrue(locationSensation.isOriginal(), "locationSensation should be original")
        self.assertFalse(fromLocationSensation.isOriginal(), "fromLocationSensation should be copy")
        
        self.assertFalse(fromLocationSensation.isForgettable(), "should be False, until detached")
        fromLocationSensation.detach(robot=self.robot)
        self.assertTrue(fromLocationSensation.isForgettable(), "should be True after detach")
        
        # Location 2
        
        locationSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Location, memoryType=Sensation.MemoryType.Sensory,
                                                    x = SensationTestCase.LOCATION_2_X,
                                                    y = SensationTestCase.LOCATION_2_Y,
                                                    z = SensationTestCase.LOCATION_2_Z,
                                                    radius = SensationTestCase.LOCATION_2_RADIUS,
                                                    name = SensationTestCase.LOCATION_2_NAME)
        self.assertEqual(locationSensation.getX(), SensationTestCase.LOCATION_2_X, "should be equal")
        self.assertEqual(locationSensation.getY(), SensationTestCase.LOCATION_2_Y, "should be equal")
        self.assertEqual(locationSensation.getZ(), SensationTestCase.LOCATION_2_Z, "should be equal")
        self.assertEqual(locationSensation.getRadius(), SensationTestCase.LOCATION_2_RADIUS, "should be equal")
        self.assertEqual(locationSensation.getName(), SensationTestCase.LOCATION_2_NAME, "should be equal")

        self.assertFalse(locationSensation.isForgettable(), "should be False, until detached")
        locationSensation.detach(robot=self.robot)
        self.assertTrue(locationSensation.isForgettable(), "should be True after detach")

        fromLocationSensation  = self.robot.createSensation(sensation=locationSensation )
        
        self.assertNotEqual(locationSensation, fromLocationSensation, "should not be equal")
        self.assertEqual(locationSensation.getDataId(), fromLocationSensation.getDataId(), "should be equal")

        self.assertEqual(locationSensation.getX(), fromLocationSensation.getX(), "should be equal")
        self.assertEqual(locationSensation.getY(), fromLocationSensation.getY(), "should be equal")
        self.assertEqual(locationSensation.getZ(), fromLocationSensation.getZ(), "should be equal")
        self.assertEqual(locationSensation.getRadius(), fromLocationSensation.getRadius(), "should be equal")
        self.assertEqual(locationSensation.getName(), fromLocationSensation.getName(), "should be equal")
        self.assertEqual(fromLocationSensation.getDataId(), locationSensation.getDataId(), "should be equal")
        self.assertTrue(locationSensation.isOriginal(), "locationSensation should be original")
        self.assertFalse(fromLocationSensation.isOriginal(), "fromLocationSensation should be copy")
        
        self.assertFalse(fromLocationSensation.isForgettable(), "should be False, until detached")
        fromLocationSensation.detach(robot=self.robot)
        self.assertTrue(fromLocationSensation.isForgettable(), "should be True after detach")

        print("\ntest_Copy DONE")

    def test_Boolean(self):        
        print("\ntest_Bytes")
        t = True
        f = False
        
        b = Sensation.booleanToBytes(t)
        self.assertEqual(t, Sensation.bytesToBoolean(b), "should be same")
        #self.assertEqual(t, Sensation.intToBoolean(int(x=b, base=16)), "should be same") # Can't test this way
        
        b = Sensation.booleanToBytes(f)
        self.assertEqual(f, Sensation.bytesToBoolean(b), "should be same")
        
    def test_getRobotType(self):        
        print("\ntest_getRobotType")
        self.robot.setMainNames(SensationTestCase.MAINNAMES_1)

        # Voice        
        voiceSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Voice, robotType=Sensation.RobotType.Sense, isCommunication=True)
        self.assertEqual(voiceSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Sense, 'isCommunication same mainNames RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Muscle, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Muscle')
        
        voiceSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Voice, robotType=Sensation.RobotType.Muscle, isCommunication=True)
        self.assertEqual(voiceSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Muscle, 'isCommunication  same mainNames RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Sense, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Sense')
        
        #Image
        imageSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Image, robotType=Sensation.RobotType.Sense, isCommunication=True)
        self.assertEqual(imageSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Sense, 'isCommunication  same mainNames RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Muscle, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Muscle')
        
        imageSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Image, robotType=Sensation.RobotType.Muscle, isCommunication=True)
        self.assertEqual(imageSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Muscle, 'isCommunication same mainNames RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Sense, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Sense')

        #Item
        itemSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Item, robotType=Sensation.RobotType.Sense)
        self.assertEqual(itemSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Sense, 'same mainNames RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Sense, 'other mainNames RobotType should be Sensation.RobotType.Sense')
        
        itemSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Item, robotType=Sensation.RobotType.Muscle)
        self.assertEqual(itemSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Muscle, 'same mainNames RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Muscle, 'other mainNames RobotType should be Sensation.RobotType.Muscle')

        #Feeling
        feelingSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Feeling, robotType=Sensation.RobotType.Sense)
        self.assertEqual(feelingSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Sense, 'same mainNames RobotType should be Sensation.RobotType.Sense')
        self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Sense, 'other mainNames RobotType should be Sensation.RobotType.Sense')
        
        feelingSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Feeling, robotType=Sensation.RobotType.Muscle)
        self.assertEqual(feelingSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
                                                     Sensation.RobotType.Muscle, 'same mainNames RobotType should be Sensation.RobotType.Muscle')
        self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
                                                     Sensation.RobotType.Muscle, 'other mainNames RobotType should be Sensation.RobotType.Muscle')

        
if __name__ == '__main__':
    unittest.main()

 