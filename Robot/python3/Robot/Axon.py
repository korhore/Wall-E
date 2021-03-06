'''
Created on Jan 19, 2014
Updated on 26.03.2021
@author: reijo.korhonen@gmail.com
'''

from queue import Queue
from Sensation import Sensation
#from Robot import LogLevel as LogLevel
# We cannot import Robot, because Robot import us,
# so we must duplicate Robot.LogLevel definition here
from enum import Enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class Axon():
    """
    Axon transfers sensation from one Robot to other Robot
    All Robots have Axon and they call Get to get next Sensation to process.
    Leaf Robots put Sensation(s) they create to the parent Robots Axon Up TransferDirection
    to Middle layer Robots until MainRobot is reached.
    
    MainRobot transfers Sensations it gets to Down TransferDirection to SubRobots that have
    capability (or subrobots subrobot has capability) to process this Sensation
    until Leaf Robot is reached.
  """
    MAX_QUEUE_LENGTH = 256
    # Robot settings"
    AxonLogLevel = enum(No=-1, Critical=0, Error=1, Normal=2, Detailed=3, Verbose=4)
     

    def __init__(self, robot):
        self.robot = robot      # owner robot of this axon
        self.queue = Queue()
       
    def put(self, robot, transferDirection, sensation):
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon put from {} to {} with original queue length {} full {}".format(robot.getName(),self.robot.getName(), self.queue.qsize(), self.queue.full()))
        sensation.attach(robot=self.robot)                        # take ownership
        # TODO commented out, because. seems attach(/detach logic is broken
# let Robots decide locations
#         if len(sensation.getLocations()) == 0:              # if sensations does not have locations yet, set it as robots locations.
#             sensation.setLocations(self.robot.getLocations())   #
        sensation.detach(robot=robot)         # release from caller
        while self.queue.qsize() > Axon.MAX_QUEUE_LENGTH:
            (_, _) = self.queue.get()
            self.robot.log("{} Axon skipped overloaded oldest Sensation, but will put asked one".format(self.robot.getName()))
        self.queue.put((transferDirection, sensation))
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon put from {} to {} with final queue length {} full {}".format(robot.getName(),self.robot.getName(), self.queue.qsize(), self.queue.full()))
 
    '''
    Robot calls this to get its sensations
    Robot gets sensations only from its own Axon,
    so robot is not mentioned as parameter 
    '''       
    def get(self, robot):
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon get from {} original queue length {} empty {} full {}".format(self.robot.getName(), self.queue.qsize(), self.queue.empty(), self.queue.full()))
        (transferDirection, sensation) = self.queue.get()
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon done get from {} final queue length {} empty {} full {}".format(self.robot.getName(), self.queue.qsize(), self.queue.empty(), self.queue.full()))
        #sensation.detachAll() # TOTO We should not need this, but without this now, we will get Not Forgottable robot Communications
                              # Meaning, that sensation.detach() is not done somewhere
        #sensation.attach(robot=robot) #attached allready to robot=self.robot
        return transferDirection, sensation
        
    def empty(self):
        return self.queue.empty()
    
    def length(self):
        return self.queue.qsize()

