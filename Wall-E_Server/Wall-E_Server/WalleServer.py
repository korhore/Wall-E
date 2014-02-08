'''
Created on Feb 24, 2013
Updated on Feb 3, 2014

@author: reijo
'''

import SocketServer
from Sensation import Sensation
from Romeo import Romeo
from Hearing import Hearing
from threading import Thread
import signal
import sys
import getopt
import socket
from Queue import Queue


import daemon
import lockfile



HOST = '0.0.0.0'
PORT = 2000
PICTURE_PORT = 2001

DAEMON=False
START=False
STOP=False

class WalleServer(Thread):
    """
    Controls Walle-robot. Walle has capabilities like moving, hearing, seeing and position sense.
    Technically we use socket servers to communicate with external devices. Romeo board is controlled
    using library using USB. We use USB-microphones and Raspberry pi camera.
    
    Walle emulates senses (camera, microphone, mobile phone) that have emit sensations to "brain" that has state and memory and gives
    commands (tecnically Sensation class instances) to muscles (Romeo Board, mobile phone)
    
    Integraterd sensation are transferred in Queue, which is thread safe. Every SEnse runs in its own thread as real senses, independently.
    External Senses are handled using sockets.
    """
    
    sensation_queue = Queue()       # global queue for senses to put sensations

    def __init__(self):
        Thread.__init__(self)
        
        self.azimuth=0.0                # position sense, azimuth from north
        self.hearing_angle = 0.0        # device hears sound from this angle, device looks to its front
                                        # to the azimuth direction

        self.hearing=Hearing(WalleServer.sensation_queue)
 


    def run(self):
        print "Starting " + self.name
        
        # starting other threads/senders/capabilities
        
        self.running=True
        self.hearing.start()
 
        while self.running:
            sensation=WalleServer.sensation_queue.get()
            self.process(sensation)

        self.hearing.stop()

class WalleSocketServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pause = 0.25
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address,
                                        RequestHandlerClass)
        self.socket.settimeout(self.pause)
        self.serving =True
        


    def serve_forever(self):
        while self.serving:
            self.handle_request()


class WalleRequestHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    

    def handle(self):
        print "WalleRequestHandler.handle"
        # self.request is the TCP socket connected to the client
        print "WalleRequestHandler.handle lf.request.recv(1024).strip()"
        self.data = self.request.recv(1024).strip()
        #print "{} wrote:".format(self.client_address[0])
        print "WalleRequestHandler.handle Client wrote " + self.data
        # just send back the same data, but upper-cased
        print "WalleRequestHandler.handle self.request.sendall(self.data.upper())"
        strings=self.data.split('|')
        for string in strings:
            print "WalleRequestHandler.handle string " + string
            if len(string) > 0:
                sensation=Sensation(string)
                print sensation
                if sensation.getSensation() == Sensation.SensationTypes.Stop:
                    self.request.sendall(str(sensation))
                    print "WalleRequestHandler.handle sensation " + str(sensation) + " Shutdown"
                    if not WalleRequestHandler.romeo is None:
                        print "_WalleRequestHandler.handle del WalleRequestHandler.romeo"
                        del WalleRequestHandler.romeo
                        WalleRequestHandler.romeo = None
                        
                    print "WalleRequestHandler.handle sensation pictureServer.shutdown()"
                    WalleRequestHandler.pictureServer.serving =False
                    
                    print "WalleRequestHandler.handle sensation " + str(sensation) + " server.shutdown()"
                    WalleRequestHandler.server.serving =False
                else:
                    sensation, imageData = self.processSensation(sensation)
                    
                    self.request.sendall(str(sensation))
                    print "WalleRequestHandler.handle sensation " + str(sensation)
                    if sensation.getSensation() == Sensation.SensationTypes.Picture:
                        self.request.sendall(imageData)
                    print "WalleRequestHandler.handle sensation imagedata " + str(len(imageData))
           
    def processSensation(self, sensation):
        if sensation.getSensation() == Sensation.SensationTypes.Picture:
            print "WalleSocketServer.processSensation Sensation.SensationTypes.Picture"
            # take a picture
            call(["raspistill", "-vf", "-ex", "night", "-o", "/tmp/image.jpg"])
            f = open("/tmp/image.jpg", 'r')
            imageData=f.read()
            sensation.setImageSize(len(imageData))
            return sensation, imageData
        else:
            if not WalleRequestHandler.romeo == None:
                return WalleRequestHandler.romeo.processSensation(sensation)
            else:
                return sensation, ""
           
        
