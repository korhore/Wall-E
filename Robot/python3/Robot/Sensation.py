'''
Created on Feb 25, 2013
Edited on 25.10.2021

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''

from PIL import Image as PIL_Image
from enum import Enum
import io
import math
import os
import psutil
import random
import struct
import sys

import time as systemTime


#def enum(**enums):
#    return type('Enum', (), enums)
LIST_SEPARATOR=':'

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


'''
Sensation is something Robot senses
'''

class Sensation(object):
    VERSION=23          # version number to check, if we picle or bytes same version
                        # instances. Otherwise we get odd errors, with old
                        # version code instances

    SEARCH_LENGTH=10    # How many response voices we check
    # Association logging max-values                      
    ASSOCIATIONS_LOG_MAX_LEVEL =   10
    ASSOCIATIONS_LOG_MAX_PARENTS = 10           
    ASSOCIATIONS_MAX_ASSOCIATIONS = 50           

    IMAGE_FORMAT =      'jpeg'
    MODE =              'RGB'       # PIL_IMAGE mode, not used now, but this it is
    DATADIR =           'data'
    VOICE_FORMAT =      'wav'
    PICLE_FILENAME =    'Sensation.pkl'
    BINARY_FORMAT =     'bin'
    
    PATH_TO_PICLE_FILE = os.path.join(DATADIR, PICLE_FILENAME)
    LOWPOINT_NUMBERVARIANCE=-100.0
    HIGHPOINT_NUMBERVARIANCE=100.0
    
    SENSORY_LIVE_TIME =     120.0;       # sensory sensation lives 120 seconds = 2 mins (may be changed)
    WORKING_LIVE_TIME =     1200.0;       # cache sensation 600 seconds = 20 mins (may be changed)
    #LONG_TERM_LIVE_TIME =   3000.0;       # cache sensation 3000 seconds = 50 mins (may be changed)
    LONG_TERM_LIVE_TIME =   24.0*3600.0;  # cache sensation 24h (may be changed)
    ### Cleanup
    MIN_CACHE_MEMORABILITY = 0.1                            # starting value of min memorability in sensation cache
    min_cache_memorability = MIN_CACHE_MEMORABILITY          # current value min memorability in sensation cache
    MAX_MIN_CACHE_MEMORABILITY = 1.6                         # max value of min memorability in sensation cache we think application does something sensible
                                                             # Makes Sensory memoryType above 150s, which should be enough
    NEAR_MAX_MIN_CACHE_MEMORABILITY = 1.5                    # max value of min memorability in sensation cache we think application does something sensible
    MIN_MIN_CACHE_MEMORABILITY = 0.1                         # min value of min memorability in sensation cache we think application does everything well and no need to
                                                             # set min_cache_memorability lower
    MIN_SCORE = 0.1                                          # min score all Sensations have score > 0 to get Memorability. This is lower than detected Item.name

    NEAR_MIN_MIN_CACHE_MEMORABILITY = 0.2                    
    startSensationMemoryUsageLevel = 0.0                     # start memory usage level after creating first Sensation
    currentSensationMemoryUsageLevel = 0.0                   # current memory usage level when creating last Sensation
    maxRss = 384.0                                           # how much there is space for Sensation as maxim MainRobot sets this from its Config
    minAvailMem = 50.0                                       # how available momory must be left. MainRobot sets this from its Config
    process = psutil.Process(os.getpid())                    # get pid of current process, so we can calculate Process memory usage
    ### Cleanup
    #
    
    LENGTH_SIZE =       2   # Sensation as string can only be 99 character long
    LENGTH_FORMAT =     "{0:2d}"
    SEPARATOR =         '|'  # Separator between messages
    SEPARATOR_SIZE =    1  # Separator length
    
    ENUM_SIZE =         1
    ID_SIZE =           4
    BYTEORDER =         "little"
    FLOAT_PACK_TYPE =   "d"
    FLOAT_PACK_SIZE =   8
    TRUE_AS_BYTE  =     b'\x01'
    FALSE_AS_BYTE  =    b'\x00'
    TRUE_AS_INT  =      1
    FALSE_AS_INR  =     0
    TRUE_AS_STR  =      'T'
    FALSE_AS_STR  =     'F'
     
    # SensationType 
    SensationType = enum(Drive='a', Stop='b', Robot='c', Azimuth='d', Acceleration='e', Location='f', Observation='g', HearDirection='h',
                         Voice='i', Image='j',  Calibrate='k', Capability='l', Item='m', Feeling='n', RobotState='o', Unknown='p', All='q')
    # RobotType of a sensation. Example in Voice: Muscle: Speaking,  Sense: Hearing In->Muscle Out->Sense
    RobotType = enum(Muscle='M', Sense='S', Communication ='C', All='A')
    # RobotType of a sensation transferring, used with Axon. Up: going up like from AlsaMicroPhone to MainRobot, Down: going down from MainRobot to leaf Robots like AlsaPlayback
    TransferDirection = enum(Direct = 'a', Up = 'b', Down='c')
    # Presence of Item  
    Presence = enum(Entering='a', Present='b', Exiting='c', Absent='d', Unknown='e')

    MemoryType = enum(Sensory='S', Working='W', LongTerm='L' , All='A')
    #MemoryType = enum(Sensory='S', LongTerm='L' )
    Kind = enum(WallE='w', Eva='e', Normal='n')
    InstanceType = enum(Real='r', SubInstance='s', Virtual='v', Remote='m')
    Mode = enum(Normal='n', StudyOwnIdentity='t',Sleeping='l',Starting='s', Stopping='p', Interrupted='i')

    # Robots states    
    RobotState = enum(#Activity level
                      ActivitySleeping='a',
                      ActivityDreaming='b',
                      ActivityLazy='c',
                      ActivityRelaxed='d',
                      ActivityNormal='e',
                      ActivityBusy='f',
                      ActivityHurry='g',
                      ActivityTired='h',
                      ActivityBreaking='i',
                      
                      # Communication
                      CommunicationNotStarted = 'j',
                      CommunicationWaiting = 'k',
                      CommunicationOn ='l',
                      CommunicationNoResponseToSay='m',
                      CommunicationEnded ='n',
                      CommunicationDelay = '0')
    
    # enum items as strings    
    ALL="All"
    MUSCLE="Muscle"
    SENSE="Sense"
    COMMUNICATION="Communication"
    SENSORY="Sensory"
    WORKING="Working"
    LONG_TERM="LongTerm"
    DRIVE="Drive"
    STOP="Stop"
    ROBOT="Robot"
    AZIMUTH="Azimuth"
    ACCELERATION="Acceleration"
    LOCATION="Location"
    OBSERVATION="Observation"
    HEARDIRECTION="HearDirection"
    VOICE="Voice"
    IMAGE="Image"
    CALIBRATE="Calibrate"
    CAPABILITY="Capability"
    ITEM="Item"
    FEELING="Feeling"
    ROBOTSTATE="RobotState"
    UNKNOWN="Unknown"
    KIND="Kind"
    WALLE="Wall-E"
    EVA="Eva"
    NORMAL="Normal"
    REAL="Real"
    SUBINSTANCE="SubInstance"
    VIRTUAL="Virtual"
    REMOTE="Remote"
    NORMAL="Normal"
    STUDYOWNIDENTITY="StudyOwnIdentity"
    SLEEPING="Sleeping"
    STARTING="Starting"
    STOPPING="Stopping"
    INTERRUPTED="Interrupted"
    ENTERING="Entering"
    PRESENT="Present"
    EXITING="Exiting"
    ABSENT="Absent"
    # Activity 
    ACTIVITYSPEEPING="Sleeping"
    ATIVITYDREAMING="Dreaming"
    ACTIVITYLAZY="Lazy"
    ACTIVITYRELAXED="Relaxed"
    ACTIVITYNORMAL="Normal"
    ACTIVITYBUSY="Busy"
    ACTIVITYHURRY="Hurry"
    ACTIVITYTIRED="Tired"
    ACTIVITYBEAKING="Breaking"
    # Communication
    COMMUNIVATIONNOTSTARTED="Not Started"
    COMMUNICATIONWAITING="Waiting"
    COMMUNICATIONON="On"
    COMMUNICATIONNORESPONSETOSAY="No Response To Say"
    COMMUNICATIONENDED="Ended"
    COMMUNICATIONDELAY="Delay"


      
    RobotTypes={RobotType.Muscle: MUSCLE,
                RobotType.Sense: SENSE,
                RobotType.Communication: COMMUNICATION,
                RobotType.All: ALL}
    NormalRobotTypes={RobotType.Muscle: MUSCLE,
                RobotType.Sense: SENSE,
                RobotType.Communication: COMMUNICATION}
    RobotTypesOrdered=(
                RobotType.Muscle,
                RobotType.Sense,
                RobotType.Communication,
                RobotType.All)
    NormalRobotTypesOrdered=(
                RobotType.Muscle,
                RobotType.Sense,
                RobotType.Communication)
    
    MemoryTypes = {
               MemoryType.Sensory: SENSORY,
               MemoryType.Working: WORKING,
               MemoryType.LongTerm: LONG_TERM,
               MemoryType.All: ALL}
    NormalMemoryTypes = {
               MemoryType.Sensory: SENSORY,
               MemoryType.Working: WORKING,
               MemoryType.LongTerm: LONG_TERM}
    MemoryTypesOrdered = (
               MemoryType.Sensory,
               MemoryType.Working,
               MemoryType.LongTerm,
               MemoryType.All)
    NormalMemoryTypesOrdered = (
               MemoryType.Sensory,
               MemoryType.Working,
               MemoryType.LongTerm)
    # QoSMemoryTypesOrdered is used in Axon
    QoSMemoryTypesOrdered = (
               MemoryType.Working,
               MemoryType.LongTerm)
    
    SensationTypes={
               SensationType.Drive: DRIVE,
               SensationType.Stop: STOP,
               SensationType.Robot: ROBOT,
               SensationType.Azimuth: AZIMUTH,
               SensationType.Acceleration: ACCELERATION,
               SensationType.Location: LOCATION,
               SensationType.Observation: OBSERVATION,
               SensationType.HearDirection: HEARDIRECTION,
               SensationType.Voice: VOICE,
               SensationType.Image: IMAGE,
               SensationType.Calibrate: CALIBRATE,
               SensationType.Capability: CAPABILITY,
               SensationType.Item: ITEM,
               SensationType.Feeling: FEELING,             
               SensationType.RobotState: ROBOTSTATE,             
               SensationType.Unknown: UNKNOWN,
               SensationType.All: ALL}
    
    RobotStates={
              # Activity          
               RobotState.ActivitySleeping: ACTIVITYSPEEPING,
               RobotState.ActivityDreaming:ATIVITYDREAMING,
               RobotState.ActivityLazy:ACTIVITYLAZY,
               RobotState.ActivityRelaxed:ACTIVITYRELAXED,
               RobotState.ActivityNormal:ACTIVITYNORMAL,
               RobotState.ActivityBusy:ACTIVITYBUSY,
               RobotState.ActivityHurry:ACTIVITYHURRY,
               RobotState.ActivityTired:ACTIVITYTIRED,
               RobotState.ActivityBreaking:ACTIVITYBEAKING,
                      
                # Communication
               RobotState.CommunicationNotStarted:COMMUNIVATIONNOTSTARTED,
               RobotState.CommunicationWaiting:COMMUNICATIONWAITING,
               RobotState.CommunicationOn:COMMUNICATIONON,
               RobotState.CommunicationNoResponseToSay:COMMUNICATIONNORESPONSETOSAY,
               RobotState.CommunicationEnded:COMMUNICATIONENDED,
               RobotState.CommunicationDelay:COMMUNICATIONDELAY}
    
    NormalSensationTypes={
               SensationType.Drive: DRIVE,
               SensationType.Stop: STOP,
               SensationType.Robot: ROBOT,
               SensationType.Azimuth: AZIMUTH,
               SensationType.Acceleration: ACCELERATION,
               SensationType.Location: LOCATION,
               SensationType.Observation: OBSERVATION,
               SensationType.HearDirection: HEARDIRECTION,
               SensationType.Voice: VOICE,
               SensationType.Image: IMAGE,
               SensationType.Calibrate: CALIBRATE,
               SensationType.Capability: CAPABILITY,
               SensationType.Item: ITEM,
               SensationType.Feeling: FEELING,             
               SensationType.RobotState: ROBOTSTATE,             
               SensationType.Unknown: UNKNOWN}
    # Sensation type, that can handle originality when copied. meaning
    # that Sensations data is saved in original Sensation and possible copies
    # have references to original data, but data is not copied to them and
    # methods isOriginal tells if this is sensatuon vontain copy of data or not
    # If SensationType is not within these types, then copy of SXensation is
    # always a copy, so also copied Sensations are orginal ones even if in memory
    # can be Sensations, the data is exactly same.
    # OriginalitySensationTypes can be changes in future, if we decide originality information
    # is valuable, but now originality is handled as technical information
    # without logical information. But as said above, this planning idiea can be changed in future.
    OriginalitySensationTypes={
               SensationType.Location: LOCATION,
               SensationType.Voice: VOICE,
               SensationType.Image: IMAGE,
               SensationType.Item: ITEM,
               SensationType.Feeling: FEELING}
    SensationTypesOrdered=(
               SensationType.Drive,
               SensationType.Stop,
               SensationType.Robot,
               SensationType.Azimuth,
               SensationType.Acceleration,
               SensationType.Location,
               SensationType.Observation,
               SensationType.HearDirection,
               SensationType.Voice,
               SensationType.Image,
               SensationType.Calibrate,
               SensationType.Capability,
               SensationType.Item,
               SensationType.Feeling,
               SensationType.RobotState,
               SensationType.Unknown,
               SensationType.All)
    NormalSensationTypesOrdered=(
               SensationType.Drive,
               SensationType.Stop,
               SensationType.Robot,
               SensationType.Azimuth,
               SensationType.Acceleration,
               SensationType.Location,
               SensationType.Observation,
               SensationType.HearDirection,
               SensationType.Voice,
               SensationType.Image,
               SensationType.Calibrate,
               SensationType.Capability,
               SensationType.Item,
               SensationType.Feeling,
               SensationType.RobotState,
               SensationType.Unknown)
    OriginalitySensationTypesOrdered=(
               SensationType.Location,
               SensationType.Voice,
               SensationType.Image,
               SensationType.Item,
               SensationType.Feeling)
    
    Kinds={Kind.WallE: WALLE,
           Kind.Eva: EVA,
           Kind.Normal: NORMAL}
    InstanceTypes={InstanceType.Real: REAL,
                   InstanceType.SubInstance: SUBINSTANCE,
                   InstanceType.Virtual: VIRTUAL,
                   InstanceType.Remote: REMOTE}

    Modes={Mode.Normal: NORMAL,
           Mode.StudyOwnIdentity: STUDYOWNIDENTITY,
           Mode.Sleeping: SLEEPING,
           Mode.Starting: STARTING,
           Mode.Stopping: STOPPING,
           Mode.Interrupted: INTERRUPTED}
    
    Presences = {
           Presence.Entering: ENTERING,
           Presence.Present:  PRESENT,
           Presence.Exiting:  EXITING,
           Presence.Absent:   ABSENT,
           Presence.Unknown:  UNKNOWN}

     # Sensation cache times
    sensationMemoryLiveTimes={
        MemoryType.Sensory:  SENSORY_LIVE_TIME,
        MemoryType.Working:  WORKING_LIVE_TIME,
        MemoryType.LongTerm: LONG_TERM_LIVE_TIME}#,
        #MemoryType.All: LONG_TERM_LIVE_TIME }
    
    # Feeling
    Terrified='Terrified' 
    Afraid='Afraid'
    Disappointed='Disappointed'
    Worried='Worried'
    Neutral='Neutral'
    Normal='Normal'
    Good='Good'
    Happy='Happy'
    InLove='InLove'
    # Feeling, Feelings can be positive or negative, stronger or weaker
    Feeling = enum(Terrified=-1000, Afraid=-100, Disappointed=-10, Worried=-1, Neutral=0, Normal=1, Good=10, Happy=100, InLove=1000)
    Feelings = {
        Feeling.Terrified : Terrified,
        Feeling.Afraid : Afraid,
        Feeling.Disappointed : Disappointed,
        Feeling.Worried : Worried,
        Feeling.Neutral : Neutral,
        Feeling.Normal : Normal,
        Feeling.Good : Good,
        Feeling.Happy : Happy,
        Feeling.InLove : InLove
    }

    # ActivityLevel
    BreakingActivityLevel='Breaking' 
    TiredActivityLevel='Tired'
    HurryActivityLevel='Hurry'
    BusyActivityLevel='Busy'
    NormalActivityLevel='Normal'
    RelaxedActivityLevel='Relaxed'
    LazyActivityLevel='Lazy'
    DreamingActivityLevel='Dreaming'
    SleepingActivityLevel = 'Sleeping'
    # Feeling, Feelings can be positive or negative, stronger or weaker
    ActivityLevel = enum(Sleeping=-4, Dreaming=-3, Lazy=-2, Relaxed=-1,Normal=0, Busy=1, Hurry=2, Tired=3, Breaking=4)
    ActivityLevels = {
        ActivityLevel.Sleeping : SleepingActivityLevel,
        ActivityLevel.Dreaming : DreamingActivityLevel,
        ActivityLevel.Lazy : LazyActivityLevel,
        ActivityLevel.Relaxed : RelaxedActivityLevel,
        ActivityLevel.Normal : NormalActivityLevel,
        ActivityLevel.Busy : BusyActivityLevel,
        ActivityLevel.Hurry : HurryActivityLevel,
        ActivityLevel.Tired : TiredActivityLevel,
        ActivityLevel.Breaking : BreakingActivityLevel
    }

    # The idea is keep Sensation in runtime memory if
    # there is a association for them for instance 10 mins
    #
    # After that we can produce higher level Sensations
    # with memory attribute in higher level,
    # Working or Memory, that association to basic
    # memory level, that is Sensory level.
    # That way we can produce meanings is higher level
    # of low level sensations. For instance we can get
    # a image (Sensory) and process it with tnsorFlow
    # which classifies it as get words and get
    # Working or Memory level Sensations that refers
    # to the original hearing, a Image, meaning
    # that robot has seen it at certain time.
    # THigher level Sensation can be processed also and
    # we can save original image in a file with
    # its classified names. After that our robot
    # knows how those classifies names look like,
    # what is has seen. 
    
    # byte conversions
    # try unicode-escape instead of utf8 toavoid error with non ascii characters bytes
    def strToBytes(e):
        return e.encode('unicode-escape')
    
    def bytesToStr(b):
        try:
            return b.decode('unicode-escape')
        except UnicodeDecodeError as e:
            print ('UnicodeDecodeError ' + str(e))
            return ''
        
    def listToBytes(l):
        ret_s = ''
        if l is not None:
            i=0
            for s in l:
                if i == 0:
                    ret_s = s
                else:
                    ret_s += LIST_SEPARATOR + s
                i = i+1
        return Sensation.strToBytes(ret_s)
        
    def bytesToList(b):
        #print('bytesToList b ' +str(b))
    
        ret_s = Sensation.bytesToStr(b)
        #print('bytesToList ret_s ' +str(ret_s))
        if len(ret_s) > 0:
            return ret_s.split(LIST_SEPARATOR)
        return []
    
    def strListToFloatList(l):
        ret_s = []
        if l is not None:
            for s in l:
                ret_s.append(float(s))
        return ret_s
    
    
    def floatToBytes(f):
        return bytearray(struct.pack(Sensation.FLOAT_PACK_TYPE, f)) 
    
    def bytesToFloat(b):
        return struct.unpack(Sensation.FLOAT_PACK_TYPE, b)[0]
    
    def booleanToBytes(boolean):
        if boolean:
            return Sensation.TRUE_AS_BYTE
        return Sensation.FALSE_AS_BYTE
    
    def bytesToBoolean(b):
        if b == Sensation.TRUE_AS_BYTE:
            return True
        return False
    def intToBoolean(i):
        if i == Sensation.TRUE_AS_INT:
            return True
        return False

    
    #helpers
        
    def getSensationTypeString(sensationType):
        ret = Sensation.SensationTypes.get(sensationType)
        return ret
    def getSensationTypeStrings():
        return Sensation.SensationTypes.values()
          
    def getRobotTypeString(robotType):
        ret = Sensation.RobotTypes.get(robotType)
        return ret
    def getRobotTypeStrings():
        return Sensation.RobotTypes.values()
    
    def getMemoryTypeString(memoryType):
        ret = Sensation.MemoryTypes.get(memoryType)
        return ret
    def getMemoryTypeStrings():
        return Sensation.MemoryTypes.values()
    
    def getSensationTypeString(sensationType):
        return Sensation.SensationTypes.get(sensationType)
    def getSensationTypeStrings():
        return Sensation.SensationTypes.values()
    
    def getPresenceString(presence):
        return Sensation.Presences.get(presence)
    def getPresenceStrings():
        return Sensation.Presences.values()

    def getKindString(kind):
        return Sensation.Kinds.get(kind)
    def getKindStrings():
        return Sensation.Kinds.values()

    def getFeelingString(feeling):
        if feeling == None:
            return ""
        return Sensation.Feelings.get(feeling)
    def getFeelingStrings():
        return Sensation.Feelings.values()
        


    def getRobotStateString(robotState):
        if robotState == None:
            return ""
        return Sensation.RobotStates.get(robotState)
    def getRobotStateStrings():
        return Sensation.RobotStates.values()
        

    def getActivityLevelString(activityLevel):
        if activityLevel== None:
            return ""
        return Sensation.ActivityLevels.get(activityLevel)
    def getActivityLevelStrings():
        return Sensation.ActivityLevels.values()
        
    '''
    get memory usage
    '''
    def getMemoryUsage():     
         #memUsage= resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0            
        return Sensation.process.memory_info().rss/(1024*1024)              # hope this works better
    
    '''
    get available memory
    '''
    def getAvailableMemory():
        return psutil.virtual_memory().available/(1024*1024)
    
        
    def strArrayToStr(sArray):
        retS = ''
        if sArray != None:
            for s in sArray:
                if len(retS) == 0:
                    retS=s
                else:
                    retS += ' ' + s
        return retS
    
    def strToStrArray(s):
        return s.split(' ')
    
         
    '''
    Association is a association between two sensations
    There is time when used, so we cab calculate strength of this association.
    Association can be only with Long Term and Work Memory Sensations, because Sensory
    sensations don't live that long.
    Work Memory Associations can't be save but Long Term Memory Association can.
    Owner is nor mentioned, so we have only one sensation in one association
    Association are identical in both sides, so reverse Association is found
    in connected Sensation.
    '''
        
    class Association(object):
        
        def __init__(self,
                     self_sensation,                        # this side of Association
                     sensation,                             # sensation to connect
                     feeling,                               # feeling of association two sensations
                     time=None):                            # last used
#                     feeling = Sensation.Feeling.Neutral):  # feeling of association two sensations
                                                            # stronger feeling make us (and robots) to remember association
                                                            # longer than neutral associations
                                                            # our behaver (and) robots has to goal to get good feelings
                                                            # and avoid negative ones
                                                            # first usage of feeling is with Communication-Robot, make it
                                                            # classify Voices with good feeling when it gets responses
                                                            # and feel CVoice use with bad feeling, if it does not
                                                            # get a response
            self.time = time
            if self.time == None:
                self.time = systemTime.time()
            self.self_sensation = self_sensation
            self.sensation = sensation
            self.feeling = feeling

        def getTime(self):
            return self.time
    
        def setTime(self, time = None):
            if time == None:
                time = systemTime.time()
            self.time = time
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            association.time = time
 
        '''
        get age in seconds
        Should not return zero, so 0.1 is minumum
        '''            
        def getAge(self):
            age = systemTime.time() - self.getTime()
            if age < 0.1:
                return 0.1
            return age
     
        def getSelfSensation(self):
            return self.self_sensation
        
        def getSensation(self):
            return self.sensation


        ''''
        setSensation is tricky
        We should first remove old Association from Association.sensation
        and add this new Association
        so for now this is not allowed, but should be done explicit way
        
        def setSensation(self, sensation):
            self.sensation = sensation
            # other part
            association = self.getAssociation(self.sensation)
            if association is None:
               self.sensation.addAssociation(self) 
            else:
                association.time = self.time
                association.feeling = self.feeling
        '''
    
        def getFeeling(self):
            return self.feeling
    
        def setFeeling(self, feeling):
            self.feeling = feeling
            self.setTime()
            # other part
            association = self.sensation.getAssociation(self.self_sensation)
            if association is not None:
                association.feeling = feeling
        
        '''
        Change feeling to more positive or negative way
        '''    
        def changeFeeling(self, positive=False, negative=False, otherPart=False):
            # this part
            self.doChangeFeeling(association=self, positive=positive, negative=negative)
            if otherPart:
                association = self.sensation.getAssociation(self.self_sensation)
                if association is not None:
                    self.doChangeFeeling(association=association, positive=positive, negative=negative)

        '''
        helper association Change feeling to more positive or negative way
        '''    
        def doChangeFeeling(self, association, positive=False, negative=False):
            if positive or not negative: # must be positive
                if association.feeling == Sensation.Feeling.Terrified:
                    association.feeling = Sensation.Feeling.Afraid
                elif association.feeling == Sensation.Feeling.Afraid:
                    association.feeling = Sensation.Feeling.Disappointed
                elif association.feeling == Sensation.Feeling.Disappointed:
                    association.feeling = Sensation.Feeling.Worried
                elif association.feeling == Sensation.Feeling.Worried:
                    association.feeling = Sensation.Feeling.Neutral
                elif association.feeling == Sensation.Feeling.Neutral:
                    association.feeling = Sensation.Feeling.Normal
                elif association.feeling == Sensation.Feeling.Normal:
                    association.feeling = Sensation.Feeling.Good
                elif association.feeling == Sensation.Feeling.Good:
                    association.feeling = Sensation.Feeling.Happy
                elif association.feeling == Sensation.Feeling.Happy:
                    association.feeling = Sensation.Feeling.InLove
            else:
                if association.feeling == Sensation.Feeling.Afraid:
                    association.feeling = Sensation.Feeling.Terrified
                elif association.feeling == Sensation.Feeling.Disappointed:
                    association.feeling = Sensation.Feeling.Afraid
                elif association.feeling == Sensation.Feeling.Worried:
                    association.feeling = Sensation.Feeling.Disappointed
                elif association.feeling == Sensation.Feeling.Neutral:
                    association.feeling = Sensation.Feeling.Worried
                elif association.feeling == Sensation.Feeling.Normal:
                    association.feeling = Sensation.Feeling.Neutral
                elif association.feeling == Sensation.Feeling.Good:
                    association.feeling = Sensation.Feeling.Normal
                elif association.feeling == Sensation.Feeling.Happy:
                    association.feeling = Sensation.Feeling.Good
                elif association.feeling == Sensation.Feeling.InLove:
                    association.feeling = Sensation.Feeling.Happy
                    
            association.setTime()

        '''
        How important this association is.
        
        Pleasant most important Associations get high positive value,
        unpleasant most important Association get high negative value and
        meaningless Association get value near zero.
        
        Uses now Feeling as main factor and score as minor factor.
        Should use also time, so old Associations are not so important than
        new ones.
        
        deprecated
        '''
#         def getImportance(self):
#             if self.feeling >= 0:
#                 return float(self.feeling+1) * (1.0 + self.self_sensation.getScore())
#             return float(self.feeling-1) * (1.0 + self.self_sensation.getScore())
        

    '''
    AssociationSensationIds is a association between two sensations ids
    It is helper class to save information of real association with sensations
    '''
        
    class AssociationSensationIds(object):
        
        def __init__(self,
                     sensation_id,                          # sensation_id to connect
                     feeling,                               # feeling of association two sensation_ids
                     time=None):                            # last used
            self.time = time
            if self.time == None:
                self.time = systemTime.time()
            self.sensation_id = sensation_id
            self.feeling = feeling

        def getTime(self):
            return self.time
    
        def setTime(self, time = None):
            if time == None:
                time = systemTime.time()
            self.time = time
             
        def getSensationId(self):
            return self.sensation_id
    
        def getFeeling(self):
            return self.feeling
    
        def setFeeling(self, feeling):
            self.feeling = feeling


    '''
    default constructor for Sensation
    '''       
    def __init__(self,
                 memory,
                 robotId,                                                    # robot id (should be always given)
                 associations=None,
                 sensation=None,
                 bytes=None,
                 binaryFilePath=None,
                 id=None,
                 #originalSensationId=None,
                 time=None,
                 receivedFrom=[],
                 # base field are by default None, so we know what fields are given and what not
                 sensationType = None,
                 memoryType = None,
                 robotType = None,
                 robot = None,
                 locations =  None,
                 #isCommunication = False,
                 mainNames =  None,
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
                                       
        from Config import Capabilities
        self.time=time
        if self.time == None:
            self.time = systemTime.time()

        self.robotId = robotId
        
        self.id = id
        if self.id == None:
            self.id = Sensation.getNextId()

# depreacated            
#         self.dataId = dataId
#         if self.dataId == None:
#             self.dataId = self.id
            
        self.attachedBy = []
        self.associations =[]
        if  associations == None:
            associations = []
        # associate makes both sides
        for association in associations:
            self.associate(sensation=association.sensation,
                           time=association.time,
                           feeling=association.feeling)
        self.potentialAssociations = [] # does not have init value in creation,
                                        # but is always empty in creation
                                       # associations are always both way
                                       
        # copy
        self.originalSensation = None # references to Sensation, that holds riginal data or image
        self.originalSensationId = self.id #None # id of originalSensation when self.originalSensation is not in Memory
                                        # we use this to set self.originalSensation and to detetec if this Sensation is Original Sensatioj por copy
                                        # there are situations, when 
        self.copySensations = []      # if this Sensation is original Sensation
                                      # then this arryy contains referencess Sensations
                                      # that have reference to this Sensations data ot image
                                      # This to bookkeeping where referencces are
                                      # because data of sound and image as picture use a lot ofr memory
                                      # and we will have ionly one vopy of those data
                                      # and copySensations will have only reference to original one
        self.copySensationIds = []   # ids of self.copySensations
                                      # used to load self.copySensations and setting data and image references, when original Sensation is loaded

        if sensation is not None:   # copy constructor
            # associate makes both sides
            Sensation.updateBaseFields(destination=self, source=sensation,
                                       #originalSensationId = originalSensationId,
                                       sensationType=sensationType,
                                       memoryType=memoryType,
                                       robotType=robotType,
                                       robot=robot,
                                       locations=locations,
                                       #isCommunication=isCommunication,
                                       mainNames=mainNames,
                                       leftPower=leftPower,rightPower=rightPower,                   # Walle motors state
                                       azimuth=azimuth,                                             # Walle robotType relative to magnetic north pole
                                       x=x, y=y, z=z, radius=radius,                                # location and acceleration of Robot
                                       hearDirection=hearDirection,                                 # sound robotType heard by Walle, relative to Walle
                                       observationDirection=observationDirection,
                                       observationDistance=observationDistance,                     # Walle's observation of something, relative to Walle
                                       filePath=filePath,
                                       data=data,                                                   # ALSA voice is string (uncompressed voice information)
                                       image=image,                                                 # Image internal representation is PIl.Image 
                                       calibrateSensationType=calibrateSensationType,
                                       capabilities=capabilities,                                   # capabilitis of sensorys, robotType what way sensation go
                                       name=name,                                                   # name of Item
                                       score=score,                                                 # used at least with item to define how good was the detection 0.0 - 1.0
                                       presence=presence,                                           # presence of Item
                                       kind=kind,                                                   # kind (for instance voice)
                                       firstAssociateSensation=firstAssociateSensation,             # associated sensation first side
                                       otherAssociateSensation=otherAssociateSensation,             # associated Sensation other side
                                       feeling=feeling,                                             # feeling of sensation or association
                                       positiveFeeling=positiveFeeling,                             # change association feeling to more positive robotType if possible
                                       negativeFeeling=negativeFeeling,
                                       robotState = robotState)                                       
            for association in sensation.associations:
                self.associate(sensation=association.sensation,
                               time=association.time,
                               feeling=association.feeling)
                
            #self.receivedFrom=sensation.receivedFrom
            # do deep copy
            self.receivedFrom=[]
            self.addReceivedFrom(sensation.receivedFrom)
            
#             self.sensationType = sensation.sensationType
#             if memoryType == None:
#                 self.memoryType = sensation.memoryType
#             else:
#                 self.memoryType = memoryType
                
            # We have here put values from sensation, but we should
            # also set values that are overwritten
            # and we don't know them exactly
            # so we don't set then, but code should use set methods itself explicitly
            
            # only way to solve this is set default values to None and for every
            # property set only those properties, that are both None
            
            # this will cause that, that if constructor, where no sensation is given,
            # we should set default value by hand.

        else:            
            Sensation.setBaseFields(   destination=self,
                                       sensationType=sensationType,
                                       memoryType=memoryType,
                                       robotType=robotType,
                                       robot=robot,
                                       locations=locations,
                                       #isCommunication=isCommunication,
                                       mainNames=mainNames,
                                       leftPower=leftPower,rightPower=rightPower,                   # Walle motors state
                                       azimuth=azimuth,                                             # Walle robotType relative to magnetic north pole
                                       x=x, y=y, z=z, radius=radius,                                # location and acceleration of Robot
                                       hearDirection=hearDirection,                                 # sound robotType heard by Walle, relative to Walle
                                       observationDirection=observationDirection,
                                       observationDistance=observationDistance,                     # Walle's observation of something, relative to Walle
                                       filePath=filePath,
                                       data=data,                                                   # ALSA voice is string (uncompressed voice information)
                                       image=image,                                                 # Image internal representation is PIl.Image 
                                       calibrateSensationType=calibrateSensationType,
                                       capabilities=capabilities,                                   # capabilitis of sensorys, robotType what way sensation go
                                       name=name,                                                   # name of Item
                                       score=score,                                                 # used at least with item to define how good was the detection 0.0 - 1.0
                                       presence=presence,                                           # presence of Item
                                       kind=kind,                                                   # kind (for instance voice)
                                       firstAssociateSensation=firstAssociateSensation,             # associated sensation first side
                                       otherAssociateSensation=otherAssociateSensation,             # associated Sensation other side
                                       feeling=feeling,                                             # feeling of sensation or association
                                       positiveFeeling=positiveFeeling,                             # change association feeling to more positive robotType if possible
                                       negativeFeeling=negativeFeeling,
                                       robotState=robotState)                                       
                          
#             self.sensationType = sensationType
#             if memoryType == None:
#                 self.memoryType = Sensation.MemoryType.Sensory
#             else:
#                 self.memoryType = memoryType
#             self.robotType = robotType
#             self.robot = robot
#             self.locations = locations
#             #self.isCommunication = isCommunication,
#             self.mainNames = mainNames
#             self.leftPower = leftPower
#             self.rightPower = rightPower
#             self.hearDirection = hearDirection
#             self.azimuth = azimuth
#             self.x = x
#             self.y = y
#             self.z = z
#             self.radius = radius
#             self.observationDirection = observationDirection
#             self.observationDistance = observationDistance
#             self.filePath = filePath
#             self.data = data
#             self.image = image
#             self.calibrateSensationType = calibrateSensationType
#             self.capabilities = capabilities
#             self.name = name
#             self.score = score
#             self.presence = presence
#             self.kind = kind
#             self.firstAssociateSensation = firstAssociateSensation
#             self.otherAssociateSensation = otherAssociateSensation
#             self.feeling = feeling
#             self.positiveFeeling = positiveFeeling
#             self.negativeFeeling = negativeFeeling

            self.attachedBy = []
           
            # associate makes both sides
            for association in associations:
                self.associate(sensation=association.sensation,
                               time=association.time,
                               feeling=association.feeling)
           
#             if receivedFrom == None:
#                 receivedFrom=[]
#             self.receivedFrom=[]
#             self.addReceivedFrom(receivedFrom)
            #self.receivedFrom=receivedFrom
            # do deep copy
            self.receivedFrom=[]
            self.addReceivedFrom(receivedFrom)
            
        if binaryFilePath != None:
            try:
                if os.path.exists(binaryFilePath):
                    try:
                        with open(binaryFilePath, "rb") as f:
                            try:
                                bytes = f.read()
                            except IOError as e:
                                print("Sensation bytes = f.read({}) error {}".binaryFilePath, format(str(e)))
                                bytes = None
                            finally:
                                f.close()
                    except Exception as e:
                        print("Sensation bytes open({}), rb) as f error {}".format(binaryFilePath, str(e)))
                        bytes = None
            except Exception as e:
                print('os.path.exists({}) error {}'.format(binaryFilePath, str(e)))

        if bytes != None:
            try:
                l=len(bytes)
                i=0
#                yougestTime=0.0
                #Version of bytes
                b =  Sensation.VERSION.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
                version = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER)
                if version == Sensation.VERSION:    # if same version of bytes
                    i += Sensation.ID_SIZE
    
                    self.robotId = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    self.id = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    self.originalSensationId = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                    i += Sensation.FLOAT_PACK_SIZE
                    
                    copySensationsLen = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    i += Sensation.ID_SIZE
                    for j in range(copySensationsLen):
                        self.copySensationIds.append(Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE]))
                        i += Sensation.FLOAT_PACK_SIZE
                    
                    self.time = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
    #                yougestTime=self.time
                    i += Sensation.FLOAT_PACK_SIZE
    
                    self.memoryType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    #print("memoryType " + str(memoryType))
                    i += Sensation.ENUM_SIZE
                    
                    self.sensationType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    #print("sensationType " + str(sensationType))
                    i += Sensation.ENUM_SIZE
                    
                    self.robotType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                    #print("robotType " + str(robotType))
                    i += Sensation.ENUM_SIZE
                                        
                    self.feeling = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER, signed=True)
                    i += Sensation.ID_SIZE
                    
                    # locations
                    locations_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("locations_size " + str(locations_size))
                    i += Sensation.ID_SIZE
                    self.locations=Sensation.bytesToList(bytes[i:i+locations_size])
                    i += locations_size
                                    
    #                 # isCommunication
    #                 self.isCommunication =  Sensation.intToBoolean(bytes[i])
    #                 i += Sensation.ENUM_SIZE
                                    
                    # mainNames
                    mainNames_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("mainNames_size " + str(mainNames_size))
                    i += Sensation.ID_SIZE
                    self.mainNames=Sensation.bytesToList(bytes[i:i+mainNames_size])
                    i += mainNames_size
                                    
                    if self.sensationType is Sensation.SensationType.Drive:
                        self.leftPower = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        self.rightPower = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                    elif self.sensationType is Sensation.SensationType.HearDirection:
                        self.hearDirection = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                    elif self.sensationType is Sensation.SensationType.Azimuth:
                        self.azimuth = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                    elif self.sensationType is Sensation.SensationType.Acceleration:
                        self.x = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        self.y = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        self.z = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                    elif self.sensationType is Sensation.SensationType.Location:
#                         self.x = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                         i += Sensation.FLOAT_PACK_SIZE
#                         self.y = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                         i += Sensation.FLOAT_PACK_SIZE
#                         self.z = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                         i += Sensation.FLOAT_PACK_SIZE
#                         self.radius = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
#                         i += Sensation.FLOAT_PACK_SIZE
                        
                        name_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        i += Sensation.ID_SIZE
                        self.name =Sensation.bytesToStr(bytes[i:i+name_size])
                        i += name_size
                    elif self.sensationType is Sensation.SensationType.Observation:
                        self.observationDirection = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        self.observationDistance = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                    elif self.sensationType is Sensation.SensationType.Voice:
                        filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        #print("filePath_size " + str(filePath_size))
                        i += Sensation.ID_SIZE
                        self.filePath =Sensation.bytesToStr(bytes[i:i+filePath_size])
                        i += filePath_size
                        data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        #print("data_size " + str(data_size))
                        i += Sensation.ID_SIZE
                        self.data = bytes[i:i+data_size]
                        i += data_size
                        self.kind = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                        i += Sensation.ENUM_SIZE
                        #check if this is copy from original
                        if not self.isOriginal():
                            #try to find original and set reference to it's data
                            originalSensation = memory.getSensationFromSensationMemory(id=self.getDataId())
                            if originalSensation != None:
                                self.data = originalSensation.getData()               
                    elif self.sensationType is Sensation.SensationType.Image:
                        filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        i += Sensation.ID_SIZE
                        self.filePath =Sensation.bytesToStr(bytes[i:i+filePath_size])
                        i += filePath_size
                        data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        i += Sensation.ID_SIZE
                        if data_size > 0:
                            self.image = PIL_Image.open(io.BytesIO(bytes[i:i+data_size]))
                        else:
                            self.image = None
                        i += data_size
                        #check if this is copy from original
                        if not self.isOriginal():
                            #try to find original and set reference to it's data
                            originalSensation = memory.getSensationFromSensationMemory(id=self.getDataId())
                            if originalSensation != None:
                                self.image = originalSensation.getImage()               
                    elif self.sensationType is Sensation.SensationType.Calibrate:
                        self.calibrateSensationType = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                        i += Sensation.ENUM_SIZE
                        if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                            self.hearDirection = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                            i += Sensation.FLOAT_PACK_SIZE
                    elif self.sensationType is Sensation.SensationType.Capability:
                        capabilities_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        #print("capabilities_size " + str(capabilities_size))
                        i += Sensation.ID_SIZE
                        self.capabilities = Capabilities(bytes=bytes[i:i+capabilities_size])
                        i += capabilities_size
                    elif self.sensationType is Sensation.SensationType.Item:
                        name_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        i += Sensation.ID_SIZE
                        self.name =Sensation.bytesToStr(bytes[i:i+name_size])
                        i += name_size
                                            
                        self.score = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        
                        self.presence = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                        i += Sensation.ENUM_SIZE
                        
                        # image part just as image # TODO filepath
                        filePath_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        i += Sensation.ID_SIZE
                        self.filePath =Sensation.bytesToStr(bytes[i:i+filePath_size])
                        i += filePath_size
                        data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        i += Sensation.ID_SIZE
                        if data_size > 0:
                            self.image = PIL_Image.open(io.BytesIO(bytes[i:i+data_size]))
                        else:
                            self.image = None
                        i += data_size
                        # voice just like as voice but no kind
                        data_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                        #print("data_size " + str(data_size))
                        i += Sensation.ID_SIZE
                        self.data = bytes[i:i+data_size]
                        i += data_size
                        
                        #check if this is copy from original
                        if not self.isOriginal():
                            #try to find original and set reference to it's data
                            originalSensation = memory.getSensationFromSensationMemory(id=self.getDataId())
                            if originalSensation != None:
                                self.name = originalSensation.getName()               
                                self.image = originalSensation.getImage()               
                                self.idata = originalSensation.getData()               
                    elif self.sensationType is Sensation.SensationType.Robot:
                        self.presence = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                        i += Sensation.ENUM_SIZE
                    elif self.sensationType is Sensation.SensationType.Feeling:
                        firstAssociateSensation_id=Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        self.firstAssociateSensation = memory.getSensationFromSensationMemory(id=firstAssociateSensation_id)
                        
                        otherAssociateSensation_id=Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                        self.otherAssociateSensation = memory.getSensationFromSensationMemory(id=otherAssociateSensation_id)
                        
                        self.positiveFeeling =  Sensation.intToBoolean(bytes[i])
                        i += Sensation.ENUM_SIZE
                        
                        self.negativeFeeling = Sensation.intToBoolean(bytes[i])
                        i += Sensation.ENUM_SIZE
                    elif self.sensationType is Sensation.SensationType.RobotState:
                        self.robotState = Sensation.bytesToStr(bytes[i:i+Sensation.ENUM_SIZE])
                        i += Sensation.ENUM_SIZE
                        
                    associationIdsLen = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("associationIdsLen " + str(associationIdsLen))
                    i += Sensation.ID_SIZE
                    for j in range(associationIdsLen):
                        sensation_id = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
                        i += Sensation.FLOAT_PACK_SIZE
                   
                        time = Sensation.bytesToFloat(bytes[i:i+Sensation.FLOAT_PACK_SIZE])
    #                    if time > yougestTime:
    #                        yougestTime=time
                        i += Sensation.FLOAT_PACK_SIZE
                    
                        feeling = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER, signed=True)
                        i += Sensation.ID_SIZE
    
                        # should not associate yet, but let Memory choose if we use this instance of
                        # sensation with its associations or keep old instance, if we already have a copy
                        # of sensation with this id in our memory
                        self.potentialAssociations.append(Sensation.AssociationSensationIds(sensation_id=sensation_id,
                                                                                            time=time,
                                                                                            feeling=feeling))
                        
                    # finally set data to copySensation that are in Memory now
                    j=0
                    while j < len(self.copySensationIds):
                        copySensation = memory.getSensationFromSensationMemory(id=self.copySensationIds[j])
                        if copySensation != None:
                            if copySensation.getSensationType() == Sensation.SensationType.Voice:
                                copySensation.data = self.data
                            elif copySensation.getSensationType() == Sensation.SensationType.Image:
                                copySensation.image = self.image
                            elif copySensation.getSensationType() == Sensation.SensationType.Item:
                                 copySensation.name = self.name
                                 copySensation.image = self.image
                            copySensation.originalSensation = self
                            copySensation.originalSensationId = self.id                               
                            self.copySensations.append(copySensation)
                                                
                            del self.copySensationIds[j] # self.copySensationIds contains only original ids, that are not found yet
                        else:
                            j=j+1

                    # if this is copy and original does not know it yet, set                            
                    if self.originalSensationId != self.id:
                        self.originalSensation = memory.getSensationFromSensationMemory(id=self.originalSensationId)
                        if self.originalSensation != None:
                            if self not in self.originalSensation.copySensations:
                                self.originalSensation.copySensations.append(self)
                                j = 0
                                while j < len(self.originalSensation.copySensationIds):
                                    if self.id == self.originalSensation.copySensationIds[j]:
                                        del self.originalSensation.copySensationIds[j]
                                        break
                                    j = j+1
 
                    #  at the end receivedFrom (list of words)
                    receivedFrom_size = int.from_bytes(bytes[i:i+Sensation.ID_SIZE-1], Sensation.BYTEORDER) 
                    #print("receivedFrom_size " + str(receivedFrom_size))
                    i += Sensation.ID_SIZE
                    self.receivedFrom=Sensation.bytesToList(bytes[i:i+receivedFrom_size])
                    i += receivedFrom_size
                    
                    # TODO Decide here is we should return this sensation or a copy of old one
                    # but should we check it here or elsewhere
                else:
                    # other version of Sensation
                    # We can only mark this to fail
                    self.sensationType = Sensation.SensationType.Unknown

            except (ValueError):
                self.sensationType = Sensation.SensationType.Unknown
                    
            
    '''
    set base fields
    '''
    def setBaseFields(destination,
                      sensationType,
                      memoryType,
                      robotType,
                      robot,
                      locations,
                      mainNames,
                      leftPower, rightPower,                            # Robot motors state
                      azimuth,                                          # Robot direction relative to magnetic north pole
                      x, y, z, radius,                                  # location and acceleration of Robot
                      hearDirection,                                    # sound direction, relative to Robot
                      observationDirection,observationDistance,         # observation of itrm, relative to Robot
                      filePath,
                      data,                                             # ALSA voice is string (uncompressed voice information)
                      image,                                            # Image internal representation is PIl.Image 
                      calibrateSensationType,
                      capabilities,                                     # capabilities of sensorys, robotType what way sensation go
                      name,                                             # name of Item
                      score,                                            # used at least with item to define how good was the detection 0.0 - 1.0
                      presence,                                         # presence of Item
                      kind,                                             # kind (for instance voice)
                      firstAssociateSensation,                          # associated sensation first side
                      otherAssociateSensation,                          # associated Sensation other side
                      feeling,                                          # feeling of sensation or association
                      positiveFeeling,                                  # change association feeling to more positive robotType if possible
                      negativeFeeling,                                  # change association feeling to more negative robotType if possible
                      robotState):
        if sensationType is not None:
            destination.sensationType = sensationType
        else:
            destination.sensationType = Sensation.SensationType.Unknown
            
        if memoryType is not None:
            destination.memoryType = memoryType
        else:
            destination.memoryType = Sensation.MemoryType.Sensory

        if robotType is not None:
            destination.robotType = robotType
        else:
            destination.robotType =  Sensation.RobotType.Sense

        if robot is not None:
            destination.robot = robot
        else:
            destination.robot = None
            
        if locations is not None:
            destination.locations = locations
        else:
            destination.locations = []
            
#         if isCommunication is not None:
#             destination.isCommunication = isCommunication
#         else:
#             destination.isCommunication = False

        if mainNames is not None:
            destination.mainNames = mainNames
        elif robot != None:
            destination.mainNames = robot.getMainNames()
        else:
            destination.mainNames = []

        if leftPower is not None:
            destination.leftPower = leftPower
        else:
            destination.leftPower = 0.0

        if rightPower is not None:
            destination.rightPower = rightPower
        else:
            destination.rightPower = 0.0

        if hearDirection is not None:
            destination.hearDirection = hearDirection
        else:
            destination.hearDirection = 0.0

        if azimuth is not None:
            destination.azimuth = azimuth
        else:
            destination.azimuth =  0.0
        
        if x is not None:
            destination.x = x
        else:
            destination.x = 0.0
        
        if y is not None:
            destination.y = y
        else:
            destination.y = 0.0
                
        if z is not None:
            destination.z = z
        else:
            destination.z = 0.0
        
        if radius is not None:
            destination.radius = radius
        else:
            destination.radius = 0.0

        if observationDirection is not None:
            destination.observationDirection = observationDirection
        else:
            destination.observationDirection = 0.0

        if observationDistance is not None:
            destination.observationDistance = observationDistance
        else:
            destination.observationDistance = 0.0

        if filePath is not None:
            destination.filePath = filePath
        else:
            destination.filePath = ''
            
        if data is not None:
            destination.data = data
        else:
            destination.data = b''
            
        if image is not None:
            destination.image = image
        else:
            destination.image = None
            
        if calibrateSensationType is not None:
            destination.calibrateSensationType = calibrateSensationType
        else:
            destination.calibrateSensationType = Sensation.SensationType.Unknown
            
        if capabilities is not None:
            destination.capabilities = capabilities
        else:
            destination.capabilities = None
            
        if name is not None:
            destination.name = name
        else:
            destination.name = ''
            
        if score is not None:
            destination.score = score
        else:
            destination.score = 0.0
            
        if presence is not None:
            destination.presence = presence
        else:
            destination.presence = Sensation.Presence.Unknown
            
        if kind is not None:
            destination.kind = kind
        else:
            destination.kind = Sensation.Kind.Normal
            
        if firstAssociateSensation is not None:
            destination.firstAssociateSensation = firstAssociateSensation
        else:
            destination.firstAssociateSensation = None
            
        if otherAssociateSensation is not None:
            destination.otherAssociateSensation = otherAssociateSensation
        else:
            destination.otherAssociateSensation = None
            
        if positiveFeeling is not None:
            destination.positiveFeeling = positiveFeeling
        else:
            destination.positiveFeeling = False
            
        if feeling is not None:
            destination.feeling = feeling
        else:
            destination.feeling = Sensation.Feeling.Neutral

        if negativeFeeling is not None:
            destination.negativeFeeling = negativeFeeling
        else:
            destination.negativeFeeling = False
            
        if robotState is not None:
            destination.robotState = robotState
        else:
            destination.robotState = None


    '''
    update base fields
    '''
    def updateBaseFields(source, destination,
                        #originalSensationId,
                        sensationType,
                        memoryType,
                        robotType,
                        robot,
                        locations,
#                        isCommunication,
                        mainNames,
                        leftPower, rightPower,                               # Walle motors state
                        azimuth,                                             # Walle robotType relative to magnetic north pole
                        x, y, z, radius,                                     # location and acceleration of Robot
                        hearDirection,                                       # sound robotType heard by Walle, relative to Walle
                        observationDirection,observationDistance,            # Walle's observation of something, relative to Walle
                        filePath,
                        data,                                                # ALSA voice is string (uncompressed voice information)
                        image,                                               # Image internal representation is PIl.Image 
                        calibrateSensationType,
                        capabilities,                                        # capabilitis of sensorys, robotType what way sensation go
                        name,                                                # name of Item
                        score,                                               # used at least with item to define how good was the detection 0.0 - 1.0
                        presence,                                            # presence of Item
                        kind,                                                # kind (for instance voice)
                        firstAssociateSensation,                             # associated sensation first side
                        otherAssociateSensation,                             # associated Sensation other side
                        feeling,                                             # feeling of sensation or association
                        positiveFeeling,                                     # change association feeling to more positive robotType if possible
                        negativeFeeling,                                      # change association feeling to more negative robotType if possible
                        robotState):                                   
#         if originalSensationId is None:
#             destination.originalSensationId = source.originalSensationId
#         else:
#             destination.originalSensationId = originalSensationId
        destination.originalSensationId = source.originalSensationId # or source.id
        destination.originalSensation = source
        if destination not in source.copySensations:
            source.copySensations.append(destination)
        
        if sensationType is None:
            destination.sensationType = source.sensationType
        else:
            destination.sensationType = sensationType
            
        if memoryType is None:
            destination.memoryType = source.memoryType
        else:
            destination.memoryType = memoryType

        if robotType is None:
            destination.robotType = source.robotType
        else:
            destination.robotType =  robotType

        if robot is None:
            destination.robot = source.robot
        else:
            destination.robot = robot
            
        if locations is None:
            destination.locations = source.locations
        else:
            destination.locations = locations
            
#         if isCommunication is None:
#             destination.isCommunication = source.isCommunication
#         else:
#             destination.isCommunication = isCommunication
            
        if mainNames is None:
            destination.mainNames = source.mainNames
        else:
            destination.mainNames = mainNames
            
        if leftPower is None:
            destination.leftPower = source.leftPower
        else:
            destination.leftPower = leftPower

        if rightPower is None:
            destination.rightPower = source.rightPower
        else:
            destination.rightPower = rightPower

        if hearDirection is None:
            destination.hearDirection = source.hearDirection
        else:
            destination.hearDirection = hearDirection

        if azimuth is None:
            destination.azimuth = source.azimuth
        else:
            destination.azimuth =  azimuth
        
        if x is None:
            destination.x = source.x
        else:
            destination.x = x
        
        if y is None:
            destination.y = source.y
        else:
            destination.y = y
                
        if z is None:
            destination.z = source.z
        else:
            destination.z = z
        
        if radius is None:
            destination.radius = source.radius
        else:
            destination.radius = radius

        if observationDirection is None:
            destination.observationDirection = source.observationDirection
        else:
            destination.observationDirection = observationDirection

        if observationDistance is None:
            destination.observationDistance = source.observationDistance
        else:
            destination.observationDistance = observationDistance

        # TODO should we copy filepath?
        if filePath is None:
            destination.filePath = source.filePath
        else:
            destination.filePath = filePath
            
        if data is None:
            destination.data = source.data
        else:
            destination.data = data
            
        if image is None:
            destination.image = source.image
        else:
            destination.image = image
            
        if calibrateSensationType is None:
            destination.calibrateSensationType = source.calibrateSensationType
        else:
            destination.calibrateSensationType = calibrateSensationType
            
        if capabilities is None:
            destination.capabilities = source.capabilities
        else:
            destination.capabilities = capabilities
            
        if name is None:
            destination.name = source.name
        else:
            destination.name = name
            
        if score is None:
            destination.score = source.score
        else:
            destination.score = score
            
        if presence is None:
            destination.presence = source.presence
        else:
            destination.presence = presence
            
        if kind is None:
            destination.kind = source.kind
        else:
            destination.kind = kind
            
        if firstAssociateSensation is None:
            destination.firstAssociateSensation = source.firstAssociateSensation
        else:
            destination.firstAssociateSensation = firstAssociateSensation
            
        if otherAssociateSensation is None:
            destination.otherAssociateSensation = source.otherAssociateSensation
        else:
            destination.otherAssociateSensation = otherAssociateSensation
            
        if positiveFeeling is None:
            destination.positiveFeeling = source.positiveFeeling
        else:
            destination.positiveFeeling = positiveFeeling
            
        if feeling is None:
            destination.feeling = source.feeling
        else:
            destination.feeling = feeling

        if negativeFeeling is None:
            destination.negativeFeeling = source.negativeFeeling
        else:
            destination.negativeFeeling = negativeFeeling

        if robotState is None:
            destination.robotState = source.robotState
        else:
            destination.robotState = robotState

    
    def __cmp__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
            print('__cmp__ self.id == other.id ' +  str(self.id) + ' == ' + str(other.id) + ' ' + str(self.id == other.id))
            return self.id == other.id
        else:
            print('__cmp__ other is not Sensation')
            return False
 
    def getNextId():
        return Sensation.getRandom(base=systemTime.time(), randomMin=Sensation.LOWPOINT_NUMBERVARIANCE, randomMax=Sensation.HIGHPOINT_NUMBERVARIANCE)

    def getRandom(base, randomMin, randomMax):
        return base + random.uniform(randomMin, randomMax)
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
#            return self.__dict__ == other.__dict__
#            print('__eq__ self.id == other.id ' +  str(self.id) + ' == ' + str(other.id) + ' ' + str(self.id == other.id))
            return self.id == other.id
        else:
#            print('__eq__ other is not Sensation')
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

                 
    def __str__(self):
        s=str(self.robotId) + ' ' + str(self.id) + ' ' + str(self.time) + ' ' + self.memoryType + ' ' + self.robotType + ' ' + self.sensationType+ ' ' + self.getLocationsStr()
        if self.sensationType == Sensation.SensationType.Drive:
            s +=  ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensationType == Sensation.SensationType.HearDirection:
            s +=  ' ' + str(self.hearDirection)
        elif self.sensationType == Sensation.SensationType.Azimuth:
            s += ' ' + str(self.azimuth)
        elif self.sensationType == Sensation.SensationType.Acceleration:
            s +=  ' ' + str(self.x)+ ' ' + str(self.y) + ' ' + str(self.z)
        elif self.sensationType == Sensation.SensationType.Location:
#            s +=  ' ' + str(self.x)+ ' ' + str(self.y) + ' ' + str(self.z) + ' ' + str(self.radius)
            s +=  ' ' + self.name
        elif self.sensationType == Sensation.SensationType.Observation:
            s += ' ' + str(self.observationDirection)+ ' ' + str(self.observationDistance)
        elif self.sensationType == Sensation.SensationType.Voice:
            #don't write binary data to sring any more
            s += ' ' + self.filePath + ' ' + self.kind
        elif self.sensationType == Sensation.SensationType.Image:
            s += ' ' + self.filePath
        elif self.sensationType == Sensation.SensationType.Calibrate:
            if self.calibrateSensationType == Sensation.SensationType.HearDirection:
                s += ' ' + self.calibrateSensationType + ' ' + str(self.hearDirection)
            else:
                s = str(self.robotId) + ' ' + str(self.id) + ' ' + self.memoryType + ' ' + self.robotType + ' ' +  Sensation.SensationType.Unknown
        elif self.sensationType == Sensation.SensationType.Capability:
            s +=  ' ' + self.getCapabilities().toString()
        elif self.sensationType == Sensation.SensationType.Item:
            s +=  ' ' + self.name
            s +=  ' ' + str(self.score)
            s +=  ' ' + self.presence
        elif self.sensationType == Sensation.SensationType.RobotState:
            s +=  ' ' + self.robotState
           
#         elif self.sensationType == Sensation.SensationType.Stop:
#             pass
#         elif self.sensationType == Sensation.SensationType.Robot:
#             pass
#         else:
#             pass

#        # at the end associations (ids)
        s += ' '
        i=0
        for association in self.associations:
            if i == 0:
                 s += str(association.getSensation().getId())
            else:
                s += LIST_SEPARATOR + str(association.getSensation().getId())
            i = i+1
#        # at the end receivedFrom
        s += ' '
        i=0
        for host in self.receivedFrom:
            if i == 0:
                 s += host
            else:
                s += LIST_SEPARATOR + host
            i = i+1
            
        return s

    '''
    Printable string
    '''
    def toDebugStr(self):
        # we can't make yet printable bytes, but as a debug purposes, it is rare neended
#         if self.sensationType == Sensation.SensationType.Voice or self.sensationType == Sensation.SensationType.Image :
#             s=str(self.robotId) + ' ' + str(self.id) + ' ' + str(self.time) + ' ' + str(self.association_time) + ' ' + Sensation.getMemoryTypeString(self.memoryType) + ' ' + Sensation.getRobotTypeString(self.robotType) + ' ' + Sensation.getSensationTypeString(self.sensationType)
#         else:
#             s=self.__str__()
        s = systemTime.ctime(self.time) + ':' + str(self.robotId) + ':' + str(self.id) + ':' + Sensation.getMemoryTypeString(self.memoryType) + ':' +\
            Sensation.getRobotTypeString(self.robotType) + ':' + Sensation.getSensationTypeString(self.sensationType)+ ':' + self.getLocationsStr() + ':'
        ## OOPS Can be NoneType
        string = Sensation.getFeelingString(self.getFeeling())
        if string :
            s = s + ':' + string 
        else:
            s = s + ':None'                 
        if self.sensationType == Sensation.SensationType.Voice:
            s = s + ':' + Sensation.getKindString(self.kind)
#         elif self.sensationType == Sensation.SensationType.Image:
#             s = s + ':' + self.getLocations()
        elif self.sensationType == Sensation.SensationType.Item:
            s = s + ':' + self.name + ':' + str(self.score) + ':' + Sensation.getPresenceString(self.presence)
        elif self.sensationType == Sensation.SensationType.Feeling:
            if self.getPositiveFeeling():
                s = s + ':positiveFeeling'
            if self.getNegativeFeeling():
                s = s + ':negativeFeeling'
        elif self.sensationType == Sensation.SensationType.RobotState:
            s = s + ':' + Sensation.getRobotStateString(self.robotState)
            
        return s

    def bytes(self):
#        b = self.id.to_bytes(Sensation.ID_SIZE, byteorder=Sensation.BYTEORDER)
        #Version of bytes
        b =  Sensation.VERSION.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)

        b += Sensation.floatToBytes(self.robotId)
        b += Sensation.floatToBytes(self.id)
        
        b += Sensation.floatToBytes(self.originalSensationId)
        
        copySensationsLen=len(self.copySensations)
        b +=  copySensationsLen.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        for j in range(copySensationsLen):
            b +=  Sensation.floatToBytes(self.copySensations[j].getId())
        
        b += Sensation.floatToBytes(self.time)
        b += Sensation.strToBytes(self.memoryType)
        b += Sensation.strToBytes(self.sensationType)
        b += Sensation.strToBytes(self.robotType)
        b += self.feeling.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER, signed=True)
        
        blist = Sensation.listToBytes(self.locations)
        #print(' blist ' +str(blist))
        blist_size=len(blist)
        b +=  blist_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        b += blist
        
        blist = Sensation.listToBytes(self.mainNames)
        #print(' blist ' +str(blist))
        blist_size=len(blist)
        b +=  blist_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        b += blist
        
        if self.sensationType is Sensation.SensationType.Drive:
            b += Sensation.floatToBytes(self.leftPower) + Sensation.floatToBytes(self.rightPower)
        elif self.sensationType is Sensation.SensationType.HearDirection:
            b +=  Sensation.floatToBytes(self.hearDirection)
        elif self.sensationType is Sensation.SensationType.Azimuth:
            b +=  Sensation.floatToBytes(self.azimuth)
        elif self.sensationType is Sensation.SensationType.Acceleration:
            b +=  Sensation.floatToBytes(self.x) + Sensation.floatToBytes(self.y) + Sensation.floatToBytes(self.z)
        elif self.sensationType is Sensation.SensationType.Location:
#             b +=  Sensation.floatToBytes(self.x) + Sensation.floatToBytes(self.y) + Sensation.floatToBytes(self.z) + Sensation.floatToBytes(self.radius)
            name_size=len(self.name)
            b +=  name_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  Sensation.strToBytes(self.name)            
        elif self.sensationType is Sensation.SensationType.Observation:
            b +=  Sensation.floatToBytes(self.observationDirection) + Sensation.floatToBytes(self.observationDistance)
        elif self.sensationType is Sensation.SensationType.Voice:
            bfilePath =  Sensation.strToBytes(self.filePath)
            filePath_size=len(bfilePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b += bfilePath
            
            data_size=len(self.data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  self.data
            b +=  Sensation.strToBytes(self.kind)
        elif self.sensationType is Sensation.SensationType.Image:
            filePath_size=len(self.filePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  Sensation.strToBytes(self.filePath)
            stream = io.BytesIO()
            if self.image is None:
                data = b''
            else:
                self.image.save(fp=stream, format=Sensation.IMAGE_FORMAT)
                data=stream.getvalue()
            data_size=len(data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  data
        elif self.sensationType is Sensation.SensationType.Calibrate:
            if self.calibrateSensationType is Sensation.SensationType.HearDirection:
                b += Sensation.strToBytes(self.calibrateSensationType) + Sensation.floatToBytes(self.hearDirection)
#             else:
#                 return str(self.robotId) + ' ' + self.id) + ' ' + self.memoryType + ' ' + self.robotType + ' ' + Sensation.SensationType.Unknown
        elif self.sensationType is Sensation.SensationType.Capability:
            bytes = self.getCapabilities().toBytes()
            capabilities_size=len(bytes)
            print("capabilities_size " + str(capabilities_size))
            b += capabilities_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b += bytes
        elif self.sensationType is Sensation.SensationType.Item:
            name_size=len(self.name)
            b +=  name_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  Sensation.strToBytes(self.name)
            b +=  Sensation.floatToBytes(self.score)
            b +=  Sensation.strToBytes(self.presence)
            # just like Image
            filePath_size=len(self.filePath)
            b +=  filePath_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  Sensation.strToBytes(self.filePath)
            stream = io.BytesIO()
            if self.image is None:
                data = b''
            else:
                self.image.save(fp=stream, format=Sensation.IMAGE_FORMAT)
                data=stream.getvalue()
            data_size=len(data)
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  data
            #just like voice, but no kind
            if self.data is not None:
                data_size=len(self.data)
            else:
                data_size=0
            b +=  data_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
            b +=  self.data
        elif self.sensationType is Sensation.SensationType.Robot:
            b +=  Sensation.strToBytes(self.presence)
        elif self.sensationType is Sensation.SensationType.Feeling:
            if self.getFirstAssociateSensation():
                id = self.getFirstAssociateSensation().getId()
            else:
                id = 0.0
            b +=  Sensation.floatToBytes(id)
            if self.getOtherAssociateSensation():
                id = self.getFirstAssociateSensation().getId()
            else:
                id = 0.0
            b +=  Sensation.floatToBytes(id)
            b +=  Sensation.booleanToBytes(self.getPositiveFeeling())
            b +=  Sensation.booleanToBytes(self.getNegativeFeeling())
        elif self.sensationType == Sensation.SensationType.RobotState:
            b +=  Sensation.strToBytes(self.robotState)
           
        #  at the end associations (ids)
        associationIdsLen=len(self.associations)
        b +=  associationIdsLen.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        for j in range(associationIdsLen):
            b +=  Sensation.floatToBytes(self.associations[j].getSensation().getId())
            b +=  Sensation.floatToBytes(self.associations[j].getTime())
            b +=  (self.associations[j].getFeeling()).to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER, signed=True)
       #  at the end receivedFrom (list of words)
        blist = Sensation.listToBytes(self.receivedFrom)
        #print(' blist ' +str(blist))
        blist_size=len(blist)
        b +=  blist_size.to_bytes(Sensation.ID_SIZE, Sensation.BYTEORDER)
        b += blist
        

# all other done
#         elif self.sensationType == Sensation.SensationType.Stop:
#             return str(self.robotId) + ' ' +str(self.id) + ' ' + self.memoryType + ' ' + self.robotType + ' ' + self.sensationType
#         elif self.sensationType == Sensation.SensationType.Robot:
#             return str(self.robotId) + ' ' +str(self.id) + ' ' + self.memoryType + ' ' + self.robotType + ' ' + self.sensationType
#         else:
#             return str(self.robotId) + ' ' +str(self.id) + ' ' + self.memoryType + ' ' + self.robotType + ' ' + self.sensationType
        
        return b


    def getTime(self):
        return self.time

    def setTime(self, time = None):
        if time == None:
            time = systemTime.time()
        self.time = time

    '''
    Get latest time, when this Sensation was used
    '''
    def getLatestTime(self):
        latest_time=self.time
        for association in self.associations:
            # TODO we could also recursive check all associations when one was latest used, but ...
            if association.getTime() > latest_time:
                latest_time=association.getTime()
        return latest_time
    
    '''
    How much livetime as a ratio there is left (1.0 -> 0.0) for this sensation
    '''
    def getLiveTimeLeftRatio(time, memoryType):
# Old with self, parameter
#         if time == None:
#             time = self.getTime()
#         if memoryType == None:
#             memoryType = self.getMemoryType()
#         liveTimeLeftRatio = \
#                 (Sensation.sensationMemoryLiveTimes[memoryType] - (systemTime.time()-time)) / \
#                 Sensation.sensationMemoryLiveTimes[memoryType]
#         if liveTimeLeftRatio < 0.0:
#             liveTimeLeftRatio = 0.0
#             
#         return liveTimeLeftRatio

        liveTimeLeftRatio = \
                (Sensation.sensationMemoryLiveTimes[memoryType] - (systemTime.time()-time)) / \
                Sensation.sensationMemoryLiveTimes[memoryType]
        if liveTimeLeftRatio < 0.0:
            liveTimeLeftRatio = 0.0
             
        return liveTimeLeftRatio

        
    
    '''
    Memorability of this Sensation
        
    Memorability goes down by time. We use logarithm and Memory type
    Sensory Sensations have very high Memorability when Sensation has low age
    but memorability goes down in very short time.
    Here we use log10(livetimeratio left)
        
    LongTerm Sensation have low memorability when the are created,
    but memorability goes down with a long time.
    Here we use ln(livetimeratio left)
    
     
    Sensation Memorability is time based function
    There are many ways to define this
    Sensation only would be time based + feeling based.
        
    Memory.forgetLessImportantSensations uses this so it would be best choice,
    feeling is based o associations, changing Sensations memorability if some association happens
        
    Associations have feelings and time. Sensations have time. we could define
    Sensation Memorability be time, Association Memorability by time+feeling and
    Sensation whole Memorability by Sensation Memorability + its Associations Memorability.
    Functions are
    1) Sensation only
    2) Sensation+its association sensation based on Feeling and time
     - used in Memory.forgetLessImportantSensations
    3) Sensations + list of potential Item-Sensations based on Feeling and Time
     - used in Communication
     
    parameters
    allAssociations     when True, we calculate Momoralibity by
                        Sensation itself and by its all Associations
    sensations          Array of SensationType.Item sensations
                        When given, calculates Momoralibity by
                        Sensation itself and by its Associations that are
                        assigned to an SensationType.Item Sensations, which
                        name-parameter is same than one of this arrays Sensation.
                        This is used by Memory method which is used by Robot.Communication
                        method that seaches best Sensations that have knows
                        Sensation.Item association.
                        Next parameters are not used
    positive            Do we search positive feeling Associations (Default)
    negative            Do we search negative feeling Associations
    absolute            Do we calculate result as abs in association, meaning that
                        result is not added by posive and negative values, but
                        by abs values, meaning that far os Feeling.Neutral is
                        bigger value even if it is posivive of negative Feeling
    
                        
    '''

    def getMemorability(self,
                        getAssociationsList = False,
                        allAssociations = False,
                        itemSensations = None,
                        robotMainNames = None,
                        robotTypes = None,#[Sensation.RobotType.Sense, Sensation.RobotType.Communication],
                        ignoredDataIds=[],
                        ignoredVoiceLens=[],
                        positive = True,
                        negative = False,
                        absolute = False):

        # Its not need to remember Feeling sensation, so we justgive then zero or minus        
        if self.getSensationType() == Sensation.SensationType.Feeling:
            return 0.0

        selfMemorability = Sensation.doGetMemorability(time = self.getTime(),
                                                       memoryType = self.getMemoryType())
        associationsMemorability = 0.0
        associations=[]
             
        if itemSensations != None or allAssociations:
            if getAssociationsList:
                associationsMemorability, associations = \
                    self.getAssociationsMemorability(
                                            getAssociationsList = getAssociationsList,
                                            allAssociations = allAssociations,
                                            itemSensations = itemSensations,
                                            robotMainNames = robotMainNames,
                                            robotTypes = robotTypes,
                                            ignoredDataIds=ignoredDataIds,
                                            positive = positive,
                                            negative = negative,
                                            absolute = absolute)
    #         if negative:
    #             return selfMemorability - associationsMemorability
                memorability = selfMemorability + associationsMemorability
                # Robot to Robot-commumunication is not so memorable than person to Robot
                if self.getRobotType() == Sensation.RobotType.Communication:
                    memorability = memorability/2.0
                return memorability, associations
            
            associationsMemorability = \
                self.getAssociationsMemorability(
                                            getAssociationsList = getAssociationsList,
                                            allAssociations = allAssociations,
                                            itemSensations = itemSensations,
                                            robotMainNames = robotMainNames,
                                            robotTypes = robotTypes,
                                            ignoredDataIds=ignoredDataIds,
                                            positive = positive,
                                            negative = negative,
                                            absolute = absolute)
    #         if negative:
    #             return selfMemorability - associationsMemorability
        memorability = selfMemorability + associationsMemorability
        # Robot to Robot-commumunication is not so memorable than person to Robot
        if self.getRobotType() == Sensation.RobotType.Communication:
            memorability = memorability/2.0
        return memorability
    
    '''
    Helper metyhod to calculate Memorability
    
    Memorability goes down by time. We use logarithm and Memory type
    Sensory Sensations have very high Memorability when Sensation has low age
    but memorability goes down in very short time.
    Here we use log10(livetimeratio left)
        
    LongTerm Sensation have low memorability when they are created,
    but memorability goes down with a long time.
    Here we use ln(livetimeratio left)
    
    Working Sensation should live longer than Sensory, but much shorter time than
    LongTerm, so it goes in the middle, using log10
    
    
    
    '''   
    def doGetMemorability(time,
                          memoryType,
                          feeling = None,
                          score=None,
                          positive = True,
                          negative = False,
                          absolute = False):
        if memoryType == Sensation.MemoryType.Sensory:
                memorability =  10.0 * (math.log10(10.0 + 10.0 * Sensation.getLiveTimeLeftRatio(time=time, memoryType=memoryType)) -1.0)
        elif memoryType == Sensation.MemoryType.Working:
                memorability =  math.e * (math.log(math.e + math.e * Sensation.getLiveTimeLeftRatio(time=time, memoryType=memoryType)) - 1.0)
        else: #Sensation.LongTerm
                memorability =  math.e * (math.log10(10.0 + 10.0 * Sensation.getLiveTimeLeftRatio(time=time, memoryType=memoryType)) -1.0)
        if memorability < 0.0:
             memorability = 0.0
             
        if feeling != None and score != None:
            memorability = memorability + memorability*float(feeling) * (score)
             
        return memorability
    
    '''
    get memorability of sensations assiciations
    We can iterate allAssociations
    This is used with forgetSensations where we want to forget most
    meaningless assosiations
    
    With Communication we wan't to find best Voice of Image Sensations that
    are connected to specifies set of SensationType.Item sensation that
    match in present Items.
    
    deprecated teporary until logic is checked
    '''

    def getAssociationsMemorability(self,
                                    getAssociationsList = False,
                                    allAssociations = False,
                                    itemSensations = None,
                                    robotMainNames = None,
                                    robotTypes = None,#[Sensation.RobotType.Sense, Sensation.RobotType.Communication],                                    
                                    ignoredDataIds=[],
                                    #ignoredVoiceLens=[],
                                    positive=True,
                                    negative=False,
                                    absolute=False):
        associations=[]
        names=[]
        if itemSensations != None:
            for sensation in itemSensations:
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    names.append(sensation.getName())
        # one level associations
        memorability = 0.0
        best_association = None
        for association in self.associations:
            if association.getSensation().getSensationType() == Sensation.SensationType.Item and\
               association.getSensation().getName() in names:
                # association.getImportance() uses score and Feling + time
                # so we get importance of this association
                memorability = memorability + \
                               Sensation.doGetMemorability(time = association.getTime(),
                                                           memoryType = association.getSensation().getMemoryType(),
                                                           feeling = association.getFeeling(),
                                                           score = association.getSensation().getScore())
                associations.append(association)
            elif allAssociations:
                memorability = memorability + \
                               Sensation.doGetMemorability(time = association.getTime(),
                                                           memoryType = association.getSensation().getMemoryType())
                associations.append(association)
               
#                 if absolute:
#                      importance = abs(importance)
#                 memorability = memorability + importance
        if getAssociationsList:
            return memorability, associations
        return memorability
                
    '''
    Calculate memorability where all MemoryType sensations should live
    half of its lifetime if Feeling is Good.
    This is guite high, so we will forgets less important Sensations soon
    but safe so, that Robot should not stop soon for out of memory
    '''            
    def getMaxMinCacheMemorability():
        maxCacheMemorability = 10000
        for memoryType in Sensation.NormalMemoryTypes:
            # set sensation more to the past and look again        
            history_time = systemTime.time() -Sensation.sensationMemoryLiveTimes[memoryType] * 0.5
            candidateMaxCacheMemorability = Sensation.doGetMemorability(time = history_time,
                                                                        memoryType = memoryType,
                                                                        feeling = Sensation.Feeling.Happy,
                                                                        score=0.5)

            if candidateMaxCacheMemorability < maxCacheMemorability:
                maxCacheMemorability = candidateMaxCacheMemorability
                
        return maxCacheMemorability


    def setId(self, id):
        self.id = id
    def getId(self):
        return self.id
    
    def setDataId(self, originalSensationId):
        self.originalSensationId = originalSensationId
    def getDataId(self):
        return self.originalSensationId
    
    def hasOriginality(self):
        return self.getSensationType() in Sensation.OriginalitySensationTypes
    def isOriginal(self):
        if self.hasOriginality():
            return self.originalSensationId == self.id
        return True

    def setRobotId(self, robotId):
        self.robotId = robotId
            
    '''
    for debugging reasons log what associations there is in our Long Term Memory
    '''  
    def logAssociations(sensation):
        if sensation.getSensationType() is Sensation.SensationType.Item:
            print('Associations: ' + sensation.getName())
            parents=[sensation]
            parents = Sensation.logSensationAssociations(level=1, parents=parents, associations=sensation.getAssociations())
            print('Associations: ' + sensation.getName() + ' >= ' + str(len(parents )-1) + ' associations')


    '''
    for debugging reasons log what associations there is in our Lng Term Memory
    '''  
    def logSensationAssociations(level, parents, associations):
#         tag=''
#         for i in range(0,level):
#             tag=tag+'-'
        tag=str(level)+': '
        for association in associations:
            sensation = association.getSensation()
            if sensation not in parents:
                if sensation.getSensationType() is Sensation.SensationType.Item:
                    print(tag + ' Item: ' + sensation.getName() + ' ' + str(len(parents )))
                else:
                    print(tag + Sensation.SensationTypes[sensation.getSensationType()] + ' ' + str(len(parents )))
                parents.append(sensation)
 
                if level < Sensation.ASSOCIATIONS_LOG_MAX_LEVEL and len(parents) < Sensation.ASSOCIATIONS_LOG_MAX_PARENTS:            
                    parents = Sensation.logSensationAssociations(level=level+1, parents=parents, associations=sensation.getAssociations())
        return parents

    
    '''
    Add single association
    Associations are always two sided, but not referencing to self
    So this method should always be called twice. Look associate -helper method!
    '''
    def addAssociation(self, association):
        # this side
        if association.getSensation() != self:
            oldAssociation = association.getSelfSensation().getAssociation(association.getSensation())
            if oldAssociation: #update old assiciation
                oldAssociation.setFeeling(association.getFeeling())
                oldAssociation.setTime(association.getTime())
            else:                             # create new association
                #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
                self.associations.append(association)
            
    '''
    Helper function to update or create an Association
    '''
    def associate(self,
                  sensation,                                    # sensation to connect
                  time=None,                                    # last used
                  feeling = Feeling.Neutral,                    # feeling of association two sensations
                  positiveFeeling = False,                      # change association feeling to more positive robotType if possible
                  negativeFeeling = False):                     # change association feeling to more negativee robotType if possible
#         self.addAssociation(Sensation.Association(self_sensation = self,
#                                                   sensation = sensation,
#                                                   time = time,
#                                                   feeling = feeling))
# 
#         sensation.addAssociation(Sensation.Association(self_sensation = sensation,
#                                                        sensation = self,
#                                                        time = time,
#                                                        feeling = feeling))
        if feeling == None:         # be sure that feeling is never None
            feeling = Sensation.Feeling.Neutral
        self.upsertAssociation(self_sensation = self,
                               sensation = sensation,
                               time=time,
                               feeling = feeling,
                               positiveFeeling = positiveFeeling,
                               negativeFeeling = negativeFeeling)

        sensation.upsertAssociation(self_sensation = sensation,
                                    sensation = self,
                                    time=time,
                                    feeling = feeling,
                                    positiveFeeling = positiveFeeling,
                                    negativeFeeling = negativeFeeling)

    '''
    Helper function to update or create one side of Association
    '''
    def upsertAssociation(self,
                          self_sensation,                               # sensation
                          sensation,                                    # sensation to connect
                          time=None,                                    # last used
                          feeling = Feeling.Neutral,                    # feeling of association two sensations
                          positiveFeeling = False,                      # change association feeling to more positive robotType if possible
                          negativeFeeling = False):                     # change association feeling to more negativee robotType if possible
        # this side
        if time == None:
            time = systemTime.time()
        if self_sensation != sensation:
            oldAssociation = self_sensation.getAssociation(sensation)
            if oldAssociation: #update old assiciation
                if positiveFeeling:
                    oldAssociation.changeFeeling(positive=True)
                elif negativeFeeling:
                    oldAssociation.changeFeeling(negative=True)
                else:
                    oldAssociation.setFeeling(feeling)
                
                oldAssociation.setTime(time)
            else:                             # create new association
                #print('addAssociation ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr())
                self_sensation.associations.append(Sensation.Association(self_sensation = self,
                                                  sensation = sensation,
                                                  time = time,
                                                  feeling = feeling))
     
    '''
    Is this Sensation in this Association already connected
    '''
    def isConnected(self, association):
        #print('isConnected ' + self.toDebugStr() + ' has ' + str(len(self.associations)) + ' associations')
        is_connected = False
        for asso in self.associations:
            if asso.getSensation() == association.getSensation():
                is_connected = True
                #print('isConnected ' + self.toDebugStr() + ' found association to ' + con.getSensation().toDebugStr() + ' == ' + association.getSensation().toDebugStr() + ' ' + str(is_connected))
                break
        #print('isConnected ' + self.toDebugStr() + ' to ' + association.getSensation().toDebugStr() + ' ' + str(is_connected))
        return is_connected
 
    '''
    get Association by Sensation
    '''
    def getAssociation(self, sensation):
        for association in self.associations:
            if sensation == association.getSensation():
                return association
        return None
       
    '''
    Add many associations
    '''
    def addAssociations(self, associations):
        for association in associations:
            self.associate( sensation = association.sensation,
                            time = association.time,
                            feeling = association.feeling)

    def getAssociations(self):
        return self.associations
    
    '''
    remove associations from this sensation connected to sensation given as parameter
    '''
    def removeAssociation(self, sensation):
        # old implementations
        #i=0
        for association in self.associations:
            if association.getSensation() == sensation:
#                print("self.associations.remove(association)")
                self.associations.remove(association)
#                 del self.associations[i]
#             else:
#                 i=i+1
        #other side
#        i=0
        for association in sensation.associations:
            if association.getSensation() == self:
#                print("sensation.associations.remove(association)")
                sensation.associations.remove(association)

        # with SensationTypr.Feeling, we have also AssociateSensations              
        if self.getSensationType() == Sensation.SensationType.Feeling:
            if sensation == self.firstAssociateSensation:
                self.firstAssociateSensation = None
            if sensation == self.therAssociateSensation:
                self.therAssociateSensation = None

#                 del sensation.associations[i]
#             else:
#                 i=i+1

# deprecated
#     def getAssociationIds(self):
#         associationIds=[]
#         for association in self.associations:
#             associationIds.append(association.getSensation().getId())
#         return associationIds

    '''
    get sensations feeling
    
    if we give other sensation as parameter, we get exact feeling between them
    if other sennsation is not given, we get  best or worst feeling of oll association this sensation has
    getFeeling -> getAssociationFeeling()
    '''    
    def getAssociationFeeling(self, sensation=None):
        feeling = Sensation.Feeling.Neutral
        if sensation:
            association = self.getAssociation(sensation=sensation)
            if association:
                feeling = association.getFeeling()
                association.time = systemTime.time()
                return feeling
        
        # one level associations
        best_association = None
        for association in self.associations:
            if abs(association.getFeeling()) > abs(feeling):
                feeling = association.getFeeling()
                best_association = association
        if best_association is not None:
            best_association.time = systemTime.time()
            
        return feeling
    
    # TODO Study logic  
    # deprecated  
#     def getImportance(self, positive=True, negative=False, absolute=False):
#         if positive:
#             importance = 10*Sensation.Feeling.Terrified
#         if negative:
#              importance = 10*Sensation.Feeling.InLove
#         if absolute:
#             importance = 0.0
#         # one level associations
#         best_association = None
#         for association in self.associations:
#             if positive:
#                 if association.getImportance() > importance:
#                     importance = association.getImportance()
#                     best_association = association
#             if negative:
#                 if association.getImportance() < importance:
#                     importance= association.getImportance()
#                     best_association = association
#             if absolute:
#                 if abs(association.getImportance()) > abs(importance):
#                     importance = association.getImportance()
#                     best_association = association
# #    don't change association time, because we don't know if this
# #    association or sensation is used
# #         if best_association is not None:
# #             best_association.time = systemTime.time()
#             
#         return self.getMemorability() * importance


    '''
    Has sensation association to other Sensation
    which SensationType is in 'associationSensationTypes'
    '''
    def hasAssociationSensationType(self, associationSensationType,
                                    associationDirections = [RobotType.Sense],
                                    ignoredDataIds=[],
                                    robotMainNames=None):
        has=False
        for association in self.associations:
            if association.getSensation().getSensationType() == associationSensationType and\
               association.getSensation().getRobotType() in associationDirections and\
               association.getSensation().getDataId() not in ignoredDataIds:
                has=True
                break       
        return has
     
    '''
    Get sensation association to other Sensation
    which SensationType is 'associationSensationType'
    '''
    def getAssociationsBySensationType(self, associationSensationType,
                                        associationDirections = [RobotType.Sense, RobotType.Communication],
                                        ignoredDataIds=[],
                                        ignoredVoiceLens=[],
                                        robotMainNames=None):
        associations=[]
        for association in self.associations:
            if association.getSensation().getSensationType() == associationSensationType and\
               association.getSensation().getRobotType() in associationDirections and\
               association.getSensation().getDataId() not in ignoredDataIds:
                associations.append(association)
        return associations
#     def setReceivedFrom(self, receivedFrom):
#         self.receivedFrom = receivedFrom
        
    '''
    Add single receivedFrom
    '''
    def addReceived(self, host):
        if len(host) > 0 and host not in self.receivedFrom:
            self.receivedFrom.append(host)
         
    '''
    Add many receiveds
    '''
    def addReceivedFrom(self, receivedFrom):
        for host in receivedFrom:
            self.addReceived(host)

    def getReceivedFrom(self):
        return self.receivedFrom
    
    '''
    returns True, if this Sensation is received from this host
    Method is used to avoid sendinmg Senation back fron some host, even if
    if has been originally setn from this host. This situation causes
    circulating Senastions for ever between hosts that have same capability to handle
    same Sensation type with same Memory level, so we must avoid it.
    
    Still it in allowed to process same sensation type sensations with different
    memory level in different hosts, so we must set self.receivedFrom, when we
    change Sensations memory level (or copy sensation to different memory level).
    '''
    def isReceivedFrom(self, host):
        return host in self.receivedFrom
           
    def setSensationType(self, sensationType):
        self.sensationType = sensationType
    def getSensationType(self):
        return self.sensationType

    def getMemoryType(self):
        return self.memoryType
       
    def setRobotType(self, robotType):
        self.robotType = robotType
    def getRobotType(self):
        return self.robotType
    
    '''
    If parameters robotMainNames is set, it is mainNames of robot
    asking sensations RobotType and robot want to know if this is
    Sense or Muscle sensation. If SensationType is Voice or Image, then
    it is used in Communication and with person Communication robot uses
    Muscles-type Robots and person can sense with is senses and answer with
    person muscles (speach).
    
    With Robot to Rpbot comunication sensation are transferred directly without
    Muscke-Sense transferring so with Robot Communication this Muscle-Sense tranferring
    is dropped out.
    
    We know that when Sensesation's MainNames and asker robor maionnanes don't match,
    then this is Robot-Robot communication and we reverser Muscle/Sensation RobotType
    we return.
    
    In all other cases (no naoinNames ios set in either Sensation or by ascing Robot
    or no Voice or Image, we return plain RobotType fron Sensation.
    Reverse robotType in foreign mainNames
    '''
#     def getRobotType(self, robotMainNames=None):
#         # compability to old implementation
# # deprecated
# #         if (self.getSensationType() != Sensation.SensationType.Voice and\
# #            self.getSensationType() != Sensation.SensationType.Image) or\
# #            robotMainNames == None or\
# #            len(robotMainNames) == 0 or\
# #            self.getMainNames() == None or\
# #            len(self.getMainNames()) == 0 or\
# #            self.isInMainNames(robotMainNames=robotMainNames):
# #             return self.robotType
#         
# #         if not self.isCommunication or\
# #            self.isInMainNames(robotMainNames=robotMainNames):
# #             return self.robotType
# # 
# #         #if robotMainNames is given as parameters and self.isInMainNames(robotMainNames=robotMainNames) reverse robotType in foreign mainNames
# #         if self.robotType == Sensation.RobotType.Muscle:
# #             return Sensation.RobotType.Sense
# #         return Sensation.RobotType.Muscle
#         return self.robotType
    
    '''
#     Is this Robot at least in one of mainNames
#     '''
#     def isInMainNames(self, robotMainNames):
#         if self.mainNames is None or len(self.mainNames) == 0 or\
#            robotMainNames is None or len(robotMainNames) == 0:
#             return True
#         for mainName in robotMainNames:
#             if mainName in self.mainNames:
#                  return True            
#         return False
    
    
    def setName(self, robot):
        self.robot = robot
    def getName(self):
        return self.robot

#     '''
#     locations are deprecated as a property and
#     now they support only one location
# they will be implemented assigning Other SentionTypes to
# SensationType.Location
# TODO Real implementation
#     '''        
    def setLocations(self, locations):
        self.locations = locations
    def getLocations(self):
        if self.locations is None:
            return []
        return self.locations

    def getLocationsStr(self):
        #from Config import strArrayToStr
        return Sensation.strArrayToStr(self.getLocations())
 
     
#     def setIsCommunication(self, isCommunication):
#         self.isCommunication = isCommunication
#     def getIsCommunication(self):
#         return self.isCommunication

    def setMainNames(self, mainNames):
        self.mainNames = mainNames
    def getMainNames(self):
        if self.mainNames is None:
            return []
        return self.mainNames

    def isInMainNames(self, mainNames):
        if mainNames is None:
            return True
        for mainName in mainNames:
            if mainName in self.getMainNames():
                return True            
        return False

    def getMainNamesString(self):
        #from Config import strArrayToStr
        return Sensation.strArrayToStr(self.getMainNames())
      

    def setLeftPower(self, leftPower):
        self.leftPower = leftPower
    def getLeftPower(self):
        return self.leftPower
        
    def setRightPower(self, rightPower):
        self.rightPower = rightPower
    def getRightPower(self):
        return self.rightPower
    
    def setHearDirection(self, hearDirection):
        self.hearDirection = hearDirection
    def getHearDirection(self):
        return self.hearDirection

    def setAzimuth(self, azimuth):
        self.azimuth = azimuth
    def getAzimuth(self):
        return self.azimuth

    def setX(self, x):
        self.x = x
    def getX(self):
        return self.x
    def setY(self, y):
        self.y = y
    def getY(self):
        return self.y
    def setZ(self, z):
        self.z = z
    def getZ(self):
        return self.z
    def setRadius(self, radius):
        self.radius = radius
    def getRadius(self):
        return self.radius

    def setObservationDirection(self, observationDirection):
        self.observationDirection = observationDirection
    def getObservationDirection(self):
        return self.observationDirection
    def setObservationDistance(self, observationDistance):
        self.observationDistance = observationDistance
    def getObservationDistance(self):
        return self.observationDistance

    def setData(self, data):
        self.data = data        
    def getData(self):
        return self.data
    
    def setImage(self, image):
        self.image = image        
    def getImage(self):
        return self.image
    
#     def setFilePath(self, filePath):
#         self.filePath = filePath       
    def getFilePath(self, sensationType=None):
        if sensationType == None:
            sensationType = self.getSensationType()
        
        format = None
        if sensationType == Sensation.SensationType.Image:
            format = Sensation.IMAGE_FORMAT
        elif sensationType == Sensation.SensationType.Voice:
            format = Sensation.VOICE_FORMAT
        elif sensationType == Sensation.SensationType.All:
            format = Sensation.BINARY_FORMAT
        else:
            format = None
            
        if format:
            return '{}/{}.{}'.format(Sensation.DATADIR, self.getId(), format)
            
        return None
   
    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
    def getCapabilities(self):
        return self.capabilities

    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name

    def setScore(self, score):
        self.score = score
    '''
    get highest score of associared  sensations
    '''    
    def getScore(self):
        score = Sensation.MIN_SCORE
        if self.score > score:
            score = self.score
        for association in self.getAssociations():
            # study only direct associations scores
            if association.getSensation().score > score:
                score = association.getSensation().score

        return score

    def setPresence(self, presence):
        self.presence = presence
    def getPresence(self):
        return self.presence

    def setKind(self, kind):
        self.kind = kind
    def getKind(self):
        return self.kind
    
    def setFirstAssociateSensation(self, firstAssociateSensation):
        self.firstAssociateSensation = firstAssociateSensation
    def getFirstAssociateSensation(self):
        return self.firstAssociateSensation
    
    def setOtherAssociateSensation(self, otherAssociateSensation):
        self.otherAssociateSensation = otherAssociateSensation
    def getOtherAssociateSensation(self):
        return self.otherAssociateSensation
    
    '''
    setAssociateFeeling -> setFeeling
    getAssociateFeeling -> getFeeling
    '''

    def setFeeling(self, feeling):
        self.feeling = feeling
    def getFeeling(self):
        return self.feeling
    
    def setPositiveFeeling(self, positiveFeeling):
        self.positiveFeeling = positiveFeeling
    def getPositiveFeeling(self):
        return self.positiveFeeling
    
    def setNegativeFeeling(self, negativeFeeling):
        self.negativeFeeling = negativeFeeling
    def getNegativeFeeling(self):
        return self.negativeFeeling
    
    def getRobotState(self):
        return self.robotState
    
    def setRobotState(self, robotState):
        self.robotState = robotState

       

    '''
        Attach a Sensation to be used by a Robot so, that
        it is not removed from Sensation cache until detached
        
        Parameters
        robot    robot that attach this Sensation
    '''    
    def attach(self, robot):
        if robot not in self.attachedBy:
            self.attachedBy.append(robot)
    '''
        Detach a Sensation 
        
        Parameters
        robot    robot that detach this Sensation
    '''
    def detach(self, robot):
        if robot in self.attachedBy:
            self.attachedBy.remove(robot)

    '''
        Detach a Sensation fron all its attached Robots
    '''
    def detachAll(self):
        del self.attachedBy[:]

    '''
    get attached Robots
    '''            
    def getAttachedBy(self):
        return self.attachedBy
            
    '''
        is Sensation forgettable
    '''
            
    def isForgettable(self):
#        return len(self.attachedBy) == 0
        if len(self.attachedBy) != 0:
#            print('is not forgettale by Robots ' + self.getAttachedByRobotStr())
            return False
            
        return True

    '''
    deprecated, move to test
    '''    
    def getAttachedByRobotStr(self):
        s=''
        for robot in self.attachedBy:
            s=s+robot.getName()+':'
        return s

    '''
    deprecated, move to test
    '''    
    def logAttachedBy(self):
        if len(self.attachedBy) > 0:
            s=''
            for robot in self.attachedBy:
                s=s+robot.getName()+':'
            print('attached by:' + self.getAttachedByRobotStr())
    

    '''
    helper method to get binary file name
    '''
#     def getFilePathByFormat(self, format):
#         return '{}/{}.{}'.format(Sensation.DATADIR, self.getId(), format)
    
    '''
    save sensation data permanently
    TODO do we need filepath at all, because we can calculate it from self.getId()
    '''  
    def save(self):
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)
            
        if (self.getSensationType() == Sensation.SensationType.Image or\
            self.getSensationType() == Sensation.SensationType.Item) and\
           self.getImage() != None:       
            fileName = self.getFilePath(sensationType=Sensation.SensationType.Image)
