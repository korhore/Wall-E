'''
Created on Jan 19, 2014
Updated on 29.11.2021
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
    MAX_QUEUE_LENGTH = 128
    # Robot settings"
    AxonLogLevel = enum(No=-1, Critical=0, Error=1, Normal=2, Detailed=3, Verbose=4)
     

    def __init__(self, robot):
        self.robot = robot              # owner robot of this axon
        self.queue = Queue()            # wait queue, where reader gets it's Sensations
        self.qualityOfServiceQueues={}  # queues, where Sensations that are got from writers
                                        # will be put
        for memorytype in Sensation.QoSMemoryTypesOrdered:
            self.qualityOfServiceQueues[memorytype] = Queue()
                                         
       
    def put(self, robot, transferDirection, sensation):
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon put from {} to {} with original queue length {} full {}".format(robot.getName(),self.robot.getName(), self.queue.qsize(), self.queue.full()))
        sensation.attach(robot=self.robot)                        # take ownership
        # TODO commented out, because. seems attach(/detach logic is broken
# let Robots decide locations
#         if len(sensation.getLocations()) == 0:              # if sensations does not have locations yet, set it as robots locations.
#             sensation.setLocations(self.robot.getLocations())   #
        sensation.detach(robot=robot)         # release from caller
        
#         # SensationType.RobotState goes always to fastest queue
          # select QOS queue only if we have sensation in normal queue or MemoryType is not first ordered Sensory
#         # so we release reader, that was blocked
        if self.queue.empty() or sensation.getSensationType() == Sensation.SensationType.RobotState:
            queue = self.queue
        else:
            queue = self.qualityOfServiceQueues[sensation.getMemoryType()]

        while queue.qsize() > Axon.MAX_QUEUE_LENGTH:
            (_, _) = queue.get()
            self.robot.log("{} Axon skipped overloaded oldest Sensation, but will put asked one, before put queue length {} empty {} full {}".format(self.robot.getName(),queue.qsize(), queue.empty(), queue.full()))
 
        #self.queue.put((transferDirection, sensation))
        queue.put((transferDirection, sensation))
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon put from {} to {} with final queue length {} full {}".format(robot.getName(),self.robot.getName(), queue.qsize(), queue.full()))
 
    '''
    Robot calls this to get its sensations
    Robot gets sensations only from its own Axon,
    so robot is not mentioned as parameter 
    '''       
    def get(self, robot):
        # QOS meaning
        # if normal queue is empty, we fill it from QoS queues in Sensation.QoSMemoryTypesOrdered order
        # but with only one sensation, so Sensory will be served first, then Working and last LongTerm,
        # as they should
        if self.queue.empty():
            for memorytype in Sensation.QoSMemoryTypesOrdered:
                # get sensation from  QOS queue and put to normal waiting queue
                while self.queue.empty() and not self.qualityOfServiceQueues[memorytype].empty():
                    (transferDirection, sensation) = self.qualityOfServiceQueues[memorytype].get()
                    self.queue.put((transferDirection, sensation))
                    break

        # if queues were all empty, we wait normal way
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon get from {} original queue length {} empty {}".format(self.robot.getName(), self.length(), self.empty()))
        (transferDirection, sensation) = self.queue.get()
        self.robot.log(logLevel=Axon.AxonLogLevel.Detailed, logStr="Axon done get from {} final queue length {} empty {}".format(self.robot.getName(), self.length(), self.empty()))
        #sensation.detachAll() # TODO We should not need this, but without this now, we will get Not Forgottable robot Communications
                               # Meaning, that sensation.detach() is not done somewhere
        #sensation.attach(robot=robot) #attached already to robot=self.robot
        return transferDirection, sensation
        
    def empty(self):
        for memorytype in Sensation.QoSMemoryTypesOrdered:
            if not self.qualityOfServiceQueues[memorytype].empty():
                return False
        return self.queue.empty()
    
    def length(self):
        l=self.queue.qsize()
        for memorytype in Sensation.QoSMemoryTypesOrdered:
            l+= self.qualityOfServiceQueues[memorytype].qsize()
        return l

