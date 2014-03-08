'''
Created on Feb 24, 2013
Updated on Mar 8, 2014

@author: reijo
'''

import SocketServer
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


class SocketServer(Thread): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):


    def __init__(self, queue, socket, address):
        Thread.__init__(self)
        self.queue=queue
        self.socket=socket
        self.address=address
        self.name = str(address)
        self.running=False
       
    def run(self):
        print "Starting " + self.name
        
        # starting other threads/senders/capabilities
        
        self.running=True
 
        while self.running:
            self.data = self.socket.recv(1024).strip()
            print "SocketServer Client " + str(self.address) + " wrote " + self.data
            if len(self.data) == 0:
                self.running = False
            else:
                strings=self.data.split('|')
                for string in strings:
                    print "WalleSocketServer string " + string
                    if len(string) > 0:
                        sensation=Sensation(string)
                        print sensation
                        self.queue.put(sensation)

        self.socket.close()

    def stop(self):
        print self.name + ":stop" 
        self.socket.sendall(str(Sensation(sensationType = 'S')))
        self.running = False

