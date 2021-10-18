'''
Created on 10.06.2019
Updated on 14.03.2021
@author: reijo.korhonen@gmail.com

test Sensation class
python3 -m unittest tests/testSensation.py


'''
import time as systemTime
import os
import shutil as shutil
#import math as testMath
from enum import Enum
import struct
import random

from PIL import Image as PIL_Image
# for testing, get Image comparison
from PIL import ImageChops


import unittest
from Sensation import Sensation#, booleanToBytes, bytesToBoolean
from Robot import Robot
from Memory import Memory

#deprecated
# # 
# # from pygments.lexers import robotframework
# try:
#     import cPickle as pickle
# #except ModuleNotFoundError:
# except Exception as e:
# #    print ("import cPickle as pickle error " + str(e))
#     import pickle

class SensationTestCase(unittest.TestCase):
    TEST_RUNS = 3
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
    
    # Fron Sensation.py
    # Values are changed, so we don't harm real runs
    
    DATADIR =           'data'
    PICLE_FILENAME =    'test_Sensation.pkl'
    PATH_TO_PICLE_FILE = os.path.join(DATADIR, PICLE_FILENAME)
    
    NAME1 = 'Wall_E'
    NAME2 = 'Eva'

    

    def setUp(self):
        self.robot=Robot(mainRobot=None)
        self.memory = self.robot.getMemory()
        # To test, we should know what is in memory, 
        # we should clear Sensation memory from binary files loaded sensation
        del self.memory.sensationMemory[:]
        self.initialMemoryLen=len(self.memory.sensationMemory)
        #TODO we would also detete Root.selfSensations
        # How to check if this makes difference to results

        self.sensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                    name='test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Entering)
        self.assertEqual(self.sensation.getPresence(), Sensation.Presence.Entering, "should be entering")
        self.assertIsNot(self.sensation, None)
        #self.assertEqual(len(self.sensation.getAssociations()), self.initialMemoryLen) ## oops self.initialMemoryLen+1 or self.initialMemoryLen
        self.assertTrue(len(self.sensation.getAssociations()) == self.initialMemoryLen or len(self.sensation.getAssociations()) == self.initialMemoryLen+1)
        Sensation.logAssociations(self.sensation)
        
        self.feeling = SensationTestCase.NORMAL_FEELING

    def tearDown(self):
        self.sensation.delete()
        
    '''
        Sensation Memorability is time based function
        There are many ways to define this
        Sensation only would be time based + feeling based.
        
        Memory.forgetLessImportantSensations uses this so it would be best choice,
        feeling is based o associations, changing Sensations memorability if some association happens
        
        Associations have feelings and time. Sensations have time. we could define
        Sensation Memorability be time, Association Memorability by time+feeling and
        Sensation whole Memorability by Sensation Memorability + its Associations Memorability.
        Functions are
        1) Sensation only
        2) Sensation+its association sensation based on Feeling and time
           - used in Memory.forgetLessImportantSensations
        3) Sensations + list of potential Item-Sensations based on Feeling and Time
           - used in Communication
    '''
        
    def test_doGetMemorability(self):
        print('\ntest_doGetMemorability')

        # now 
        print("\ntime now")
        testTime = systemTime.time()
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        # sensoryMemorability > workingMemorability >l ongTermMemorability
        
        self.assertTrue(sensoryMemorability > workingMemorability)
        self.assertTrue(sensoryMemorability > longTermMemorability)
        self.assertTrue(workingMemorability > longTermMemorability)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 0.1)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) < 0.1)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) < 0.1)
       
        self.assertTrue(feelingSensoryMemorability > feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability > feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)

        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) > 100.0)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) > 100.0)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) > 100.0)
       
        self.assertTrue(feelingSensoryMemorability > feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability > feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)
        
        # Test in half time Sensory lifetime
        print("\nhalf time of Sensory lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.Sensory]/2
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        # workingMemorability > sensoryMemorability >longTermMemorability
        
        self.assertTrue(sensoryMemorability < workingMemorability)
        self.assertTrue(sensoryMemorability > longTermMemorability)
        self.assertTrue(workingMemorability > longTermMemorability)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 0.1)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) < 0.1)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) < 0.1)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability > feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)

        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        test=abs(sensoryMemorability)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) > 100.0)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) > 100.0)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) > 100.0)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability > feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)
        
        # Test near end time of Sensory lifetime
        print("\nnear end time of Sensory lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.Sensory] *.98
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        # sensoryMemorability < workingMemorability  >longTermMemorability
        
        self.assertTrue(sensoryMemorability < workingMemorability)
        self.assertTrue(sensoryMemorability < longTermMemorability)
        self.assertTrue(workingMemorability > longTermMemorability)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        test=abs(sensoryMemorability)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 0.1)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) < 0.1)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) < 0.1)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability < feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)

        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 100.0)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) > 100.0)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) > 100.0)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability < feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)
        
####################################################################################################################
# Working

        # Test in half time Working lifetime
        print("\nhalf time of Working lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.Working]/2
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        
        self.assertTrue(sensoryMemorability < workingMemorability)
        self.assertTrue(sensoryMemorability < longTermMemorability)
        self.assertTrue(workingMemorability > longTermMemorability)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        test=abs(sensoryMemorability)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 0.1)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) < 0.1)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) < 0.1)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability < feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)

        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        test=abs(sensoryMemorability)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 0.1)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) > 100.0)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) > 100.0)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability < feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability > feelingLongTermMemorability)
        
        # Test near end time of Working lifetime
        print("\nnear end time of Working lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.Working] *.98
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        # sensoryMemorability < workingMemorability  >longTermMemorability
        
        self.assertTrue(sensoryMemorability < workingMemorability)
        self.assertTrue(sensoryMemorability < longTermMemorability)
        self.assertTrue(workingMemorability < longTermMemorability)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        test=abs(sensoryMemorability)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 0.1)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) < 0.1)
        self.assertTrue(abs(longTermMemorability - feelingLongTermMemorability) < 0.1)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability < feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability < feelingLongTermMemorability)

        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(abs(sensoryMemorability - feelingSensoryMemorability) < 1.0)
        self.assertTrue(abs(workingMemorability - feelingWorkingMemorability) > 10.0)
        self.assertTrue(abs(longTermMemorability - feelingLongTermMemorability) > 100.0)
       
        self.assertTrue(feelingSensoryMemorability < feelingWorkingMemorability)
        self.assertTrue(feelingSensoryMemorability < feelingLongTermMemorability)
        self.assertTrue(feelingWorkingMemorability < feelingLongTermMemorability)

####################################################################################################################
# LongTerm

        # Test in half time LongTerm lifetime
        print("\nhalf time of LongTerm lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.LongTerm]/2
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        
        self.assertTrue(sensoryMemorability == 0.0)
        self.assertTrue(workingMemorability == 0.0)
        self.assertTrue(longTermMemorability > 0.0)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(feelingSensoryMemorability == 0.0)
        self.assertTrue(feelingWorkingMemorability == 0.0)
        self.assertTrue(abs(longTermMemorability -feelingLongTermMemorability) < 0.1)
       

        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(feelingSensoryMemorability == 0.0)
        self.assertTrue(feelingWorkingMemorability == 0.0)
        self.assertTrue(abs(longTermMemorability - feelingLongTermMemorability) > 100.0)
        
        # Test near end time of LongTerm lifetime
        print("\nnear end time of LongTerm lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.LongTerm] *.98
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                           memoryType = Sensation.MemoryType.LongTerm)
        # sensoryMemorability < workingMemorability  >longTermMemorability
        
        self.assertTrue(sensoryMemorability == 0.0)
        self.assertTrue(workingMemorability == 0.0)
        self.assertTrue(longTermMemorability > 0.0)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(feelingSensoryMemorability == 0.0)
        self.assertTrue(feelingWorkingMemorability == 0.0)
        self.assertTrue(abs(feelingLongTermMemorability - longTermMemorability) < 0.1)
       
        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(feelingSensoryMemorability == 0.0)
        self.assertTrue(feelingWorkingMemorability == 0.0)
        self.assertTrue(abs(feelingLongTermMemorability - longTermMemorability) > 10.0)
       
        # Test beyond end time of LongTerm lifetime
        print("\nbeyond end time of LongTerm lifetime")
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.LongTerm] * 1.1
        sensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Sensory)
        workingMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.Working)
        longTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                          memoryType = Sensation.MemoryType.LongTerm)
        # sensoryMemorability < workingMemorability  >longTermMemorability
        
        self.assertTrue(sensoryMemorability == 0.0)
        self.assertTrue(workingMemorability == 0.0)
        self.assertTrue(longTermMemorability == 0.0)
        
        # test Feeling
        # neutral feeling does not change much
        feeling = Sensation.Feeling.Neutral
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(feelingSensoryMemorability == 0.0)
        self.assertTrue(feelingWorkingMemorability == 0.0)
        self.assertTrue(feelingLongTermMemorability == 0.0)
       
        # InLove feeling does change much
        feeling = Sensation.Feeling.InLove
        score = 0.8
        feelingSensoryMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Sensory,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingWorkingMemorability = Sensation.doGetMemorability(time = testTime,
                                                                 memoryType = Sensation.MemoryType.Working,
                                                                 feeling=feeling,
                                                                 score=score)
        feelingLongTermMemorability = Sensation.doGetMemorability(time = testTime,
                                                                  memoryType = Sensation.MemoryType.LongTerm,
                                                                  feeling=feeling,
                                                                  score=score)
        self.assertTrue(feelingSensoryMemorability == 0.0)
        self.assertTrue(feelingWorkingMemorability == 0.0)
        self.assertTrue(feelingLongTermMemorability == 0.0)
       

        

    '''
        Sensation Memorability is time based function
        There are many ways to define this
        Sensation only would be time based + feeling based.
        
        Memory.forgetLessImportantSensations uses this so it would be best choice,
        feeling is based o associations, changing Sensations memorability if some association happens
        
        Associations have feelings and time. Sensations have time. we could define
        Sensation Memorability be time, Association Memorability by time+feeling and
        Sensation whole Memorability by Sensation Memorability + its Associations Memorability.
        Functions are
        1) Sensation only
        2) Sensation+its association sensation based on Feeling and time
           - used in Memory.forgetLessImportantSensations
        3) Sensations + list of potential Item-Sensations based on Feeling and Time
           - used in Communication
    '''
        
    def test_Sensation_Only_Memorybility(self):
        print('\ntest_Memorybility')
        sensorySensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                      name='Working_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(sensorySensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(sensorySensation, None)
        #self.assertEqual(len(sensorySensation.getAssociations()), self.initialMemoryLen) # OOPS this depends

        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation, None)
        #self.assertEqual(len(workingSensation.getAssociations()), self.initialMemoryLen) # OOPS This depends

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                       name='LongTerm', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(longTermSensation, None)
        #self.assertEqual(len(longTermSensation.getAssociations()), self.initialMemoryLen)
                                                                      # OOPS This depends
                                                                      # 2 sensations are associated each other if they are Exiting, changed to Absent
                                                                      # to west they should not, but be independent to get memorability of each other
                                                                      # lets do some violance to separate them.

        print("\nSensory time now")
