'''
Created on 03.06.2020
Updated on 13.06.2021
@author: reijo.korhonen@gmail.com

test Robot.Identity class

Testing is complicated, because we must test Identity thread
and unittest goes to tearDown while we are in the middle of testing.
so we must set sleep in tearDown

python3 -m unittest tests/testidentity.py



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
    MAINNAMES = ["IdentityTestCaseMainName"]
    
    '''
    Robot modeling
    '''
    
    def getAxon(self):
        return self.axon
    def getId(self):
        return 1.1
    def getParent(self):
        return None
    def getName(self):
        return "IdentityTestCase"
    def getName(self):
        #print('CommunicationTestCase getName')
        return "Wall-E"
    def getMainNames(self):
        return self.MAINNAMES
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
                     print(self.identity.getName() + ":" + str( self.identity.config.level) + ":" + Sensation.Modes[self.identity.mode] + ": " + logStr)
    
    '''
    route to test class
    '''
    def route(self, transferDirection, sensation):
        self.log(logLevel=self.identity.LogLevel.Normal, logStr='route: ' + sensation.toDebugStr())
        self.log(logLevel=self.identity.LogLevel.Detailed, logStr='route: '  + str(transferDirection) +  ' ' + sensation.toDebugStr())
        self.getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
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

        self.identity = Identity(      mainRobot=self,
                                       parent=self,
                                       instanceName='identity',
                                       instanceType= Sensation.InstanceType.SubInstance,
                                       memory = self.memory,
                                       level=2)
        self.identity.SLEEPTIME = 5    # test faster
        self.identity.sleeptime = 5

        self.identity.CLASSIFICATION_TIME = 20
        Identity.CLASSIFICATION_TIME = 20
        
        self.identity.SLEEP_BETWEEN_VOICES = 1


    def tearDown(self):
        if self.identity.isRunning():
            self.identity.stop()
            print('tearDown sleep ' + str(IdentityTestCase.TEST_STOP_TIME) + ' time for self.identity to stop')
            systemTime.sleep(IdentityTestCase.TEST_STOP_TIME)       # give Robot some time to stop

        del self.identity
        del self.axon
        
    def test_Identity(self):
        i=0
        self.identity.start()
        while self.identity.isRunning() and i < 100:
            print('test_Identification sleep ' + str(IdentityTestCase.TEST_TIME) + ' waiting while self.identity.isRunning() and {} < 100: sleep {}s'.format(i, IdentityTestCase.TEST_TIME))
            systemTime.sleep(IdentityTestCase.TEST_TIME)
            i=i+1

if __name__ == '__main__':
    unittest.main()

 
