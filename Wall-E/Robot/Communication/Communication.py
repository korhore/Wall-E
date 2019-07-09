'''
Created on 06.06.2019
Updated on 28.05.2019

@author: reijo.korhonen@gmail.com

Communication is a Robot, that communicates  association between things.
It is interested about Items and tries to find out how to communicate
with them.

This first version Communication with Voices. When it finds out an Item
it searches Voices it has heard and Playbacks best Sensation.Association ranged Voice
it can find out.

Next version can wait for a response. Or we can introduce ourselves, because we
have an identity, a directory where is stored our own Voice.

We should also implement Feelings to decide what Voices are good ones (they will be replied)
and what are bad ones.

We                Other
1) Introduce
2) Best Voice from Other
3) Wait response

if                Voice
4) Feel Best      Voice
- We would use this Voice next time with Other
5) Connect Other with Voice
5) Feel Good      Introduce
6) Feel Good      Best Voice from Other
- This will be second best choice with Other

else
7) Feel Sad Best Voice from Other
   - this way we would try next time other Voice

'''
import time as systemTime

from Robot import  Robot
from Sensation import Sensation

class Communication(Robot):

    COMMUNICATION_INTERVAL=60.0     # time window to history 
                                    # for sensations we communicate
    COMMUNICATION_SCORE_LIMIT=0.1   # how strong association sensation should have
                                    # if sensations are connected  with others sensations
                                    # in time window
                                    
    class CommunicationItem():
        def _init__(self,
                    sensation,
                    time,
                    association):
            self.sensation = sensation
            self.time  = time
            self.association = association
            
        def getSensation(self):
            return self.sensation
        def setSensation(self, ensation):
            self.sensation = sensation
     
        def getTime(self):
            return self.time
        def setTime(self, time):
            self.time = time
            
        def getAssociation(self):
            return self.association
        def setAssociation(self, association):
            self.association = association
        

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in Communication, not Robot")
        self.communicationItems = []
        
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
 
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        #run default implementation first
        #super(Communication, self).process(transferDirection=transferDirection, sensation=sensation)
        # don't communicate with history Sensation Items, we are comunicating Item.name just seen.
        if sensation.getSensationType() == Sensation.SensationType.Item and\
            systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: Item Sensation ' + sensation.toDebugStr())
            # try to find best item.Name with Voice
            candidate_for_communication = Sensation.getBestSensation( sensationType = Sensation.SensationType.Item,
                                                                      name = sensation.getName(),
                                                                      notName = None,
                                                                      timemin = None,
                                                                      timemax = None,
                                                                      associationSensationType=Sensation.SensationType.Voice)
            if candidate_for_communication is not None:
                # get best Voice
                voiceSensation = None
                for association in candidate_for_communication.getAssociations():
                    if association.getSensation().getSensationType() == Sensation.SensationType.Voice:
                        if voiceSensation is None or association.getScore() > voiceSensation.getScore():
                            voiceSensation = association.getSensation()
                if voiceSensation  is not None:
                    # create new Voice to speak and associate it to this sensation so
                    # we remember that we spoke it now
                    association = Sensation.Association(sensation=sensation,
                                                        score=voiceSensation.getScore())
                    voiceSensation = Sensation.create(associations = [association],
                                                      sensation = voiceSensation,
                                                      direction = Sensation.Direction.In, # speak
                                                      memory = Sensation.Memory.Sensory)
                    # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
                    voiceSensation.setDirection(Sensation.Direction.In)
                    voiceSensation.setMemory(Sensation.Memory.Sensory)
                    # association other way
                    association = Sensation.Association(sensation=voiceSensation,
                                                        score=voiceSensation.getScore())
                    voiceSensation.addAssociation(association)

# Not needed to remember, that we tried to speak
# this make too many associations
# # No, try to remember
# May get a loop
# still in a loop
#                         candidate_for_communication.addAssociation(Sensation.Association(sensation=voiceSensation,
#                                                                                        score=candidate_for_communication.getScore()))
                    self.log('Communication.process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)')

                    self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=voiceSensation)                    
                    # now we wait for a response for this
                    self.communicationItems.append(CommunicationItem(sensation = sensation,
                                                                     time,
                                                                     association = association))
                    # for this long
                    
                     # TODO We should wait answer and communicate as long other part wants
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: No  candidate_for_communication for ' + sensation.toDebugStr())
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not Item ' + sensation.toDebugStr())

     def stopWaitingResponse(self):
