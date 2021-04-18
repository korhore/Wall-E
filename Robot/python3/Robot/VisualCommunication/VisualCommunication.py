'''
Created on 08.04.2021
Updated on 08.04.2021

@author: reijo.korhonen@gmail.com

This class is pass through class for VisualCommunication and includes visual functionality neede.
Communication is independent class that can implement all communication functionality
This class is places between MainRobot and Communication, but Communication
can also be directly under MainRobot.

Meaning of this class is
- help to develope Communication giving clear pisture what Sensation go to Communication
  and what Sensations Communication produces
- be a prototype for user i9nterface for UI of Communication, how Communication UI
  with UI capable devices should work. This feature is in very only start point.

'''

import time as time
from threading import Thread
#from threading import Timer
from PIL import Image as PIL_Image
import wx

from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

class VisualCommunication(Robot):
    SLEEPTIME = 30.0
    SLEEPTIMERANDOM = 15.0
    
    WIDTH=1000
    HEIGHT=400
    
    PANEL_WIDTH=900
    PANEL_HEIGHT=300
    
    LOG_TAB_NAME =                      'Log'
    TREE_LOG_TAB_NAME =                 'Tree Log'
    COMMUNICATION_TAB_NAME =            'Communication'

    IDENTITY_SIZE=80
    IMAGE_SIZE=40
    
    
    # column that can be Item.name, SensationType or Image
    COLUMN_DATA_TYPE_ITEM =    0
    COLUMN_DATA_TYPE_IMAGE =   1
    
    # log panel
    LOG_PANEL_SENSATION_LINES =          16
    LOG_PANEL_SENSATION_COLUMNS =        8
    LOG_PANEL_COLUMN_DATA_TYPE_COLUMNS = 2
    
    LOG_PANEL_COLUMN_MAINNAMES =         0
    LOG_PANEL_COLUMN_TYPE =              1
    LOG_PANEL_COLUMN_DATA =              2
    LOG_PANEL_COLUMN_MEMORY =            3
    LOG_PANEL_COLUMN_DIRECTION =         4
    LOG_PANEL_COLUMN_LOCATIONS =         5
    LOG_PANEL_COLUMN_RECEIVEDFROM =      6
    LOG_PANEL_COLUMN_TIME =              7
    
    # Common panel column names
    PANEL_COLUMN_TIME_NAME =             'Time'
    PANEL_COLUMN_LOCATIONS_NAME =        'Locations'
    PANEL_COLUMN_RECEIVEDFROM_NAME =     'Received From'

    # log panel
    LOG_PANEL_COLUMN_SENSATION_MAINNAMES_NAME ='Main Names'
    LOG_PANEL_COLUMN_SENSATION_TYPE_NAME ='Sens. Type'
    LOG_PANEL_COLUMN_DATA_NAME =         'Data'
    LOG_PANEL_COLUMN_MEMORY_NAME =       'Memory'
    LOG_PANEL_COLUMN_ROBOT_TYPE_NAME =   'Robot Type'
    
    # tree log panel
    
    #communication panel
    COMMUNICATION_PANEL_SENSATION_LINES =     16
    COMMUNICATION_PANEL_SENSATION_COLUMNS =   9
    
    COMMUNICATION_COLUMN_FIRST =              0
    COMMUNICATION_COLUMN_OTHER =              1
    COMMUNICATION_COLUMN_FEELING =            2
    COMMUNICATION_COLUMN_FEELING_DIRECTION =  3
    COMMUNICATION_COLUMN_POSITIVE =           4
    COMMUNICATION_COLUMN_NEGATIVE =           5
    COMMUNICATION_COLUMN_LOCATIONS =          6
    COMMUNICATION_COLUMN_RECEIVEDFROM =       7
    COMMUNICATION_COLUMN_TIME =               8

    COMMUNICATION_COLUMN_FIRST_NAME =         'First'
    COMMUNICATION_COLUMN_OTHER_NAME =         'Other'
    COMMUNICATION_COLUMN_FEELING_NAME =       'Feeling'
    COMMUNICATION_COLUMN_FEELING_DIRECTION_NAME =  'Change'
    COMMUNICATION_COLUMN_POSITIVE_NAME =      'Positive'
    COMMUNICATION_COLUMN_NEGATIVE_NAME =      'Negative'
    
    
    TREE_UNUSED_AREA_COLOUR =           wx.Colour( 7*255/8, 7*255/8, 7*255/8 )
    TREE_BACKGROUND_COLOUR =            wx.Colour( 255, 255, 255 )
    TREE_IMAGELIST_INITIAL_COUNT =      50
    TREE_ROOT_CHILD_MAX =               5
    TREE_CHILD_CHILD_MAX =              10
    TREE_CHILD_MAX =                    50
    TREE_CHILD_LEVEL_MAX =              3
 
    # Button definitions
    # Stop
    ID_STOP = wx.ID_ANY
    # Feeling changes
    ID_POSITIVE = wx.ID_ANY
    ID_NEGATIVE = wx.ID_ANY
    
    # Sensation visualisation
    ID_SENSATION = wx.ID_ANY
        
    def __init__(self,
                 mainRobot,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0,
                 memory = None,
                 maxRss = Config.MAXRSS_DEFAULT,
                 minAvailMem = Config.MINAVAILMEM_DEFAULT,
                 location=None,
                 config=None):
        Robot.__init__(self,
                       mainRobot=mainRobot,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level,
                       memory = memory,
                       maxRss =  maxRss,
                       minAvailMem = minAvailMem,
                       location = location,
                       config = config)
        print("We are in VisualCommunication, not Robot")
        self.app = None
        
        # not yet running
        self.running=False
                            
                            
    def run(self):
        # default
        self.running=True
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run: Starting robot name " + self.getName() + " kind " + self.getKind() + " instanceType " + self.config.getInstanceType())      
        # wait until started so all others can start first        
        time.sleep(Sensation.getRandom(base = VisualCommunication.SLEEPTIME,
                                       randomMin = -VisualCommunication.SLEEPTIMERANDOM,
                                       randomMax = VisualCommunication.SLEEPTIMERANDOM))       
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        
        #self.app = VisualCommunication.MainApp(robot=self)
        #self.app.setRobot(self)
        
        self.wxWorker = VisualCommunication.wxWorker(robot=self)#, app=self.app)
        self.wxWorker.start()       # start ui on its own thread
       
       # default
        while self.running:
            # if we can't sense, the we wait until we get something into Axon
            # or if we can sense, but there is something in our Axon, process it
            if not self.getAxon().empty() or not self.canSense():
                transferDirection, sensation = self.getAxon().get(robot=self)
                self.log(logLevel=Robot.LogLevel.Normal, logStr="got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr() + ' len(sensation.getAssociations()) '+ str(len(sensation.getAssociations())))      
                self.process(transferDirection=transferDirection, sensation=sensation)
            else:
                self.sense()
 
        self.mode = Sensation.Mode.Stopping
        self.log(logLevel=Robot.LogLevel.Normal, logStr="Stopping robot")   

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            robot.stop()
            
        self.wxWorker.join()       # wait UI thread stops

       
        self.log(logLevel=Robot.LogLevel.Normal, logStr="run ALL SHUT DOWN")
        
    def process(self, transferDirection, sensation):
        # default Robot.process
        super(VisualCommunication, self).process(transferDirection, sensation)
#             # just pass Sensation to wx-process
#             # if we already got self.app and self.app.frame running
#             # otherwise we just forget this sensation and wait new ones to come and to be shown
        if self.app: 
              wx.PostEvent(self.app.frame, VisualCommunication.Event(eventType=VisualCommunication.ID_SENSATION, data=sensation))
       # and all sensations are also processed to wx 
#         self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr() + '  len(sensation.getAssociations()) '+ str(len(sensation.getAssociations()))) #called
#         if sensation.getSensationType() == Sensation.SensationType.Stop:
#             self.log(logLevel=Robot.LogLevel.Verbose, logStr='process: SensationSensationType.Stop')      
#             self.stop()
#         elif transferDirection == Sensation.TransferDirection.Up:
#             if self.getParent() is not None: # if sensation is going up  and we have a parent
#                 self.log(logLevel=Robot.LogLevel.Detailed, logStr='process: self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation))')      
#                 self.getParent().getAxon().put(robot=self, transferDirection=transferDirection, sensation=sensation)
#         else:
#             # just pass Sensation to wx-process
#             # if we already got self.app and self.app.frame running
#             # otherwise we just forget this sensation and wait new ones to come and to be shown
#             if self.app and self.app: 
#                 wx.PostEvent(self.app.frame, VisualCommunication.Event(eventType=VisualCommunication.ID_SENSATION, data=sensation))
#         # TODO should we release sensation, when we delete it from UI
#         # that way we should attach also all sensations we get from associations
#         # maybe for readonly logic this is not a problem
        sensation.detach(robot=self) # finally release played sensation

 
    '''
    stop
        When we are asked to stop
        default handling
        and stopping wz-process as it wants to be called
    '''           
    def stop(self):
        #run once
        if self.running:
            Robot.stop(self) # default handling
            # and send it to wx-process
            if self.app:
                # To stop wx we regenerate stop Sensation
                sensation=self.createSensation(associations=[], sensationType = Sensation.SensationType.Stop)
                wx.PostEvent(self.app.frame, VisualCommunication.Event(eventType=VisualCommunication.ID_SENSATION, data=sensation))
    '''
    Helpers
    '''
            
    def PILTowx (image, size, setMask=False, square=False):
        width, height = image.size
        bitmap = wx.Bitmap.FromBuffer(width, height, image.tobytes())
        if square:
            height = size
            width = size
        else:
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
       
        wxBitmap = wx.Bitmap(wxImage)
        
        bmapHasMask  = wxBitmap.GetMask()    # "GetMask()", NOT "HasMask()" !
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
        def __init__(self, robot): #app, 
            """Init wxWorker Thread Class."""
            Thread.__init__(self) #called
            self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
            #self.app = app
            self.robot = robot
            #self.app = robot.app = VisualCommunication.MainApp(robot=self)
     
        def setRobot(self, robot):
            self.robot=robot
        def getRobot(self):
            return self.robot
        
        def run(self):
            """Run wxWorker Thread."""
            # We should create all wx.variables and ui here, in this thread
            # It is de simplt
            self.app = self.robot.app = VisualCommunication.MainApp(robot=self.robot)

            self.app.MainLoop() #called
    
    class Event(wx.PyEvent):
        """Simple event to carry arbitrary result data."""
        def __init__(self, eventType, data):
            """Init Result Event."""
            wx.PyEvent.__init__(self)
            self.SetEventType(eventType)
            self.data = data
#  wx.EVT_BUTTON == PyEventBinder
# wx.EventType
#        
    # GUI LogPanel
    class LogPanel(wx.Panel):
        """Class LogPanel"""
        def __init__(self, parent, robot):
            """Create the MainFrame."""
            wx.Panel.__init__(self, parent) #called
            self.robot = robot
     
            self.SetInitialSize((VisualCommunication.PANEL_WIDTH, VisualCommunication.PANEL_HEIGHT))
            
            VisualCommunication.setEventHandler(self, VisualCommunication.ID_SENSATION, self.OnSensation)
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            # grid
            # grid = wx.grid.Grid(background, size=(WIDTH,HEIGHT), pos=(0,0))
            # grid.CreateGrid(6,6)
            # grid.HideRowLabels()
            
            self.gs = wx.GridSizer(VisualCommunication.LOG_PANEL_SENSATION_LINES+1,
                                   VisualCommunication.LOG_PANEL_SENSATION_COLUMNS,
                                   5, 5)
            headerFont = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
             
            self.gs.AddMany( [
                (wx.StaticText(self, label=VisualCommunication.LOG_PANEL_COLUMN_SENSATION_MAINNAMES_NAME), 0, wx.EXPAND),        # 0
                (wx.StaticText(self, label=VisualCommunication.LOG_PANEL_COLUMN_SENSATION_TYPE_NAME), 0, wx.EXPAND),             # 1
                (wx.StaticText(self, label=VisualCommunication.LOG_PANEL_COLUMN_DATA_NAME), 0, wx.EXPAND),                       # 2
                (wx.StaticText(self, label=VisualCommunication.LOG_PANEL_COLUMN_MEMORY_NAME), 0, wx.EXPAND),                     # 3
                (wx.StaticText(self, label=VisualCommunication.LOG_PANEL_COLUMN_ROBOT_TYPE_NAME), 0, wx.EXPAND|wx.ALIGN_CENTER), # 4
                (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_LOCATIONS_NAME), 0, wx.EXPAND),                      # 5
                (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_RECEIVEDFROM_NAME), 0, wx.EXPAND),                   # 6
                (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_TIME_NAME), 0, wx.EXPAND)])                          # 7
            for j in range(VisualCommunication.LOG_PANEL_SENSATION_COLUMNS):
                item = self.gs.GetItem(j)               
                item.GetWindow().SetFont(headerFont) 
                               
            for i in range(VisualCommunication.LOG_PANEL_SENSATION_LINES):
                for j in range(VisualCommunication.LOG_PANEL_SENSATION_COLUMNS):
                    if j is VisualCommunication.LOG_PANEL_COLUMN_DATA:
                        data_gs = wx.GridSizer(cols=VisualCommunication.LOG_PANEL_COLUMN_DATA_TYPE_COLUMNS, vgap=5, hgap=5)
                        data_gs.AddMany([(wx.StaticText(self, label=''), 0, wx.EXPAND),
                                         (wx.StaticBitmap(parent=self, id=-1, pos=(0, int(-VisualCommunication.IMAGE_SIZE/2)), size=(int(VisualCommunication.IMAGE_SIZE),int(VisualCommunication.IMAGE_SIZE))), 0, wx.EXPAND)
                                         ])
