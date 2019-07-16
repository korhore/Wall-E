'''
Created on 28.05.2019
Updated on 28.05.2019

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

    ASSOCIATION_INTERVAL=10.0    # time window plus/minus in seconds 
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
 
    def process(self, transferDirection, sensation):
        self.log('1:  process: sensation ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        new_association = False
        #run default implementation first
        # if still running and we can process this
        #
        # Connect to Item that has strongest Sensation.Association
        # Item is name of a thing happening just now, person, table, chair, etc.
        # This way we Connect characteristic features for thing Thing, what it looks like (Image),
        # what sound it keeps (Voice), What other  Things are present, when this one is present, etc
        
        # If we got Item, then get best Item.name
        if sensation.getSensationType() == Sensation.SensationType.Item:
            # Connect to Item that has strongest Sensation.Association
            # Item is name of a thing happening just now, person, table, chair, etc.
            # This way we Connect characteristic features for thing Thing, what it looks like (Image),
            # what sound it keeps (Voice), What other  Things are present, when this one is present, etc
            
            # choose best Item.name for associations
            candidate_for_connect = Sensation.getBestSensation( sensationType = Sensation.SensationType.Item,
                                                                name = sensation.getName(),
                                                                timemin = sensation.getTime()-Association.ASSOCIATION_INTERVAL,
                                                                timemax = sensation.getTime()+Association.ASSOCIATION_INTERVAL)
            if candidate_for_connect is not None:
                self.log('2:  process: candidate_for_connect ' + time.ctime(candidate_for_connect.getTime()) + ' ' + candidate_for_connect.toDebugStr())
            
            if candidate_for_connect is not None and \
               len(candidate_for_connect.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS and \
               candidate_for_connect != sensation and \
               candidate_for_connect.getScore() > sensation.getScore():
                sensation = candidate_for_connect
                self.log('3:  process: better sensation found ' + time.ctime(sensation.getTime()) + ' ' + sensation.toDebugStr())
                # put  to the parent Axon going up to main Robot
                # TODO, this is sensed item, so we should check that from sensation
                self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)

        # TODO if we connect a Voice, notName is meaningless                                        
        # get candidates from sensation cache, that are Items with different name
        
        if len(sensation.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS:
                
            candidate_to_connect = Sensation.getBestSensation( sensationType = Sensation.SensationType.Item,
                                                               notName = sensation.getName(),
                                                               timemin = sensation.getTime()-Association.ASSOCIATION_INTERVAL,
                                                               timemax = sensation.getTime()+Association.ASSOCIATION_INTERVAL)
            # connect different Items to each other or
            # connect other thing to different Items, but best of item name found
            # to get reasonable associations
            if candidate_to_connect is not None:
                self.log('4:  process: candidate_to_connect ' + time.ctime(candidate_to_connect.getTime()) + ' ' + candidate_to_connect.toDebugStr())
                # get current connected Item.name
                current_connected_sensation = sensation.getBestConnectedSensation( sensationType = Sensation.SensationType.Item,
                                                                                   name = sensation.getName())
                if current_connected_sensation is None: # if not yet connecter Item.name
                    new_association=True
                    self.log('5:  process: no current association')
                elif candidate_to_connect.getScore() > current_connected_sensation.getScore():
                    new_association=True
                    # remove old worse association
                    self.log('6:  process: current_connected_sensation was worse ' + time.ctime(current_connected_sensation.getTime()) + ' ' + current_connected_sensation.toDebugStr())
                    self.log('7:  process: sensation.removeAssociation(current_connected_sensation)')
                    sensation.removeAssociation(current_connected_sensation)
                    
    
                if new_association and len(candidate_to_connect.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS:                
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
                        
                    sensation.addAssociation(Sensation.Association(self_sensation=sensation,
                                                                   sensation=candidate_to_connect,
                                                                   score=candidate_to_connect.getScore()))
        
                    # for debugging reasons we log what associations we have now
                    #Sensation.logAssociations(sensation)
            
            # get other candidates from sensation cache, that are other than Item
            candidates_to_connect = Sensation.getSensations( capabilities = self.getCapabilities(),
                                                             timemin = sensation.getTime()-Association.ASSOCIATION_INTERVAL,
                                                             timemax = sensation.getTime()+Association.ASSOCIATION_INTERVAL)
            for candidate_to_connect in candidates_to_connect:
                if candidate_to_connect is not sensation and len(candidate_to_connect.getAssociations()) < Sensation.ASSOCIATIONS_MAX_ASSOCIATIONS:
                    self.log('9:  process: Sensation ' + sensation.toDebugStr() + ' will be connected to: ' +\
                                candidate_to_connect.toDebugStr())
                    # if we have found got Sensory sensation, we want to remember this, so copy it as LongTerm-memory sensations
                    if sensation.getMemory()==Sensation.Memory.Sensory:
                        sensation.setMemory(Sensation.Memory.LongTerm)
                        self.log('10: process: sensation.setMemory(Sensation.Memory.LongTerm) ' + sensation.toDebugStr())
    #                     sensation = Sensation.create(sensation=sensation, memory=Sensation.Memory.LongTerm)
                        sensation.save()    # this is worth to save its data
                    # if we have found candidate_to_connect got Sensory sensation, we want to remember this, so copy it as LongTerm-memory sensations
                    if candidate_to_connect.getMemory()==Sensation.Memory.Sensory:
                        candidate_to_connect.setMemory(Sensation.Memory.LongTerm)
                        self.log('11: process: candidate_to_connect.setMemory(Sensation.Memory.LongTerm) ' + candidate_to_connect.toDebugStr())
    #                     candidate_to_connect = Sensation.create(sensation=candidate_to_connect, memory=Sensation.Memory.LongTerm)
                        candidate_to_connect.save()    # this is worth to save its data
                        
                    # TODO study which score we will get
                            
                    self.log('12: process: sensation.addAssociation(Sensation.Association(self_sensation==sensation ' +  sensation.toDebugStr() + ' sensation=candidate_to_connect ' + candidate_to_connect.toDebugStr())
#                     print("12 before len(sensation.getAssociations()) " + str(len(sensation.getAssociations())))
#                     print("12 before len(candidate_to_connect.getAssociations()) " + str(len(candidate_to_connect.getAssociations())))
                    sensation.addAssociation(Sensation.Association(self_sensation=sensation,
                                                                   sensation=candidate_to_connect,
                                                                   score=candidate_to_connect.getScore()))
#                     print("12 after  len(sensation.getAssociations()) " + str(len(sensation.getAssociations())))
#                     print("12 after  len(candidate_to_connect.getAssociations()) " + str(len(candidate_to_connect.getAssociations())))
                    
                    # for testing purposes try other way
                    candidate_to_connect.addAssociation(Sensation.Association(self_sensation=candidate_to_connect,
                                                                   sensation=sensation,
                                                                   score=candidate_to_connect.getScore()))
#                     print("12 after2  len(sensation.getAssociations()) " + str(len(sensation.getAssociations())))
#                     print("12 after2  len(candidate_to_connect.getAssociations()) " + str(len(candidate_to_connect.getAssociations())))

#                     # TODO this is now needed, but should it? Association is ment to be two sided.
#                     self.log('13: process: candidate_to_connect.addAssociation(Sensation.Association(sensation=sensation ' + candidate_to_connect.toDebugStr())
#                     candidate_to_connect.addAssociation(Sensation.Association(self_sensation=candidate_to_connect,
#                                                                               sensation=sensation,
#                                                                               score=sensation.getScore()))
                    new_association = True
                    # TODO
                    # At this point we could also start communicating if sensation is Item and candidate_to_connect is Voice or opposite way
                    # At this point we haven't implemented Communication status fot detecting if we get a response from the item we are communicating with
                    # disabled
#                     if sensation.getSensationType() == Sensation.SensationType.Item and \
#                        candidate_to_connect.getSensationType() == Sensation.SensationType.Voice:
#                         voiceSensation = Sensation.create(associations=[],
#                                                           sensation=candidate_to_connect,
#                                                           direction= Sensation.Direction.In, # speak
#                                                           memory = Sensation.Memory.Sensory)
# # TODO Not needed to remember that we tries to speak with Item
# # This makes too many Associations
# #                        sensation.addAssociation(Sensation.Association(sensation=voiceSensation,
# #                                                                     score=sensation.getScore()))
#                         self.log('14:  process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)')
#                         self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)
#                     elif sensation.getSensationType() == Sensation.SensationType.Voice and \
#                          candidate_to_connect.getSensationType() == Sensation.SensationType.Item:
#                         voiceSensation = Sensation.create(associations=[],
#                                                           sensation=sensation,
#                                                           direction= Sensation.Direction.In, # speak
#                                                           memory = Sensation.Memory.Sensory)
# # TODO Not needed to remember that we tries to speak with Item
# # This makes too many Associations
# #                        candidate_to_connect.addAssociation(Sensation.Association(sensation=voiceSensation,
# #                                                                                score=candidate_to_connect.getScore()))
#                         self.log('15:  process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)')
#                         self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)
                
            #if new_association:
            if new_association and self.getLogLevel() >= Robot.LogLevel.Detailed:
               # for debugging reasons we log what associations we have now
                Sensation.logAssociations(sensation)
        else:
            self.log('99: process: sensation has reached association max ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())

       