#             self.setFilePath(fileName)
#             fileName = '{}.{}'.format(fileName,Sensation.IMAGE_FORMAT) # with image format
#             self.setFilePath(fileName)
            try:
                if not os.path.exists(fileName):
                    try:
                        with open(fileName, "wb") as f:
                            try:
                                self.getImage().save(f)
                            except IOError as e:
                                print("self.getImage().save(f)) error {}".format(str(e)))
                            finally:
                                f.close()
                    except Exception as e:
                        print("Sensation.save Image open({}), wb) as f error {}".format(fileName, str(e)))
            except Exception as e:
                print('os.path.exists({}) error {}'.format(fileName, str(e)))
        if (self.getSensationType() == Sensation.SensationType.Voice or\
              self.getSensationType() == Sensation.SensationType.Item) and\
             self.getData() != None:             
            fileName = self.getFilePath(sensationType=Sensation.SensationType.Voice)
#             fileName = '{}/{}'.format(Sensation.DATADIR, self.getId()) # without voice format
#             self.setFilePath(fileName)
#             fileName = '{}.{}'.format(fileName,Sensation.DATADIR,self.getId(),Sensation.VOICE_FORMAT)
            try:
                if not os.path.exists(fileName):
                    try:
                        with open(fileName, 'wb') as f:
                            try:
                                f.write(self.getData())
                            except IOError as e:
                                print("f.write(self.getData()) error {}".format(str(e)))
                            finally:
                                f.close()
                    except Exception as e:
                        print("Sensation.save Voice1 open({}), wb) as f error {}".format(fileName, str(e)))
            except Exception as e:
                print("Sensation.save Voice2 not os.path.exists({}) error {}".format(fileName, str(e)))
                
        binaryFilePath = self.getFilePath(sensationType = Sensation.SensationType.All)
        # update file if exists
        #try:
            #if not os.path.exists(binaryFilePath):
        try:
            with open(binaryFilePath, "wb") as f:
                try:
                    f.write(self.bytes())
                except IOError as e:
                    print("Sensation.save f.write(self.bytes()) error {}".format(str(e)))
                finally:
                    f.close()
        except Exception as e:
             print("Sensation.save open({}), wb) as f error {}".format(binaryFilePath, str(e)))
        #except Exception as e:
        #    print('os.path.exists({}) error {}'.format(binaryFilePath, str(e)))
     
    '''
    delete sensation data permanently
    but sensation will be remained to be deteted dy del
    You should call first 'sensation.delete()' and right a way 'del sensation'
    '''  
    def delete(self):
        # Note self.associations changes while 
        # self.associations[0].getSensation().removeAssociation(self)
        # so we can not use 'for association in self.associations' syntax
        while len(self.associations) > 0: 
            self.associations[0].getSensation().removeAssociation(self)
            
        # remove references to other objects
        if self.getSensationType() == Sensation.SensationType.Feeling:
            self.firstAssociateSensation = None
            self.otherAssociateSensation = None
        self.robot = None
        
        # remove copy references
        if self.originalSensation != None:
            i = 0
            while i < len(self.originalSensation.copySensations):
                if self.originalSensation.copySensations[i] is self:
                    del self.originalSensation.copySensations[i]
                    break
                i += 1
            self.originalSensation = None
        # if we have only one copy, then
        if len(self.copySensations) > 0:
            # first vopy will now be next original
            self.copySensations[0].originalSensation = None
            self.copySensations[0].originalSensationId = self.copySensations[0].id
            i=1
            # next copySentations will get first one as original
            while i < len(self.copySensations):
                self.copySensations[i].originalSensation = self.copySensations[0]
                self.copySensations[i].originalSensationId = self.copySensations[0].id
                self.copySensations[0].copySensations.append(self.copySensations[i])
                i +=1
            # finally we don't have references to copySensations
            del self.copySensations[:]
            # Note, that chared referenced data in original and copySensation is handled
            # by python memory handling, when there is one reference less now
            # and data if free-ed, when no rererences 
                
           
        # if we have copy sensations, we are ogiginal one and we
        # must arrange new original ti them
 
        # remove files assiciated to this Sensation
        if not os.path.exists(Sensation.DATADIR):
            os.makedirs(Sensation.DATADIR)

        # first delete files this sensation has created            
        if self.getSensationType() == Sensation.SensationType.Image or \
           self.getSensationType() == Sensation.SensationType.Voice:
            if os.path.exists(self.getFilePath()): 
                try:
                    os.remove(self.getFilePath())
                except Exception as e:
                    print("os.remove(self.getFilePath() error " + str(e))
                    
        binaryFilePath = self.getFilePath(sensationType=Sensation.SensationType.All)
        if os.path.exists(binaryFilePath): 
            try:
                os.remove(binaryFilePath)
            except Exception as e:
                print("os.remove({} error {}".format(binaryFilePath,str(e)))
       
