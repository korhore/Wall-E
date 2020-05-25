'''
Created on 06.06.2019
Updated on 24.05.2020

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
import random

from Robot import Robot
from Sensation import Sensation
from Config import Config

class Communication(Robot):

    COMMUNICATION_INTERVAL=30.0     # time window to history 
                                    # for sensations we communicate
    #COMMUNICATION_INTERVAL=15.0     # time window to history for test to be run quicker
    #COMMUNICATION_INTERVAL=2.5     # time window to history for test to be run quicker
    CONVERSATION_INTERVAL=300.0     # if no change in present item.names and
                                    # last conversation is ended, how long
                                    # we wait until we will respond if
                                    # someone speaks
    SEARCH_LENGTH=10                # How many response voices we check
                                    
#                 self.sensation.detach(robot=self.robot)


    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT):
        print("We are in Communication, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss =  maxRss,
                       minAvailMem = minAvailMem)

        self.lastConversationEndTime =None

        self.mostImportantItemSensation = None      # current most important item in conversation
        self.mostImportantVoiceAssociation  = None  # current association most important voice, item said in some previous conversation
                                                    # but not in this conversation
        self.mostImportantVoiceSensation = None     # current most important voice, item said in some previous conversation
                                                    # but not in this conversation
        self.spokedVoiceSensation = None            # last voice we have said

        self.timer=None
        self.usedVoices = []    # Voices we have used in this conversation 
                                # always say something, that we have not yet said
        self.usedVoiceLens = [] # Voices we have used in this conversation 
 
    def process(self, transferDirection, sensation, association=None):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        # don't communicate with history Sensation Items, we are communicating Item.name just seen.
        #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
        self.log(logLevel=Robot.LogLevel.Normal, logStr="process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
        # accept heard voices and Item.name presentation Item.name changes
        #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Ssensory
        if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
           sensation.getRobotType() == Sensation.RobotType.Sense:
            # all kind Items found
            if sensation.getSensationType() == Sensation.SensationType.Item and\
               (sensation.getPresence() == Sensation.Presence.Entering or\
               sensation.getPresence() == Sensation.Presence.Present or\
               sensation.getPresence() == Sensation.Presence.Exiting):
                # presence is tracked in MainRobot for all Robots
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + 'got item ' + sensation.toDebugStr())
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
#                 namesStr = self.communicationItemsToStr(sensation.getName())
#                 if len(namesStr) > 0:
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' communicates now with ' + namesStr)
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' joined to communication')
                # communication is not going on item.name when comes
                #if len(self.communicationItems) == 0:
                if not self.isConversationOn():
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: starting new communication with ' +sensation.getName())
                    self.speak(onStart=True) #itemSensation=sensation)
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' joined to communication, but don\'t know if heard previous voices. wait someone to speak')
                # else maybe change in present items, no need other way than keep track on present items
            # if a Spaken Voice voice
            elif sensation.getSensationType() == Sensation.SensationType.Voice and\
                 sensation.getMemoryType() == Sensation.MemoryType.Sensory and\
                 sensation.getRobotType() == Sensation.RobotType.Sense:
                # if response in a going on conversation 
                if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
                   self.isConversationOn():
#                    len(self.communicationItems) > 0:
                    # we have someone to talk with
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + 'got voice as response ' + sensation.toDebugStr()+ ' from ' + self.mostImportantItemSensation.getName())
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
 
                    if self.timer is not None:
                        self.timer.cancel()
                        self.timer = None
                    # We want to remember this voice
                    #sensation.setMemory(memoryType=Sensation.MemoryType.Working)
                    self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                    # don't use this voice in this same conversation
                    self.usedVoices.append(sensation)
                    self.usedVoiceLens.append(len(sensation.getData()))
                    
                    # mark original item Sensation to be remembered
                    # and also good feeling to the original voice
                    # to this voice will be found again in new conversations
                    if self.mostImportantItemSensation is not None:
                        #self.mostImportantItemSensation.setMemory(memoryType=Sensation.MemoryType.LongTerm)
                        self.getMemory().setMemoryType(sensation=self.mostImportantItemSensation, memoryType=Sensation.MemoryType.LongTerm)
                        # publish opdate to other sites
                        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.mostImportantItemSensation, association=None)
                    if self.mostImportantVoiceSensation is not None:
                        #self.mostImportantVoiceSensation.setMemory(memoryType=Sensation.MemoryType.LongTerm)                
                        self.getMemory().setMemoryType(sensation=self.mostImportantItemSensation, memoryType=Sensation.MemoryType.LongTerm)
                        # publish update to other sites
                        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.mostImportantVoiceSensation, association=None)
                    #  mark also good feeling to original voice we said
#                     if self.mostImportantVoiceAssociation is not None:
#                         self.mostImportantVoiceAssociation.changeFeeling(positive=True) #last voice was a good one because we got a response
                    feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                      firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantVoiceSensation,
                                                      #associateFeeling=communicationItem.getAssociation().getFeeling())
                                                      positiveFeeling=True, locations='')#self.getLocations()) # valid in this location, can be chosen other way
                    self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation, association=None)
                        # TODO
                        
#                     for communicationItem in self.communicationItems:
#                         if sensation.getTime() > communicationItem.getTime():               # is this a response
#                             if communicationItem.getAssociation() is not None:
#                                 communicationItem.getAssociation().changeFeeling(positive=True) #last voice was a good one because we got a response
#                                 # TODO
#                                 self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(communicationItem.getSensation().getTime()) + ' '  + communicationItem.getSensation().toDebugStr() + ' feeling for voice '+ str(communicationItem.getAssociation().getFeeling()))
#                             # heard voice is also as good
#                             # create new voice we remember
#                             if communicationItem.getSensation() is not None and\
#                                 communicationItem.getAssociation() is not None:
#                                 communicationItem.getSensation().associate(sensation=sensation,
#                                                                            feeling=communicationItem.getAssociation().getFeeling())
#                                 # TODO Same as Feeling sensation
#                                 feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
#                                                       firstAssociateSensation=communicationItem.getSensation(), otherAssociateSensation=sensation,
#                                                       associateFeeling=communicationItem.getAssociation().getFeeling())
#                                 self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation, association=None)
                    if len(self.getMemory().presentItemSensations) > 0:          
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().presenceToStr())
                        self.speak(onStart=False)
################
                # we have someone to talk with
                # time is elapsed, so we can start communicating again with present item.names
#                 elif len(self.communicationItems) == 0 and\
                elif not self.isConversationOn() and\
                    len(self.getMemory().presentItemSensations) > 0 and\
                     self.lastConversationEndTime is not None and\
                     sensation.getTime() - self.lastConversationEndTime > 10*self.CONVERSATION_INTERVAL:
                    # we have someone to talk with
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + 'got voice as restarted conversation ' + sensation.toDebugStr())
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
 
#                 if self.timer is not None:
#                     self.timer.cancel()
#                     self.timer = None
                    # We want to remember this voice
                    #sensation.setMemory(memoryType=Sensation.MemoryType.Working)
                    self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                    # don't use this voice in this same conversation
                    self.usedVoices.append(sensation)
                    self.usedVoiceLens.append(len(sensation.getData()))
                
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().presenceToStr())
                    self.speak(onStart=True)
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: not Item or RESPONSE Voice in communication or too soon from last conversation ' + sensation.toDebugStr())
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not heard voice of detected item ' + sensation.toDebugStr())
        
        sensation.detach(robot=self)    # detach processed sensation
        
    def isConversationOn(self):
        return  self.mostImportantItemSensation is not None      # when conversaing, we know most important item.name to cerversate with

                       
#     def communicationItemsToStr(self, name):
#         namesStr=''
#         for communicationItem in self.communicationItems:
#             if name != communicationItem.getName():
#                 namesStr = namesStr + ' ' + communicationItem.getName()
#         return namesStr
        

    '''
    Speak:
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
    def speak(self, onStart=False):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak {}'.format(str(onStart)))
        startedAlready = False
        
        if self.mostImportantItemSensation is not None:
            self.mostImportantItemSensation.detach(robot=self)
        self.mostImportantItemSensation = None
        
        self.mostImportantVoiceAssociation = None
        
        if self.mostImportantVoiceSensation is not None:
            self.mostImportantVoiceSensation.detach(robot=self)
        self.mostImportantVoiceSensation  = None
        
        if self.spokedVoiceSensation is not None:
            self.spokedVoiceSensation.detach(robot=self)
        self.spokedVoiceSensation = None

