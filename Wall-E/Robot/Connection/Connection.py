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
        self.log('1:  process: sensation ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        new_connection = False
        #run default implementation first
        # if still running and we can process this
        #
        # Connect to Item that has strongest Sensation.Connection
        # Item is name of a thing happening just now, person, table, chair, etc.
        # This way we Connect characteristic features for thing Thing, what it looks like (Image),
        # what sound it keeps (Voice), What other  Things are present, when this one is present, etc
        
        # If we got Item, then get best Item.name
        if sensation.getSensationType() == Sensation.SensationType.Item:
            # Connect to Item that has strongest Sensation.Connection
            # Item is name of a thing happening just now, person, table, chair, etc.
            # This way we Connect characteristic features for thing Thing, what it looks like (Image),
            # what sound it keeps (Voice), What other  Things are present, when this one is present, etc
            
            # choose best Item.name for connections
            candidate_for_connect = Sensation.getBestSensation( sensationType = Sensation.SensationType.Item,
                                                                name = sensation.getName(),
                                                                timemin = sensation.getTime()-Connection.CONNECTION_INTERVAL,
                                                                timemax = sensation.getTime()+Connection.CONNECTION_INTERVAL)
            if candidate_for_connect is not None:
                self.log('2:  process: candidate_for_connect ' + time.ctime(candidate_for_connect.getTime()) + ' ' + candidate_for_connect.toDebugStr())
            
            if candidate_for_connect is not None and \
               candidate_for_connect != sensation and \
               candidate_for_connect.getScore() > sensation.getScore():
                sensation = candidate_for_connect
                self.log('3:  process: sensation ' + time.ctime(sensation.getTime()) + ' ' + sensation.toDebugStr())
                                        
        # get candidates from sensation cache, that are Items with different name
                
        candidate_to_connect = Sensation.getBestSensation( sensationType = Sensation.SensationType.Item,
                                                           notName = sensation.getName(),
                                                           timemin = sensation.getTime()-Connection.CONNECTION_INTERVAL,
                                                           timemax = sensation.getTime()+Connection.CONNECTION_INTERVAL)
        # connect different Items to each other or
        # connect other thing to different Items, but best of item name found
        # to get reasonable connections
        if candidate_to_connect is not None:
            self.log('4:  process: candidate_to_connect ' + time.ctime(candidate_to_connect.getTime()) + ' ' + candidate_to_connect.toDebugStr())
            # get current connected Item.name
            current_connected_sensation = sensation.getBestConnectedSensation( sensationType = Sensation.SensationType.Item,
                                                                               name = sensation.getName())
            if current_connected_sensation is None: # if not yet connecter Item.name
                new_connection=True
                self.log('5:  process: no current connection')
            elif candidate_to_connect.getScore() > current_connected_sensation.getScore():
                new_connection=True
                # remove old worse connection
                self.log('6:  process: current_connected_sensation was worse ' + time.ctime(current_connected_sensation.getTime()) + ' ' + current_connected_sensation.toDebugStr())
                self.log('7:  process: sensation.removeConnection(current_connected_sensation)')
                sensation.removeConnection(current_connected_sensation)
                

            if new_connection:                
                self.log('8:  process: Sensation ' + sensation.toDebugStr() + ' will be connected to: ' +\
                        candidate_to_connect.toDebugStr())
                # if we have found got Sensory sensation, we want to remember this, so copy it as LongTerm-memory sensations
                if sensation.getMemory()==Sensation.Memory.Sensory:
                    sensation.setMemory(Sensation.Memory.LongTerm)
#                    sensation = Sensation.create(sensation=sensation, memory=Sensation.Memory.LongTerm)
                    sensation.save()    # this is worth to save its data
                # if we have found candidate_to_connect got Sensory sensation, we want to remember this, so copy it as LongTerm-memory sensations
                if candidate_to_connect.getMemory()==Sensation.Memory.Sensory:
                    candidate_to_connect.setMemory(Sensation.Memory.LongTerm)
#                    candidate_to_connect = Sensation.create(sensation=candidate_to_connect, memory=Sensation.Memory.LongTerm)
                    candidate_to_connect.save()    # this is worth to save its data
                    
                sensation.addConnection(Sensation.Connection(sensation=candidate_to_connect,
                                                             score=candidate_to_connect.getScore()))
    
                # for debugging reasons we log what connections we have now
                #Sensation.logConnections(sensation)
        
        # get other candidates from sensation cache, that are other than Item
        candidates_to_connect = Sensation.getSensations( capabilities = self.getCapabilities(),
                                                         timemin = sensation.getTime()-Connection.CONNECTION_INTERVAL,
                                                         timemax = sensation.getTime()+Connection.CONNECTION_INTERVAL)
        for candidate_to_connect in candidates_to_connect:
            if candidate_to_connect is not sensation:
                self.log('9:  process: Sensation ' + sensation.toDebugStr() + ' will be connected to: ' +\
                            candidate_to_connect.toDebugStr())
                # if we have found got Sensory sensation, we want to remember this, so copy it as LongTerm-memory sensations
                if sensation.getMemory()==Sensation.Memory.Sensory:
                    sensation.setMemory(Sensation.Memory.LongTerm)
                    self.log('10:  process: sensation.setMemory(Sensation.Memory.LongTerm) ' + sensation.toDebugStr())
#                     sensation = Sensation.create(sensation=sensation, memory=Sensation.Memory.LongTerm)
                    sensation.save()    # this is worth to save its data
                # if we have found candidate_to_connect got Sensory sensation, we want to remember this, so copy it as LongTerm-memory sensations
                if candidate_to_connect.getMemory()==Sensation.Memory.Sensory:
                    candidate_to_connect.setMemory(Sensation.Memory.LongTerm)
                    self.log('11:  process: candidate_to_connect.setMemory(Sensation.Memory.LongTerm) ' + candidate_to_connect.toDebugStr())
#                     candidate_to_connect = Sensation.create(sensation=candidate_to_connect, memory=Sensation.Memory.LongTerm)
                    candidate_to_connect.save()    # this is worth to save its data
                        
                self.log('12:  process: sensation.addConnection(Sensation.Connection(sensation=candidate_to_connect ' + sensation.toDebugStr())
                sensation.addConnection(Sensation.Connection(sensation=candidate_to_connect,
                                                             score=candidate_to_connect.getScore()))
                # TODO this is now needed, but should it? Connection in ment to be two sided.
                self.log('13:  process: candidate_to_connect.addConnection(Sensation.Connection(sensation=sensation ' + candidate_to_connect.toDebugStr())
                candidate_to_connect.addConnection(Sensation.Connection(sensation=sensation,
                                                                        score=sensation.getScore()))
                new_connection = True
            
        if new_connection:
            # for debugging reasons we log what connections we have now
            Sensation.logConnections(sensation)

       
