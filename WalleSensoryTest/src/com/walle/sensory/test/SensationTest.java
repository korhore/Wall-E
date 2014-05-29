package com.walle.sensory.test;

import com.walle.sensory.server.Sensation;
import com.walle.sensory.server.Sensation.SensationType;

import junit.framework.TestCase;

public class SensationTest extends TestCase {

	public SensationTest(String name) {
		super(name);
	}

/*	
	public SensationTest() {
		super("com.walle.sensory", Sensation.class);
		}
*/
	
	protected void setUp() throws Exception {
		super.setUp();
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}
	
	public final void testSensation() {
		Sensation s = new Sensation("12 S I D 0.97 0.56");
		
		assertTrue("number should be 12", s.getNumber() == 12);
		assertTrue("SensationType should be Drive", s.getSensationType() == SensationType.Drive);
		assertEquals("LeftPower should be 0.97", 0.97f, s.getLeftPower(), 0.0001f);
		assertEquals("RightPower should be 0.56", 0.56f, s.getRightPower(), 0.0001f);
		
		s = new Sensation("13 S I S");
		assertEquals("number should be 13", 13, s.getNumber());
		assertTrue("SensationType should be Stop", s.getSensationType() == SensationType.Stop);

		s = new Sensation("14 S I W");
		assertEquals("number should be 14", 14, s.getNumber());
		assertTrue("SensationType should be Who", s.getSensationType() == SensationType.Who);

		s = new Sensation("15 S I H -0.75");
		assertEquals("number should be 15", 15, s.getNumber());
		assertTrue("SensationType should be Hear", s.getSensationType() == SensationType.HearDirection);
		assertEquals("Hear should be -0.75", -0.75f, s.getHearDirection(), 0.0001f);

		s = new Sensation("16 S I A 0.75");
		assertEquals("number should be 16", 16, s.getNumber());
		assertTrue("SensationType should be Azimuth", s.getSensationType() == SensationType.Azimuth);
		assertEquals("Azimuth should be 0.75", 0.75f, s.getAzimuth(), 0.0001f);

		s = new Sensation("17 S I G 0.75 1.75 2.75");
		assertEquals("number should be 17", 17, s.getNumber());
		assertTrue("SensationType should be Acceleration", s.getSensationType() == SensationType.Acceleration);
		assertEquals("AccelerationX be 0.75", 0.75f, s.getAccelerationX(), 0.0001f);
		assertEquals("AccelerationY be 1.75", 1.75f, s.getAccelerationY(), 0.0001f);
		assertEquals("AccelerationZ be 1.75", 2.75f, s.getAccelerationZ(), 0.0001f);


		s = new Sensation("16 W I O 0.75 5.5");
		assertEquals("number should be 16", 16, s.getNumber());
		assertTrue("SensationType should be Observatio", s.getSensationType() == SensationType.Observation);
		assertEquals("ObservationDirection should be 0.75", 0.75f, s.getObservationDirection(), 0.0001f);
		assertEquals("ObservationDistance should be 5.5", 5.5f, s.getObservationDistance(), 0.0001f);

		s = new Sensation("18 S I P 12300");
		assertEquals("number should be 18", 18, s.getNumber());
		assertTrue("SensationType should be Picture", s.getSensationType() == SensationType.Picture);
		assertEquals("ImageSize should be 12300", 12300, s.getImageSize());

		s = new Sensation("19 S I C H -0.75");
		assertEquals("number should be 19", 19, s.getNumber());
		assertTrue("SensationType should be Calibrate", s.getSensationType() == SensationType.Calibrate);
		assertTrue("Calibrate SensationType should be Hear", s.getCalibrateSensationType() == SensationType.HearDirection);
		assertEquals("Hear should be -0.75", -0.75f, s.getHearDirection(), 0.0001f);

		// Calibrate tests for sensation types that are not supported yet
		s = new Sensation("20 S I C O -0.75");
		assertEquals("number should be 20", 20, s.getNumber());
		assertTrue("SensationType should be Unknown", s.getSensationType() == SensationType.Unknown);


		try
		{
			s = new Sensation("18 oho");
		    fail("Should have thrown IllegalArgumentException");
		 }
		 catch(IllegalArgumentException e)
		 {
		    //success
		 }
	}
	
	/*

	public final void testSensationIntSensationType() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSensationIntSensationTypeFloatFloat() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSensationIntSensationTypeFloat() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSensationIntSensationTypeDirectionSensationTypeArray() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSensationString() {
		fail("Not yet implemented"); // TODO
	}

	public final void testToString() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetNumber() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetNumber() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetSensationType() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetSnsationType() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetLeftPower() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetLeftPower() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetRightPower() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetRightPower() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetHear() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetHear() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetAzimuth() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetAzimuth() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetImageSize() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetImageSize() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetDirection() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetDirection() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetCapabilities() {
		fail("Not yet implemented"); // TODO
	}

	public final void testGetStrCapabilities() {
		fail("Not yet implemented"); // TODO
	}

	public final void testSetCapabilities() {
		fail("Not yet implemented"); // TODO
	}

	public final void testToString1() {
		fail("Not yet implemented"); // TODO
	}
*/
}
