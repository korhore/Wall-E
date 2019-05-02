'''
Created on 30.04.2019
Updated on 30.04.2019

@author: reijo.korhonen@gmail.com
'''

from Robot import  Robot
from Config import Config, Capabilities


class Seeing(Robot):
    """
     Study dynamic import
     Implemenation of this functionality comes later
    """

    def __init__(self,
                 instance=None,
                 is_virtualInstance=False,
                 is_subInstance=False,
                 level=0,

                 inAxon=None, # we read this as muscle functionality and getting
                              # sensationsfron ot subInstances (Senses)
                              # write to this when submitting things to subInstances
                 outAxon=None):
        Robot.__init__(self,
                       instance=instance,
                       is_virtualInstance=is_virtualInstance,
                       is_subInstance=is_subInstance,
                       level=level,
                       inAxon=inAxon,
                       outAxon=outAxon)
        print("We are in Seeing, not Robot")
        

    '''    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    TODO above implementation is mostly for Hearing Sensory and
    Moving Sensory and should be move to those implementations.
    
    '''
            
            
    def process(self, sensation):
        self.log('process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + str(sensation))      
        if sensation.getSensationType() == Sensation.SensationType.Drive:
            self.log('process: Sensation.SensationType.Drive')      
        elif sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log('process: SensationSensationType.Stop')      
            self.stop()
        elif sensation.getSensationType() == Sensation.SensationType.Who:
            print (self.name + ": Robotserver.process Sensation.SensationType.Who")
            
        # TODO study what capabilities out subrobots have ins put sensation to them
        elif self.config.canHear() and sensation.getSensationType() == Sensation.SensationType.HearDirection:
            self.log('process: SensationType.HearDirection')      
             #inform external senses that we remember now hearing          
            self.out_axon.put(sensation)
            self.hearing_angle = sensation.getHearDirection()
            if self.calibrating:
                self.log("process: Calibrating hearing_angle " + str(self.hearing_angle) + " calibrating_angle " + str(self.calibrating_angle))      
            else:
                self.observation_angle = self.add_radian(original_radian=self.azimuth, added_radian=self.hearing_angle) # object in this angle
                self.log("process: create Sensation.SensationType.Observation")
                observation = Sensation(sensationType = Sensation.SensationType.Observation,
                                        memory=Memory.Work,
                                        observationDirection= self.observation_angle,
                                        observationDistance=Robot.DEFAULT_OBSERVATION_DISTANCE,
                                        reference=sensation)
                # process internally
                self.log("process: put Observation to in_axon")
                self.inAxon.put(observation)
                
                #process by remote robotes
                # mark hearing sensation to be processed to set direction out of memory, we forget it
                sensation.setDirection(Sensation.Direction.Out)
                observation.setDirection(Sensation.Direction.Out)
                #inform external senses that we don't remember hearing any more           
                self.log("process: put HearDirection to out_axon")
                self.out_axon.put(sensation)
                # seems that out_axon is handled when observation is processed internally here
                #self.log("process: put Observation to out_axon")
                #self.out_axon.put(observation)
        elif sensation.getSensationType() == Sensation.SensationType.Azimuth:
            if not self.calibrating:
                self.log('process: Sensation.SensationType.Azimuth')      
                #inform external senses that we remember now azimuth          
                #self.out_axon.put(sensation)
                self.azimuth = sensation.getAzimuth()
                self.turn()
        elif sensation.getSensationType() == Sensation.SensationType.Observation:
            if not self.calibrating:
                self.log('process: Sensation.SensationType.Observation')      
                #inform external senses that we remember now observation          
                self.observation_angle = sensation.getObservationDirection()
                self.turn()
                self.log("process: put Observation to out_axon")
                sensation.setDirection(Sensation.Direction.Out)
                self.out_axon.put(sensation)
        elif sensation.getSensationType() == Sensation.SensationType.ImageFilePath:
            self.log('process: Sensation.SensationType.ImageFilePath')      
        elif sensation.getSensationType() == Sensation.SensationType.Calibrate:
            self.log('process: Sensation.SensationType.Calibrate')      
            if sensation.getMemory() == Sensation.Memory.Working:
                if sensation.getDirection() == Sensation.Direction.In:
                    self.log('process: asked to start calibrating mode')      
                    self.calibrating = True
                else:
                    self.log('process: asked to stop calibrating mode')      
                    self.calibrating = False
                # ask external senses to to set same calibrating mode          
                self.out_axon.put(sensation)
            elif sensation.getMemory() == Sensation.Memory.Sensory:
                if self.config.canHear() and self.calibrating:
                    if self.turning_to_object:
                        print (self.name + ": Robotserver.process turning_to_object, can't start calibrate activity yet")
                    else:
                        # allow requester to start calibration activaties
                        if sensation.getDirection() == Sensation.Direction.In:
                            self.log('process: asked to start calibrating activity')      
                            self.calibrating_angle = sensation.getHearDirection()
                            self.hearing.setCalibrating(calibrating=True, calibrating_angle=self.calibrating_angle)
                            sensation.setDirection(Sensation.Direction.In)
                            self.log('process: calibrating put HearDirection to out_axon')      
                            self.out_axon.put(sensation)
                            #self.calibratingTimer = Timer(Robot.ACTION_TIME, self.stopCalibrating)
                            #self.calibratingTimer.start()
                        else:
                            self.log('process: asked to stop calibrating activity')      
                            self.hearing.setCalibrating(calibrating=False, calibrating_angle=self.calibrating_angle)
                            #self.calibratingTimer.cancel()
                else:
                    self.log('process: asked calibrating activity WITHOUT calibrate mode, IGNORED')      


        elif sensation.getSensationType() == Sensation.SensationType.Capability:
            self.log('process: Sensation.SensationType.Capability')      
        elif sensation.getSensationType() == Sensation.SensationType.Unknown:
            self.log('process: Sensation.SensationType.Unknown')
 
        # Just put sensation to our parent            
        self.outAxon.put(sensation)    
