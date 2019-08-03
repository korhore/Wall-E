'''
Created on Feb 24, 2013
Updated on 29.06.2019
@author: reijo.korhonen@gmail.com

This class Main robot
that start and manages all subrobots

    Controls Robot-robot. Robot has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Robot emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.


'''

import os
import time
import sys
import signal
import getopt
import daemon
import lockfile

from threading import Thread
from threading import Timer

import socket



from Robot import Robot
from Config import Config, Capabilities
from Sensation import Sensation

HOST = ''
PORT = 2000
ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM

DAEMON=False
START=False
STOP=False
MANUAL=False


class MainRobot(Robot):
    """
    Controls Robot-robot. Robot has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Robot emulates sensorys (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (technically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Sensations from integrated sensorys are transferred By axons ad in real organs, implemented as Queue, which is thread safe.
    Every sensory runs in its own thread as real sensorys, independently.
    External Sensorys are handled using sockets.
    """
 
    SOCKET_ERROR_WAIT_TIME  =   60.0
    HOST_RECONNECT_MAX_TRIES =  10
    IS_SOCKET_ERROR_TEST =      False
    SOCKET_ERROR_TEST_RATE =    10
    SOCKET_ERROR_TEST_NUMBER =  0
    
    sharedSensationHosts = []                # hosts with we have already shared our sensations

    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.Real,
                 level=0):
        print("We are in MainRobot, not Robot")
        cwd = os.getcwd()
        print("cwd " + cwd)

 
        Robot.__init__(self,
                       parent = None,                            # Main robot can't have parent
                       instanceName=Config.MAIN_INSTANCE,        # instance name is main robot
                       instanceType=Sensation.InstanceType.Real, # Instancetype is real
                       level=level)
        print("We are in MainRobot, not Robot")
        
        # in main robot, set up Long_tem Memory and set up TCPServer
        if self.level == 1:
            Sensation.loadLongTermMemory()
            Sensation.CleanDataDirectory()
            self.tcpServer=TCPServer(parent=self,
                                     hostNames=self.config.getHostNames(),
                                     instanceName='TCPServer',
                                     instanceType=Sensation.InstanceType.Remote,
                                     level=self.level,
                                     address=(HOST,PORT))


    def run(self):
        self.running=True
        self.log("run: Starting Main Robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + self.config.getInstanceType())      
        
        # starting other threads/senders/capabilities
        for robot in self.subInstances:
            if robot.getInstanceType() != Sensation.InstanceType.Remote:
                robot.start()

        # main robot starts tcpServer first so clients gets association
        if self.level == 1:
            self.tcpServer.start()
           
        # study own identity
        # starting point of robot is always to study what it knows himself
        self.studyOwnIdentity()

        # live until stopped
        self.mode = Sensation.Mode.Normal
        while self.running:
            transferDirection, sensation = self.getAxon().get()
            self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())
            # We are main Robot, so sensation hoes always down to be processed    
            self.process(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)
            # as a test, echo everything to external device
            #self.out_axon.put(sensation)
 
        self.mode = Sensation.Mode.Stopping
        self.log("Stopping MainRobot")      

         # stop virtual instances here, when main instance is not running any more
        for robot in self.subInstances:
            self.log("MainRobot Stopping " + robot.getWho())      
            robot.stop()
            
        # main robot starts tcpServer first so clients gets association
        if self.level == 1:
            self.log("MainRobot Stopping self.tcpServer " + self.tcpServer.getWho())      
            self.tcpServer.stop()
            # finally save memories
            Sensation.saveLongTermMemory()

        self.log("run ALL SHUT DOWN")      
        
        
    def studyOwnIdentity(self):
        self.mode = Sensation.Mode.StudyOwnIdentity
        self.log("My name is " + self.getWho())      
        self.kind = self.config.getKind()
        self.log("My kind is " + str(self.kind))      
        self.identitypath = self.config.getIdentityDirPath(self.kind)
        self.log('My identitypath is ' + self.identitypath)      
        for dirName, subdirList, fileList in os.walk(self.identitypath):
            self.log('Found directory: %s' % dirName)      
            for fname in fileList:
                self.log('\t%s' % fname)      

    '''    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    TODO above implementation is mostly for Hearing Sensory and
    Moving Sensory and should be move to those implementations.
    
    '''
            
