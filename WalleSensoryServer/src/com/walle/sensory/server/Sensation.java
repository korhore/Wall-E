package com.walle.sensory.server;


import android.util.Log;


public class Sensation extends Object {
	final String LOGTAG="Sensation";

	public final static int SENSATION_LENGTH_SIZE = 2;
	public final static int SENSATION_MAX_LENGTH = 99;
	public final static String SENSATION_LENGTH_FORMAT = "%2d";

	public final static String  SENSATION_SEPRATOR = "|";
	public final static int SENSATION_SEPRATOR_SIZE = 1;

	private int m_number;
	private SensationType m_sensationType;
	private Memory m_memory;
	private Direction m_direction;
	private float m_leftPower;
	private float m_rightPower;
	private float m_hearDirection;
	private float m_azimuth;
	private float m_accelerationX;
	private float m_accelerationY;
	private float m_accelerationZ;
	private float m_observationDirection;
	private float m_observationDistance;
	private int m_imageSize;
	private SensationType m_calibrateSensationType;
	private SensationType[] m_capabilities;

    public enum SensationType {
    	Drive("D"),
    	Stop("S"),
    	Who("W"),
    	HearDirection("H"),
    	Azimuth("A"),
    	Acceleration("G"),
    	Observation("O"),
    	Picture("P"),
    	Calibrate("C"),
    	Capability("1"),
    	Unknown("U") 	;

    	private String text;

    	SensationType(String text) {
    		this.text = text;
    	}

    	public String getText() {
    		return this.text;
    	}

    	public static SensationType fromString(String text) {
    		if (text != null) {
    			for (SensationType s : SensationType.values()) {
    				if (text.equalsIgnoreCase(s.text)) {
    					return s;
    				}
    			}
    	    }
    		throw new IllegalArgumentException("No constant with text " + text + " found");
    	}
    }
    
    public enum Direction {
    	In("I"),
    	Out("O");

    	private String text;

    	Direction(String text) {
    		this.text = text;
    	}

    	public String getText() {
    		return this.text;
    	}

    	public static Direction fromString(String text) {
    		if (text != null) {
    			for (Direction d : Direction.values()) {
    				if (text.equalsIgnoreCase(d.text)) {
    					return d;
    				}
    			}
    		}
    		throw new IllegalArgumentException("No constant with text " + text + " found");
    	}
    }
 
    public enum Memory {
    	Sensory("S"),
    	Working("W"),
    	LongTerm("L");

    	private String text;

    	Memory(String text) {
    		this.text = text;
    	}

    	public String getText() {
    		return this.text;
    	}

    	public static Memory fromString(String text) {
    		if (text != null) {
    			for (Memory m : Memory.values()) {
    				if (text.equalsIgnoreCase(m.text)) {
    					return m;
    				}
    			}
    		}
    		throw new IllegalArgumentException("No constant with text " + text + " found");
    	}
    }

    /**
     * Constructors
     */
    
    public Sensation( int a_number,
					  Memory a_memory,
					  Direction a_direction,
					  SensationType a_sensationType) {

		if ((a_sensationType == SensationType.Stop) ||
			(a_sensationType == SensationType.Who)) {
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_memory = a_memory;
	    	m_direction = a_direction;

	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	m_hearDirection = 0.0f;
	    	m_azimuth = 0.0f;
	    	m_accelerationX = 0.0f;
	    	m_accelerationY = 0.0f;
	    	m_accelerationZ = 0.0f;
	    	m_observationDirection = 0.0f;
	    	m_observationDistance = -1.0f;
	    	m_imageSize = 0;
	    	m_calibrateSensationType = SensationType.Unknown;
	    	m_capabilities = null;
		} else {
			throw new IllegalArgumentException();
		}
	}
    
