package com.walle.capabilities;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;

import android.app.Activity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.view.Menu;
import android.widget.EditText;

public class CapabilitiesActivity extends Activity implements SensorEventListener {
	final private float kFilteringFactor = 0.1f;
	
    private EditText mHostField;
    private EditText mPortField;
    private EditText mAzimuthField;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mMagnetometer;

    private float[] mGravity;
	private float[] mGeomagnetic;
	private float mAzimuth;

	 Socket mSocket = null;
	 DataOutputStream mDataOutputStream = null;
	 DataInputStream mDataInputStream = null;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_capabilities);
		
	    mHostField = (EditText)findViewById(R.id.host_field);
	    mPortField = (EditText)findViewById(R.id.port_field);
	    mAzimuthField = (EditText)findViewById(R.id.azimuth_field);
	    
	    mGravity = new float[3] ;
		mGeomagnetic = new float[3];
    	for (int i=0; i<3; i++)
    	{
    		mGravity[i] = 0.0f;
    		mGeomagnetic[i] = 0.0f;
    	}

	    
	    mSensorManager = (SensorManager)getSystemService(SENSOR_SERVICE);
	    mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
	    mMagnetometer = mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
	    
	    try {
	    	  mSocket = new Socket("127.0.0.1", 8888);
	    	  mDataInputStream = new DataInputStream(mSocket.getInputStream());
	    	  mDataOutputStream = new DataOutputStream(mSocket.getOutputStream());
	    	  /*
	    	  mDataOutputStream.writeUTF(textOut.getText().toString());
	    	  textIn.setText(mDataInputStream.readUTF());*/
	    	 } catch (UnknownHostException e) {
	    	  // TODO Auto-generated catch block
	    	  e.printStackTrace();
	    	 } catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			 }


	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.capabilities, menu);
		return true;
	}
	
	protected void onResume() {
	    super.onResume();
	    mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_NORMAL);
	    mSensorManager.registerListener(this, mMagnetometer, SensorManager.SENSOR_DELAY_NORMAL);
	}
		 
	protected void onPause() {
	    super.onPause();
	    mSensorManager.unregisterListener(this);
	}
	
	protected void onDestroy() {
		super.onDestroy();
		if (mSocket != null) {
			try {
			    mSocket.close();
			} catch (IOException e) {
			    // TODO Auto-generated catch block
			    e.printStackTrace();
			}
		}

		if (mDataOutputStream != null) {
			try
			{
				mDataOutputStream.close();
		    } catch (IOException e) {
		    	// TODO Auto-generated catch block
		    	e.printStackTrace();
		    }

		}
		if (mDataInputStream != null) {
			try {
				mDataInputStream.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
		 
		 
		  
	@Override
	public void onSensorChanged(SensorEvent event) {
	    if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER)
	    {
	    	for (int i=0; i<3; i++)
	    	{
	    		mGravity[i] = ((1.0f - kFilteringFactor ) * mGravity[i]) + (kFilteringFactor  * event.values[i]);
	    	}
	    	//mGravity=event.values;
	    }
	    if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD)
	    {
	    	for (int i=0; i<3; i++)
		    {
	    		mGeomagnetic[i] = ((1.0f - kFilteringFactor ) * mGeomagnetic[i]) + (kFilteringFactor  * event.values[i]);
		    }
	    	//mGeomagnetic=event.values;
		}

	      if (mGravity != null && mGeomagnetic != null) {
	      float R[] = new float[9];
	      float I[] = new float[9];
	      boolean success = SensorManager.getRotationMatrix(R, I, mGravity, mGeomagnetic);
	      if (success) {
	        float orientation[] = new float[3];
	        SensorManager.getOrientation(R, orientation);
	        mAzimuth = orientation[0]; // orientation contains: azimuth, pitch and roll
	        // update azimuth field
	        mAzimuthField.setText(String.format("%8.3f", Math.toDegrees(mAzimuth)));
	        reportAzimuth(mAzimuth);
	      }
	    }
	}

	@Override
	public void onAccuracyChanged(Sensor sensor, int accuracy) {
		// TODO Auto-generated method stub
		
	}
	
	private void reportAzimuth(float aAzimuth) {
		try {
			mDataOutputStream.writeUTF(String.format("%8.3f", Math.toDegrees(aAzimuth)));
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			mDataInputStream.readUTF();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}
	


}
