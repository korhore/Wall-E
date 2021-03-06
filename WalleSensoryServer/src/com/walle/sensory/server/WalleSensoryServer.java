package com.walle.sensory.server;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.concurrent.LinkedBlockingQueue;

import com.walle.sensory.server.Sensation.Direction;
import com.walle.sensory.server.Sensation.Memory;
import com.walle.sensory.server.Sensation.SensationType;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.media.MediaPlayer;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.PowerManager;
import android.os.RemoteException;
import android.util.Log;
import android.view.View;

public class WalleSensoryServer extends Service implements SensorEventListener {
	final String LOGTAG="WalleSensoryServer";
	
	public enum ConnectionState {NOT_CONNECTED, NO_HOST, SOCKET_ERROR, IO_ERROR, CONNECTING, CONNECTED, WRITING, READING};
	public enum Functionality {sensory, calibrate, remoteController};

	final private float kFilteringFactor = 0.1f;
	// Create a constant to convert nanoseconds to seconds.
	private static final float NS2S = 1.0f / 1000000000.0f;
	final private float kAccelometerAccuracyFactor = 0.2f;
	final private float kAzimuthAccuracyFactor = (float)(Math.PI * 5.0)/180.0f;
	final private long kCalibrateTime = 60l * 1000000000l;	// nanoseconds
	final private float EPSILON = kAzimuthAccuracyFactor;
	


	private static Functionality mFunctionality = Functionality.sensory;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mMagnetometer;
    private Sensor mGyroscope;
    
    private PowerManager mPowerManager;
    private PowerManager.WakeLock mWakeLock;

    private boolean mCalibrated = false;
    private boolean mCalibrationStarted = false;

    private float[] mAcceleration;
    private float[] mPreviousAcceleration;
    private float[] mCalibrateAcceleration;
	private float[] mGeomagnetic;
	private float[] mGyro;
	private long mTimestamp = 0l;
	private long mCalibrationStartTime = 0l;
	private float[] mDeltaRotationVector;
	private float mAzimuth = 0.0f;
	private float mPreviousAzimuth = 0.0f;
	private int mSensationNumber = 0;

	// queues to ftp socket
	private LinkedBlockingQueue<Sensation> mSensationOutQueue;

	// ftp socket with technical streams
	private Socket mSocket = null;
	//private boolean mSocketError = false;
	private ConnectionState mConnectionState = ConnectionState.NOT_CONNECTED;
	private DataOutputStream mDataOutputStream = null;
	private DataInputStream mDataInputStream = null;
	private SocketServer mSocketServer = null;
	
	//private CreateConnectionTask mCreateConnectionTask;
	
	private SharedPreferences mPrefs;
	private SettingsModel mSettingsModel;
    private ArrayList<Messenger> mClients = new ArrayList<Messenger>();
    
	private MediaPlayer mMediaPlayer;
	boolean mSayingWalle = false;

    
    
    /**
     * Command to the service to register a client, receiving callbacks
     * from the service.  The Message's replyTo field must be a Messenger of
     * the client where callbacks should be sent.
     */
    public static final int MSG_REGISTER_CLIENT = 1;

    /**
     * Command to the service to unregister a client, or stop receiving callbacks
     * from the service.  The Message's replyTo field must be a Messenger of
     * the client as previously given with MSG_REGISTER_CLIENT.
     */
    public static final int MSG_UNREGISTER_CLIENT = MSG_REGISTER_CLIENT+1;
    
    /**
     * Command to report connection state to walle-server
     */
    public static final int MSG_CONNECTION_STATE = MSG_UNREGISTER_CLIENT+1;

    /**
     * Command to report azimuth.
     */
    public static final int MSG_AZIMUTH = MSG_CONNECTION_STATE+1;

    /**
     * Command to report accelerometer.
     */
    public static final int MSG_ACCELEROMETER = MSG_AZIMUTH+1;

