'''
Created on 21.06.2019
Updated on 21.06.2019
@author: reijo.korhonen@gmail.com

test Connection class
python3 -m unittest tests/testConnection.py


'''

import unittest
from Sensation import Sensation
from Connection.Connection import Connection

class ConnectionTestCase(unittest.TestCase):
#    ''' create situation, where we have found
#        - Wall_E_item
#        - Image
#        - voice
#    '''
    def setUp(self):
        self.Wall_E_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Wall-E')
        self.Wall_E_image_sensation = Sensation.create(sensationType=Sensation.SensationType.Image)
        self.Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice)

    def tearDown(self):
        self.Wall_E_item_sensation.delete()
        self.Wall_E_image_sensation.delete()
        self.Wall_E_voice_sensation.delete()
        
    def test_SensationCreate(self):
        self.assertIsNot(self.Wall_E_item_sensation, None)
        
    def test_AddConnection(self):
        addSensation = Sensation.create(sensation=self.Wall_E_item_sensation, memory=Sensation.Memory.LongTerm, name='connect_test')
        self.assertIsNot(addSensation, None)
        addSensation.save()    # this is worth to save its data
        self.assertIs(len(addSensation.getConnections()), 0)
        
        connection_number = len(self.Wall_E_item_sensation.getConnections())

        self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=addSensation,
                                                          score=addSensation.getScore()))
        self.assertIs(len(self.Wall_E_item_sensation.getConnections()), connection_number+1)
        self.assertIs(len(addSensation.getConnections()), 1)
        Sensation.logConnections(self.Wall_E_item_sensation)
        # again, should not add connection twise
        self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=addSensation,
                                                          score=addSensation.getScore()))
        self.assertIs(len(self.Wall_E_item_sensation.getConnections()), connection_number+1)
        self.assertIs(len(addSensation.getConnections()), 1)
        Sensation.logConnections(self.Wall_E_item_sensation)



        
if __name__ == '__main__':
    unittest.main()

 