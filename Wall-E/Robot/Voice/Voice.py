'''
Created on 28.05.2019
Updated on 28.05.2019

@author: reijo.korhonen@gmail.com
'''

from Robot import  Robot
from Sensation import Sensation


class Voice(Robot):
    """
     Basic derivation
    """

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0):
        print("We are in Voice, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
    