    /**
     * Command to report observation, not in use
     */
    // public static final int MSG_OBSERVATION = MSG_ACCELEROMETER+1;

   /**
     * Get host
     */
    public static final int MSG_GET_HOST = MSG_ACCELEROMETER+1;

    /**
     * Set host
     */
    public static final int MSG_SET_HOST = MSG_GET_HOST+1;
    
    /**
     * Get port
     */
    public static final int MSG_GET_PORT = MSG_SET_HOST+1;

    /**
     * Set port
     */
    public static final int MSG_SET_PORT = MSG_GET_PORT+1;
    
    /**
     * send/receive Sensation
     */
    public static final int MSG_SENSATION = MSG_SET_PORT+1;
     
    /**
     * emit Sensation
     * from client
     * send Sensation to Walle
     */
    public static final int MSG_EMIT_SENSATION = MSG_SENSATION+1;

    /**
     * Handler of incoming messages from clients.
     */
    class IncomingHandler extends Handler {
        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case MSG_REGISTER_CLIENT:
      	    	  	Log.d(LOGTAG, "handleMessage MSG_REGISTER_CLIENT");
      	    	    mClients.add(msg.replyTo);
      	    	  	Log.d(LOGTAG, "handleMessage clients " + String.valueOf(mClients.size()));
                    break;
                case MSG_UNREGISTER_CLIENT:
      	    	  	Log.d(LOGTAG, "handleMessage MSG_UNREGISTER_CLIENT");
                    mClients.remove(msg.replyTo);
      	    	  	Log.d(LOGTAG, "handleMessage clients " + String.valueOf(mClients.size()));
                    if (mClients.size() == 0) {
         	    	  	Log.d(LOGTAG, "handleMessage stopSelf()");
         	    	  	stopSelf();
                    }
                    break;
                    
                case MSG_CONNECTION_STATE:
      	    	  	//Log.d(LOGTAG, "handleMessage MSG_CONNECTION_STATE");
      		    	try {
      		    		msg.replyTo.send(Message.obtain(null, MSG_CONNECTION_STATE, mConnectionState.ordinal(), 0));
      		        } catch (RemoteException e) {
      			                // The client is dead.  Remove it from the list;
      			                // we are going through the list from back to front
      			                // so this is safe to do inside the loop.
      		        	mClients.remove(msg.replyTo);
      		        }
                    break;

                case MSG_GET_HOST:
      	    	  	//Log.d(LOGTAG, "handleMessage MSG_GET_HOST " + mSettingsModel.getHost());
      		    	try {
      		    		msg.replyTo.send(Message.obtain(null, MSG_GET_HOST, 0,  0, mSettingsModel.getHost()));
      		        } catch (RemoteException e) {
      			                // The client is dead.  Remove it from the list;
      			                // we are going through the list from back to front
      			                // so this is safe to do inside the loop.
      		        	mClients.remove(msg.replyTo);
      		        }
                    break;

                case MSG_SET_HOST:
      	    	  	//Log.d(LOGTAG, "handleMessage MSG_SET_HOST " + (String) msg.obj);
      	    	    mSettingsModel.setHost((String) msg.obj);
                    break;

                case MSG_GET_PORT:
      	    	  	//Log.d(LOGTAG, "handleMessage MSG_GET_PORT " +  String.valueOf(mSettingsModel.getPort()));
      		    	try {
      		    		msg.replyTo.send(Message.obtain(null, MSG_GET_PORT,  mSettingsModel.getPort(),  0, null));
      		        } catch (RemoteException e) {
      			                // The client is dead.  Remove it from the list;
      			                // we are going through the list from back to front
      			                // so this is safe to do inside the loop.
      		        	mClients.remove(msg.replyTo);
      		        }
                    break;

                case MSG_SET_PORT:
      	    	  	//Log.d(LOGTAG, "handleMessage MSG_SET_PORT " + String.valueOf(msg.arg1));
      	    	    mSettingsModel.setPort(msg.arg1);
                    break;