    public Sensation(	int a_number,
						Memory a_memory,
						Direction a_direction,
						SensationType a_sensationType,
						float a_value_1,
						float a_value_2 ) {

    	if ((a_sensationType == SensationType.Drive) || (a_sensationType == SensationType.Observation)){
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_memory = a_memory;
	    	m_direction = a_direction;
	    	m_leftPower = a_value_1;
	    	m_rightPower = a_value_2;
	    	m_hearDirection = 0.0f;
	    	m_azimuth = 0.0f;
	    	m_accelerationX = 0.0f;
	    	m_accelerationY = 0.0f;
	    	m_accelerationZ = 0.0f;
	    	m_observationDirection = 0.0f;
	    	m_observationDistance = -1.0f;
	    	m_imageSize = 0;
	    	m_calibrateSensationType = SensationType.Unknown;
	    	m_capabilities = null;
	    	if (a_sensationType == SensationType.Drive) {
		    	m_leftPower = a_value_1;
		    	m_rightPower = a_value_2;
		    	m_observationDirection = 0.0f;
		    	m_observationDistance = -1.0f;
	    	}
	    	else {
		    	m_leftPower = 0.0f;
		    	m_rightPower = 0.0f;
		    	m_observationDirection = a_value_1;
		    	m_observationDistance = a_value_2;
	    	}
    	} else {
    		throw new IllegalArgumentException();
    	}
    }

    public Sensation(	int a_number,
						Memory a_memory,
						Direction a_direction,
						SensationType a_sensationType,
						float a_value) {

		if ((a_sensationType == SensationType.HearDirection) ||
			(a_sensationType == SensationType.Azimuth)){
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_memory = a_memory;
	    	m_direction = a_direction;
	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	m_accelerationX = 0.0f;
	    	m_accelerationY = 0.0f;
	    	m_accelerationZ = 0.0f;
	    	m_observationDirection = 0.0f;
	    	m_observationDistance = -1.0f;
	    	m_imageSize = 0;
	    	m_calibrateSensationType = SensationType.Unknown;
	    	m_capabilities = null;
	    	if (a_sensationType == SensationType.HearDirection) {
		    	m_hearDirection = a_value;
		    	m_azimuth = 0.0f;
	    	} else {
		    	m_hearDirection = 0.0f;
		    	m_azimuth = a_value;
	    	}
		} else {
			throw new IllegalArgumentException();
		}
	}

    public Sensation(	int a_number,
			Memory a_memory,
			Direction a_direction,
			SensationType a_sensationType,
			float a_accelerationX,
			float a_accelerationY,
			float a_accelerationZ ) {

		if (a_sensationType == SensationType.Acceleration) {
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_memory = a_memory;
	    	m_direction = a_direction;
	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	m_hearDirection = 0.0f;
	    	m_azimuth = 0.0f;
	    	m_accelerationX = a_accelerationX;
	    	m_accelerationY = a_accelerationY;
	    	m_accelerationZ = a_accelerationZ;
	    	m_observationDirection = 0.0f;
	    	m_observationDistance = -1.0f;
	    	m_imageSize = 0;
	    	m_calibrateSensationType = SensationType.Unknown;
	    	m_capabilities = null;
		} else {
			throw new IllegalArgumentException();
		}
    }
    
    public Sensation(	int a_number,
			Memory a_memory,
			Direction a_direction,
			SensationType a_sensationType,
			SensationType a_calibrateSensationType,
			float a_value) {

    	if (a_calibrateSensationType == SensationType.HearDirection) {
			m_number = a_number;
			m_sensationType = a_sensationType;
			m_memory = a_memory;
			m_direction = a_direction;
			m_leftPower = 0.0f;
			m_rightPower = 0.0f;
			m_accelerationX = 0.0f;
			m_accelerationY = 0.0f;
			m_accelerationZ = 0.0f;
			m_observationDirection = 0.0f;
			m_observationDistance = -1.0f;
			m_imageSize = 0;
			m_calibrateSensationType = a_calibrateSensationType;
			m_capabilities = null;
			m_azimuth = 0.0f;
			m_hearDirection = a_value;
    	} else {
    		throw new IllegalArgumentException();
    	}
    }


