'''
Created on 06.06.2019
Updated on 03.08.2019

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

    COMMUNICATION_INTERVAL=30.0     # time window to history 
                                    # for sensations we communicate
    #COMMUNICATION_INTERVAL=2.5     # time window to history for test to be run quicker
                                    
    class CommunicationItem():
        
        def __init__(self,
                     name,
                     sensation,
                     time,
                     association = None):
            self.name = name
            self.sensation = sensation
            self.time = time
            self.association = association
            
        def getName(self):
            return self.name
        def setName(self, name):
            self.name = name
            
        def getSensation(self):
            return self.sensation
        def setSensation(self, sensation):
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
        self.present_items={}
        self.lastItemTime=None

        self.communicationItems = []
        self.mostImportantItemSensation = None      # current most important item in conversation
        self.mostImportantVoiceAssociation  = None  # current association most important voice, item said in some previous conversation
                                                    # but not in this conversation
        self.mostImportantVoiceSensation  = None    # current most important voice, item said in some previous conversation
                                                    # but not in this conversation
        self.spokedVoiceSensation = None           # last voice we have said

        self.timer=None
        self.usedVoices = []    # Voices we have used in all conversations
                                # always say something, that we have not yet said
        self.heardVoices = []    # Voices we have used in this conversation        
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
        if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL:
            if sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemory() == Sensation.Memory.LongTerm and\
               sensation.getDirection() == Sensation.Direction.Out:
                isNewItemName = self.tracePresents(sensation)
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' present now' + self.presenceToStr())
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' communicates now with ' + self.communicationItemsToStr())
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' joined to communication')
                # communication is not going on item.name is comes
                if len(self.communicationItems) == 0:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: starting new communication with ' +sensation.getName())
                    self.startSpeaking()#itemSensation=sensation)
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' joined to communication, but don\'t know if heard previous voices. wait someone to speak')
                # else maybe change in present iterms, no need other way than keep track on prent items
            elif sensation.getSensationType() == Sensation.SensationType.Voice and\
                 sensation.getDirection() == Sensation.Direction.Out and\
                 sensation not in self.heardVoices and\
                 systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
                 len(self.communicationItems) > 0: # communication going and we got a response, nice
                if self.timer is not None:
                    self.timer.cancel()
                    self.timer = None
                # We want to remember this voice
                sensation.setMemory(memory=Sensation.Memory.LongTerm)
                # don't use this voice in this same conversation
                self.usedVoices.append(sensation)
                self.heardVoices.append(sensation)
                
                #  mark good feeling to voice we said
                if self.mostImportantVoiceAssociation is not None:
                    self.mostImportantVoiceAssociation.changeFeeling(positive=True) #last voice was a good one because we got a response
                for communicationItem in self.communicationItems:
                    if sensation.getTime() > communicationItem.getTime():               # is this a response
                        communicationItem.getAssociation().changeFeeling(positive=True) #last voice was a good one because we got a response
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(communicationItem.getSensation().getTime()) + ' '  + communicationItem.getSensation().toDebugStr() + ' feeling for voice '+ str(communicationItem.getAssociation().getFeeling()))
                        # heard voice is also as good
                        # create new voice we remember
                        communicationItem.getSensation().associate(sensation=sensation,
                                                                   feeling=communicationItem.getAssociation().getFeeling(),
                                                                   score=communicationItem.getAssociation().getScore())
                if len(self.present_items) > 0:          
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.presenceToStr())
                    self.startSpeaking()
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: not Item or RESPONSE Voice in communication ' + sensation.toDebugStr())
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation ' + sensation.toDebugStr())
            
    def presenceToStr(self):
        namesStr=''
        for name, sensation in self.present_items.items():
            namesStr = namesStr + ' ' + name
        return namesStr
            
    def communicationItemsToStr(self):
        namesStr=''
        for communicationItem in self.communicationItems:
            namesStr = namesStr + ' ' + communicationItem.getName()
        return namesStr
        

    '''
    Response:
    Say something, when we know Item.name's that are present.
    In this starting version we don't care what was said before, except
    what we have said, but because we don't have any clue, what is meaning of the
    speak, or even what Item.names can really speak,
    we just use statistical methods to guess, how we can keep on conversation
    on. We start to speak with voices heard, when best score
    - identification Item.name as Image was happened.
    We set feeling, when we get a response.
    By those methods we can set Importance of Voices
    '''
    def startSpeaking(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking')
        startedAlready = False
        self.mostImportantItemSensation = None
        self.mostImportantVoiceAssociation  = None
        self.mostImportantVoiceSensation  = None
        self.spokedVoiceSensation = None
        del self.communicationItems[:]  #clear old list
        candidate_communicationItems = []
        for name, sensation in self.present_items.items():
            candidate_for_communication, candidate_for_association, candidate_for_voice = \
                Sensation.getMostImportantSensation( sensationType = Sensation.SensationType.Item,
                                                     name = name,
                                                     notName = None,
                                                     timemin = None,
                                                     timemax = None,
                                                     associationSensationType=Sensation.SensationType.Voice,
                                                     #ignoredSensations = []) # TESTING
                                                     ignoredSensations = self.usedVoices)
            if self.mostImportantItemSensation is None or\
               (candidate_for_communication is not None and\
               candidate_for_communication.getImportance() > self.mostImportantItemSensation.getImportance()):
                self.mostImportantItemSensation = candidate_for_communication
                self.mostImportantVoiceAssociation = candidate_for_association
                self.mostImportantVoiceSensation  = candidate_for_voice
            # if this name is capable to speak (has something to say)
            if candidate_for_communication is not None:
                communicationItem = Communication.CommunicationItem(name = name,
                                                                    sensation = candidate_for_communication,
                                                                    time = systemTime.time())
                candidate_communicationItems.append(communicationItem)
        if self.mostImportantItemSensation is not None:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: Sensation.getMostImportantSensation did find self.mostImportantItemSensation OK')
            self.spokedVoiceSensation = Sensation.create(sensation = self.mostImportantVoiceSensation, kind=self.getKind() )
            # test
            #self.spokedVoiceSensation = self.mostImportantVoiceSensation
            # NOTE This is needed now, because Sensation.create parameters direction and memory parameters are  overwritten by sensation parameters
            self.spokedVoiceSensation.setKind(self.getKind())
            self.spokedVoiceSensation.setDirection(Sensation.Direction.In)  # speak        
            self.spokedVoiceSensation.setMemory(Sensation.Memory.Sensory)
            association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation )
 
            # keep track what we said to whom
            for communicationItem in candidate_communicationItems:
                self.spokedVoiceSensation.associate(sensation = communicationItem.getSensation(),
                                               score=association.getScore(),
                                               feeling=association.getFeeling())
                communicationItem.setAssociation(association=communicationItem.getSensation().getAssociation(self.spokedVoiceSensation))
            self.usedVoices.append(self.spokedVoiceSensation)                    
            self.usedVoices.append(self.mostImportantVoiceSensation )   
            # speak                 
            self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceSensation)
            # wait response
            self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
            self.timer.start()
            self.communicationItems = candidate_communicationItems
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process startSpeaking: Sensation.getMostImportantSensation did NOT find self.mostImportantItemSensation')
               
        
    def stopWaitingResponse(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
 
        if self.mostImportantVoiceAssociation is not None:
            self.mostImportantVoiceAssociation.changeFeeling(positive=False, negative=True) #last voice was a bad one because we did not get a response
        # feel disappointed or worse about this voice, so we don't use this again easily
        if self.mostImportantVoiceAssociation.getFeeling() > Sensation.Association.Feeling.Disappointed:
            self.mostImportantVoiceAssociation.setFeeling(Sensation.Association.Feeling.Disappointed)
            
        for communicationItem in self.communicationItems:
            communicationItem.getAssociation().changeFeeling(positive=False, negative=True)
            # feel disappointed or worse about this voice, so we don't use this again easily
            if communicationItem.getAssociation().getFeeling() > Sensation.Association.Feeling.Disappointed:
                communicationItem.getAssociation().setFeeling(Sensation.Association.Feeling.Disappointed)
            self.log(logLevel=Robot.LogLevel.Normal, logStr='stopWaitingResponse: ' + systemTime.ctime(communicationItem.getSensation().getTime()) + ' '  + communicationItem.getSensation().toDebugStr() + ' feeling for voice '+ str(communicationItem.getAssociation().getFeeling()))
        del self.communicationItems[:]  #clear old list
#         self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: del self.usedVoices[:]")
        #del self.usedVoices[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
        del self.heardVoices[:]                          # clear heard voices, communication is ended, so used voices are free to be used in next conversation. 
        self.mostImportantItemSensation = None          # no current voice and item, because no current conversation
        self.mostImportantVoiceAssociation = None
        self.mostImportantVoiceSensation = None
        self.spokedVoiceSensation = None
        self.timer = None
        
    def tracePresents(self, sensation):
        # present means pure Present, all other if handled not present
        isNewItemName = False
        if self.lastItemTime is None or sensation.getTime() > self.lastItemTime:    # sensation should come in order
            self.lastItemTime = sensation.getTime()

            if sensation.getPresence() == Sensation.Presence.Entering or\
               sensation.getPresence() == Sensation.Presence.Present:
                isNewItemName = sensation.getName() not in self.present_items
                self.present_items[sensation.getName()] = sensation
                self.log(logLevel=Robot.LogLevel.Normal, logStr="entering or present " + sensation.getName())

            else:
                if sensation.getName() in self.present_items:
                    del self.present_items[sensation.getName()]
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="absent " + sensation.getName())
        return  isNewItemName