#                         data_gs.Hide(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
#                         data_gs.Hide(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)
                       
                        self.gs.Add(data_gs, 0, wx.EXPAND)
                        #self.gs.Add(wx.StaticBitmap(parent=self, id=-1, bitmap=None, pos=(10, 5), size=(0, 0)), 0, wx.EXPAND)
                    else:
                        self.gs.Add(wx.StaticText(self), 0, wx.EXPAND)
                
                
            vbox.Add(self.gs, proportion=1, flag=wx.EXPAND)
            self.SetSizer(vbox)
            
            #self.status = wx.StaticText(self, -1)   
            #vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            self.Fit()
            
        def setRobot(self, robot):
            self.robot=robot #called
        def getRobot(self):
            return self.robot #called
 
        '''
        helper method to return SensationType.Item name with presewnce, when presence is valid
        '''       
        def getItemNamePresenceString(self, sensation):
            if sensation.getRobotType() == Sensation.RobotType.Sense:
                return '{}:{}'.format(sensation.getName(),Sensation.getPresenceString(sensation.getPresence()))
            return sensation.getName()
            
                    
        def OnSensation(self, event):
            """OnSensation."""
            #show sensation
            if event.data is not None:
                # Thread aborted (using our convention of None return)
                sensation=event.data
                #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr='LogPanel.OnSensation got sensation from event.data ' + sensation.toDebugStr() + ' len(sensation.getAssociations()) '+ str(len(sensation.getAssociations()))) 
                #self.status.SetLabel('Got Sensation Event')
                
                # First delete last line
                ind = ((VisualCommunication.LOG_PANEL_SENSATION_LINES) * VisualCommunication.LOG_PANEL_SENSATION_COLUMNS)
                for j in range(VisualCommunication.LOG_PANEL_SENSATION_COLUMNS):
                    item = self.gs.GetItem(ind)
                    item.DeleteWindows()
                    isChildItemRemoved = self.gs.Remove(index=ind)
                    
                # insert new line after headers
                # Because we don't use Grid-class but GridSizer class, we add new line manually into right place cell bt cell
                # by line. Indexes of cells are calculated right if insertation in done in natural order, from left to right
                # because index increases
                
                # Main Names
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_MAINNAMES,
                               window=wx.StaticText(self, label=sensation.getMainNamesString()),  proportion=0, flag=wx.EXPAND)
                
                # type of Sensation
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_TYPE,
                               window=wx.StaticText(self, label=Sensation.getSensationTypeString(sensationType=sensation.getSensationType())),  proportion=0, flag=wx.EXPAND)
                
                # Sensation data we show either Image or Item.name, but other SEnsation types data is not visual
                if sensation.getSensationType() == Sensation.SensationType.Image:
                    image = sensation.getImage()
                    if image is not None:
                        bitmap = VisualCommunication.PILTowx(image=image, size=VisualCommunication.IMAGE_SIZE)
                        self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_DATA,
                                       window=wx.StaticBitmap(parent=self, id=-1, size=(int(VisualCommunication.IMAGE_SIZE),int(VisualCommunication.IMAGE_SIZE)), bitmap=bitmap), proportion=0, flag=wx.EXPAND | wx.LEFT)