    public Sensation(	int a_number,
						Memory a_memory,
						Direction a_direction,
						SensationType a_sensationType,
						SensationType[] a_capabilities) {

		if (a_sensationType == SensationType.Capability) {
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_memory = a_memory;
	    	m_direction = a_direction;
	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	m_hearDirection = 0.0f;
		    m_azimuth = 0.0f;
	    	m_accelerationX = 0.0f;
	    	m_accelerationY = 0.0f;
	    	m_accelerationZ = 0.0f;
	    	m_observationDirection = 0.0f;
	    	m_observationDistance = -1.0f;
	    	m_imageSize = 0;
	    	m_calibrateSensationType = SensationType.Unknown;
	    	m_capabilities = a_capabilities;
		} else {
			throw new IllegalArgumentException();
		}
	}

    public Sensation( String a_string ) {
    	
    	m_number = 0;
		m_sensationType = SensationType.Unknown;
    	m_memory = Memory.Sensory;
    	m_direction = Direction.In;
		m_leftPower = 0.0f;
		m_rightPower = 0.0f;
		m_hearDirection = 0.0f;
		m_azimuth = 0.0f;
    	m_accelerationX = 0.0f;
    	m_accelerationY = 0.0f;
    	m_accelerationZ = 0.0f;
    	m_observationDirection = 0.0f;
    	m_observationDistance = -1.0f;
		m_imageSize = 0;
    	m_calibrateSensationType = SensationType.Unknown;
		m_capabilities = null;
		
		boolean success=false;


        String params[] = a_string.split(" ");
        if (params.length >= 3) {
       		m_number = Integer.parseInt(params[0]);
       		//Log.d(LOGTAG, String.valueOf(m_number));
			m_memory = Memory.fromString(params[1]);
       		//Log.d(LOGTAG, m_memory.toString());
			m_direction = Direction.fromString(params[2]);
       		//Log.d(LOGTAG, m_direction.toString());
          
            if (params.length >= 4) {
           		m_sensationType = SensationType.fromString(params[3]);
           		if (m_sensationType == SensationType.Drive) {
           			if (params.length >= 5) {
           				m_leftPower = Float.parseFloat(params[4]);
           				//Log.d(LOGTAG, String.valueOf(m_leftPower));
           			}
           			if (params.length >= 6) {
           				m_rightPower = Float.parseFloat(params[5]);
           				success=true;
           				//Log.d(LOGTAG, String.valueOf(m_rightPower));
           			}
           		} else if (m_sensationType == SensationType.HearDirection) {
           			if (params.length >= 5) {
           				m_hearDirection = Float.parseFloat(params[4]);
           				success=true;
           				//Log.d(LOGTAG, String.valueOf(m_hearDirection));
           			}
           		} else if (m_sensationType == SensationType.Azimuth) {
           			if (params.length >= 5) {
           				m_azimuth = Float.parseFloat(params[4]);
           				success=true;
           				//Log.d(LOGTAG, String.valueOf(m_azimuth));
           			}
           		} else if (m_sensationType == SensationType.Acceleration) {
           			if (params.length >= 5) {
           				m_accelerationX = Float.parseFloat(params[4]);
           				//Log.d(LOGTAG, String.valueOf(m_accelerationX));
           			}
           			if (params.length >= 6) {
           				m_accelerationY = Float.parseFloat(params[5]);
           				//Log.d(LOGTAG, String.valueOf(m_accelerationY));
           			}
           			if (params.length >= 7) {
           				m_accelerationZ = Float.parseFloat(params[6]);
           				success=true;
           				//Log.d(LOGTAG, String.valueOf(m_accelerationZ));
           			}
           		} else if (m_sensationType == SensationType.Observation) {
           			if (params.length >= 5) {
           				this.m_observationDirection = Float.parseFloat(params[4]);
           				//Log.d(LOGTAG, String.valueOf(this.m_observationDirection));
           			}
           			if (params.length >= 6) {
           				this.m_observationDistance = Float.parseFloat(params[5]);
           				success=true;
          				//Log.d(LOGTAG, String.valueOf(this.m_observationDistance));
           			}
           		} else if (m_sensationType == SensationType.Picture) {
           			if (params.length >= 5) {
           				m_imageSize = Integer.parseInt(params[4]);
           				success=true;
           				//Log.d(LOGTAG, String.valueOf(m_imageSize));
           			}
           		} else if (m_sensationType == SensationType.Calibrate) {
           			if (params.length >= 6) {
           				m_calibrateSensationType = SensationType.fromString(params[4]);
           				if (m_calibrateSensationType == SensationType.HearDirection) {
           					m_hearDirection = Float.parseFloat(params[5]);
           					success=true;
	           				//Log.d(LOGTAG, String.valueOf(m_hearDirection));
           				}
           			}
            	} else if (m_sensationType == SensationType.Capability) {
           			if (params.length >= 5) {
           				m_capabilities = new SensationType[params.length -4];
           				for (int i = 4; i < params.length; i++)
           					m_capabilities[i-4] = SensationType.fromString(params[i]);
           				success=true;
           			}
           		} else if ((m_sensationType == SensationType.Stop) || (m_sensationType == SensationType.Who)){
           			success=true;
           		}
       		}
         } else {
			throw new IllegalArgumentException();
		}
      
		if (!success) {
			m_sensationType = SensationType.Unknown;
		}


    }
        
