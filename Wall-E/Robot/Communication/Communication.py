'''
Created on 06.06.2019
Updated on 12.07.2019

@author: reijo.korhonen@gmail.com

Communication is a Robot, that communicates association between things.
It is interested about Items and tries to find out how to communicate
with them.

This is NEED implementation for a Robot. Robot has a need to communicate
with an Item.name and it tries to find best way to it.
It Tries best Voice it knows. If it gets a response, it feels glad.
It classifies this voice it used higher with its feeling.

If it does not get a response, Robot feels sad. This classifies this voice lower,
so this voice is not used next time.

Result is a Robot with a a need, capability to feel and capability to lean
what is the best way to get its need fulfilled.

At other words below:

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
import threading 

from Robot import  Robot
from Sensation import Sensation

class Communication(Robot):

    COMMUNICATION_INTERVAL=60.0     # time window to history 
                                    # for sensations we communicate
    COMMUNICATION_SCORE_LIMIT=0.1   # how strong association sensation should have
                                    # if sensations are connected  with others sensations
                                    # in time window
    TEST_RESPONSE_TIME=2.5
                                    
    class CommunicationItem():
        def __init__(self,
                    sensation,
                    voiceSensation,
                    time,
                    association,
                    timer = None):
            self.sensation = sensation
            self.voiceSensation = voiceSensation
            self.time  = time
            self.association = association
            self.timer = timer
            
        def getSensation(self):
            return self.sensation
        def setSensation(self, sensation):
            self.sensation = sensation
     
        def getVoiceSensation(self):
            return self.voiceSensation
        def setVoiceSensation(self, voiceSensation):
            self.voiceSensation = voiceSensation
     
        def getTime(self):
            return self.time
        def setTime(self, time):
            self.time = time
            
        def getAssociation(self):
            return self.association
        def setAssociation(self, association):
            self.association = association
            
        def getTimer(self):
            return self.timer
        def setTimer(self, timer):
            self.timer = timer
       

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
            self.speakToItem(itemSensation=sensation)
        elif sensation.getSensationType() == Sensation.SensationType.Voice and\
            sensation.getDirection() == Sensation.Direction.Out and\
            systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL:
            for communicationItem in self.communicationItems:
                if sensation.getTime() > communicationItem.getTime():   # is this a response
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got a voice response for ' + communicationItem.getSensation().toDebugStr())
                    communicationItem.getTimer().cancel()
                    responce_voiceSensation = Sensation.create(sensation = sensation,
                                                               direction = Sensation.Direction.Out, # heard
                                                               memory = Sensation.Memory.LongTerm)
                    # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
                    responce_voiceSensation.setDirection(Sensation.Direction.Out)
                    responce_voiceSensation.setMemory(Sensation.Memory.LongTerm)
                    responce_voiceSensation.associate(sensation = communicationItem.getSensation(),
                                                      feeling=Sensation.Association.Feeling.Good)
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: created a voice feeling good  ' + responce_voiceSensation.toDebugStr())
                    sensation=communicationItem.getSensation

                    del communicationItem
                    
                    #response
                    self.speakToItem(itemSensation=sensation)
                    
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not Item ' + sensation.toDebugStr())

    def speakToItem(self, itemSensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speakToItem: Item Sensation ' + itemSensation.toDebugStr())
        
        candidate_for_communication = Sensation.getMostImportantSensation( sensationType = Sensation.SensationType.Item,
                                                                           name = itemSensation.getName(),
                                                                           notName = None,
                                                                           timemin = None,
                                                                           timemax = None,
                                                                           associationSensationType=Sensation.SensationType.Voice)
        if candidate_for_communication is not None:
            # get best Voice
            voiceSensation = None
            for association in candidate_for_communication.getAssociations():
                if association.getSensation().getSensationType() == Sensation.SensationType.Voice:
                    if voiceSensation is None or association.getImportance() > voiceSensation.getImportance():
                        voiceSensation = association.getSensation()
            if voiceSensation  is not None:
                # create new Voice to speak and associate it to this sensation so
                # we remember that we spoke it now
#                association = Sensation.Association(sensation=sensation,
#                                                         score=voiceSensation.getScore())
                spoke_voiceSensation = Sensation.create(sensation = voiceSensation,
                                                        direction = Sensation.Direction.In, # speak
                                                        memory = Sensation.Memory.Sensory)
                # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
                spoke_voiceSensation.setDirection(Sensation.Direction.In)
                spoke_voiceSensation.setMemory(Sensation.Memory.Sensory)
                spoke_voiceSensation.associate(sensation = voiceSensation,
                                               score=voiceSensation.getScore())
                itemSensation.associate(sensation = voiceSensation,
                                    score = itemSensation.getScore())
                itemSensation.associate(sensation = spoke_voiceSensation,
                                    score = itemSensation.getScore())

# Not needed to remember, that we tried to speak
# this make too many associations
# # No, try to remember
# May get a loop
# still in a loop
#                         candidate_for_communication.addAssociation(Sensation.Association(sensation=voiceSensation,
#                                                                                        score=candidate_for_communication.getScore()))
                self.log('Communication.process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=spoke_voiceSensation)')

                self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=spoke_voiceSensation)                    
                    # now we wait for a response for this
                association = itemSensation.getAssociation(sensation=spoke_voiceSensation)
                communicationItem = Communication.CommunicationItem(sensation = itemSensation,
                                                                    voiceSensation = spoke_voiceSensation,
                                                                    time = systemTime.time(),
                                                                    association = association)
                self.communicationItems.append(communicationItem)
                # test
                timer = threading.Timer(interval=Communication.TEST_RESPONSE_TIME, function=self.stopWaitingResponse, args = (communicationItem,))
                communicationItem.setTimer(timer=timer)
                # real
                #timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
                timer.start()
                # for this long
                    
                # TODO We should wait answer and communicate as long other part wants
                return True
        return False
        
    # TODO
    def stopWaitingResponse(self, communicationItem):
        print("We did not get response. Do something!")
 
        i = 0       
        for commItem in self.communicationItems:
            if  commItem == communicationItem:
                print("commItem.getTimer().cancel() && del self.communicationItems[i]")
                commItem.getTimer().cancel()
                del self.communicationItems[i]
            else:
                print("i=i+1")
                i=i+1
