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
    
    MainRobot transfers Sensatations it gets to Down TransferDirection to SubRobots that have
    capability (or subrobots subrobot has capability) to process this Sensation
    until Leaf Robot is reached-
  """
    

    def __init__(self):
        self.queue = Queue()
       
    def put(self, transferDirection, sensation, association=None):
        self.queue.put((transferDirection, sensation, association))
        
    def get(self):
        (transferDirection, sensation, association) = self.queue.get()
        return transferDirection, sensation, association
        
    def empty(self):
        return self.queue.empty()
