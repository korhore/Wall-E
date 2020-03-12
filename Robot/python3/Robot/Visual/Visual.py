'''
Created on 12.03.2020
Updated on 12.03.2020

@author: reijo.korhonen@gmail.com

This class is low level sensory (muscle) for visual
combined with low level sense feedback.
implemented by wxPython and need display hardware and drivers (linux X, Windows its own, etc)

Idea is to implement one way visual and feedback so
that only one function is going on in a time.
Default is to used threading, like Robot-framework uses normally.


'''
import time as systemTime
from threading import Thread
from threading import Timer
import wx

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

class Visual(Robot):

    # Button definitions
    ID_START = wx.NewId()
    ID_STOP = wx.NewId()
        
    # Define notification event for thread completion
    EVT_RESULT_ID = wx.NewId()
    
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0):
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        print("We are in Visual, not Robot")
        
        self.app = Visual.MainApp(0)
        self.app.setRobot(self)
        
        self.wxWorker = Visual.wxWorker(robot=self, app=self.app)

        # not yet running
        self.running=False
                            
                            
    def run(self):
        # default
        self.running=True
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run: Starting robot who " + self.getWho() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()
        self.studyOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        
        # added
        self.wxWorker.start()       # start ui on its own thread
       
       # default
        while self.running:
            # if we can't sense, the we wait until we get something into Axon
            # or if we can sense, but there is something in our xon, process it
            if not self.getAxon().empty() or not self.canSense():
                transferDirection, sensation, association = self.getAxon().get()
                self.log(logLevel=Robot.LogLevel.Normal, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
                self.process(transferDirection=transferDirection, sensation=sensation, association=association)
                # as a test, echo everything to external device
                #self.out_axon.put(sensation)
            else:
                self.sense()
 
        self.mode = Sensation.Mode.Stopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")   

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
       
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run ALL SHUT DOWN")
        
    def process(self, transferDirection, sensation, association=None):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr()) #called
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
            
    def EVT_RESULT(win, func):
        """Define Result Event."""
        win.Connect(-1, -1, Visual.EVT_RESULT_ID, func) #called

                     
    '''
    We can't sense as a meaning of Robot-framework
    even if we can produce feedback.
    '''
                
    def canSense(self):
        return False #     def test_Presense(self): #called

     
    # Thread class that executes wxPython gui on its own thread
    class wxWorker(Thread):
        """Worker Thread Class."""
        def __init__(self, app, robot):
            """Init wxWorker Thread Class."""
            Thread.__init__(self) #called
            self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
            self.app = app
            self.robot = robot
     
        def setRobot(self, robot):
            self.robot=robot
        def getRobot(self):
            return self.robot
        
        def run(self):
            """Run wxWorker Thread."""
            self.app.MainLoop() #ccalled
    
    class ResultEvent(wx.PyEvent):
        """Simple event to carry arbitrary result data."""
        def __init__(self, data):
            """Init Result Event."""
            wx.PyEvent.__init__(self)
            self.SetEventType(Visual.EVT_RESULT_ID)
            self.data = data
            
    # GUI Frame class that spins off the worker thread
    class MainFrame(wx.Frame):
        """Class MainFrame."""
        def __init__(self, parent, id):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, 'Thread Test') #called
    
            # Dumb sample frame with two buttons
            wx.Button(self, Visual.ID_START, 'Start', pos=(0,0))
            wx.Button(self, Visual.ID_STOP, 'Stop', pos=(0,50))
            self.status = wx.StaticText(self, -1, '', pos=(0,100))
    
            self.Bind(wx.EVT_BUTTON, self.OnStart, id=Visual.ID_START)
            self.Bind(wx.EVT_BUTTON, self.OnStop, id=Visual.ID_STOP)
    
        def setRobot(self, robot):
            self.robot=robot #called
        def getRobot(self):
            return self.robot #called
        
        def OnStart(self, event):
            """Start Computation."""
            self.status.SetLabel('Starting computation')
            #self.worker = Visual.WorkerThread(notify_window=self, robot=self.getRobot())
    
        def OnStop(self, event):
            """Stop Computation."""
            #Tell our Robot that we wan't to stop
            self.getRobot().running=False
            self.Close()
    
    class MainApp(wx.App):
        """Class Main App."""
        def OnInit(self):
            """Init Main App."""
            self.frame = Visual.MainFrame(None, -1)
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True

        def setRobot(self, robot):
            self.robot=robot
            self.frame.setRobot(robot)
        def getRobot(self):
            return self.robot
            

if __name__ == "__main__":
    visual = Visual()
    #alsaAudioMicrophonePlayback.start()  