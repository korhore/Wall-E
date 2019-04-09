'''
Created on Jan 19, 2014

@author: reijo
'''

from queue import Queue
from Sensation import Sensation



class Axon():
    """
    Axon transfers sensation
  """
    

    def __init__(self):
        self.queue = Queue()
       
    def put(self, sensation):
        self.queue.put(sensation)
        
    def get(self):
        return self.queue.get()
        
    def empty(self):
        return self.queue.empty()


        
