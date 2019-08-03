'''
Created on 03.08.2019
Updated on 03.08.2019

@author: reijo.korhonen@gmail.com

Common setting for all AlsaAudio-Robots

'''
import alsaaudio

AUDIO_CONVERSION_FORMAT='<i2'
AUDIO_CHANNELS=1
AUDIO_RATE = 44100
AUDIO_FORMAT = alsaaudio.PCM_FORMAT_S16_LE
AUDIO_PERIOD_SIZE = 2018
