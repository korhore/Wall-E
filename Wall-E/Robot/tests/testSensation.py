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
        self.sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='test')

    def tearDown(self):
        self.sensation.delete()
        
    def test_SensationCreate(self):
        self.assertIsNot(self.sensation, None)
        
    def test_AddConnection(self):
        addSensation = Sensation.create(sensation=self.sensation, memory=Sensation.Memory.LongTerm, name='connect_test')
        self.assertIsNot(addSensation, None)
        addSensation.save()    # this is worth to save its data
        self.assertIs(len(addSensation.getConnections()), 0)
        
        connection_number = len(self.sensation.getConnections())

        self.sensation.addConnection(Sensation.Connection(sensation=addSensation,
                                                          score=addSensation.getScore()))
        self.assertIs(len(self.sensation.getConnections()), connection_number+1)
        self.assertIs(len(addSensation.getConnections()), 1)
        Sensation.logConnections(self.sensation)
        # again, should not add connection twise
        self.sensation.addConnection(Sensation.Connection(sensation=addSensation,
                                                          score=addSensation.getScore()))
        self.assertIs(len(self.sensation.getConnections()), connection_number+1)
        self.assertIs(len(addSensation.getConnections()), 1)
        Sensation.logConnections(self.sensation)



        
if __name__ == '__main__':
    unittest.main()

 