#                                       window=wx.StaticBitmap(parent=self, id=-1, pos=(0, int(-VisualCommunication.IMAGE_SIZE/2)), size=(int(VisualCommunication.IMAGE_SIZE),int(VisualCommunication.IMAGE_SIZE)), bitmap=bitmap), proportion=0, flag=wx.EXPAND)
                    else: # add something
                        self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_DATA,
                                       window=wx.StaticText(self, label=''), proportion=0, flag=wx.EXPAND)
                elif sensation.getSensationType() == Sensation.SensationType.Item:
                    self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_DATA,
                                   window=wx.StaticText(self, label=self.getItemNamePresenceString(sensation)), proportion=0, flag=wx.EXPAND)
                else:
                    self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_DATA,
                                   window=wx.StaticText(self, label=''), proportion=0, flag=wx.EXPAND)

#                  # Main Names                  
#                 self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_MAINNAMES,
#                                window=wx.StaticText(self, label=sensation.getMainNamesString()), proportion=0, flag=wx.EXPAND)
               # Memory type                    
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_MEMORY,
                               window=wx.StaticText(self, label=Sensation.getMemoryTypeString(memoryType=sensation.getMemoryType())), proportion=0, flag=wx.EXPAND)

                # Robot type that the Sensation, Muscle/Sense /Communication                                      
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_DIRECTION,
                               window=wx.StaticText(self, label=Sensation.getRobotTypeString(robotType=sensation.getRobotType())), proportion=0, flag=wx.EXPAND)

                # Locations                    
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_LOCATIONS,
                               window=wx.StaticText(self, label=sensation.getLocationsStr()), proportion=0, flag=wx.EXPAND)

                # received from other hosts                    
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_RECEIVEDFROM,
                               window=wx.StaticText(self, label=str(sensation.getReceivedFrom())), proportion=0, flag=wx.EXPAND)

                # time
                self.gs.Insert(index=VisualCommunication.LOG_PANEL_SENSATION_COLUMNS + VisualCommunication.LOG_PANEL_COLUMN_TIME,
                               window=wx.StaticText(self, label=time.ctime(sensation.getTime())), proportion=0, flag=wx.EXPAND)

                # Without this lines are not updated right, at all
                # will be done in first line                   
                (x,y) = self.GetSize()
                self.SetSize((x-1,y-1))
                self.SetSize((x,y))

#                 # also refrersh is commented out
#                 self.Refresh()
#                 self.Update()
                
                #self.status.SetLabel('Processed Sensation Event')

#             else:
#                 self.status.SetLabel('Sensation is None in Sensation Event')
                
                                

    # GUI TreeLogPanel
    class TreeLogPanel(wx.Panel):
        """Class TreeLogPanel"""
        def __init__(self, parent, robot):
            """Create the MainFrame."""
            wx.Panel.__init__(self, parent) #called
            self.robot = robot
     
            self.SetInitialSize((VisualCommunication.PANEL_WIDTH, VisualCommunication.PANEL_HEIGHT))
            # background that is not used by tree
            self.SetBackgroundColour( VisualCommunication.TREE_UNUSED_AREA_COLOUR )           
           
            VisualCommunication.setEventHandler(self, VisualCommunication.ID_SENSATION, self.OnSensation)
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            
            self.tree =  wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                           wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT) 
            # background that is used by tree
            self.tree.SetBackgroundColour( VisualCommunication.TREE_BACKGROUND_COLOUR )           
            self.root = self.tree.AddRoot('Root')
            
            self.imageList = wx.ImageList(width=VisualCommunication.IMAGE_SIZE,
                                          height=VisualCommunication.IMAGE_SIZE,
                                          initialCount=2*VisualCommunication.TREE_CHILD_MAX)
            self.tree.AssignImageList(self.imageList)
            self.unusedImageListIdexes=[] # keep track indexes that are not used any more
                                          # for reuses
           
            vbox.Add(self.tree, 0, wx.EXPAND)
            
#             self.status = wx.StaticText(self, -1)   
#             vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            
            self.SetSizer(vbox)
            #vbox.Fit() # Try to expand
            vbox.SetMinSize (width=10*VisualCommunication.IMAGE_SIZE, height=50*VisualCommunication.IMAGE_SIZE)
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
                self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr='TreeLogPanel.OnSensation got sensation from event.data ' + sensation.toDebugStr() + '  len(sensation.getAssociations()) '+ str(len(sensation.getAssociations()))) 
                #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="OnSensation len(sensation.getAssociations()) " + str(len(sensation.getAssociations())))
#                 self.status.SetLabel('Got Sensation Event')
                self.handleSensation(parent=self.root,
                                     sensation=sensation,
                                     level=1,
                                     associatedSensations=[],
                                     childrencount=0)
                self.deleteOldItems()
                self.tree.ExpandAll()
                self.Fit()
