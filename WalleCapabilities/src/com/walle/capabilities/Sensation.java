package com.walle.capabilities;

import android.util.Log;

public class Sensation {
	final String LOGTAG="Sensation";
	
	private int m_number;
	private SensationType m_sensationType;
	private float m_leftPower;
	private float m_rightPower;
	private float m_hear;
	private float m_azimuth;
	private int m_imageSize;
	private Direction m_direction;
	private SensationType[] m_capabilities;

//    enum SensationTypes {Drive='D', Stop='S', Who='W', Hear='H', Azimuth='A', Picture='P', Capability='C', Unknown='U'};
//    enum SensationTypes {Drive, Stop, Who, Hear, Azimuth, Picture, Capability, Unknown};
//    public enum  Direction {Input("I"), Output=("O")};
//    public enum  Direction {Input, Output};
    public enum SensationType {
    	Drive("D"),
    	Stop("S"),
    	Who("W"),
    	Hear("H"),
    	Azimuth("A"),
    	Picture("P"),
    	Capability("C"),
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
    	Input("I"),
    	Output("O");

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
    
    /**
     * Constructors
     */
    
    public Sensation( int a_number,
					  SensationType a_sensationType) {

		if ((a_sensationType == SensationType.Stop) ||
			(a_sensationType == SensationType.Who)){
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	m_hear = 0.0f;
	    	m_azimuth = 0.0f;
	    	m_imageSize = 0;
	    	m_direction = Direction.Input;
	    	m_capabilities = null;
		} else {
			throw new IllegalArgumentException();
		}
	}
    
    public Sensation(	int a_number,
    			SensationType a_sensationType,
    			float a_leftPower,
    			float a_rightPower ) {

    	if (a_sensationType == SensationType.Drive) {
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_leftPower = a_leftPower;
	    	m_rightPower = a_rightPower;
	    	m_hear = 0.0f;
	    	m_azimuth = 0.0f;
	    	m_imageSize = 0;
	    	m_direction = Direction.Input;
	    	m_capabilities = null;
    	} else {
    		throw new IllegalArgumentException();
    	}
    }

    public Sensation(	int a_number,
				SensationType a_sensationType,
				float a_value) {

		if ((a_sensationType == SensationType.Hear) ||
			(a_sensationType == SensationType.Azimuth)){
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	if (a_sensationType == SensationType.Hear) {
		    	m_hear = a_value;
		    	m_azimuth = 0.0f;
	    	} else {
		    	m_hear = 0.0f;
		    	m_azimuth = a_value;
	    	}
	    	m_imageSize = 0;
	    	m_direction = Direction.Input;
	    	m_capabilities = null;
		} else {
			throw new IllegalArgumentException();
		}
	}

    public Sensation(	int a_number,
				SensationType a_sensationType,
				Direction a_direction,
				SensationType[] a_capabilities) {

		if (a_sensationType == SensationType.Capability) {
	    	m_number = a_number;
	    	m_sensationType = a_sensationType;
	    	m_leftPower = 0.0f;
	    	m_rightPower = 0.0f;
	    	m_hear = 0.0f;
		    m_azimuth = 0.0f;
	    	m_imageSize = 0;
	    	m_direction = a_direction;
	    	m_capabilities = a_capabilities;
		} else {
			throw new IllegalArgumentException();
		}
	}