#         #print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working time now")
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("LongTerm time now")
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() > workingSensation.getMemorability(), 'now Sensory sensation must be more Memorability than Working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'now Working sensation must be more Memorability than LongTerm sensation')

        # set sensation to the past and look again  
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.5      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'half Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # test Feeling, it is not worth to remember after processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability() == 0.0, 'feelingSensation sensation must be zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.8      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        
        print("sensorySensation.getMemorability() {} < workingSensation.getMemorability() {}".format(sensorySensation.getMemorability(), workingSensation.getMemorability()))
       
        self.assertTrue(sensorySensation.getMemorability() < workingSensation.getMemorability(), 'near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.98      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() < workingSensation.getMemorability(), 'very near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'very near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.5      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'half working lifetime Working sensation must be more than zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'half working lifetime LongTerm sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.8      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
         # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.95      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very near working lifetime Working sensation must be less Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.98      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very very near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 1.05      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.5     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.98     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'very very near long term lifetime Sensory sensation must still be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 1.02     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  == 0.0, 'beyond end long term lifetime Sensory sensation must be zero')
        
        # test Feeling, it is not worth to remember aftered processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability()  == 0.0, 'feelingSensation sensation must be zero')
        
    '''
    Test Memorability with Assosiations
    '''

    def test_Sensation_Assosiations_Memorybility(self):
        print('\ntest_Sensation_Assosiations_Memorybility')
        
        # create SensatyType-Item Sensations
        sensorySensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                      name=self.NAME1, score=SensationTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertEqual(sensorySensation.getPresence(), Sensation.Presence.Present, "should be Absent")
        self.assertIsNot(sensorySensation, None)
        #self.assertEqual(len(sensorySensation.getAssociations()), self.initialMemoryLen+1)  # OOPS this depends

        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name=self.NAME1, score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation, None)
        #self.assertEqual(len(workingSensation.getAssociations()), self.initialMemoryLen) # OOPS this depends

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                       name=self.NAME1, score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(longTermSensation, None)
        #self.assertEqual(len(longTermSensation.getAssociations()), self.initialMemoryLen)# OOPS this depends
                                                                                           #2 sensations are associated each other if they are Exiting, changed to Absent
                                                                      # to test they should not, but be independent to get memorability of each other
                                                                      # lets do some violance to separate them.
                                                                      
        # Create Voice sensation with default parameters
        voiceSensation1 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory)
        # associate voice it to longterm Item
        longTermSensation.associate(sensation=voiceSensation1)
        # We should now get memoraboility
        voiceSensation1Memorability = voiceSensation1.getMemorability(itemSensations = [longTermSensation])
        self.assertTrue(voiceSensation1Memorability > 0)
        # make better feeling
        association = voiceSensation1.getAssociation(sensation=longTermSensation)
        association.setFeeling(feeling=Sensation.Feeling.Normal) #> Neutral
        self.assertTrue( voiceSensation1.getMemorability(itemSensations = [longTermSensation]) > voiceSensation1Memorability, "Better feeling, better Memorability")
        
        association.setFeeling(feeling=Sensation.Feeling.Worried) # < Neutral
        self.assertTrue( voiceSensation1.getMemorability(itemSensations = [longTermSensation]) <  voiceSensation1Memorability, "Worse feeling, worse Memorability")
                                                                      

        
        # create other SensatyType-Item Sensations
        sensorySensation2 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                      name=self.NAME2, score=SensationTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertEqual(sensorySensation2.getPresence(), Sensation.Presence.Present, "should be Absent")
        self.assertIsNot(sensorySensation2, None)
        #self.assertEqual(len(sensorySensation2.getAssociations()), self.initialMemoryLen) # OOPS This depends

        workingSensation2 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name=self.NAME2, score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation2.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation2, None)
        #self.assertEqual(len(workingSensation2.getAssociations()), self.initialMemoryLen) # OOPS This depends

        longTermSensation2 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                       name=self.NAME2, score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(longTermSensation2.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(longTermSensation2, None)
        #self.assertEqual(len(longTermSensation2.getAssociations()), self.initialMemoryLen) # OOPS This depends # 2 sensations are associated each other if they are Exiting, changed to Absent

        # associate to longTermSensation2
        # to test that Sensation.getMemorability(sensations = []) works independently with Iten.names
        # meaning that Sensations association have independent feeling with names they are defined
        longTermSensation2.associate(sensation=voiceSensation1)
        voiceSensation1Memorability2 = voiceSensation1.getMemorability(itemSensations = [longTermSensation2])
        # and test again with original name associated and we should get same results
        # make worse feeling with other association feeling
        association2 = voiceSensation1.getAssociation(sensation=longTermSensation2)
        association2.setFeeling(feeling=Sensation.Feeling.Normal) #>Neutral
        # still get last result with other association
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation]) <  voiceSensation1Memorability, "Worse feeling still, worse Memorability")
        # other gets its independent Memorability
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation2]) >  voiceSensation1Memorability2, "better feeling still, better Memorability")

        # and if we change original voice now, we get its changed, original voice not
        association.setFeeling(feeling=Sensation.Feeling.Normal) #> Neutral
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation]) > voiceSensation1Memorability, "Better feeling, better Memorability")
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation2]) >  voiceSensation1Memorability2, "better feeling still, better Memorability")

        # make voice 2 Feeling Worse
        association2.setFeeling(feeling=Sensation.Feeling.Worried) #> Neutral
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation]) > voiceSensation1Memorability, "Better feeling, better Memorability")
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation2]) <  voiceSensation1Memorability2, "Worse feeling still, Worse Memorability")

        # test allAssiciations = True
        # verify test
        #self.assertTrue(len(voiceSensation1.getAssociations()) == 2) # OOPS This depends
        voiceSensation1SelfMemorability = voiceSensation1.getMemorability()
        
        association.setFeeling(feeling=Sensation.Feeling.Normal)
        association2.setFeeling(feeling=Sensation.Feeling.Normal)
        self.assertTrue(voiceSensation1.getMemorability(allAssociations=True) > voiceSensation1SelfMemorability, "Memorability with positive association should be bigger than plain, because feelings are discarded, but associations itself are posivite")

        association.setFeeling(feeling=Sensation.Feeling.Worried)
        association2.setFeeling(feeling=Sensation.Feeling.Worried)
        self.assertTrue(voiceSensation1.getMemorability(allAssociations=True) > voiceSensation1SelfMemorability, " Memorability with negative association should be bigger than plain, because feelings are discarded, but associations itself are posivite")


        # Create other voice associated to Name2
        # and test that they are handled independently
        
        # Create Voice sensation with default parameters
        voiceSensation2 = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory)
        # associate voice it to longterm Item
        longTermSensation.associate(sensation=voiceSensation2)
        # We should now get memoraboility
        voiceSensation1Memorability2 = voiceSensation2.getMemorability(itemSensations = [longTermSensation])
        self.assertTrue(voiceSensation1Memorability2 > 0)
        # make better feeling
        association2 = voiceSensation2.getAssociation(sensation=longTermSensation)
        association2.setFeeling(feeling=Sensation.Feeling.Normal) #> Neutral
        self.assertTrue(voiceSensation2.getMemorability(itemSensations = [longTermSensation]) > voiceSensation1Memorability2, "Better feeling, better Memorability")
        
        association2.setFeeling(feeling=Sensation.Feeling.Worried) # < Neutral
        self.assertTrue( voiceSensation1.getMemorability(itemSensations = [longTermSensation]) <  voiceSensation1Memorability2, "Worse feeling, worse Memorability")
        
        # and test again with original name associated and we should get same results
        # make worse feeling with other association feeling
        association2.setFeeling(feeling=Sensation.Feeling.Normal) #>Neutral
        # still get last result with other association
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation]) <  voiceSensation1Memorability, "Worse feeling still, worse Memorability")
        # other gets its independent Memorability
        self.assertTrue(voiceSensation2.getMemorability(itemSensations = [longTermSensation]) >  voiceSensation1Memorability2, "better feeling still, better Memorability")

        # and if we change original voice now, we get its changed, original voice not
        association.setFeeling(feeling=Sensation.Feeling.Normal) #> Neutral
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation]) > voiceSensation1Memorability, "Better feeling, better Memorability")
        self.assertTrue(voiceSensation2.getMemorability(itemSensations = [longTermSensation]) >  voiceSensation1Memorability2, "better feeling still, better Memorability")

        # make voice 2 Feeling Worse
        association2.setFeeling(feeling=Sensation.Feeling.Worried) #> Neutral
        self.assertTrue(voiceSensation1.getMemorability(itemSensations = [longTermSensation]) > voiceSensation1Memorability, "Better feeling, better Memorability")
        self.assertTrue(voiceSensation2.getMemorability(itemSensations = [longTermSensation]) <  voiceSensation1Memorability2, "Worse feeling still, Worse Memorability")

        
        # TODO test times
        
	    # rest part of test is copied from test_Sensation_Assosiations_Memorybility and we should get same results even if we have
        # associations now, when we use Sensation.getMemorability() (without parameters, because it should ignore association
        print("\nSensory time now")
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working time now")
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("LongTerm time now")
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() > workingSensation.getMemorability(), 'now Sensory sensation must be more Memorability than Working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'now Working sensation must be more Memorability than LongTerm sensation')

        # set sensation to the past and look again  
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.5      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'half Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # test Feeling, it is not worth to remember after processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability() == 0.0, 'feelingSensation sensation must be zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.8      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        
        print("sensorySensation.getMemorability() {} < workingSensation.getMemorability() {}".format(sensorySensation.getMemorability(), workingSensation.getMemorability()))
       
        self.assertTrue(sensorySensation.getMemorability() < workingSensation.getMemorability(), 'near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.98      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() < workingSensation.getMemorability(), 'very near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'very near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.5      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'half working lifetime Working sensation must be more than zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'half working lifetime LongTerm sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.8      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
         # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.95      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very near working lifetime Working sensation must be less Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.98      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very very near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 1.05      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.5     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.98     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'very very near long term lifetime Sensory sensation must still be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 1.02     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
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
        sensorySensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                      name='Working_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(sensorySensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(sensorySensation, None)
        #self.assertEqual(len(sensorySensation.getAssociations()), self.initialMemoryLen+0)#1 ## Oops this depends 

        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(workingSensation, None)
        #self.assertEqual(len(workingSensation.getAssociations()), self.initialMemoryLen+0) # OOPS this depends

        longTermSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.LongTerm,
                                                       name='LongTerm', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(longTermSensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        self.assertIsNot(longTermSensation, None)
        #self.assertEqual(len(longTermSensation.getAssociations()), self.initialMemoryLen+0) # OOPS This depends

        print("\nSensory time now")
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working time now")
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
        print("LongTerm time now")
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() > workingSensation.getMemorability(), 'now Sensory sensation must be more Memorability than Working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'now Working sensation must be more Memorability than LongTerm sensation')

        # set sensation to the past and look again  
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.5      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
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
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.8      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() < workingSensation.getMemorability(), 'near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[sensorySensation.getMemoryType()] * 0.98      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() < workingSensation.getMemorability(), 'very near end Sensory lifetime Sensory sensation must be less Memorability than working sensation')
        self.assertTrue(workingSensation.getMemorability() > longTermSensation.getMemorability(), 'very near end Sensory lifetime Working sensation must be more Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.5      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'half working lifetime Working sensation must be more than zero')
        self.assertTrue(longTermSensation.getMemorability() > 0.0, 'half working lifetime LongTerm sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.8      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
         # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.95      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very near working lifetime Working sensation must be less Memorability than LongTerm sensation')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 0.98      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() > 0.0, 'very very near working lifetime Sensory sensation must still be more than zero')
        self.assertTrue(workingSensation.getMemorability() < longTermSensation.getMemorability(), 'very very near working lifetime Working sensation must be less Memorability than LongTerm sensation')
        
        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[workingSensation.getMemoryType()] * 1.05      
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.5     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'long term lifetime Sensory sensation must be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 0.98     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  > 0.0, 'very very near long term lifetime Sensory sensation must still be more than zero')

        # set sensation more to the past and look again        
        history_time = Sensation.sensationMemoryLiveTimes[longTermSensation.getMemoryType()] * 1.02     
        sensorySensation.setTime(systemTime.time() - history_time)
        workingSensation.setTime(systemTime.time() - history_time)
        longTermSensation.setTime(systemTime.time() - history_time)
        print("\nSensory history time " + str(history_time))
#         print("sensorySensation.getLiveTimeLeftRatio() " + str(sensorySensation.getLiveTimeLeftRatio()))
        print("sensorySensation.getMemorability() " + str(sensorySensation.getMemorability()))
        print("Working history time " + str(history_time))
#         print("workingSensation.getLiveTimeLeftRatio() " + str(workingSensation.getLiveTimeLeftRatio()))
        print("workingSensation.getMemorability() " + str(workingSensation.getMemorability()))
#         print("longTermSensation.getLiveTimeLeftRatio() " + str(longTermSensation.getLiveTimeLeftRatio()))
        print("longTermSensation.getMemorability() " + str(longTermSensation.getMemorability()))
        self.assertTrue(sensorySensation.getMemorability() == 0.0, 'beyond end Sensory lifetime Sensory sensation must be zero')
        self.assertTrue(workingSensation.getMemorability() == 0.0, 'beyond end working lifetime Sensory sensation must be zero')
        self.assertTrue(longTermSensation.getMemorability()  == 0.0, 'beyond end long term lifetime Sensory sensation must be zero')
        
        # test Feeling, it is not worth to remember aftered processed
        feelingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                     firstAssociateSensation=longTermSensation, otherAssociateSensation=workingSensation,
                                                     negativeFeeling=True, locations=self.robot.getLocations())
        self.assertTrue(feelingSensation.getMemorability()  == 0.0, 'feelingSensation sensation must be zero')
        
    '''
    deprecated
    '''
    def deprecated_test_Importance(self):        
        print("\ntest_Importance")
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present)
        self.assertEqual(workingSensation.getPresence(), Sensation.Presence.Present, "should be present")
        self.assertIsNot(workingSensation, None)
        self.assertEqual(len(workingSensation.getAssociations()), self.initialMemoryLen+1)
        workingSensation.associate(sensation=sensorySensation,
                                    feeling=SensationTestCase.NORMAL_FEELING)
        Sensation.logAssociations(workingSensation)
        self.assertEqual(len(workingSensation.getAssociations()), self.initialMemoryLen+2)
        association = sensorySensation.getAssociation(sensation=workingSensation)
        self.assertIsNot(association, None)
        print("SensationTestCase.NORMAL_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > 0.0, "association importance must greater than zero")
        print("SensationTestCase.NORMAL_FEELING workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() > 0.0, "sensation now importance must greater than zero")
        
        previousAssociationImportance = association.getImportance()
        previousWorkingSensationImportance = workingSensation.getImportance()
        
        # Feeling
        association.setFeeling(feeling=SensationTestCase.BETTER_FEELING)
        print("SensationTestCase.BETTER_FEELING association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > previousAssociationImportance, "better feeling association importance must greater than worse feeling")
        print("SensationTestCase.BETTER_FEELING workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() > previousWorkingSensationImportance, "better feeling sensation now importance must greater than worse feeling")
 
        #score
        workingSensation.setScore(score=SensationTestCase.SCORE2)
        print("SensationTestCase.bigger_score association.getImportance() " + str(association.getImportance()))
        self.assertTrue(association.getImportance() > previousAssociationImportance, "bigger score association importance must greater than smaller score")
        print("SensationTestCase.bigger_score workingSensation.getImportance() " + str(workingSensation.getImportance()))
        self.assertTrue(workingSensation.getImportance() > previousWorkingSensationImportance, "bigger score sensation now importance must greater than smaller scor")
        
               
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
        #print("[workingSensation.getMemoryType()] * 0.5 workingSensation.getImportance() {} previousWorkingSensationImportance {}".format(workingSensation.getImportance(). previousWorkingSensationImportance))
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
        self.assertTrue(addSensation in self.sensation.copySensations)
        # TODO logic is odd, when we copy a sensation, its data should not be changed ans here name is data
        # We should prevent this
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
        
        
    def test_AssociateRemoveAssociations(self):
        print('\ntest_AddAssociations')
        for i in range(SensationTestCase.TEST_RUNS):
            self.do_test_AssociateRemoveAssociation()

        
    def do_test_AssociateRemoveAssociation(self):
        # test this test
        print('do_test_AssociateRemoveAssociation 0\n')
        self.assertEqual(self.sensation.getScore(), SensationTestCase.SCORE)
        
        # We must set all Items absent
        
        absentensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, memoryType=Sensation.MemoryType.Sensory,
                                                    name='test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Absent)
        self.assertEqual(absentensation.getPresence(), Sensation.Presence.Absent, "should be Absent")
        
        
        # when we create sensation=self.sensation, other parameters can't be used
        #self.robot.createSensation(associations=None, sensation=self.sensation)
        addSensations=[]
        testTime = systemTime.time() - Sensation.sensationMemoryLiveTimes[Sensation.MemoryType.Sensory]/2
        associationNumber = len(self.sensation.getAssociations())
        
        # test asssociation
        for i in range(SensationTestCase.TEST_RUNS):
            addSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory,
                                                      name='do_test_AssociateRemoveAssociation',
                                                      time=testTime)
            self.assertEqual(len(addSensation.getAssociations()), 0)
            self.assertEqual(addSensation.getName(), 'do_test_AssociateRemoveAssociation', "should be \'do_test_AssociateRemoveAssociation\' ")
            self.robot.getMemory().setMemoryType(sensation=addSensation, memoryType=Sensation.MemoryType.Working)
            self.assertEqual(addSensation.getMemoryType(), Sensation.MemoryType.Working, "should be Sensation.MemoryType.Working")
            
            self.sensation.associate(sensation=addSensation,
                                     feeling=self.feeling)
            self.assertEqual(len(addSensation.getAssociations()), 1)
            self.assertEqual(len(self.sensation.getAssociations()), associationNumber+i+1)
            self.assertEqual(self.sensation.getScore(), SensationTestCase.SCORE)
            self.assertEqual(self.sensation.getAssociationFeeling(addSensation), self.feeling)
            self.assertEqual(len(addSensation.getAssociations()), 1)
            
            self.assertEqual(addSensation.getScore(), SensationTestCase.SCORE)
            self.assertEqual(addSensation.getAssociationFeeling(self.sensation), self.feeling)

            j=0            
            for sensation in addSensations:
                sensation.associate(addSensation,
                                    feeling=self.feeling)
                self.assertEqual(len(sensation.getAssociations()), len(addSensations)+1)#i+j+1)
                self.assertEqual(len(addSensation.getAssociations()), j+2)
                j=j+1            
     
            addSensations.append(addSensation)
            self.assertEqual(len(addSensations), i+1)
            
            
    
        
#       # test delete
        while len(addSensations) > 0:
            addSensations[0].delete()
            self.assertEqual(len(addSensations[0].getAssociations()), 0)
            i=1     
            while i < len(addSensations):
                self.assertEqual(len(addSensations[i].getAssociations()), len(addSensations)-1)
                i=i+1
            del addSensations[0]
            
        # TODO test vopy#
        
    '''
    Test PIL-image equality with PILO-library method
    '''
    def areImagesEqual(self, image1, image2):
        diff = ImageChops.difference(image1, image2)

        box = diff.getbbox()
        if box:
            return False
        return True
    
    def test_ItemWithImageVoice(self):        
        print("\ntest_ItemWithImageVoice")
        # voice test data
        data=b'\x01\x02'
        # image test data
        image=PIL_Image.new(mode="RGB", size=(10, 10), color = (153, 153, 255))
        print("1 image.format {}".format(image.format))
        
        self.robot.setMainNames(SensationTestCase.MAINNAMES_1)
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, image=image,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_2_LOCATIONS)
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(SensationTestCase.MAINNAMES_1, workingSensation.getMainNames(), "should be equal")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        
        # test image
        self.assertTrue(workingSensation.getImage() == image, "image should be equal")
        self.assertTrue(self.areImagesEqual(workingSensation.getImage(), image), "image  areImagesEqual should be equal") # should test this thios special method
                
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        
        # NOTE, at this point we should change original sensations id, because other way
        # creations thinks, that we are updating original sensation with new data
        workingSensationId = workingSensation.getId()
        workingSensation.setId(Sensation.getNextId())
        workingSensationDataId   = workingSensation.getDataId()
        workingSensation.setDataId(workingSensation.getId())

        # we should get back original kind Sensation        
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertEqual(fromBytesWorkingSensation.getId(), workingSensationId, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getDataId(), workingSensationDataId, "should be equal")
        
        self.assertNotEqual(fromBytesWorkingSensation, workingSensation, "should not be equal, because we changedmanulla original id")
        self.assertEqual(fromBytesWorkingSensation.getMainNames(), workingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        self.assertNotEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should not be equal, because we changed manually original id")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")
        
#         
        # test Item.image
        self.assertTrue(self.areImagesEqual(workingSensation.getImage(), image), "areImagesEqual should be equal" ) # should test this this special method

        self.assertIsNotNone(fromBytesWorkingSensation.getImage(), "should get image")
        fromBytesImage = fromBytesWorkingSensation.getImage() # this is now JPegImageFile, image is PIL.image, so we can't compare them
        self.assertFalse(self.areImagesEqual(fromBytesWorkingSensation.getImage(), image), "should not be equal, because Image format differs") # should test this thios special method
        self.assertFalse(fromBytesWorkingSensation.getImage() == image, "should not be equal, because Image format differs")
        
        

        # Item with Voice
        voiceSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, data=data,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_2_LOCATIONS)
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(SensationTestCase.MAINNAMES_1, workingSensation.getMainNames(), "should be equal")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        
        # test Voice data
        self.assertTrue(workingSensation.getData() == data, "data should be equal")
                
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        
        # NOTE, at this point we should change original sensations id, because other way
        # creations thinks, that we are updating original sensation with new data
        workingSensationId = workingSensation.getId()
        workingSensation.setId(Sensation.getNextId())
        workingSensationDataId   = workingSensation.getDataId()
        workingSensation.setDataId(workingSensation.getId())

        # we should get back original kind Sensation        
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertEqual(fromBytesWorkingSensation.getId(), workingSensationId, "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getDataId(), workingSensationDataId, "should be equal")
        
        self.assertNotEqual(fromBytesWorkingSensation, workingSensation, "should not be equal, because we changedmanulla original id")
        self.assertEqual(fromBytesWorkingSensation.getMainNames(), workingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        self.assertNotEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should not be equal, because we changed manually original id")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")
        
#         
        # test Item.Voice
        self.assertEqual(workingSensation.getData(), data, " should be equal" ) # should test this this special method

        self.assertIsNotNone(fromBytesWorkingSensation.getData(), "should get data")
        self.assertEqual(fromBytesWorkingSensation.getData(), data, "should be equal")
        self.assertTrue(fromBytesWorkingSensation.getData() == data, "should not be equal")
        # item with voice
        
        
        # TODO maybe voice-test is not reasonable, because  we don't update from bytes, but get new voices, look image below
        
        #data=b'\x01\x02'
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

    
    def test_Bytes(self):        
        print("\ntest_Bytes")
        # voice test data
        data=b'\x01\x02'
        # image test data
        image=PIL_Image.new(mode="RGB", size=(10, 10), color = (153, 153, 255))
        print("1 image.format {}".format(image.format))
        
        self.robot.setMainNames(SensationTestCase.MAINNAMES_1)
        workingSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Item, image=image,
                                                      memoryType=Sensation.MemoryType.Working,
                                                      name='Working_Importance_test', score=SensationTestCase.SCORE, presence=Sensation.Presence.Present, receivedFrom=[],
                                                      locations = SensationTestCase.SET_1_2_LOCATIONS)
        self.assertEqual(SensationTestCase.MAINNAMES_1, workingSensation.getMainNames(), "should be equal")
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        
        # test image
        self.assertTrue(workingSensation.getImage() == image, "image should be equal")
        self.assertTrue(self.areImagesEqual(workingSensation.getImage(), image), "image  areImagesEqual should be equal") # should test this thios special method
                
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
        
        # NOTE, at this point we should change original sensations id, because other way
        # creations thinks, that we are updating original sensation with new data
        workingSensation.setId(Sensation.getNextId())
        workingSensation.setDataId(workingSensation.getId())
        
        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertNotEqual(fromBytesWorkingSensation, workingSensation, "should not be equal, because we changed manully original id")
        self.assertEqual(fromBytesWorkingSensation.getMainNames(), workingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_2_LOCATIONS, "should be equal")
        self.assertNotEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should not be equal, because we changed manually original id")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")
        
        workingSensation.setLocations(locations = SensationTestCase.SET_1_1_LOCATIONS_1)
        self.assertTrue(workingSensation != None, "should be created")
        self.assertEqual(workingSensation.getLocations(), SensationTestCase.SET_1_1_LOCATIONS_1, "should be equal")
        bytes=workingSensation.bytes()
        self.assertTrue(bytes != None, "should be get bytes")
    
        # NOTE, at this point we should change original sensations id, because other way
        # creations thinks, that we are updating original sensation with new data
        workingSensation.setId(Sensation.getNextId())
        workingSensation.setDataId(workingSensation.getId())

        fromBytesWorkingSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(fromBytesWorkingSensation != None, "should be created")
        self.assertNotEqual(fromBytesWorkingSensation, workingSensation, "should not be equal, because we changed manually original id")
        self.assertEqual(SensationTestCase.MAINNAMES_1, fromBytesWorkingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getMainNames(), workingSensation.getMainNames(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), workingSensation.getLocations(), "should be equal")
        self.assertEqual(fromBytesWorkingSensation.getLocations(), SensationTestCase.SET_1_1_LOCATIONS_1, "should be equal")
        self.assertNotEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should not be equal, because we changed manually original id")
        self.assertTrue(workingSensation.isOriginal(), "workingSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesWorkingSensation should be original")
        
        # test Item.image
        self.assertTrue(self.areImagesEqual(workingSensation.getImage(), image), "areImagesEqual should be equal" ) # should test this this special method

        self.assertIsNotNone(fromBytesWorkingSensation.getImage(), "should get image")
        fromBytesImage = fromBytesWorkingSensation.getImage() # this is now JPegImageFile, image is PIL.image, so we can't compare them
        self.assertFalse(self.areImagesEqual(fromBytesWorkingSensation.getImage(), image), "should not be equal, because Image format differs") # should test this thios special method
        self.assertFalse(fromBytesWorkingSensation.getImage() == image, "should not be equal, because Image format differs")
        self.assertTrue(self.areImagesEqual(workingSensation.getImage(), image), "should be equal") # should test this thios special method
        self.assertTrue(workingSensation.getImage() == image, "should be equal")
        self.assertFalse(workingSensation.getImage() == fromBytesWorkingSensation.getImage(), "should not be equal, because Image format differs")
        self.assertNotEqual(fromBytesWorkingSensation.getDataId(), workingSensation.getDataId(), "should be not equal, because we have changed original id")
        self.assertTrue(workingSensation.isOriginal(), "imageSensation should be original")
        self.assertTrue(fromBytesWorkingSensation.isOriginal(), "fromBytesImageSensation should be original")
        
        
        # Working_Importance_test
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
        # TODO maybe voice-test is not reasonable, because  we don't update from bytes, but get new voices, look image below
        
        #data=b'\x01\x02'
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
        
        imageSensation = self.robot.createSensation(associations=None, sensationType=Sensation.SensationType.Image, memoryType=Sensation.MemoryType.Sensory, image=image, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)
        # test test
        self.assertTrue(imageSensation.getImage() == image, "should be equal 1")
        self.assertTrue(self.areImagesEqual(imageSensation.getImage(), image), "areImagesEqual should be equal 1") # should test this thios special method

        self.assertFalse(imageSensation.isForgettable(), "should be False, until detached")
        imageSensation.detach(robot=self.robot)
        self.assertTrue(imageSensation.getImage() == image, "should be equal 2")
        self.assertTrue(self.areImagesEqual(imageSensation.getImage(), image), "areImagesEqual should be equal 2") # should test this thios special method
        self.assertTrue(imageSensation.isForgettable(), "should be True after detach")

        bytes=imageSensation.bytes() # Note, this changes Sensation.image, even if iamage itself is same inside Sensation.image
        self.assertTrue(imageSensation.getImage() == image, "== should be equal 3")
        self.assertTrue(self.areImagesEqual(imageSensation.getImage(), image), "areImagesEqual should be equal 3") # should test this this special method
        self.assertTrue(bytes != None, "should be get bytes")
        
        # NOTE, at this point we should change original sensations id, because other way
        # creations thinks, that we are updating original sensation with new data
        imageSensation.setId(Sensation.getNextId())
        imageSensation.setDataId(imageSensation.getId())
        
        fromBytesImageSensation = self.robot.createSensation(bytes=bytes)
        self.assertTrue(self.areImagesEqual(imageSensation.getImage(), image), "areImagesEqual should be equal 4") # should test this this special method

        fromBytesImage = fromBytesImageSensation.getImage() # this is now JPegImageFile, image is PIL.image, so we can't compare them
        self.assertFalse(imageSensation == fromBytesImageSensation, "should be equal, because we have changed id manually")
        self.assertFalse(self.areImagesEqual(fromBytesImageSensation.getImage(), image), "should not be equal 4, because Image format differs") # should test this thios special method
        self.assertFalse(fromBytesImageSensation.getImage() == image, "should be equal 4, because Image format differs")
        self.assertTrue(self.areImagesEqual(imageSensation.getImage(), image), "should be equal 5") # should test this thios special method
        self.assertTrue(imageSensation.getImage() == image, "should be equal 5")
        self.assertFalse(imageSensation.getImage() == fromBytesImageSensation.getImage(), "should not be equal, because Image format differs")
        self.assertTrue(imageSensation.getLocations() == fromBytesImageSensation.getLocations(), "should be equal")
        self.assertNotEqual(fromBytesImageSensation.getDataId(), imageSensation.getDataId(), "should be not equal, because we have changed original id")
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
        self.assertEqual(fromWorkingSensation.getDataId(), workingSensation.getId(), "should be equal")
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
        # test that Sensation.data is same instance
        self.assertEqual(voiceSensation.data, fromVoiceSensation.data)
        self.assertTrue(voiceSensation.data is fromVoiceSensation.data)
       
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
        # test that SEnsation.data is same instance
        #self.assertEqual(voiceSensation.image, fromVoiceSensation.image)
        self.assertTrue(voiceSensation.image is fromVoiceSensation.image)
        
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
        voiceSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Voice, robotType=Sensation.RobotType.Sense)
        self.assertEqual(voiceSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Sense, 'isCommunication same mainNames RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Muscle, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Muscle')
        
        voiceSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Voice, robotType=Sensation.RobotType.Muscle)
        self.assertEqual(voiceSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Muscle, 'isCommunication  same mainNames RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(voiceSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Sense, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Sense')
        
        voiceSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Voice, robotType=Sensation.RobotType.Communication)
        self.assertEqual(voiceSensation.getRobotType(), Sensation.RobotType.Communication, 'plain RobotType should be Sensation.RobotType.Communication')

        #Image
        imageSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Image, robotType=Sensation.RobotType.Sense)
        self.assertEqual(imageSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Sense, 'isCommunication  same mainNames RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Muscle, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Muscle')
        
        imageSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Image, robotType=Sensation.RobotType.Muscle)
        self.assertEqual(imageSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Muscle, 'isCommunication same mainNames RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(imageSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Sense, 'isCommunication other mainNames RobotType should be Sensation.RobotType.Sense')
        imageSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Image, robotType=Sensation.RobotType.Communication)
        self.assertEqual(imageSensation.getRobotType(), Sensation.RobotType.Communication, 'plain RobotType should be Sensation.RobotType.Communication')

        #Item
        itemSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Item, robotType=Sensation.RobotType.Sense)
        self.assertEqual(itemSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Sense, 'same mainNames RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Sense, 'other mainNames RobotType should be Sensation.RobotType.Sense')
        
        itemSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Item, robotType=Sensation.RobotType.Muscle)
        self.assertEqual(itemSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Muscle, 'same mainNames RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(itemSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Muscle, 'other mainNames RobotType should be Sensation.RobotType.Muscle')
        itemSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Item, robotType=Sensation.RobotType.Communication)
        self.assertEqual(itemSensation.getRobotType(), Sensation.RobotType.Communication, 'plain RobotType should be Sensation.RobotType.Communication')

        #Feeling
        feelingSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Feeling, robotType=Sensation.RobotType.Sense)
        self.assertEqual(feelingSensation.getRobotType(), Sensation.RobotType.Sense, 'plain RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Sense, 'same mainNames RobotType should be Sensation.RobotType.Sense')
#         self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Sense, 'other mainNames RobotType should be Sensation.RobotType.Sense')
        
        feelingSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Feeling, robotType=Sensation.RobotType.Muscle)
        self.assertEqual(feelingSensation.getRobotType(), Sensation.RobotType.Muscle, 'plain RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_1), 
#                                                      Sensation.RobotType.Muscle, 'same mainNames RobotType should be Sensation.RobotType.Muscle')
#         self.assertEqual(feelingSensation.getRobotType(robotMainNames=SensationTestCase.MAINNAMES_2), 
#                                                      Sensation.RobotType.Muscle, 'other mainNames RobotType should be Sensation.RobotType.Muscle')
        feelingSensation = self.robot.createSensation(sensationType=Sensation.SensationType.Feeling, robotType=Sensation.RobotType.Communication)
        self.assertEqual(feelingSensation.getRobotType(), Sensation.RobotType.Communication, 'plain RobotType should be Sensation.RobotType.Communication')
        
#     '''
#     test_picleability
#     deprecated
#     '''
#         
#     def deprecated_test_Picleability(self):
#         print("\ntest_Picleability\n")
# 
#         print("Basic constructor without Robot")
#         memory = Memory(robot = None,                          # owner robot
#                         maxRss = Memory.maxRss,
#                         minAvailMem = Memory.minAvailMem)
# 
#         sensation = Sensation(memory=memory, robotId=0.0)
#         self.do_Test_Picleability(sensation=sensation)
#         
#         print("Memory constructor")
#         sensation = memory.create(robot=self.robot)
#         sensation.detachAll()        
#         sensation.robot=None
# 
#         self.do_Test_Picleability(sensation=sensation)
#         
# 
#         print("Robot constructor")
#         sensation = self.robot.createSensation()
#         sensation.detachAll()        
#         sensation.robot=None
# 
#         self.do_Test_Picleability(sensation=sensation)
# 
#     
#     '''
#     Picle Sensation same way, than Memory does it.
#     '''        
#     def do_Test_Picleability(self, sensation):
#         
#         print("do_Test_Picleability")
#         sensation.save()
#         
#         # picle
# 
#         # save sensation instances
#         if not os.path.exists(SensationTestCase.DATADIR):
#             os.makedirs(SensationTestCase.DATADIR)
#             
#         try:
#             with open(SensationTestCase.PATH_TO_PICLE_FILE, "wb") as f2:
#                 try:
#                     pickler = pickle.Pickler(f2, -1)
#                     pickler.dump(Sensation.VERSION)
#                     pickler.dump(sensation)
#                 except IOError as e:
#                     self.assertTrue(False,'pickler.dump(sensation) IOError ' + str(e))
#                 except pickle.PickleError as e:
#                     self.assertTrue(False,'pickler.dump(sensation) PickleError ' + str(e))
#                 except pickle.PicklingError as e:
#                     self.assertTrue(False,'pickler.dump(sensation) PicklingError ' + str(e))
# 
#                 finally:
#                     f2.close()
#         except Exception as e:
#                 self.assertTrue(False,"saveLongTermMemory open(fileName, wb) as f2 error " + str(e))
#                 
#         # load
#         if os.path.exists(Sensation.DATADIR):
#             try:
#                 with open(SensationTestCase.PATH_TO_PICLE_FILE, "rb") as f:
#                     try:
#                         version = pickle.load(f)
#                         if version == Sensation.VERSION:
#                             loadedSensation = pickle.load(f)
#                             print('sensation loaded')
#                             self.assertEqual(sensation, loadedSensation, "dumped and loaded Sensation should be equal")
#                         else:
#                             print("Sensation could not be loaded. because Sensation cache version {} does not match current sensation version {}".format(version,Sensation.VERSION))
#                     except IOError as e:
#                         self.assertTrue(False,"pickle.load(f) error " + str(e))
#                     except pickle.PickleError as e:
#                         self.assertTrue(False,'pickle.load(f) PickleError ' + str(e))
#                     except pickle.PicklingError as e:
#                         self.assertTrue(False,'pickle.load(f) PicklingError ' + str(e))
#                     except Exception as e:
#                         self.assertTrue(False,'pickle.load(f) Exception ' + str(e))
#                     finally:
#                         f.close()
#             except Exception as e:
#                     self.assertTrue(False,'with open(' + Sensation.PATH_TO_PICLE_FILE + ',"rb") as f error ' + str(e))
# 
#         print("\ndo_Test_Picleability OK\n")

    '''
    test save and load to binary file
    '''
        
    def test_Save(self):
        print("\ntest_Save\n")

        # test all SensationTypes
        
        for sensationtype in Sensation.SensationTypesOrdered:
            # Stop and Capability will mever be saved to Memory
            if sensationtype != Sensation.SensationType.Stop and\
               sensationtype != Sensation.SensationType.Capability and\
               sensationtype != Sensation.SensationType.Unknown:
                # TODO, if memory tries to delete Sensations
                # test fails so this test is memory amount denpendent
#                 memory = Memory(robot = None,
#                                 maxRss = 10*Memory.maxRss,
#                                 minAvailMem = 0)#Memory.minAvailMem)
                self.do_Test_CopyBinaryFiles(sensationtype = sensationtype,
                                             memory=self.memory)
#         
#         self.do_Test_CopyBinaryFiles(sensationtype = Sensation.SensationType.Voice)
#         self.do_Test_CopyBinaryFiles(sensationtype = Sensation.SensationType.Image)
#         self.do_Test_CopyBinaryFiles(sensationtype = Sensation.SensationType.Item)
        
    '''
    test save and load to binary file
    '''
        
    def do_Test_CopyBinaryFiles(self, sensationtype, memory):
        print("\ndo_Test_CopyBinaryFiles {}\n".format(Sensation.getSensationTypeString(sensationtype)))

        
        data = b'\x01\x02'
        image = PIL_Image.new(size=(2,2), mode='RGB')
        name = "name"
        
        # dont use self.robot.createSensation, because it can delete unused sensations from memory
        # but wse must use pure Sensation creation
        
        if sensationtype == Sensation.SensationType.Voice:
            originalSensation = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       associations=None, sensationType=sensationtype, memoryType=Sensation.MemoryType.Sensory,
                                       data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)
        elif sensationtype == Sensation.SensationType.Image:
            originalSensation = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       associations=None, sensationType=sensationtype, memoryType=Sensation.MemoryType.Sensory,
                                       image=image, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)
        elif sensationtype == Sensation.SensationType.Item:
            originalSensation = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       associations=None, sensationType=sensationtype, memoryType=Sensation.MemoryType.Sensory,
                                       name=name, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)
        else:
             originalSensation = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       associations=None, sensationType=sensationtype, memoryType=Sensation.MemoryType.Sensory,
                                       locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)

        memory.addToSensationMemory(originalSensation, isForgetLessImportantSensations = False)
        self.assertTrue(originalSensation in memory.sensationMemory)
        
        # copy 1
        copySensation1 = Sensation(memory=memory,
                                   robotId=self.robot.getId(),
                                   sensation=originalSensation)
        memory.addToSensationMemory(copySensation1, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation1 in memory.sensationMemory)
        # originalSensation knows its copies
        self.assertTrue(copySensation1 in originalSensation.copySensations)

        # test test        
        self.assertNotEqual(originalSensation, copySensation1, "should not be equal")
        self.assertEqual(originalSensation.getKind(), copySensation1.getKind(), "should be equal")
        self.assertEqual(originalSensation.getData(), copySensation1.getData(), "should be equal")
        # TODO Enable this, locations should be equal
        self.assertEqual(originalSensation.getLocations(), copySensation1.getLocations(), "should be equal")
        self.assertEqual(copySensation1.getDataId(), originalSensation.getDataId(), "should be equal")
        self.assertTrue(originalSensation.isOriginal(), "originalSensation should be original")
        self.assertFalse(copySensation1.isOriginal(), "copySensation1 should be copy")
        # test that Sensation.data is same instance
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(originalSensation.data, copySensation1.data)
            self.assertTrue(originalSensation.data is copySensation1.data)
        elif sensationtype == Sensation.SensationType.Image:
            self.assertEqual(originalSensation.image, copySensation1.image)
            self.assertTrue(originalSensation.image is copySensation1.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(originalSensation.name, copySensation1.name)
            self.assertTrue(originalSensation.name is copySensation1.name)
               
        # copy 2
        copySensation2 = Sensation(memory=memory,
                                   robotId=self.robot.getId(),
                                   sensation=originalSensation)
        memory.addToSensationMemory(copySensation2, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation2 in memory.sensationMemory)
        # originalSensation knows its copies
        self.assertTrue(copySensation2 in originalSensation.copySensations)

        # test test        
        self.assertNotEqual(originalSensation, copySensation2, "should not be equal")
        self.assertEqual(originalSensation.getKind(), copySensation2.getKind(), "should be equal")
        self.assertEqual(originalSensation.getData(), copySensation2.getData(), "should be equal")
        # TODO Enable this, locaion should be equal
        self.assertEqual(originalSensation.getLocations(), copySensation2.getLocations(), "should be equal")
        self.assertEqual(copySensation2.getDataId(), originalSensation.getDataId(), "should be equal")
        self.assertTrue(originalSensation.isOriginal(), "originalSensation should be original")
        self.assertFalse(copySensation2.isOriginal(), "copySensation2 should be copy")
        # test that Sensation.data is same instance
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(originalSensation.data, copySensation2.data)
            self.assertTrue(originalSensation.data is copySensation2.data)
        elif sensationtype == Sensation.SensationType.Image:
            self.assertEqual(originalSensation.image, copySensation2.image)
            self.assertTrue(originalSensation.image is copySensation2.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(originalSensation.name, copySensation2.name)
            self.assertTrue(originalSensation.name is copySensation2.name)
        
        # save
        originalSensation.save()
        originalSensationBinaryFilePath = originalSensation.getFilePath(sensationType = Sensation.SensationType.All)
        # delete deletes also bin files, so we must save binary files.
        originalSensationBinaryFilePathBak = originalSensationBinaryFilePath+'.bak'
        shutil.copyfile(src=originalSensationBinaryFilePath, dst=originalSensationBinaryFilePathBak)
        originalSensationId = originalSensation.getId()
        
        copySensation1.save()
        copySensation1BinaryFilePath = copySensation1.getFilePath(sensationType = Sensation.SensationType.All)
        copySensation1BinaryFilePathBak = copySensation1BinaryFilePath+'.bak'
        # delete deletes also bin files, so we must save binary files.
        shutil.copyfile(src=copySensation1BinaryFilePath, dst=copySensation1BinaryFilePathBak)
        copySensation1Id = copySensation1.getId()
        
        copySensation2.save()
        copySensation2BinaryFilePath = copySensation2.getFilePath(sensationType = Sensation.SensationType.All)
        copySensation2BinaryFilePathBak = copySensation2BinaryFilePath+'.bak'
        # delete deletes also bin files, so we must save binary files.
        shutil.copyfile(src=copySensation2BinaryFilePath, dst=copySensation2BinaryFilePathBak)
        copySensation2Id = copySensation2.getId()
        
        # now delete originalSensation and copySensation1 from memory
        # reverse order
        
        # copySensation2 is copy
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation2.originalSensation is originalSensation)
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 2)

        copySensation2.delete()
        # copySensation2 is not copy any more copy
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertFalse(copySensation2.originalSensation is originalSensation)
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 1)

        # copySensation1 is still copy
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertTrue(copySensation1.originalSensation is originalSensation)
        self.assertTrue(copySensation1 in originalSensation.copySensations)

        copySensation1.delete()
        # copySensation1 is not copy any more copy
        self.assertFalse(copySensation1 in originalSensation.copySensations)
        self.assertFalse(copySensation1.originalSensation is originalSensation)
        self.assertFalse(copySensation1 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 0)
        
        originalSensation.delete() # does nothing for copysensations, necause it does not ave them
        self.assertEqual(len(originalSensation.copySensations), 0)

        # do physical delete from memory        
        i=0
        while i < len(memory.sensationMemory) and (originalSensation != None or\
              copySensation1 != None or copySensation2 != None):
            if originalSensation != None and\
               memory.sensationMemory[i].getId() == originalSensation.getId():
                del memory.sensationMemory[i]
                originalSensation = None
            elif copySensation1 != None and\
                 memory.sensationMemory[i].getId() == copySensation1.getId():
                del memory.sensationMemory[i]
                copySensation1 = None
            elif copySensation2 != None and\
                 memory.sensationMemory[i].getId() == copySensation2.getId():
                del memory.sensationMemory[i]
                copySensation2 = None
            else:
                i += 1
            
        #test test
        self.assertEqual(originalSensation, None)
        self.assertEqual(copySensation1, None)
        self.assertEqual(copySensation2, None)
        
        # now create deleted Sensation fron files and test that there is only
        # one copy of data
        # original
        originalSensation = Sensation(memory=memory,
                                   robotId=self.robot.getId(),
                                   binaryFilePath=originalSensationBinaryFilePathBak)
        self.assertEqual(originalSensationId, originalSensation.getId())
        # this does not yet add Sensation to Memory
        memory.addToSensationMemory(originalSensation, isForgetLessImportantSensations = False)
        self.assertTrue(originalSensation in memory.sensationMemory)
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(originalSensation.data, data)
            #self.assertFalse(originalSensation.data is data)
