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
    
    SENSATION_LINES=10
    SENSATION_COLUMNS=5
    
    SENSATION_COLUMN_TYPE =         0
    SENSATION_COLUMN_DATA =         1
    SENSATION_COLUMN_MEMORY =       2
    SENSATION_COLUMN_DIRECTION =    3
    SENSATION_COLUMN_TIME =         4

    SENSATION_COLUMN_TYPE_NAME =         'Type'
    SENSATION_COLUMN_DATA_NAME =         'Data'
    SENSATION_COLUMN_MEMORY_NAME =       'Memory'
    SENSATION_COLUMN_DIRECTION_NAME =    'Direction'
    SENSATION_COLUMN_TIME_NAME =         'Time'
    # Button definitions
    ID_START = wx.NewId()
    ID_STOP = wx.NewId()

    # Sensation visualisation definitions
    ID_SENSATION = wx.NewId()
        
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
            # or if we can sense, but there is something in our Axon, process it
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
        else:
            wx.PostEvent(self.app.frame, Visual.Event(eventType=Visual.ID_SENSATION, data=sensation))

            
    def setEventHandler(win, eventId, func):
        """Set Event Handler"""
        win.Connect(-1, -1, eventId, func) #called

                     
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
    
    class Event(wx.PyEvent):
        """Simple event to carry arbitrary result data."""
        def __init__(self, eventType, data):
            """Init Result Event."""
            wx.PyEvent.__init__(self)
            self.SetEventType(eventType)
            self.data = data
            
    # GUI Frame class that spins off the worker thread
    class MainFrame(wx.Frame):
        """Class MainFrame."""
        def __init__(self, parent, id):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, 'Thread Test') #called
            
            Visual.setEventHandler(self, Visual.ID_SENSATION, self.OnSensation)

            
            # try grid
            vbox = wx.BoxSizer(wx.VERTICAL)
            self.display = wx.TextCtrl(self, style=wx.TE_RIGHT)
            vbox.Add(self.display, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            self.gs = wx.GridSizer(Visual.SENSATION_LINES,
                                   Visual.SENSATION_COLUMNS,
                                   5, 5)
            
            self.status = wx.StaticText(self, -1)
    
            self.gs.AddMany( [(wx.StaticText(self, label=Visual.SENSATION_COLUMN_TYPE_NAME), 0, wx.EXPAND), # 0
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_DATA_NAME), 0, wx.EXPAND),               # 1
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_MEMORY_NAME), 0, wx.EXPAND),             # 2
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_DIRECTION_NAME), 0, wx.EXPAND|wx.ALIGN_CENTER),                 # 3
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_TIME_NAME), 0, wx.EXPAND),                 # 4
                
                (wx.Button(self, label='9'), 0, wx.EXPAND),                 # 5
                (wx.Button(self, label='/'), 0, wx.EXPAND),                 # 5
                (wx.Button(self, label='4'), 0, wx.EXPAND),
                (wx.Button(self, label='5'), 0, wx.EXPAND),
                (wx.Button(self, label='6'), 0, wx.EXPAND),
                (wx.Button(self, label='*'), 0, wx.EXPAND),
                (wx.Button(self, label='1'), 0, wx.EXPAND),
                (wx.Button(self, label='2'), 0, wx.EXPAND),
                (wx.Button(self, label='3'), 0, wx.EXPAND),
                (wx.Button(self, label='-'), 0, wx.EXPAND),
                (wx.Button(self, label='0'), 0, wx.EXPAND),
                (wx.Button(self, label='.'), 0, wx.EXPAND),
                (wx.Button(self, label='='), 0, wx.EXPAND),
                (wx.Button(self, label='+'), 0, wx.EXPAND),
                
                (wx.Button(self, Visual.ID_START, 'Start'), 0, wx.EXPAND),
                (wx.Button(self, Visual.ID_STOP, 'Stop'), 0, wx.EXPAND),
                (self.status, 0, wx.EXPAND)])
                
            vbox.Add(self.gs, proportion=1, flag=wx.EXPAND)
            self.SetSizer(vbox)
                
        
#             # Dumb sample frame with two buttons
#             wx.Button(self, Visual.ID_START, 'Start', pos=(0,0))
#             wx.Button(self, Visual.ID_STOP, 'Stop', pos=(0,50))
#             self.status = wx.StaticText(self, -1, '', pos=(0,100))
    
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
            
        def OnSensation(self, event):
            """Stop Computation."""
            #show sensation
            if event.data is not None:
                # Thread aborted (using our convention of None return)
                sensation=event.data
                self.status.SetLabel('Got Sensation Event')
                
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_TYPE)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getSensationTypeString(sensationType=sensation.getSensationType()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_MEMORY)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getMemoryString(memory=sensation.getMemory()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_DIRECTION)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getDirectionString(direction=sensation.getDirection()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_TIME)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(systemTime.ctime(sensation.getTime()))

            else:
                # Process results here
                self.status.SetLabel('Sensation is None in Sensation Event')
   
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