# all process logic in Robot.py
            
        
'''
TCPserver is a Robot that gets associations from other Robots behind network
and delivers them to main Robot. This is done as sensation, because main
robot is a robot that reads sensations.
'''
        
class TCPServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    request_queue_size = 5
    #allow_reuse_address = False

    def __init__(self,
                 address,
                 hostNames,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0):

        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in TCPServer, not Robot")
        self.address=address
        self.setWho('TCPServer: ' + str(address))
        # convert hostnames to IP addresses so same thing has always same name
        self.hostNames = []
        for hostname in hostNames:
            self.hostNames.append(socket.gethostbyname(hostname))

        self.log('__init__: creating socket' )
        self.sock = socket.socket(family=ADDRESS_FAMILY,
                                  type=SOCKET_TYPE)
        self.sock.setblocking(True)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketServers = []
        self.socketClients = []
        self.running=False
       
    def run(self):
        self.log('run: Starting')
               
        self.running=True
        self.mode = Sensation.Mode.Normal
          
        try:
            self.log('run: bind '+ str(self.address))
            self.sock.bind(self.address)
            self.server_address = self.sock.getsockname()
            self.sock.listen(self.request_queue_size)
            
            self.log("TCPServer for hostName in self.hostNames")
            for hostName in self.hostNames:
                connected = False
                tries=0
                while not connected and tries < MainRobot.HOST_RECONNECT_MAX_TRIES:
                    self.log('run: TCPServer.connectToHost ' + str(hostName))
                    connected = self.connectToHost(hostName)

                    if not connected:
                        self.log('run: TCPServer.connectToHost did not succeed ' + str(hostName) + ' time.sleep(MainRobot.SOCKET_ERROR_WAIT_TIME)')
                        time.sleep(MainRobot.SOCKET_ERROR_WAIT_TIME)
                        tries=tries+1
                if connected:
                    self.log('run: self.tcpServer.connectToHost SUCCEEDED to ' + str(hostName))
                else:
                    self.log('run: self.tcpServer.connectToHost did not succeed FINAL, no more tries to ' + str(shostName))
        except Exception as e:
                self.log("run: sock.bind, listen exception " + str(e))
                self.running = False
        
 
        while self.running:
            self.log('run: waiting self.sock.accept()')
            sock, address = self.sock.accept()
            self.log('run: self.sock.accept() '+ str(address))
            if self.running:
                self.log('run: socketServer = self.createSocketServer'+ str(address))
                socketServer = self.createSocketServer(sock=sock, address=address)
                self.log('run: socketClient = self.createSocketClient'+ str(address))
                socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer, tcpServer=self)
                self.log('run: socketServer.setSocketClient(socketClient)'+ str(address))
                socketServer.setSocketClient(socketClient)
                #self.parent.subInstances.append(socketServer)
                self.parent.subInstances.append(socketClient) # Note to parent subInstances
    
    
                if self.running:
                    self.log('run: socketServer.start()')
                    socketServer.start()
                    time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
                if self.running:
                    self.log('run: socketClient.start()')
                    socketClient.start()
                    time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
        self.log('run: STOPPED')
        
    '''
    Connect to host by creating SocketClient and SocketServer
    '''
        
    def connectToHost(self, hostName):
        self.log("connectToHost hostName " + hostName)
        address=(hostName, PORT)
        sock = socket.socket(family=ADDRESS_FAMILY,
                             type=SOCKET_TYPE)
                
        connected=False
        try:
            self.log('connectToHost: sock.connect('  + str(address) + ')')
            sock.connect(address)
            connected=True
            self.log('connectToHost: done sock.connect('  + str(address) + ')')
        except Exception as e:
            self.log("connectToHost: sock.connect(" + str(address) + ') exception ' + str(e))
            connected = False
    
        if connected:
            socketServer = self.createSocketServer(sock=sock, address=address)
            socketClient = self.createSocketClient(sock=sock, address=address, socketServer=socketServer, tcpServer=self)
            socketServer.setSocketClient(socketClient)
            # add only socketClients to subInstances, because they give us capabilities
            # but we give capabilities to others with socketServer
            #self.parent.subInstances.append(socketServer)
            self.parent.subInstances.append(socketClient)  # Note to parent subInstances
            socketServer.start()
            time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
            socketClient.start()
            time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything
        return connected
        

    def stop(self):
        self.log('stop')
        self.running = False
        self.mode = Sensation.Mode.Stopping
        for socketServer in self.socketServers:
            if socketServer.running:
                self.log('stop: socketServer.stop()')
                socketServer.stop()
        for socketClient in self.socketClients:
            if socketClient.running:
                self.log('stop: socketClient.stop()')
                socketClient.stop()
        # Connect to ourselves as a fake client
        # so server gets association and closes it
        self.log('stop: s.connect(self.address)')
        # Connect to ourselves as a fake client.
        address=('localhost', PORT)
        sock = socket.socket(family=ADDRESS_FAMILY,
                             type=SOCKET_TYPE)
        try:
            self.log('run: sock.connect('  + str(address) + ')')
            sock.connect(address)
            self.log('run: done sock.connect('  + str(address) + ')')
        except Exception as e:
            self.log("run: sock.connect(" + str(address) + ') exception ' + str(e))
 
                   
    def createSocketServer(self, sock, address, socketClient=None):
        self.log('createSocketServer: creating new SocketServer')
        socketServer = SocketServer(parent=self,
                                    instanceName='SocketServer',
                                    instanceType=Sensation.InstanceType.Remote,
                                    level=self.level,
                                    address=address,
                                    sock=sock,
                                    socketClient=socketClient)
        self.socketServers.append(socketServer)
        self.log('createSocketServer: return socketServer')
        return socketServer

    def createSocketClient(self, sock, address, tcpServer, socketServer=None):
        self.log('createSocketClient: creating new SocketClient')
        socketClient = SocketClient(parent=self.parent,
                                    instanceName='SocketClient',
                                    instanceType=Sensation.InstanceType.Remote,
                                    level=self.level,
                                    address=address,
                                    sock=sock,
                                    socketServer=socketServer,
                                    tcpServer=tcpServer)
        self.socketClients.append(socketClient)
        return socketClient

