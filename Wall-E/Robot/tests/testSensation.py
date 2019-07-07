'''
Created on 10.06.2019
Updated on 10.06.2019
@author: reijo.korhonen@gmail.com

test Sensation class
python3 -m unittest tests/testSensation.py


'''

import unittest
from Sensation import Sensation

class SensationTestCase(unittest.TestCase):
    def setUp(self):
        self.sensation = Sensation.create(associations=[], sensationType=Sensation.SensationType.Item, name='test')

    def tearDown(self):
        self.sensation.delete()
        
    def test_SensationCreate(self):
        self.assertIsNot(self.sensation, None)
        
    def test_AddAssociation(self):
        addSensation = Sensation.create(associations=[], sensation=self.sensation, memory=Sensation.Memory.LongTerm, name='connect_test')
        self.assertIsNot(addSensation, None)
        addSensation.save()    # this is worth to save its data
        self.assertIs(len(addSensation.getAssociations()), 0)
        
        association_number = len(self.sensation.getAssociations())

        self.sensation.addAssociation(Sensation.Association(sensation=addSensation,
                                                          score=addSensation.getScore()))
        self.assertIs(len(self.sensation.getAssociations()), association_number+1)
        self.assertIs(len(addSensation.getAssociations()), 1)
        Sensation.logAssociations(self.sensation)
        # again, should not add association twise
        self.sensation.addAssociation(Sensation.Association(sensation=addSensation,
                                                          score=addSensation.getScore()))
        self.assertIs(len(self.sensation.getAssociations()), association_number+1)
        self.assertIs(len(addSensation.getAssociations()), 1)
        Sensation.logAssociations(self.sensation)



        
if __name__ == '__main__':
    unittest.main()

 