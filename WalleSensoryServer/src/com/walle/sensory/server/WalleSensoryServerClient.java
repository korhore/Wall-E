/*
 * WalleSensoryServerClient.java
 * 
 * Helper class, that does all hard work how client can use WalleSensoryServer
 * 
 * 
 */

package com.walle.sensory.server;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.RemoteException;
import android.util.Log;

import com.walle.sensory.server.WalleSensoryServer;


public abstract class WalleSensoryServerClient extends Activity{
	final String LOGTAG="WalleSensoryServerClient";
	
    /** Messenger for communicating with service. */
    Messenger mService = null;
    /** Flag indicating whether we have called bind on the service. */
    boolean mIsBound;
    
    // abstract methods that must be implemented

    // Parent class that extracts this utility class, return itself (this) 

    abstract protected void onConnectionState(WalleSensoryServer.ConnectionState aConnectionState);
    abstract protected void onAzimuth(float aAzimuth);
    abstract protected void onAccelerometer(float[] aAccelerometer);
    abstract protected void onHost(String aHost);
    abstract protected void onPort(int aPort);
    abstract protected void onSensation(Sensation aSensation);
   
    abstract protected void onConnectedService();
    abstract protected void onDisconnectedService();

    /////////////////////////////////////////
    //
    // Service connection
  
    /**
     * Handler of incoming messages from service.
     */
    class IncomingHandler extends Handler {
    	
    	// TODO 
    	// in.readParceleable(LocationType.class.getClassLoader());
        @Override
        public void handleMessage(Message msg) {
   	        Log.d(LOGTAG, "handleMessage " + String.valueOf(msg.what));
            switch (msg.what) {
	            case WalleSensoryServer.MSG_CONNECTION_STATE:
	       	        Log.d(LOGTAG, "handleMessage MSG_CONNECTION_STATE");
	            	// When service is separate process, we must do tricks to get parcelable parameter
	            	// This implementation is in same process, no tricks
	             	onConnectionState(WalleSensoryServer.toConnectionState(msg.arg1));
	            	break;
                case WalleSensoryServer.MSG_AZIMUTH:
	       	        Log.d(LOGTAG, "handleMessage MSG_AZIMUTH");
                	// When service is separate process, we must do tricks to get parcelable parameter
                	// This implementation is in same process, no tricks
                 	onAzimuth((Float) msg.obj);
                	break;
                case WalleSensoryServer.MSG_ACCELEROMETER:
	       	        Log.d(LOGTAG, "handleMessage MSG_ACCELEROMETER");
	       	                     	// When service is separate process, we must do tricks to get parcelable parameter
                	// This implementation is in same process, no tricks
                 	onAccelerometer((float[]) msg.obj);
            	    break;
            	    
                case WalleSensoryServer.MSG_GET_HOST:
	       	        Log.d(LOGTAG, "handleMessage MSG_GET_HOST");
                	// When service is separate process, we must do tricks to get parcelable parameter
                	// This implementation is in same process, no tricks
                	onHost((String) msg.obj);
                	break;
               	 
                case WalleSensoryServer.MSG_GET_PORT:
	       	        Log.d(LOGTAG, "handleMessage MSG_GET_PORT");
                	onPort(msg.arg1);
                	break;
               	 
                case WalleSensoryServer.MSG_SENSATION:
	       	        Log.d(LOGTAG, "handleMessage MSG_SENSATION");
	       	        onSensation(new Sensation((String) msg.obj));
                	break;
               	 
               default:
	       	        Log.d(LOGTAG, "handleMessage default no handler here");
                    super.handleMessage(msg);
            }
        }
    }

    /**
     * Target we publish for clients to send messages to IncomingHandler.
     */
    final Messenger mMessenger = new Messenger(new IncomingHandler());


