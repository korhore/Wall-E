package com.walle.sensory;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.PowerManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;


public class CapabilitiesActivity extends Activity implements SensorEventListener {
	final String LOGTAG="CapabilitiesActivity";
	
	enum connectionState {NOT_CONNECTED, CONNECTED, NO_HOST, SOCKET_ERROR, IO_ERROR};

	final private float kFilteringFactor = 0.1f;
	// Create a constant to convert nanoseconds to seconds.
	private static final float NS2S = 1.0f / 1000000000.0f;
	//final private int PORT = 2000;
	//final private String HOST = "10.0.0.55";
	//final private String HOST = "10.0.0.17";
	final private float kAccuracyFactor = (float)(Math.PI * 5.0)/180.0f;
	final private float EPSILON = kAccuracyFactor;
	

    private TextView mAzimuthField;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mMagnetometer;
    private Sensor mGyroscope;
    
    private PowerManager mPowerManager;
    private PowerManager.WakeLock mWakeLock;

    private float[] mGravity;
	private float[] mGeomagnetic;
	private float[] mGyro;
	private float mTimestamp = 0.0f;
	private float[] mDeltaRotationVector;
	private float mAzimuth = 0.0f;
	private float mPreviousAzimuth = 0.0f;
	private int mNumber = 0;

	private Socket mSocket = null;
	//private boolean mSocketError = false;
	private connectionState mConnectionState = connectionState.NOT_CONNECTED;
	private DataOutputStream mDataOutputStream = null;
	private DataInputStream mDataInputStream = null;
	