class SocketClient(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 tcpServer,
                 address = None,
                 remoteHost=None,
                 sock = None,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0,
                 socketServer=None):
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)

        print("We are in SocketClient, not Robot")
        self.tcpServer = tcpServer
        self.sock = sock
        self.address = address
        self.remoteHost=remoteHost
        self.socketServer = socketServer
        if self.sock is None or self.address is None:       
            self.address=(self.remoteHost, PORT)
        self.setWho('SocketClient: '+str(address))
        self.running=False
        self.log("__init__ done")
        
    def getHost(self):
        return self.address[0]

    def setSocketServer(self, socketServer):
        self.socketServer = socketServer
    def getSocketServer(self):
        return self.socketServer

    def run(self):
        self.running=True
        self.mode = Sensation.Mode.Normal
        self.log("run: Starting")
                 
        try:
            # tell who we are, speaking
            sensation=Sensation(associations=[], direction=Sensation.Direction.In, sensationType = Sensation.SensationType.Who, who=self.getWho())
            self.log('run: sendSensation(sensation=Sensation(sensationType = Sensation.SensationType.Who), sock=self.sock,'  + str(self.address) + ')')
            self.running =  self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
            self.log('run: done sendSensation(sensation=Sensation(sensationType = Sensation.SensationType.Who), sock=self.sock,'  + str(self.address) + ')')
            if self.running:
                 # tell our local capabilities
                 # it is important to deliver only local capabilities to the remote,
                 # because other way we would deliver back remote's own capabilities we don't have and
                 # remote would and we to do something that it only can do and
                 # we would route sensation back to remote, which routes it back to us
                 # in infinite loop
                capabilities=self.getLocalMasterCapabilities()
                self.log('run: self.getLocalMasterCapabilities() '  + capabilities.toString())
                self.log('run: self.getLocalMasterCapabilities() ' +capabilities.toDebugString())

                sensation=Sensation(associations=[], direction=Sensation.Direction.In, sensationType = Sensation.SensationType.Capability, capabilities=capabilities)
                self.log('run: sendSensation(sensationType = Sensation.SensationType.Capability, capabilities=self.getLocalCapabilities()), sock=self.sock,'  + str(self.address) + ')')
                self.running = self.sendSensation(sensation=sensation, sock=self.sock, address=self.address)
                self.log('run: sendSensation Sensation.SensationType.Capability done ' + str(self.address) +  ' '  + sensation.getCapabilities().toDebugString('SocketClient'))
        except Exception as e:
            self.log("run: SocketClient.sendSensation exception " + str(e))
            self.running = False

        # finally normal run from Robot-class
        if self.running:
            super(SocketClient, self).run()

        
        # starting other threads/senders/capabilities

        
    def process(self, transferDirection, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        # We can handle only sensation going down transfer-direction
        if transferDirection == Sensation.TransferDirection.Down:
            self.running = self.sendSensation(sensation, self.sock, self.address)
            # if we have got broken pipe -error, meaning that socket writing does not work any more
            # then try to get new association, meaning that ask TCPServer to give us a new open socket
            if not self.running and self.mode == Sensation.Mode.Interrupted:
                self.log('process: interrupted')
                connected = False
                tries=0
                while not connected and tries < MainRobot.HOST_RECONNECT_MAX_TRIES:
                    self.log('process: interrupted self.tcpServer.connectToHost ' + str(self.getHost()))
                    connected = self.tcpServer.connectToHost(self.getHost())
                    if not connected:
                        self.log('process: interrupted self.tcpServer.connectToHost did not succeed ' + str(self.getHost()) + ' time.sleep(MainRobot.SOCKET_ERROR_WAIT_TIME)')
                        time.sleep(MainRobot.SOCKET_ERROR_WAIT_TIME)
                        tries=tries+1
                if connected:
                    self.log('process: interrupted self.tcpServer.connectToHost SUCCEEDED to ' + str(self.getHost()))
                else:
                    self.log('process: interrupted self.tcpServer.connectToHost did not succeed FINAL, no more tries to ' + str(self.getHost()))
                # we are stopped anyway, if we are lucky we have new SocketServer and SocketClient now to our host
                # don't touch anything, if we are reused


    '''
    Overwrite local method. This way we can use remote Robot
    same way than local ones.
    
    our server has got capabilities from remote host
    our own capabilities are meaningless
    '''
    def getCapabilities(self):
        if self.getSocketServer() is not None:
            #self.log('getCapabilities: self.getSocketServer().getCapabilities() ' + self.getSocketServer().getCapabilities().toDebugString('SocketClient Capabilities'))
            return self.getSocketServer().getCapabilities()
        return None

    '''
    Create local method with different name
    We use this to send capabilities to remote
        '''
    def getLocalCapabilities(self):
        return self.capabilities

    '''
    share out knowledge of sensation memory out client has capabilities
       
    This is happening when SocketServer is calling it and we don't know if
    SocketClient is running so best way can be just put all sensations into our Axon
    '''
    def shareSensations(self, capabilities):
        if self.getHost() not in MainRobot.sharedSensationHosts:
            for sensation in Sensation.getSensations(capabilities):
                 self.getAxon().put(transferDirection=Sensation.TransferDirection.Down, sensation=sensation)

            MainRobot.sharedSensationHosts.append(self.getHost())

    '''
    method for sending a sensation
    '''
        
    def sendSensation(self, sensation, sock, address):
        #self.log('SocketClient.sendSensation')
        ok = True
        
        if sensation.isReceivedFrom(self.getHost()) or \
           sensation.isReceivedFrom(self.getSocketServer().getHost()):
            pass
            #self.log('socketClient.sendSensation asked to send sensation back to sensation original host. We Don\'t recycle it!')
        else:
            bytes = sensation.bytes()
            length =len(bytes)
            length_bytes = length.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
    
            try:
                l = sock.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
                if Sensation.SEPARATOR_SIZE == l:
                    pass
                    #self.log('SocketClient.sendSensation wrote separator to ' + str(address))
                else:
                    self.log("SocketClient.sendSensation length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
                    ok = False
            except Exception as err:
                self.log("SocketClient.sendSensationt error writing Sensation.SEPARATOR to " + str(address)  + " error " + str(err))
                ok=False
                self.mode = Sensation.Mode.Interrupted
            ## if we test, then we cause error time by time by us
            if MainRobot.IS_SOCKET_ERROR_TEST and self.mode == Sensation.Mode.Normal and\
               self.getSocketServer().mode == Sensation.Mode.Normal:
                MainRobot.SOCKET_ERROR_TEST_NUMBER = MainRobot.SOCKET_ERROR_TEST_NUMBER+1
                self.log("SocketClient.sendSensation MainRobot.IS_SOCKET_ERROR_TEST MainRobot.SOCKET_ERROR_TEST_NUMBER % MainRobot.SOCKET_ERROR_TEST_RATE: " + str(MainRobot.SOCKET_ERROR_TEST_NUMBER % MainRobot.SOCKET_ERROR_TEST_RATE))
                if MainRobot.SOCKET_ERROR_TEST_NUMBER % MainRobot.SOCKET_ERROR_TEST_RATE == 0:
                    self.log("SocketClient.sendSensation MainRobot.IS_SOCKET_ERROR_TEST sock.close()")
                    sock.close()
            if ok:
                try:
                    l = sock.send(length_bytes)                            # message length section
                    #self.log("SocketClient wrote length " + str(length) + " of Sensation to " + str(address))
                except Exception as err:
                    self.log("SocketClient.sendSensation error writing length of Sensation to " + str(address) + " error " + str(err))
                    ok = False
                    self.mode = Sensation.Mode.Interrupted
                    self.log("SocketClient.sendSensation self.mode = Sensation.Mode.Interrupted " + str(address))
                if ok:
                    try:
                        sock.sendall(bytes)                              # message data section
                        #self.log("SocketClient wrote Sensation to " + str(address))
                        self.log("SocketClient.sendSensationt wrote sensation " + sensation.toDebugStr() + " to " + str(address))
                        # try to send same sensation only once
                        # TODO maybe not a good idea, id sensation is changed by us
                        sensation.addReceived(self.getHost())
                        sensation.addReceived(self.getSocketServer().getHost())
                    except Exception as err:
                        self.log("SocketClient.sendSensationt error writing Sensation to " + str(address) + " error " + str(err))
                        ok = False
                        self.mode = Sensation.Mode.Interrupted
#             if not ok:
#                 # TODO This logic does not work, because sock is bad file descriptor at this point
#                 self.log("send SocketClient error, try to reconnect after sleep ")
#                 time.sleep(MainRobot.SOCKET_ERROR_WAIT_TIME)
#                 self.log("send: sock.connect(" + str(address) +")")
#                 try:
#                     sock.connect(address)
#                     self.log("send: sock.connect(" + str(address) +") succeeded")
#                     ok = True
#                 except Exception as err:
#                     self.log("SocketClient sock.connect(" + str(address) + ") error " + str(err))
#                     ok = False 
        return ok

    '''
    Method for stopping remote host
    and after that us
    '''
    def stop(self):
        # We should first stop or SocketServer because it is not in Robots subinstaves list
        self.log("stop")
        self.running = False
        self.mode = Sensation.Mode.Stopping
        
        # socketserver can't close itself, just put it to closing mode
        self.getSocketServer().stop() # socketserver can't close itself, we must send a stop sensation to it
        # we must send a stop sensation to it
        self.sendSensation(sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop), sock=self.getSocketServer().getSocket(), address=self.getSocketServer().getAddress())
        # stop remote with same technic
        self.sendSensation(sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop), sock=self.sock, address=self.address)
        self.sock.close()
         
        super(SocketClient, self).stop()

    '''
    Global method for stopping remote host
    '''
    def sendStop(sock, address):
        print("SocketClient.sendStop(sock, address)") 
        sensation=Sensation(associations=[], sensationType = Sensation.SensationType.Stop)

        bytes = sensation.bytes()
        length =len(bytes)
        length_bytes = length.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)
    
        ok = True
        try:
            l = sock.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
            if Sensation.SEPARATOR_SIZE == l:
                print('SocketClient.sendStop wrote separator to ' + str(address))
            else:
                print("SocketClient.sendStop length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
                ok = False
        except Exception as err:
            print("SocketClient.sendStop error writing Sensation.SEPARATOR to " + str(address)  + " error " + str(err))
            ok=False
            self.mode = Sensation.Mode.Interrupted
        if ok:
            try:
                l = sock.send(length_bytes)                            # message length section
                print("SocketClient.sendStop wrote length " + str(length) + " of Sensation to " + str(address))
            except Exception as err:
                self.log("SocketClient.sendStop error writing length of Sensation to " + str(address) + " error " + str(err))
                ok = False
            if ok:
                try:
                    l = sock.send(bytes)                              # message data section
                    print("SocketClient.sendStop wrote Sensation to " + str(address))
                    if length != l:
                        print("SocketClient.sendStop length " + str(l) + " != " + str(length) + " error writing to " + str(address))
                        ok = False
                except Exception as err:
                    print("SocketClient.sendStop error writing Sensation to " + str(address) + " error " + str(err))
                    ok = False
                    self.mode = Sensation.Mode.Interrupted
        return ok
        

class SocketServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 sock, 
                 address,
                 parent=None,
                 instanceName=None,
                 instanceType=Sensation.InstanceType.Remote,
                 level=0,
                 socketClient = None):

        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        
        print("We are in SocketServer, not Robot")
        self.sock=sock
        self.address=address
        self.socketClient = socketClient
        self.setWho('SocketServer: ' + str(address))
    
    def getSocket(self):
        return self.sock
    def getAddress(self):
        return self.address
       
    def getHost(self):
        return self.address[0]
       
    def setSocketClient(self, socketClient):
        self.socketClient = socketClient
    def getSocketClient(self):
        return self.socketClient
    
    def run(self):
        self.running=True
        self.mode = Sensation.Mode.Normal
        self.log("run: Starting")
        
        # starting other threads/senders/capabilities
        
        # if we don't know our capabilities, we should ask them
        # Wed can't talk to out  host direction, but client can,
        # so we ask it to do the job
