'''
Created on Feb 24, 2013
Updated on 06.05.2019

@author: reijo.korhonen@gmail.com

Socketserver is a Robot that gets sensations from a Robot behind network
TODO Capabilities come from network
'''

import socket

from Robot import  Robot
from Config import Config, Capabilities
from Sensation import Sensation
from SocketClient import SocketClient


class SocketServer(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 socket, 
                 address,
                 parent=None,
                 instance=None,
                 is_virtualInstance=False,
                 is_subInstance=False,
                 level=0):

        Robot.__init__(self,
                       parent=parent,
                       instance=instance,
                       is_virtualInstance=is_virtualInstance,
                       is_subInstance=is_subInstance,
                       level=level)
        
        print("We are in SocketServer, not Robot")
        self.socket=socket
        self.address=address
        self.name = str(address)
       
    def run(self):
        print("Starting " + self.name)
        
        # starting other threads/senders/capabilities
        
        self.running=True
 
        while self.running:
            print("SocketServer waiting next Sensation from" + str(self.address))
            synced = False
            self.data = self.socket.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
            if len(self.data) == 0:
                synced = True# Test
                #self.running = False
            #print "WalleSocketServer separator l " + str(len(self.data)) + ' ' + str(len(Sensation.SEPARATOR))
            while not synced and self.running:
                if len(self.data) == len(Sensation.SEPARATOR):
                    if self.data[0] is Sensation.SEPARATOR[0]:    # this also syncs to next message, if we get socket transmit errors
                        synced = True
                if not synced:
                    self.data = self.socket.recv(Sensation.SEPARATOR_SIZE).strip().decode('utf-8')  # message separator section
                    #print "WalleSocketServer separator l " + str(len(self.data)) + ' ' + str(len(Sensation.SEPARATOR))
                    if len(self.data) == 0:
                        self.running = False               

            if synced and self.running:
                print("SocketServer waiting size of next Sensation from" + str(self.address))
                #self.data = self.socket.recv(Sensation.LENGTH_SIZE).strip().decode('utf-8') # message length section
                self.data = self.socket.recv(Sensation.NUMBER_SIZE)                         # message length section
                if len(self.data) == 0:
                    self.running = False
                else:
                    #length = int.from_bytes(self.data, Sensation.BYTEORDER)
                    #print("SocketServer Client " + str(self.address) + " wrote " + self.data)
                    length_ok = True
                    try:
                        #sensation_length = int(self.data)
                        sensation_length = int.from_bytes(self.data, Sensation.BYTEORDER)
                    except:
                        print("SocketServer Client protocol error, no valid length resyncing" + str(self.address) + " wrote " + self.data)
                        length_ok = False
                        
                    if length_ok:
                        print("SocketServer Client " + str(self.address) + " wrote " + str(sensation_length))
                        #print "SocketServer of next Sensation from " + str(self.address)
                        self.data=None
                        while sensation_length > 0:
                            #data = self.socket.recv(sensation_length).strip().decode('utf-8') # message data section
                            data = self.socket.recv(sensation_length)                       # message data section
                            if len(data) == 0:
                                self.running = False
                            else:
                                if self.data is None:
                                    self.data = data
                                else:
                                    self.data = self.data+data
                                sensation_length = sensation_length - len(data)
                                #print "SocketServer Sensation data from " + str(self.address)+ ' ' + self.data + ' left ' + str(sensation_length)
                                
                                
                        if self.running:
                            #print "SocketServer string " + self.data
                            #sensation=Sensation(self.data)
                            sensation=Sensation(associations=[], bytes=self.data)
                            self.log("SocketServer got sensation" + str(sensation))
                            self.process(sensation)
            

        self.socket.close()

    def stop(self):
        print(self.name + ":stop") 
        ok = SocketClient.stop(socket = self.socket, address=self.address)
        self.running = False