#    def handle(self):
#        # self.rfile is a file-like object created by the handler;
#        # we can now use e.g. readline() instead of raw recv() calls
#        self.data = self.rfile.readline().strip()
#        print "{} wrote:".format(self.client_address[0])
#        print self.data
#        # Likewise, self.wfile is a file-like object used to write back
#        # to the client
#        self.wfile.write(self.data.upper())

def threaded_server(arg):
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "threaded_server: starting server"
    arg.serve_forever()
    print "threaded_server: arg.serve_forever() ended"

def signal_handler(signal, frame):
    print 'signal_handler: You pressed Ctrl+C!'
    
    print 'signal_handler: Shutting down sensation server ...'
    WalleRequestHandler.server.serving =False
    print 'signal_handler: sensation server is down OK'
    
    print 'signal_handler: Shutting down picture server...'
    WalleRequestHandler.pictureServer.serving =False
    print 'signal_handler: picture server is down OK'

  

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

# TODO remove # after test
#    print "do_server: create romeo"
#    try:
#        WalleRequestHandler.romeo = Romeo()
#    except AttributeError:
#        print "do_server: Romeo error, only tests wuthout it are possible"
#        WalleRequestHandler.romeo = None
 
    #romeo.test2()

    print "do_server: create WalleServer"
    walle = WalleServer()
    #server = WalleSocketServer((HOST, PORT), WalleRequestHandler)
    #WalleRequestHandler.server = server

    succeeded=True
    try:
        
        # Create the server, binding to localhost on port 2000
        print "do_server: create SocketServer.TCPServer "
        print "do_server: create SocketServer.TCPServer " + HOST + " " + str(PORT)
        #server = SocketServer.TCPServer((HOST, PORT), WalleRequestHandler)
        server = WalleSocketServer((HOST, PORT), WalleRequestHandler)
        WalleRequestHandler.server = server
        
        print "do_server: create SocketServer.TCPServer " + HOST + " " + str(PICTURE_PORT)
        #pictureServer = SocketServer.TCPServer((HOST, PICTURE_PORT), WalleRequestHandler)
        pictureServer = WalleSocketServer((HOST, PICTURE_PORT), WalleRequestHandler)
        WalleRequestHandler.pictureServer = pictureServer

    except Exception: 
        print "do_server: socket error, exiting"
        succeeded=False
   # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    #threaded_server(pictureServer)
    #threaded_server(server)
    if succeeded:
        print 'do_server: Press Ctrl+C to Stop'
        
        print 'do_server: Creating serverThread'
        serverThread = Thread(target = threaded_server, args = (server, ))
        print 'do_server: Starting  serverThread'
        serverThread.start()
        
        print 'do_server: Creating pictureServerThread'
        pictureServerThread = Thread(target = threaded_server, args = (pictureServer, ))
        print 'do_server: Starting  pictureServerThread'
        pictureServerThread.start()
          
        print 'do_server: Waiting pictureServerThread to stop'
        pictureServerThread.join()

        print 'do_server: Waiting serverThread to stop'
        serverThread.join()
        
        print 'do_server: Servers stoppped OK'
    
    print "do_server exit"
    
def start(is_daemon):
        if is_daemon:
            print "start: daemon.__file__ " +  daemon.__file__
            stdout=open('/tmp/Wall-E_Server.stdout', 'w+')
            stderr=open('/tmp/Wall-E_Server.stderr', 'w+')
            #remove('/var/run/Wall-E_Server.pid.lock')
            pidfile=lockfile.FileLock('/var/run/Wall-E_Server.pid')
            with daemon.DaemonContext(stdout=stdout,
                                      stderr=stderr,
                                      pidfile=pidfile):
                do_server()
        else:
           do_server()

    