if __name__ == '__main__':

# testing
# create need a Robot as a parameter, so these test don't work until fixed
# TODO fromString(Sensation.toString) -tests are deprecated
# Sensation data in transferred by menory or by byte with tcp
# and str form is for debugging purposes
# Most importand sensations are now voice and image and string form does not handle
# parameters any more. Can be fixed if im plementing parameter type in string
# but it mo more vice to concentrate to byte tranfer for str test will be removed soon.

    from Config import Config, Capabilities
    config = Config()
    capabilities = Capabilities(config=config)
    
    s_Drive=Sensation(associations=[], sensationType = Sensation.SensationType.Drive, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, leftPower = 0.77, rightPower = 0.55)
    print("str s  " + str(s_Drive))
    b=s_Drive.bytes()
    # TODO should s2 be here really association to s, same instance? maybe
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Drive == s2))
    
    #test with create
    print("test with create")
    s_Drive_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Drive, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, leftPower = 0.77, rightPower = 0.55)
    print(("Sensation.create: str s  " + str(s_Drive_create)))
    b=s_Drive_create.bytes()
    # TODO should s2 be here really association to s, same instance? maybe
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create:" + str(s_Drive_create == s2))
    print()

    
    s_Stop=Sensation(associations=[], sensationType = Sensation.SensationType.Stop, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle)
    print("str s  " + str(s_Stop))
    b=s_Stop.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Stop == s2))

    #test with create
    print("test with create")
    s_Stop_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Stop, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle)
    print(("Sensation.create: str s  " + str(s_Stop_create)))
    b=s_Stop_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Stop_create == s2))
    print()
    
    s_Who=Sensation(associations=[], sensationType = Sensation.SensationType.Robot, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle)
    print("str s  " + str(s_Who))
    b=s_Who.bytes()
    s2=Sensation(associations=[], bytes=b)
    print("str s2 " + str(s2))
    print(str(s_Who == s2))
    
    #test with create
    print("test with create")
    s_Who_create=Sensation.create(associations=[], sensationType = Sensation.SensationType.Robot, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle)
    print(("Sensation.create: str s  " + str(s_Who_create)))
    b=s_Who_create.bytes()
    s2=Sensation.create(associations=[], bytes=b)
    print("Sensation.create: str s2 " + str(s2))
    print("Sensation.create: " + str(s_Who_create == s2))
    print()

 
    # TODO
    # We can't  test this way any more, because SEnsation we create cant be used until it is created  
