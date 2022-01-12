'''
Created on 06.06.2019
Updated on 20.12.2021

@author: reijo.korhonen@gmail.com

Communication is a Robot, that communicates association between things.
It is interested about Items and tries to find out how to communicate
with them.

This is NEED implementation for a Robot. Robot has a need to communicate
with an Item.name and it tries to find best way to do it.
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

Communication is a prototype for a job for Robot to understand world around it,
how to behave at seems that it is strong stateful. Robot must keep track
state of a conversation and state of of it, what it has done and how it's
environment responses and to what Robots action response is.

This means that technically we must syncronize Communication, Microphone and
Playback Robots actions with Commmunication state, because default implementation
of MainRobot is fully asyncronous. We can't know status of other Robot's, because
all Robot does it's job as fast as they can, but what is the order of subRobots
job order, we can't know.

This last version utilizes SensationType RobotState, which enables both inform
other Robots about Robot's state and Robot to set Other Robots state. We keep
track of state of the conversation and state of Playback-Robot to know, when it
has done playback for Robots voices to know, what Microphone-Robots heard voices
are responses to what Robot's voices.

Sound complicated, but that way person works, person must know what voice is a
response of what it's own said voice. So fionally we must mi9mic person to act like
a person to find out a picture of conversation world with humans.

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
   
Conversation states are:
 CommunicationNotStarted
 CommunicationWaiting
 CommunicationOn
 CommunicationWaitingVoicePlayed
 CommunicationVoicePlayed
 CommunicationWaitingResponse
 CommunicationResponseHeard
 CommunicationNoResponseHeard
 CommunicationNoResponseToSay
 CommunicationEnded
 
State is changed like this

CommunicationNotStarted
  ->CommunicationWaiting
  
CommunicationOn
 ->CommunicationWaiting

- When new Item presence is detected
- When there is item presence and voice is heard
CommunicationWaiting
 ->CommunicationStarted

- When we start communication we can fins voice to say or not 
CommunicationStarted
-> CommunicationWaitingVoicePlayed
-> CommunicationNoResponseToSay 

 CommunicationWaitingVoicePlayed
 -> CommunicationVoicePlayed
 
- if we hear or nor hear a response
CommunicationVoicePlayed
 -> CommunicationResponseHeard
 -> CommunicationNoResponseHeard
 
CommunicationResponseHeard
-> CommunicationWaitingVoicePlayed
-> CommunicationNoResponseToSay

CommunicationNoResponseHeard
-> CommunicationEnded

CommunicationEnded
-> CommunicationWaiting

CommunicationNoResponseToSay
-> CommunicationEnded

   
TODO tests for
- isNoResponseToSay


'''
import time as systemTime
from enum import Enum
import threading 
#import random
import traceback

# relative import from parent starts
# if mainRobot functionality, then working directory is different than source
# and we should use relative import, adding also parent 
# relative import from parent sys.path
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
# relative import from parent end

from Robot import Robot
from Sensation import Sensation
from Config import Config

#Study
#from Robot import LogLevel as LogLevel
# We cannot import Robot, because Robot import us,0
# so we must duplicate Robot.LogLevel definition here
from enum import Enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Communication(Robot):

    CommunicationLogLevel = enum(No=-1, Critical=0, Error=1, Normal=2, Detailed=3, Verbose=4)


    COMMUNICATION_INTERVAL=60.0     # time window to history 
                                    # for sensations we communicate
    CONVERSATION_INTERVAL=300.0     # if no change in present item.names and
                                    # last conversation is ended, how long
                                    # we wait until we will respond if
                                    # someone speaks
    SEARCH_LENGTH=10                # How many response voices we check
    IGNORE_LAST_HEARD_SENSATIONS_LENGTH=5 #5 Optimize this
                                    # How many last heard voices we ignore in this conversation, when
                                    # we search best voices to to response to voices
                                    # This mast be >= 1 for sure, otherwise we are echo
                                    # but probably >=2, otherwise we are parrot
    IGNORE_LAST_SAID_SENSATIONS_LENGTH=20 #5 Optimize this
                                    # How many last said voices we ignore in this conversation, when
                                    # we search best voices to to response to voices
                                    # This mast be >= 1 for sure, otherwise we are repeat ourselves
    
    ROBOT_RESPONSE_MAX = 6          # How many times we response to a Robot in one conversation
    
