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
    

    def __init__(self, host):
        self.queue = Queue()
        self.host = host
        self.who = None
       
    def put(self, sensation):
        self.queue.put(sensation)
        
    def get(self):
        sensation = self.queue.get();
        sensation = self.process(sensation)
        return sensation
        
    def empty(self):
        return self.queue.empty()
    
    def process(self, sensation):
        if sensation.getSensationType() == Sensation.SensationType.Who:
            self.who = sensation.getWho()
        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            self.capabilities = sensation.getCapabilities()
            
        return sensation


    def setWho(self, who):
        self.who = who
    def getWho(self):
        return self.who

    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
    def getCapabilities(self):
        return self.capabilities
    


        