    public Sensation( String a_string ) {
    	
    	m_number = 0;
		m_sensationType = SensationType.Unknown;
		m_leftPower = 0.0f;
		m_rightPower = 0.0f;
		m_hear = 0.0f;
		m_azimuth = 0.0f;
		m_imageSize = 0;
		m_direction = Direction.Input;
		m_capabilities = null;

        String params[] = a_string.split(" ");
        System.out.println(params.toString());
        Log.d(LOGTAG, params.toString());
        if (params.length >= 1) {
       		m_number = Integer.parseInt(params[0]);
            System.out.println(m_number);
            
            if (params.length >= 2) {
           		m_sensationType = SensationType.fromString(params[1]);
           		if (m_sensationType == SensationType.Drive) {
           			if (params.length >= 3) {
           				m_leftPower = Float.parseFloat(params[2]);
           				System.out.println(m_leftPower);
           			}
           			if (params.length >= 4) {
           				m_rightPower = Float.parseFloat(params[3]);
           				System.out.println(m_rightPower);
           			}
           		} else if (m_sensationType == SensationType.Hear) {
           			if (params.length >= 3) {
           				m_hear = Float.parseFloat(params[2]);
           				System.out.println(m_hear);
           			}
           		} else if (m_sensationType == SensationType.Azimuth) {
           			if (params.length >= 3) {
           				m_azimuth = Float.parseFloat(params[2]);
           				System.out.println(m_azimuth);
           			}
           		} else if (m_sensationType == SensationType.Picture) {
           			if (params.length >= 3) {
           				m_imageSize = Integer.parseInt(params[2]);
           				System.out.println(m_imageSize);
           			}
           		} else if (m_sensationType == SensationType.Capability) {
           			if (params.length >= 3) {
           				m_direction = Direction.fromString(params[2]);
               			System.out.println(m_direction);
           			}
           			if (params.length >= 4) {
           				m_capabilities = new SensationType[params.length -3];
           				for (int i = 3; i < params.length; i++)
           					m_capabilities[i-3] = SensationType.fromString(params[i]);
           			}
           		}
           	}
        }
    }
        
        /**
         * toString
         */
        
        
    public String toString() {
        if (this.m_sensationType == SensationType.Drive)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType.toString() + ' ' +  ' ' + Float.toString(this.m_leftPower) +  ' ' + Float.toString(this.m_rightPower);
        else if (this.m_sensationType == SensationType.Hear)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType + ' ' + Float.toString(this.m_hear);
        else if (this.m_sensationType == SensationType.Azimuth)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType + ' ' + Float.toString(this.m_azimuth);
        else if (this.m_sensationType == SensationType.Picture)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType + ' ' + Integer.toString(this.m_imageSize);
        else if (this.m_sensationType == SensationType.Capability)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType + ' ' + this.m_direction +  ' ' + this.getStrCapabilities();
        else if (this.m_sensationType == SensationType.Stop)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType;
        else if (this.m_sensationType == SensationType.Who)
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType;
        else
            return Integer.toString(this.m_number) + ' ' + this.m_sensationType;
        	
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

	public void setSnsationType(SensationType a_sensationType) {
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

	public float getHear() {
		return m_hear;	
	}

	public void setHear(float a_hear) {
		this.m_hear = a_hear;
	}

	public float getAzimuth() {
		return m_azimuth;
	}

	public void setAzimuth(float a_azimuth) {
		this.m_azimuth = a_azimuth;
	}

	public int getImageSize() {
		return m_imageSize;
	}

	public void setImageSize(int a_imageSize) {
		this.m_imageSize = a_imageSize;
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
    
    SensationTypes = enum(Drive='D', Stop='S', Who='W', Hear='H', Azimuth='A', Picture='P', Capability='C', Unknown='U')
    Direction = enum(Input='I', Output='O')
   
    def __init__(self, string="",
                 number=-1, sensation = 'U', leftPower = 0.0, rightPower = 0.0, hear = 0.0, azimuth = 0.0, imageSize=0,
                 direction='I', capabilities = []):
        self.number = number
        self.sensation = sensation
        self.leftPower = leftPower
        self.rightPower = rightPower
        self.hear = hear
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
                elif sensation == Sensation.SensationTypes.Hear:
                    self.sensation = Sensation.SensationTypes.Hear
                    if len(params) >= 3:
                        self.hear = float(params[2])
                        print str(self.hear)
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
        elif self.sensation == Sensation.SensationTypes.Hear:
            return str(self.number) + ' ' + self.sensation + ' ' + str(self.hear)
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
    
    def setHear(self, hear):
        self.hear = hear
    def getHear(self):
        return self.hear

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
    
    c=Sensation(number=100, sensation = 'H', hear = 0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=101, sensation = 'A', azimuth = -0.85)
    print "A str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

    c=Sensation(number=102, sensation = 'C', direction = 'O', capabilities = [Sensation.SensationTypes.Drive, Sensation.SensationTypes.Hear, Sensation.SensationTypes.Azimuth])
    print "C str " + str(c)
    print "str(Sensation(str(c))) " + str(Sensation(string=str(c)))

	 */
	
	/**
	 * Unit tests
	 */
	
	

}
