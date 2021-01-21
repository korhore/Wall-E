'''
Created on 06.06.2019
Updated on 21.01.2021

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
import traceback

from Robot import Robot
from Sensation import Sensation
from Config import Config

class Communication(Robot):

    COMMUNICATION_INTERVAL=30.0     # time window to history 
                                    # for sensations we communicate
    CONVERSATION_INTERVAL=300.0     # if no change in present item.names and
                                    # last conversation is ended, how long
                                    # we wait until we will respond if
                                    # someone speaks
    SEARCH_LENGTH=10                # How many response voices we check
    IGNORE_LAST_HEARD_SENSATIONS_LENGTH=5
                                    # How last heard voices we ignore in this conversation, when
                                    # we search best voicess to to pesponse to voices
                                    # This mast be >= 1 for sure, otherwise we are echo
                                    # vut propapble >=2, otherwise we are parrot
                                    

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

        self.lastConversationEndTime = None
        self._isConversationOn = False
        self._isConversationEnded = False
        self._isConversationDelay = False

        self.mostImportantItemSensation = None      # current most important item in conversation
        self.mostImportantVoiceAssociation  = None  # current association most important voice, item said in some previous conversation
                                                    # but not in this conversation
        self.mostImportantVoiceSensation = None     # current most important voice, item said in some previous conversation
                                                    # but not in this conversation
        self.mostImportantImageAssociation  = None  # current association most important image, item said in some previous conversation
                                                    # but not in this conversation
        self.mostImportantImageSensation = None     # current most important image, item said in some previous conversation
                                                    # but not in this conversation
        self.spokedVoiceMuscleSensation = None      # last voice we have said to a person
        self.spokedVoiceCommunicationSensation = None      # last voice we have said to a person
        self.spokedImageMuscleSensation = None      # last voice we have saidt o a person
        self.spokedVoiceCommunicationSensation = None      # last voice we have said to a Robot
        self.spokedImageCommunicationSensation = None      # last voice we have said to a Robot

        self.timer=None
        self.saidSensations = []    # Voices we have said in this conversation 
        self.heardSensations = []   # Voices we have heard in this conversation
        
    '''
    Overridable method to be run just before
    while self.running:
    loop
    
    Say as isCommunication that This MainRobot is present and ready to Communicate
    with other Robots
    '''
        
    def initRobot(self):
        itemSensation = self.createSensation(memoryType=Sensation.MemoryType.Sensory,
                                            sensationType=Sensation.SensationType.Item,
                                            robotType=Sensation.RobotType.Muscle,
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
        # accept heard voices and Item.name presentation Item.name changes
        #sensation.getMemoryType() == Sensation.MemoryType.Working and# No item is Working, voice is Sensory
        if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
            (sensation.getRobotType() == Sensation.RobotType.Sense or\
             sensation.getRobotType() == Sensation.RobotType.Communication):
            # all kind Items found
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
    
                    # if communication is not going on item.name when comes
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got item starting new ={} communication with {}'.format(not self.isConversationOn(), sensation.getName()))
                    self.speak(onStart=not self.isConversationOn()) #itemSensation=sensation)
               elif sensation.getPresence() == Sensation.Presence.Absent and\
                    not self.getMemory().hasPresence() and\
                    self.isConversationOn():
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
                #self.heardSensations.append(sensation.getDataId())

                # if response in a going on conversation 
                if systemTime.time() - sensation.getTime() < Communication.COMMUNICATION_INTERVAL and\
                   self.isConversationOn():
                    if self.mostImportantItemSensation is not None:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as response ' + sensation.toDebugStr()+ ' from ' + self.mostImportantItemSensation.getName())
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as response ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
 
                    if self.timer is not None:
                        self.timer.cancel()
                        self.timer = None
                    # We want to remember this voice
                    #sensation.setMemory(memoryType=Sensation.MemoryType.Working)
                    self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                    # don't use this voice in this same conversation
                    # for reason or another, same voice can be heard twice. accept until we know why to accept
                    #assert sensation.getDataId() not in self.heardSensations
                    if sensation.getDataId() not in self.heardSensations:
                        self.heardSensations.append(sensation.getDataId())
                        while len(self.heardSensations) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
                            del self.heardSensations[0]
                    
                    # mark original item Sensation to be remembered
                    # and also good feeling to the original voice
                    # to this voice will be found again in new conversations
                    # TODO study if we can publish these sensations or not, because is RobotType is Muscle, we speak etc.
                    if self.mostImportantItemSensation is not None:
                        if self.mostImportantItemSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                            self.getMemory().setMemoryType(sensation=self.mostImportantItemSensation, memoryType=Sensation.MemoryType.LongTerm)
                            # publish update to other sites TODO
                            # self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.mostImportantItemSensation)
                    if self.mostImportantVoiceSensation is not None:
                        if self.mostImportantVoiceSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                            self.getMemory().setMemoryType(sensation=self.mostImportantVoiceSensation, memoryType=Sensation.MemoryType.LongTerm)
                            # publish update to other sites TODO
                            # self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.mostImportantVoiceSensation)
                    if self.mostImportantImageSensation is not None:
                        if self.mostImportantImageSensation.getMemoryType() != Sensation.MemoryType.LongTerm:
                            self.getMemory().setMemoryType(sensation=self.mostImportantImageSensation, memoryType=Sensation.MemoryType.LongTerm)
                            # publish update to other sites TODO
                            # self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.mostImportantImageSensation)
                    #  mark also good feeling to original voice we said
#                     if self.mostImportantVoiceAssociation is not None:
#                         self.mostImportantVoiceAssociation.changeFeeling(positive=True) #last voice was a good one because we got a response
                    if self.mostImportantItemSensation is not None and self.mostImportantVoiceSensation is not None:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good voice feeling with ' + self.mostImportantItemSensation.getName())
                        feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                          firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantVoiceSensation,
                                                          positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                    else:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good image feeling but conversation protocol or implementation error ')
                        
                    if self.mostImportantItemSensation is not None and self.mostImportantImageSensation is not None:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good image feeling with ' + self.mostImportantItemSensation.getName())
                        feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                          firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantImageSensation,
                                                          positiveFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen other way
                        self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                    else:
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: good image feeling but conversation implementation did not get image this time error ')
                    
                    if self.getMemory().hasPresence():          
                        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + sensation.getName() + ' got voice and tries to speak with presents ones' + self.getMemory().presenceToStr())
                        self.speak(onStart=False)
                    else:
                        self._isConversationOn = False # present ones are disappeared even if we  head a voice.                       
                # we have someone to talk with
                # time is elapsed, so we can start communicating again with present item.names
                elif not self.isConversationOn() and\
                    self.getMemory().hasPresence() and\
                     (not self.isConversationDelay() or\
                      sensation.getTime() - self.lastConversationEndTime > self.CONVERSATION_INTERVAL):
                    self._isConversationDelay = False
                    # we have still someone to talk with and not yeat started a conversation at all or
                    # enough time is elapses of last conversation
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.toDebugStr())
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' present now' + self.getMemory().presenceToStr())
 
                    # We want to remember this voice
                    self.getMemory().setMemoryType(sensation=sensation, memoryType=Sensation.MemoryType.Working)
                    # don't use this voice in this same conversation
                    assert sensation.getDataId() not in self.heardSensations
                    self.heardSensations.append(sensation.getDataId())
                    while len(self.heardSensations) > Communication.IGNORE_LAST_HEARD_SENSATIONS_LENGTH:
                        del self.heardSensations[0]
                
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='process: got voice as restarted conversation ' + sensation.getName() + ' got voice and tries to speak with presents ones ' + self.getMemory().presenceToStr())
                    self.speak(onStart=True)
            else:
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: not Item or RESPONSE Voice or Image in communication or too soon from last conversation ' + sensation.toDebugStr())
        else:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process: too old sensation or not heard voice or image of detected item ' + sensation.toDebugStr())
        
        sensation.detach(robot=self)    # detach processed sensation
        
    def isConversationOn(self):
        return  self._isConversationOn
        # returnself.mostImportantItemSensation is not None      # when conversaing, we know most important item.name to cerversate with
   
    def isConversationEnded(self):
        return  self._isConversationEnded
    
    def isConversationDelay(self):
        return self._isConversationDelay
        

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
        
        if self.spokedVoiceMuscleSensation is not None:
            self.spokedVoiceMuscleSensation.detach(robot=self)
        self.spokedVoiceMuscleSensation = None
        if self.spokedVoiceCommunicationSensation is not None:
            self.spokedVoiceCommunicationSensation.detach(robot=self)
        self.spokedVoiceCommunicationSensation = None

        self.mostImportantImageAssociation = None
        
        if self.mostImportantImageSensation is not None:
            self.mostImportantImageSensation.detach(robot=self)
        self.mostImportantImageensation  = None

        if self.spokedImageMuscleSensation is not None:
            self.spokedImageMuscleSensation.detach(robot=self)
        self.spokedImageMuscleSensation = None
        if self.spokedImageCommunicationSensation is not None:
            self.spokedImageCommunicationSensation.detach(robot=self)
        self.spokedImageCommunicationSensation = None

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
            self._isConversationOn = True              
        #else:
        if True:
            # we try to find out something to say                
            succeeded=False
            while not succeeded:
                try:
                    for location in self.getMemory()._presentItemSensations.keys():
                        for name, sensation in self.getMemory()._presentItemSensations[location].items():
                    #for name, sensation in self.getMemory().presentItemSensations.items():
#                                 self.getMemory().getMostImportantSensation( sensationType = Sensation.SensationType.Item,
#                                                                      robotType = Sensation.RobotType.Sense,
#                                                                      name = name,
#                                                                      notName = None,
#                                                                      timemin = None,
#                                                                      timemax = None,
#                                                                      associationSensationType=Sensation.SensationType.Voice,
#                                                                      associationDirection = Sensation.RobotType.Sense,
#                                                                      #ignoredSensations = []) # TESTING
#                                                                      ignoredSensations = self.ignoredSensations,
#                                                                      ignoredVoiceLens = self.usedVoiceLens,
#                                                                      searchLength=Communication.SEARCH_LENGTH)
                            candidate_for_communication_item, candidate_for_voice, candidate_for_voice_association,\
                                                              candidate_for_image, candidate_for_image_association = \
                                self.getMemory().getMostImportantCommunicationSensations( 
                                                                     #robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                     robotMainNames=self.getMainNames(),
                                                                     name = name,
                                                                     timemin = None,
                                                                     timemax = None,
                                                                     ignoredSensations = self.saidSensations + self.heardSensations,
                                                                     searchLength=Communication.SEARCH_LENGTH)
                            if candidate_for_voice is not None:
                                assert candidate_for_voice.getDataId() not in self.saidSensations
                                
                            if self.mostImportantItemSensation is None or\
                               (candidate_for_communication_item is not None and\
                               candidate_for_communication_item.getImportance() > self.mostImportantItemSensation.getImportance()):
                                self.mostImportantItemSensation = candidate_for_communication_item
                                self.mostImportantVoiceAssociation = candidate_for_voice_association
                                self.mostImportantVoiceSensation  = candidate_for_voice
                                self.mostImportantImageAssociation = candidate_for_image_association
                                self.mostImportantImageSensation  = candidate_for_image
        
                        if self.mostImportantItemSensation is None:     # if no voices assosiated to present item.names, then any voice will do
#                             self.mostImportantItemSensation, self.mostImportantVoiceAssociation, self.mostImportantVoiceSensation = \
#                                 self.getMemory().getMostImportantSensation( sensationType = Sensation.SensationType.Item,
#                                                                      robotType = Sensation.RobotType.Sense,
#                                                                      name = None,
#                                                                      notName = None,
#                                                                      timemin = None,
#                                                                      timemax = None,
#                                                                      associationSensationType=Sensation.SensationType.Voice,
#                                                                      associationDirection = Sensation.RobotType.Sense,
#                                                                      #ignoredSensations = []) # TESTING
#                                                                      ignoredSensations = self.saidSensations,
#                                                                      ignoredVoiceLens = self.usedVoiceLens,
#                                                                      searchLength=Communication.SEARCH_LENGTH)
                            self.mostImportantItemSensation, self.mostImportantVoiceSensation, self.mostImportantVoiceAssociation,\
                                                             self.mostImportantImageSensation, self.mostImportantImageAssociation =\
                                self.getMemory().getMostImportantCommunicationSensations( 
                                                                     #robotTypes = [Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                                                                     robotMainNames=self.getMainNames(),
                                                                     name = None,
                                                                     timemin = None,
                                                                     timemax = None,
                                                                     ignoredSensations = self.saidSensations + self.heardSensations,
                                                                     searchLength=Communication.SEARCH_LENGTH)
                        succeeded=True  # no exception,  self.getMemory().presentItemSensations did not changed   
                except AssertionError as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: AssertionError ' + str(e) + ' ' + str(traceback.format_exc()))
                    raise e
                except Exception as e:
                    self.log(logLevel=Robot.LogLevel.Critical, logStr='Communication.process speak: ignored exception ' + str(e) + ' ' + str(traceback.format_exc()))

            # TODO self.mostImportantItemSensation is not None             
            if self.mostImportantItemSensation is not None and (self.mostImportantVoiceSensation is not None or self.mostImportantImageSensation is not None):
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantItemSensation OK')
                self.mostImportantItemSensation.attach(robot=self)         #attach Sensation until speaking is ended based on these voices
                if self.mostImportantImageSensation is not None:
                    self.mostImportantImageSensation.attach(robot=self)
                    self.mostImportantImageSensation.save()     # for debug reasons save voices we have spoken as heard voices
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantImageSensation OK')
                    self.spokedImageMuscleSensation = self.createSensation( sensation = self.mostImportantImageSensation, kind=self.getKind(),
                                                                      locations=self.getLocations())
                    # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                    self.spokedImageMuscleSensation.setKind(self.getKind())
                    self.spokedImageMuscleSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
                    # TODO self.mostImportantItemSensation is now None, but it should not be possible             
                    #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantImageSensation)
                    self.getMemory().setMemoryType(sensation=self.spokedImageMuscleSensation, memoryType=Sensation.MemoryType.Sensory)

                    self.spokedImageCommunicationSensation = self.createSensation( sensation = self.mostImportantImageSensation, kind=self.getKind(),
                                                                      locations=self.getLocations())
                    # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                    self.spokedImageCommunicationSensation.setKind(self.getKind())
                    self.spokedImageCommunicationSensation.setRobotType(Sensation.RobotType.Communication)  # Communicate      
                    # TODO self.mostImportantItemSensation is now None, but it should not be possible             
                    #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantImageSensation)
                    self.getMemory().setMemoryType(sensation=self.spokedImageCommunicationSensation, memoryType=Sensation.MemoryType.Sensory)
                    
                    assert self.mostImportantImageSensation.getDataId() not in self.saidSensations                    
                    self.saidSensations.append(self.mostImportantImageSensation.getDataId())   
                    # speak                 
                    self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedImageMuscleSensation)
                    # communicate                 
                    self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedImageCommunicationSensation)

                if self.mostImportantVoiceSensation is not None:        
                    self.mostImportantVoiceSensation.attach(robot=self)
                    self.mostImportantVoiceSensation.save()     # for debug reasons save voices we have spoken as heard voices
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did find self.mostImportantVoiceSensation OK')
                    self.spokedVoiceMuscleSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
                                                                      locations=self.getLocations())
                    # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                    self.spokedVoiceMuscleSensation.setKind(self.getKind())
                    self.spokedVoiceMuscleSensation.setRobotType(Sensation.RobotType.Muscle)  # speak        
                    #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                    self.getMemory().setMemoryType(sensation=self.spokedVoiceMuscleSensation, memoryType=Sensation.MemoryType.Sensory)
                    self.spokedVoiceCommunicationSensation = self.createSensation( sensation = self.mostImportantVoiceSensation, kind=self.getKind(),
                                                                      locations=self.getLocations())
                    # NOTE This is needed now, because Sensation.create parameters robotType and memoryType parameters are  overwritten by sensation parameters
                    self.spokedVoiceCommunicationSensation.setKind(self.getKind())
                    self.spokedVoiceCommunicationSensation.setRobotType(Sensation.RobotType.Communication)  # communicate with Robots      
                    #association = self.mostImportantItemSensation.getAssociation(sensation = self.mostImportantVoiceSensation)
                    self.getMemory().setMemoryType(sensation=self.spokedVoiceCommunicationSensation, memoryType=Sensation.MemoryType.Sensory)

                    #self.saidSensations.append(self.spokedVoiceMuscleSensation.getDataId())
                    assert self.mostImportantVoiceSensation.getDataId() not in self.saidSensations
                    self.saidSensations.append(self.mostImportantVoiceSensation.getDataId())   
                    # speak                 
                    self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceMuscleSensation)
                    # Communicate                
                    self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=self.spokedVoiceCommunicationSensation)
                
                # wait response
                if self.timer is not None:
                    self.timer.cancel() # cancel previous one
                self.timer = threading.Timer(interval=Communication.COMMUNICATION_INTERVAL, function=self.stopWaitingResponse)
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: timer.start()')
                self.timer.start()
                self._isConversationOn = True              
                
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: spoke {}'.format(self.spokedVoiceMuscleSensation.toDebugStr()))
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: commicated {}'.format(self.spokedVoiceCommunicationSensation.toDebugStr()))
            else:
                # We did not find anything to say, but are ready to start new conversation, if someone speaks.
                self._isConversationDelay = False
    
                self.log(logLevel=Robot.LogLevel.Normal, logStr='Communication.process speak: self.getMemory().getMostImportantCommunicationSensations did NOT find self.mostImportantItemSensation')
                self._isConversationOn = False             
                self.clearConversation()

    '''
    We did not get response
    '''
        
    def stopWaitingResponse(self):
        self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: We did not get response")
        
        if self.mostImportantVoiceSensation is not None and self.mostImportantItemSensation is not None:
        
            feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                    firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantVoiceSensation,
                                                    negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen also other way
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Voice self.getParent().getAxon().put do feelingSensation negativeFeeling")
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Voice self.getParent().getAxon().put done")
        if self.mostImportantImageSensation  is not None and self.mostImportantItemSensation is not None:
        
            feelingSensation = self.createSensation(associations=None, sensationType=Sensation.SensationType.Feeling, memoryType=Sensation.MemoryType.Sensory,
                                                    firstAssociateSensation=self.mostImportantItemSensation, otherAssociateSensation=self.mostImportantImageSensation ,
                                                    negativeFeeling=True, locations=self.getLocations())#self.getLocations()) # valid in this location, can be chosen also other way
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Image self.getParent().getAxon().put do feelingSensation negativeFeeling")
            self.getParent().getAxon().put(robot=self, transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="stopWaitingResponse: Image self.getParent().getAxon().put done")
        
        self.endConversation()
        self._isConversationDelay = True

        
    def clearConversation(self):
        if self.mostImportantItemSensation is not None:
            self.mostImportantItemSensation.detach(robot=self)
        self.mostImportantItemSensation = None
        
        self.mostImportantVoiceAssociation  = None
        
        if self.mostImportantVoiceSensation is not None:
            self.mostImportantVoiceSensation.detach(robot=self)
        self.mostImportantVoiceSensation  = None
        
        if self.spokedVoiceMuscleSensation is not None:
            self.spokedVoiceMuscleSensation.detach(robot=self)
        self.spokedVoiceMuscleSensation = None
        if self.spokedVoiceCommunicationSensation is not None:
            self.spokedVoiceCommunicationSensation.detach(robot=self)
        self.spokedVoiceCommunicationSensation = None

        if self.mostImportantImageSensation is not None:
            self.mostImportantImageSensation.detach(robot=self)
        self.mostImportantImageSensation  = None
        
        if self.spokedImageMuscleSensation is not None:
            self.spokedImageMuscleSensation.detach(robot=self)
        self.spokedImageMuscleSensation = None

        if  self.spokedImageCommunicationSensation is not None:
            self.spokedImageCommunicationSensation.detach(robot=self)
        self.spokedImageCommunicationSensation = None

        del self.saidSensations[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
        del self.heardSensations[:]                          # clear used voices, communication is ended, so used voices are free to be used in next conversation.
        
    def endConversation(self):
        self.clearConversation()
        self.timer = None
        self.lastConversationEndTime=systemTime.time()
        self._isConversationOn = False
        self._isConversationEnded = True
        self._isConversationDelay = True

        

