'''
Created on Jan 19, 2014
Edfited 01.05.2019

@author: reijo
'''

import alsaaudio
from configparser import ConfigParser

from Config import Config



      
if __name__ == "__main__":
    #main()
    print ("Setting up microphones for Walle-robot")
    print
    print ('str(alsaaudio.cards())' + str(alsaaudio.cards()))
    print ("Your audio cards are:")
    for card in alsaaudio.cards():
        if card != 'ALSA':
            print (card)
            
    print ('Unplug both LEFT and RIGT microphone or lyour only microphone, so your microphone(s) can be detected.')
    input('Press Return when ready')
    cards_no_mic = alsaaudio.cards()
    for card in cards_no_mic:
        if card != 'ALSA':
            print (card)

            
    print ('Plug Only or LEFT microphone on, unplug right one if it is plugged, so LEFT microphone can be detected.')
    input('Press Return when ready')
    left = None
    cards_left_mic = alsaaudio.cards()
    for card in alsaaudio.cards():
        if card != 'ALSA' and left is None:
            print (card)
            if card not in cards_no_mic:
                left =  card
                print ("LEFT microphone is set as \'" + left + '\'')
                break
    if left is None:
        print ("LEFT microphone was not found")
        print ("Setting is NOT DONE!")
        exit(-1)
           
    print ()
    right = None
    print ('Plug RIGHT microphone on, keep left plugged, so RIGHT microphone can be detected.')
    reply = input('Press Y + Return when ready or N, if you don\'t have other microphone: ')
    print ("Reply " + reply)
    if reply.upper()[0] == 'Y':
        cards_left_mic = alsaaudio.cards()
        for card in alsaaudio.cards():
            if card != 'ALSA' and right is None:
                if card not in cards_left_mic:
                    right =  card
                    print ("RIGHT microphone is set as \'" + right + '\'')
                    break
        if right is None:
            print ("RIGHT microphone was not found")
            print ("Setting is NOT DONE!")
            exit(-1)

    print ()
    print ("Microphones are set")
    if left is not None:
        print ("LEFT or ONLY microphone is set as \'" + left + '\'')
    if right is not None:
        print ("RIGHT microphone is set as \'" + right + '\'')
    print
    print ("Writing config file")

    try:
        config = ConfigParser()
        config.read(Config.CONFIG_FILE_PATH)
    
    #    config.add_section(Config.LOCALHOST)
        if left is not None:
            config.set(Config.LOCALHOST, Config.MICROPHONE, left)
            config.set(Config.LOCALHOST, Config.MICROPHONE_LEFT, left)
        if right is not None:
            config.set(Config.LOCALHOST, Config.MICROPHONE_RIGHT, right)
    
        # Writing our configuration file to 'Robot.cfg'
        configfile = open(Config.CONFIG_FILE_PATH, 'w')
        config.write(configfile)
        configfile.close()
    
        # Reading our configuration file to 'Walle.cfg'
        config.read(Config.CONFIG_FILE_PATH)
        if left is not None:
            print ('From config file: microphone: \'' + config.get(Config.LOCALHOST, Config.MICROPHONE) + '\'')
            print ('From config file: left: \'' + config.get(Config.LOCALHOST, Config.MICROPHONE_LEFT) + '\'')
        if right is not None:
            print ('From config file: right: \'' + config.get(Config.LOCALHOST, Config.MICROPHONE_RIGHT) + '\'')
    except Exception as e:
                print('Got exception, when writing config file ' + str(e))
    print ("Setting is DONE!")

#         ear1=Ear(card=alsaaudio.cards()[0]) #'Set') # card=alsaaudio.cards()[1]
#         ear1.start()
#         ear2=Ear(card=alsaaudio.cards()[1]) # card=alsaaudio.cards()[1]
#         ear2.start()
#         
# 
#         t = Timer(60.0, stop)
#         t.start() # after 30 seconds, Ear will be stopped

    exit()
       
        
