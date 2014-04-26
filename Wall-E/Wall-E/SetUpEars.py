'''
Created on Jan 19, 2014

@author: reijo
'''

import alsaaudio
#from threading import Thread
#from Queue import Queue
#import math
#import time

#from Ear import Ear
#from Sound import Sound
#from SoundPosition import SoundPosition
#from Sensation import Sensation
import ConfigParser



      
if __name__ == "__main__":
    #main()
    print "Setting up microprones for Walle-robot"
    print
    print 'str(alsaaudio.cards())' + str(alsaaudio.cards())
    print "Your audio cards are:"
    for card in alsaaudio.cards():
        if card != 'ALSA':
            print card
            
    print 'Plug LEFT microphone on, unplug righ one if it is plugged, so LEFT microphone can be detected.'
    raw_input('Press Return when ready')
    left = None
    for card in alsaaudio.cards():
        if card != 'ALSA' and left is None:
            print card
            left =  card
            print "LEFT microphone is set as " + left
            break
    if left is None:
        print "LEFT microphone was not found"
        print "Setting is NOT DONE!"
        exit(-1)
           
    print
    print 'Plug RIGHT microphone on, keep left plugged, so RIGHT microphone can be detected.'
    raw_input('Press Return when ready')
    right = None
    for card in alsaaudio.cards():
        if card != 'ALSA' and right is None and card != left:
            print card
            right =  card
            print "RIGHT microphone is set as " + right
            break
    if right is None:
        print "RIGHT microphone was not found"
        print "Setting is NOT DONE!"
        exit(-1)

    print
    print "Microprhones are set"
    print "LEFT microphone is set as " + left
    print "RIGHT microhrone is set as " + right
    print
    print "Writing config file"

    config = ConfigParser.RawConfigParser()

    config.add_section('Microprhones')
    config.set('Microprhones', 'left', left)
    config.set('Microprhones', 'right', right)

    # Writing our configuration file to 'Walle.cfg'
    with open('Walle.cfg', 'wb') as configfile:
        config.write(configfile)

    # Reading our configuration file to 'Walle.cfg'
    config.read('Walle.cfg')
    print 'From config file: left: ' + config.get('Microprhones', 'left')
    print 'From config file: right: ' + config.get('Microprhones', 'right')
    print "Setting is DONE!"

#         ear1=Ear(card=alsaaudio.cards()[0]) #'Set') # card=alsaaudio.cards()[1]
#         ear1.start()
#         ear2=Ear(card=alsaaudio.cards()[1]) # card=alsaaudio.cards()[1]
#         ear2.start()
#         
# 
#         t = Timer(60.0, stop)
#         t.start() # after 30 seconds, Ear will be stopped

    exit()
       
        