#             else:
#                 self.status.SetLabel('Sensation is None in Sensation Event')
                
        def handleSensation(self, parent, sensation, level, associatedSensations, childrencount):
            """handleSensation."""
            #show sensation
            #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="handleSensation len(sensation.getAssociations()) " + str(len(sensation.getAssociations())) + " level " + str(level))
            if sensation not in associatedSensations:
                associatedSensations.append(sensation)
                imageInd=-1
                if sensation.getSensationType() == Sensation.SensationType.Image:
                    image = sensation.getImage()
                    if image is not None:
                        bitmap = VisualCommunication.PILTowx(image=image, size=VisualCommunication.IMAGE_SIZE, square=True)
                        imageInd = self.getImageInd(bitmap=bitmap)
                            
                text=Sensation.getSensationTypeString(sensationType=sensation.getSensationType())
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    text = text + ' ' + sensation.getName()
                text = text + ' ' + Sensation.getMemoryTypeString(memoryType=sensation.getMemoryType()) + \
                              ' ' + Sensation.getRobotTypeString(robotType=sensation.getRobotType()) +\
                              ' ' + time.ctime(sensation.getTime())
                treeItem = self.tree.InsertItem (parent=parent,
                                                 pos=0,
                                                 text=text,
                                                 image=imageInd)
                #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="" + text + " imageInd "+ str(imageInd))
                level=level+1
                if level <= VisualCommunication.TREE_CHILD_LEVEL_MAX and\
                    childrencount < VisualCommunication.TREE_CHILD_CHILD_MAX-level:
                    childrencount = self.insertChildren(
                                        parent=treeItem,
                                        sensation=sensation,
                                        level=level,
                                        associatedSensations=associatedSensations,
                                        childrencount=childrencount)
            return childrencount
                
        def getImageInd(self, bitmap):
            if len(self.unusedImageListIdexes) > 0:
                index = self.unusedImageListIdexes.pop()
                self.imageList.Replace(index, bitmap)
                return index
            else:
                return self.imageList.Add(bitmap=bitmap)
               
        def insertChildren(self,
                           parent,
                           sensation,
                           level,
                           associatedSensations,
                           childrencount):
            if level <= VisualCommunication.TREE_CHILD_LEVEL_MAX and\
                childrencount < VisualCommunication.TREE_CHILD_CHILD_MAX-level:
                #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="insertChildren len(sensation.getAssociations()) " + str(len(sensation.getAssociations())) + " level " + str(level))
                for association in sensation.getAssociations():
                    childrencount = self.handleSensation(
                                         parent=parent,
                                         sensation=association.getSensation(),
                                         level=level,
                                         associatedSensations=associatedSensations,
                                         childrencount=childrencount)
                    childrencount = childrencount+1
                    if childrencount >= VisualCommunication.TREE_CHILD_CHILD_MAX-level:
                        break
            return childrencount
                    
        def deleteOldItems(self):
            """deleteOldItems."""
            rootChildCount=self.tree.GetChildrenCount(item=self.root, recursively=False)
            childCount = self.tree.GetChildrenCount(item=self.root, recursively=True)
            while (childCount > VisualCommunication.TREE_CHILD_MAX or\
                   rootChildCount > VisualCommunication.TREE_ROOT_CHILD_MAX) and rootChildCount > 1:
                self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="deleteOldItems rootChildCount " + str(rootChildCount) + " childCount " + str(childCount))
                rootLastChild =self.tree.GetLastChild(item=self.root)
                self.removeImages(item=rootLastChild)
                self.tree.Delete(rootLastChild)
                rootChildCount = rootChildCount-1
                childCount = self.tree.GetChildrenCount(item=self.root, recursively=True)
                
        def removeImages(self, item):
            index = self.tree.GetItemImage(item)
            if index > 0:
                self.tree.SetItemImage(item, -1)
                self.unusedImageListIdexes.append(index)
            (child,cookie) = self.tree.GetFirstChild(item=item)
            while child.IsOk():
                self.removeImages(item=child)
                (child, cookie) = self.tree.GetNextChild(item=item, cookie=cookie)
                
                                
    # GUI CommunicationPanel
    class CommunicationPanel(wx.Panel):
        """Class CommunicationPanel"""
#         class FeelingButton(wx.Button):
#             def __init__ (self,
#                           parent,
#                           sensation,
#                           isPositive,
#                           id=wx.ID_ANY, label="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.ButtonNameStr):
#                 super().__init__(parent=parent,
#                                    id=id,
#                                    label=label,
#                                    pos=pos,
#                                    size=size,
#                                    style=style,
#                                    validator=validator,
#                                    name=name)
#                 self.isPositive = isPositive
#                 self.setSensation(sensation=sensation)
#                 
#             def getSensation(self):
#                 return self.sensation
#             def setSensation(self, sensation):
#                 self.sensation = sensation
#                 if sensation is not None and\
#                    sensation.getFirstAssociateSensation() is not None and\
#                    sensation.getOtherAssociateSensation() is not None:                 
#                     if self.getIsPositive():
#                         self.Bind(wx.EVT_BUTTON, lambda evt, temp=sensation: self.GetParent().OnPositive(evt, temp) )
#                         self.SetLabel(str(sensation.getPositiveFeeling()))
#                     else:
#                         self.Bind(wx.EVT_BUTTON, lambda evt, temp=sensation: self.GetParent().OnNegative(evt, temp) )
#                         self.SetLabel(str(sensation.getNegativeFeeling()))
#                     self.Show(show=True)
#                 else:
#                     self.Show(show=False)
# 
#             def getIsPositive(self):
#                 return self.isPositive
#             def setIsPositive(self, isPositive):
#                  self.isPositive = isPositive
               
        def __init__(self, parent, robot):
            """Create the MainFrame."""
            wx.Panel.__init__(self, parent) #called
            self.robot = robot
     
            self.SetInitialSize((VisualCommunication.PANEL_WIDTH, VisualCommunication.PANEL_HEIGHT))
            
            VisualCommunication.setEventHandler(self, VisualCommunication.ID_SENSATION, self.OnSensation)
            # like mainFrame with tabs
            # placeholder for tabs
            panel = wx.Panel(self)
            self.notebook = wx.Notebook(panel)            

            vbox = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(vbox)
#             hbox = wx.BoxSizer(wx.HORIZONTAL)
            # Set notebook in a sizer to create the layout
            # without this tabs get 1 bit size
            sizer = wx.BoxSizer()
            sizer.Add(self.notebook, 1, wx.EXPAND)
            panel.SetSizer(sizer)
            vbox.Add(panel, 1, wx.EXPAND)
            

            
            self.communicationByLocationPanels={}
            
