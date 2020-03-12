'''
Created on 19.07.2019
Updated on 19.07.2019

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
        
        # some demo implementation

        # not yet running
        self.running=False
        self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
                            # does not help
        
    def run(self):
        self.log("Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.nextSenseTime = None
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
        
        app = Visual.MainApp(0)
        app.setRobot(self)
        app.MainLoop()
        # We get here
        # /tmp/pip-install-au36yiyx/wxPython/ext/wxWidgets/src/unix/threadpsx.cpp(1810): assert "wxThread::IsMain()" failed in OnExit(): only main thread can be here [in thread 7f98d05bd740]
        # so thread is stopped here and no other lines are executed
        app.ExitMainLoop()
        while self.running:
            systemTime.sleep(1)
            
    def OnIdle(self):
        if not self.getAxon().empty():
            transferDirection, sensation, association = self.getAxon().get()
            self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())  
            if transferDirection == Sensation.TransferDirection.Up:
                self.log(logLevel=Robot.LogLevel.Detailed, logStr='OnIdle: self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation))')      
                self.getParent().getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
            else:
                if sensation.getSensationType() == Sensation.SensationType.Stop:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='OnIdle: SensationSensationType.Stop')      
                    self.stop()
                else:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr='OnIdle: TODO Visual processing')      
#                     
#                 # stop
#                 if sensation.getSensationType() == Sensation.SensationType.Stop:
#                 #self.alsaAudioMicrophone.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
#                 self.alsaAudioMicrophone.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                         self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                         self.running=False
#                    # Item.name.presence to microphone
# #                     elif sensation.getSensationType() == Sensation.SensationType.Item and sensation.getMemory() == Sensation.Memory.Working and\
# #                          sensation.getDirection() == Sensation.Direction.Out:
# #                         #self.alsaAudioMicrophone.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
# #                         self.alsaAudioMicrophone.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                     # Voice to playback
#                     else:
#                         #self.alsaAudioPlayback.getAxon().put(transferDirection=transferDirection, sensation=sensation, association=association)
#                         self.nextSenseTime = systemTime.time() + self.alsaAudioPlayback.getPlaybackTime(datalen=len(sensation.getData()))
#                         self.alsaAudioPlayback.process(transferDirection=transferDirection, sensation=sensation, association=association)
#                         
#                         # sleep voice playing length, so we don't sense spoken voices
#                         #systemTime.sleep(self.alsaAudioPlayback.getPlaybackTime())
#             # we have time to sense
#             else:
#                 # check, id playback is going on
#                 if self.nextSenseTime is not None and\
#                    systemTime.time() < self.nextSenseTime:
#                     systemTime.sleep(self.nextSenseTime - systemTime.time())
#                     self.nextSenseTime = None
# 
#                 self.alsaAudioMicrophone.sense()
                    
    #def EVT_RESULT(self, win, func):
    def EVT_RESULT(win, func):
        """Define Result Event."""
        win.Connect(-1, -1, Visual.EVT_RESULT_ID, func)

                     
    '''
    We can't sense as a meaning of Robot-framework
    even if we can produce feedback.
    '''
                
    def canSense(self):
        return False 
     
    class ResultEvent(wx.PyEvent):
        """Simple event to carry arbitrary result data."""
        def __init__(self, data):
            """Init Result Event."""
            wx.PyEvent.__init__(self)
            self.SetEventType(Visual.EVT_RESULT_ID)
            self.data = data

    # Thread class that executes processing
    class WorkerThread(Thread):
        """Worker Thread Class."""
        def __init__(self, notify_window, robot):
            """Init Worker Thread Class."""
            Thread.__init__(self)
            self.notify_window = notify_window
            self.robot = robot
            self.want_abort = False
            # This starts the thread running on creation, but you could
            # also make the GUI thread responsible for calling this
            self.setDaemon(1)   # Fool wxPython to think, that we are in a main thread
            self.start()
    
        def setRobot(self, robot):
            self.robot=robot
        def getRobot(self):
            return self.robot
        
        def run(self):
            """Run Worker Thread."""
            
            while self.getRobot().running:
                self.getRobot().OnIdle()
#             # This is the code executing in the new thread. Simulation of
#             # a long process (well, 10s here) as a simple loop - you will
#             # need to structure your processing so that you periodically
#             # peek at the abort variable
#             for i in range(10):
#                 systemTime.sleep(1)
#                 if self.want_abort:
#                     # Use a result of None to acknowledge the abort (of
#                     # course you can use whatever you'd like or even
#                     # a separate event type)
#                     if self.notify_window is not None:
#                         wx.PostEvent(self.notify_window, Visual.ResultEvent(None))
#                     return
#             # Here's where the result would be returned (this is an
#             # example fixed result of the number 10, but it could be
#             # any Python object)
#             wx.PostEvent(self.notify_window, Visual.ResultEvent(10))
#     
        def abort(self):
            """abort worker thread."""
            # Method for use by main thread to signal an abort
            self.want_abort = True
            
    # GUI Frame class that spins off the worker thread
    class MainFrame(wx.Frame):
        """Class MainFrame."""
        def __init__(self, parent, id):
            """Create the MainFrame."""
            wx.Frame.__init__(self, parent, id, 'Thread Test')
    
            # Dumb sample frame with two buttons
            wx.Button(self, Visual.ID_START, 'Start', pos=(0,0))
            wx.Button(self, Visual.ID_STOP, 'Stop', pos=(0,50))
            self.status = wx.StaticText(self, -1, '', pos=(0,100))
    
            self.Bind(wx.EVT_BUTTON, self.OnStart, id=Visual.ID_START)
            self.Bind(wx.EVT_BUTTON, self.OnStop, id=Visual.ID_STOP)
            self.Bind (wx.EVT_IDLE, self.OnIdle)

    
            # Set up event handler for any worker thread results
            Visual.EVT_RESULT(self,self.OnResult)
            Visual.EVT_RESULT(self,self.OnResult)
    
            # And indicate we don't have a worker thread yet
            self.worker = None
    
        def setRobot(self, robot):
            self.robot=robot
        def getRobot(self):
            return self.robot
        
        def OnStart(self, event):
            """Start Computation."""
            # Trigger the worker thread unless it's already busy
            if not self.worker:
                self.status.SetLabel('Starting computation')
                self.worker = Visual.WorkerThread(notify_window=self, robot=self.getRobot())
    
        def OnStop(self, event):
            """Stop Computation."""
            # Flag the worker thread to stop if running
            if self.worker:
                self.status.SetLabel('Trying to abort computation')
                self.worker.abort()
            #Tell also our Robot that we wan't to stop
            self.getRobot().running=False
            self.Close()
#            wx.WakeUpMainThread() # to get the main thread to process events.
    
        def OnResult(self, event):
            """Show Result status."""
            if event.data is None:
                # Thread aborted (using our convention of None return)
                self.status.SetLabel('Computation aborted')
            else:
                # Process results here
                self.status.SetLabel('Computation Result: %s' % event.data)
            # In either event, the worker is done
            self.worker = None
            
        def OnIdle(self, event):
            """ on Idle do Robot processing """
            self.getRobot().OnIdle()
    
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