#         self.releaseCommunicationItems() #detach old list
#         del self.communicationItems[:]  #clear old list
        
        candidate_communicationItems = []
        if onStart and len(self.getMemory().getRobot().voiceSensations) > 0:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: onStart')
            # use randown own voice instead of self.voiceind
            voiceind = random.randint(0, len(self.getMemory().getRobot().voiceSensations)-1)
            self.spokedVoiceSensation = self.createSensation( associations=[], sensation=self.getMemory().getRobot().voiceSensations[voiceind],
                                                              memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, locations=self.getLocations())
            #self.spokedVoiceSensation.setMemoryType(memoryType = Sensation.MemoryType.Sensory)
            #self.spokedVoiceSensation = self.createSensation( associations=[], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, data=data)
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceSensation, association=None) # or self.process
            self.log("speak: Starting with presenting Robot voiceind={} self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation={}".format(str(voiceind), self.spokedVoiceSensation.toDebugStr()))
#             self.voiceind=self.voiceind+1
#             if self.voiceind >= len(self.getMemory().getRobot().voiceSensations):
#                 self.voiceind = 0
            self.usedVoices.append(self.spokedVoiceSensation)
            self.usedVoiceLens.append(len(self.spokedVoiceSensation.getData()))                
               
        # self.getMemory().presentItemSensations can be changed
        succeeded=False
        while not succeeded:
            try:
                for name, sensation in self.getMemory().presentItemSensations.items():
