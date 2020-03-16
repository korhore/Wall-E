'''
Created on 12.03.2020
Updated on 16.03.2020

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
from PIL import Image as PIL_Image
import wx

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

class Visual(Robot):
    
    WIDTH=1000
    HEIGHT=400
    
    IDENTITY_SIZE=80
    IMAGE_SIZE=40
    
    
    SENSATION_LINES=18
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
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        
        self.app = Visual.MainApp(robot=self)
        #self.app.setRobot(self)
        
        self.wxWorker = Visual.wxWorker(robot=self, app=self.app)
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
            
        self.wxWorker.join()       # wait UI thread stops

       
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run ALL SHUT DOWN")
        
    def process(self, transferDirection, sensation, association=None):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr()) #called
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
        else:
            wx.PostEvent(self.app.frame, Visual.Event(eventType=Visual.ID_SENSATION, data=sensation))
            
    '''
    Helpels
    '''
            
    def PILTowx (image, size, setMask=False):
        width, height = image.size
        bitmap = wx.Bitmap.FromBuffer(width, height, image.tobytes())
        if width > height:
            height = int((float(height)/float(width)*float(size)))
            width=size
        else:
            width = int((float(width)/float(height)*float(size)))
            height=size
        wxImage = bitmap.ConvertToImage()
        wxImage = wxImage.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        
        if wxImage.HasMask() :
            wxImage.InitAlpha()
        if setMask and not wxImage.HasMask() :
            wxImage.SetMaskColour(red=255, green=255, blue=255)
       
        #wxBitmap = wx.BitmapFromImage(wxImage)
        wxBitmap = wx.Bitmap(wxImage)
        bmapHasMask  = wxBitmap.GetMask()    # "GetMask()", NOT "HasMask()" !
        #bmapHasAlpha = wxBitmap.HasAlpha()
        if setMask and not bmapHasMask:
            SetMaskColour(self, red, green, blue)
            wxBitmap.setAlpha()
            
        return wxBitmap
        
    
    def wx2PIL (bitmap):
        size = tuple(bitmap.GetSize())
        try:
            buf = size[0]*size[1]*3*"\x00"
            bitmap.CopyToBuffer(buf)
        except:
            del buf
            buf = bitmap.ConvertToImage().GetData()
        return PIL_Image.frombuffer("RGB", size, buf, "raw", "RGB", 0, 1)
            

            
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
            self.app.MainLoop() #called
    
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
        def __init__(self, parent, id, robot):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, robot.getWho()) #called
            self.robot = robot
     
            self.SetInitialSize((Visual.WIDTH, Visual.HEIGHT))
            
            Visual.setEventHandler(self, Visual.ID_SENSATION, self.OnSensation)
            
            self.emptyStaticText = wx.StaticText(self, label='')

            
            # try grid
            vbox = wx.BoxSizer(wx.VERTICAL)
            #self.identity = wx.TextCtrl(self, style=wx.TE_RIGHT)
            if len(Robot.images) > 0:
                bitmap = Visual.PILTowx(image=Robot.images[0], size=Visual.IDENTITY_SIZE, setMask=True)
                self.identity = wx.StaticBitmap(self, -1, bitmap, (10, 5), (bitmap.GetWidth(), bitmap.GetHeight()))
                #icon = wx.EmptyIcon()
                icon = wx.Icon()
                icon.CopyFromBitmap(bitmap)
                self.SetIcon(icon)                
                #self.SetIcon(wx.IconFromBitmap(bitmap))
            else:
                self.identity = wx.StaticText(self, label=self.robot.getWho())
                
            vbox.Add(self.identity, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            self.gs = wx.GridSizer(Visual.SENSATION_LINES+1,
                                   Visual.SENSATION_COLUMNS,
                                   5, 5)
            headerFont = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
             
            self.gs.AddMany( [(wx.StaticText(self, label=Visual.SENSATION_COLUMN_TYPE_NAME), 0, wx.EXPAND),         # 0
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_DATA_NAME), 0, wx.EXPAND),                       # 1
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_MEMORY_NAME), 0, wx.EXPAND),                     # 2
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_DIRECTION_NAME), 0, wx.EXPAND|wx.ALIGN_CENTER),  # 3
                (wx.StaticText(self, label=Visual.SENSATION_COLUMN_TIME_NAME), 0, wx.EXPAND)])                      # 4
            for j in range(Visual.SENSATION_COLUMNS):
                item = self.gs.GetItem(j)               
                item.GetWindow().SetFont(headerFont) 
                               
            for i in range(Visual.SENSATION_LINES):
                for j in range(Visual.SENSATION_COLUMNS):
                    if j is Visual.SENSATION_COLUMN_DATA:
                        self.gs.Add(wx.StaticBitmap(parent=self, id=-1, pos=(0, -Visual.IMAGE_SIZE/2), size=(Visual.IMAGE_SIZE,Visual.IMAGE_SIZE)), 0, wx.EXPAND)
                        #self.gs.Add(wx.StaticBitmap(parent=self, id=-1, bitmap=None, pos=(10, 5), size=(0, 0)), 0, wx.EXPAND)
                    else:
                        self.gs.Add(wx.StaticText(self), 0, wx.EXPAND)
                
                
            vbox.Add(self.gs, proportion=1, flag=wx.EXPAND)
            self.SetSizer(vbox)
            
            
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(wx.Button(self, Visual.ID_START, 'Start'), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            hbox.Add(wx.Button(self, Visual.ID_STOP, 'Stop'), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            vbox.Add(hbox, flag=wx.EXPAND)
            
            self.status = wx.StaticText(self, -1)   
            vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            self.Fit()
                    
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
                
                for i in range(Visual.SENSATION_LINES-2,0,-1):
                    for j in range(Visual.SENSATION_COLUMNS):
                        fromInd=(i*Visual.SENSATION_COLUMNS) +j
                        from_item = self.gs.GetItem(fromInd)
                        toInd = ((i+1)*Visual.SENSATION_COLUMNS) +j
                        to_item = self.gs.GetItem(toInd)
                        
                        if from_item is not None and from_item.IsWindow() and\
                           to_item is not None and to_item.IsWindow():
                            if j == Visual.SENSATION_COLUMN_DATA:
                                bitmap = from_item.GetWindow().GetBitmap()
                                to_item.GetWindow().SetBitmap(bitmap)
                                if self.gs.IsShown(fromInd):
                                    self.gs.Show(toInd)
                                else:
                                    self.gs.Hide(toInd)
                                self.Refresh()
                            else:
                                #print("OnSensation fromInd " + str(fromInd) + " " + from_item.GetWindow().GetLabel() + " toInd "+ str(toInd) + " " + to_item.GetWindow().GetLabel())
                                to_item.GetWindow().SetLabel(from_item.GetWindow().GetLabel())
                        else:
                            print("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " error")
                
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_TYPE)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getSensationTypeString(sensationType=sensation.getSensationType()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_DATA)
                if item is not None and item.IsWindow():
                    image = sensation.getImage()
                    if image is not None:
                        self.gs.Show(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_DATA)
                        bitmap = Visual.PILTowx(image=image, size=Visual.IMAGE_SIZE)
                        item.GetWindow().SetBitmap(bitmap)
                        item.GetWindow().SetSize((Visual.IMAGE_SIZE,Visual.IMAGE_SIZE))
                    else:
                        self.gs.Hide(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_DATA)
                    self.Refresh()
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_MEMORY)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getMemoryString(memory=sensation.getMemory()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_DIRECTION)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getDirectionString(direction=sensation.getDirection()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_TIME)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(systemTime.ctime(sensation.getTime()))
                    
                self.Refresh()


            else:
                # Process results here
                self.status.SetLabel('Sensation is None in Sensation Event')
   
    class MainApp(wx.App):
        """Class Main App."""
        def __init__(self, robot, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
            self.robot=robot
            wx.App.__init__(self, redirect=redirect, filename=filename, useBestVisual=useBestVisual, clearSigInt=clearSigInt)


        def OnInit(self):
            """Init Main App."""
            self.frame = Visual.MainFrame(parent=None, id=-1, robot=self.getRobot())
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