#             vbox = wx.BoxSizer(wx.VERTICAL)
#             # grid
#             self.gs = wx.GridSizer(VisualCommunication.COMMUNICATION_PANEL_SENSATION_LINES+1,
#                                    VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS,
#                                    5, 5)
#             headerFont = wx.Font(18, wx.DECjyväskyläORATIVE, wx.ITALIC, wx.BOLD)
#              
#             self.gs.AddMany( [(wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_FIRST_NAME), 0, wx.EXPAND),       # 0
#                 (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_OTHER_NAME), 0, wx.EXPAND),                     # 1
#                 (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_FEELING_NAME), 0, wx.EXPAND),                   # 2
#                 (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_FEELING_DIRECTION_NAME), 0, wx.EXPAND),         # 3
#                 (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME), 0, wx.EXPAND),                  # 4
#                 (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE_NAME), 0, wx.EXPAND),                  # 5
#                 (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_LOCATIONS_NAME), 0, wx.EXPAND),                         # 6
#                 (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_RECEIVEDFROM_NAME), 0, wx.EXPAND),                      # 7
#                 (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_TIME_NAME), 0, wx.EXPAND)])                             # 8
#             for j in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS):
#                 item = self.gs.GetItem(j)               
#                 item.GetWindow().SetFont(headerFont) 
#                                
#             for i in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_LINES):
#                 for j in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS):
#                     if j == VisualCommunication.COMMUNICATION_COLUMN_FIRST or j is VisualCommunication.COMMUNICATION_COLUMN_OTHER:
#                         data_gs = wx.GridSizer(cols=VisualCommunication.LOG_PANEL_COLUMN_DATA_TYPE_COLUMNS, vgap=5, hgap=5)
#                         data_gs.AddMany([(wx.StaticText(self, label=''), 0, wx.EXPAND),
#                                          (wx.StaticBitmap(parent=self, id=-1, pos=(0, int(-VisualCommunication.IMAGE_SIZE/2)), size=(int(VisualCommunication.IMAGE_SIZE),int(VisualCommunication.IMAGE_SIZE))), 0, wx.EXPAND)
#                                          ])                       
#                         self.gs.Add(data_gs, 0, wx.EXPAND)
#                         #self.gs.Add(wx.StaticBitmap(parent=self, id=-1, bitmap=None, pos=(10, 5), size=(0, 0)), 0, wx.EXPAND)
#                     elif j == VisualCommunication.COMMUNICATION_COLUMN_POSITIVE:
#                         self.gs.Add(VisualCommunication.CommunicationPanel.FeelingButton(
#                                         sensation=None, isPositive=True,
#                                         parent=self, id=VisualCommunication.ID_POSITIVE, label=VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME), wx.EXPAND)
#                         #self.gs.Hide(i*VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + j)
#                     elif j == VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE:
#                         self.gs.Add(VisualCommunication.CommunicationPanel.FeelingButton(
#                                         sensation=None, isPositive=False,
#                                         parent=self, id=VisualCommunication.ID_POSITIVE, label=VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME), wx.EXPAND)
#                     else:
#                         self.gs.Add(wx.StaticText(self), 0, wx.EXPAND)
#                 
#                 
#             vbox.Add(self.gs, proportion=1, flag=wx.EXPAND)
#             self.SetSizer(vbox)
#             
#             self.status = wx.StaticText(self, -1)   
#             vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            # finally set communication tabs
            for location in self.getRobot().getLocations():
                communicationByLocationPanel = VisualCommunication.CommunicationByLocationPanel(parent=self.notebook, robot=self.getRobot(), location=location)
                self.notebook.AddPage(communicationByLocationPanel, location)
                self.communicationByLocationPanels[location]=communicationByLocationPanel
            
            self.Fit()
            
            #VisualCommunication.setEventHandler(self, VisualCommunication.ID_POSITIVE, self.OnFeelingChange)
   
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
                self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr='CommunicationPanel.OnSensation got sensation from event.data ' + sensation.toDebugStr() + ' len(sensation.getAssociations()) '+ str(len(sensation.getAssociations()))) 
                #self.status.SetLabel('Got Sensation Event')
                
                if sensation.getLocations() == None or\
                   len(sensation.getLocations()) == 0:
                    self.handleLocation(location='', sensation=sensation)
                else:
                    for location in sensation.getLocations():
                        self.handleLocation(location, sensation=sensation)

        def handleLocation(self, location, sensation):

            # if no subpage by location, create one            
            if location in self.communicationByLocationPanels:
#                  
#                 communicationByLocationPanel = VisualCommunication.CommunicationByLocationPanel(parent=self.notebook, robot=self.getRobot(), location=location)
#                 self.notebook.AddPage(communicationByLocationPanel, location)
# 
# #                 self.sizer.Add(communicationByLocationPanel)
# #                 self.AddPage(communicationByLocationPanel, location)
#                 self.communicationByLocationPanels[location]=communicationByLocationPanel
#                 
                self.communicationByLocationPanels[location].OnSensation(sensation=sensation)
                
