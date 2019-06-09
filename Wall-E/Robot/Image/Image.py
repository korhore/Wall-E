'''
Created on 20.05.2019
Updated on 20.05.2019

@author: reijo.korhonen@gmail.com
'''

from Robot import  Robot
from Sensation import Sensation


class Image(Robot):
    """
    Basic derivation
    """

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in Image, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
    