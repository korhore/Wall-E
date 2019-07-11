'''
Created on 21.06.2019
Updated on 11.07.2019
@author: reijo.korhonen@gmail.com

test Association class
python3 -m unittest tests/testAssociation.py


'''
import time as systemTime

import unittest
from Sensation import Sensation
from Association.Association import Association
from Axon import Axon

from PIL import Image as PIL_Image

class AssociationTestCase(unittest.TestCase):
    ''' create situation, where we have found
        - Wall_E_item
        - Image
        - voice
    '''
    
    SCORE=0.8
    
    def setUp(self):
        self.axon = Axon()
#         self.Wall_E_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item,  direction=Sensation.Direction.Out, name='Wall-E')
#         self.Wall_E_image_sensation = Sensation.create(sensationType=Sensation.SensationType.Image, direction=Sensation.Direction.Out)
#         self.Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation,
#                                              score=AssociationTestCase.SCORE)
        
        self.association = Association(parent=self,
                                       instanceName='Association',
                                       instanceType= Sensation.InstanceType.SubInstance,
                                       level=2)


    def tearDown(self):
#         self.Wall_E_item_sensation.delete()
#         self.Wall_E_image_sensation.delete()
        
        del self.association
        
#     def test_SensationCreate(self):
#         self.assertIsNot(self.Wall_E_item_sensation, None)
#         self.assertIsNot(self.Wall_E_image_sensation, None)

    '''
    1) Voice
    2) Image
    3) Simulate Item creation from Image and Connect Image and Item
    4) Item2 found at same time than Item
    '''
       
    def test_ProcessItem(self):
        # First voice
        Wall_E_voice_sensation = Sensation.create(sensationType=Sensation.SensationType.Voice, direction=Sensation.Direction.Out)
        print("1 len(Wall_E_voice_sensation.getAssociations()) " + str(len(Wall_E_voice_sensation.getAssociations())))
              
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 0)
        # process situation, where voice is happened same time than Item
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_sensation)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 0)
        
        #then image and Item
        Wall_E_image_sensation = Sensation.create(sensationType=Sensation.SensationType.Image,  direction=Sensation.Direction.Out, image=PIL_Image.new(mode='RGB',size=(1,1)),)
        print("-2 len(Wall_E_voice_sensation.getAssociations()) " + str(len(Wall_E_voice_sensation.getAssociations())))
        print('-3 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
#         Wall_E_item_sensation.associate(sensation=self.Wall_E_image_sensation,
#                                         score=AssociationTestCase.SCORE)
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        print("2 len(Wall_E_voice_sensation.getAssociations()) " + str(len(Wall_E_voice_sensation.getAssociations())))
        for association in Wall_E_voice_sensation.getAssociations():
            print (Wall_E_voice_sensation.toDebugStr() + ' is connected to ' + association.getSensation().toDebugStr())
        print('3 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        for association in Wall_E_voice_sensation.getAssociations():
            print (Wall_E_voice_sensation.toDebugStr() + ' is connected to ' + association.getSensation().toDebugStr())
        # item is not connected to Image, because we don,t have Item yet/connected together
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        
#         self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
#         # Voice and Image are Connected
#         self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 1)
#         self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)

        #finally  Item
        Wall_E_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item,  direction=Sensation.Direction.Out, name='Wall-E')
        print('4 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 0)
       # TensorflowCalssification Connects image and Item, so we simulate it
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation,
                                        score=AssociationTestCase.SCORE)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(Wall_E_item_sensation.getAssociations()[0].getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)

        # again, this should not do anything
        Wall_E_image_sensation.associate(sensation=Wall_E_item_sensation,
                                         score=AssociationTestCase.SCORE)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(Wall_E_item_sensation.getAssociations()[0].getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)

        print('5 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('6 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))
        # this connection should be connected to a Voice now, when we process new Item created
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # Voice, Image and Item are Connected
        print('7 len(Wall_E_voice_sensation.getAssociations()) ' + str(len(Wall_E_voice_sensation.getAssociations())))
        print('8 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('9 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))

        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 2)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 2)
        
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_image_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_voice_sensation.getScore(), 0.0) # 0.0. is OK, if Association-Robot does not touch on Scores, but only associates
      
        
        Eva_item_sensation = Sensation.create(sensationType=Sensation.SensationType.Item,  direction=Sensation.Direction.Out, name='Eva')
        print('10 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        
        self.assertEqual(Wall_E_voice_sensation.getScore(), 0.0)
        self.assertEqual(Wall_E_image_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)

        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Eva_item_sensation)
        print('11 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        self.assertEqual(len(Eva_item_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 3)
                 
        self.assertEqual(Eva_item_sensation.getScore(),  AssociationTestCase.SCORE)  # 0.0. is OK, if Association-Robot does not touch on Scores, but only associates
        self.assertEqual(Wall_E_voice_sensation.getScore(), 0.0)
        self.assertEqual(Wall_E_image_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)

    '''
    1) Image
    2) Simulate Item creation from Image and Connect Image and Item
    3) Voice
    4) Item2 found at same time than Item
    '''

    def test_ProcessItemFirst(self):
        # define time, that is different than in others tests
        sensationTime = systemTime.time() + 2*Association.ASSOCIATION_INTERVAL
#         #First image and Item
        Wall_E_image_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Image,  direction=Sensation.Direction.Out, image=PIL_Image.new(mode='RGB',size=(1,1)))
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        print('1 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        # item is not connected to Image, because we don,t have Item yet/connected together
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 0)
        
        # then Item
        Wall_E_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name='Wall-E',  direction=Sensation.Direction.Out)
        print('2 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 0)
       # TensorflowCalssification Connects image and Item, so we simulate it
        Wall_E_item_sensation.associate(sensation=Wall_E_image_sensation,
                                        score=AssociationTestCase.SCORE)

        print('3 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('4 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # Voice, Image and Item are Connected
        print('5 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('6 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))

        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        
##############################################################################################
        
        # last voice
        Wall_E_voice_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Voice,  direction=Sensation.Direction.Out)
        print("7 len(Wall_E_voice_sensation.getAssociations()) " + str(len(Wall_E_voice_sensation.getAssociations())))
              
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 0)
        # process situation, where voice is happened same time than Image and, but processed after Item
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_sensation)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 2)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 2)      
        
        Eva_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item, name='Eva',  direction=Sensation.Direction.Out)
        print('8 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))

        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Eva_item_sensation)
        print('9 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        self.assertEqual(len(Eva_item_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 3)
         
        self.assertEqual(Eva_item_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_voice_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_image_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)
      
    '''
    1) Item2 found
    2) Voice
    3) Image
    4) Simulate Item creation from Image and Connect Image and Item
    '''

    def test_ProcessItem2First(self):
        # define time, that is different than in others tests
        sensationTime = systemTime.time() + 4*Association.ASSOCIATION_INTERVAL
#         #First Item2
        Eva_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item,  direction=Sensation.Direction.Out, name='Eva')
        print('1 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Eva_item_sensation)
        print('2 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        
        self.assertEqual(len(Eva_item_sensation.getAssociations()), 0)
        
        # then voice
        Wall_E_voice_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Voice,  direction=Sensation.Direction.Out)
        print("3 len(Wall_E_voice_sensation.getAssociations()) " + str(len(Wall_E_voice_sensation.getAssociations())))              
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 0)
        # process situation, where voice is happened same time than Item2
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_voice_sensation)
        
        self.assertEqual(len(Eva_item_sensation.getAssociations()), 1)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 1)
        

        # Simulate We get Image and create an Item
        Wall_E_image_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Image,  direction=Sensation.Direction.Out, image=PIL_Image.new(mode='RGB',size=(1,1)))
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        print('4 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('5 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        print('6 len(Wall_E_voice_sensation.getAssociations()) ' + str(len(Wall_E_voice_sensation.getAssociations())))

        # We have an item so all are connected together
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 2)
        self.assertEqual(len(Eva_item_sensation.getAssociations()), 2)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 2)
        
        # finally we simulate Item is created from image
        Wall_E_item_sensation = Sensation.create(time=sensationTime, sensationType=Sensation.SensationType.Item,  direction=Sensation.Direction.Out, name='Wall-E')
        print('7 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 0)
       # TensorflowCalssification Connects image and Item, so we simulate it
        Wall_E_item_sensation.associate(sensation = Wall_E_image_sensation,
                                        score = AssociationTestCase.SCORE)

        print('8 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('9 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 1)
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_image_sensation)
        self.association.process(transferDirection=Sensation.TransferDirection.Up, sensation=Wall_E_item_sensation)
        # Items2, Voice, Image, Item are Connected
        print('10 len(Eva_item_sensation.getAssociations()) ' + str(len(Eva_item_sensation.getAssociations())))
        print('11 len(Wall_E_voice_sensation.getAssociations()) ' + str(len(Wall_E_voice_sensation.getAssociations())))
        print('12 len(Wall_E_image_sensation.getAssociations()) ' + str(len(Wall_E_image_sensation.getAssociations())))
        print('13 len(Wall_E_item_sensation.getAssociations()) ' + str(len(Wall_E_item_sensation.getAssociations())))


        self.assertEqual(len(Eva_item_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_voice_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_image_sensation.getAssociations()), 3)
        self.assertEqual(len(Wall_E_item_sensation.getAssociations()), 3)

        self.assertEqual(Eva_item_sensation.getScore(), 0.0)  # 0.0. is OK, if Association-Robot does not touch on Scores, but only associates
        self.assertEqual(Wall_E_voice_sensation.getScore(), 0.0)
        self.assertEqual(Wall_E_image_sensation.getScore(), AssociationTestCase.SCORE)
        self.assertEqual(Wall_E_item_sensation.getScore(), AssociationTestCase.SCORE)
        
if __name__ == '__main__':
    unittest.main()

 