#             
#                 notebook.AddPage(self.treeLogPanel, VisualCommunication.TREE_LOG_TAB_NAME)
#                 notebook.AddPage(self.communicationPanel, VisualCommunication.COMMUNICATION_TAB_NAME)
# 
#                 
#                 for i in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_LINES-1,0,-1):
#                     for j in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS):
#                         fromInd=(i*VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS) +j
#                         from_item = self.gs.GetItem(fromInd)
#                         toInd = ((i+1)*VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS) +j
#                         to_item = self.gs.GetItem(toInd)
#                         
#                         if from_item is not None and to_item is not None:
#                             if from_item.IsWindow() and to_item.IsWindow():
#                                to_item.GetWindow().SetLabel(from_item.GetWindow().GetLabel())
#                                # move feeling sensation down
#                                if j == VisualCommunication.COMMUNICATION_COLUMN_POSITIVE or j == VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE:
#                                    to_item.GetWindow().setSensation(from_item.GetWindow().getSensation())                                   
#                             elif from_item.IsSizer() and to_item.IsSizer():
#                                 from_data_gs = from_item.GetSizer()
#                                 to_data_gs = to_item.GetSizer()
#                                 
#                                 # item
#                                 from_item_item = from_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
#                                 label = from_item_item.GetWindow().GetLabel()
#                                 to_item_item = to_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
#                                 to_item_item.GetWindow().SetLabel(from_item_item.GetWindow().GetLabel())
#                                 to_item_item.GetWindow().Show(show=from_item_item.GetWindow().IsShown())
#                                 # image
#                                 from_image_item = from_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)
#                                 to_image_item = to_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)                                
#                                 bitmap = from_image_item.GetWindow().GetBitmap()
#                                 to_image_item .GetWindow().SetBitmap(bitmap)
#                                 to_image_item.GetWindow().Show(show=from_image_item.GetWindow().IsShown())
#                                     #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="OnSensation image fromInd " + str(fromInd) + " toInd "+ str(toInd) + " SetBitmap Hide")
#                                 #self.Refresh()
#                             else:
#                                 self.getRobot().log("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " error")
#                         else:
#                             self.getRobot().log("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " None error")
#                
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_FIRST)
#                 if item is not None and item.IsSizer():
#                     self.showSensation(data_gs = item.GetSizer(), sensation=sensation.getFirstAssociateSensation())
#                     
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_OTHER)
#                 if item is not None and item.IsSizer():
#                     self.showSensation(data_gs = item.GetSizer(), sensation=sensation.getOtherAssociateSensation())
# 
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_FEELING)
#                 if item is not None and item.IsWindow():
#                     label=''
#                     item.GetWindow().SetLabel('')
#                     # associated feeling between Sensations
#                     if sensation.getFirstAssociateSensation() is not None and\
#                        sensation.getOtherAssociateSensation() is not None :
#                         association=sensation.getFirstAssociateSensation().getAssociation(sensation.getOtherAssociateSensation())
#                         if association is not None:
#                             label=Sensation.getFeelingString(association.getFeeling())
#                     # global feeling
#                     elif sensation.getFirstAssociateSensation() is None and\
#                          sensation.getOtherAssociateSensation() is None:
#                         label=Sensation.getFeelingString(sensation.getFeeling())
#                     item.GetWindow().SetLabel(label)
#                     
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_FEELING_DIRECTION)
#                 if item is not None and item.IsWindow():
#                     item.GetWindow().SetLabel(self.getFeelingDirectionString(sensation = sensation))
# 
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_POSITIVE)
#                 if item is not None and item.IsWindow():
#                     item.GetWindow().setSensation(sensation=sensation)
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE)
#                 if item is not None and item.IsWindow():
#                     item.GetWindow().setSensation(sensation=sensation)
#                     
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_LOCATIONS)
#                 if item is not None and item.IsWindow():
#                     item.GetWindow().SetLabel(sensation.getLocationsStr())
#                     
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_RECEIVEDFROM)
#                 if item is not None and item.IsWindow():
#                     item.GetWindow().SetLabel(str(sensation.getReceivedFrom()))
# 
#                 item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_TIME)
#                 if item is not None and item.IsWindow():
#                     item.GetWindow().SetLabel(time.ctime(sensation.getTime()))
#                     
#                 #self.Refresh()
#                 # in raspberry data_gs rows are not updated both SetLevels, if we don't change main windows size so
#                 (x,y) = self.GetSize()
#                 self.SetSize((x-1,y-1))
#                 #self.Refresh()
#                 self.SetSize((x,y))
#                 #self.Refresh()
#                 
#                 self.status.SetLabel('Processed Sensation Event')
# 
#             else:
#                 self.status.SetLabel('Sensation is None in Sensation Event')
#                 
#         def OnPositive(self, Event, sensation):
#             self.OnFeeling(sensation=sensation, isPositive=True)
# 
#         def OnNegative(self, Event, sensation):
#             self.OnFeeling(sensation=sensation, isPositive=False)
#              
#         def OnFeeling(self, sensation, isPositive):
#             self.getRobot().log(logLevel=Robot.LogLevel.Normal, logStr='OnFeeling ' + sensation.toDebugStr())
#             feelingSensation=self.getRobot().createSensation(sensation=sensation)
#             feelingSensation.setPositiveFeeling(isPositive)
#             feelingSensation.setNegativeFeeling(not isPositive)
#             feelingSensation.setRobotType(Sensation.RobotType.Sense)
#             self.getRobot().getMemory().setMemoryType(sensation=feelingSensation, memoryType=Sensation.MemoryType.Sensory)
#             self.getRobot().getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
#                 
#                 
#         def showSensation(self, data_gs, sensation):
#             image_item = data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)
#             item_item = data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
#             if image_item is not None and image_item.IsWindow() and\
#                item_item is not None and item_item.IsWindow():
#                 if sensation is not None:
#                     if sensation.getSensationType() == Sensation.SensationType.Image:
#                         item_item.GetWindow().Show(show=False)
#                         image = sensation.getImage()
#                         if image is not None:
#                             bitmap = VisualCommunication.PILTowx(image=image, size=VisualCommunication.IMAGE_SIZE)
#                             image_item.GetWindow().SetBitmap(bitmap)
#                             image_item.GetWindow().SetSize((VisualCommunication.IMAGE_SIZE,VisualCommunication.IMAGE_SIZE))
#                             image_item.GetWindow().Show(show=True)
#                         else:
#                             image_item.GetWindow().Show(show=False)
#                     elif sensation.getSensationType() == Sensation.SensationType.Item:
#                         image_item.GetWindow().Show(show=False)
#                         name = sensation.getName()
#                         if name is not None:
#                             item_item.GetWindow().SetLabel(name)
#                             item_item.GetWindow().Show(show=True)
#                         else:
#                             item_item.GetWindow().Show(show=False)
#                     else:
#                         image_item.GetWindow().Show(show=False)
#                         item_item.GetWindow().Show(show=True)
#                         item_item.GetWindow().SetLabel(Sensation.getSensationTypeString(sensation.getSensationType()))
#                 else:
#                     image_item.GetWindow().Show(show=False)
#                     item_item.GetWindow().Show(show=False)
#             else:
#                 image_item.GetWindow().Show(show=False)
#                 item_item.GetWindow().Show(show=False)
#             #self.Refresh()
#            
#             
#                 
#         def getFeelingDirectionString(self, sensation):
#             s=""
#             
#             if sensation.getPositiveFeeling():
#                 s = VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME
#             elif sensation.getNegativeFeeling():
#                 s = VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE_NAME
#             
#             return s
        
    class CommunicationByLocationPanel(wx.Panel):
        """Class CommunicationByLocationPanel"""
        class FeelingButton(wx.Button):
            def __init__ (self,
                          parent,
                          sensation,
                          isPositive,
                          id=wx.ID_ANY, label="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.ButtonNameStr):
                super().__init__(parent=parent,
                                   id=id,
                                   label=label,
                                   pos=pos,
                                   size=size,
                                   style=style,
                                   validator=validator,
                                   name=name)
                self.isPositive = isPositive
                self.setSensation(sensation=sensation)
                
            def getSensation(self):
                return self.sensation
            def setSensation(self, sensation):
                self.sensation = sensation
                if sensation is not None and\
                   sensation.getFirstAssociateSensation() is not None and\
                   sensation.getOtherAssociateSensation() is not None:                 
                    if self.getIsPositive():
                        self.Bind(wx.EVT_BUTTON, lambda evt, temp=sensation: self.GetParent().OnPositive(evt, temp) )
                        self.SetLabel(str(sensation.getPositiveFeeling()))
                    else:
                        self.Bind(wx.EVT_BUTTON, lambda evt, temp=sensation: self.GetParent().OnNegative(evt, temp) )
                        self.SetLabel(str(sensation.getNegativeFeeling()))
                    self.Show(show=True)
                else:
                    self.Show(show=False)

            def getIsPositive(self):
                return self.isPositive
            def setIsPositive(self, isPositive):
                 self.isPositive = isPositive
               
        def __init__(self, parent, robot, location):
            """Create the MainFrame."""
            wx.Panel.__init__(self, parent) #called
            self.robot = robot
     
            self.SetInitialSize((VisualCommunication.PANEL_WIDTH, VisualCommunication.PANEL_HEIGHT))
            
            VisualCommunication.setEventHandler(self, VisualCommunication.ID_SENSATION, self.OnSensation)
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            # grid
            self.gs = wx.GridSizer(VisualCommunication.COMMUNICATION_PANEL_SENSATION_LINES+1,
                                   VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS,
                                   5, 5)
            headerFont = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
             
            self.gs.AddMany( [(wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_FIRST_NAME), 0, wx.EXPAND),       # 0
                (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_OTHER_NAME), 0, wx.EXPAND),                     # 1
                (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_FEELING_NAME), 0, wx.EXPAND),                   # 2
                (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_FEELING_DIRECTION_NAME), 0, wx.EXPAND),         # 3
                (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME), 0, wx.EXPAND),                  # 4
                (wx.StaticText(self, label=VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE_NAME), 0, wx.EXPAND),                  # 5
                (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_LOCATIONS_NAME), 0, wx.EXPAND),                         # 6
                (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_RECEIVEDFROM_NAME), 0, wx.EXPAND),                      # 7
                (wx.StaticText(self, label=VisualCommunication.PANEL_COLUMN_TIME_NAME), 0, wx.EXPAND)])                             # 8
            for j in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS):
                item = self.gs.GetItem(j)               
                item.GetWindow().SetFont(headerFont) 
                               
            for i in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_LINES):
                for j in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS):
                    if j == VisualCommunication.COMMUNICATION_COLUMN_FIRST or j is VisualCommunication.COMMUNICATION_COLUMN_OTHER:
                        data_gs = wx.GridSizer(cols=VisualCommunication.LOG_PANEL_COLUMN_DATA_TYPE_COLUMNS, vgap=5, hgap=5)
                        data_gs.AddMany([(wx.StaticText(self, label=''), 0, wx.EXPAND),
                                         (wx.StaticBitmap(parent=self, id=-1, pos=(0, int(-VisualCommunication.IMAGE_SIZE/2)), size=(int(VisualCommunication.IMAGE_SIZE),int(VisualCommunication.IMAGE_SIZE))), 0, wx.EXPAND)
                                         ])                       
                        self.gs.Add(data_gs, 0, wx.EXPAND)
                        #self.gs.Add(wx.StaticBitmap(parent=self, id=-1, bitmap=None, pos=(10, 5), size=(0, 0)), 0, wx.EXPAND)
                    elif j == VisualCommunication.COMMUNICATION_COLUMN_POSITIVE:
                        self.gs.Add(VisualCommunication.CommunicationByLocationPanel.FeelingButton(
                                        sensation=None, isPositive=True,
                                        parent=self, id=VisualCommunication.ID_POSITIVE, label=VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME), wx.EXPAND)
                        #self.gs.Hide(i*VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + j)
                    elif j == VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE:
                        self.gs.Add(VisualCommunication.CommunicationByLocationPanel.FeelingButton(
                                        sensation=None, isPositive=False,
                                        parent=self, id=VisualCommunication.ID_POSITIVE, label=VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME), wx.EXPAND)
                    else:
                        self.gs.Add(wx.StaticText(self), 0, wx.EXPAND)
                
                
            vbox.Add(self.gs, proportion=1, flag=wx.EXPAND)
            self.SetSizer(vbox)
            