#         if self.getCapabilities() is None and self.socketClient is not None:
#             self.socketClient.askCapabilities()
 
        while self.running:
            self.log("run: waiting next Sensation from" + str(self.address))
            synced = False
            ok = True
            while not synced and self.running:
                try:
                    self.data = self.sock.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
                    if len(self.data) == len(Sensation.SEPARATOR) and self.data[0] is Sensation.SEPARATOR[0]:
                        synced = True
                        ok = True
                except Exception as err:
                    self.log("self.sock.recv SEPARATOR " + str(self.address) + " error " + str(err))
                    self.running = False
                    ok = False
                    self.mode = Sensation.Mode.Interrupted   
            if synced and self.running:
                # message length section
                self.log("run: waiting size of next Sensation from " + str(self.address))
                # we can get number of sensation in many pieces
                sensation_length_length = Sensation.NUMBER_SIZE
                self.data = None
                while sensation_length_length > 0 and self.running and ok:
                    try:
                        data = self.sock.recv(sensation_length_length)                       # message data section
                        if len(data) == 0:
                            self.running = False
                            ok = False
                        else:
                            if self.data is None:
                                self.data = data
                            else:
                                self.data = self.data+data
                        sensation_length_length = sensation_length_length - len(data)
                    except Exception as err:
                        self.log("run: self.sock.recv(sensation_length_length) Interrupted error " + str(self.address) + " " + str(err))
                        self.running = False
                        ok = False
                        self.mode = Sensation.Mode.Interrupted
                if ok:
                    length_ok = True
                    try:
                        sensation_length = int.from_bytes(self.data, Sensation.BYTEORDER)
                    except Exception as err:
                        self.log("run: SocketServer Client protocol error, no valid length resyncing " + str(self.address) + " wrote " + self.data)
                        length_ok = False
                        synced = False
                                
                    if length_ok:
                        self.log("run: SocketServer Client " + str(self.address) + " wrote " + str(sensation_length))
                        self.data=None
                        while self.running and ok and sensation_length > 0:
                            try:
                                data = self.sock.recv(sensation_length)                       # message data section
                                if len(data) == 0:
                                    self.running = False
                                    ok = False
                                else:
                                    if self.data is None:
                                        self.data = data
                                    else:
                                        self.data = self.data+data
                                sensation_length = sensation_length - len(data)
                            except Exception as err:
                                self.log("run: self.sock.recv(sensation_length) Interrupted error " + str(self.address) + " " + str(err))
                                self.running = False
                                ok = False
                                self.mode = Sensation.Mode.Interrupted
                        if self.running and ok:
                            sensation=Sensation(associations=[], bytes=self.data)
                            sensation.addReceived(self.getHost())  # remember route
                            if sensation.getSensationType() == Sensation.SensationType.Capability:
                                self.log("run: SocketServer got Capability sensation " + sensation.getCapabilities().toDebugString('SocketServer'))
                                self.process(transferDirection=Sensation.TransferDirection.Up, sensation=sensation)
                                # share here sensations from our memory that this host has capabilities
                                # We wan't always share our all knowledge with all other robots
                                if self.getSocketClient() is not None:
                                    self.getSocketClient().shareSensations(self.getCapabilities())
                            else:
                                self.log("run: SocketServer got sensation " + sensation.toDebugStr())
                                self.getParent().getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=sensation) # write sensation to TCPServers Parent, because TCPServer does not read its Axon

        try:
            self.sock.close()
        except Exception as err:
            self.log("self.sock.close() " + str(self.address) + " error " + str(err))

    def stop(self):
        self.log("stop")
