'''
Created on Feb 24, 2013
Updated on Mar 8, 2014

@author: reijo
'''

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
            print "SocketServer waiting size of next Sensation from" + str(self.address)
            self.data = self.socket.recv(Sensation.LENGTH_SIZE).strip()
            if len(self.data) == 0:
                self.running = False
            else:
                print "SocketServer Client " + str(self.address) + " wrote " + self.data
                length_ok = True
                try:
                    sensation_length = int(self.data)
                except:
                    print "SocketServer Client protocol error, no valid length resyncing" + str(self.address) + " wrote " + self.data
                    length_ok = False
                    
                if length_ok:
                    print "SocketServer of next Sensation from" + str(self.address)
                    self.data = self.socket.recv(sensation_length).strip()

                    if len(self.data) == 0:
                        self.running = False
                    else:
                        print "WalleSocketServer string " + self.data
                        sensation=Sensation(self.data)
                        print sensation
                        self.queue.put(sensation)

        self.socket.close()

    def stop(self):
        print self.name + ":stop" 
        self.socket.sendall(str(Sensation(sensationType = 'S')))
        self.running = False

