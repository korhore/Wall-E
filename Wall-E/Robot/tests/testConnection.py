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

from PIL import Image as PIL_Image

class ConnectionTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    SCORE=0.8
    
    def setUp(self):
#         self.Wall_E_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Wall-E')
#         self.Wall_E_image_sensation = Sensation.create(sensationType=Sensation.SensationType.Image)
#         self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=self.Wall_E_image_sensation,
#                                                                       score=ConnectionTestCase.SCORE))
        
        self.connection = Connection(parent=self,
                                     instanceName='Connection',
                                     instanceType= Sensation.InstanceType.SubInstance,
                                     level=2)


    def tearDown(self):
#         self.Wall_E_item_sensation.delete()
#         self.Wall_E_image_sensation.delete()
        
        del self.connection
        
#     def test_SensationCreate(self):
#         self.assertIsNot(self.Wall_E_item_sensation, None)
#         self.assertIsNot(self.Wall_E_image_sensation, None)
       
    def test_ProcessItem(self):
        # First voice
        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice, connections=[])
#        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice)
        print("1 len(Wall_E_voice_sensation.getConnections()) " + str(len(Wall_E_voice_sensation.getConnections())))
              
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 0)
        # process situation, where voice is happened same time than Item
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_sensation)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 0)
        
#         #then image and Item
#         Wall_E_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Wall-E')
        Wall_E_image_sensation = Sensation.create(sensationType=Sensation.SensationType.Image, image=PIL_Image.new(mode='RGB',size=(1,1)), connections=[])
#        Wall_E_image_sensation = Sensation.create(sensationType=Sensation.SensationType.Image, image=PIL_Image.new(mode='RGB',size=(1,1)))
        print("-2 len(Wall_E_voice_sensation.getConnections()) " + str(len(Wall_E_voice_sensation.getConnections())))
        print('-3 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
#         Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=self.Wall_E_image_sensation,
#                                                                       score=ConnectionTestCase.SCORE))
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        print("2 len(Wall_E_voice_sensation.getConnections()) " + str(len(Wall_E_voice_sensation.getConnections())))
        for connection in Wall_E_voice_sensation.getConnections():
            print (Wall_E_voice_sensation.toDebugStr() + ' is connected to ' + connection.getSensation().toDebugStr())
        print('3 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        for connection in Wall_E_voice_sensation.getConnections():
            print (Wall_E_voice_sensation.toDebugStr() + ' is connected to ' + connection.getSensation().toDebugStr())
        # item is not connected to Image, because we don,t have Item yet/connected together
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 1)
        
#         self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
#         # Voice and Image are Connected
#         self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 1)
#         self.assertEqual(len(Wall_E_image_sensation.getConnections()), 1)

        #finally  Item
        Wall_E_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Wall-E', connections=[])
        print('4 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 0)
       # TensorflowCalssification Connects image and Item, so we simulate it
        Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=Wall_E_image_sensation,
                                                                 score=ConnectionTestCase.SCORE))
# TODO this should not do anything, but it does!
# left away, to test that all sensatons will finally get 2 connections with each other
        #Wall_E_image_sensation.addConnection(Sensation.Connection(sensation=Wall_E_item_sensation,
        #                                                          score=ConnectionTestCase.SCORE))

        print('5 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('6 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 1)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 1)
        # this connectin should be connected to a Voice now, when we process new Item created
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # Voice, Image and Item are Connected
        print('7 len(Wall_E_voice_sensation.getConnections()) ' + str(len(Wall_E_voice_sensation.getConnections())))
        print('8 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('9 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))

        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 2)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 2)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 2)
       
        
        Eva_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Eva', connections=[])
#        Eva_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Eva')
        print('10 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))

        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Eva_item_sensation)
        print('11 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))
        self.assertEqual(len(Eva_item_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 3)
         
        #self.assertIs(Wall_E_voice_sensation.getConnections()[0].getSensation(), self.Wall_E_item_sensation)
        self.assertEqual(Eva_item_sensation.getConnections()[0].getScore(), ConnectionTestCase.SCORE)
       

#     def test_AddConnection(self):
#         addSensation = Sensation.create(sensation=self.Wall_E_item_sensation, memory=Sensation.Memory.LongTerm, name='connect_test')
#         self.assertIsNot(addSensation, None)
#         addSensation.save()    # this is worth to save its data
#         self.assertIs(len(addSensation.getConnections()), 1)
#         
#         connection_number = len(self.Wall_E_item_sensation.getConnections())
# 
#         self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=addSensation,
#                                                           score=addSensation.getScore()))
#         self.assertIs(len(self.Wall_E_item_sensation.getConnections()), connection_number+1)
#         self.assertIs(len(addSensation.getConnections()), 2)
#         Sensation.logConnections(self.Wall_E_item_sensation)
#         # again, should not add connection twise
#         self.Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=addSensation,
#                                                           score=addSensation.getScore()))
#         self.assertIs(len(self.Wall_E_item_sensation.getConnections()), connection_number+1)
#         self.assertIs(len(addSensation.getConnections()), 2)
#         Sensation.logConnections(self.Wall_E_item_sensation)



        
if __name__ == '__main__':
    unittest.main()

 