'''
Created on 28.05.2019
Updated on 28.05.2019

@author: reijo.korhonen@gmail.com

Connection is a Robot, that finds connection between things.
It is interested about anything and connects those  Sensations together,
that happen in short time window. So in Robot finds an Image, that produces an Item
named 'person' and then, before or after hears an sound, Robot finds out,
that person can keep sound. Or if a chair is seen when person is seen, we know
if we see a chair, soon we can see a person or other way.

These connection as base structure of our memories structure, memories are
connected between others and connections that are used, will become stronger.
Our Robot acts just same way, it tries to lean which things are connected together,
to lean how this world works and what is happening.



'''
import time

from Robot import  Robot
from Sensation import Sensation


class Connection(Robot):

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
        print("We are in Connection, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
 
    def process(self, transferDirection, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        #run default implementation first
        # if still running and we can process this
        #
        # Connect to Item that has strongest Sensation.Connection
        # Item is name of a thing happening just now, person, table, chair, etc.
        # This way we Connect characteristic features for thing Thing, what it looks like (Image),
        # what sound it keeps (Voice), What other  Things are present, when this one is present, etc
        candidate_sensationsToConnect = Sensation.getSensations(capabilities=self.getCapabilities(),
                                                               timemin=sensation.getTime()-Connection.CONNECTION_INTERVAL,
                                                               timemax=sensation.getTime()+Connection.CONNECTION_INTERVAL)
        # connect different Items to each other or
        # connect other thing to different Items, but best of item name found
        # to get reasonable connections
        new_connection=False
        candidate_sensationToConnect = None
        if len(candidate_sensationsToConnect) > 0:
            # find out highest scored Item and Connect it with other
            for sens in candidate_sensationsToConnect:
                if sens.getSensationType() == Sensation.SensationType.Item and\
                   sens.getScore() > Connection.CONNECTION_SCORE_LIMIT and\
                   (candidate_sensationToConnect is None or\
                    sens.getScore() > candidate_sensationToConnect.getScore()):
                        candidate_sensationToConnect = sens
            if candidate_sensationToConnect is not None:
                    self.log('process: Sensation ' + sensation.toDebugStr() + ' will be connected to: ' +\
                             candidate_sensationToConnect.toDebugStr())
                    new_connection=True
                    # if we have found got Sensory sensation, we want to remember this, so Chanbge it as LongTerm-memory sensations
                    if sensation.getMemory()==Sensation.Memory.Sensory:
                        sensation.setMemory(Sensation.Memory.LongTerm)
                    sensation.save()    # this is worth to save its data
                    sensation.addConnection(Sensation.Connection(sensation=candidate_sensationToConnect,
                                                                 score=candidate_sensationToConnect.getScore()))

        # for debugging reasons we log what connections we have now
        if new_connection:
            Sensation.logConnections(sensation)
