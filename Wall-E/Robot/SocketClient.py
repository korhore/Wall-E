'''
Created on Feb 24, 2013
Updated on Mar 8, 2014

@author: reijo
'''

from threading import Thread
import signal
import sys
import getopt
import socket
import math
import time

import daemon
import lockfile

#from Axon import Axon
from Sensation import Sensation
#from Romeo import Romeo
#from ManualRomeo import ManualRomeo
#from Hearing import Hear





class SocketClient(Thread): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, queue, socket, address):
        Thread.__init__(self)
        self.queue=queue
        self.socket=socket
        self.address=address
        self.name = str(address)
        self.running=False
       
    def run(self):
        print("Starting " + self.name)
        
        # starting other threads/senders/capabilities
        
        self.running=True
 
        while self.running:
            print("SocketClient waiting size of next Sensation from queue")
            sensation = self.queue.get()
            self.running = SocketClient.sendSensation(sensation, self.socket, self.address)
#             sensation_string = str(sensation)
#             length =len(sensation_string)
#             length_string = str(length)
#             length_ok = True
#             try:
#                 l = self.socket.send(length_string) # message length section
#                 print("SocketClient wrote length of Sensation to " + str(self.address))
#             except:
#                 print("SocketClient error writing length of Sensation to, closing socket " + str(self.address))
#                 self.running=False
#                 length_ok = False
#             if length_ok:
#                 try:
#                     l = self.socket.send(sensation_string)  # message data section
#                     print("SocketClient wrote Sensation to " + str(self.address))
#                     if length != l:
#                         print("SocketClient length " + str(l) + " != " + length_string + " error writing to " + str(self.address))
#                 except:
#                     print("SocketClient error writing Sensation to, closing socket " + str(self.address))
#                     self.running=False
#             if self.running:
#                 try:
#                     l = self.socket.send(Sensation.SEPARATOR)  # message separator section
#                     if Sensation.SEPARATOR_SIZE == l:
#                         print("SocketClient wrote separator to " + str(self.address))
#                     else:
#                         print("SocketClient length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(self.address))
#                 except:
#                     print("SocketClient error writing Sensation to, closing socket " + str(self.address))
#                     self.running=False
                

        self.socket.close()

    '''
    Global method for sending a sensation
    '''
        
    def sendSensation(sensation, socket, address):
        print("SocketClient.sendSensation")
        
#         sensation_string = str(sensation)
#         length =len(sensation_string)
#         length_string = Sensation.LENGTH_FORMAT.format(length)
        bytes = sensation.bytes()
        length =len(bytes)
        length_bytes = length.to_bytes(Sensation.NUMBER_SIZE, byteorder=Sensation.BYTEORDER)

        ok = True
        try:
            l = socket.send(Sensation.SEPARATOR.encode('utf-8'))        # message separator section
            if Sensation.SEPARATOR_SIZE == l:
                print("SocketClient wrote separator to " + str(address))
            else:
                print("SocketClient length " + str(l) + " != " + str(Sensation.SEPARATOR_SIZE) + " error writing to " + str(address))
                ok = False
        except Exception as err:
            print("SocketClient error writing Sensation.SEPARATOR to " + str(address)  + " error " + str(err))
            ok=False
        if ok:
            try:
#                l = socket.send(length_string.encode('utf-8'))          # message length section
                l = socket.send(length_bytes)                            # message length section
                print("SocketClient wrote length " + str(length) + " of Sensation to " + str(address))
            except Exception as err:
                print("SocketClient error writing length of Sensation to " + str(address) + " error " + str(err))
                ok = False
            if ok:
                try:
#                    l = socket.send(sensation_string.encode('utf-8'))  # message data section
                    l = socket.send(bytes)                              # message data section
                    print("SocketClient wrote Sensation to " + str(address))
                    if length != l:
                        print("SocketClient length " + str(l) + " != " + str(length) + " error writing to " + str(address))
                        ok = False
                except Exception as err:
                    print("SocketClient error writing Sensation to " + str(address) + " error " + str(err))
                    ok = False
        return ok

    '''
    Method for stopping remote host
    and after that us
    '''
    def stop(self):
        print(self.name + ":stop") 
        SocketClient.sendSensation(sensation=Sensation(number=0, sensationType = Sensation.SensationType.Stop), socket=self.socket, address=self.address)
        self.running = False

    '''
    Global method for stopping remote host
    '''
    def stop(socket, address):
        print("SocketClient:stop") 
        SocketClient.sendSensation(sensation=Sensation(number=0, sensationType = Sensation.SensationType.Stop), socket=socket, address=address)
