'''
Created on Feb 24, 2013
Updated on 19.06.2019

@author: reijo.korhonen@gmail.com

Deprecated. Implementation is in MainRobot

SocketCilent is a Robot that puts its sensations behind network to another
Robot

TODO Capabilities come from network

'''


import socket

from Robot import  Robot
from Config import Config, Capabilities
from Sensation import Sensation






class SocketClient(Robot): #, SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self,
                 address = None,
                 remoteHost=None,
                 sock = None,
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

        print("We are in SocketClient, not Robot")
        self.queue=queue
        self.socket=sock
        self.address=address
        self.name = str(address)
        self.remoteHost=remoteHost

        self.running=False
 
        if self.socket is None:       
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect to server
                self.log('__init__: ' + 'self.socket.connect(' + str(self.address) + ')')
                self.address=(self.remoteHost, PORT)
                self.socket.connect(self.address)
                self.log('__init__: ' + 'connected' + str(self.address))
            except Exception as err: 
                self.log('__init__: ' + 'elf.socket.connect error ' + str(err))

        
    def process(self, sensation, association=None):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')      
            self.stop()

        # We handle only sensation going in-direction
        elif sensation.getDirection() == Sensation.Direction.In:
             self.running = SocketClient.sendSensation(sensation, self.socket, self.address)                

        self.socket.close()

    '''
    Global method for sending a sensation
    '''
        
    def sendSensation(sensation, socket, address):
        #print("SocketClient.sendSensation")
        
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
                pass
                #print("SocketClient wrote separator to " + str(address))
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
                #print("SocketClient wrote length " + str(length) + " of Sensation to " + str(address))
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
        self.log('stop')
        SocketClient.sendSensation(associations=[], sensation=Sensation(number=0, sensationType = Sensation.SensationType.Stop), socket=self.socket, address=self.address)
        self.running = False

        self.socket.close()
        super(SocketClient, self).stop()

    '''
    Global method for stopping remote host
    '''
#     def stop(socket, address):
#         print("SocketClient:stop") 
#         SocketClient.sendSensation(sensation=Sensation(number=0, sensationType = Sensation.SensationType.Stop), socket=socket, address=address)

