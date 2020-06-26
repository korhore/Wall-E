'''
Created on 03.06.2020
Updated on 03.06.2020
@author: reijo.korhonen@gmail.com

test Robot.Identification class
you must provide models/research
PYTHONPATH=/<here it is>/models/research python3 -m unittest tests/testidentification.py

Testing is complicated, because we must test Identity thread
and unittest goes to tearDown while we are in the middle of testing.
so we must set sleep in teadDown


'''
import time as systemTime
import os
import io
import shutil
import ntpath


import unittest
from Sensation import Sensation
from Robot import Robot, Identity
from Axon import Axon
from Memory import Memory
from Config import Config

from PIL import Image as PIL_Image


class IdentityTestCase(unittest.TestCase):
    TEST_TIME = 10
    TEST_STOP_TIME = 10  
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getWho(self):
        return "IdentityTestCase"
    def getWho(self):
        #print('CommunicationTestCase getWho')
        return "Wall-E"
    def getLocation(self): 
        return 'testLocation'  
    def getExposures(self):
#        return ['Eva']
        return ['Eva','father','family']
    def log(self, logStr, logLevel=None):
        #print('CommunicationTestCase log')
        if hasattr(self, 'identity'):
            if self.identity:
                if logLevel == None:
                    logLevel = self.identity.LogLevel.Normal
                if logLevel <= self.identity.getLogLevel():
                     print(self.identity.getWho() + ":" + str( self.identity.config.level) + ":" + Sensation.Modes[self.identity.mode] + ": " + logStr)
    
    '''
    Testing    
    '''
    
    def setUp(self):
        self.isFirstSleep=True
        self.processTimeSum = 0.0
        self.processNumber = 0

        self.axon = Axon(robot=self)
        
        self.memory = Memory(robot = self,
                             maxRss = Config.MAXRSS_DEFAULT,
                             minAvailMem = Config.MINAVAILMEM_DEFAULT)

        self.identity = Identity(parent=self,
                                       instanceName='identity',
                                       instanceType= Sensation.InstanceType.SubInstance,
                                       memory = self.memory,
                                       level=2)


    def tearDown(self):
        print('sleep ' + str(IdentityTestCase.TEST_TIME) + ' to Stop Robot and test finishes')
        systemTime.sleep(IdentityTestCase.TEST_TIME)       # give Robot some time to stop
        self.identity.getAxon().put(robot=self,
                                                    transferDirection=Sensation.TransferDirection.Up,
                                                    sensation=self.identity.createSensation(associations=[], sensationType = Sensation.SensationType.Stop))
        print('sleep ' + str(IdentityTestCase.TEST_STOP_TIME) + ' time for Robot to process Stop Sensation')
        systemTime.sleep(IdentityTestCase.TEST_STOP_TIME)       # give Robot some time to stop

        del self.identity
        del self.axon
        
    def test_Identification(self):
        # how to test?
        i=0
        self.identity.start()
        while self.identity.isRunning() and i < 100:
            print('test_Identification sleep ' + str(IdentityTestCase.TEST_TIME) + ' waiting test to finish {}'.format(i))
            systemTime.sleep(IdentityTestCase.TEST_TIME)
            i=i+1

if __name__ == '__main__':
    unittest.main()

 