#                     communicationItem = Communication.CommunicationItem(robot=self,
#                                                                         name = name,
#                                                                         sensation = sensation,
#                                                                         time = systemTime.time())
#                     self.communicationItems.append(communicationItem)
                    
                    candidate_for_communication_item, candidate_for_association, candidate_for_voice = \
                        self.getMemory().getMostImportantSensation( sensationType = Sensation.SensationType.Item,
                                                             robotType = Sensation.RobotType.Sense,
                                                             name = name,
                                                             notName = None,
                                                             timemin = None,
                                                             timemax = None,
                                                             associationSensationType=Sensation.SensationType.Voice,
                                                             associationDirection = Sensation.RobotType.Sense,
                                                             #ignoredSensations = []) # TESTING
                                                             ignoredSensations = self.usedVoices,
                                                             ignoredVoiceLens = self.usedVoiceLens,
                                                             searchLength=Communication.SEARCH_LENGTH)
                    if self.mostImportantItemSensation is None or\
                       (candidate_for_communication_item is not None and\
                       candidate_for_communication_item.getImportance() > self.mostImportantItemSensation.getImportance()):
                        self.mostImportantItemSensation = candidate_for_communication_item
                        self.mostImportantVoiceAssociation = candidate_for_association
                        self.mostImportantVoiceSensation  = candidate_for_voice

                if self.mostImportantItemSensation is None:     # if no voices assosiated to present item.names, then any voice will do
                    self.mostImportantItemSensation, self.mostImportantVoiceAssociation, self.mostImportantVoiceSensation = \
                        self.getMemory().getMostImportantSensation( sensationType = Sensation.SensationType.Item,
                                                             robotType = Sensation.RobotType.Sense,
                                                             name = None,
                                                             notName = None,
                                                             timemin = None,
                                                             timemax = None,
                                                             associationSensationType=Sensation.SensationType.Voice,
                                                             associationDirection = Sensation.RobotType.Sense,
                                                             #ignoredSensations = []) # TESTING
                                                             ignoredSensations = self.usedVoices,
                                                             ignoredVoiceLens = self.usedVoiceLens,
                                                             searchLength=Communication.SEARCH_LENGTH)
                succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
            except Exception as e:
                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: ignored exception ' + str(e))
#                  self.releaseCommunicationItems() #detach old list
#                  del self.communicationItems[:]  #clear old list
            
        if (self.mostImportantItemSensation is not None) and (self.mostImportantVoiceSensation is not None):
            self.mostImportantItemSensation.attach(robot=self)         #attach Sensation until speaking is ended based on these voices
            self.mostImportantVoiceSensation.attach(robot=self)
            self.mostImportantVoiceSensation.save()     # for debug reasons save voices we have spoken as heard voices
            
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantSensation did find self.mostImportantItemSensation OK')
            self.spokedVoiceSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
                                                              locations=self.getLocations() )
            self.spokedVoiceSensation.attach(robot=self)         #attach Sensation until speaking is ended based on these voices
            # test
            #self.spokedVoiceSensation = self.mostImportantVoiceSensation
            # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
            self.spokedVoiceSensation.setKind(self.getKind())
            self.spokedVoiceSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
            association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
            self.getMemory().setMemoryType(sensation=self.spokedVoiceSensation, memoryType=Sensation.MemoryType.Sensory)
            # TODO at this point we why present items and voice to be spoken.
            # not needed to associate anything
            if association is not None: # be careful, association can be None, if there is no self.mostImportantVoiceSensation any more
                association.setTime(time=None)  # renew association time, so no-one will delete these sensations and they are marked more important by time
                # keep track what we said to whom
                #for communicationItem in candidate_communicationItems:
