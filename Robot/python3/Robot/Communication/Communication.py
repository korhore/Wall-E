'''
Created on 06.06.2019
Updated on 17.03.2021

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
#from syntaxnet.tensorflow.tensorflow.contrib.boosted_trees.lib.learner.batch import ordinal_split_handler
#from syntaxnet.tensorflow.tensorflow.contrib.boosted_trees.lib.learner.batch import ordinal_split_handler
#from Robot import LogLevel as LogLevel
# We cannot import Robot, because Robot import us,
# so we must duplicate Robot.LogLevel definition here
from enum import Enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Communication(Robot):

    # Communication is in statefull,
    # always im one of these states    
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
    IGNORE_LAST_HEARD_SENSATIONS_LENGTH=10 #5 Optimize this
                                    # How last heard voices we ignore in this conversation, when
                                    # we search best voices to to response to voices
                                    # This mast be >= 1 for sure, otherwise we are echo
                                    # but probably >=2, otherwise we are parrot
    ROBOT_RESPONSE_MAX = 6          # How many times we response to a Robot in one conversation
    
    class Conversation(object):
        def __init__(self,
                     robot,
                     location=None):
            self.ROBOT_RESPONSE_MAX = robot.ROBOT_RESPONSE_MAX
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
#                 isCommunication=False,
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
#                 isCommunication=isCommunication,
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
        implementation for this location
        
        Overridable method to be run just after
        while self.running:
        loop
        
        Say as isCommunication that This MainRobot is absent and stops to Communicate
        with other Robots
        '''
            
     
        def process(self, transferDirection, sensation):
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: {} {}'.format(systemTime.ctime(sensation.getTime()),transferDirection,sensation.toDebugStr()))
            # don't communicate with history Sensation Items, we are communicating Item.name just seen.
            #self.log(logLevel=Robot.LogLevel.Normal, logStr="process: systemTime.time() " + str(systemTime.time()) + ' -  sensation.getTime() ' + str(sensation.getTime()) + ' < Communication.COMMUNICATION_INTERVAL ' + str(Communication.COMMUNICATION_INTERVAL))
            self.log(logLevel=Robot.LogLevel.Normal, logStr="process: " + str(systemTime.time() - sensation.getTime()) + ' < ' + str(Communication.COMMUNICATION_INTERVAL))
            # accept heard voices and Item.name presentation Item.name changes
            #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
            # TODO enable line below, disabled for testing only
            if (systemTime.time() - sensation.getTime()) < Communication.COMMUNICATION_INTERVAL and\
               self.isThisLocation(sensation.getLocations()) and\
               (sensation.getRobotType() == Sensation.RobotType.Sense or\
                sensation.getRobotType() == Sensation.RobotType.Communication):
                #  entering to this location
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    if sensation.getPresence() == Sensation.Presence.Entering or\
                    sensation.getPresence() == Sensation.Presence.Present:
                        # or sensation.getPresence() == Sensation.Presence.Exiting):
                        # presence is tracked in MainRobot for all Robots
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got item ' + sensation.toDebugStr())
                        self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: got item ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got item ' + sensation.getName() + ' joined to communication')
                        self._isConversationDelay = False   # ready to continue conversation with new Item.name
                        
                        # now we can say something to the sensation.getName()
                        # even if we have said something so other present ones
                        # this means we need (again)
        
                        # if communication is going on item.name when comes
                        # handle as a response to said voice
                        # because it was as interesting that new iterm.name joins into conversation
                        
                        if self.timer is not None:
                            self.timer.cancel()
                            self.timer = None
                        if self.spokedAssociations != None:
                            for associations in self.spokedAssociations:
                                for association in associations:
                                    firstAssociateSensation = association.getSensation()
                                    otherAssociateSensation = association.getSelfSensation()
                                        
                                    if firstAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                                        self.getMemory().setMemoryType(sensation=firstAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
                                    if otherAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                                        self.getMemory().setMemoryType(sensation=otherAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
            
                                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice/image feeling with ' + firstAssociateSensation.getName())
                                    feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                          firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                          positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                                    self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                                        
                                    # detach
                                    firstAssociateSensation.detach(robot=self.getRobot())
                                    otherAssociateSensation.detach(robot=self.getRobot())
                                    # TODO Try to enable remembering
                                    feelingSensation.detach(robot=self.getRobot())        
                                       
                                    
                        self.speak(onStart=not self.isConversationOn())
    # THO what are these comments
    #                 # we have someone to talk with
    #                 # time is elapsed, so we can start communicating again with present item.names
                    elif sensation.getPresence() == Sensation.Presence.Absent and\
                        not self.getMemory().hasPresence(location=self.getLocation()):# and\
                        #self.isConversationOn():
                        # conversation is on and they have left us without responding
                        # We are disappointed
                        # don't wait response
                        if self.timer is not None:
                            self.timer.cancel() # cancel previous one
                            self.timer = None
                        self.stopWaitingResponse()                    
                        
                # if a Spoken Voice voice or image
                #     self.getMainNamesRobotType(robotType=sensation.getRobotType(), mainNames=sensation.getMainNames()) == Sensation.RobotType.Sense:
                elif (sensation.getSensationType() == Sensation.SensationType.Voice or sensation.getSensationType() == Sensation.SensationType.Image) and\
                     sensation.getMemoryType() == Sensation.MemoryType.Sensory and\
                     (sensation.getRobotType() == Sensation.RobotType.Sense or sensation.getRobotType() == Sensation.RobotType.Communication):
                    # don't echo same voice in this conversation
                    self.heardDataIds.append(sensation.getDataId())
                    while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
                        del self.heardDataIds[0]
    
                    # if response in a going on conversation 
                    if self.isConversationOn():
                        if self.spokedAssociations is not None:
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got response ' + sensation.toDebugStr())
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got response ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
         
                        if self.timer is not None:
                            self.timer.cancel()
                            self.timer = None
                        # We want to remember this voice
                        #sensation.setMemory(memoryType=Sensation.MemoryType.Working)
                        self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                            
                        # new implementation
                        if self.spokedAssociations != None:
                            for associations in self.spokedAssociations:
                                for association in associations:
                                    firstAssociateSensation = association.getSensation()
                                    otherAssociateSensation = association.getSelfSensation()
                                        
                                    if firstAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                                        self.getMemory().setMemoryType(sensation=firstAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
                                    if otherAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                                        self.getMemory().setMemoryType(sensation=otherAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
            
                                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice feeling with ' + otherAssociateSensation.getName())
                                    feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                            firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                            positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                                    self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                                        
                                    # detach
                                    firstAssociateSensation.detach(robot=self.getRobot())
                                    otherAssociateSensation.detach(robot=self.getRobot())
                                    # TODO Try to enable remembering
                                    feelingSensation.detach(robot=self.getRobot())        
                                       
                                    
                                    
                            
                        if self.getMemory().hasPresence(location=self.getLocation()):          
                            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().presenceToStr(location=self.getLocation()))
                            self.speak(onStart=False)
                        else:
                            self._isConversationOn = False # present ones are disappeared even if we  head a voice.
                            self.communicationState = Communication.CommunicationState.Waiting
                            self.robotResponses = 0
    
                    # we have someone to talk with
                    # time is elapsed, so we can start communicating again with present item.names
                    elif not self.isConversationOn() and\
                        self.getMemory().hasPresence(location=self.getLocation()) and\
                         (not self.isConversationDelay() or\
                          sensation.getTime() - self.lastConversationEndTime > self.CONVERSATION_INTERVAL):
                        self._isConversationDelay = False
                        self.robotResponses = 0
                       # we have still someone to talk with and not yet started a conversation at all or
                        # enough time is elapses of last conversation
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as new or restarted conversation ' + sensation.toDebugStr())
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as new or restarted conversation ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr(location=self.getLocation()))
     
                        # We want to remember this voice
                        self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                        # don't use this voice in this same conversation
                        #assert sensation.getDataId() not in self.heardDataIds
                        self.heardDataIds.append(sensation.getDataId())
                        while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
                            del self.heardDataIds[0]
                    
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().presenceToStr())
                        self.speak(onStart=True)
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: not Item or RESPONSE Voice or Image in communication or too soon from last conversation ' + sensation.toDebugStr())
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not heard voice or image of detected item ' + sensation.toDebugStr())
            
            sensation.detach(robot=self.getRobot())    # detach processed sensation
            
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
        '''
        def speak(self, onStart=False):
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak {}'.format(str(onStart)))
            startedAlready = False
            
            if self.spokedAssociations != None:
                for associations in self.spokedAssociations:
                    for association in associations:
                        association.getSelfSensation().detach(robot=self.getRobot())
                        association.getSensation().detach(robot=self.getRobot())
                self.spokedAssociations = None
                self.log(logLevel=Robot.LogLevel.Normal, logStr="speak: self.spokedAssociations = None")
                   
    
           # Temporarely commented out introducing ourselves
            #if onStart and len(self.getMemory().getRobot().voiceSensations) > 0:
            if onStart:
                # we just introduce ourselves
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: onStart')
                # use random own voice instead of self.voiceind
                # Temporarely commented out introducing ourselves
    #             voiceind = random.randint(0, len(self.getMemory().getRobot().voiceSensations)-1)
    #             self.spokedVoiceMuscleSensation = self.createSensation( associations=[], sensation=self.getMemory().getRobot().voiceSensations[voiceind],
    #                                                               memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle,
    #                                                               locations=self.getUpLocations())
    #             self.spokedVoiceCommunicationSensation = self.createSensation( associations=[], sensation=self.getMemory().getRobot().voiceSensations[voiceind],
    #                                                               memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Communication,
    #                                                               locations=self.getUpLocations())
    #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceMuscleSensation) # or self.process
    #             self.log("speak: Starting with presenting Robot voiceind={} self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation={}".format(str(voiceind), self.spokedVoiceMuscleSensation.toDebugStr()))
    #             self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
    #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceCommunicationSensation) # or self.process
    #             self.log("speak: Starting with presenting Robot voiceind={} self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation={}".format(str(voiceind), self.spokedVoiceCommunicationSensation.toDebugStr()))
    #             self.saidSensations.append(self.spokedVoiceCommunicationSensation.getDataId())
    #             
    #             # wait response
    #             if self.timer is not None:
    #                 self.timer.cancel() # cancel previous one
    #             self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
    #             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: timer.start()')
    #             self.timer.start()
    #             self._isConversationOn = True
    #             self.communicationState = Communication.CommunicationState.On                                               
    
            #else:
            if True:
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
                        print('speak names {}'.format(names))
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
    
                                    #sensation.attach(robot=self.getRobot()) # TODO yes or no, no reason to attach
                                    sensation.save()     # for debug reasons save voices we have spoken as heard voices and images
                                    self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getBestSensations did find sensations, spoke {}'.format(sensation.toDebugStr()))
    
                                    #create normal Muscle sensation for persons to be hards
                                    spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
                                    # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                    spokedSensation.setKind(self.getKind())
                                    spokedSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
                                    #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                                    self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
                                    # speak                 
                                    self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
                                    # TODO Try to enable remembering, commented out, getAxon().put does this
                                    #spokedSensation.detach(robot=self.getRobot())        
                                    
                                    # create Communication sensation for Robots to be 'heard'
                                    # Robot.createSensation set RobotMainNames
                                    if self.robotResponses < self.ROBOT_RESPONSE_MAX:
                                        spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
                                        # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                                        spokedSensation.setKind(self.getKind())
                                        spokedSensation.setRobotType(Sensation.RobotType.Communication)  # 'speak' to Robots       
                                        #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                                        self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
                                        # speak                 
                                        self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
                                        # TODO Try to enable remembering
                                        #spokedSensation.detach(robot=self.getRobot())
                                        self.robotResponses = self.robotResponses+1
                                    
                                self.spokedAssociations = associations
                                self.log(logLevel=Robot.LogLevel.Normal, logStr="speak: self.spokedAssociations = associations")
                                # wait response
                                if self.timer is not None:
                                    self.timer.cancel() # cancel previous one
                                self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: timer.start()')
                                self.timer.start()
                                self._isConversationOn = True
                                self.communicationState = Communication.CommunicationState.On                                                                            
                            else:
                                # We did not find anything to say, but are ready to start new conversation, if someone speaks.
                                #self._isConversationDelay = True
                    
                                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getBestSensations did NOT find Sensation to speak')
                                self._isNoResponseToSay = True
                                self.communicationState = Communication.CommunicationState.NoResponseToSay                                             
                                #self.clearConversation()
                                   
                        succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
                    except AssertionError as e:
                        self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
                        raise e
                    except Exception as e:
                        self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))
    
        '''
        We did not get response
        '''
            
        def stopWaitingResponse(self):
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
                            
            if self.spokedAssociations is not None:
                for associations in self.spokedAssociations:
                    for association in associations:
                        firstAssociateSensation = association.getSensation()
                        otherAssociateSensation = association.getSelfSensation()
                                    
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='stopWaitingResponse:  bad feeling with ' + otherAssociateSensation.getName())
                        feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                                firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
                                                                negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                        self.getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                        # TODO Try to enable remembering
                        feelingSensation.detach(robot=self.getRobot())        
            self.endConversation()
            self._isConversationDelay = True
    
            
        def clearConversation(self):     
            if self.spokedAssociations != None:        
                for associations in self.spokedAssociations:
                    for association in associations:
                        association.getSelfSensation().detach(robot=self.getRobot())
                        association.getSensation().detach(robot=self.getRobot())
            self.spokedAssociations = None 
            self.log(logLevel=Robot.LogLevel.Normal, logStr="clearConversation: self.spokedAssociations = None")
    
            del self.spokedDataIds[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
            del self.heardDataIds[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
            
        def endConversation(self):
            self.clearConversation()
            self.timer = None
            self.lastConversationEndTime=systemTime.time()
            self._isConversationOn = False
            self._isConversationEnded = True
            self._isConversationDelay = True
            self.communicationState = Communication.CommunicationState.Delay
            self.robotResponses = 0


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
        

#         self.lastConversationEndTime = None
#         self._isConversationOn = False
#         self._isConversationEnded = False
#         self._isConversationDelay = False
#         self._isNoResponseToSay = False
        
        self.conversations={}
        if len(self.getLocations()) > 0:
            for location in self.getLocations():
                self.conversations[location] =\
                    Communication.Conversation(robot=self, location=location)
        else:
            self.conversations['']=Conversation(robot=self, location='')

#         self.communicationState = Communication.CommunicationState.Waiting
#         
#         self.spokedSensations = None                # Sensations that we last said to other side 
#         self.spokedAssociations = None              # Associations that spoked Sensations were assigned to Item.name sensations
# 
#         self.mostImportantItemSensation = None      # current most important item in conversation
#         self.mostImportantVoiceAssociation  = None  # current association most important voice, item said in some previous conversation
#                                                     # but not in this conversation
#         self.mostImportantVoiceSensation = None     # current most important voice, item said in some previous conversation
#                                                     # but not in this conversation
#         self.mostImportantImageAssociation  = None  # current association most important image, item said in some previous conversation
#                                                     # but not in this conversation
#         self.mostImportantImageSensation = None     # current most important image, item said in some previous conversation
#                                                     # but not in this conversation
# #         self.spokedVoiceMuscleSensation = None      # last voice we have said to a person
# #         self.spokedVoiceCommunicationSensation = None      # last voice we have said to a person
# #         self.spokedImageMuscleSensation = None      # last voice we have said to a person
# #         self.spokedVoiceCommunicationSensation = None      # last voice we have said to a Robot
# #         self.spokedImageCommunicationSensation = None      # last voice we have said to a Robot
# 
#         self.timer=None
#         self.spokedDataIds = []     # Sensations dataIds we have said in this conversation 
#         self.heardDataIds = []      # Sensations ataIds  we have heard in this conversation
#         self.robotResponses = 0
        
    '''
    Overridable method to be run just before
    while self.running:
    loop
    
    Say as isCommunication that This MainRobot is present and ready to Communicate
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
    
    Say as isCommunication that This MainRobot is absent and stops to Communicate
    with other Robots
    '''
        
    def deInitRobot(self):
        itemSensation = self.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                            sensationType=Sensation.SensationType.Item,
                                            robotType=Sensation.RobotType.Muscle,
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
            for location in self.getLocations():
                self.conversations[location].process(transferDirection=transferDirection, sensation=sensation)
        else:
            for location in sensation.getLocations():
                if location in self.conversations:
                    self.conversations[location].process(transferDirection=transferDirection, sensation=sensation)

        sensation.detach(robot=self)    # detach processed sensation
        
# old global locations conversation logic commented out
        
#         
#         # accept heard voices and Item.name presentation Item.name changes
#         #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
#         # TODO enable line below, disabled for testing only
#         #if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
#         if (sensation.getRobotType() == Sensation.RobotType.Sense or\
#              sensation.getRobotType() == Sensation.RobotType.Communication):
#             # all kind Items found
#             if sensation.getSensationType() == Sensation.SensationType.Item:
#                 if sensation.getPresence() == Sensation.Presence.Entering or\
#                    sensation.getPresence() == Sensation.Presence.Present:
#                     # or sensation.getPresence() == Sensation.Presence.Exiting):
#                     # presence is tracked in MainRobot for all Robots
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got item ' + sensation.toDebugStr())
#                     self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: got item ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got item ' + sensation.getName() + ' joined to communication')
#                     self._isConversationDelay = False   # ready to continue conversation with new Item.name
#                     
#                     # now we can say something to the sensation.getName()
#                     # even if we have said something so other present ones
#                     # this means we need (again)
#     
#                     # if communication is going on item.name when comes
#                     # handle as a response to said voice
#                     # because it was as interesting that new iterm.name joins into conversation
#                     
#                     if self.timer is not None:
#                         self.timer.cancel()
#                         self.timer = None
#                     if self.spokedAssociations != None:
#                         for associations in self.spokedAssociations:
#                             for association in associations:
#                                 firstAssociateSensation = association.getSensation()
#                                 otherAssociateSensation = association.getSelfSensation()
#                                     
#                                 if firstAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
#                                     self.getMemory().setMemoryType(sensation=firstAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
#                                 if otherAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
#                                     self.getMemory().setMemoryType(sensation=otherAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
#         
#                                 self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice/image feeling with ' + firstAssociateSensation.getName())
#                                 feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
#                                                                       firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
#                                                                       positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
#                                 self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
#                                     
#                                 # detach
#                                 firstAssociateSensation.detach(robot=self)
#                                 otherAssociateSensation.detach(robot=self)
#                                 # TODO Try to enable remembering
#                                 feelingSensation.detach(robot=self)        
#                                            sensation.detach(robot=self)    # detach processed sensation
# 
#                                 
#                     self.speak(onStart=not self.isConversationOn())
# #                 # we have someone to talk with
# #                 # time is elapsed, so we can start communicating again with present item.names
# #                 elif not self.isConversationOn() and\
# #                     self.getMemory().hasPresence() and\
# #                      (not self.isConversationDelay() or\
# #                       sensation.getTime() - self.lastConversationEndTime > self.CONVERSATION_INTERVAL):
# #                     self._isConversationDelay = False
# #                     # we have still someone to talk with and not yet started a conversation at all or
# #                     # enough time is elapses of last conversation
# #                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.toDebugStr())
# #                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
# #  
# #                     # We want to remember this voice
# #                     self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
# #                     # don't use this voice in this same conversation
# #                     #assert sensation.getDataId() not in self.heardDataIds
# #                     self.heardDataIds.append(sensation.getDataId())
# #                     while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
# #                         del self.heardDataIds[0]
# #                 
# #                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().presenceToStr())
# #                     self.speak(onStart=True)
# #                     
# #                     
# #                     
# #                     
# #                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got item starting new = {} communication with {}'.format(not self.isConversationOn(), sensation.getName()))
# #                     self.speak(onStart=not self.isConversationOn()) #itemSensation=sensation)
#                 elif sensation.getPresence() == Sensation.Presence.Absent and\
#                     not self.getMemory().hasPresence():# and\
#                     #self.isConversationOn():
#                     # conversation is on and they have left us without responding
#                     # We are disappointed
#                     # don't wait response
#                     if self.timer is not None:
#                         self.timer.cancel() # cancel previous one
#                         self.timer = None
#                     self.stopWaitingResponse()                    
#                     
#             # if a Spoken Voice voice or image
#             #     self.getMainNamesRobotType(robotType=sensation.getRobotType(), mainNames=sensation.getMainNames()) == Sensation.RobotType.Sense:
#             elif (sensation.getSensationType() == Sensation.SensationType.Voice or sensation.getSensationType() == Sensation.SensationType.Image) and\
#                  sensation.getMemoryType() == Sensation.MemoryType.Sensory and\
#                  (sensation.getRobotType() == Sensation.RobotType.Sense or sensation.getRobotType() == Sensation.RobotType.Communication):
#                 # don't echo same voice in this conversation
#                 self.heardDataIds.append(sensation.getDataId())
#                 while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
#                     del self.heardDataIds[0]
# 
#                 # if response in a going on conversation 
#                 if True:
#                 # TODO enable line below, disabled for test
#                 #if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL:
#                     if self.isConversationOn():
# #                     if self.mostImportantItemSensation is not None:
# #                         self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as response ' + sensation.toDebugStr()+ ' from ' + self.mostImportantItemSensation.getName())
#                         if self.spokedAssociations is not None:
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got response ' + sensation.toDebugStr())
#                         self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got response ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
#      
#                         if self.timer is not None:
#                             self.timer.cancel()
#                             self.timer = None
#                         # We want to remember this voice
#                         #sensation.setMemory(memoryType=Sensation.MemoryType.Working)
#                         self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
#                         
#                         # new implementation
#                         if self.spokedAssociations != None:
#                             for associations in self.spokedAssociations:
#                                 for association in associations:
#                                     firstAssociateSensation = association.getSensation()
#                                     otherAssociateSensation = association.getSelfSensation()
#                                     
#                                     if firstAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
#                                         self.getMemory().setMemoryType(sensation=firstAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
#                                     if otherAssociateSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
#                                         self.getMemory().setMemoryType(sensation=otherAssociateSensation, memoryType=Sensation.MemoryType.LongTerm)
#         
#                                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice feeling with ' + otherAssociateSensation.getName())
#                                     feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
#                                                                       firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
#                                                                       positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
#                                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
#                                     
#                                     # detach
#                                     firstAss        sensation.detach(robot=self)    # detach processed sensation
# ociateSensation.detach(robot=self)
#                                     otherAssociateSensation.detach(robot=self)
#                                     # TODO Try to enable remembering
#                                     feelingSensation.detach(robot=self)        
#                                    
#                                 
#                                 
#                         
#                         if self.getMemory().hasPresence():          
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().presenceToStr())
#                             self.speak(onStart=False)
#                         else:
#                             self._isConversationOn = False # present ones are disappeared even if we  head a voice.
#                             self.communicationState = Communication.CommunicationState.Waiting
#                             self.robotResponses = 0
# 
#                 # we have someone to talk with
#                 # time is elapsed, so we can start communicating again with present item.names
#                 elif not self.isConversationOn() and\
#                     self.getMemory().hasPresence() and\
#                      (not self.isConversationDelay() or\
#                       sensation.getTime() - self.lastConversationEndTime > self.CONVERSATION_INTERVAL):
#                     self._isConversationDelay = False
#                     self.robotResponses = 0
#                    # we have still someone to talk with and not yet started a conversation at all or
#                     # enough time is elapses of last conversation
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.toDebugStr())
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
#  
#                     # We want to remember this voice
#                     self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
#                     # don't use this voice in this same conversation
#                     #assert sensation.getDataId() not in self.heardDataIds
#                     self.heardDataIds.append(sensation.getDataId())
#                     while len(self.heardDataIds) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
#                         del self.heardDataIds[0]
#                 
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().presenceToStr())
#                     self.speak(onStart=True)
#             else:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: not Item or RESPONSE Voice or Image in communication or too soon from last conversation ' + sensation.toDebugStr())
#         else:
#             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not heard voice or image of detected item ' + sensation.toDebugStr())
#         
#         sensation.detach(robot=self)    # detach processed sensation
#         
#     def isConversationOn(self):
#         return self._isConversationOn
#         # returnself.mostImportantItemSensation is not None      # when conversaing, we know most important item.name to cerversate with
#    
#     def isConversationEnded(self):
#         return self._isConversationEnded
#     
#     def isConversationDelay(self):
#         return self._isConversationDelay
#         
#     def isNoResponseToSay(self):
#         return self._isNoResponseToSay
# 
#     '''
#     Speak:
#     Say something, when we know Item.name's that are present.
#     In this starting version we don't care what was said before, except
#     what we have said, but because we don't have any clue, what is meaning of the
#     speak, or even what Item.names can really speak,
#     we just use statistical methods to guess, how we can keep on conversation
#     on. We start to speak with voices heard, when best score
#     - identification Item.name as Image was happened.
#     We set feeling, when we get a response.
#     By those methods we can set Importance of Voices
#     '''
#     def speak(self, onStart=False):
#         self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak {}'.format(str(onStart)))
#         startedAlready = False
#         
# #         if self.mostImportantItemSensation is not None:
# #             self.mostImportantItemSensation.detach(robot=self)
# #         self.mostImportantItemSensation = None
# #         
# #         self.mostImportantVoiceAssociation = None
# #         
# #         if self.mostImportantVoiceSensation is not None:
# #             self.mostImportantVoiceSensation.detach(robot=self)
# #         self.mostImportantVoiceSensation  = None
# #         
# #         if self.spokedVoiceMuscleSensation is not None:
# #             self.spokedVoiceMuscleSensation.detach(robot=self)
# #         self.spokedVoiceMuscleSensation = None
# #         if self.spokedVoiceCommunicationSensation is not None:
# #             self.spokedVoiceCommunicationSensation.detach(robot=self)
# #         self.spokedVoiceCommunicationSensation = None
# # 
# #         self.mostImportantImageAssociation = None
# #         
# #         if self.mostImportantImageSensation is not None:
# #             self.mostImportantImageSensation.detach(robot=self)
# #         self.mostImportantImageensation  = None
# # 
# #         if self.spokedImageMuscleSensation is not None:
# #             self.spokedImageMuscleSensation.detach(robot=self)
# #         self.spokedImageMuscleSensation = None
# #         if self.spokedImageCommunicationSensation is not None:
# #             self.spokedImageCommunicationSensation.detach(robot=self)
# #         self.spokedImageCommunicationSensation = None
#         
#         if self.spokedAssociations != None:
#             for associations in self.spokedAssociations:
#                 for association in associations:
#                     association.getSelfSensation().detach(robot=self)
#                     association.getSensation().detach(robot=self)
#             self.spokedAssociations = None
#             self.log(logLevel=Robot.LogLevel.Normal, logStr="speak: self.spokedAssociations = None")
#                
# 
#        # Temporarely commented out introducing ourselves
#         #if onStart and len(self.getMemory().getRobot().voiceSensations) > 0:
#         if onStart:
#             # we just introduce ourselves
#             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: onStart')
#             # use random own voice instead of self.voiceind
#             # Temporarely commented out introducing ourselves
# #             voiceind = random.randint(0, len(self.getMemory().getRobot().voiceSensations)-1)
# #             self.spokedVoiceMuscleSensation = self.createSensation( associations=[], sensation=self.getMemory().getRobot().voiceSensations[voiceind],
# #                                                               memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle,
# #                                                               locations=self.getUpLocations())
# #             self.spokedVoiceCommunicationSensation = self.createSensation( associations=[], sensation=self.getMemory().getRobot().voiceSensations[voiceind],
# #                                                               memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Communication,
# #                                                               locations=self.getUpLocations())
# #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceMuscleSensation) # or self.process
# #             self.log("speak: Starting with presenting Robot voiceind={} self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation={}".format(str(voiceind), self.spokedVoiceMuscleSensation.toDebugStr()))
# #             self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
# #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceCommunicationSensation) # or self.process
# #             self.log("speak: Starting with presenting Robot voiceind={} self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation={}".format(str(voiceind), self.spokedVoiceCommunicationSensation.toDebugStr()))
# #             self.saidSensations.append(self.spokedVoiceCommunicationSensation.getDataId())
# #             
# #             # wait response
# #             if self.timer is not None:
# #                 self.timer.cancel() # cancel previous one
# #             self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
# #             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: timer.start()')
# #             self.timer.start()
# #             self._isConversationOn = True
# #             self.communicationState = Communication.CommunicationState.On                                               
# 
#         #else:
#         if True:
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
#                     print('speak names {}'.format(names))
#                     if len(itemSensations) > 0:  # something found
#                         # the search candidates what we say or/and show next
#                         # We want now sensations and associations that
#                         # have association to one or more SensationType.Itemss thst bame matches
#                         # Sensation.SensationType is Voice or Image
#                         # RobotType is Sense of Communication which RoborMainNames does not match, meaning that it is from foreign Robot 'spoken'
#                         # it is in ignoredDataIds dataId meaning that it is not spoken by us in this conversation
#                         sensations, associations  = self.getMemory().getBestSensations(
#                                                         #allAssociations = False,
#                                                         itemSensations = itemSensations,
#                                                         sensationTypes = [Sensation.SensationType.Voice, Sensation.SensationType.Image],
#                                                         robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
#                                                         robotMainNames = self.getMainNames(),
#                                                         ignoredDataIds=self.spokedDataIds+self.heardDataIds)#,
#                                                         #ignoredVoiceLens=self.ignoredVoiceLens)
#                         if len(sensations) > 0 and len(associations) > 0:
#                             self._isNoResponseToSay = False
#                             for sensation in sensations:
#                                 #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
#                                 assert sensation.getDataId() not in self.spokedDataIds
#                                 self.spokedDataIds.append(sensation.getDataId())   
# 
#                                 #sensation.attach(robot=self) # TODO yes or no, no reason to attach
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
#                                 self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
#                                 # TODO Try to enable remembering, commented out, getAxon().put does this
#                                 #spokedSensation.detach(robot=self)        
#                                 
#                                 # create Communication sensation for Robots to be 'heard'
#                                 # Robot.createSensation set RobotMainNames
#                                 if self.robotResponses < self.ROBOT_RESPONSE_MAX:
#                                     spokedSensation = self.createSensation(sensation = sensation, kind=self.getKind(), locations=self.getLocations())
#                                     # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
#                                     spokedSensation.setKind(self.getKind())
#                                     spokedSensation.setRobotType(Sensation.RobotType.Communication)  # 'speak' to Robots       
#                                     #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
#                                     self.getMemory().setMemoryType(sensation=spokedSensation, memoryType=Sensation.MemoryType.Sensory)
#                                     # speak                 
#                                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=spokedSensation)
#                                     # TODO Try to enable remembering
#                                     #spokedSensation.detach(robot=self)
#                                     self.robotResponses = self.robotResponses+1
#                                 
#                             self.spokedAssociations = associations
#                             self.log(logLevel=Robot.LogLevel.Normal, logStr="speak: self.spokedAssociations = associations")
#                             # wait response
#                             if self.timer is not None:
#                                 self.timer.cancel() # cancel previous one
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
#                         # TODO continue implementation change from this
# 
# #                         self.mostImportantVoiceSensation = None
# #                         bestMemorability = -1000
# #                         for candidateVoice in candidateVoices:
# #                             candidateVoiceMemorability =
# #                                 candidateVoice.getMemorability(allAssociations = False,
# #                                                                itemSensations = itemSensations,
# #                                                                robotMainNames = self.getMainNames())
# #                             if self.mostImportantVoiceSensation == None or candidateVoiceMemorability > bestMemorability:
# #                                 bestMemorability = candidateVoiceMemorability
# #                                 self.mostImportantVoiceSensation = candidateVoice
# #                         if self.mostImportantVoiceSensation is not None:        
# #                             self.mostImportantVoiceSensation.attach(robot=self)
# #                             self.mostImportantVoiceSensation.save()     # for debug reasons save voices we have spoken as heard voices
# #                             self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantVoiceSensation OK')
# #                             self.spokedVoiceMuscleSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
# #                                                                               locations=self.getLocations())
# #                             # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
# #                             self.spokedVoiceMuscleSensation.setKind(self.getKind())
# #                             self.spokedVoiceMuscleSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
# #                             #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
# #                             self.getMemory().setMemoryType(sensation=self.spokedVoiceMuscleSensation, memoryType=Sensation.MemoryType.Sensory)
# #                             self.spokedVoiceCommunicationSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
# #                                                                               locations=self.getLocations())
# #                             # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
# #                             self.spokedVoiceCommunicationSensation.setKind(self.getKind())
# #                             self.spokedVoiceCommunicationSensation.setRobotType(Sensation.RobotType.Communication)  # communicate with Robots      
# #                             #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
# #                             self.getMemory().setMemoryType(sensation=self.spokedVoiceCommunicationSensation, memoryType=Sensation.MemoryType.Sensory)
# #         
# #                             #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
# #                             assert self.mostImportantVoiceSensation.getDataId() not in self.saidSensations
# #                             self.saidSensations.append(self.mostImportantVoiceSensation.getDataId())   
# #                             # speak                 
# #                             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceMuscleSensation)
# #                             # Communicate                
# #                             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceCommunicationSensation)
# #                                 
# #                                 
# #                             if candidateVoice.getMemorability(allAssociations = False,
# #                                                               itemSensations = itemSensations,
# #                                                               robotMainNames = self.getMainNames())
# # 
# #                                 
# #                     for location in self.getMemory()._presentItemSensations.keys():
# #                         for name, sensation in self.getMemory()._presentItemSensations[location].items():
# #                     #for name, sensation in self.getMemory().presentItemSensations.items():
# # #                                 self.getMemory().getMostImportantSensation( sensationType = Sensation.SensationType.Item,
# # #                                                                      robotType = Sensation.RobotType.Sense,
# # #                                                                      name = name,
# # #                                                                      notName = None,
# # #                                                                      timemin = None,
# # #                                                                      timemax = None,
# # #                                                                      associationSensationType=Sensation.SensationType.Voice,
# # #                                                                      associationDirection = Sensation.RobotType.Sense,
# # #                                                                      #ignoredSensations = []) # TESTING
# # #                                                                      ignoredSensations = self.ignoredSensations,
# # #                                                                      ignoredVoiceLens = self.usedVoiceLens,
# # #                                                                      searchLength=Communication.SEARCH_LENGTH)
# #                             candidate_for_communication_item, candidate_for_voice, candidate_for_voice_association,\
# #                                                               candidate_for_image, candidate_for_image_association = \
# #                                 self.getMemory().getMostImportantCommunicationSensations( 
# #                                                                      #robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
# #                                                                      robotMainNames=self.getMainNames(),
# #                                                                      name = name,
# #                                                                      timemin = None,
# #                                                                      timemax = None,
# #                                                                      ignoredSensations = self.saidSensations + self.heardDataIds,
# #                                                                      searchLength=Communication.SEARCH_LENGTH)
# #                             if candidate_for_voice is not None:
# #                                 assert candidate_for_voice.getDataId() not in self.saidSensations
# #                                 
# #                             if self.mostImportantItemSensation is None or\
# #                                (candidate_for_communication_item is not None and\
# #                                candidate_for_communication_item.getImportance() > self.mostImportantItemSensation.getImportance()):
# #                                 self.mostImportantItemSensation = candidate_for_communication_item
# #                                 self.mostImportantVoiceAssociation = candidate_for_voice_association
# #                                 self.mostImportantVoiceSensation  = candidate_for_voice
# #                                 self.mostImportantImageAssociation = candidate_for_image_association
# #                                 self.mostImportantImageSensation  = candidate_for_image
# #         
# #                         if self.mostImportantItemSensation is None:     # if no voices assosiated to present item.names, then any voice will do
# # #                             self.mostImportantItemSensation, self.mostImportantVoiceAssociation, self.mostImportantVoiceSensation = \
# # #                                 self.getMemory().getMostImportantSensation( sensationType = Sensation.SensationType.Item,
# # #                                                                      robotType = Sensation.RobotType.Sense,
# # #                                                                      name = None,
# # #                                                                      notName = None,
# # #                                                                      timemin = None,
# # #                                                                      timemax = None,
# # #                                                                      associationSensationType=Sensation.SensationType.Voice,
# # #                                                                      associationDirection = Sensation.RobotType.Sense,
# # #                                                                      #ignoredSensations = []) # TESTING
# # #                                                                      ignoredSensations = self.saidSensations,
# # #                                                                      ignoredVoiceLens = self.usedVoiceLens,
# # #                                                                      searchLength=Communication.SEARCH_LENGTH)
# #                             self.mostImportantItemSensation, self.mostImportantVoiceSensation, self.mostImportantVoiceAssociation,\
# #                                                              self.mostImportantImageSensation, self.mostImportantImageAssociation =\
# #                                 self.getMemory().getMostImportantCommunicationSensations( 
# #                                                                      #robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
# #                                                                      robotMainNames=self.getMainNames(),
# #                                                                      name = None,
# #                                                                      timemin = None,
# #                                                                      timemax = None,
# #                                                                      ignoredSensations = self.saidSensations + self.heardDataIds,
# #                                                                      searchLength=Communication.SEARCH_LENGTH)
#                     succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
#                 except AssertionError as e:
#                     self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
#                     raise e
#                 except Exception as e:
#                     self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))
# # 
# #             # TODO self.mostImportantItemSensation is not None             
# #             if self.mostImportantItemSensation is not None and (self.mostImportantVoiceSensation is not None or self.mostImportantImageSensation is not None):
# #                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantItemSensation OK')
# #                 self.mostImportantItemSensation.attach(robot=self)         #attach Sensation until speaking is ended based on these voices
# #                 if self.mostImportantImageSensation is not None:
# #                     self.mostImportantImageSensation.attach(robot=self)
# #                     self.mostImportantImageSensation.save()     # for debug reasons save voices we have spoken as heard voices
# #                     self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantImageSensation OK')
# #                     self.spokedImageMuscleSensation = self.createSensation( sensation = self.mostImportantImageSensation, kind=self.getKind(),
# #                                                                       locations=self.getLocations())
# #                     # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
# #                     self.spokedImageMuscleSensation.setKind(self.getKind())
# #                     self.spokedImageMuscleSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
# #                     # TODO self.mostImportantItemSensation is now None, but it should not be possible             
# #                     #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantImageSensation)
# #                     self.getMemory().setMemoryType(sensation=self.spokedImageMuscleSensation, memoryType=Sensation.MemoryType.Sensory)
# # 
# #                     self.spokedImageCommunicationSensation = self.createSensation( sensation = self.mostImportantImageSensation, kind=self.getKind(),
# #                                                                       locations=self.getLocations())
# #                     # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
# #                     self.spokedImageCommunicationSensation.setKind(self.getKind())
# #                     self.spokedImageCommunicationSensation.setRobotType(Sensation.RobotType.Communication)  # Communicate      
# #                     # TODO self.mostImportantItemSensation is now None, but it should not be possible             
# #                     #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantImageSensation)
# #                     self.getMemory().setMemoryType(sensation=self.spokedImageCommunicationSensation, memoryType=Sensation.MemoryType.Sensory)
# #                     
# #                     assert self.mostImportantImageSensation.getDataId() not in self.saidSensations                    
# #                     self.saidSensations.append(self.mostImportantImageSensation.getDataId())   
# #                     # speak                 
# #                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedImageMuscleSensation)
# #                     # communicate                 
# #                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedImageCommunicationSensation)
# # 
# #                 if self.mostImportantVoiceSensation is not None:        
# #                     self.mostImportantVoiceSensation.attach(robot=self)
# #                     self.mostImportantVoiceSensation.save()     # for debug reasons save voices we have spoken as heard voices
# #                     self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantVoiceSensation OK')
# #                     self.spokedVoiceMuscleSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
# #                                                                       locations=self.getLocations())
# #                     # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
# #                     self.spokedVoiceMuscleSensation.setKind(self.getKind())
# #                     self.spokedVoiceMuscleSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
# #                     #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
# #                     self.getMemory().setMemoryType(sensation=self.spokedVoiceMuscleSensation, memoryType=Sensation.MemoryType.Sensory)
# #                     self.spokedVoiceCommunicationSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
# #                                                                       locations=self.getLocations())
# #                     # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
# #                     self.spokedVoiceCommunicationSensation.setKind(self.getKind())
# #                     self.spokedVoiceCommunicationSensation.setRobotType(Sensation.RobotType.Communication)  # communicate with Robots      
# #                     #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
# #                     self.getMemory().setMemoryType(sensation=self.spokedVoiceCommunicationSensation, memoryType=Sensation.MemoryType.Sensory)
# # 
# #                     #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
# #                     assert self.mostImportantVoiceSensation.getDataId() not in self.saidSensations
# #                     self.saidSensations.append(self.mostImportantVoiceSensation.getDataId())   
# #                     # speak                 
# #                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceMuscleSensation)
# #                     # Communicate                
# #                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceCommunicationSensation)
# #                 
# #                 # wait response
# #                 if self.timer is not None:
# #                     self.timer.cancel() # cancel previous one
# #                 self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
# #                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: timer.start()')
# #                 self.timer.start()
# #                 self._isConversationOn = True              
#                  
# #                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: spoke {}'.format(self.spokedVoiceMuscleSensation.toDebugStr()))
# #                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: commicated {}'.format(self.spokedVoiceCommunicationSensation.toDebugStr()))
# #             else:
# #                 # We did not find anything to say, but are ready to start new conversation, if someone speaks.
# #                 self._isConversationDelay = False
# #      
# #                 self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did NOT find self.mostImportantItemSensation')
# #                 self._isConversationOn = False             
# #                 self.clearConversation()
# 
#     '''
#     We did not get response
#     '''
#         
#     def stopWaitingResponse(self):
#         self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
#         
# #         if self.mostImportantVoiceSensation is not None and self.mostImportantItemSensation is not None:
# #         
# #             feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
# #                                                     firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantVoiceSensation,
# #                                                     negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen also other way
# #             self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Voice self.getParent().getAxon().put do feelingSensation negativeFeeling")
# #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
# #             self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Voice self.getParent().getAxon().put done")
# #         if self.mostImportantImageSensation  is not None and self.mostImportantItemSensation is not None:
# #         
# #             feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
# #                                                     firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantImageSensation ,
# #                                                     negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen also other way
# #             self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Image self.getParent().getAxon().put do feelingSensation negativeFeeling")
# #             self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
# #             self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Image self.getParent().getAxon().put done")
#             
#         if self.spokedAssociations is not None:
#             for associations in self.spokedAssociations:
#                 for association in associations:
#                     firstAssociateSensation = association.getSensation()
#                     otherAssociateSensation = association.getSelfSensation()
#                                 
#                     self.log(logLevel=Robot.LogLevel.Normal, logStr='stopWaitingResponse:  bad feeling with ' + otherAssociateSensation.getName())
#                     feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
#                                                             firstAssociateSensation=firstAssociateSensation, otherAssociateSensation=otherAssociateSensation,
#                                                             negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
#                     self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
#                     # TODO Try to enable remembering
#                     feelingSensation.detach(robot=self)        
# #         else:
# #             self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: self.spokedAssociations is None BUT IT SHOULD NOT")
# #             
#         
#         self.endConversation()
#         self._isConversationDelay = True
# 
#         
#     def clearConversation(self):
# #         if self.mostImportantItemSensation is not None:
# #             self.mostImportantItemSensation.detach(robot=self)
# #         self.mostImportantItemSensation = None
# #         
# #         self.mostImportantVoiceAssociation  = None
# #         
# #         if self.mostImportantVoiceSensation is not None:
# #             self.mostImportantVoiceSensation.detach(robot=self)
# #         self.mostImportantVoiceSensation  = None
# #         
# #         if self.spokedVoiceMuscleSensation is not None:
# #             self.spokedVoiceMuscleSensation.detach(robot=self)
# #         self.spokedVoiceMuscleSensation = None
# #         if self.spokedVoiceCommunicationSensation is not None:
# #             self.spokedVoiceCommunicationSensation.detach(robot=self)
# #         self.spokedVoiceCommunicationSensation = None
# # 
# #         if self.mostImportantImageSensation is not None:
# #             self.mostImportantImageSensation.detach(robot=self)
# #         self.mostImportantImageSensation  = None
# #         
# #         if self.spokedImageMuscleSensation is not None:
# #             self.spokedImageMuscleSensation.detach(robot=self)
# #         self.spokedImageMuscleSensation = None
# # 
# #         if  self.spokedImageCommunicationSensation is not None:
# #             self.spokedImageCommunicationSensation.detach(robot=self)
# #         self.spokedImageCommunicationSensation = None
#  
#         if self.spokedAssociations != None:        
#             for associations in self.spokedAssociations:
#                 for association in associations:
#                     association.getSelfSensation().detach(robot=self)
#                     association.getSensation().detach(robot=self)
# #                 
#         self.spokedAssociations = None 
#         self.log(logLevel=Robot.LogLevel.Normal, logStr="clearConversation: self.spokedAssociations = None")
#          
# 
#         del self.spokedDataIds[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
#         del self.heardDataIds[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
#         
#     def endConversation(self):
#         self.clearConversation()
#         self.timer = None
#         self.lastConversationEndTime=systemTime.time()
#         self._isConversationOn = False
#         self._isConversationEnded = True
#         self._isConversationDelay = True
#         self.communicationState = Communication.CommunicationState.Delay
#         self.robotResponses = 0
        

        

