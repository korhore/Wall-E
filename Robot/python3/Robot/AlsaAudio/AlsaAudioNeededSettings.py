'''
Created on 03.08.2019
Updated on 22.08.2019

@author: reijo.korhonen@gmail.com

Common setting for all AlsaAudio-Robots
These setting need that alsaaudio (pyalsaaudio) is installed into system
and that can need that C-alsa-headers are nstalled, because installing
may need alsa-compilation etc.

For that reason these settings are in separate file, because only
those robots that read or write alsa-devices need these, but
other Robots may nee other settings and those systems can be virtual ons
without capability to use ausio at all, so there is no reason to install
alsa for those.


'''
import alsaaudio

AUDIO_FORMAT = alsaaudio.PCM_FORMAT_S16_LE
