'''
Created on 06.06.2019
Updated on 29.03.2021

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
   
TODO tests for
- isConversationDelay
- isNoResponseToSay


'''
import time as systemTime
from enum import Enum
import threading 
#import random
import traceback

from Robot import Robot
from Sensation import Sensation
from Config import Config
#from Robot import LogLevel as LogLevel
# We cannot import Robot, because Robot import us,
# so we must duplicate Robot.LogLevel definition here
from enum import Enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Communication(Robot):

    # Communication is statefull,
    # always in one of these states    
    CommunicationState = enum(NotStarted = 'n',
                              Waiting = 'w',
                              On ='o',
                              NoResponseToSay='n',
                              Ended ='e',
                              Delay = 'd')
    CommunicationLogLevel = enum(No=-1, Critical=0, Error=1, Normal=2, Detailed=3, Verbose=4)


    COMMUNICATION_INTERVAL=30.0     # time window to history 
                                    # for sensations we communicate
    CONVERSATION_INTERVAL=300.0     # if no change in present item.names and
                                    # last conversation is ended, how long
                                    # we wait until we will respond if
                                    # someone speaks
    SEARCH_LENGTH=10                # How many response voices we check
    IGNORE_LAST_HEARD_SENSATIONS_LENGTH=20 #5 Optimize this
                                    # How last heard voices we ignore in this conversation, when
                                    # we search best voices to to response to voices
                                    # This mast be >= 1 for sure, otherwise we are echo
                                    # but probably >=2, otherwise we are parrot
    ROBOT_RESPONSE_MAX = 6          # How many times we response to a Robot in one conversation
    
    '''
    base
    class Conversation implements generic conversation
    '''
    
    class Conversation(object):
        def __init__(self,
                     robot,
                     location=None):
            self.robot=robot
            self.location=location  # single location, NOT array
                                    
            self.lastConversationEndTime = None
            self._isConversationOn = False
            self._isConversationEnded = False
            self._isConversationDelay = False
            self._isNoResponseToSay = False
    
            self.communicationState = Communication.CommunicationState.Waiting
            
            self.spokedSensations = None                # Sensations that we last said to other side 
            self.spokedAssociations = None              # Associations that spoked Sensations were assigned to Item.name sensations
    
            self.mostImportantItemSensation = None      # current most important item in conversation
            self.mostImportantVoiceAssociation  = None  # current association most important voice, item said in some previous conversation
                                                        # but not in this conversation
            self.mostImportantVoiceSensation = None     # current most important voice, item said in some previous conversation
                                                        # but not in this conversation
            self.mostImportantImageAssociation  = None  # current association most important image, item said in some previous conversation
                                                        # but not in this conversation
            self.mostImportantImageSensation = None     # current most important image, item said in some previous conversation
                                                        # but not in this conversation    
            self.timer=None
            self.spokedDataIds = []                     # Sensations dataIds we have said in this conversation 
            self.heardDataIds = []                      # Sensations dataIds  we have heard in this conversation
            self.robotResponses = 0
            
            
            
        def getRobot(self):
            return self.robot
        def getLocation(self):                           # Not this is Sensation.location(s), not config-file location
            return self.location                        # which is sesction, but thats TODO there, not here, this is fine
        
        # helper, to Robot-class
        def log(self, logStr, logLevel=2):
            # TODO this is hack, import problem Communication.CommunicationLogLevel.Normal):
            self.getRobot().log(logStr="{}:{}".format(self.getLocation(),logStr), logLevel=logLevel)
            
        def getMemory(self):
            return self.getRobot().getMemory()
        
        def getMainNames(self):
            return self.getRobot().getMainNames()
           
        def createSensation(self,
                 log=True,
                 associations = None,
                 sensation=None,
                 bytes=None,
                 id=None,
                 time=None,
                 receivedFrom=[],
                 
                  # base field are by default None, so we know what fields are given and what not
                 sensationType = None,
                 memoryType = None,
                 robotType = None,
                 robot = None,
                 mainNames = None,                 
                 locations =  None,
                 leftPower = None, rightPower = None,                        # Walle motors state
                 azimuth = None,                                             # Walle robotType relative to magnetic north pole
                 x=None, y=None, z=None, radius=None,                        # location and acceleration of Robot
                 hearDirection = None,                                       # sound robotType heard by Walle, relative to Walle
                 observationDirection = None,observationDistance = None,     # Walle's observation of something, relative to Walle
                 filePath = None,
                 data = None,                                                # ALSA voice is string (uncompressed voice information)
                 image = None,                                               # Image internal representation is PIl.Image 
                 calibrateSensationType = None,
                 capabilities = None,                                        # capabilitis of sensorys, robotType what way sensation go
                 name = None,                                                # name of Item
                 score = None,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                 presence = None,                                            # presence of Item
                 kind = None,                                                # kind (for instance voice)
                 firstAssociateSensation = None,                             # associated sensation first side
                 otherAssociateSensation = None,                             # associated Sensation other side
                 feeling = None,                                             # feeling of sensation or association
                 positiveFeeling = None,                                     # change association feeling to more positive robotType if possible
                 negativeFeeling = None):                                    # change association feeling to more negative robotType if possible


        
            return self.getRobot().createSensation(
                 log=log,
                 associations = associations,
                 sensation=sensation,
                 bytes=bytes,
                 id=id,
                 time=time,
                 receivedFrom=receivedFrom,
                 sensationType = sensationType,
                 memoryType=memoryType,
                 robotType=robotType,
                 #robot=robot,
                 mainNames=mainNames,
                 locations=locations,
                 leftPower = leftPower, rightPower = rightPower,
                 azimuth = azimuth,
                 x=x, y = y, z = z, radius=radius,
                 hearDirection = hearDirection,
                 observationDirection = observationDirection, observationDistance = observationDistance,
                 filePath = filePath,
                 data = data,
                 image = image,
                 calibrateSensationType = calibrateSensationType,
                 capabilities = capabilities,
                 name = name,
                 score = score,
                 presence = presence,
                 kind = kind,
                 firstAssociateSensation = firstAssociateSensation,
                 otherAssociateSensation = otherAssociateSensation,
                 feeling = feeling,
                 positiveFeeling=positiveFeeling,
                 negativeFeeling=negativeFeeling)
        def getKind(self):
            return self.getRobot().getKind()
        def getLocations(self):
            return [self.getLocation()]
        def getParent(self):
            return self.getRobot().getParent()
        def getName(self):
            return self.getRobot().getName()
        
   

        '''
        Handle got feedback.
        Feedback can be positive, negative or neutral.
        We stop time, if it is running and populate got feedback
        '''
                    
        def handleGotFeedback(self, positiveFeeling, negativeFeeling):
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            if self.spokedAssociations != None:
                for associations in self.spokedAssociations:
                    for association in associations:
                        firstAssociateSensation = association.getSensation()
                        otherAssociateSensation = association.getSelfSensation()
                                        
                        if positiveFeeling and firstAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                            self.getMemory().setMemoryType(sensation=firstAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
                        if positiveFeeling and otherAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                            self.getMemory().setMemoryType(sensation=otherAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
                                
                        if positiveFeeling:
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice/image feeling with ' + firstAssociateSensation.getName())
                            feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                    firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                    positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                        elif negativeFeeling:
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: bad voice/image feeling with ' + firstAssociateSensation.getName())
                            feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                    firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                    negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way

                        self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                                        
                        # detach
                        firstAssociateSensation.detach(robot=self.getRobot())
                        otherAssociateSensation.detach(robot=self.getRobot())
                        feelingSensation.detach(robot=self.getRobot())
                        
            self.spokedAssociations = None 
                                       
            
        def isThisLocation(self, locations):
            if locations == None or\
               len(locations) == 0:
                return True
            if self.getLocation() == None or\
               len(self.getLocation()) == 0:
                return True
            return self.getLocation() in locations
            
        def isConversationOn(self):
            return self._isConversationOn
            # returnself.mostImportantItemSensation is not None      # when conversaing, we know most important item.name to cerversate with
       
        def isConversationEnded(self):
            return self._isConversationEnded
        
        def isConversationDelay(self):
            return self._isConversationDelay
            
        def isNoResponseToSay(self):
            return self._isNoResponseToSay
    
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
        
        Parameters
        onStart    True, if we start a conversation
                   Now this parameters is meaningless,
                   because we found out, that introducing our Robot
                   makes no sense with same voices it uses anyway.
                   And speaking should be clear so, that when we get
                   answer, it means that our target thinks that
                   our last voice was interesting and positive
        '''
#         def speak(self, onStart=False):
#             # cancel timer, because we got response and try to speak again
#             if self.timer is not None:
#                 self.timer.cancel()
#             self.timer = None
#             
#             if self.spokedAssociations != None:
#                 for associations in self.spokedAssociations:
#                     for association in associations:
#                         association.getSelfSensation().detach(robot=self.getRobot())
#                         association.getSensation().detach(robot=self.getRobot())
#                 self.spokedAssociations = None
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr="speak: self.spokedAssociations = None")
#                        
#             # we try to find out something to say                
#             succeeded=False
#             while not succeeded:
#                 try:
#                     # communicate in all locations this Robot is present, so
#                     # collect first SensationType.name we are communicating
#                     itemSensations = []
#                     names = []
#                     for location in self.getMemory()._presentItemSensations.keys():
#                         for name, sensation in self.getMemory()._presentItemSensations[location].items():
#                             if sensation.getName() not in names:
#                                 names.append(sensation.getName())
#                                 itemSensations.append(sensation)
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='speak with names {}'.format(names))
#                     if len(itemSensations) > 0:  # something found
#                         # the search candidates what we say or/and show next
#                         # We want now sensations and associations that
#                         # have association to one or more SensationType.Itemss thst bame matches
#                         # Sensation.SensationType is Voice or Image
#                         # RobotType is Sense of Communication which RoborMainNames does not match, meaning that it is from foreign Robot 'spoken'
#                         # it is in ignoredDataIds dataId meaning that it is not spoken by us in this conversation
#                         sensations, associations  = self.getMemory().getBestSensations(
#                                                             #allAssociations = False,
#                                                             itemSensations = itemSensations,
#                                                             sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
#                                                             robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
#                                                             robotMainNames = self.getMainNames(),
#                                                             ignoredDataIds=self.spokedDataIds+self.heardDataIds)#,
#                                                             #ignoredVoiceLens=self.ignoredVoiceLens)
#                         if len(sensations) > 0 and len(associations) > 0:
#                             self._isNoResponseToSay = False
#                             for sensation in sensations:
#                                 #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
#                                 assert sensation.getDataId() not in self.spokedDataIds
#                                 self.spokedDataIds.append(sensation.getDataId())   
#     
#                                 sensation.save()     # for debug reasons save voices we have spoken as heard voices and images
#                                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getBestSensations did find sensations, spoke {}'.format(sensation.toDebugStr()))
#     
#                                 #create normal Muscle sensation for persons to be hards
#                                 spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
#                                 # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
#                                 spokedSensation.setKind(self.getKind())
#                                 spokedSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
#                                 #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
#                                 self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
#                                 # speak                 
#                                 self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
#                                 # create Communication sensation for Robots to be 'heard'
#                                 # Robot.createSensation set RobotMainNames
#                                 if self.robotResponses < Communication.ROBOT_RESPONSE_MAX:
#                                     spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
#                                     # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
#                                     spokedSensation.setKind(self.getKind())
#                                     spokedSensation.setRobotType(Sensation.RobotType.Communication)  # 'speak' to Robots       
#                                     #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
#                                     self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
#                                     # speak                 
#                                     self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
#                                     self.robotResponses = self.robotResponses+1
#                                     
#                             self.spokedAssociations = associations
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr="speak: self.spokedAssociations = associations")
#                             # wait response
#                             self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: timer.start()')
#                             self.timer.start()
#                             self._isConversationOn = True
#                             self.communicationState = Communication.CommunicationState.On                                                                            
#                         else:
#                             # We did not find anything to say, but are ready to start new conversation, if someone speaks.
#                             #self._isConversationDelay = True
#                     
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getBestSensations did NOT find Sensation to speak')
#                             self._isNoResponseToSay = True
#                             self.communicationState = Communication.CommunicationState.NoResponseToSay                                             
#                             #self.clearConversation()
#                                    
#                     succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
#                 except AssertionError as e:
#                     self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
#                     raise e
#                 except Exception as e:
#                     self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))
    
        '''
        We did not get response
        '''
            
        def stopWaitingResponse(self):
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
            self.timer = None

            # We are disappointed            
            self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
                            
            self.endConversation()
            self._isConversationDelay = True
    
            
        def clearConversation(self):
            self.detachSpokedAssociations()  
            del self.spokedDataIds[:]            # clear used spoked voices, communication is ended, so used voices are free to be used in next conversation.
            del self.heardDataIds[:]             # clear used heard  voices, communication is ended, so used voices are free to be used in next conversation.
            
        def detachSpokedAssociations(self):     
            if self.spokedAssociations != None:        
                for associations in self.spokedAssociations:
                    for association in associations:
                        association.getSelfSensation().detach(robot=self.getRobot())
                        association.getSensation().detach(robot=self.getRobot())
            self.spokedAssociations = None 
            self.log(logLevel=Robot.LogLevel.Normal, logStr="detachSpokedAssociations self.spokedAssociations = None")
            
        def endConversation(self):
            self.clearConversation()
            self.timer = None
            self.lastConversationEndTime=systemTime.time()
            self._isConversationOn = False
            self._isConversationEnded = True
            self._isConversationDelay = True
            self.communicationState = Communication.CommunicationState.Delay
            self.robotResponses = 0

    '''
    class ConversationWithItem implements conversation
    with a person
    '''
    
    class ConversationWithItem(Conversation):
        def __init__(self,
                     robot,
                     location=None):
            super().__init__(
                     robot,
                     location)
        '''
        implementation for this location
        
        Overridable method to be run just after
        while self.running:
        loop
        '''
            
     
        def process(self, transferDirection, sensation):
            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
            # don't communicate with history Sensation Items, we are communicating Item.name just seen.
            #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
            self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithItem process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
            # accept heard voices and Item.name presentation Item.name changes
            #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
            # TODO enable line below, disabled for testing only
            if (systemTime.time() - sensation.getTime()) < Communication.COMMUNICATION_INTERVAL and\
               self.isThisLocation(sensation.getLocations()) and\
               sensation.getRobotType() == Sensation.RobotType.Sense:
                #  entering to this location
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    if sensation.getPresence() == Sensation.Presence.Entering or\
                       sensation.getPresence() == Sensation.Presence.Present:
                        # or sensation.getPresence() == Sensation.Presence.Exiting):
                        # presence is tracked in MainRobot for all Robots
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got item ' + sensation.toDebugStr())
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='ConversationWithItem process: got item ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr())
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got item ' + sensation.getName() + ' joined to communication')
                        self._isConversationDelay = False   # ready to continue conversation with new Item.name
                        
                        # ask other Robots to say, what we should say to this Item.name
                        if self.getMemory().hasRobotsPresence():
                            askSensation = self.createSensation(sensation = sensation, locations=self.getLocations())
                            # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                            askSensation.setKind(self.getKind())
                            askSensation.setRobotType(Sensation.RobotType.Communication)  # communication to other Robots       
                            self.getMemory().setMemoryType(sensation=askSensation, memoryType=Sensation.MemoryType.Sensory)
                            # speak                 
                            self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=askSensation)
     
                        # now we can say something to the sensation.getName()
                        # even if we have said something so other present ones
                        # this means we need (again)
        
                        # if communication is going on item.name when comes
                        # handle as a response to said voice
                        # because it was as interesting that new iterm.name joins into conversation
                        
                        self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
                        
                        self.speak(onStart=not self.isConversationOn())
                    elif sensation.getPresence() == Sensation.Presence.Absent and\
                         not self.getMemory().hasItemsPresence(location=self.getLocation()):
                        # conversation is on and they have left us without responding
                        # We are disappointed
                        self._isConversationOn = False # present ones are disappeared even if we  head a voice.
                        self.communicationState = Communication.CommunicationState.Waiting
#                         self.robotResponses = 0
                        self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
                        self.endConversation()
                        
                # if a Spoken Voice voice or image
                elif (sensation.getSensationType() == Sensation.SensationType.Voice or sensation.getSensationType() == Sensation.SensationType.Image) and\
                     sensation.getMemoryType() == Sensation.MemoryType.Sensory and\
                     sensation.getRobotType() == Sensation.RobotType.Sense:
                    # don't echo same voice in this conversation
                    self.heardDataIds.append(sensation.getDataId())
                    while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
                        del self.heardDataIds[0]
    
                    # if response in a going on conversation
                    # This is positive feedback
                    if self.isConversationOn():
                        if self.spokedAssociations is not None:
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got response ' + sensation.toDebugStr())
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got response ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr())
                        # If we have still someone to talk, this is posivive beedback
                        if self.getMemory().hasItemsPresence(location=self.getLocation()):        
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().itemsPresenceToStr(location=self.getLocation()))
                            self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                            self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
                            self.speak(onStart=False)
                        else:
                            # No presence, meaning that they left out Robot alone, even if we said something
                            # We are disappointed
                            self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
                            self._isConversationOn = False # present ones are disappeared even if we  head a voice.
                            self.communicationState = Communication.CommunicationState.Waiting
#                             self.robotResponses = 0
    
                    # we have someone to talk with
                    # if time is elapsed, so we can start communicating again with present item.names
                    elif not self.isConversationOn() and\
                        self.getMemory().hasItemsPresence(location=self.getLocation()) and\
                         (not self.isConversationDelay() or\
                          sensation.getTime() - self.lastConversationEndTime > Communication.CONVERSATION_INTERVAL):
                        self._isConversationDelay = False
                        self.robotResponses = 0
                       # we have still someone to talk with and not yet started a conversation at all or
                        # enough time is elapses of last conversation
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got voice as new or restarted conversation ' + sensation.toDebugStr())
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got voice as new or restarted conversation ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr(location=self.getLocation()))
     
                        # We want to remember this voice
                        self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                    
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got voice as restarted conversation ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().itemsPresenceToStr())
                        self.speak(onStart=True)
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: not Item or RESPONSE Voice or Image in communication or too soon from last conversation ' + sensation.toDebugStr())
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: too old sensation, not heard voice or image of detected item or no present Items ' + sensation.toDebugStr())
            
            sensation.detach(robot=self.getRobot())    # detach processed sensation

 
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
        
        Parameters
        onStart    True, if we start a conversation
                   Now this parameters is meaningless,
                   because we found out, that introducing our Robot
                   makes no sense with same voices it uses anyway.
                   And speaking should be clear so, that when we get
                   answer, it means that our target thinks that
                   our last voice was interesting and positive
        '''
        def speak(self, onStart=False):
            # cancel timer, because we got response and try to speak again
            if self.timer is not None:
                self.timer.cancel()
            self.timer = None
            
            if self.spokedAssociations != None:
                for associations in self.spokedAssociations:
                    for association in associations:
                        association.getSelfSensation().detach(robot=self.getRobot())
                        association.getSensation().detach(robot=self.getRobot())
                self.spokedAssociations = None
                self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithItem speak: self.spokedAssociations = None")
                       
            # we try to find out something to say                
            succeeded=False
            while not succeeded:
                try:
                    # communicate in all locations this Robot is present, so
                    # collect first SensationType.name we are communicating
                    itemSensations = []
                    names = []
                    for location in self.getMemory()._presentItemSensations.keys():
                        for name, sensation in self.getMemory()._presentItemSensations[location].items():
                            if sensation.getName() not in names:
                                names.append(sensation.getName())
                                itemSensations.append(sensation)
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem speak with names {}'.format(names))
                    if len(itemSensations) > 0:  # something found
                        # the search candidates what we say or/and show next
                        # We want now sensations and associations that
                        # have association to one or more SensationType.Itemss thst bame matches
                        # Sensation.SensationType is Voice or Image
                        # RobotType is Sense of Communication which RoborMainNames does not match, meaning that it is from foreign Robot 'spoken'
                        # it is in ignoredDataIds dataId meaning that it is not spoken by us in this conversation
                        sensations, associations  = self.getMemory().getBestSensations(
                                                            #allAssociations = False,
                                                            itemSensations = itemSensations,
                                                            sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                            robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                            robotMainNames = self.getMainNames(),
                                                            ignoredDataIds=self.spokedDataIds+self.heardDataIds)#,
                                                            #ignoredVoiceLens=self.ignoredVoiceLens)
                        if len(sensations) > 0 and len(associations) > 0:
                            self._isNoResponseToSay = False
                            for sensation in sensations:
                                #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
                                assert sensation.getDataId() not in self.spokedDataIds
                                self.spokedDataIds.append(sensation.getDataId())   
    
                                sensation.save()     # for debug reasons save voices we have spoken as heard voices and images
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process speak: self.getMemory().getBestSensations did find sensations, spoke {}'.format(sensation.toDebugStr()))
    
                                #create normal Muscle sensation for persons to be hards
                                spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
                                # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                spokedSensation.setKind(self.getKind())
                                spokedSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
                                #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                                self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
                                # speak                 
                                self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
                                # create Communication sensation for Robots to be 'heard'
                                # Robot.createSensation set RobotMainNames
                                    
                            self.spokedAssociations = associations
                            self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithItem speak: self.spokedAssociations = associations")
                            # wait response
                            self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process speak: timer.start()')
                            self.timer.start()
                            self._isConversationOn = True
                            self.communicationState = Communication.CommunicationState.On                                                                            
                        else:
                            # We did not find anything to say, but are ready to start new conversation, if someone speaks.
                            #self._isConversationDelay = True
                    
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process speak: self.getMemory().getBestSensations did NOT find Sensation to speak')
                            self._isNoResponseToSay = True
                            self.communicationState = Communication.CommunicationState.NoResponseToSay                                             
                            #self.clearConversation()
                                   
                    succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
                except AssertionError as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='ConversationWithItem process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
                    raise e
                except Exception as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='ConversationWithItem process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))
    


    '''
    class ConversationWithRobot implements conversation
    with a Robot
    '''
    
    class ConversationWithRobot(Conversation):
        def __init__(self,
                     robot,
                     location=None):
            super().__init__(
                     robot,
                     location)
        '''
        implementation for this location
        
        Overridable method to be run just after
        while self.running:
        loop
        '''
            
        # TODO remove feedback etc,
        # This is only consultation what it would say    
        def process(self, transferDirection, sensation):
            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
            # don't communicate with history Sensation Items, we are communicating Item.name just seen.
            #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
            self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithRobot process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
            # accept heard voices and Item.name presentation Item.name changes
            #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
            # TODO enable line below, disabled for testing only
            if (systemTime.time() - sensation.getTime()) < Communication.COMMUNICATION_INTERVAL and\
               self.isThisLocation(sensation.getLocations()) and\
               sensation.getRobotType() == Sensation.RobotType.Communication:
                #  entering to this location
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    if sensation.getPresence() == Sensation.Presence.Entering or\
                       sensation.getPresence() == Sensation.Presence.Present:
                        # or sensation.getPresence() == Sensation.Presence.Exiting):
                        # presence is tracked in MainRobot for all Robots
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got item ' + sensation.toDebugStr())
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='ConversationWithRobot process: got item ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr())
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got item ' + sensation.getName() + ' joined to communication')
                        self._isConversationDelay = False   # ready to continue conversation with new Item.name
                        
                        # now we can say something to the sensation.getName()
                        # even if we have said something so other present ones
                        # this means we need (again)
        
                        # if communication is going on item.name when comes
                        # handle as a response to said voice
                        # because it was as interesting that new iterm.name joins into conversation
                        
#                         self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
                         
                        self.speak(onStart=not self.isConversationOn())
                    elif sensation.getPresence() == Sensation.Presence.Absent and\
                         not self.getMemory().hasItemsPresence(location=self.getLocation()):
                        # conversation is on and they have left us without responding
                        # We are disappointed
                        self._isConversationOn = False # present ones are disappeared even if we  head a voice.
                        self.communicationState = Communication.CommunicationState.Waiting
#                         self.robotResponses = 0
#                         self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
                        #self.endConversation()
                        
#                 # if a Spoken Voice voice or image
#                 elif (sensation.getSensationType() == Sensation.SensationType.Voice or sensation.getSensationType() == Sensation.SensationType.Image) and\
#                      sensation.getMemoryType() == Sensation.MemoryType.Sensory and\
#                      sensation.getRobotType() == Sensation.RobotType.Communication:
#                     # don't echo same voice in this conversation
#                     self.heardDataIds.append(sensation.getDataId())
#                     while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
#                         del self.heardDataIds[0]
#     
#                     # if response in a going on conversation
#                     # This is positive feedback
#                     if self.isConversationOn():
#                         if self.spokedAssociations is not None:
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got response ' + sensation.toDebugStr())
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got response ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr())
#                         # If we have still someone to talk, this is posivive beedback
#                         if self.getMemory().hasItemsPresence(location=self.getLocation()):        
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().itemsPresenceToStr(location=self.getLocation()))
#                             self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
#                             self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
#                             self.speak(onStart=False)
#                         else:
#                             # No presence, meaning that they left out Robot alone, even if we said something
#                             # We are disappointed
#                             self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
#                             self._isConversationOn = False # present ones are disappeared even if we  head a voice.
#                             self.communicationState = Communication.CommunicationState.Waiting
# #                             self.robotResponses = 0
#     
#                     # we have someone to talk with
#                     # if time is elapsed, so we can start communicating again with present item.names
#                     elif not self.isConversationOn() and\
#                         self.getMemory().hasItemsPresence(location=self.getLocation()) and\
#                          (not self.isConversationDelay() or\
#                           sensation.getTime() - self.lastConversationEndTime > Communication.CONVERSATION_INTERVAL):
#                         self._isConversationDelay = False
#                         self.robotResponses = 0
#                        # we have still someone to talk with and not yet started a conversation at all or
#                         # enough time is elapses of last conversation
#                         self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got voice as new or restarted conversation ' + sensation.toDebugStr())
#                         self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got voice as new or restarted conversation ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr(location=self.getLocation()))
#      
#                         # We want to remember this voice
#                         self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
#                     
#                         self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: got voice as restarted conversation ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().itemsPresenceToStr())
#                         self.speak(onStart=True)
#                 else:
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: not Item or RESPONSE Voice or Image in communication or too soon from last conversation ' + sensation.toDebugStr())
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: too old sensation, not heard voice or image of detected item or no present items ' + sensation.toDebugStr())
            
            sensation.detach(robot=self.getRobot())    # detach processed sensation

 
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
        
        Parameters
        onStart    True, if we start a conversation
                   Now this parameters is meaningless,
                   because we found out, that introducing our Robot
                   makes no sense with same voices it uses anyway.
                   And speaking should be clear so, that when we get
                   answer, it means that our target thinks that
                   our last voice was interesting and positive
        '''
        def speak(self, onStart=False):
            # cancel timer, because we got response and try to speak again
            if self.timer is not None:
                self.timer.cancel()
            self.timer = None
            
            if self.spokedAssociations != None:
                for associations in self.spokedAssociations:
                    for association in associations:
                        association.getSelfSensation().detach(robot=self.getRobot())
                        association.getSensation().detach(robot=self.getRobot())
                self.spokedAssociations = None
                self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithRobot speak: self.spokedAssociations = None")
                       
            # we try to find out something to say                
            succeeded=False
            while not succeeded:
                try:
                    # communicate in all locations this Robot is present, so
                    # collect first SensationType.name we are communicating
                    itemSensations = []
                    names = []
                    for location in self.getMemory()._presentItemSensations.keys():
                        for name, sensation in self.getMemory()._presentItemSensations[location].items():
                            if sensation.getName() not in names:
                                names.append(sensation.getName())
                                itemSensations.append(sensation)
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak with names {}'.format(names))
                    if len(itemSensations) > 0:  # something found
                        # the search candidates what we say or/and show next
                        # We want now sensations and associations that
                        # have association to one or more SensationType.Itemss thst bame matches
                        # Sensation.SensationType is Voice or Image
                        # RobotType is Sense of Communication which RoborMainNames does not match, meaning that it is from foreign Robot 'spoken'
                        # it is in ignoredDataIds dataId meaning that it is not spoken by us in this conversation
                        sensations, associations  = self.getMemory().getBestSensations(
                                                            #allAssociations = False,
                                                            itemSensations = itemSensations,
                                                            sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                            robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                            robotMainNames = self.getMainNames(),
                                                            ignoredDataIds=self.spokedDataIds+self.heardDataIds)#,
                                                            #ignoredVoiceLens=self.ignoredVoiceLens)
                        if len(sensations) > 0 and len(associations) > 0:
                            self._isNoResponseToSay = False
                            for sensation in sensations:
                                #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
                                assert sensation.getDataId() not in self.spokedDataIds
                                self.spokedDataIds.append(sensation.getDataId())   
    
                                sensation.save()     # for debug reasons save voices we have spoken as heard voices and images
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak: self.getMemory().getBestSensations did find sensations, spoke {}'.format(sensation.toDebugStr()))
    
                                if self.robotResponses < Communication.ROBOT_RESPONSE_MAX:
                                    spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
                                    # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                    spokedSensation.setKind(self.getKind())
                                    spokedSensation.setRobotType(Sensation.RobotType.Communication)  # 'speak' to Robots       
                                    #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                                    self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
                                    # speak                 
                                    self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
#                                     self.robotResponses = self.robotResponses+1
#                                     
#                             self.spokedAssociations = associations
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithRobot speak: self.spokedAssociations = associations")
#                             # wait response
#                             self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak: timer.start()')
#                             self.timer.start()
#                             self._isConversationOn = True
#                             self.communicationState = Communication.CommunicationState.On                                                                            
#                             if self.robotResponses >= Communication.ROBOT_RESPONSE_MAX:
#                                 # We can't response any more to a Robot
#                                 self._isConversationOn = False # present ones are disappeared even if we  head a voice.
#                                 self.communicationState = Communication.CommunicationState.Waiting
#         #                       # neutreal feedback, meaning that we don't send
#                                 self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
#                                 self.endConversation()
#                         
#                                 self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak: Robot response limit')
                        else:
                            # We did not find anything to say, but are ready to start new conversation, if someone speaks.
                            #self._isConversationDelay = True
                    
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak: self.getMemory().getBestSensations did NOT find Sensation to speak')
                            self._isNoResponseToSay = True
                            self.communicationState = Communication.CommunicationState.NoResponseToSay                                             
                            #self.clearConversation()
                                   
                    succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
                except AssertionError as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='ConversationWithRobot process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
                    raise e
                except Exception as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='ConversationWithRobot process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))
    


    # base class 
    def __init__(self,
                 mainRobot,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        print("We are in Communication, not Robot")
        Robot.__init__(self,
                       mainRobot=mainRobot,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss =  maxRss,
                       minAvailMem = minAvailMem,
                       location = location,
                       config = config)
                
        self.itemConversations={}
        self.robotConversations={}
        if len(self.getLocations()) > 0:
            for location in self.getLocations():
                self.itemConversations[location] =\
                    Communication.ConversationWithItem(robot=self, location=location)
                self.robotConversations[location] =\
                    Communication.ConversationWithRobot(robot=self, location=location)
        else:
            location=''
            self.itemConversations[location] =\
                Communication.ConversationWithItem(robot=self, location=location)
            self.robotConversations[location] =\
                Communication.ConversationWithRobot(robot=self, location=location)

        
    '''
    Overridable method to be run just before
    while self.running:
    loop
    
    Say as isCommunication that this MainRobot is present and ready to Communicate
    with other Robots
    '''
        
    def initRobot(self):
        self.communicationState = Communication.CommunicationState.Waiting
        itemSensation = self.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                            sensationType=Sensation.SensationType.Item,
                                            robotType=Sensation.RobotType.Communication,
                                            name=self.getMainRobot().getName(),
                                            presence=Sensation.Presence.Present,
                                            locations=self.getLocations())    
        # speak                 
        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=itemSensation)

    '''
    Overridable method to be run just after
    while self.running:
    loop
    
    Say as isCommunication that this MainRobot is absent and stops to Communicate
    with other Robots
    '''
        
    def deInitRobot(self):
        itemSensation = self.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                            sensationType=Sensation.SensationType.Item,
                                            robotType=Sensation.RobotType.Communication,
                                            name=self.getMainRobot().getName(),
                                            presence=Sensation.Presence.Absent,
                                            locations=self.getLocations())
        # speak                 
        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=itemSensation)
 
    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
        # don't communicate with history Sensation Items, we are communicating Item.name just seen.
        #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
        self.log(logLevel=Robot.LogLevel.Normal, logStr="process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
        if len(sensation.getLocations()) == 0:
            self.itemConversations[''].process(transferDirection=transferDirection, sensation=sensation)
            self.robotConversations[''].process(transferDirection=transferDirection, sensation=sensation)
        else:
            for location in sensation.getLocations():
                if location in self.itemConversations:
                    self.itemConversations[location].process(transferDirection=transferDirection, sensation=sensation)
                if location in self.robotConversations:
                    self.robotConversations[location].process(transferDirection=transferDirection, sensation=sensation)

        sensation.detach(robot=self)    # detach processed sensation
                

        