#             self.status = wx.StaticText(self, -1)   
#             vbox.Add(self.status, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            self.Fit()
            
            #VisualCommunication.setEventHandler(self, VisualCommunication.ID_POSITIVE, self.OnFeelingChange)
   
        def setRobot(self, robot):
            self.robot=robot #called
        def getRobot(self):
            return self.robot #called
                    
        def OnSensation(self, sensation):
            """OnSensation."""
            #show sensation
            if sensation is not None:
                # Thread aborted (using our convention of None return)
                #sensation=event.data
                self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr='CommunicationByLocationPanel.OnSensation got sensation from event.data ' + sensation.toDebugStr() + ' len(sensation.getAssociations()) '+ str(len(sensation.getAssociations()))) 
#                 self.status.SetLabel('Got Sensation Event')
                
                for i in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_LINES-1,0,-1):
                    for j in range(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS):
                        fromInd=(i*VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS) +j
                        from_item = self.gs.GetItem(fromInd)
                        toInd = ((i+1)*VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS) +j
                        to_item = self.gs.GetItem(toInd)
                        
                        if from_item is not None and to_item is not None:
                            if from_item.IsWindow() and to_item.IsWindow():
                               to_item.GetWindow().SetLabel(from_item.GetWindow().GetLabel())
                               # move feeling sensation down
                               if j == VisualCommunication.COMMUNICATION_COLUMN_POSITIVE or j == VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE:
                                   to_item.GetWindow().setSensation(from_item.GetWindow().getSensation())                                   
                            elif from_item.IsSizer() and to_item.IsSizer():
                                from_data_gs = from_item.GetSizer()
                                to_data_gs = to_item.GetSizer()
                                
                                # item
                                from_item_item = from_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
                                label = from_item_item.GetWindow().GetLabel()
                                to_item_item = to_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
                                to_item_item.GetWindow().SetLabel(from_item_item.GetWindow().GetLabel())
                                to_item_item.GetWindow().Show(show=from_item_item.GetWindow().IsShown())
                                # image
                                from_image_item = from_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)
                                to_image_item = to_data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)                                
                                bitmap = from_image_item.GetWindow().GetBitmap()
                                to_image_item .GetWindow().SetBitmap(bitmap)
                                to_image_item.GetWindow().Show(show=from_image_item.GetWindow().IsShown())
                                    #self.getRobot().log(logLevel=Robot.LogLevel.Detailed, logStr="OnSensation image fromInd " + str(fromInd) + " toInd "+ str(toInd) + " SetBitmap Hide")
                                #self.Refresh()
                            else:
                                self.getRobot().log("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " error")
                        else:
                            self.getRobot().log("OnSensation fromInd " + str(fromInd) + " toInd "+ str(toInd) + " None error")
               
                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_FIRST)
                if item is not None and item.IsSizer():
                    self.showSensation(data_gs = item.GetSizer(), sensation=sensation.getFirstAssociateSensation())
                    
                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_OTHER)
                if item is not None and item.IsSizer():
                    self.showSensation(data_gs = item.GetSizer(), sensation=sensation.getOtherAssociateSensation())

                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_FEELING)
                if item is not None and item.IsWindow():
                    label=''
                    item.GetWindow().SetLabel('')
                    # associated feeling between Sensations
                    if sensation.getFirstAssociateSensation() is not None and\
                       sensation.getOtherAssociateSensation() is not None :
                        association=sensation.getFirstAssociateSensation().getAssociation(sensation.getOtherAssociateSensation())
                        if association is not None:
                            label=Sensation.getFeelingString(association.getFeeling())
                    # global feeling
                    elif sensation.getFirstAssociateSensation() is None and\
                         sensation.getOtherAssociateSensation() is None:
                        label=Sensation.getFeelingString(sensation.getFeeling())
                    item.GetWindow().SetLabel(label)
                    
                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_FEELING_DIRECTION)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(self.getFeelingDirectionString(sensation = sensation))

                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_POSITIVE)
                if item is not None and item.IsWindow():
                    item.GetWindow().setSensation(sensation=sensation)
                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE)
                if item is not None and item.IsWindow():
                    item.GetWindow().setSensation(sensation=sensation)
                    
                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_LOCATIONS)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(sensation.getLocationsStr())
                    
                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_RECEIVEDFROM)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(str(sensation.getReceivedFrom()))

                item = self.gs.GetItem(VisualCommunication.COMMUNICATION_PANEL_SENSATION_COLUMNS + VisualCommunication.COMMUNICATION_COLUMN_TIME)
                if item is not None and item.IsWindow():
                    item.GetWindow().SetLabel(time.ctime(sensation.getTime()))
                    
                #self.Refresh()
                # in raspberry data_gs rows are not updated both SetLevels, if we don't change main windows size so
                (x,y) = self.GetSize()
                self.SetSize((x-1,y-1))
                #self.Refresh()
                self.SetSize((x,y))
                #self.Refresh()
                
#                 self.status.SetLabel('Processed Sensation Event')

