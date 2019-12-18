'''
Created on 28.05.2019
Updated on 07.08.2019

@author: reijo.korhonen@gmail.com

Association is a Robot, that finds association between things.
It is interested about anything and connects those  Sensations together,
that happen in short time window. So in Robot finds an Image, that produces an Item
named 'person' and then, before or after hears an sound, Robot finds out,
that person can keep sound. Or if a chair is seen when person is seen, we know
if we see a chair, soon we can see a person or other way.

These association as base structure of our memories structure, memories are
connected between others and associations that are used, will become stronger.
Our Robot acts just same way, it tries to lean which things are connected together,
to lean how this world works and what is happening.



'''
import time

from Robot import  Robot
from Sensation import Sensation


class Association(Robot):

    #ASSOCIATION_INTERVAL=30.0    # time window plus/minus in seconds 
                                # for  sensations we connect together
    #ASSOCIATION_SCORE_LIMIT=0.1  # how strong association sensation should have
                                # if we we connect it together with others sensations
                                # in time window 

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in Association, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
    def process(self, transferDirection, sensation, association=None):
        self.log('process: sensation ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
           #Robot.presentItemSensations can be changed
        succeeded = False
        while not succeeded:
            try:
                for itemSensation in Robot.presentItemSensations.values():
                    if sensation is not itemSensation and\
                       sensation.getTime() >=  itemSensation.getTime() and\
                       len(itemSensation.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS:
                        self.log('process: sensation.associate(Sensation.Association(self_sensation==itemSensation ' +  itemSensation.toDebugStr() + ' sensation=sensation ' + sensation.toDebugStr())
                        itemSensation.associate(sensation=sensation,
                                                score=itemSensation.getScore())
                    else:
                        self.log('process: itemSensation ignored too much associations or items not newer than present itemSensation or sensation is present sensation' + itemSensation.toDebugStr())
                succeeded = True
            except Exception as e:
                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Association.process: ignored exception ' + str(e))

