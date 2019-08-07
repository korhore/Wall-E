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

    ASSOCIATION_INTERVAL=30.0    # time window plus/minus in seconds 
                                # for  sensations we connect together
    ASSOCIATION_SCORE_LIMIT=0.1  # how strong association sensation should have
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
        self.present_items={}
        
    def process(self, transferDirection, sensation, association=None):
        self.log('process: sensation ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        now = time.time()
        if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemory() == Sensation.Memory.LongTerm and\
           sensation.getDirection() == Sensation.Direction.Out: 
            self.tracePresents(sensation)
        #we have present item.names we can connect
        elif len(self.present_items) > 0 and \
             sensation.getTime() >= now - Association.ASSOCIATION_INTERVAL and \
             sensation.getTime() <= now + Association.ASSOCIATION_INTERVAL and \
             len(sensation.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS:
            for itemSensation in self.present_items.values():
                if len(itemSensation.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS:
                    self.log('process: sensation.associate(Sensation.Association(self_sensation==itemSensation ' +  itemSensation.toDebugStr() + ' sensation=sensation ' + sensation.toDebugStr())
                    itemSensation.associate(sensation=sensation,
                                            score=itemSensation.getScore())
                else:
                    self.log('process: itemSensation ignored too much associations ' + itemSensatio.toDebugStr())
        else:
            self.log('process: sensation ignored')
       

    '''
        Trace present Item.names from sensations
    '''
  
    def tracePresents(self, sensation):
        # present means pure Present, all other if handled not present
        if sensation.getPresence() == Sensation.Presence.Entering or\
           sensation.getPresence() == Sensation.Presence.Present:
            if sensation.getName() not in self.present_items or\
                sensation.getTime() > self.present_items[sensation.getName()].getTime():
                self.present_items[sensation.getName()] = sensation
                self.log(logLevel=Robot.LogLevel.Normal, logStr="entering or present " + sensation.getName())
            else:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr="entering or present did not come in order for " + sensation.getName())
        else:
            if sensation.getName() in self.present_items:
                if sensation.getTime() > self.present_items[sensation.getName()].getTime():
                    del self.present_items[sensation.getName()]
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="absent " + sensation.getName())
                else:
                    self.log(logLevel=Robot.LogLevel.Detailed, logStr="absent did not come in order for " + sensation.getName())
            else:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr="absent but did not enter for " + sensation.getName())
       