def stop():
    
    print "stop: socket.socket(socket.AF_INET, socket.SOCK_STREAM)"
    # Create a socket (SOCK_STREAM means a TCP socket)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception: 
        print "stop: socket error"

    
    try:
        # Connect to server and send data
        print 'stop: sock.connect((localhost, PORT))'
        sock.connect(('localhost', PORT))
        print "stop: sock.sendall STOP sensation"
        sock.sendall(str(Sensation(sensation = 'S')))
    
        # Receive data from the server
        received = sock.recv(1024)
        print 'stop: received answer ' + received
    except Exception: 
        print "stop: connect error"
    finally:
        print 'stop: sock.close()'
        sock.close()
    print "stop: end"

 
def main():
    signal.signal(signal.SIGINT, signal_handler)
     

    WalleRequestHandler.romeo = None    # no romeo device connection yet
#    print "main: create romeo"
#    romeo = Romeo()
    #romeo.test2()

    #HOST, PORT = "localhost", 2000

    # Create the server, binding to localhost on port 2000
    print "main: create SocketServer.TCPServer " + HOST + " " + str(PORT)
    server = SocketServer.TCPServer((HOST, PORT), WalleRequestHandler)
    
    print "main: create SocketServer.TCPServer " + HOST + " " + str(PICTURE_PORT)
    pictureServer = SocketServer.TCPServer((HOST, PICTURE_PORT), WalleRequestHandler)

 
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    #threaded_server(pictureServer)
    #threaded_server(server)
    
    print 'main: Press Ctrl+C to Stop'
    
    print 'main: Creating serverThread'
    serverThread = Thread(target = threaded_server, args = (server, ))
    print 'main: Starting  serverThread'
    serverThread.start()
    
    print 'main: Creating pictureServerThread'
    pictureServerThread = Thread(target = threaded_server, args = (pictureServer, ))
    print 'main: Starting  pictureServerThread'
    pictureServerThread.start()
    
    print 'main: Waiting serverThread to stop'
    serverThread.join()
    print 'main: Waiting pictureServerThread to stop'
    pictureServerThread.join()
    
    print 'main: Servers stoppped OK'
    
    sys.exit(0)



if __name__ == "__main__":
    WalleRequestHandler.romeo = None    # no romeo device connection yet

    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)
    try:
        opts, args = getopt.getopt(sys.argv[1:],"",["start","stop","restart","daemon"])
    except getopt.GetoptError:
      print sys.argv[0] + '[--start] [--stop] [--restart] [--daemon]'
      sys.exit(2)
    print 'opts '+ str(opts)
    for opt, arg in opts:
        print 'opt '+ opt
        if opt == '--start':
            print sys.argv[0] + ' start'
            START=True
        elif opt == '--stop':
            print sys.argv[0] + ' stopt'
            STOP=True
        elif opt == '--restart':
            print sys.argv[0] + ' restart'
            STOP=True
            START=True
        elif opt == '--daemon':
            print sys.argv[0] + ' daemon'
            DAEMON=True
            
    if not START and not STOP:
        START=True
    
    if (STOP):
        stop()
    if (START): 
        start(DAEMON)        
#        if DAEMON:
#            print "daemon.__file__ " +  daemon.__file__
#            stdout=open('/tmp/Wall-E_Server.stdout', 'w+')
#            stderr=open('/tmp/Wall-E_Server.stderr', 'w+')
#            #remove('/var/run/Wall-E_Server.pid.lock')
#            pidfile=lockfile.FileLock('/var/run/Wall-E_Server.pid')
#            with daemon.DaemonContext(stdout=stdout,
#                                      stderr=stderr,
#                                      pidfile=pidfile):
#                do_server()
#        else:
#           do_server()
    
    # if romeo device connection, then delete it as last thing
    if not WalleRequestHandler.romeo is None:
        print "_main__ del WalleRequestHandler.romeo"
        del WalleRequestHandler.romeo
        WalleRequestHandler.romeo = None
    print "__main__ exit"
    exit()