    /**
     * Class for interacting with the main interface of the service.
     */
    private ServiceConnection mConnection = new ServiceConnection() {
        public void onServiceConnected(ComponentName className,
                IBinder service) {
            // This is called when the connection with the service has been
            // established, giving us the service object we can use to
            // interact with the service.  We are communicating with our
            // service through an IDL interface, so get a client-side
            // representation of that from the raw service object.
            mService = new Messenger(service);

            // We want to monitor the service for as long as we are
            // connected to it.
            try {
                Message msg = Message.obtain(null,
                		WalleSensoryServer.MSG_REGISTER_CLIENT, 0, 0);
                msg.replyTo = mMessenger;
                mService.send(msg);	

            } catch (RemoteException e) {
                // In this case the service has crashed before we could even
                // do anything with it; we can count on soon being
                // disconnected (and then reconnected if it can be restarted)
                // so there is no need to do anything here.
            }

            // tell the user what happened.
            onConnectedService();
        }
 
        public void onServiceDisconnected(ComponentName className) {
            // This is called when the connection with the service has been
            // unexpectedly disconnected -- that is, its process crashed.
            mService = null;

            // tell the user what happened.
            onDisconnectedService();
        }
    };
    
	protected void onResume() {
	    super.onResume();
        doBindService();
	}

    

    // Establish a connection with the service.  We use an explicit
    // class name because there is no reason to be able to let other
    // applications replace our component.
    void doBindService() {
        if (!mIsBound) {
	        bindService(new Intent(this, 
	        		WalleSensoryServer.class), mConnection, Context.BIND_AUTO_CREATE);
	        mIsBound = true;
	        onConnectedService();
        }
    }

	protected void onDestroy() {
		super.onDestroy();
        // disconnect from the the service
        try {
   	        Log.d(LOGTAG, "onDestroy MSG_UNREGISTER_CLIENT");
            Message msg = Message.obtain(null,
            		WalleSensoryServer.MSG_UNREGISTER_CLIENT, 0, 0);
            msg.replyTo = mMessenger;
            mService.send(msg);	// this crashes Android, if service is separate process (Can't marshal non-Parcelable objects across processes.)
        } catch (RemoteException e) {
            // In this case the service has crashed
            // so there is no need to do anything here.
        }
	    doUnbindService();
	}
    
    // Close connection with the service.
    void doUnbindService() {
        if (mIsBound) {
            // Detach our existing connection.
            unbindService(mConnection);
            mIsBound = false;
        }
    }
    
    /////////////////////////////////////////
    //
    // Methods to use service
    // All methods are asyncronous, so getters don't return anything, but
    // result is got on class extending  this utility class in its on-methods

    
    // call service asynchronously
    
    public void getConnectionState() {
    	if (mService != null) {
	        try {
	            Message msg = Message.obtain(null,
	            		WalleSensoryServer.MSG_CONNECTION_STATE, 0, 0);
	            msg.replyTo = mMessenger;
	            mService.send(msg);	
	        } catch (RemoteException e) {
	            // In this case the service has crashed
	        }
    	}
    }

    public void getHost() {
    	if (mService != null) {
	        try {
	            Message msg = Message.obtain(null,
	            		WalleSensoryServer.MSG_GET_HOST, 0, 0);
	            msg.replyTo = mMessenger;
	            mService.send(msg);	
	        } catch (RemoteException e) {
	            // In this case the service has crashed
	        }
    	}
    }
    
    public void setHost(String aHost) {
    	if (mService != null) {
	        try {
	            Message msg = Message.obtain(null,
	            		WalleSensoryServer.MSG_SET_HOST, 0, 0, aHost);
	            msg.replyTo = mMessenger;
	            mService.send(msg);	
	        } catch (RemoteException e) {
	            // In this case the service has crashed
	        }
    	}
    }

    public void getPort() {
    	if (mService != null) {
	    		try {
	    		Message msg = Message.obtain(null,
	                		WalleSensoryServer.MSG_GET_PORT, 0, 0);
	            msg.replyTo = mMessenger;
	                mService.send(msg);	
	    	} catch (RemoteException e) {
	    		// In this case the service has crashed
	    	}
    	}
    }
    public void setPort(int aPort) {
    	if (mService != null) {
	    	try {
	    		Message msg = Message.obtain(null,
	                		WalleSensoryServer.MSG_SET_PORT, aPort, 0);
	            msg.replyTo = mMessenger;
	                mService.send(msg);	
	    	} catch (RemoteException e) {
	    		// In this case the service has crashed
	    	}
    	}
    }

    
	

}