#    spokedDataIds = []              # Sensations dataIds we have said
#    heardDataIds = []               # Sensations dataIds  we have heard
    
    '''
    base
    class Conversation implements generic conversation
    '''
    
    class Conversation(object):
        def __init__(self,
                     robot,
                     location=''):
            self.robot=robot
            self.location=location    # local single location, NOT array
                                    
            self.lastConversationEndTime = None
    
            self.robotState = Sensation.RobotState.CommunicationNotStarted # None
#            self.informRobotState(Sensation.RobotState.CommunicationWaiting)
#             robotStateSensation = self.createSensation( associations=None,
#                                                         sensationType=Sensation.SensationType.RobotState,
#                                                         memoryType=Sensation.MemoryType.Sensory,
#                                                         robotState=self.robotState,
#                                                         locations=self.getLocations())
#             self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=robotStateSensation)
           
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
            self.responseTimer=None
            self.spokedDataIds = []                     # Sensations dataIds we have said in this conversation 
            self.heardDataIds = []                      # Sensations dataIds  we have heard in this conversation
#             self.robotResponses = 0
            self.voicesToBePlayed = 0
            
            
            
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
                 negativeFeeling = None,                                     # change association feeling to more negative robotType if possible
                 robotState = None):


        
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
                 negativeFeeling=negativeFeeling,
                 robotState=robotState)
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
            if self.responseTimer is not None:
                self.responseTimer.cancel()
                self.responseTimer = None
            if self.spokedAssociations != None:
                for sensationType in self.spokedAssociations:
                    # for sensationTypeAssociations in self.spokedAssociations[sensationType]:
                    #     for association in sensationTypeAssociations:
                    for association in self.spokedAssociations[sensationType]:
                        # for association in sensationTypeAssociations:
                            firstAssociateSensation = association.getSensation()
                            otherAssociateSensation = association.getSelfSensation()
                                            
                            if positiveFeeling and firstAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                                self.getMemory().setMemoryType(sensation=firstAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
                            if positiveFeeling and otherAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                                self.getMemory().setMemoryType(sensation=otherAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
                                    
                            if positiveFeeling:
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice/image feeling with ' + firstAssociateSensation.getName())
                                feelingSensation = self.createSensation(robotType = Sensation.RobotType.Sense,
                                                                        associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                        firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                        positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                            elif negativeFeeling:
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: bad voice/image feeling with ' + firstAssociateSensation.getName())
                                feelingSensation = self.createSensation(robotType = Sensation.RobotType.Sense,
                                                                        associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                        firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                        negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
    
    #                         self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
    #                         self.getParent().route(transferDirection=Sensation.TransferDirection.Direct, sensation=feelingSensation)
                            self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=feelingSensation)
    
                                            
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
            return self.robotState in [Sensation.RobotState.CommunicationOn,
                                       Sensation.RobotState.CommunicationWaitingVoicePlayed,
                                       Sensation.RobotState.CommunicationVoicePlayed,
                                       Sensation.RobotState.CommunicationWaitingResponse,
                                       Sensation.RobotState.CommunicationResponseHeard,
                                       Sensation.RobotState.CommunicationNoResponseHeard,
                                       Sensation.RobotState.CommunicationNoResponseToSay,
                                       ]
       
        def isWaitingVoiceOrItem(self):
            return not self.robotState in [Sensation.RobotState.CommunicationWaitingVoicePlayed
                                           ]
        def isWaitingWaitingResponse(self):
            return self.robotState in [Sensation.RobotState.CommunicationWaitingResponse
                                      ]
        def isConversationEnded(self):
            return self.robotState in [Sensation.RobotState.CommunicationNotStarted,
                                       Sensation.RobotState.CommunicationWaiting,
                                       Sensation.RobotState.CommunicationEnded,
                                       Sensation.RobotState.CommunicationDelay,
                                       ]
        
        def isConversationDelay(self):
#             return self._isConversationDelay
            return self.robotState is Sensation.RobotState.CommunicationDelay
        
#         def isNoResponseToSay(self):
# #             return self._isNoResponseToSay
#             return self.robotState is Sensation.RobotState.CommunicationNoResponseToSay
    
        '''
        We did not get response
        '''
        def stopWaitingResponse(self):
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
            self.responseTimer = None

            # We are disappointed            
            self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
            self.informRobotState(robotState = Sensation.RobotState.CommunicationNoResponseHeard)
            # conversation is ended
            self.endConversation()
            self._isConversationDelay = True
            
    
            
        def clearConversation(self):
            self.detachSpokedAssociations()
            # Try to use global spokedDataIds
            #del self.spokedDataIds[:]            # clear used spoked voices, communication is ended, so used voices are free to be used in next conversation.
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
            self.responseTimer = None
            self.lastConversationEndTime=systemTime.time()
            if self.getMemory().hasItemsPresence(location=self.getLocation()):
                self.informRobotState(robotState = Sensation.RobotState.CommunicationDelay)

            else:
                self.informRobotState(robotState = Sensation.RobotState.CommunicationEnded)

        '''
        This method is used by Robot.Communication
        it wants sensations and associations that
        - have association to one or more SensationType.Itemss that name matches
        - Sensation.SensationType matches
        - RobotType matches with robotMainNames
        - it's dataId is not in ignoredDataIds
    
        '''    
        def getBestSensations(self,
                              #allAssociations = False,
                              itemSensations,
                              sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                              robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                              robotMainNames = [],
                              ignoredDataIds = [],
                              searchLength = 10):
            # result as dictionaries, key sensationType
            copied_ignoredDataIds = ignoredDataIds[:]   # deep copy, so original lict is not changed
            sensations = {}
            associations = {}
            memorabilitys = {}
    
            # get Sensation.SensationType.Item name's We are seraching associations
            names=[]       
            for sensation in itemSensations:
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    names.append(sensation.getName())
                    
            # check Sensation.SensationType.Item sensations where name matches        
            #  if sensation.getDataId() not in copied_ignoredDataIds and\
            searched = 0
            for name in names:
                if name in self.getMemory().masterItems:
                    for itemSensation in self.getMemory().masterItems[name]:
                        for associtionSensationtype in sensationTypes:
                            for association in itemSensation.getAssociations():
                                sensation = association.getSensation()
                                if sensation.getSensationType() in sensationTypes and\
                                   sensation.getRobotType() in robotTypes and\
                                   sensation.getDataId() not in copied_ignoredDataIds:
                                    hasSensationType = True
                                    if sensation.getRobotType() == Sensation.RobotType.Communication:
                                        isInMainNames = sensation.isInMainNames(mainNames=robotMainNames)
                                        #print("isInMainNames {}".format(isInMainNames))
                                        if sensation.getRobotType() == Sensation.RobotType.Communication and isInMainNames:
                                            hasSensationType = False
                                        #print("hasSensationType {}  isInMainNames {}".format(hasSensationType, isInMainNames))
                                                     
                                    if hasSensationType: # sensation associated to itemSensation is right kind
                                                         # sensation can have many matching Item.nane associations
                                                         # we should accept then all
                                        memorability, sensationAssociations = \
                                                    sensation.getMemorability(
                                                            getAssociationsList = True,
                                                            itemSensations = itemSensations,
                                                            robotMainNames = robotMainNames,
                                                            robotTypes = robotTypes,#[Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                            ignoredDataIds=copied_ignoredDataIds,
                                                            positive = True,
                                                            negative = False,
                                                            absolute = False)
                                        if sensation.getSensationType() not in memorabilitys or\
                                           memorability > memorabilitys[sensation.getSensationType()]:
                                            copied_ignoredDataIds.append(sensation.getDataId())    # We have checked this, so don't check again if found assigned 
                                                                                                   # with other Item
                                            memorabilitys[sensation.getSensationType()] = memorability
                                            sensations[sensation.getSensationType()] = sensation
                                            associations[sensation.getSensationType()] = sensationAssociations
                                            
                                            searched = searched+1
                                            if searched >= searchLength:
                                                return sensations.values(), associations.values()
            
            # return sensations.values(), associations.values()
            return sensations, associations

        '''
        Inform in what robotState this Robot is to other Robots
        '''   
        def informRobotState(self, robotState):
            if self.robotState != robotState:
                # chech sommunication syncronizing
                if robotState == Sensation.RobotState.CommunicationNotStarted:
                    if self.robotState != None:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError
                elif robotState == Sensation.RobotState.CommunicationWaiting:
                    if self.robotState not in [None,
                                               Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationNotStarted,
                                               Sensation.RobotState.CommunicationEnded,
                                               Sensation.RobotState.CommunicationNoResponseToSay,
                                               Sensation.RobotState.CommunicationDelay]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError
                elif robotState == Sensation.RobotState.CommunicationOn:
                    if self.robotState not in [Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationWaiting]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError
                elif robotState == Sensation.RobotState.CommunicationResponseHeard:
                    if self.robotState not in [Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationWaitingResponse]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError
                elif robotState == Sensation.RobotState.CommunicationNoResponseHeard:
                    if self.robotState not in [Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationWaitingResponse]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError                     
                elif robotState == Sensation.RobotState.CommunicationVoicePlayed:
                    if self.robotState not in [Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationWaitingVoicePlayed]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError
                elif robotState == Sensation.RobotState.CommunicationWaitingVoicePlayed:
                    if self.robotState not in [Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationOn,
                                               Sensation.RobotState.CommunicationWaiting,
                                               Sensation.RobotState.CommunicationResponseHeard]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError
                elif robotState == Sensation.RobotState.CommunicationNoResponseToSay:
                    if self.robotState not in [Sensation.RobotState.CommunicationSyncError,
                                               Sensation.RobotState.CommunicationOn,
                                               Sensation.RobotState.CommunicationWaiting,
                                               Sensation.RobotState.CommunicationResponseHeard]:
                        self.log(logLevel=Robot.LogLevel.Error, logStr='ConversationWithItem informRobotState: Cannot change robotState from {} to {}'.format(Sensation.getRobotStateString(robotState=self.robotState),
                                                                                                                                                              Sensation.getRobotStateString(robotState=robotState)))
                        robotState = Sensation.RobotState.CommunicationSyncError

                self.robotState = robotState
                robotStateSensation = self.createSensation(associations=None,
                                                           sensationType=Sensation.SensationType.RobotState,
                                                           memoryType=Sensation.MemoryType.Sensory,
                                                           robotState=robotState,
                                                           locations=self.getLocations())
                self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=robotStateSensation)
    '''
    class ConversationWithItem implements conversation
    with a person
    '''
    
    class ConversationWithItem(Conversation):
        def __init__(self,
                     robot,
                     location=''):
            super().__init__(
                     robot,
                     location)
            self.spokedVoiceSensations=[]
        '''
        process
        
        implementation for this location
        
        Overridable method to be run just after
        while self.running:
        loop
        
        return shouldDelete    True if detected sensation that ca't be processed and
                                should not be saved to Memory, because it is not sure
                                that it is valid voice from environment, nut can be
                                echo of our own voice
        '''
            
     
        def process(self, transferDirection, sensation):
            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: {} {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
            # don't communicate with history Sensation Items, we are communicating Item.name just seen.
            #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
            self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithItem process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
            # accept heard voices and Item.name presentation Item.name changes
            #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
            # TODO enable line below, disabled for testing only
            shouldDelete=False
            
            if (systemTime.time() - sensation.getTime()) < Communication.COMMUNICATION_INTERVAL and\
               self.isThisLocation(locations=sensation.getLocations()) and\
               sensation.getRobotType() == Sensation.RobotType.Sense:
                #  entering to this location
                if sensation.getSensationType() == Sensation.SensationType.Item and\
                   sensation.getMemoryType() == Sensation.MemoryType.Working  :
                    if sensation.getPresence() == Sensation.Presence.Entering or\
                       sensation.getPresence() == Sensation.Presence.Present:
                        # or sensation.getPresence() == Sensation.Presence.Exiting):
                        # presence is tracked in MainRobot for all Robots
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got item ' + sensation.toDebugStr())
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='ConversationWithItem process: got item ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr())
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got item ' + sensation.getName() + ' joined to communication')
                        # ready to continue conversation with new Item.name
                        # TODO is we are not already waiting a response#
                        if self.isWaitingVoiceOrItem() and not self.isWaitingWaitingResponse():
                        #if True:
                            #comment?
                            self.informRobotState(robotState = Sensation.RobotState.CommunicationWaiting)
                            
                            # ask other Robots to say, what we should say to this Item.name
                            if self.getMemory().hasRobotsPresence():
                                askSensation = self.createSensation(sensation = sensation, locations=Robot.GLOBAL_LOCATIONS)
                                # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                askSensation.setKind(self.getKind())
                                askSensation.setRobotType(Sensation.RobotType.Communication)  # communication to other Robots       
                                self.getMemory().setMemoryType(sensation=askSensation, memoryType=Sensation.MemoryType.Sensory)
                                # speak                 
                                self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=askSensation)
                                askSensation.detach(robot=self.getRobot())
        
                            # now we can say something to the sensation.getName()
                            # even if we have said something so other present ones
                            # this means we need (again)
            
                            # if communication is going on item.name when comes
                            # handle as a response to said voice
                            # because it was as interesting that new iterm.name joins into conversation
                            
                            self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
                            
                            self.speak(onStart=not self.isConversationOn())
                    elif sensation.getPresence() == Sensation.Presence.Absent:
                        # if someone is present
                        if self.getMemory().hasItemsPresence(location=self.getLocation()):
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='{} is now absent, but there are others we wait answer'.format(sensation.getName()))
                        else:
                            # no-one is present, no hope someone responses
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='no-one are now present, so we are disappointed')
                            self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
                            self.endConversation()
                        
                # if a Spoken voice Note Item.name == person  can not show us images, Robots can, but they consult, not communicate
                elif sensation.getSensationType() == Sensation.SensationType.Voice and\
                     sensation.getMemoryType() == Sensation.MemoryType.Sensory and\
                     sensation.getRobotType() == Sensation.RobotType.Sense:
                    if self.isWaitingVoiceOrItem and self.isWaitingWaitingResponse():
                        # don't echo same voice in this conversation
                        self.heardDataIds.append(sensation.getDataId())
                        while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
                            del self.heardDataIds[0]
        
                        # if response in a going on conversation
                        # This is positive feedback
                        if self.isWaitingWaitingResponse():
                            if self.spokedAssociations is not None:
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got response ' + sensation.toDebugStr())
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got response ' + sensation.getName() + ' present now' + self.getMemory().itemsPresenceToStr())
                                self.informRobotState(robotState = Sensation.RobotState.CommunicationResponseHeard)
                           # If we have still someone to talk, this is positive feedback
                            if self.getMemory().hasItemsPresence(location=self.getLocation()):        
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().itemsPresenceToStr(location=self.getLocation()))
                                self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                                self.handleGotFeedback(positiveFeeling=True, negativeFeeling=False)
                                self.speak(onStart=False)
                            else:
                                # No presence, meaning that they left out Robot alone, even if we said something
                                # We are disappointed
                                self.handleGotFeedback(positiveFeeling=False, negativeFeeling=True)
                                self.informRobotState(robotState = Sensation.RobotState.CommunicationEnded)
                                self.informRobotState(robotState = Sensation.RobotState.CommunicationWaiting)
         
                        # we have someone to talk with
                        # if time is elapsed, so we can start communicating again with present item.names
                        elif not self.isConversationOn() and\
                            self.getMemory().hasItemsPresence(location=self.getLocation()) and\
                             (not self.isConversationDelay() or\
                              sensation.getTime() - self.lastConversationEndTime > Communication.CONVERSATION_INTERVAL):
    #                         self._isConversationDelay = False
                            # we have still someone to talk with and not yet started a conversation at all or
                            # enough time is elapses of last conversation
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got voice as new or restarted conversation ' + sensation.toDebugStr())
         
                            # We want to remember this voice
                            self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                            
                            self.informRobotState(robotState = Sensation.RobotState.CommunicationOn)
                         
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got voice as restarted conversation got voice and tries to speak with presents ones ' + self.getMemory().itemsPresenceToStr(location=self.getLocation()))
                            self.speak(onStart=True)
                    else:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got voice, which it can\'t  process, because its response is not yet played ' + sensation.toDebugStr())
                        shouldDelete=True
                elif sensation.getSensationType() == Sensation.SensationType.RobotState and sensation.getRobotState() == Sensation.RobotState.CommunicationVoicePlayed:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got CommunicationVoicePlayed')
                    for a in sensation.getAssociations():
                        if  a.getSensation().getSensationType() ==  a.getSensation().SensationType.Voice and\
                            a.getSensation().getMemoryType() == Sensation.MemoryType.Sensory and\
                            a.getSensation().getRobotType() == Sensation.RobotType.Muscle:
                            if a.getSensation() in self.spokedVoiceSensations:
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: got CommunicationVoicePlayed about OUR OWN Voice')
                                self.spokedVoiceSensations.remove(a.getSensation())
                                a.getSensation().detach(robot=self.getRobot()) # to be sure
                                self.voicesToBePlayed -= 1
                                if self.voicesToBePlayed == 0:
                                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: all Voices Played, can start to wait response')
                                    self.informRobotState(robotState=Sensation.RobotState.CommunicationWaitingResponse)
                                    # wait response
                                    self.responseTimer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
                                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process speak: timer.start()')
                                    self.responseTimer.start()
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: not Item or RESPONSE Voice or Image in communication or too soon from last conversation ' + sensation.toDebugStr())
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process: too old sensation, not heard voice or image of detected item or no present Items ' + sensation.toDebugStr())

            return shouldDelete
 
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
            if self.responseTimer is not None:
                self.responseTimer.cancel()
            self.responseTimer = None
            #self.robotState = None # we reset self.robotState to be sure, that we give feedback how we succeeded
            
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
                        #sensations, associations  = self.getBestSensations(
                        sensations, associations  = self.getBestSensations(
                                                            #allAssociations = False,
                                                            itemSensations = itemSensations,
                                                            sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                            robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                            robotMainNames = self.getMainNames(),
                                                            ignoredDataIds=self.spokedDataIds+self.heardDataIds)
                                                            #ignoredVoiceLens=self.ignoredVoiceLens)
                        if len(sensations) > 0 and len(associations) > 0 and Sensation.SensationType.Voice in sensations:
                            self._isNoResponseToSay = False
                            for sensationType in sensations:#.keys():
                                sensation = sensations[sensationType]
                                #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
                                assert sensation.getDataId() not in self.spokedDataIds
                                while len(self.spokedDataIds) > Communication.IGNORE_LAST_SAID_SENSATIONS_LENGTH:
                                    del self.spokedDataIds[0]
                                self.spokedDataIds.append(sensation.getDataId())   
        
                                sensation.save()     # for debug reasons save voices we have spoken as heard voices and images
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process speak: self.getBestSensations did find sensations, spoke {}'.format(sensation.toDebugStr()))
        
                                #create normal Muscle sensation for persons to be heard
                                spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
                                # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                spokedSensation.setKind(self.getKind())
                                spokedSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
                                #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                                self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
                                # speak                 
    #                                 self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
    #                                 self.getParent().route(transferDirection=Sensation.TransferDirection.Direct, sensation=spokedSensation)
                                self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=spokedSensation)
                                spokedSensation.detach(robot=self.getRobot()) # to be sure
                                    
                                # if voice, then we wait RobotState message from Playback, that voice is played
                                if spokedSensation.getSensationType() == Sensation.SensationType.Voice and spokedSensation.getRobotType() == Sensation.RobotType.Muscle:
                                    self.voicesToBePlayed += 1
                                    self.informRobotState(robotState=Sensation.RobotState.CommunicationWaitingVoicePlayed)
                                    self.spokedVoiceSensations.append(spokedSensation)
                                else:
                                    spokedSensation.detach(robot=self.getRobot()) # to be sure
                                    
                            self.spokedAssociations = associations
                            
                            self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithItem speak: self.spokedAssociations = associations")
                        else:
                            # We did not find anything to say, but are ready to start new conversation, if someone speaks.
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithItem process speak: self.getBestSensations did NOT find Sensation to speak')
                            self._isNoResponseToSay = True
                            self.informRobotState(robotState = Sensation.RobotState.CommunicationNoResponseToSay)
                                   
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
                     location=''):
            super().__init__(
                     robot=robot,
                     location=location)
            self.robotState = None

        '''
        implementation for this location
        
        Overridable method to be run just after
        while self.running:
        loop
        '''
            
        def process(self, transferDirection, sensation):
            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
            # don't communicate with history Sensation Items, we are communicating Item.name just seen.
            #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
            self.log(logLevel=Robot.LogLevel.Normal, logStr="ConversationWithRobot process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
            # accept heard voices and Item.name presentation Item.name changes
            #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
            # TODO enable line below, disabled for testing only
            if (systemTime.time() - sensation.getTime()) < Communication.COMMUNICATION_INTERVAL and\
               self.isThisLocation(locations=sensation.getLocations()) and\
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
 
                        # consult other robot what we would say in this situation                       
                        
                        self.speak()
                    elif sensation.getPresence() == Sensation.Presence.Absent and\
                         not self.getMemory().hasItemsPresence(location=self.getLocation()):
                        self.informRobotState(robotState = Sensation.RobotState.CommunicationWaiting)
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot process: too old sensation, not present communication item or no present items ' + sensation.toDebugStr())

 
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
        def speak(self):
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
                        #sensations, associations  = self.getBestSensations(
                        sensations, associations  = self.getBestSensations(
                                                            #allAssociations = False,
                                                            itemSensations = itemSensations,
                                                            sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
                                                            robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                            robotMainNames = self.getMainNames())
                        if len(sensations) > 0 and len(associations) > 0 and Sensation.SensationType.Voice in sensations:
                            for sensationType in sensations:#.keys():
                                sensation = sensations[sensationType]
                                sensation.save()     # for debug reasons save voices we have spoken as heard voices and images
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak: self.getBestSensations did find sensations, spoke {}'.format(sensation.toDebugStr()))
                                # speak                                                     self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
                                spokedSensation = self.createSensation(sensation = sensation,
                                                                       robotType = Sensation.RobotType.Communication,
                                                                       memoryType = Sensation.MemoryType.Sensory,
                                                                       locations=Robot.GLOBAL_LOCATIONS)
                                # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                spokedSensation.setRobotType(Sensation.RobotType.Communication)  # 'speak' to Robots
#                                 self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
#                                 self.getParent().route(transferDirection=Sensation.TransferDirection.Direct, sensation=spokedSensation)
                                self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=spokedSensation)
                                spokedSensation.detach(robot=self.getRobot()) # to be sure
                        else:
                            # We did not find anything to say, but are ready to start new conversation, if someone speaks.
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='ConversationWithRobot speak: self.getBestSensations did NOT find Sensation to speak')
                            self.informRobotState(robotState = Sensation.RobotState.CommunicationNoResponseToSay )
                    succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
                except AssertionError as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='ConversationWithRobot process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
                    raise e
                except Exception as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='ConversationWithRobot process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))
    
        '''
        Inform in what robotState this Robot is to other Robots
        '''   
        def informRobotState(self, robotState):
            if self.robotState != robotState: 
                self.robotState = robotState
                robotStateSensation = self.createSensation(associations=None,
                                                           sensationType=Sensation.SensationType.RobotState,
                                                           memoryType=Sensation.MemoryType.Sensory,
                                                           robotState=robotState,
                                                          locations=self.getLocations())
                self.getRobot().route(transferDirection=Sensation.TransferDirection.Direct, sensation=robotStateSensation)


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
                 location='',
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
                
        self.robotConversation = Communication.ConversationWithRobot(robot=self, location='')
        self.itemConversations = {}

        if len(self.getLocations()) > 0:
            for location in self.getLocations():
                self.itemConversations[location] =\
                    Communication.ConversationWithItem(robot=self, location=location)
        else:
            location=''
            self.itemConversations[location] =\
                Communication.ConversationWithItem(robot=self, location=location)

        
    '''
    Overridable method to be run just before
    while self.running:
    loop
    
    Say as isCommunication that this MainRobot is present and ready to Communicate
    with other Robots
    '''
        
    def initRobot(self):
        self.robotState = Sensation.RobotState.CommunicationWaiting
        robotStateSensation = self.createSensation( robotType = Sensation.RobotType.Sense,
                                                    associations=None,
                                                    sensationType=Sensation.SensationType.RobotState,
                                                    memoryType=Sensation.MemoryType.Sensory,
                                                    robotState=self.robotState,
                                                    locations=self.getLocations())
        self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=robotStateSensation)
        itemSensation = self.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                            sensationType=Sensation.SensationType.Item,
                                            robotType=Sensation.RobotType.Communication,
                                            name=self.getMainRobot().getName(),
                                            presence=Sensation.Presence.Present,
                                            locations=self.getLocations())    
        # speak                 