        /**
         * toString
         */
        
        
    public String toString() {
        if (this.m_sensationType == SensationType.Drive)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' +  ' ' + Float.toString(this.m_leftPower) +  ' ' + Float.toString(this.m_rightPower);
        else if (this.m_sensationType == SensationType.HearDirection)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + Float.toString(this.m_hearDirection);
        else if (this.m_sensationType == SensationType.Azimuth)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + Float.toString(this.m_azimuth);
        else if (this.m_sensationType == SensationType.Acceleration)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + Float.toString(this.m_accelerationX) + ' ' + Float.toString(this.m_accelerationY) + ' ' + Float.toString(this.m_accelerationZ);
        else if (this.m_sensationType == SensationType.Observation)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + Float.toString(this.m_observationDirection) + ' ' + Float.toString(this.m_observationDistance);
        else if (this.m_sensationType == SensationType.Picture)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + Integer.toString(this.m_imageSize);
        else if (this.m_sensationType == SensationType.Calibrate) {
        	if (this.m_calibrateSensationType == SensationType.HearDirection)
        		return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + this.m_calibrateSensationType.getText() + ' '+ Float.toString(this.m_hearDirection);
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + SensationType.Unknown.getText();
        }
        else if (this.m_sensationType == SensationType.Capability)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText() + ' ' + this.m_direction +  ' ' + this.getStrCapabilities();
        else if (this.m_sensationType == SensationType.Stop)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText();
        else if (this.m_sensationType == SensationType.Who)
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText();
        else
            return Integer.toString(this.m_number) + ' ' + this.m_memory.getText() + ' ' + this.m_direction.getText() + ' ' + this.m_sensationType.getText();
        	
    }

	public int getNumber() {
		return m_number;
	}

	public void setNumber(int a_number) {
		this.m_number = a_number;
	}

	public SensationType getSensationType() {
		return m_sensationType;
	}

	public void setSensationType(SensationType a_sensationType) {
		this.m_sensationType = a_sensationType;
	}

	public float getLeftPower() {
		return m_leftPower;
	}

	public void setLeftPower(float a_leftPower) {
		this.m_leftPower = a_leftPower;
	}

	public float getRightPower() {
		return m_rightPower;
	}

	public void setRightPower(float a_rightPower) {
		this.m_rightPower = a_rightPower;
	}

	public float getHearDirection() {
		return m_hearDirection;	
	}

	public void setHearDirection(float a_hearDirection) {
		this.m_hearDirection = a_hearDirection;
	}

	public float getAzimuth() {
		return m_azimuth;
	}

	public void setAzimuth(float a_azimuth) {
		this.m_azimuth = a_azimuth;
	}

	public float getAccelerationX() {
		return m_accelerationX;
	}

