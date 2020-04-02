'''
Created on 12.03.2020
Updated on 31.03.2020

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
    
    PANEL_WIDTH=900
    PANEL_HEIGHT=300
    
    LOG_TAB_NAME =                      'Log'
    COMMUNICATION_TAB_NAME =            'Communication'

    IDENTITY_SIZE=80
    IMAGE_SIZE=40
    
    
    SENSATION_LINES=18
    SENSATION_COLUMNS=5
    
    SENSATION_COLUMN_TYPE =             0
    SENSATION_COLUMN_DATA =             1
    SENSATION_COLUMN_MEMORY =           2
    SENSATION_COLUMN_DIRECTION =        3
    SENSATION_COLUMN_TIME =             4

    SENSATION_COLUMN_TYPE_NAME =        'Type'
    SENSATION_COLUMN_DATA_NAME =        'Data'
    SENSATION_COLUMN_MEMORY_NAME =      'Memory'
    SENSATION_COLUMN_DIRECTION_NAME =   'Direction'
    SENSATION_COLUMN_TIME_NAME =        'Time'
    
    SENSATION_COLUMN_DATA_TYPE_COLUMNS = 2
    SENSATION_COLUMN_DATA_TYPE_ITEM =    0
    SENSATION_COLUMN_DATA_TYPE_IMAGE =   1
    
    TREE_UNUSED_AREA_COLOUR =           wx.Colour( 7*255/8, 7*255/8, 7*255/8 )
    TREE_BACKGROUND_COLOUR =            wx.Colour( 255, 255, 255 )
    TREE_IMAGELIST_INITIAL_COUNT =      20
 
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
            
    # GUI LogPanel
    class LogPanel(wx.Panel):
        """Class LogPanel"""
        def __init__(self, parent, robot):
            """Create the MainFrame."""
            wx.Panel.__init__(self, parent) #called
            self.robot = robot
     
            self.SetInitialSize((Visual.PANEL_WIDTH, Visual.PANEL_HEIGHT))
            
            Visual.setEventHandler(self, Visual.ID_SENSATION, self.OnSensation)
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            # grid
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
                        data_gs = wx.GridSizer(cols=Visual.SENSATION_COLUMN_DATA_TYPE_COLUMNS, vgap=5, hgap=5)
                        data_gs.AddMany([(wx.StaticText(self, label=''), 0, wx.EXPAND),
                                         (wx.StaticBitmap(parent=self, id=-1, pos=(0, -Visual.IMAGE_SIZE/2), size=(Visual.IMAGE_SIZE,Visual.IMAGE_SIZE)), 0, wx.EXPAND)
                                         ])
#                         data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
#                         data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                       
                        self.gs.Add(data_gs, 0, wx.EXPAND)
                        #self.gs.Add(wx.StaticBitmap(parent=self, id=-1, bitmap=None, pos=(10, 5), size=(0, 0)), 0, wx.EXPAND)
                    else:
                        self.gs.Add(wx.StaticText(self), 0, wx.EXPAND)
                
                
            vbox.Add(self.gs, proportion=1, flag=wx.EXPAND)
            self.SetSizer(vbox)
            
            self.status = wx.StaticText(self, -1)   
            vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            self.Fit()
    
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
            """OnSensation."""
            #show sensation
            if event.data is not None:
                # Thread aborted (using our convention of None return)
                sensation=event.data
                self.status.SetLabel('Got Sensation Event')
                
                for i in range(Visual.SENSATION_LINES-1,0,-1):
                    for j in range(Visual.SENSATION_COLUMNS):
                        fromInd=(i*Visual.SENSATION_COLUMNS) +j
                        from_item = self.gs.GetItem(fromInd)
                        toInd = ((i+1)*Visual.SENSATION_COLUMNS) +j
                        to_item = self.gs.GetItem(toInd)
                        
                        if from_item is not None and to_item is not None:
                            if from_item.IsWindow() and to_item.IsWindow():
                               to_item.GetWindow().SetLabel(from_item.GetWindow().GetLabel())
                            elif from_item.IsSizer() and to_item.IsSizer():
                                from_data_gs = from_item.GetSizer()
                                to_data_gs = to_item.GetSizer()
                                
                                # item
                                from_item_item = from_data_gs.GetItem(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                                label = from_item_item.GetWindow().GetLabel()
                                to_item_item = to_data_gs.GetItem(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                                to_item_item.GetWindow().SetLabel(from_item_item.GetWindow().GetLabel())
                                if from_data_gs.IsShown(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM):
                                    to_data_gs.Show(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                                    print("OnSensation item fromInd " + str(fromInd) + " toInd "+ str(toInd) + " SetLabel " + label + " Show")
                                    self.Refresh()
                                else:
                                    to_data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                                    print("OnSensation item fromInd " + str(fromInd) + " toInd "+ str(toInd) + " SetLabel " + label + " Hide ")
                                    self.Refresh()
                                # image
                                from_image_item = from_data_gs.GetItem(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                                to_image_item = to_data_gs.GetItem(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)                                
                                bitmap = from_image_item.GetWindow().GetBitmap()
                                to_image_item .GetWindow().SetBitmap(bitmap)
                                if from_data_gs.IsShown(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE):
                                    to_data_gs.Show(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                                    print("OnSensation image fromInd " + str(fromInd) + " toInd "+ str(toInd) + " SetBitmap Show")
                                    self.Refresh()
                                else:
                                    to_data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                                    print("OnSensation image fromInd " + str(fromInd) + " toInd "+ str(toInd) + " SetBitmap Hide")
                                self.Refresh()
                            else:
                                print("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " error")
                        else:
                            print("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " None error")
               
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_TYPE)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(Sensation.getSensationTypeString(sensationType=sensation.getSensationType()))
                    
                item = self.gs.GetItem(Visual.SENSATION_COLUMNS + Visual.SENSATION_COLUMN_DATA)
                if item is not None and item.IsSizer():
                    data_gs = item.GetSizer()
                    image_item = data_gs.GetItem(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                    item_item = data_gs.GetItem(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                    if image_item is not None and image_item.IsWindow() and\
                       item_item is not None and item_item.IsWindow():
                        if sensation.getSensationType() == Sensation.SensationType.Image:
                            data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                            image = sensation.getImage()
                            if image is not None:
                                data_gs.Show(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                                bitmap = Visual.PILTowx(image=image, size=Visual.IMAGE_SIZE)
                                image_item.GetWindow().SetBitmap(bitmap)
                                image_item.GetWindow().SetSize((Visual.IMAGE_SIZE,Visual.IMAGE_SIZE))
                            else:
                                data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                        elif sensation.getSensationType() == Sensation.SensationType.Item:
                            data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
                            name = sensation.getName()
                            if name is not None:
                                data_gs.Show(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                                item_item.GetWindow().SetLabel(name)
                            else:
                                data_gs.Hide(Visual.SSENSATION_COLUMN_DATA_TYPE_ITEM)
                        else:
                            data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_ITEM)
                            data_gs.Hide(Visual.SENSATION_COLUMN_DATA_TYPE_IMAGE)
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
                # in raspberry data_gs rows are not updated bith SetLavels, if we don't change main windows size so
                (x,y) = self.GetSize()
                self.SetSize((x-1,y-1))
                self.Refresh()
                self.SetSize((x,y))
                self.Refresh()

            else:
                self.status.SetLabel('Sensation is None in Sensation Event')
                                

    # GUI CommunicationPanel
    class CommunicationPanel(wx.Panel):
        """Class CommunicationPanel"""
        def __init__(self, parent, robot):
            """Create the MainFrame."""
            wx.Panel.__init__(self, parent) #called
            self.robot = robot
     
            self.SetInitialSize((Visual.PANEL_WIDTH, Visual.PANEL_HEIGHT))
            # background that is not used by tree
            self.SetBackgroundColour( Visual.TREE_UNUSED_AREA_COLOUR )           
           
            Visual.setEventHandler(self, Visual.ID_SENSATION, self.OnSensation)
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            
            self.tree =  wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                           wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT) 
            # background that is used by tree
            self.tree.SetBackgroundColour( Visual.TREE_BACKGROUND_COLOUR )           
            self.root = self.tree.AddRoot('Root')
            
            self.imageList = wx.ImageList(width=Visual.IMAGE_SIZE,
                                          height=Visual.IMAGE_SIZE,
                                          initialCount=Visual.TREE_IMAGELIST_INITIAL_COUNT)
            self.tree.AssignImageList(self.imageList)
           
            vbox.Add(self.tree, 0, wx.EXPAND)
            
            self.status = wx.StaticText(self, -1)   
            vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            
            self.SetSizer(vbox)
            self.Fit()
    
        def setRobot(self, robot):
            self.robot=robot #called
        def getRobot(self):
            return self.robot #called
        
            
        def OnSensation(self, event):
            """OnSensation."""
            #show sensation
            if event.data is not None:
                # Thread aborted (using our convention of None return)
                sensation=event.data
                self.status.SetLabel('Got Sensation Event')
                
                imageInd=-1
                if sensation.getSensationType() == Sensation.SensationType.Image:
                    image = sensation.getImage()
                    if image is not None:
                        bitmap = Visual.PILTowx(image=image, size=Visual.IMAGE_SIZE)
                        imageInd = self.imageList.Add (bitmap=bitmap)
                        
                text=Sensation.getSensationTypeString(sensationType=sensation.getSensationType())
                treeItem = self.tree.InsertItem (parent=self.root,
                                                 pos=0,
                                                 text=text,
                                                 image=imageInd)
                #
                #                                 , image=-1, selImage=-1, data=None)
                print("" + text + " imageInd "+ str(imageInd))
                self.Fit()
            else:
                self.status.SetLabel('Sensation is None in Sensation Event')
                                

    # GUI Frame class that spins off the worker thread
    class MainFrame(wx.Frame):
        """Class MainFrame."""
        def __init__(self, parent, id, robot):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, robot.getWho())
            self.robot = robot
     
            self.SetInitialSize((Visual.WIDTH, Visual.HEIGHT))
            
            Visual.setEventHandler(self, Visual.ID_SENSATION, self.OnSensation)
            
            # placeholder for tabs
            panel = wx.Panel(self)
            notebook = wx.Notebook(panel)            

            vbox = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(vbox)
            #self.identity = wx.TextCtrl(self, style=wx.TE_RIGHT)
            print("MainFrame.__init__ len(Robot.images) " + str(len(Robot.images)))
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
            
            vbox.Add(panel, 1, wx.EXPAND)
             
            self.logPanel = Visual.LogPanel(parent=notebook, robot=robot)
            self.communicationPanel = Visual.CommunicationPanel(parent=notebook, robot=robot)
            
            notebook.AddPage(self.logPanel, Visual.LOG_TAB_NAME)
            notebook.AddPage(self.communicationPanel, Visual.COMMUNICATION_TAB_NAME)
            
            # Set notebook in a sizer to create the layout
            # without this tabs get 1 bit size
            sizer = wx.BoxSizer()
            sizer.Add(notebook, 1, wx.EXPAND)
            panel.SetSizer(sizer)
           
            #mainframe buttons           
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(wx.Button(self, Visual.ID_START, 'Start'), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            hbox.Add(wx.Button(self, Visual.ID_STOP, 'Stop'), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            vbox.Add(hbox, flag=wx.EXPAND)
            
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
            """OnSensation."""
            #show sensation
            if event.data is not None:
                # deliver to tabs
                sensation=event.data
                wx.PostEvent(self.logPanel, Visual.Event(eventType=Visual.ID_SENSATION, data=sensation))
                # if sensation is output then log it in communication tab
                if sensation.getDirection() == Sensation.Direction.In and\
                   sensation.getMemory() == Sensation.Memory.Sensory:
                    wx.PostEvent(self.communicationPanel, Visual.Event(eventType=Visual.ID_SENSATION, data=sensation))

                
 
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