#                 for communicationItem in self.communicationItems:
#                     self.spokedVoiceSensation.associate(sensation = communicationItem.getSensation(),
#                                                         feeling=association.getFeeling())
#                     communicationItem.setAssociation(association=communicationItem.getSensation().getAssociation(self.spokedVoiceSensation))
#                     # same as Feeling Sensation
#                     feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
#                                                       firstAssociateSensation=self.spokedVoiceSensation, otherAssociateSensation=communicationItem.getSensation(),
#                                                       associateFeeling=association.getFeeling())
#                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation, association=None)
            self.usedVoices.append(self.spokedVoiceSensation)
            self.usedVoiceLens.append(len(self.spokedVoiceSensation.getData()))      # TODO self.spokedVoiceSensation can be None          
            self.usedVoices.append(self.mostImportantVoiceSensation)   
            self.usedVoiceLens.append(len(self.mostImportantVoiceSensation.getData()))               
            # speak                 
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceSensation, association=None)
            # wait response
            self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
            self.timer.start()
            #self.communicationItems = candidate_communicationItems
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: spoke {}'.format(self.spokedVoiceSensation.toDebugStr()))
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantSensation did NOT find self.mostImportantItemSensation')
            self.endConversation()
               
        
    def stopWaitingResponse(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
        
        if self.mostImportantVoiceSensation is not None and self.mostImportantItemSensation is not None:
        
            feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                    firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantVoiceSensation,
                                                          #associateFeeling=communicationItem.getAssociation().getFeeling())
                                                    negativeFeeling=True, locations='')#self.getLocations()) # valid in this location, can be chosen also other way
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: self.getParent().getAxon().put do")
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation, association=None)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: self.getParent().getAxon().put done")
        
 
#         if self.mostImportantVoiceAssociation is not None:
#             self.mostImportantVoiceAssociation.changeFeeling(positive=False, negative=True) #last voice was a bad one because we did not get a response
#             # TODO
#             # feel disappointed or worse about this voice, so we don't use this again easily
#             if self.mostImportantVoiceAssociation.getFeeling() > Sensation.Feeling.Disappointed:
#                 self.mostImportantVoiceAssociation.setFeeling(Sensation.Feeling.Disappointed)
#             # make also original voice spoken to be more easy to forgotten, when not any more in LongTerm memoryType
#             if self.mostImportantVoiceSensation is not None:
#                 #self.mostImportantVoiceSensation.setMemory(memoryType=Sensation.MemoryType.Sensory)                
#                 self.getMemory().setMemoryType(sensation=self.mostImportantVoiceSensation, memoryType=Sensation.MemoryType.Sensory)
            
#         for communicationItem in self.communicationItems:
#             if communicationItem.getAssociation() is not None:
#                 communicationItem.getAssociation().changeFeeling(positive=False, negative=True)
#                 # TODO
#                 # feel disappointed or worse about this voice, so we don't use this again easily
#                 if communicationItem.getAssociation().getFeeling() > Sensation.Feeling.Disappointed:
#                     communicationItem.getAssociation().setFeeling(Sensation.Feeling.Disappointed)
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='stopWaitingResponse: ' + systemTime.ctime(communicationItem.getSensation().getTime()) + ' '  + communicationItem.getSensation().toDebugStr() + ' feeling for voice '+ str(communicationItem.getAssociation().getFeeling()))
 
        self.endConversation()
        
    def endConversation(self):
        if self.mostImportantItemSensation is not None:
            self.mostImportantItemSensation.detach(robot=self)
        self.mostImportantItemSensation = None
        
        self.mostImportantVoiceAssociation  = None
        
        if self.mostImportantVoiceSensation is not None:
            self.mostImportantVoiceSensation.detach(robot=self)
        self.mostImportantVoiceSensation  = None
        
        if self.spokedVoiceSensation is not None:
            self.spokedVoiceSensation.detach(robot=self)
        self.spokedVoiceSensation = None

#         self.releaseCommunicationItems() #detach old list
#         del self.communicationItems[:]  #clear old list
#         self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: del self.usedVoices[:]")
        del self.usedVoices[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
        del self.usedVoiceLens[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
        self.timer = None
        self.lastConversationEndTime=systemTime.time()
        
#     def releaseCommunicationItems(self):
#         for communicationItem in self.communicationItems:
#              communicationItem.detach()
        