	public void setAccelerationX(float a_accelerationX) {
		this.m_accelerationX = a_accelerationX;
	}

	public float getAccelerationY() {
		return m_accelerationY;
	}

	public void setAccelerationY(float a_accelerationY) {
		this.m_accelerationY = a_accelerationY;
	}

	public float getAccelerationZ() {
		return m_accelerationZ;
	}

	public void setAccelerationZ(float a_accelerationZ) {
		this.m_accelerationZ = a_accelerationZ;
	}

	public float getObservationDirection() {
		return m_observationDirection;	
	}

	public void setObservationDirection(float a_observationDirection) {
		this.m_observationDirection = a_observationDirection;
	}
	
	public float getObservationDistance() {
		return m_observationDistance;	
	}

	public void setObservationDistance(float a_observationDistance) {
		this.m_observationDistance = a_observationDistance;
	}


	public int getImageSize() {
		return m_imageSize;
	}

	public void setImageSize(int a_imageSize) {
		this.m_imageSize = a_imageSize;
	}

	public SensationType getCalibrateSensationType() {
		return m_calibrateSensationType;
	}

	public void setCalibrateSensationType(SensationType a_sensationType) {
		this.m_calibrateSensationType = a_sensationType;
	}

	public Direction getDirection() {
		return m_direction;
	}

	public void setDirection(Direction a_direction) {
		this.m_direction = a_direction;
	}

	public SensationType[] getCapabilities() {
		return m_capabilities;
	}
	
	public String getStrCapabilities() {
        String capabilities = "";
        for (int i=0; i < m_capabilities.length; i++)
            capabilities += " " + m_capabilities[i];
        return capabilities;
	}


	public void setCapabilities(SensationType[] a_capabilities) {
		this.m_capabilities = a_capabilities;
	}