#         self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=itemSensation)
#         self.getParent().route(transferDirection=Sensation.TransferDirection.Direct, sensation=itemSensation)
        self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=itemSensation)

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
#         self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=itemSensation)
        self.route(transferDirection=Sensation.TransferDirection.Direct, sensation=itemSensation)

    def process(self, transferDirection, sensation):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
        # don't communicate with history Sensation Items, we are communicating Item.name just seen.
        #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
        self.log(logLevel=Robot.LogLevel.Normal, logStr="process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
        self.activityNumber += 1
        handledSensation = False
        shouldDelete = False
        if len(sensation.getLocations()) == 0:
            if '' in self.itemConversations:
                shouldDelete = self.itemConversations[''].process(transferDirection=transferDirection, sensation=sensation)
                handledSensation = True
        else:
            if (systemTime.time() - sensation.getTime()) < Communication.COMMUNICATION_INTERVAL:
                if sensation.getRobotType() == Sensation.RobotType.Sense and\
                    (sensation.getSensationType() == Sensation.SensationType.Item or sensation.getSensationType() == Sensation.SensationType.Voice) or\
                    (sensation.getSensationType() == Sensation.SensationType.RobotState and sensation.getRobotState() == Sensation.RobotState.CommunicationVoicePlayed):
                    for location in sensation.getLocations():
                        if location in self.itemConversations:
                            shouldDelete = self.itemConversations[location].process(transferDirection=transferDirection, sensation=sensation)
                            handledSensation = True
                if sensation.getRobotType() == Sensation.RobotType.Communication and\
                   sensation.getSensationType() == Sensation.SensationType.Item and\
                   self.getMemory().hasRobotsPresence():
                        self.robotConversation.process(transferDirection=transferDirection, sensation=sensation)
                        handledSensation = True
        # if we are mainRobot, we should use default processing also
        if self.isMainRobot():
            super().process(transferDirection=transferDirection, sensation=sensation)
        else:
            if not handledSensation:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='process: could not process this Sensation {}'.format(sensation.toDebugStr()))
        sensation.detach(robot=self)    # detach processed sensation
        # we have detected sensation that can be echo from ourselves and we can't process it and save to Memory, so it is deleted from memory
        if shouldDelete:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: deleting this sensation we can\'t save to Memory {}'.format(sensation.toDebugStr()))
            self.getMemory().deleteFromSensationMemory(sensation=sensation)
            del sensation
        
    
# Main Robot starting code
if __name__ == "__main__":
    from Robot import doMainRobot
    print ("Communication __main__: create Robot mainRobot = Communication(mainRobot=None)")
    global mainRobot
    mainRobot = Communication(mainRobot=None, instanceName="Communication")
    print ("Communication __main__: create Robot doMainRobot(mainRobot=mainRobot, instanceName=\"Communication\")")
    doMainRobot(mainRobot=mainRobot)
    print ("Communication __main__: create Robot all done")
# add this code to your main Robot code    
# # Main Robot starting code
# if __name__ == "__main__":
#     print ("Communication __main__: create Robot mainRobot = Communication(mainRobot=None)")
#     doMainRobot()
#     global mainRobot
#     mainRobot = Robot(mainRobot=None)
#     mainRobot.doMainRobot()

        
        
                

        

