'''
Created on Feb 24, 2013

@author: reijo
'''

import SocketServer
from Command import Command
from Romeo import Romeo
from subprocess import call
from threading import Thread
import signal
import sys
import getopt
import socket


import daemon
import lockfile



HOST = '0.0.0.0'
PORT = 2000
PICTURE_PORT = 2001

DAEMON=False
START=False
STOP=False


class WalleServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
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
                command=Command(string)
                print command
                if command.getCommand() == Command.CommandTypes.Stop:
                    self.request.sendall(str(command))
                    print "WalleRequestHandler.handle command " + str(command) + " Shutdown"
                    if not WalleRequestHandler.romeo is None:
                        print "_WalleRequestHandler.handle del WalleRequestHandler.romeo"
                        del WalleRequestHandler.romeo
                        WalleRequestHandler.romeo = None
                        
                    print "WalleRequestHandler.handle command pictureServer.shutdown()"
                    WalleRequestHandler.pictureServer.serving =False
                    
                    print "WalleRequestHandler.handle command " + str(command) + " server.shutdown()"
                    WalleRequestHandler.server.serving =False
                else:
                    command, imageData = self.processCommand(command)
                    
                    self.request.sendall(str(command))
                    print "WalleRequestHandler.handle command " + str(command)
                    if command.getCommand() == Command.CommandTypes.Picture:
                        self.request.sendall(imageData)
                    print "WalleRequestHandler.handle command imagedata " + str(len(imageData))
           
    def processCommand(self, command):
        if command.getCommand() == Command.CommandTypes.Picture:
            print "WalleServer.processCommand Command.CommandTypes.Picture"
            # take a picture
            call(["raspistill", "-vf", "-ex", "night", "-o", "/tmp/image.jpg"])
            f = open("/tmp/image.jpg", 'r')
            imageData=f.read()
            command.setImageSize(len(imageData))
            return command, imageData
        else:
            return WalleRequestHandler.romeo.processCommand(command)
            
        
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
    
    print 'signal_handler: Shutting down command server ...'
    WalleRequestHandler.server.serving =False
    print 'signal_handler: command server is down OK'
    
    print 'signal_handler: Shutting down picture server...'
    WalleRequestHandler.pictureServer.serving =False
    print 'signal_handler: picture server is down OK'
   

def do_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    print "do_server: create romeo"
    WalleRequestHandler.romeo = Romeo()
    #romeo.test2()


    succeeded=True
    try:
        # Create the server, binding to localhost on port 2000
        print "do_server: create SocketServer.TCPServer " + HOST + " " + str(PORT)
        #server = SocketServer.TCPServer((HOST, PORT), WalleRequestHandler)
        server = WalleServer((HOST, PORT), WalleRequestHandler)
        WalleRequestHandler.server = server
        
        print "do_server: create SocketServer.TCPServer " + HOST + " " + str(PICTURE_PORT)
        #pictureServer = SocketServer.TCPServer((HOST, PICTURE_PORT), WalleRequestHandler)
        pictureServer = WalleServer((HOST, PICTURE_PORT), WalleRequestHandler)
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
        print "stop: sock.sendall STOP command"
        sock.sendall(str(Command(command = 'S')))
    
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
     

    WalleRequestHandler.romeo = None    # no romeo devoce connection yet
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
    WalleRequestHandler.romeo = None    # no romeo devoce connection yet

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



