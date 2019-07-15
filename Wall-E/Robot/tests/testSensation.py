'''
Created on 10.06.2019
Updated on 13.07.2019
@author: reijo.korhonen@gmail.com

test Sensation class
python3 -m unittest tests/testSensation.py


'''
import time as systemTime
import unittest
from Sensation import Sensation

class SensationTestCase(unittest.TestCase):
    TEST_RUNS = 2
    SCORE=0.5
    SCORE2=0.8
    
    FEELING = Sensation.Association.Feeling.Good
    BETTER_FEELING = Sensation.Association.Feeling.Happy
    TERRIFIED_FEELING = Sensation.Association.Feeling.Terrified

    def setUp(self):
        self.sensation = Sensation.create(associations=None, sensationType=Sensation.SensationType.Item, memory=Sensation.Memory.Sensory, name='test')
        self.assertIsNot(self.sensation, None)
        self.assertIs(len(self.sensation.getAssociations()), 0)
        #print('\nlogAssociations 1: setUp')
        Sensation.logAssociations(self.sensation)
        
        self.feeling = SensationTestCase.FEELING

    def tearDown(self):
        self.sensation.delete()
        
    def test_Memorybility(self):        
        longTermSensation = Sensation.create(associations=None, sensationType=Sensation.SensationType.Item, memory=Sensation.Memory.LongTerm, name='LongTerm_test')
        self.assertIsNot(longTermSensation, None)
        self.assertIs(len(longTermSensation.getAssociations()), 0)

        print("\nSensory time  now")
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm time  now")
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() > longTermSensation.getMemorability(), 'now Sensory sensation must be more Memorability than Longterm sensation')

        # set sensation to the past and look again  
        history_time = Sensation.sensationMemoryLiveTimes[self.sensation.getMemory()] * 0.5      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[self.sensation.getMemory()] * 0.8      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() < longTermSensation.getMemorability(), 'near end Sensory lifetime Sensory sensation must be less Memorability than Longterm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[self.sensation.getMemory()] * 0.98      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() < longTermSensation.getMemorability(), 'very near end Sensory lifetime Sensory sensation must be less Memorability than Longterm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemory()] * 0.5      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'half Longterm lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemory()] * 0.8      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'near Longterm lifetime Sensory sensation must still be more than zero')
        
         # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemory()] * 0.95      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'very near Longterm lifetime Sensory sensation must still be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemory()] * 0.98      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'very very near Longterm lifetime Sensory sensation must still be more than zero')
        
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemory()] * 1.05      
        self.sensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
        print("self.sensation.getLiveTimeLeftRatio() " + str(self.sensation.getLiveTimeLeftRatio()))
        print("self.sensation.getMemorability() " + str(self.sensation.getMemorability()))
        print("LongTerm history time " + str(history_time))
        print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(self.sensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability() == 0.0, 'beyond end Longterm lifetime Sensory sensation  must be zero')

    def test_Importance(self):        
        print("\ntest_Importance")
        longTermSensation = Sensation.create(associations=None, sensationType=Sensation.SensationType.Item, memory=Sensation.Memory.LongTerm, name='LongTerm_Importance_test')
        self.assertIsNot(longTermSensation, None)
        self.assertIs(len(longTermSensation.getAssociations()), 0)
        longTermSensation.associate(sensation=self.sensation,
                                    score=SensationTestCase.SCORE,
                                    feeling=SensationTestCase.FEELING)
        Sensation.logAssociations(longTermSensation)
        self.assertIs(len(longTermSensation.getAssociations()), 1)
        association = self.sensation.getAssociation(sensation=longTermSensation)
        self.assertIsNot(association, None)
        print("SensationTestCase.FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > 0.0, "association importance must greater than zero")
        print("SensationTestCase.FEELING longTermSensation.getImportance() " + str(longTermSensation.getImportance()))
        self.assertTrue(longTermSensation.getImportance() > 0.0, "sensation now importance must greater than zero")
        
        previousAssociationImportance = association.getImportance()
        previousLongTermSensationImportance = longTermSensation.getImportance()
        association.setFeeling(feeling=SensationTestCase.BETTER_FEELING)
        print("SensationTestCase.BETTER_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > previousAssociationImportance, "better feeling association importance must greater than worse feeling")
        print("SensationTestCase.BETTER_FEELING longTermSensation.getImportance() " + str(longTermSensation.getImportance()))
        self.assertTrue(longTermSensation.getImportance() > previousLongTermSensationImportance, "better feeling sensation now importance must greater than worse feeling")
        
        previousAssociationImportance = association.getImportance()
        previousLongTermSensationImportance = longTermSensation.getImportance()
        association.setFeeling(feeling=SensationTestCase.TERRIFIED_FEELING)
        print("feeling=SensationTestCase.TERRIFIED_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() < previousAssociationImportance, "terrified feeling association importance must smaller than any other feeling")
        print("feeling=SensationTestCase.TERRIFIED_FEELING longTermSensation.getImportance() " + str(longTermSensation.getImportance()))
        self.assertTrue(longTermSensation.getImportance() < previousLongTermSensationImportance, "terrified feeling sensation now importance must smaller than any other feeling")
       
        previousAssociationImportance = association.getImportance()
        previousLongTermSensationImportance = longTermSensation.getImportance()
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemory()] * 0.5      
        longTermSensation.setTime(systemTime.time() - history_time)
        association.setTime(systemTime.time() - history_time)
        print("[longTermSensation.getMemory()] * 0.5 longTermSensation.getImportance() " + str(longTermSensation.getImportance()))
        self.assertTrue(longTermSensation.getImportance() > previousLongTermSensationImportance, "terrified feeling sensation must be more positive when time goes on")

    def test_AddAssociations(self):
        for i in range(SensationTestCase.TEST_RUNS):
            self.do_test_AddAssociation()

        
    def do_test_AddAssociation(self):
        addSensation = Sensation.create(associations=None, sensation=self.sensation, memory=Sensation.Memory.LongTerm, name='connect_test')
        self.assertIsNot(addSensation, None)
        
        addSensation.setName('connect_test')
        addSensation.setMemory(Sensation.Memory.LongTerm)
        addSensation.save()    # this is worth to save its data
        association_number = len(self.sensation.getAssociations())
        #print('\nlogAssociations 2: test_AddAssociation')
        Sensation.logAssociations(addSensation)
        
        self.sensation.associate(sensation=addSensation,
                                 score=SensationTestCase.SCORE,
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

        self.assertIs(len(self.sensation.getAssociations()), association_number+1)
        self.assertIs(self.sensation.getScore(), SensationTestCase.SCORE)
        self.assertIs(self.sensation.getFeeling(), self.feeling)
        
        self.assertIs(len(addSensation.getAssociations()), association_number+1)
        self.assertIs(addSensation.getScore(), SensationTestCase.SCORE)
        self.assertIs(addSensation.getFeeling(), self.feeling)
        
        # TODO rest if the test

        #print('\nlogAssociations 5: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        # again, should not add association twise
        self.sensation.addAssociation(Sensation.Association(self_sensation=self.sensation,
                                                            sensation=addSensation,
                                                            score=SensationTestCase.SCORE2,
                                                            feeling=SensationTestCase.TERRIFIED_FEELING))
        self.assertIs(len(self.sensation.getAssociations()), association_number+1)
        self.assertIs(self.sensation.getScore(), SensationTestCase.SCORE)
        self.assertIs(self.sensation.getFeeling(), self.feeling)
        
        self.assertIs(len(addSensation.getAssociations()), association_number+1)
        self.assertIs(addSensation.getScore(), SensationTestCase.SCORE)
        self.assertIs(addSensation.getFeeling(), self.feeling)

        #print('\nlogAssociations 6: test_AddAssociation')
        Sensation.logAssociations(self.sensation)
        
        # better feeling
        self.feeling = SensationTestCase.BETTER_FEELING
        addAssociation = addSensation.getAssociation(self.sensation)
        self.assertIsNot(addAssociation, None)

        # change feeling in association        
        addAssociation.setFeeling(self.feeling)
        # and it should be changed in both way association in both ways
        self.assertIs(self.sensation.getFeeling(), self.feeling)
        self.assertIs(addSensation.getFeeling(), self.feeling)



        
if __name__ == '__main__':
    unittest.main()

 