#         self.getSocketClient().sendStop(sock = self.sock, address=self.address)
        self.running = False
        self.mode = Sensation.Mode.Stopping
        



def threaded_server(arg):
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print ("threaded_server: starting server")
    arg.serve_forever()
    print ("threaded_server: arg.serve_forever() ended")

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print ("do_server: create MainRobot")
    global mainRobot
    mainRobot = MainRobot()

    succeeded=True
    try:
        mainRobot.start()
#         for virtailInstace in mainRobot.GetVirtailInstaces():
#             virtailInstace.start()
        
    except Exception: 
        print ("do_server: sock error, " + str(e) + " exiting")
        succeeded=False

    if succeeded:
        print ('do_server: Press Ctrl+C to Stop')

        MainRobot.mainRobot = mainRobot   # remember mainRobot so
                              # we can stop it in signal_handler   
        mainRobot.join()
        
    print ("do_server exit")
    
def signal_handler(signal, frame):
    print ('signal_handler: You pressed Ctrl+C!')
    
    mainRobot.doStop()
    print ('signal_handler: ended!')
#     exit()
    
#     print ('signal_handler: Shutting down sensation server ...')
#     RobotRequestHandler.server.serving =False
#     print ('signal_handler: sensation server is down OK')
#     
#     print ('signal_handler: Shutting down picture server...')
#     RobotRequestHandler.pictureServer.serving =False
#     print ('signal_handler: picture server is down OK')



    
def start(is_daemon):
        if is_daemon:
            print ("start: daemon.__file__ " +  daemon.__file__)
            stdout=open('/tmp/Robot_Server.stdout', 'w+')
            stderr=open('/tmp/Robot_Server.stderr', 'w+')
            #remove('/var/run/Robot_Server.pid.lock')
            pidfile=lockfile.FileLock('/var/run/Robot.pid')
            cwd = os.getcwd()   #work at that directory we are when calling this
                                # We have data and config directories there
                                # so it is important where we are

            with daemon.DaemonContext(working_directory=cwd,
                                      stdout=stdout,
                                      stderr=stderr,
                                      pidfile=pidfile):
                do_server()
        else:
            do_server()
            print ("start: stopped")

    