# image is not same, tham char arraays
        elif sensationtype == Sensation.SensationType.Image:
            pass # we can't test equality og PIL image like this
            #self.assertEqual(originalSensation.image, image)
            #self.assertFalse(originalSensation.image is image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(originalSensation.name, name)
            #self.assertFalse(originalSensation.name is name)
        
        #copy 1
        copySensation1 = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       binaryFilePath=copySensation1BinaryFilePathBak)
        self.assertEqual(copySensation1Id, copySensation1.getId())
        memory.addToSensationMemory(copySensation1, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation1 in memory.sensationMemory)
        
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(copySensation1.data, data)
            #self.assertFalse(copySensation1.data is data)
# image is not same, tham char arraays
        elif sensationtype == Sensation.SensationType.Image:
            pass # We can't test eqiality like this
            #self.assertEqual(originalSensation.image, image)
            #self.assertFalse(originalSensation.image is image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(copySensation1.name, name)
            #self.assertFalse(copySensation1.name is name)


        
        # copy data should be referenge to original
        if sensationtype == Sensation.SensationType.Voice:
            self.assertTrue(originalSensation.data is copySensation1.data)
        elif sensationtype == Sensation.SensationType.Image:
            self.assertTrue(originalSensation.image is copySensation1.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertTrue(originalSensation.name is copySensation1.name)

        #copy 2
        copySensation2 = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       binaryFilePath=copySensation2BinaryFilePathBak)
        memory.addToSensationMemory(copySensation2, isForgetLessImportantSensations = False)
        self.assertEqual(copySensation2Id, copySensation2.getId())
        self.assertTrue(copySensation2 in memory.sensationMemory)

        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(copySensation2.data, data)
            #self.assertFalse(copySensation2.data is data)
             # copy data should be referenge to original
            self.assertTrue(originalSensation.data is copySensation2.data)
        elif sensationtype == Sensation.SensationType.Image:
             # copy image should be referenge to original
            self.assertTrue(originalSensation.image is copySensation2.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(copySensation2.name, name)
            #self.assertFalse(copySensation2.name is name)
             # copy name should be referenge to original
            self.assertTrue(originalSensation.name is copySensation2.name)
        
        # now delete originalSensation and copySensation1 from memory
        # reverse order
        
        # copySensation2 is copy
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation2.originalSensation is originalSensation)
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 2)

        copySensation2.delete()
        # copySensation2 is not copy any more copy
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertFalse(copySensation2.originalSensation is originalSensation)
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 1)

        # copySensation1 is still copy
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertTrue(copySensation1.originalSensation is originalSensation)
        self.assertTrue(copySensation1 in originalSensation.copySensations)

        copySensation1.delete()
        # copySensation1 is not copy any more copy
        self.assertFalse(copySensation1 in originalSensation.copySensations)
        self.assertFalse(copySensation1.originalSensation is originalSensation)
        self.assertFalse(copySensation1 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 0)
        
        originalSensation.delete() # does nothing for copysensations, necause it does not ave them
        self.assertEqual(len(originalSensation.copySensations), 0)

        i=0
        while i < len(memory.sensationMemory) and\
             (originalSensation != None or copySensation1 != None or copySensation2 != None):
            if originalSensation != None and\
               memory.sensationMemory[i].getId() == originalSensation.getId():
                del memory.sensationMemory[i]
                originalSensation = None
            elif copySensation1 != None and\
                 memory.sensationMemory[i].getId() == copySensation1.getId():
                del memory.sensationMemory[i]
                copySensation1 = None
            elif copySensation2 != None and\
                 memory.sensationMemory[i].getId() == copySensation2.getId():
                del memory.sensationMemory[i]
                copySensation2 = None
            else:
                i += 1
            
        #test test
        self.assertEqual(originalSensation, None)
        self.assertEqual(copySensation1, None)
        self.assertEqual(copySensation2, None)
        
        # load copy first copySensation1, then copySensation2 and finally original
        #copy 1
        copySensation1 = Sensation(memory=memory,
                                        robotId=self.robot.getId(),
                                        binaryFilePath=copySensation1BinaryFilePathBak)
        self.assertEqual(copySensation1Id, copySensation1.getId())

        memory.addToSensationMemory(copySensation1, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation1 in memory.sensationMemory)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation1.getId()),
                         copySensation1)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation1Id),
                         copySensation1)
        
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(copySensation1.data, data)
            #self.assertFalse(copySensation1.data is data)
        elif sensationtype == Sensation.SensationType.Image:
            pass # We can't test eqiality like this
            #self.assertEqual(copySensation1.image, image)
            #self.assertFalse(copySensation1.image is image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(copySensation1.name, name)
            #self.assertFalse(copySensation1.name is name)
        
       
        # and load copy 2
        copySensation2 = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       binaryFilePath=copySensation2BinaryFilePathBak)
        self.assertEqual(copySensation2Id, copySensation2.getId())
        memory.addToSensationMemory(copySensation2, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation2 in memory.sensationMemory)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation2.getId()),
                         copySensation2)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation2Id),
                         copySensation2)

        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(copySensation2.data, data)
            #self.assertFalse(copySensation2.data is data)
        elif sensationtype == Sensation.SensationType.Image:
            pass # We can't test eqiality like this
            #self.assertEqual(copySensation2.image, image)
            #self.assertFalse(copySensation2.image is image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(copySensation2.name, name)
            #self.assertFalse(copySensation2.name is name)

        # then original
        originalSensation = Sensation(memory=memory,
                                   robotId=self.robot.getId(),
                                   binaryFilePath=originalSensationBinaryFilePathBak)
        self.assertEqual(originalSensationId, originalSensation.getId())
        # this does not yet add Sensation to Memory
        memory.addToSensationMemory(originalSensation, isForgetLessImportantSensations = False)
        self.assertTrue(originalSensation in memory.sensationMemory)
        
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(originalSensation.data, data)
            #self.assertFalse(originalSensation.data is data)
        elif sensationtype == Sensation.SensationType.Image:
            pass # We can't test eqiality like this
            #self.assertEqual(originalSensation.image, image)
            #self.assertFalse(originalSensation.image is image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(originalSensation.name, name)
            #self.assertFalse(originalSensation.name is name)
                        
        self.assertEqual(len(originalSensation.copySensationIds), 0)
        self.assertEqual(len(originalSensation.copySensations), 2)
 
        
        # and now copy2 should have reference to original from its data
        # this fails now, because we don't have Sensation ids of copyes in
        # our original
        if sensationtype == Sensation.SensationType.Voice:
            self.assertTrue(originalSensation.data is copySensation1.data)
            self.assertTrue(originalSensation.data is copySensation2.data)
            self.assertTrue(copySensation1.data is copySensation2.data)
        elif sensationtype == Sensation.SensationType.Image:
            self.assertTrue(originalSensation.image is copySensation1.image)
            self.assertTrue(originalSensation.image is copySensation2.image)
            self.assertTrue(copySensation1.image is copySensation2.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertTrue(originalSensation.name is copySensation1.name)
            self.assertTrue(originalSensation.name is copySensation2.name)
            self.assertTrue(copySensation1.name is copySensation2.name)
                
        ######################################
        # load first copy and then original
        # now delete originalSensation and copySensation1 from memory

        # now delete originalSensation and copySensation1 from memory
        # reverse order
        
        # copySensation2 and copySensation2 is copies
        
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation2.originalSensation is originalSensation)
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertTrue(copySensation1.originalSensation is originalSensation)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 2)
        

        originalSensation.delete()
        # should have new original now
        self.assertEqual(len(originalSensation.copySensations), 0)
        # copySensation1 is new original now
        self.assertTrue(copySensation1.isOriginal())
        self.assertFalse(copySensation2.isOriginal())
        self.assertTrue(copySensation2 in copySensation1.copySensations)
        self.assertTrue(copySensation2.originalSensation is copySensation1)
        self.assertEqual(len(copySensation1.copySensations), 1)
        self.assertEqual(copySensation1.copySensations[0], copySensation2)
        
        copySensation2.delete()
        # copySensation2 is not copy any more copy
        self.assertFalse(copySensation2 in copySensation1.copySensations)
        self.assertFalse(copySensation2.originalSensation is copySensation1)
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertEqual(len(copySensation1.copySensations), 0)
        self.assertTrue(copySensation1.isOriginal())
        
        copySensation1.delete() # does nothing for copysensations, necause it does not ave them
        self.assertEqual(len(copySensation1.copySensations), 0)
        
        i=0
        while i < len(memory.sensationMemory) and (originalSensation != None or\
              copySensation1 != None or copySensation2 != None):
            if originalSensation != None and\
               memory.sensationMemory[i].getId() == originalSensation.getId():
                del memory.sensationMemory[i]
                originalSensation = None
            elif copySensation1 != None and\
                 memory.sensationMemory[i].getId() == copySensation1.getId():
                del memory.sensationMemory[i]
                copySensation1 = None
            elif copySensation2 != None and\
                 memory.sensationMemory[i].getId() == copySensation2.getId():
                del memory.sensationMemory[i]
                copySensation2 = None
            else:
                i += 1
            
        #test test
        self.assertEqual(originalSensation, None)
        self.assertEqual(copySensation1, None)
        self.assertEqual(copySensation2, None)
        
        #################################
        
        # load copy first copySensation1, then original  and finally copySensation2        
        
        #copy 1
        copySensation1 = Sensation(memory=memory,
                                        robotId=self.robot.getId(),
                                        binaryFilePath=copySensation1BinaryFilePathBak)
        self.assertEqual(copySensation1Id, copySensation1.getId())

        memory.addToSensationMemory(copySensation1, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation1 in memory.sensationMemory)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation1.getId()),
                         copySensation1)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation1Id),
                         copySensation1)

        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(copySensation1.data, data)
            #self.assertFalse(copySensation1.data is data)
        elif sensationtype == Sensation.SensationType.Image:
            pass # We can't test eqiality like this
            #self.assertEqual(copySensation1.image, image)
            #self.assertFalse(copySensation1.image is image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(copySensation1.name, name)
            #self.assertFalse(copySensation1.name is name)

        
        # then original
        originalSensation = Sensation(memory=memory,
                                   robotId=self.robot.getId(),
                                   binaryFilePath=originalSensationBinaryFilePathBak)
        self.assertEqual(originalSensationId, originalSensation.getId())
        # this does not yet add Sensation to Memory
        memory.addToSensationMemory(originalSensation, isForgetLessImportantSensations = False)
        self.assertTrue(originalSensation in memory.sensationMemory)
        
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(originalSensation.data, data)
            #self.assertFalse(originalSensation.data is data)
            self.assertTrue(copySensation1.data is originalSensation.data)
        elif sensationtype == Sensation.SensationType.Image:
            # We can't test eqiality like this
            #self.assertEqual(originalSensation.image, image)
            #self.assertFalse(originalSensation.image is image)
            self.assertTrue(copySensation1.image is originalSensation.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(originalSensation.name, name)
            #self.assertFalse(originalSensation.name is name)
            self.assertTrue(copySensation1.name is originalSensation.name)
                                
        self.assertEqual(len(originalSensation.copySensationIds), 1)
        self.assertEqual(len(originalSensation.copySensations), 1)
        
        
        # and load copy 2
        copySensation2 = Sensation(memory=memory,
                                       robotId=self.robot.getId(),
                                       binaryFilePath=copySensation2BinaryFilePathBak)
        self.assertEqual(copySensation2Id, copySensation2.getId())
        memory.addToSensationMemory(copySensation2, isForgetLessImportantSensations = False)
        self.assertTrue(copySensation2 in memory.sensationMemory)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation2.getId()),
                         copySensation2)
        self.assertEqual(memory.getSensationFromSensationMemory(id=copySensation2Id),
                         copySensation2)
        
        
        if sensationtype == Sensation.SensationType.Voice:
            self.assertEqual(copySensation2.data, data)
            #self.assertFalse(copySensation2.data is data)
            self.assertTrue(copySensation2.data is originalSensation.data)
            self.assertTrue(copySensation2.originalSensation is originalSensation)
            # also copySensation1 remain
            self.assertEqual(copySensation1.data, data)
            #self.assertFalse(copySensation1.data is data)
            self.assertTrue(copySensation1.data is originalSensation.data)
        elif sensationtype == Sensation.SensationType.Image:
            #self.assertEqual(copySensation2.image, image)
            #self.assertFalse(copySensation2.image is image)
            self.assertTrue(copySensation2.image is originalSensation.image)
            self.assertTrue(copySensation2.originalSensation is originalSensation)
            # also copySensation1 remain
            # We can't test eqiality like this
            #self.assertEqual(copySensation1.image, image)
            #self.assertFalse(copySensation1.image is image)
            self.assertTrue(copySensation1.image is originalSensation.image)
        elif sensationtype == Sensation.SensationType.Item:
            self.assertEqual(copySensation2.name, name)
            #self.assertFalse(copySensation2.name is name)
            self.assertTrue(copySensation2.name is originalSensation.name)
            self.assertTrue(copySensation2.originalSensation is originalSensation)
            # also copySensation1 remain1
            self.assertEqual(copySensation1.name, name)
            #self.assertFalse(copySensation1.name is name)
            self.assertTrue(copySensation1.name is originalSensation.name)
                        
        self.assertEqual(len(originalSensation.copySensations), 2)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensationIds), 0)
 

        # now delete originalSensation and copySensation1 from memory
        # reverse order
        
        # copySensation2 and copySensation2 is copies
        
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation2.originalSensation is originalSensation)
        self.assertTrue(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertTrue(copySensation1.originalSensation is originalSensation)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 2)
        
        copySensation2.delete()
        # originalSensation losesis its copy
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertFalse(copySensation2.originalSensation is originalSensation)
        self.assertFalse(copySensation2 in originalSensation.copySensations)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertTrue(copySensation1.originalSensation is originalSensation)
        self.assertTrue(copySensation1 in originalSensation.copySensations)
        self.assertEqual(len(originalSensation.copySensations), 1)
        self.assertTrue(originalSensation.isOriginal())
        self.assertFalse(copySensation1.isOriginal())
        
        originalSensation.delete()
        #copySensation1 loses its original
        self.assertEqual(len(originalSensation.copySensations), 0)
        # copySensation1 is new original now
        self.assertTrue(copySensation1.isOriginal())
        self.assertEqual(len(copySensation1.copySensations), 0)
        
        
        copySensation1.delete() # does nothing for copysensations, necause it does not ave them
        self.assertEqual(len(copySensation1.copySensations), 0)
         
        # finally delete originalSensation and copySensation1 from memory
        i=0
        while i < len(memory.sensationMemory) and\
             (originalSensation != None or copySensation1 != None or copySensation2 != None):
            if originalSensation != None and\
               memory.sensationMemory[i].getId() == originalSensation.getId():
                del memory.sensationMemory[i]
                originalSensation = None
            elif copySensation1 != None and\
                 memory.sensationMemory[i].getId() == copySensation1.getId():
                del memory.sensationMemory[i]
                copySensation1 = None
            elif copySensation2 != None and\
                 memory.sensationMemory[i].getId() == copySensation2.getId():
                del memory.sensationMemory[i]
                copySensation2 = None
            else:
                i += 1
            
        #test test
        self.assertEqual(originalSensation, None)
        self.assertEqual(copySensation1, None)
        self.assertEqual(copySensation2, None)
        
        # cleanup memory
        del memory.sensationMemory[:]


    '''
    test save and load to binary file
    '''
        
    def if_needed_testSaveCopyBinaryFile(self):
        print("\ntest_Save\n")

        
        print("Basic constructor without Robot")
        memory = Memory(robot = None,                          # owner robot
                        maxRss = Memory.maxRss,
                        minAvailMem = Memory.minAvailMem)

        sensation = Sensation(memory=memory, robotId=0.0)
        sensation.save()
        
        binaryFilePath = sensation.getFilePath(sensationType = Sensation.SensationType.All)

        self.assertTrue(os.path.exists(binaryFilePath), "Binary file {} should exist".format(binaryFilePath))
        loadedSensation = Sensation(memory=memory,
                                    robotId=0.0,
                                    binaryFilePath=binaryFilePath)
        self.assertEqual(sensation, loadedSensation, "Loaded sensation should be equal to original one")
        
        # test image and Voice
        # Voice
        # TODO pure constructor of Sensation can't be used
        # bacause it does not inset sensations to memory even if it has that parameter.
        
        data=b'\x01\x02'
        voiceSensation = Sensation(memory=memory, robotId=0.0,
                                   associations=None, sensationType=Sensation.SensationType.Voice, memoryType=Sensation.MemoryType.Sensory, data=data, locations=SensationTestCase.SET_1_1_LOCATIONS_2, kind=Sensation.Kind.Eva)
        self.assertTrue(voiceSensation in memory.sensationMemory)
        fromVoiceSensation = Sensation(memory=memory, robotId=0.0,
                                       sensation=voiceSensation)
        self.assertTrue(fromVoiceSensation in memory.sensationMemory)

        # test test        
        self.assertNotEqual(voiceSensation, fromVoiceSensation, "should not be equal")
        self.assertEqual(voiceSensation.getKind(), fromVoiceSensation.getKind(), "should be equal")
        self.assertEqual(voiceSensation.getData(), fromVoiceSensation.getData(), "should be equal")
        # TODO Enable this, locaion should be equal
        #self.assertEqual(voiceSensation.getLocations(), fromVoiceSensation.getLocations(), "should be equal")
        self.assertEqual(fromVoiceSensation.getDataId(), voiceSensation.getDataId(), "should be equal")
        self.assertTrue(voiceSensation.isOriginal(), "voiceSensation should be original")
        self.assertFalse(fromVoiceSensation.isOriginal(), "fromVoiceSensation should be copy")
        # test that Sensation.data is same instance
        self.assertEqual(voiceSensation.data, fromVoiceSensation.data)
        self.assertTrue(voiceSensation.data is fromVoiceSensation.data)
       
        
        # save
        voiceSensation.save()
        voiceSensationBinaryFilePath = voiceSensation.getFilePath(sensationType = Sensation.SensationType.All)
        
        fromVoiceSensation.save()
        fromVoiceSensationBinaryFilePath = fromVoiceSensation.getFilePath(sensationType = Sensation.SensationType.All)
        
        # now delete voiceSensation and fromVoiceSensation from memory
        i=0
        while i < len(memory.sensationMemory) and (voiceSensation != None or\
              fromVoiceSensation != None):
            if memory.sensationMemory[i].getId() == voiceSensation.getId():
                del memory.sensationMemory[i]
                voiceSensation = None
            elif memory.sensationMemory[i].getId() == fromVoiceSensation.getId():
                del memory.sensationMemory[i]
                fromVoiceSensation = None
            else:
                i += 1
            
        #test test
        self.assertEqual(voiceSensation, None)
        self.assertEqual(fromVoiceSensation, None)
        
        # now create deleted Sensation fron files and test that there is only
        # one copy of data
        # original
        voiceSensation = Sensation(memory=memory,
                                    robotId=0.0,
                                    binaryFilePath=voiceSensationBinaryFilePath)
        self.assertEqual(voiceSensation.data, data)
        self.assertFalse(voiceSensation.data is data)
        
        #copy
        fromVoiceSensation = Sensation(memory=memory,
                                       robotId=0.0,
                                       binaryFilePath=fromVoiceSensationBinaryFilePath)
        self.assertEqual(fromVoiceSensation.data, data)
        self.assertFalse(fromVoiceSensation.data is data)
        
        # copy data should be rerenge to original
        self.assertFalse(voiceSensation.data is fromVoiceSensation.data)
        
        # load first copy and then original
       

        
if __name__ == '__main__':
    unittest.main()

 