#             else:
#                 self.status.SetLabel('Sensation is None in Sensation Event')
                
        def OnPositive(self, Event, sensation):
            self.OnFeeling(sensation=sensation, isPositive=True)

        def OnNegative(self, Event, sensation):
            self.OnFeeling(sensation=sensation, isPositive=False)
             
        def OnFeeling(self, sensation, isPositive):
            self.getRobot().log(logLevel=Robot.LogLevel.Normal, logStr='OnFeeling ' + sensation.toDebugStr())
            feelingSensation=self.getRobot().createSensation(sensation=sensation)
            feelingSensation.setPositiveFeeling(isPositive)
            feelingSensation.setNegativeFeeling(not isPositive)
            feelingSensation.setRobotType(Sensation.RobotType.Sense)
            self.getRobot().getMemory().setMemoryType(sensation=feelingSensation, memoryType=Sensation.MemoryType.Sensory)
            self.getRobot().getParent().getAxon().put(robot=self.getRobot(), transferDirection=Sensation.TransferDirection.Up, sensation=feelingSensation)
                
                
        def showSensation(self, data_gs, sensation):
            image_item = data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_IMAGE)
            item_item = data_gs.GetItem(VisualCommunication.COLUMN_DATA_TYPE_ITEM)
            if image_item is not None and image_item.IsWindow() and\
               item_item is not None and item_item.IsWindow():
                if sensation is not None:
                    if sensation.getSensationType() == Sensation.SensationType.Image:
                        item_item.GetWindow().Show(show=False)
                        image = sensation.getImage()
                        if image is not None:
                            bitmap = VisualCommunication.PILTowx(image=image, size=VisualCommunication.IMAGE_SIZE)
                            image_item.GetWindow().SetBitmap(bitmap)
                            image_item.GetWindow().SetSize((VisualCommunication.IMAGE_SIZE,VisualCommunication.IMAGE_SIZE))
                            image_item.GetWindow().Show(show=True)
                        else:
                            image_item.GetWindow().Show(show=False)
                    elif sensation.getSensationType() == Sensation.SensationType.Item:
                        image_item.GetWindow().Show(show=False)
                        name = sensation.getName()
                        if name is not None:
                            item_item.GetWindow().SetLabel(name)
                            item_item.GetWindow().Show(show=True)
                        else:
                            item_item.GetWindow().Show(show=False)
                    else:
                        image_item.GetWindow().Show(show=False)
                        item_item.GetWindow().Show(show=True)
                        item_item.GetWindow().SetLabel(Sensation.getSensationTypeString(sensation.getSensationType()))
                else:
                    image_item.GetWindow().Show(show=False)
                    item_item.GetWindow().Show(show=False)
            else:
                image_item.GetWindow().Show(show=False)
                item_item.GetWindow().Show(show=False)
            #self.Refresh()
           
            
                
        def getFeelingDirectionString(self, sensation):
            s=""
            
            if sensation.getPositiveFeeling():
                s = VisualCommunication.COMMUNICATION_COLUMN_POSITIVE_NAME
            elif sensation.getNegativeFeeling():
                s = VisualCommunication.COMMUNICATION_COLUMN_NEGATIVE_NAME
            
            return s
        
    # GUI Frame class that spins off the worker thread
    class MainFrame(wx.Frame):
        """Class MainFrame."""
        def __init__(self, parent, id, robot):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, robot.getMemory().getRobot().getName())
            self.robot = robot
            self.presentItemNames=[]
     
            self.SetInitialSize((VisualCommunication.WIDTH, VisualCommunication.HEIGHT))
            
            VisualCommunication.setEventHandler(self, VisualCommunication.ID_SENSATION, self.OnSensation)
            
            # placeholder for tabs
            panel = wx.Panel(self)
            notebook = wx.Notebook(panel)            

            vbox = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(vbox)
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            
            self.identityText = wx.StaticText(self, label=self.robot.getMemory().getRobot().getName())
            self.feelingText = wx.StaticText(self, label=Sensation.getFeelingString(self.robot.getMemory().getRobot().getFeeling()))
            self.activityLevelText = wx.StaticText(self, label=Sensation.getActivityLevelString(self.robot.getMemory().getRobot().getActivityLevel()))
            
            hbox.Add(self.identityText, proportion=1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            # set font
            headerFont = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
            item = hbox.GetItem(0)               
            item.GetWindow().SetFont(headerFont) 
            
            
            if robot.getMemory().getRobot().selfImage:
                bitmap = VisualCommunication.PILTowx(image=robot.getMemory().getRobot().selfImage, size=VisualCommunication.IDENTITY_SIZE, setMask=True)
                self.identityBitMap = wx.StaticBitmap(self, -1, bitmap, (10, 5), (bitmap.GetWidth(), bitmap.GetHeight()))
                icon = wx.Icon()
                icon.CopyFromBitmap(bitmap)
                self.SetIcon(icon)                
                hbox.Add(self.identityBitMap, proportion=1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            hbox.Add(self.feelingText, proportion=1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            hbox.Add(self.activityLevelText, proportion=1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            
            vbox.Add(hbox, 0, wx.EXPAND)
            
            vbox.Add(panel, 1, wx.EXPAND)
             
            self.logPanel = VisualCommunication.LogPanel(parent=notebook, robot=robot)
            self.treeLogPanel = VisualCommunication.TreeLogPanel(parent=notebook, robot=robot)
            self.communicationPanel = VisualCommunication.CommunicationPanel(parent=notebook, robot=robot)
            
            notebook.AddPage(self.logPanel, VisualCommunication.LOG_TAB_NAME)
            notebook.AddPage(self.treeLogPanel, VisualCommunication.TREE_LOG_TAB_NAME)
            notebook.AddPage(self.communicationPanel, VisualCommunication.COMMUNICATION_TAB_NAME)
            
            # Set notebook in a sizer to create the layout
            # without this tabs get 1 bit size
            sizer = wx.BoxSizer()
            sizer.Add(notebook, 1, wx.EXPAND)
            panel.SetSizer(sizer)
           
            #mainframe presents           
            presenceHbox = wx.BoxSizer(wx.HORIZONTAL)
            self.presenceText = wx.StaticText(self, label="Empty")#label=self.robot.getMemory().itemsPresenceToStr())
            presenceHbox.Add(self.presenceText, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            vbox.Add(presenceHbox, flag=wx.EXPAND)
            
            #mainframe buttons           
            buttonHbox = wx.BoxSizer(wx.HORIZONTAL)
            buttonHbox.Add(wx.Button(self, VisualCommunication.ID_STOP, 'Stop'), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
            vbox.Add(buttonHbox, flag=wx.EXPAND)
            
            self.Fit()
                    
            self.Bind(wx.EVT_BUTTON, self.OnStop, id=VisualCommunication.ID_STOP)
    
        def setRobot(self, robot):
            self.robot=robot #called
        def getRobot(self):
            return self.robot #called
        
        def OnStop(self, event):
            """Stop Robot."""
            #Tell our Robot that we wan't to stop
            #self.getRobot().stop()
            #time.sleep(1)    # wait MainRobot stops also TCP-connected hosts
            self.Close()
            #Tell our Robot that we wan't to stop
            self.getRobot().stop()
            
        def OnSensation(self, event):
            """OnSensation."""
            #show activity
            self.activityLevelText.SetLabel(label=Sensation.getActivityLevelString(self.robot.getMemory().getRobot().getActivityLevel()))

            #show sensation
            if event.data is not None:
                # deliver to tabs
                sensation=event.data
                # log presence to user
                if sensation.getSensationType() == Sensation.SensationType.Item:
                    self.tracePresence(sensation)
                # all sensation are shown  in  log and treeview
                wx.PostEvent(self.logPanel, VisualCommunication.Event(eventType=VisualCommunication.ID_SENSATION, data=sensation))
                wx.PostEvent(self.treeLogPanel, VisualCommunication.Event(eventType=VisualCommunication.ID_SENSATION, data=sensation))
                # feeling to Communication, because all communication reactions gives some feeling sensation
                if sensation.getSensationType() == Sensation.SensationType.Feeling:
                    wx.PostEvent(self.communicationPanel, VisualCommunication.Event(eventType=VisualCommunication.ID_SENSATION, data=sensation))
                    self.feelingText.SetLabel(label = Sensation.getFeelingString(self.robot.getMemory().getRobot().getFeeling()))


        '''
        Presence
        '''
        def tracePresence(self, sensation):
            # present means pure Present, all other if handled not present
            # if present sensations must come in order
            self.presenceText.SetLabel(label='items:{} robots:{}'.format(self.robot.getMemory().itemsPresenceToStr(),self.robot.getMemory().robotsPresenceToStr()))
                
 
    class MainApp(wx.App):
        """Class Main App."""
        def __init__(self, robot, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
            self.robot=robot
            wx.App.__init__(self, redirect=redirect, filename=filename, useBestVisual=useBestVisual, clearSigInt=clearSigInt)


        def OnInit(self):
            """Init Main App."""
            self.frame = VisualCommunication.MainFrame(parent=None, id=-1, robot=self.getRobot())
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True

        def setRobot(self, robot):
            self.robot=robot
            self.frame.setRobot(robot)
        def getRobot(self):
            return self.robot
            

if __name__ == "__main__":
    visual = VisualCommunication()
    #visual.start()  