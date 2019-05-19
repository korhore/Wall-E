'''
Created on Jan 19, 2014
Updated on 19.05.2019
@author: reijo.korhonen@gmail.com
'''

from queue import Queue
from Sensation import Sensation

class Axon():
    """
    Axon transfers sensation from one Robot to other Robot
    All Robots have Axon and they caal Get to get next Sensation tp process
    Leaf Rpbots put Sensatio(s) they create to the parent Robots Axon out-direction
    Middle layer  Sesation(s) to In direction Robots
    until there is and Muscle (Leaf)Robots
  """
    

    def __init__(self):
        self.queue = Queue()
       
    def put(self, sensation):
        self.queue.put(sensation)
        
    def get(self):
        sensation = self.queue.get();
        return self.queue.get()
        
    def empty(self):
        return self.queue.empty()
