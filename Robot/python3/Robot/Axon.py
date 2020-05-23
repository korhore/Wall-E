'''
Created on Jan 19, 2014
Updated on 07.08.2019
@author: reijo.korhonen@gmail.com
'''

from queue import Queue
from Sensation import Sensation

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
    

    def __init__(self, robot):
        self.robot = robot      # owner robot of this axon
        self.queue = Queue()
       
    def put(self, robot, transferDirection, sensation, association=None, detach=True):
        self.robot.log("Axon put from {} to {} with original queue length {} full {}".format(robot.getWho(),self.robot.getWho(), self.queue.qsize(), self.queue.full()))
        sensation.attach(self.robot)                        # take ownership
# let Robots decide locations
#         if len(sensation.getLocations()) == 0:              # if sensations does not have locations yet, set it as robots locations.
#             sensation.setLocations(self.robot.getLocations())   #
        if detach:
            sensation.detach(robot)         # release from caller
        self.queue.put((transferDirection, sensation, association))
        self.robot.log("Axon put from {} to {} with final queue length {} full {}".format(robot.getWho(),self.robot.getWho(), self.queue.qsize(), self.queue.full()))
 
    '''
    Robot calls this to get its sensations
    Robot gets sensations only from its own Axon,
    so robot is not mentioned as parameter 
    '''       
    def get(self):
        self.robot.log("Axon get from {} original queue length {} empty {} full {}".format(self.robot.getWho(), self.queue.qsize(), self.queue.empty(), self.queue.full()))
        (transferDirection, sensation, association) = self.queue.get()
        self.robot.log("Axon done get from {} result queue length {} empty {} full {}".format(self.robot.getWho(), self.queue.qsize(), self.queue.empty(), self.queue.full()))
        return transferDirection, sensation, association
        
    def empty(self):
        return self.queue.empty()
