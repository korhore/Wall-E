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
import time as systemTime

from Robot import  Robot
from Sensation import Sensation

class Communication(Robot):

    COMMUNICATION_INTERVAL=60.0    # time window to history 
                                    # for  sensations we communicate
    COMMUNICATION_SCORE_LIMIT=0.1   # how strong connection sensation should have
                                    # if sensations are connected  with others sensations
                                    # in time window 

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in Communication, not Robot")
        self.spokenVoiceSensation = None
        self.itemSensation = None
        
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
 
    def process(self, transferDirection, sensation):
        self.log('process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        #run default implementation first
        #super(Communication, self).process(transferDirection=transferDirection, sensation=sensation)
        # don't communicate with history Sensation Items, we are comunicating Item.name just seen.
        if sensation.getSensationType() == Sensation.SensationType.Item and\
            systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL:
            self.log('Communication.process: Item Sensation ' + sensation.toDebugStr())
            # try to find best item.Name with Voice
            candidate_for_communication = Sensation.getBestSensation( sensationType = Sensation.SensationType.Item,
                                                                name = sensation.getName(),
                                                                timemin = None,
                                                                timemax = None,
                                                                connectionSensationType=Sensation.SensationType.Voice)
            if candidate_for_communication is not None:
                for connection in candidate_for_communication.getConnections():
                    if connection.getSensation().getSensationType() == Sensation.SensationType.Voice:
                        voiceSensation = Sensation.create(connections = [],
                                                          sensation = connection.getSensation(),
                                                          direction = Sensation.Direction.In, # speak
                                                          memory = Sensation.Memory.Sensory)
                        # to be sure
#                         voiceSensation.setDirection(Sensation.Direction.In)
#                         voiceSensation.setMemory(Sensation.Memory.Sensory)
# Not needed to remember, that we tried to speak
# this make too many connections
#                        candidate_for_communication.addConnection(Sensation.Connection(sensation=voiceSensation,
#                                                                                       score=candidate_for_communication.getScore()))
                        self.log('Communication.process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)')
                        self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)
                        
                        # TODO We should wait answer and communicate as long other part wants

 