#     s_HearDirection=Sensation(associations=[Sensation.Association(self_sensation=s_HearDirection, sensation=s_Drive)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, hearDirection = 0.85)
#     print(("str s  " + str(s_HearDirection)))
#     b=s_HearDirection.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_HearDirection == s2))
# 
#     #test with create
#     print("test with create")
#     s_HearDirection_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_HearDirection_create, sensation=s_Drive_create)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.HearDirection, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, hearDirection = 0.85)
#     print(("Sensation.create: str s  " + str(s_HearDirection_create)))
#     b=s_HearDirection_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_HearDirection_create == s2))
#     print()
# 
#     s_Azimuth=Sensation(associations=[Sensation.Association(self_sensation=s_Azimuth, sensation=s_HearDirection)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, azimuth = -0.85)
#     print(("str s  " + str(s_Azimuth)))
#     b=s_Azimuth.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Azimuth == s2))
# 
#     #test with create
#     print("test with create")
#     s_Azimuth_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Azimuth_create, sensation=s_Who_create)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Azimuth, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, azimuth = -0.85)
#     print(("Sensation.create: str s  " + str(s_Azimuth_create)))
#     b=s_Azimuth_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Azimuth_create == s2))
#     print()
# 
#     s_Acceleration=Sensation(associations=[Sensation.Association(self_sensation=s_Acceleration, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Acceleration, sensation=s_Azimuth)], receivedFrom=['localhost', 'raspberry'], sensationType = Sensation.SensationType.Acceleration, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, x = -0.85, y = 2.33, z = -0.085)
#     print(("str s  " + str(s_Acceleration)))
#     b=s_Acceleration.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Acceleration == s2))
# 
#     #test with create
#     print("test with create")
#     s_Acceleration_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Acceleration_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Acceleration_create, sensation=s_Azimuth_create)], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Acceleration, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, x = -0.85, y = 2.33, z = -0.085)
#     print(("Sensation.create: str s  " + str(s_Acceleration_create)))
#     b=s_Acceleration_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " +str(s_Acceleration_create == s2))
#     print()
# 
#     
#     s_Observation=Sensation(associations=[Sensation.Association(self_sensation=s_Observation, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Observation, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Observation, sensation=s_Acceleration)], receivedFrom=['localhost', 'raspberry', 'virtualWalle'], sensationType = Sensation.SensationType.Observation, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, observationDirection= -0.85, observationDistance=-3.75)
#     print(("str s  " + str(s_Observation)))
#     b=s_Observation.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s_Observation == s2))
# 
#     #test with create
#     print("test with create")
#     s_Observation_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Observation_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Observation_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Observation_create, sensation=s_Acceleration_create)],  receivedFrom=['localhost', 'raspberry', 'virtualWalle',  'remoteWalle'], sensationType = Sensation.SensationType.Observation, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, observationDirection= -0.85, observationDistance=-3.75)
#     print(("Sensation.create: str s  " + str(s_Observation_create)))
#     b=s_Observation_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Observation_create == s2))
#     print()
#     
#     # voice
#     s_VoiceFilePath=Sensation(associations=[Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_Observation),Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_HearDirection),Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_Azimuth),Sensation.Association(self_sensation=s_VoiceFilePath, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, filePath="my/own/path/to/file")
#     print("str s  " + str(s_VoiceFilePath))
#     b=s_VoiceFilePath.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print(("str s2 " + str(s2)))
#     print(str(s_VoiceFilePath == s2))
# 
#     #test with create
#     print("test with create")
#     s_VoiceFilePath_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_VoiceFilePath_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, filePath="my/own/path/to/file")
#     print(("Sensation.create: str s  " + str(s_VoiceFilePath_create)))
#     b=s_VoiceFilePath_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_VoiceFilePath_create == s2))
#     print()
# 
#     s_VoiceData=Sensation(associations=[Sensation.Association(self_sensation=s_VoiceData, sensation=s_VoiceFilePath),Sensation.Association(self_sensation=s_VoiceData, sensation=s_Observation),Sensation.Association(self_sensation=s_VoiceData, sensation=s_HearDirection),Sensation.Association(self_sensation=s_VoiceData, sensation=s_Azimuth),Sensation.Association(self_sensation=s_VoiceData, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, data=b'\x01\x02\x03\x04\x05')
#     print(("str s  " + str(s_VoiceData)))
#     b=s_VoiceData.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_VoiceData == s2))
# 
#     #test with create
#     print("test with create")
#     s_VoiceData_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_VoiceFilePath_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_VoiceData_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Voice, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle,  data=b'\x01\x02\x03\x04\x05')
#     print(("Sensation.create: str s  " + str(s_VoiceData_create)))
#     b=s_VoiceData_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " +str(s_VoiceData_create == s2))
#     print()
#     
#     # image    
#     s_ImageFilePath=Sensation(associations=[Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_Observation),Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_HearDirection),Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_Azimuth),Sensation.Association(self_sensation=s_ImageFilePath, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, filePath="my/own/path/to/file")
#     print(("str s  " + str(s_ImageFilePath)))
#     b=s_ImageFilePath.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_ImageFilePath == s2))
# 
#     #test with create
#     print("test with create")
#     s_ImageFilePath_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_ImageFilePath_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, filePath="my/own/path/to/file")
#     print(("Sensation.create: str s  " + str(s_ImageFilePath_create)))
#     b=s_ImageFilePath_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_ImageFilePath_create == s2))
#     print()
# 
#     s_ImageData=Sensation(associations=[Sensation.Association(self_sensation=s_ImageData, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_ImageData, sensation=s_Observation),Sensation.Association(self_sensation=s_ImageData, sensation=s_HearDirection),Sensation.Association(self_sensation=s_ImageData, sensation=s_Azimuth),Sensation.Association(self_sensation=s_ImageData, sensation=s_Acceleration)], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
#     print("str s  " + str(s_ImageData))
#     b=s_ImageData.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_ImageData == s2))
# 
#     #test with create
#     print("test with create")
#     s_ImageData_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_ImageData_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_ImageData_create, sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Image, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Muscle, image=PIL_Image.new(mode=Sensation.MODE, size=(10,10)))
#     print("Sensation.create: str s  " + str(s_ImageData_create))
#     b=s_ImageData_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " +str(s_ImageData_create == s2))
#     print()
# 
#     s_Calibrate=Sensation(associations=[Sensation.Association(self_sensation=s_Calibrate, sensation=s_ImageData),Sensation.Association(self_sensation=s_Calibrate, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_Calibrate, sensation=s_Observation),Sensation.Association(self_sensation=s_Calibrate, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Calibrate, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Calibrate, sensation=s_Acceleration)], sensationType = Sensation.SensationType.Calibrate, memoryType = Sensation.MemoryType.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, robotType = Sensation.RobotType.Muscle, hearDirection = 0.85)
#     print("str s  " + str(s_Calibrate))
#     b=s_Calibrate.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Calibrate == s2))
# 
#     #test with create
#     print("test with create")
#     s_Calibrate_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_ImageData_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Calibrate_create, sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Calibrate, memoryType = Sensation.MemoryType.Sensory, calibrateSensationType = Sensation.SensationType.HearDirection, robotType = Sensation.RobotType.Muscle, hearDirection = 0.85)
#     print("Sensation.create: str s  " + str(s_Calibrate_create))
#     b=s_Calibrate_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Calibrate_create == s2))
#     print()
# 
# #    s_Capability=Sensation(associations=[s_Calibrate,s_VoiceData,s_VoiceFilePath,s_ImageData,s_ImageFilePath,s_Observation,s_HearDirection,s_Azimuth,s_Acceleration], sensationType = Sensation.SensationType.Capability, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, capabilities = [Sensation.SensationType.Drive, Sensation.SensationType.HearDirection, Sensation.SensationType.Azimuth])
#     s_Capability=Sensation(associations=[Sensation.Association(self_sensation=s_Capability, sensation=s_Calibrate),Sensation.Association(self_sensation=s_Capability, sensation=s_VoiceData),Sensation.Association(self_sensation=s_Capability, sensation=s_VoiceFilePath),Sensation.Association(self_sensation=s_Capability, sensation=s_ImageData),Sensation.Association(self_sensation=s_Capability, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_Capability, sensation=s_Observation),Sensation.Association(self_sensation=s_Capability, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Capability, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Capability, sensation=s_Acceleration)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, capabilities = capabilities)
#     print(("str s  " + str(s_Capability)))
#     b=s_Capability.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Capability == s2))
#     
#      #test with create
#     print("test with create")
#     s_Capability_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Capability_create, sensation=s_Calibrate_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_VoiceData_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_VoiceFilePath_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_ImageData_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Capability_create, sensation=s_Acceleration_create)], receivedFrom=['localhost'], sensationType = Sensation.SensationType.Capability, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, capabilities = capabilities)
#     print(("Sensation.create: str s  " + str(s_Capability_create)))
#     b=s_Capability_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Capability_create == s2))
#     
#     # item
#     
#     s_Item=Sensation(associations=[Sensation.Association(self_sensation=s_Item, sensation=s_Calibrate),Sensation.Association(self_sensation=s_Item, sensation=s_VoiceData),Sensation.Association(self_sensation=s_Item, sensation=s_VoiceFilePath),Sensation.Association(self_sensation=s_Item, sensation=s_ImageData),Sensation.Association(self_sensation=s_Item, sensation=s_ImageFilePath),Sensation.Association(self_sensation=s_Item, sensation=s_Observation),Sensation.Association(self_sensation=s_Item, sensation=s_HearDirection),Sensation.Association(self_sensation=s_Item, sensation=s_Azimuth),Sensation.Association(self_sensation=s_Item, sensation=s_Acceleration)], sensationType = Sensation.SensationType.Item, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, name='person')
#     print(("str s  " + str(s_Item)))
#     b=s_Item.bytes()
#     s2=Sensation(associations=[], bytes=b)
#     print("str s2 " + str(s2))
#     print(str(s_Item == s2))
#     
#      #test with create
#     print("test with create")
#     s_Item_create=Sensation.create(associations=[Sensation.Association(self_sensation=s_Item_create, sensation=s_Calibrate_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_VoiceData_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_VoiceFilePath_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_ImageData_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_ImageFilePath_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_Observation_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_HearDirection_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_Azimuth_create),Sensation.Association(self_sensation=s_Item_create, sensation=s_Acceleration_create)], sensationType = Sensation.SensationType.Item, memoryType = Sensation.MemoryType.Sensory, robotType = Sensation.RobotType.Sense, name='person')
#     print(("Sensation.create: str s  " + str(s_Item_create)))
#     b=s_Item_create.bytes()
#     s2=Sensation.create(associations=[], bytes=b)
#     print("Sensation.create: str s2 " + str(s2))
#     print("Sensation.create: " + str(s_Item_create == s2))
    
