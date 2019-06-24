'''
Created on 21.06.2019
Updated on 21.06.2019
@author: reijo.korhonen@gmail.com

test Connection class
python3 -m unittest tests/testConnection.py


'''
import time as systemTime

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

    '''
    1) Voice
    2) Image
    3) Simulate Item creratin from Image and Connect Image ans Item
    4) Item2 found at same time than Item
    '''
       
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
 
    '''
    1) Image
    2) Simulate Item creratin from Image and Connect Image ans Item
    3) Voice
    4) Item2 found at same time than Item
    '''

    def test_ProcessItemFirst(self):
        # define time, that is different than in others tests
        sensationTime = systemTime.time() + 2*Connection.CONNECTION_INTERVAL
#         #First image and Item
        Wall_E_image_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Image, image=PIL_Image.new(mode='RGB',size=(1,1)), connections=[])
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        print('1 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        # item is not connected to Image, because we don,t have Item yet/connected together
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 0)
        
        # then Item
        Wall_E_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name='Wall-E', connections=[])
        print('2 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 0)
       # TensorflowCalssification Connects image and Item, so we simulate it
        Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=Wall_E_image_sensation,
                                                                 score=ConnectionTestCase.SCORE))

        print('3 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('4 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 0)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 1)
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # Voice, Image and Item are Connected
        print('5 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('6 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))

        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 1)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 1)
        
##############################################################################################
        
        # last voice
        Wall_E_voice_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Voice, connections=[])
#        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice)
        print("7 len(Wall_E_voice_sensation.getConnections()) " + str(len(Wall_E_voice_sensation.getConnections())))
              
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 0)
        # process situation, where voice is happened same time than Image and, but processed after Item
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_sensation)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 2)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 2)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 2)      
        
        Eva_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name='Eva', connections=[])
#        Eva_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item, name='Eva')
        print('8 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))

        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Eva_item_sensation)
        print('9 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))
        self.assertEqual(len(Eva_item_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 3)
         
        #self.assertIs(Wall_E_voice_sensation.getConnections()[0].getSensation(), self.Wall_E_item_sensation)
        self.assertEqual(Eva_item_sensation.getConnections()[0].getScore(), ConnectionTestCase.SCORE)
      
    '''
    1) Item2 found
    2) Voice
    3) Image
    4) Simulate Item creation from Image and Connect Image ans Item
    '''

    def test_ProcessItem2First(self):
        # define time, that is different than in others tests
        sensationTime = systemTime.time() + 4*Connection.CONNECTION_INTERVAL
#         #First Item2
        Eva_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name='Eva', connections=[])
        print('1 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Eva_item_sensation)
        print('2 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))
        
        self.assertEqual(len(Eva_item_sensation.getConnections()), 0)
        
        # then voice
        Wall_E_voice_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Voice, connections=[])
#        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice)
        print("3 len(Wall_E_voice_sensation.getConnections()) " + str(len(Wall_E_voice_sensation.getConnections())))              
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 0)
        # process situation, where voice is happened same time than Item2
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_sensation)
        
        self.assertEqual(len(Eva_item_sensation.getConnections()), 1)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 1)
        

        # Simulate We get Image and create an Item
        Wall_E_image_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Image, image=PIL_Image.new(mode='RGB',size=(1,1)), connections=[])
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        print('4 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('5 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))
        print('6 len(Wall_E_voice_sensation.getConnections()) ' + str(len(Wall_E_voice_sensation.getConnections())))

        # We have an item so all are connected together
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 2)
        self.assertEqual(len(Eva_item_sensation.getConnections()), 2)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 2)
        
        # finally we simulate Item is created from image
        Wall_E_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name='Wall-E', connections=[])
        print('7 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 0)
       # TensorflowCalssification Connects image and Item, so we simulate it
        Wall_E_item_sensation.addConnection(Sensation.Connection(sensation=Wall_E_image_sensation,
                                                                 score=ConnectionTestCase.SCORE))

        print('8 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('9 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 2)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 1)
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        self.connection.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # Items2, Voice, Image, Item are Connected
        print('10 len(Eva_item_sensation.getConnections()) ' + str(len(Eva_item_sensation.getConnections())))
        print('11 len(Wall_E_voice_sensation.getConnections()) ' + str(len(Wall_E_voice_sensation.getConnections())))
        print('12 len(Wall_E_image_sensation.getConnections()) ' + str(len(Wall_E_image_sensation.getConnections())))
        print('13 len(Wall_E_item_sensation.getConnections()) ' + str(len(Wall_E_item_sensation.getConnections())))


        self.assertEqual(len(Eva_item_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_voice_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_image_sensation.getConnections()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getConnections()), 3)

        
if __name__ == '__main__':
    unittest.main()

 