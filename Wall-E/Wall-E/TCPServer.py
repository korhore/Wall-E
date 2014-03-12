'''
Created on Feb 24, 2013
Updated on Mar 8, 2014

@author: reijo
'''

from SocketServer import SocketServer
from Axon import Axon
from Sensation import Sensation
from Romeo import Romeo
from ManualRomeo import ManualRomeo
from Hearing import Hearing
from threading import Thread
import signal
import sys
import getopt
import socket
import math
import time


import daemon
import lockfile



HOST = '0.0.0.0'
PORT = 2000
PICTURE_PORT = 2001

DAEMON=False
START=False
STOP=False
MANUAL=False

     
class TCPServer(Thread): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    
    # inhered
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    #allow_reuse_address = False


    def __init__(self, queue, server_address):
        Thread.__init__(self)
        self.name = "TCPServer"
        self.queue = queue
        self.server_address = server_address
        print self.name + ": creating socket"
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.socket.setblocking(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketServers = []
        self.running=False
       
    def run(self):
        print self.name + ":Starting" 
        
        
        self.running=True
#        if self.allow_reuse_address:
#            self.socket.setsockopt(socket.SOL_TCP, socket.SO_REUSEADDR, 1)
#            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          
        print self.name + "; bind " + str(self.server_address)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()
        self.socket.listen(self.request_queue_size)
 
        while self.running:
            print self.name + ": waiting self.socket.accept()"
            socket, address = self.socket.accept()
            print self.name + ": self.socket.accept() " + str(address)
            socketServer = self.createSocketServer(queue=self.queue, socket=socket, address=address)
            socketServer.start()
            time.sleep(5)        # sleep to get first request handled, it may wan't to stop everything

    def stop(self):
        print self.name + ":stop" 
        self.running = False
        for socketServer in self.socketServers:
            if socketServer.running:
                socketServer.stop()
        
    def createSocketServer(self, queue, socket, address):
        socketServer =  None
        for socketServerCandidate in self.socketServers:
            if not socketServerCandidate.running:
                socketServer = socketServerCandidate
                print self.name + ":createSocketServer: found SocketServer not running"
                socketServer.__init__(queue, socket, address)
                break
        if not socketServer:
            print self.name + ":createSocketServer: creating new SocketServer"
            socketServer = SocketServer(queue, socket, address)
            self.socketServers.append(socketServer)
        return socketServer
