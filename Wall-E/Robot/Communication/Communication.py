'''
Created on 06.06.2019
Updated on 28.05.2019

@author: reijo.korhonen@gmail.com

Communication is a Robot, that communicates  connection between things.
It is interested about Items and tries to find out how to communicate
with them.

This first version Communication with Voices. When it finds out an Item
it searches Voices it has heard and Playbacks best Sensation.Connection ranged Voice
it can find out.

Next version can wait for a response. Or we can introduce ourselves, because we
have an identity, a directory where is stored our own Voice.

'''
import time

from Robot import  Robot
from Sensation import Sensation


class Communication(Robot):

    CONNECTION_INTERVAL=10.0    # time window plus/minus in seconds 
                                # for  sensations we connect together
    CONNECTION_SCORE_LIMIT=0.1  # how strong connection sensation should have
                                # if we we connect it together with others sensations
                                # in time window 

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in Communication, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
 
    def process(self, transferDirection, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        #run default implementation first
        #super(Communication, self).process(transferDirection=transferDirection, sensation=sensation)
        if sensation.getSensationType() == Sensation.SensationType.Item:
            self.log('Communication.process: Item Sensation ' + sensation.toDebugStr())
            # TODO find out best Voices, not needed direct connections but some level accepted, maybe three
            for connection in sensation.getConnections():
                if connection.getSensation().getSensationType() == Sensation.SensationType.Voice:
                    voiceSensation = Sensation.create(connections=[],
                                                      sensation=connection.getSensation(),
                                                      direction= Sensation.Direction.In, # speak
                                                      memory = Sensation.Memory.Sensory)
                    self.log('Communication.process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)')
                    self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)

 