	/*
	 * '''
Created on Feb 25, 2013

@author: Reijo Korhonen, reijo.korhonen@gmail.com
'''
def enum(**enums):
    return type('Enum', (), enums)

class Sensation(object):
    
    SensationTypes = enum(Drive='D', Stop='S', Who='W', HearDirection='H', Azimuth='A', Picture='P', Capability='C', Unknown='U')
    Direction = enum(In='I', Out='O')
   
    def __init__(self, string="",
                 number=-1, sensation = 'U', leftPower = 0.0, rightPower = 0.0, hearDirection = 0.0, azimuth = 0.0, imageSize=0,
                 direction='I', capabilities = []):
        self.number = number
        self.sensation = sensation
        self.leftPower = leftPower
        self.rightPower = rightPower
        self.hearDirection = hearDirection
        self.azimuth = azimuth
        self.imageSize = imageSize
        self.direction = direction
        self.capabilities = capabilities
       
        params = string.split()
        print params
        if len(params) >= 1:
            try:
                self.number = int(params[0])
            except (ValueError):
                self.sensation = Sensation.SensationTypes.Unknown
                return
                
            print self.number
            if len(params) >= 2:
                sensation = params[1]
                if sensation == Sensation.SensationTypes.Drive:
                    self.sensation = Sensation.SensationTypes.Drive
                    if len(params) >= 3:
                        self.leftPower = float(params[2])
                        print str(self.leftPower)
                    if len(params) >= 4:
                        self.rightPower = float(params[3])
                        print str(self.rightPower)
                elif sensation == Sensation.SensationTypes.HearDirection:
                    self.sensation = Sensation.SensationTypes.HearDirection
                    if len(params) >= 3:
                        self.hearDirection = float(params[2])
                        print str(self.hearDirection)
                elif sensation == Sensation.SensationTypes.Azimuth:
                    self.sensation = Sensation.SensationTypes.Azimuth
                    if len(params) >= 3:
                        self.azimuth = float(params[2])
                        print str(self.azimuth)
                elif sensation == Sensation.SensationTypes.Picture:
                    self.sensation = Sensation.SensationTypes.Picture
                    if len(params) >= 3:
                        self.imageSize = int(params[2])
                        print str(self.imageSize)
                elif sensation == Sensation.SensationTypes.Capability:
                    self.sensation = Sensation.SensationTypes.Capability
                    if len(params) >= 3:
                        self.direction = params[2]
                        print str(self.direction)
                    if len(params) >= 4:
                        self.capabilities = params[3:]
                        print str(self.capabilities)
    
                elif sensation == Sensation.SensationTypes.Stop:
                    self.sensation = Sensation.SensationTypes.Stop
                elif sensation == Sensation.SensationTypes.Who:
                    self.sensation = Sensation.SensationTypes.Who
                else:
                    self.sensation = Sensation.SensationTypes.Unknown
                print self.sensation
            
    def __str__(self):
        if self.sensation == Sensation.SensationTypes.Drive:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.leftPower) +  ' ' + str(self.rightPower)
        elif self.sensation == Sensation.SensationTypes.HearDirection:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.hearDirection)
        elif self.sensation == Sensation.SensationTypes.Azimuth:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.azimuth)
        elif self.sensation == Sensation.SensationTypes.Picture:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.imageSize)
        elif self.sensation == Sensation.SensationTypes.Capability:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.direction) +  ' ' + self.getStrCapabilities()
        elif self.sensation == Sensation.SensationTypes.Stop:
            return str(self.number) + ' ' + self.sensation
        elif self.sensation == Sensation.SensationTypes.Who:
            return str(self.number) + ' ' + self.sensation
        else:
            return str(self.number) + ' ' + self.sensation

    def setNumber(self, number):
        self.number = number
    def getNumber(self):
        return self.number
 
    def setSensation(self, sensation):
        self.sensation = sensation
    def getSensation(self):
        return self.sensation
       
    def setLeftPower(self, leftPower):
        self.leftPower = leftPower
    def getLeftPower(self):
        return self.leftPower
        
    def setRightPower(self, rightPower):
        self.rightPower = rightPower
    def getRightPower(self):
        return self.rightPower
    
    def setHearDirection(self, hearDirection):
        self.hearDirection = hearDirection
    def getHearDirection(self):
        return self.hearDirection

    def setAzimuth(self, azimuth):
        self.azimuth = azimuth
    def getAzimuth(self):
        return self.azimuth

    def setImageSize(self, imageSize):
        self.imageSize = imageSize
    def getImageSize(self):
        return self.imageSize
    

    def setCapabilities(self, capabilities):
        self.capabilities = capabilities
    def getCmageSize(self):
        return self.capabilities
    def setStrCapabilities(self, string):
        str_capabilities = string.split()
        self.capabilities=[]
        for capability in str_capabilities:
            self.capabilities.add(capability)
        self.capabilities = capabilities
    def getStrCapabilities(self):
        capabilities = ""
        for capability in self.capabilities:
            capabilities += ' ' + str(capability)
        return capabilities

        
if __name__ == '__main__':
    c=Sensation(string="12 D 0.97 0.56")
    print "str " + str(c)
    c=Sensation(string="13 S")
    print "str " + str(c)
    c=Sensation(string="13 W")
    print "str " + str(c)
    c=Sensation(string="14 H -0.75")
    print "str " + str(c)
    c=Sensation(string="15 A 0.75")
    print "str " + str(c)
    c=Sensation(string="16 P 12300")
    print "str " + str(c)
    c=Sensation(string="17 oho")
    print "str " + str(c)
    c=Sensation(string="hupsis oli")
    print "str " + str(c)
    
    c=Sensation(number=99, sensation = 'D', leftPower = 0.77, rightPower = 0.55)
    print "D str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))
    
    c=Sensation(number=100, sensation = 'H', hearDirection = 0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=101, sensation = 'A', azimuth = -0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=102, sensation = 'C', direction = 'O', capabilities = [Sensation.SensationTypes.Drive, Sensation.SensationTypes.HearDirection, Sensation.SensationTypes.Azimuth])
    print "C str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

	 */
	
	/**
	 * Unit tests
	 */
	
	

}
