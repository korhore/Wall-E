'''
Created on 30.04.2019
Updated on 30.04.2019

@author: reijo.korhonen@gmail.com
'''

from Robot import  Robot
from Config import Config, Capabilities


class Hearing(Robot):
    """
     Study dynamic import
     Implemenation of this functionality comes later
    """

    def __init__(self, workingDirectory=None,
                 configFilePath=Config.CONFIG_FILE_PATH,
                 inAxon=None, # we read this as muscle functionality and getting
                              # sensationsfron ot subInstances (Senses)
                              # write to this when submitting things to subInstances
                 outAxon=None):
        Robot.__init__(self, workingDirectory=workingDirectory,
                 configFilePath=configFilePath,
                 inAxon=None,
                 outAxon=outAxon)
        print("We are in Hearing, not Robot")

