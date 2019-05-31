'''
Created on 28.05.2019
Updated on 28.05.2019

@author: reijo.korhonen@gmail.com

Connection a Robot, that finds connection between things.
It is interested about anything and sconnect Sensations together, that happen
in short time window. So in Robot finds an Image, that produces an Item
named 'person' and then, before or after hears an sound, Robot finds out,
that person can keep sound. Or if a shair is seen when person is seen, we know
if we see a chair, soon we can see a person or other way.

These connection as base structure of out memories structure, memories are
connected between otgers and connections that are used, will become stronger.
Our Robot acts just same way, it tries to lean which things are connected together,
to lean how this world works and is happening.

'''
import time

from Robot import  Robot
from Sensation import Sensation


class Connection(Robot):

    CONNECTION_INTERVAL=10.0    # time how old sensations we connect together

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in Connection, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
 
    def process(self, sensation):
        #run default implementation first
        super(Connection, self).process(sensation)
            # if still running and we can process this
        candidate_sensatiosToConnect = Sensation.getNearbySensations(sensation.getTime()-Connection.CONNECTION_INTERVAL, sensation.getTime()+Connection.CONNECTION_INTERVAL)
        # connect different Items to each other or
        # connect other thing to different Items, but best of item name found
        # to get reasonable connections
        if len(candidate_sensatiosToConnect) > 0:
            sensatiosToConnect={}
            for sens in candidate_sensatiosToConnect:
                if sens.getSensationType() == Sensation.SensationType.Item:
                    # if we have already Item with this name, then update
                    # name with better one candidate
                    if sens.getName() in sensatiosToConnect:
                        # avoid connecting items with same name
                        if sens.getScore() > sensatiosToConnect[sens.getName()].getScore() and \
                           (sensation.getSensationType() is not Sensation.SensationType.Item or \
                            sensation.getName() != sens.getName()):
                            sensatiosToConnect[sens.getName()] = sens
                    else:
                        sensatiosToConnect[sens.getName()] = sens
            if len(sensatiosToConnect) > 0:
                self.log('process: Sensation ' + sensation.toDebugStr() + ' will be connected to:')
                sensation.save()    # this is worth to save its data
                for sens in sensatiosToConnect.values():
                     self.log(sens.toDebugStr())
                     sens.save()    # this is worth to save its data
                sensation.addReferences(sensatiosToConnect.values())
