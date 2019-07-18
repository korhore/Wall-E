'''
Created on 06.06.2019
Updated on 18.07.2019

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
    present = []        # which items are present

    #COMMUNICATION_INTERVAL=30.0     # time window to history 
                                    # for sensations we communicate
    COMMUNICATION_INTERVAL=2.5      # time window to history for test to be run quicker
                                    
    class CommunicationItem():
        
        def __init__(self,
                     name,
                     sensation,
                     time,
                     voiceSensation = None,
                     association = None,
                     timer = None):
            self.sensation = sensation
            self.voiceSensation = voiceSensation
            self.time  = time
            self.association = association
            self.timer = timer
            
        def getName(self):
            return self.name
        def setName(self, name):
            self.name = name
            
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
        self.spokenVoiceSensation = None     #last voice we said
        self.heardVoiceSensation = None      #last voice we heard

        self.timer=None
        self.usedVoices = []    # Voices we have used in this conversation
                                # always say something, that we have not yet said
        
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
 
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        # don't communicate with history Sensation Items, we are communicating Item.name just seen.
        self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
        self.log(logLevel=Robot.LogLevel.Normal, logStr="process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
        if sensation.getSensationType() == Sensation.SensationType.Item and\
            systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL:
            self.presence(name=sensation.getName(), presence=sensation.getPresence())
             # communication is not going on item.name is comes
            if len(self.communicationItems) == 0 and\
               (sensation.getPresence() == Sensation.Presence.Entering or sensation.getPresence() == Sensation.Presence.Present) :
                self.startSpeaking()#itemSensation=sensation)
            # else maybe change in prent iterms, no neet other way thankeep prack pn prent items
        elif sensation.getSensationType() == Sensation.SensationType.Voice and\
            sensation.getDirection() == Sensation.Direction.Out and\
            systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
            len(self.communicationItems) > 0: # commucation going and we got a response, nice
#             print("systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
#             print(str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
            # get best response for this response, but do not respond voice with same just heard voice
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            # We want to remember this voice
            sensation.setMemory(memory=Sensation.Memory.LongTerm)
            # don't use this voice in this same conversation
            self.usedVoices.append(sensation)
            
            # cancel timers and mark good feeling to voice we said
            for communicationItem in self.communicationItems:
                if sensation.getTime() > communicationItem.getTime():               # is this a response
                    #communicationItem.getTimer().cancel()                           # cancel last timer
                    communicationItem.getAssociation().changeFeeling(positive=True) #last voice was a good one because we got a response
                    # heard voice is also as good
                    # create new voice we remember
                    communicationItem.getSensation().associate(sensation=sensation,
                                                               feeling=communicationItem.getAssociation().getFeeling(),
                                                               score=communicationItem.getAssociation().getScore())
            # TODO get new responce and speak and set timer
            # TODO get new list of sensationsItems we are speaking
            # TODO get new responce and speak and set timer
            # TODO same logic than when starting new conversation with a new item
            
            self.startSpeaking()#itemSensation=sensation)


#             responceVoiceSensation=None                 
#             voiceSensation=self.getBestResponse()
#             score=0.0
#             if voiceSensation is not None:
#                 score = voiceSensation.getScore()
#                 responceVoiceSensation = Sensation.create(sensation = voiceSensation)
#     #           # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
#                 responceVoiceSensation.setDirection(Sensation.Direction.In) # speak
#                 responceVoiceSensation.setMemory(Sensation.Memory.Sensory)
#                 
#             i = 0
#             new_communicationItems=[]
#             for communicationItem in self.communicationItems:
#                 if sensation.getTime() > communicationItem.getTime():               # is this a response
#                     communicationItem.getTimer().cancel()                           # cancel last timer
#                     communicationItem.getAssociation().changeFeeling(positive=True) #last voice was a good one because we got a response
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: voice of feeling even better  ' + communicationItem.getVoiceSensation().toDebugStr())
#                     if responceVoiceSensation is not None:
#                         # update communicationItem
#                         feeling = communicationItem.getAssociation().getFeeling()
#                         communicationItem.getSensation().associate(voiceSensation,
#                                                                    score=score,
#                                                                    feeling=feeling)
#                         communicationItem.getSensation().associate(responceVoiceSensation,
#                                                                    score=score,
#                                                                    feeling=feeling)
#                         association = communicationItem.getSensation().getAssociation(sensation=responceVoiceSensation)
#                         assert(association != None)
#                         
#                         new_communicationItem = Communication.CommunicationItem(name = communicationItem.getSensation().getName(),
#                                                                                 sensation = communicationItem.getSensation(),
#                                                                                 voiceSensation = responceVoiceSensation,
#                                                                                 time = systemTime.time(),
#                                                                                 association = association)
#                         new_communicationItems.append(new_communicationItem)
#                         
#                         del self.communicationItems[i]
#                 else:
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr="process: i=i+1")
#                     i = i+1
#             # speak once for all items in discussion
#             if len(new_communicationItems) > 0 and responceVoiceSensation is not None:
#                 self.log('Communication.process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=responceVoiceSensation)')
#                 self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=responceVoiceSensation)
#                 self.usedVoices.append(responceVoiceSensation)
#                                     
#                 for new_communicationItem in new_communicationItems:
#                     # when all is set, start new timers
#                     timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse, args = (new_communicationItem,))
#                     new_communicationItem.setTimer(timer=timer)
#                     timer.start()
#                     self.communicationItems.append(new_communicationItem)

                    
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not Item or Voice ' + sensation.toDebugStr())
            
    def presence(self, name, presence):
        if presence == Sensation.Presence.Entering or presence == Sensation.Presence.Present:
            if name not in Communication.present:
                Communication.present.append(name)
        elif presence == Sensation.Presence.Absent:
            i = 0
            for n in Communication.present:
                if n == name:
                    del Communication.present[i]
                else:
                    i=i+1

    '''
    response
    Say something, when we know Item.name's that are present.
    In this starting version we don't care what was said before, except
    what we have said, but because we don't have any clue, what is meaning of the
    speach, or even what Item.names can really speak,
    we just use statistical methods to guess, how we can keep on conversation
    on. We start to speak with voices heard, when best score
    - identification Item.name as Image was happened.
    We set feeling, when we get a response.
    By those methods we can set Importance of Voices
    '''
    def startSpeaking(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking')#: Item Sensation ' + itemSensation.toDebugStr())
        startedAlready = False
        mostImportantItemSensation = None
        voiceSensation = None
        del self.communicationItems[:]  #clear old list
        for name in Communication.present:
            candidate_for_communication, candidate_for_voice = \
                Sensation.getMostImportantSensation( sensationType = Sensation.SensationType.Item,
                                                     name = name,
                                                     notName = None,
                                                     timemin = None,
                                                     timemax = None,
                                                     associationSensationType=Sensation.SensationType.Voice,
                                                     #ignoredSensations = []) # TESTING
                                                     ignoredSensations = self.usedVoices)
            if mostImportantItemSensation is None or\
               (candidate_for_communication is not None and\
               candidate_for_communication.getImportance() > mostImportantItemSensation.getImportance()):
                mostImportantItemSensation = candidate_for_communication
                voiceSensation = candidate_for_voice
            if candidate_for_communication is not None:
                communicationItem = Communication.CommunicationItem(name = name,
                                                                    sensation = candidate_for_communication,
                                                                    time = systemTime.time())
                self.communicationItems.append(communicationItem)
        if mostImportantItemSensation is not None:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: Sensation.getMostImportantSensation did find mostImportantItemSensation OK')
            spoke_voiceSensation = Sensation.create(sensation = voiceSensation)
            # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
            spoke_voiceSensation.setDirection(Sensation.Direction.In)  # speak        
            spoke_voiceSensation.setMemory(Sensation.Memory.Sensory)
            association = mostImportantItemSensation.getAssociation(sensation = voiceSensation)
 
            # keep track what we said to whom
            for communicationItem in self.communicationItems:
                spoke_voiceSensation.associate(sensation = communicationItem.getSensation(),
                                               score=association.getScore(),
                                               feeling=association.getFeeling())
                communicationItem.setAssociation(association=communicationItem.getSensation().getAssociation(spoke_voiceSensation))
            self.usedVoices.append(spoke_voiceSensation)                    
            self.usedVoices.append(voiceSensation)   
            # speak                 
            self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=spoke_voiceSensation)
            # wait response
            self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
            self.timer.start()
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: Sensation.getMostImportantSensation did NOT find mostImportantItemSensation')
#                 
#             itemSensation.associate(sensation = voiceSensation,
#                                     score = itemSensation.getScore())
#             itemSensation.associate(sensation = spoke_voiceSensation,
#                                     score = itemSensation.getScore())
#                 
#         for communicationItem in self.communicationItems:
#             if communicationItem.getSansation.getName() == itemSensation.getName():
#                 startedAlready = True
#         if startedAlready:
#             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: already started communication')
#         else:
#             candidate_for_communication = Sensation.getMostImportantSensation( sensationType = Sensation.SensationType.Item,
#                                                                                name = itemSensation.getName(),
#                                                                                notName = None,
#                                                                                timemin = None,
#                                                                                timemax = None,
#                                                                                associationSensationType=Sensation.SensationType.Voice,
#                                                                                ignoredSensations = []) # TESTING
#                                                                                #ignoredSensations = self.usedVoices)
#             if candidate_for_communication is not None:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: Sensation.getMostImportantSensation did find candidate_for_communication OK')
#                 # get best Voice
#                 voiceSensation = None
#                 for association in candidate_for_communication.getAssociations():
#                     if association.getSensation().getSensationType() == Sensation.SensationType.Voice and\
#                        association.getSensation() not in self.usedVoices:
#                         if voiceSensation is None or association.getImportance() > voiceSensation.getImportance():
#                             voiceSensation = association.getSensation()
#                             
#                 self.usedVoices.append(spoke_voiceSensation)                    
#                 self.usedVoices.append(voiceSensation)   
#                 # speak                 
#                 self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=spoke_voiceSensation)
# 
#                 if voiceSensation is not None:
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: found voiceSensation OK')
#                     # create new Voice to speak and associate it to this sensation so
#                     # we remember that we spoke it now
#     #                association = Sensation.Association(sensation=sensation,
#     #                                                         score=voiceSensation.getScore())
#                     spoke_voiceSensation = Sensation.create(sensation = voiceSensation)
#     #                # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
#                     spoke_voiceSensation.setDirection(Sensation.Direction.In)  # speak
#                     spoke_voiceSensation.setMemory(Sensation.Memory.Sensory)
#                     spoke_voiceSensation.associate(sensation = voiceSensation,
#                                                    score=voiceSensation.getScore())
#                     itemSensation.associate(sensation = voiceSensation,
#                                             score = itemSensation.getScore())
#                     itemSensation.associate(sensation = spoke_voiceSensation,
#                                             score = itemSensation.getScore())
#         
#                     self.log('Communication.process: self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=spoke_voiceSensation)')
#         
#                     self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=spoke_voiceSensation)
#                     self.usedVoices.append(spoke_voiceSensation)                    
#                     self.usedVoices.append(voiceSensation)                    
#                     # now we wait for a response for this
#                     association = itemSensation.getAssociation(sensation=spoke_voiceSensation)
#                     communicationItem = Communication.CommunicationItem(name = itemSensation.getName(),
#                                                                         sensation = itemSensation,
#                                                                         voiceSensation = spoke_voiceSensation,
#                                                                         time = systemTime.time(),
#                                                                         association = association)
#                     self.communicationItems.append(communicationItem)
#                     timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse, args = (communicationItem,))
#                     communicationItem.setTimer(timer=timer)
#                     timer.start()
#                 else:
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: did not find voiceSensation and can\'t start communication')
#                     
#             else:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: Did not find Sensation.getMostImportantSensation! Can\'t start communication!')
                
    '''
    Get common best response for response of items we are discussing, but don't know which one is speaking
    '''          
    def getBestResponse(self, sensation):
        responceVoiceSensation=None
        for communicationItem in self.communicationItems:
            if sensation.getTime() > communicationItem.getTime():   # is this a response
                candidate_for_communication = Sensation.getMostImportantSensation( sensationType = Sensation.SensationType.Item,
                                                                                   name = communicationItem.getSensation().getName(),
                                                                                   notName = None,
                                                                                   timemin = None,
                                                                                   timemax = None,
                                                                                   associationSensationType=Sensation.SensationType.Voice,
                                                                                   ignoredSensations = []) # TESTING
                                                                                   #ignoredSensations = self.usedVoices)
                if candidate_for_communication is not None:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process getBestResponse: Sensation.getMostImportantSensation did find candidate_for_communication OK')
                    # get best Voice
                    for association in candidate_for_communication.getAssociations():
                        if association.getSensation().getSensationType() == Sensation.SensationType.Voice and\
                           association.getSensation() not in self.usedVoices:
                            if responceVoiceSensation is None or association.getSensation().getImportance() > responceVoiceSensation.getImportance():
                                responceVoiceSensation = association.getSensation()
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process getBestResponse: found responceVoiceSensation OK')
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process getBestResponse: Sensation.getMostImportantSensation did not find anything')

        if responceVoiceSensation ==None:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process getBestResponse: Did not find response! Can\'t continue communication!')
        return responceVoiceSensation

        
    #def stopWaitingResponse(self, communicationItem):
    def stopWaitingResponse(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
 
#        i = 0       
        for commItem in self.communicationItems:
            commItem.getAssociation().changeFeeling(positive=False, negative=True)
        del self.communicationItems[:]  #clear old list
#         self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: del self.usedVoices[:]")
        del self.usedVoices[:]          # clear used voices, communication is ended
#             if  commItem == communicationItem:
#                 self.log("stopWaitingResponse: commItem.getAssociation().changeFeeling(negative=True)")
#                 commItem.getAssociation().changeFeeling(positive=False, negative=True)
#                 self.log("stopWaitingResponse: commItem.getTimer().cancel() && del self.communicationItems[i]")
#                 commItem.getTimer().cancel()
#                 del self.communicationItems[i]
#             else:
#                 print("stopWaitingResponse: NEVER should go here i=i+1")
#                 i=i+1
#         if len(self.communicationItems) == 0:   # conversation is ended
#             self.usedVoices = []                # we are free to use voices used at ended conversations
