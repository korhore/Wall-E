'''
Created on 10.06.2019
Updated on 09.07.2019
@author: reijo.korhonen@gmail.com

test Sensation class
python3 -m unittest tests/testSensation.py


'''

import unittest
from Sensation import Sensation

class SensationTestCase(unittest.TestCase):
    SCORE=0.5
    SCORE2=0.8
    
    FEELING = Sensation.Association.Feeling.Good
    BETTER_FEELING = Sensation.Association.Feeling.Happy
    FEELING2 = Sensation.Association.Feeling.Terrified

    def setUp(self):
        self.sensation = Sensation.create(associations=None, sensationType=Sensation.SensationType.Item, name='test')
        self.assertIsNot(self.sensation, None)
        self.assertIs(len(self.sensation.getAssociations()), 0)
        #print('\nlogAssociations 1: setUp')
        Sensation.logAssociations(self.sensation)
        
        self.feeling = SensationTestCase.FEELING

    def tearDown(self):
        self.sensation.delete()
        
    def test_AddAssociations(self):
        for i in range(100):
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
                                                            feeling=SensationTestCase.FEELING2))
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

 