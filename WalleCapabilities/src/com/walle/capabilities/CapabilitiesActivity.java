package com.walle.capabilities;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.PowerManager;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.EditText;
import android.widget.TextView;

public class CapabilitiesActivity extends Activity implements SensorEventListener {
	final String LOGTAG="CapabilitiesActivity";

	final private float kFilteringFactor = 0.1f;
	final private int PORT = 2000;
	final private String HOST = "10.0.0.55";
	//final private String HOST = "10.0.0.17";
	final private float kAccuracyFactor = (float)(Math.PI * 5.0)/180.0f;
	

    private TextView mAzimuthField;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mMagnetometer;
    
    private PowerManager mPowerManager;
    private PowerManager.WakeLock mWakeLock;

    private float[] mGravity;
	private float[] mGeomagnetic;
	private float mAzimuth = 0.0f;
	private float mPreviousAzimuth = 0.0f;
	private int mNumber = 0;

	private Socket mSocket = null;
	private DataOutputStream mDataOutputStream = null;
	private DataInputStream mDataInputStream = null;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.capabilities_main);
		
	    
	    mAzimuthField = (TextView)findViewById(R.id.azimuth_field);
	    mAzimuthField.setText(String.valueOf(mAzimuth));
	    
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

	    // listen always, also in paused
	    // TODO we get sensor data only, if we don't sleep
	    mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_NORMAL);
	    mSensorManager.registerListener(this, mMagnetometer, SensorManager.SENSOR_DELAY_NORMAL);
	    
	    // Test createConnection();
	    
	    mPowerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
	    mWakeLock = mPowerManager.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "CapabilitiesActivity");
	    mWakeLock.acquire();	    
	}
	
	private void createConnection() {
	    try {
	    	  mSocket = new Socket(HOST, PORT);
	    	  mDataInputStream = new DataInputStream(mSocket.getInputStream());
	    	  mDataOutputStream = new DataOutputStream(mSocket.getOutputStream());
	    	  /*
	    	  mDataOutputStream.writeUTF(textOut.getText().toString());
	    	  textIn.setText(mDataInputStream.readUTF());*/
	    } catch (UnknownHostException e) {
	    	  // TODO Auto-generated catch block
	    	Log.e(LOGTAG, "createConnection", e);
	    } catch (IOException e) {
				// TODO Auto-generated catch block
	    	Log.e(LOGTAG, "createConnection", e);
		}
		
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.capabilities, menu);
		return true;
	}
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item){
	    switch(item.getItemId()){
	    case R.id.action_settings:
	    	Intent launchNewIntent = new Intent(CapabilitiesActivity.this,SettingsActivity.class);
	    	startActivityForResult(launchNewIntent, 0);
	    	return true;            
	    }
	    return false;
	}
	
	protected void onResume() {
	    super.onResume();
	    //mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_NORMAL);
	    //mSensorManager.registerListener(this, mMagnetometer, SensorManager.SENSOR_DELAY_NORMAL);
	}
		 
	protected void onPause() {
	    super.onPause();
	    //mSensorManager.unregisterListener(this);
	}
	
	protected void onDestroy() {
		super.onDestroy();
		if (mSocket != null) {
			try {
			    mSocket.close();
			} catch (IOException e) {
			    // TODO Auto-generated catch block
    	        Log.e(LOGTAG, "onDestroy", e);
			}
		}

		if (mDataOutputStream != null) {
			try
			{
				mDataOutputStream.close();
		    } catch (IOException e) {
		    	// TODO Auto-generated catch block
    	        Log.e(LOGTAG, "onDestroy", e);
		    }

		}
		if (mDataInputStream != null) {
			try {
				mDataInputStream.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
    	        Log.e(LOGTAG, "onDestroy", e);
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
		if (mDataOutputStream != null) {
			if (Math.abs(aAzimuth - mPreviousAzimuth) > kAccuracyFactor) {
				try {
					Sensation sensation = new Sensation(mNumber, Sensation.SensationType.Azimuth, aAzimuth);
					String s = sensation.toString() +  "|";
					byte[] bytes = s.getBytes("UTF-8");
	    	        Log.d(LOGTAG, "reportAzimuth write " + Integer.toString(bytes.length));
					mDataOutputStream.write(bytes);
				} catch (IOException e) {
					// TODO Auto-generated catch block
	    	        Log.e(LOGTAG, "reportAzimuth write", e);
	    	        createConnection();
	    	        return;
				}
				mNumber++;
				mPreviousAzimuth = aAzimuth;

				if (mDataInputStream != null) {
					try {
						int available = mDataInputStream.available();
						int l=0;
		    	        Log.d(LOGTAG, "reportAzimuth read " + Integer.toString(available));
						while (available > 0)
						{
							byte[] b = new byte[256];
			    	        Log.d(LOGTAG, "reportAzimuth read available " + Integer.toString(available));
							l += mDataInputStream.read(b, l, available);
			    	        Log.d(LOGTAG, "reportAzimuth read l " + Integer.toString(l));
							available = mDataInputStream.available();
						}
					} catch (IOException e) {
						// TODO Auto-generated catch block
		    	        Log.e(LOGTAG, "reportAzimuth read", e);
		    	        createConnection();
		    	        return;
					}
				}
			}
		}
		else {
	        Log.d(LOGTAG, "reportAzimuth; no mDataOutputStream");
		}
	}
	


}