def stop():
    
    print ("stop: socket.socket(sock.AF_INET, socket.SOCK_STREAM)")
    # Create a socket (SOCK_STREAM means a TCP socket)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            print ('stop: sock.connect((localhost, PORT))')
            address=('localhost', PORT)
            sock.connect(address)
            print ("stop: connected")
            print ("stop: SocketClient.stop(sock = sock, address=address)")
            ok = SocketClient.sendStop(sock = sock, address=address)
        except Exception as err: 
            print ("stop: sock connect, cannot stop localhost, error " + str(err))
            return
    except Exception as err: 
        print ("stop: socket error, cannot stop localhost , error " + str(err))
        return

    finally:
        print ('stop: sock.close()')
        sock.close()
    print ("stop: end")

 


if __name__ == "__main__":
    #RobotRequestHandler.romeo = None    # no romeo device association yet
    cwd = os.getcwd()
    print("cwd " + cwd)


    print ('Number of arguments:', len(sys.argv), 'arguments.')
    print ('Argument List:', str(sys.argv))
    try:
        opts, args = getopt.getopt(sys.argv[1:],"",["start","stop","restart","daemon","manual"])
    except getopt.GetoptError:
      print (sys.argv[0] + '[--start] [--stop] [--restart] [--daemon] [--manual]')
      sys.exit(2)
    print ('opts '+ str(opts))
    for opt, arg in opts:
        print ('opt '+ opt)
        if opt == '--start':
            print (sys.argv[0] + ' start')
            START=True
        elif opt == '--stop':
            print (sys.argv[0] + ' stop')
            STOP=True
        elif opt == '--restart':
            print (sys.argv[0] + ' restart')
            STOP=True
            START=True
        elif opt == '--daemon':
            print (sys.argv[0] + ' daemon')
            DAEMON=True
        elif opt == '--manual':
            print (sys.argv[0] + ' manual')
            MANUAL=True
           
    if not START and not STOP:
        START=True
    
    if (STOP):
        stop()
    if (START): 
        start(DAEMON)   
             
    print ("__main__ exit")
    exit()
    print ("__main__ exit has been done so this should not be printed")