                case MSG_EMIT_SENSATION:
      	    	  	Log.d(LOGTAG, "handleMessage MSG_EMIT_SENSATION " + (String) msg.obj);
      	    	    emitSensation((String) msg.obj);
                    break;

                default:
                    super.handleMessage(msg);
                    
            }
        }
    }

	@Override
	public IBinder onBind(Intent arg0) {
        return mMessenger.getBinder();
	}
	
    /**
     * Home we publish for clients to send messages to IncomingHandler.
     */
    final Messenger mMessenger = new Messenger(new IncomingHandler());

    /** Called when the activity is first created. */
    @Override
    public void onCreate() {
        super.onCreate();
//
        //Log.d(TAG, "onCreate: creating mSensorManager");
        
        //mContext = getBaseContext();
	    mAcceleration = new float[3];
	    mPreviousAcceleration = new float[3];
	    mCalibrateAcceleration = new float[3];
		mGeomagnetic = new float[3];
		mGyro = new float[3];
		mDeltaRotationVector = new float[4];
    	for (int i=0; i<3; i++)
    	{
    		mAcceleration[i] = 0.0f;
    		mPreviousAcceleration[i] = 0.0f;
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
	    mWakeLock = mPowerManager.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "WallaSensoryServer");
	    mWakeLock.acquire();
	    
		mPrefs = this.getSharedPreferences(
			      "com.walle.sensory", Context.MODE_PRIVATE);
		mSettingsModel = new SettingsModel(mPrefs);
		
		//mCreateConnectionTask = new CreateConnectionTask();
		
		mSensationOutQueue = new LinkedBlockingQueue<Sensation>();

		createConnection();

	}
    
	private void createConnection() {
		if ((mConnectionState.ordinal() < ConnectionState.CONNECTING.ordinal())) {
			mSocketServer = new SocketServer();
			mSocketServer.start();
		}
	}
    
    @Override
	public void onDestroy() {
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
		if (!mCalibrationStarted) {
			mCalibrationStartTime = event.timestamp;
			mCalibrationStarted = true;
	        Log.d(LOGTAG, "onSensorChanged mCalibrationStartTime " + String.valueOf(mCalibrationStartTime));
		}
		boolean is_orientation=true;
		
	    if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER)
	    {
	        //Log.d(LOGTAG, "onSensorChanged TYPE_ACCELEROMETER");
	    	is_orientation=true;
	    	boolean report=false;
	    	for (int i=0; i<3; i++)
	    	{
	    		mAcceleration[i] = ((1.0f - kFilteringFactor ) * mAcceleration[i]) + (kFilteringFactor  * event.values[i]);
	    		if (Math.abs(mAcceleration[i] - mPreviousAcceleration[i]) > kAccelometerAccuracyFactor) {
	    			report=true;
	    		}

	    	}
	    	if (mCalibrated) {
		    	if (report) {
		    		report(mAcceleration);
		    	}
	    	}
	    	else {
	    		if ((event.timestamp - mCalibrationStartTime) > kCalibrateTime) {
	    	        Log.d(LOGTAG, "onSensorChanged Calibrated " + String.valueOf(event.timestamp));
	    	    	for (int i=0; i<3; i++)
	    	    	{
	    	    		mCalibrateAcceleration[i] = mAcceleration[i];
		    	        Log.d(LOGTAG, "onSensorChanged Calibrated " + String.valueOf(mCalibrateAcceleration[i]));
	    	    	}
	    	    	mCalibrated = true;
	    			
	    		}
	    	}
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
		      if (mAcceleration != null && mGeomagnetic != null) {
		      float R[] = new float[9];
		      float I[] = new float[9];
		      boolean success = SensorManager.getRotationMatrix(R, I, mAcceleration, mGeomagnetic);
		      if (success) {
		    	  float orientation[] = new float[3];
		    	  SensorManager.getOrientation(R, orientation);
		    	  mAzimuth = orientation[0]; // orientation contains: azimuth, pitch and roll
		    	  // update azimuth field
		    	  if (Math.abs(mAzimuth - mPreviousAzimuth) > kAzimuthAccuracyFactor) {
		    		  report(mAzimuth);
		    	  }
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
	
	private void report(float aAzimuth) {
		if (Math.abs(aAzimuth - mPreviousAzimuth) > kAzimuthAccuracyFactor) {
		    boolean reported=false;
		    
		    for (int i=mClients.size()-1; i>=0; i--) {
		    	try {
		    		mClients.get(i).send(Message.obtain(null, MSG_AZIMUTH, 0,  0, aAzimuth));
		    		reported=true;
			        } catch (RemoteException e) {
			                // The client is dead.  Remove it from the list;
			                // we are going through the list from back to front
			                // so this is safe to do inside the loop.
			        	mClients.remove(i);
			    }
		    }
		    
		    if (reported) {
			    Log.d(LOGTAG, "report Azimuth " + String.valueOf(aAzimuth) );
		    }
		}

		if (mConnectionState.ordinal() >= ConnectionState.CONNECTED.ordinal()) {
		    Log.d(LOGTAG, "report Azimuth connected " + mConnectionState.toString() );
			if (Math.abs(aAzimuth - mPreviousAzimuth) > kAzimuthAccuracyFactor) {
			    Log.d(LOGTAG, "report " + String.valueOf(aAzimuth) );
				Sensation sensation = new Sensation(++mSensationNumber, Memory.Sensory, Direction.In, Sensation.SensationType.Azimuth, aAzimuth);
				mSensationOutQueue.add(sensation);
				mPreviousAzimuth = aAzimuth;
			}
		} else {
			report(mConnectionState);
        	createConnection();
		}
	}
	
	private void report(float[] aAcceleration) {
/*		
		float[] reporGrafity = new float[3];
    	for (int i=0; i<3; i++)
    	{
    		mPreviousAcceleration[i] = aAcceleration[i];
    		reporGrafity[i] = aAcceleration[i] - mCalibrateAcceleration[i];
    	}

	    for (int i=mClients.size()-1; i>=0; i--) {
	    	try {
	    		mClients.get(i).send(Message.obtain(null, MSG_ACCELEROMETER, 0,  0, reporGrafity));
	        } catch (RemoteException e) {
		                // The client is dead.  Remove it from the list;
		                // we are going through the list from back to front
		                // so this is safe to do inside the loop.
	        	mClients.remove(i);
	        }
	    }
	    
		if (mConnectionState.ordinal() >= ConnectionState.CONNECTED.ordinal()) {
		    Log.d(LOGTAG, "report Acceleration connected " + mConnectionState.toString() );
			Log.d(LOGTAG, "report " + String.valueOf(reporGrafity[0]) + ' ' + String.valueOf(reporGrafity[1]) + ' ' + String.valueOf(reporGrafity[2]));
			Sensation sensation = new Sensation(++mSensationNumber, Sensation.Memory.Sensory, Sensation.Direction.In, Sensation.SensationType.Acceleration, reporGrafity[0], reporGrafity[1], reporGrafity[2]);
			mSensationOutQueue.add(sensation);
		} else {
			report(mConnectionState);
        	createConnection();
		}
*/
	}
	
	private void report(ConnectionState aConnectionState) {
		if (aConnectionState != mConnectionState) {
	    	//Log.d(LOGTAG, "report " + aConnectionState.toString() + " previous " + mConnectionState.toString());
		    for (int i=mClients.size()-1; i>=0; i--) {
		    	try {
		    	   	//Log.d(LOGTAG, "report mClients.get(" + String.valueOf(i) + ").send");
		    		mClients.get(i).send(Message.obtain(null, MSG_CONNECTION_STATE, aConnectionState.ordinal(),  0));
		        } catch (RemoteException e) {
			                // The client is dead.  Remove it from the list;
			                // we are going through the list from back to front
			                // so this is safe to do inside the loop.
		    	   	Log.e(LOGTAG, e.toString());
		        	mClients.remove(i);
		        }
		    }
		    mConnectionState = aConnectionState;
	    }
		
	}
	
	public static ConnectionState toConnectionState( int i ) {
		final ConnectionState[] v = ConnectionState.values();
		return i >= 0 && i < v.length ? v[i] : ConnectionState.NOT_CONNECTED;
	}
	
	private void report(Sensation aSensation) {
    	//Log.d(LOGTAG, "report " + aSensation.toString());
		for (int i=mClients.size()-1; i>=0; i--) {
			try {
				//Log.d(LOGTAG, "report mClients.get(" + String.valueOf(i) + ").send");
		    	mClients.get(i).send(Message.obtain(null, MSG_SENSATION, 0, 0, aSensation.toString()));
		    } catch (RemoteException e) {
			            // The client is dead.  Remove it from the list;
			            // we are going through the list from back to front
			            // so this is safe to do inside the loop.
		       	Log.e(LOGTAG, e.toString());
		       	mClients.remove(i);
		    }
	    }
	}
		
	private void emitSensation(String aSensationString) {
    	//Log.d(LOGTAG, "emitSensation " + aSensationString);
	    	
		if (mConnectionState.ordinal() >= ConnectionState.CONNECTED.ordinal()) {
		    //Log.d(LOGTAG, "emitSensation connected " + mConnectionState.toString() );
			Sensation sensation = new Sensation(aSensationString);
			mSensationOutQueue.add(sensation);
			mSensationNumber++;
		} else {
			report(mConnectionState);
        	createConnection();
		}
		
		/* What's this? Why we are echoing sensations back?

		for (int i=mClients.size()-1; i>=0; i--) {
			try {
				//Log.d(LOGTAG, "emitSensation mClients.get(" + String.valueOf(i) + ").send");
		    	mClients.get(i).send(Message.obtain(null, MSG_SENSATION, 0, 0, aSensationString));
		    } catch (RemoteException e) {
			            // The client is dead.  Remove it from the list;
			            // we are going through the list from back to front
			            // so this is safe to do inside the loop.
		       	Log.e(LOGTAG, e.toString());
		       	mClients.remove(i);
		    }
	    }
	    */
	}

	private void process(Sensation aSensation) {
		if (aSensation.getSensationType() == SensationType.Calibrate) {
			if (aSensation.getCalibrateSensationType() == Sensation.SensationType.HearDirection) {
				if (aSensation.getMemory() == Memory.Working) {
					if (aSensation.getDirection() == Direction.In) {
						mFunctionality = Functionality.calibrate;
				    	Log.d(LOGTAG, "process asked to start calibrate mode");
					} else {
				    	Log.d(LOGTAG, "process asked to stop calibrate mode, going to sensory mode" );
						mFunctionality = Functionality.sensory;
					}
				} else if (aSensation.getMemory() == Memory.Sensory) {
					if (mFunctionality == Functionality.calibrate) {
				    	Log.d(LOGTAG, "process in calibrate mode" );
						if (aSensation.getDirection() == Direction.In) {
					    	Log.d(LOGTAG, "process in calibrate mode, start calibrate activity" );
			    			playSayWalle();

						} else {
					    	Log.d(LOGTAG, "process in calibrate mode, stop calibrate activity" );
							// TODO handle here hearing calibration, saying walle!
						}
					} else {
				    	Log.d(LOGTAG, "process asked to start calibrate activity without sensory mode, ignired" );
						mFunctionality = Functionality.sensory;
					}
	
				}
			}
		} else {
	    	Log.d(LOGTAG, "process asked to calibrate other than HearDirection, can not calibrate those, ignored" );
		}

	}
		
		private void playSayWalle() {
	    	//play sound
			if (mSayingWalle) {
		    	Log.d(LOGTAG, "playSayWalle asked to play sound, but was already started, ignored");
			} else {
		    	mMediaPlayer = MediaPlayer.create(getBaseContext(), R.raw.evesayswalle);
		    	mMediaPlayer.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
		    		public void onCompletion(MediaPlayer aMediaPlayer) {
		    			mSayingWalle = false;
		    			mMediaPlayer.release();
		    			// report stoped calibrating action
		    			report( new Sensation(	++mSensationNumber,
								Sensation.Memory.Sensory,
								Sensation.Direction.Out,
								Sensation.SensationType.Calibrate,
								Sensation.SensationType.HearDirection,
								0.0f));
	
		    		}
		    	});
				mSayingWalle = true;
				mMediaPlayer.start();
		    	Log.d(LOGTAG, "playSayWalle started to play sound");
			}
		}

	
	/////////////////////////////////////////////
	//
	// socket ftp in async threading
	
	private class SocketServer extends Thread {
		
		private SocketWriter mSocketWriter;
		private SocketReader mSocketReader;
		
		public SocketServer() {
			mSocketWriter = new SocketWriter();
			mSocketReader = new SocketReader();
						
		}
		public void run (){
			
			
			report(ConnectionState.CONNECTING);
		    try {

		    	  Log.d(LOGTAG, "SocketServer.run " + mSettingsModel.getHost() + ' ' + String.valueOf(mSettingsModel.getPort()));
		    	  mSocket = new Socket(mSettingsModel.getHost(), mSettingsModel.getPort());
		    	  mDataInputStream = new DataInputStream(mSocket.getInputStream());
		    	  mDataOutputStream = new DataOutputStream(mSocket.getOutputStream());
		    	  report(ConnectionState.CONNECTED);
		    } catch (SocketException e) {
		    	report(ConnectionState.SOCKET_ERROR);
		    	Log.e(LOGTAG, "SocketServer.run SocketException", e);
		    } catch (UnknownHostException e) {
		    	report(ConnectionState.NO_HOST);
		    	Log.e(LOGTAG, "SocketServer.run  UnknownHostException", e);
		    } catch (IOException e) {
		    	report(ConnectionState.IO_ERROR);
		    	Log.e(LOGTAG, "SocketServer.run IOException", e);
			}
		    
		    if (mConnectionState == ConnectionState.CONNECTED) {
		    	mSocketWriter.start();	
		    	mSocketReader.start();
		    }
			
		}
	}
	
	/**
	 * Reads Sensations from the queue and writes them to the socket.
	 * Uses very simple and efficient protocol <message length> <messages>
	 * Our goal is use as less resources as possible (we block if no Sensations to write)
	 * but transfer Sensations as fast as possible to the client (socket buffer is just Sensation length,
	 * every time, even it variates) so our robot gets its sensations fast and can perform many sensations
	 * processing in same event/manouver. 
	 *
	 */
	private class SocketWriter extends Thread {
		public void run () {
	    	Log.d(LOGTAG, "SocketWriter.run");
			while ((mSocket.isConnected()) && (!mSocket.isOutputShutdown())) {
				Sensation sensation;
				try {
					sensation = mSensationOutQueue.take();
				 	Log.d(LOGTAG, "SocketWriter.run take " + sensation.toString());
					report(ConnectionState.WRITING);
				    try {
						byte[] bytes = (sensation.toString()).getBytes("UTF-8");
						byte[] length_of_bytes = (String.format(Sensation.SENSATION_LENGTH_FORMAT,bytes.length)).getBytes("UTF-8");
						byte[] separator_bytes = (Sensation.SENSATION_SEPRATOR).getBytes("UTF-8");
			    	    //Log.d(LOGTAG, "SocketWriter.run write " + Integer.toString(bytes.length));
						mDataOutputStream.write(length_of_bytes);				// message length section
					    mDataOutputStream.flush();
						mDataOutputStream.write(bytes);							// message data section
					    mDataOutputStream.flush();
						mDataOutputStream.write(separator_bytes);				// message separator section
					    mDataOutputStream.flush();
					    report(ConnectionState.CONNECTED);
					} catch (IOException e) {
				        Log.e(LOGTAG, "SocketWriter.run write", e);
				        report(ConnectionState.IO_ERROR);
					}
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
		    	    Log.e(LOGTAG, "SocketWriter.run write", e);
				}
			}
		}
	}

	/**
	 * Reads Sensations from the socket and reports them to the client.
	 * Uses same very simple and efficient protocol <message length> <messages>
	 * than socket writer.
	 *
	 */

	private class SocketReader extends Thread {
		public void run () {
		 	Log.d(LOGTAG, "SocketReader.run");
			byte[] bl = new byte[Sensation.SENSATION_LENGTH_SIZE];
			byte[] b;
			int l;
			while ( (mConnectionState.ordinal() >= ConnectionState.CONNECTED.ordinal()) &&
					(mSocket.isConnected()) && (!mSocket.isInputShutdown())) {
				try  {
					while ((l = mDataInputStream.read(bl)) == Sensation.SENSATION_LENGTH_SIZE) {	// messge length section
		    	        //Log.d(LOGTAG, "SocketReader.run read message length l " + Integer.toString(l) + ' ' +  new String(bl) + " bytes" );
		    			report(ConnectionState.READING);
						
		                boolean length_ok = true;
//		                boolean resyncing = false;
	                	int sensation_length=0;
	                	try {
		                	sensation_length = Integer.parseInt(new String(bl));
		                } catch (Exception e) {
		                	Log.e(LOGTAG, "SocketServer Client protocol read error, no valid length, resyncing", e);
		                    length_ok = false;
//		                    resyncing = true;
		                }
	                	if (length_ok) {
	    					try {
	    						b = new byte[sensation_length];
	    						int read=0;
	    						while (sensation_length > 0) {
		    						l = mDataInputStream.read(b, read, sensation_length);		// messge data section
		    						read += l;
		    						sensation_length -= l;
			    		    	    //Log.d(LOGTAG, "SocketReader.run read data section l " + Integer.toString(l) + ' ' +  new String(b));
	    						}
		    		    	    if (sensation_length == 0) {
		    		    	    	Sensation s = new Sensation(new String(b));
		    					 	Log.d(LOGTAG, "SocketReader.run read " + s.toString());
		    					 	process(s);
		    		    	    	report(s);
		    		    	    } else {
			    		    	    Log.d(LOGTAG, "SocketReader.run read Sensation read " + Integer.toString(read) + " ignoring " +  Integer.toString(sensation_length) + " does not match with it, resyncing" );
//				                    resyncing = true;
		    		    	    }
	    					}
	    					catch (Exception e) {
			                	Log.e(LOGTAG, "SocketServer Client Sensation read error resyncing", e);
//			                    resyncing = true;
	    					}
	                	}
	                	// message separator section
	                	// handles also resyncing if socket transmit error
						b = new byte[Sensation.SENSATION_SEPRATOR_SIZE];
	                	do {
    						mDataInputStream.read(b);
//	    		    	    Log.d(LOGTAG, "SocketReader.run separator section read char " +  new String(b));
	                	} while (b[0] != Sensation.SENSATION_SEPRATOR.charAt(0));
					}
				}
    			catch (Exception e) {
    				Log.e(LOGTAG, "SocketServer Client Sensation lenght read error, closing socket", e);
	    	        Log.d(LOGTAG, "SocketReader.run mSocket.close()");
	    	        report(ConnectionState.IO_ERROR);
	    	        try {
						mSocket.close();
					} catch (IOException e1) {
						// TODO Auto-generated catch block
	    				Log.e(LOGTAG, "SocketServer closing socket", e1);
					}
				}
			}
		}
	}

}