	private SharedPreferences mPrefs;
	private SettingsModel mSettingsModel;

	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.capabilities_main);
		
	    
	    mAzimuthField = (TextView)findViewById(R.id.azimuth_field);
	    mAzimuthField.setText(String.valueOf(mAzimuth));
	    
	    mGravity = new float[3] ;
		mGeomagnetic = new float[3];
		mGyro = new float[3];
		mDeltaRotationVector = new float[4];
    	for (int i=0; i<3; i++)
    	{
    		mGravity[i] = 0.0f;
    		mGeomagnetic[i] = 0.0f;
    		mGyro[i] = 0.0f;
    		mDeltaRotationVector[i] = 0.0f;
    	}
    	mDeltaRotationVector[3] = 0.0f;

	    
	    mSensorManager = (SensorManager)getSystemService(SENSOR_SERVICE);
	    mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
	    mMagnetometer = mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
	    mGyroscope = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
	    
	    // listen always, also in paused
	    // TODO we get sensor data only, if we don't sleep
	    mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_NORMAL);
	    mSensorManager.registerListener(this, mMagnetometer, SensorManager.SENSOR_DELAY_NORMAL);
	    mSensorManager.registerListener(this, mGyroscope, SensorManager.SENSOR_DELAY_NORMAL);
	    
	    // Test createConnection();
	    
	    mPowerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
	    mWakeLock = mPowerManager.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "CapabilitiesActivity");
	    mWakeLock.acquire();
	    
		mPrefs = this.getSharedPreferences(
			      "com.walle.sensory", Context.MODE_PRIVATE);
		mSettingsModel = new SettingsModel(mPrefs);
		createConnection();

	}
	
	private void createConnection() {
    	//mSocketError = false;

	    try {
	    	  mConnectionState = connectionState.CONNECTED;

	    	  Log.d(LOGTAG, "createConnection Socket " + mSettingsModel.getHost() + ' ' + String.valueOf(mSettingsModel.getPort()));
	    	  mSocket = new Socket(mSettingsModel.getHost(), mSettingsModel.getPort());
	    	  mDataInputStream = new DataInputStream(mSocket.getInputStream());
	    	  mDataOutputStream = new DataOutputStream(mSocket.getOutputStream());
	    	  /*
	    	  mDataOutputStream.writeUTF(textOut.getText().toString());
	    	  textIn.setText(mDataInputStream.readUTF());*/
	    } catch (SocketException e) {
	    	mConnectionState = connectionState.SOCKET_ERROR;
	    	//mSocketError = true;
	    	Log.e(LOGTAG, "createConnection SocketException", e);
	    } catch (UnknownHostException e) {
	    	  // TODO Auto-generated catch block
	    	//mSocketError = true;
	    	mConnectionState = connectionState.NO_HOST;
	    	Log.e(LOGTAG, "createConnection UnknownHostException", e);
	    } catch (IOException e) {
				// TODO Auto-generated catch block
	    	//mSocketError = true;
	    	mConnectionState = connectionState.IO_ERROR;
	    	Log.e(LOGTAG, "createConnection IOException", e);
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
	
	public void onActivityResult(int requestCode, int resultCode, Intent data) {
		if (resultCode == 0) {	// if SettingActivity ended
								// TODO Check if changes in settings
								// create new connection
	    	mConnectionState = connectionState.NOT_CONNECTED;;

			createConnection();
			
		}
		
	}
	
	protected void onResume() {
	    super.onResume();
	    //mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_NORMAL);
	    //mSensorManager.registerListener(this, mMagnetometer, SensorManager.SENSOR_DELAY_NORMAL);
	    //mSensorManager.registerListener(this, mGyroscope, SensorManager.SENSOR_DELAY_NORMAL);
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
		boolean is_orientation=true;
		
	    if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER)
	    {
	        //Log.d(LOGTAG, "onSensorChanged TYPE_ACCELEROMETER");
	    	is_orientation=true;
	    	for (int i=0; i<3; i++)
	    	{
	    		mGravity[i] = ((1.0f - kFilteringFactor ) * mGravity[i]) + (kFilteringFactor  * event.values[i]);
	    	}
	    	//mGravity=event.values;
	    }
	    if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD)
	    {
	        //Log.d(LOGTAG, "onSensorChanged TYPE_MAGNETIC_FIELD");
	    	is_orientation=true;
	    	for (int i=0; i<3; i++)
		    {
	    		mGeomagnetic[i] = ((1.0f - kFilteringFactor ) * mGeomagnetic[i]) + (kFilteringFactor  * event.values[i]);
		    }
	    	//mGeomagnetic=event.values;
		}
	    if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE)
	    {
	        //Log.d(LOGTAG, "onSensorChanged TYPE_GYROSCOPE");
	    	is_orientation=false;
	    	for (int i=0; i<3; i++)
		    {
	    		mGyro[i] = ((1.0f - kFilteringFactor ) * mGyro[i]) + (kFilteringFactor  * event.values[i]);
		    }
	    	//mGyro=event.values;
		}
	    
	    if (is_orientation) {
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
	    else {
	    	// Android example code
	    	// This timestep's delta rotation to be multiplied by the current rotation
	    	// after computing it from the gyro sample data.
	    	if (mTimestamp != 0) {
	    		final float dT = (event.timestamp - mTimestamp) * NS2S;
	    	    // Axis of the rotation sample, not normalized yet.

	    	    // Calculate the angular speed of the sample
	    	    float omegaMagnitude = (float) Math.sqrt((double) mGyro[0]*mGyro[0] + mGyro[1]*mGyro[1] + mGyro[2]*mGyro[2]);

	    	    // Normalize the rotation vector if it's big enough to get the axis
	    	    // (that is, EPSILON should represent your maximum allowable margin of error)
	    	    if (omegaMagnitude > EPSILON) {
	    	      mGyro[0] /= omegaMagnitude;
	    	      mGyro[1] /= omegaMagnitude;
	    	      mGyro[2] /= omegaMagnitude;
	    	    }

	    	    // Integrate around this axis with the angular speed by the timestep
	    	    // in order to get a delta rotation from this sample over the timestep
	    	    // We will convert this axis-angle representation of the delta rotation
	    	    // into a quaternion before turning it into the rotation matrix.
	    	    float thetaOverTwo = omegaMagnitude * dT / 2.0f;
	    	    float sinThetaOverTwo = (float) Math.sin((double) thetaOverTwo);
	    	    float cosThetaOverTwo = (float) Math.cos((double) thetaOverTwo);
	    	    mDeltaRotationVector[0] = sinThetaOverTwo * mGyro[0];
	    	    mDeltaRotationVector[1] = sinThetaOverTwo * mGyro[1];
	    	    mDeltaRotationVector[2] = sinThetaOverTwo * mGyro[2];
	    	    mDeltaRotationVector[3] = cosThetaOverTwo;
	    	  }
	    	  mTimestamp = event.timestamp;
	    	  float[] deltaRotationMatrix = new float[9];
//	    	  /*boolean success = */ SensorManager.getRotationMatrixFromVector(deltaRotationMatrix, mDeltaRotationVector);
	    	    // User code should concatenate the delta rotation we computed with the current rotation
	    	    // in order to get the updated rotation.
	    	    // rotationCurrent = rotationCurrent * deltaRotationMatrix;
		      Log.d(LOGTAG, "onSensorChanged TYPE_GYROSCOPE SensorManager.getRotationMatrixFromVector");
	    }
	}

	@Override
	public void onAccuracyChanged(Sensor sensor, int accuracy) {
		// TODO Auto-generated method stub
		
	}
	
	private void reportAzimuth(float aAzimuth) {
		if (mConnectionState == connectionState.CONNECTED) {
			if (Math.abs(aAzimuth - mPreviousAzimuth) > kAccuracyFactor) {
				try {
					Sensation sensation = new Sensation(mNumber, Sensation.SensationType.Azimuth, aAzimuth);
					String s = sensation.toString() +  "|";
					byte[] bytes = s.getBytes("UTF-8");
	    	        Log.d(LOGTAG, "reportAzimuth write " + Integer.toString(bytes.length));
					mDataOutputStream.write(bytes);
			    	mDataOutputStream.flush();
				} catch (IOException e) {
					// TODO Auto-generated catch block
	    	        Log.e(LOGTAG, "reportAzimuth write", e);
	    	        mConnectionState = connectionState.IO_ERROR;
	    	        try {
						mSocket.close();
					} catch (IOException e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}
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
			    	        Log.d(LOGTAG, "reportAzimuth read l " + Integer.toString(l) + ' ' +  b);
							available = mDataInputStream.available();
						}
					} catch (IOException e) {
						// TODO Auto-generated catch block
		    	        Log.e(LOGTAG, "reportAzimuth read", e);
		    	        mConnectionState = connectionState.IO_ERROR;
		    	        try {
							mSocket.close();
						} catch (IOException e1) {
							// TODO Auto-generated catch block
							e1.printStackTrace();
						}
	    	        	createConnection();
		    	        return;
					}
				}
			}
		}
	}
	


}
