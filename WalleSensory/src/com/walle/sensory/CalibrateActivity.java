package com.walle.sensory;


import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.os.PowerManager;
import android.util.AttributeSet;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ImageView.ScaleType;
import android.widget.Toast;

import com.walle.sensory.server.Sensation;
import com.walle.sensory.server.WalleSensoryServer.ConnectionState;
import com.walle.sensory.server.WalleSensoryServerClient;


public class CalibrateActivity extends WalleSensoryServerClient  {
	final static String LOGTAG="CalibrateActivity";
	

	final static int boundary=2;
	



	private ImageView mWalleImage;
	private ImageView mEwaImage;
	
	private static Sensation mHearDirectionSensation;
	private static Sensation mEmitSensation;
	

    
	private Button mSensoryButton;
	private Button mLeftButton;
	private Button mMiddleButton;
	private Button mRightButton;

	private static int mSensationNumber = 0;
	
	private MediaPlayer mMediaPlayer;






	// Note, custom view class must be static to allow it be initialized from layoyt file
	private static class World extends View {
		private CalibrateActivity mCapabilitiesActivity=null;	// Note, when this is static class, there are situations
																	// we want to access outer class members.
																	// All of then can't be changes to static, so
																	// it's better to use reference to outer class, when needed
		
		final static float DISTANCE=5.0f;	// We see 5.0 m around Walle
	    int screenW;
	    int screenH;
	    float screen;
	    int X;
	    int Y;
	    int evaW;
	    int evaH;
	    int walleW;
	    int walleH;
	    int earW;
	    int earH;
	    int hearingDistance;
	    Bitmap mEva, mWalle, mEar;
	    
	
	    public World(Context context) {
	        super(context);
	        mEva = BitmapFactory.decodeResource(getResources(),R.drawable.eva); //load a mEva image
	        mWalle = BitmapFactory.decodeResource(getResources(),R.drawable.walle); //load a background
	        mEar = BitmapFactory.decodeResource(getResources(),R.drawable.ear); //load a mEarimage
	        evaW = mEva.getWidth();
	        evaH = mEva.getHeight();
	        walleW = mWalle.getWidth();
	        walleH = mWalle.getHeight();
	        earW = mEar.getWidth();
	        earH = mEar.getHeight();

	    }

	    public World(Context context, AttributeSet attr) {
	        super(context, attr);
	        mEva = BitmapFactory.decodeResource(getResources(),R.drawable.eva); //load a mEva image
	        mWalle = BitmapFactory.decodeResource(getResources(),R.drawable.walle); //load a background
	        mEar = BitmapFactory.decodeResource(getResources(),R.drawable.ear); //load a mEar image
	        evaW = mEva.getWidth();
	        evaH = mEva.getHeight();
	        walleW = mWalle.getWidth();
	        walleH = mWalle.getHeight();
	        earW = mEar.getWidth();
	        earH = mEar.getHeight();
	        

	    }
	
	    @Override
	    public void onSizeChanged (int w, int h, int oldw, int oldh) {
	    	Log.d(LOGTAG, "onSizeChanged");
	        super.onSizeChanged(w, h, oldw, oldh);
	        screenW = w;
	        screen = screenW;
	        screenH = h;
	        if (screenH < screen)
	        	screen = screenH;
	        screen = screen/2.0f;
	        //mWalle = Bitmap.createScaledBitmap(mWalle, w, h, true); //Resize background to fit the screen.
	        X = (screenW /2);// - (walleW / 2) ; //Centre mWalle into the centre of the screen.
	        Y = (screenH /2);// - (walleW / 2);
	        if (screenW < screenH)
	        	hearingDistance = screenW/8;
	        else
	        	hearingDistance = screenH/8;
	    	Log.d(LOGTAG, "onSizeChanged hearingDistance " + hearingDistance);
	    }
	
	    @Override
	    public void onDraw(Canvas canvas) {
	        super.onDraw(canvas);
	        
	        //Draw Hearing
	        if (mHearDirectionSensation != null)
	        {
	        	double angle =  mHearDirectionSensation.getHearDirection() - Math.PI/2.0d; // convert azimuth coordination to drawing coordination
	        	float x = (float) ((float)X + (hearingDistance * Math.cos(angle)) - (earW / 2.0f));
	        	float y = (float) ((float)Y + (hearingDistance * Math.sin(angle)) - (earH / 2.0f));
		        canvas.drawBitmap(	mEar,
    					x,
    					y,
						null); //Draw the mEva on the rotated canvas.
	        }

	        //Draw Buttons

	    }
	    
	    @Override
	    public boolean onTouchEvent(MotionEvent event) {
	    	float eventX = event.getX();
	    	float eventY = event.getY();
	    	Log.d(LOGTAG, "onTouchEvent X " + eventX + " Y " + eventY);
	    	double x = eventX - X - (evaW / 2.0f);
	    	double y = eventY - Y - (evaH / 2.0f);
	    	double h = (float) Math.sqrt((double) ((x*x) + (y*y))); // hypotenusa as pixels
	    	h = h*DISTANCE/screen;									// hypotenusa as meters
	    	double angle = Math.atan2(y, x) + Math.PI/2.0d;			// convert from screen coordinates to azimuth coordinates
	    	if (angle > Math.PI)
	    		angle = (-2.0d*Math.PI) + angle;
	    	Log.d(LOGTAG, "onTouchEvent x " + x + " y " + y + " h " + h + " angle " + angle);
	      
	    	// calculate Observation Sensation
	    	//(eventX -X + (evaW / 2.0f)))/h = Math.cos(angle);
	    	//double angle = Math.asin(x/h);
	    	//(eventY -Y + (evaH / 2.0f)))/h = Math.sin(angle);


	    	switch (event.getAction()) {
		    	case MotionEvent.ACTION_DOWN:
			    	Log.d(LOGTAG, "onTouchEvent ACTION_DOWN");
		    		return true;
		    	case MotionEvent.ACTION_MOVE:
			    	Log.d(LOGTAG, "onTouchEvent ACTION_MOVE");
			    	break;
		    	case MotionEvent.ACTION_UP:
			    	Log.d(LOGTAG, "onTouchEvent ACTION_UP");
			    	// here we should report sensation
			    	mEmitSensation = new Sensation(	++mSensationNumber,
															Sensation.Memory.Sensory,
															Sensation.Direction.In,
															Sensation.SensationType.Observation,
															(float) angle, (float) h);
			    	mCapabilitiesActivity.emitSensation(mEmitSensation);	// Note, should use outer class reference
			    															// to access no static methods from it
			    	break;
		    	default:
		    		return false;
	    	}
	    	
			return false;
	    }

	}
	
	private World mWorld;

	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
    	Log.d(LOGTAG, "onCreate()");
    	
    	mHearDirectionSensation = null;

   	
		setContentView(R.layout.capabilities_calibrate);
	    
	    mWalleImage = (ImageView)findViewById(R.id.walle_image);
	    mEwaImage = (ImageView)findViewById(R.id.walle_image);
		mWorld = (World)findViewById(R.id.calibrate_world);
		mWorld.mCapabilitiesActivity = this;	// allow static inner class to accces outer class non static members
		
		mSensoryButton = (Button)findViewById(R.id.sensory_button);
		mSensoryButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
    	    	Intent launchNewIntent = new Intent(CalibrateActivity.this,CapabilitiesActivity.class);
    	    	startActivityForResult(launchNewIntent, 0);
            }
        });
		

		mLeftButton = (Button)findViewById(R.id.left_button);
		
		//mMiddleButton = new Button(getContext());;
		//mMiddleButton.setText(R.string.middle);
		mMiddleButton = (Button)findViewById(R.id.middle_button);
		mMiddleButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
		    	Log.d(LOGTAG, "mMiddleButton.onClick");
		    	// here we should report sensation
		    	mEmitSensation = new Sensation(	++mSensationNumber,
														Sensation.Memory.Sensory,
														Sensation.Direction.In,
														Sensation.SensationType.Observation,
														0f, 3.0f);
		    	emitSensation(mEmitSensation);
		    	//play sound
		    	//mMediaPlayer = MediaPlayer.create(getBaseContext(), R.raw.evesayswalle);
		    	//mMediaPlayer.start();
            }
        });

		
		mRightButton = (Button)findViewById(R.id.right_button);


	    
	}
	
	@Override
	protected void onResume() {
		super.onResume();
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
	    	Intent launchNewIntent = new Intent(CalibrateActivity.this,SettingsActivity.class);
	    	startActivityForResult(launchNewIntent, 0);
	    	return true;            
	    }
	    return false;
	}
	
	public void onActivityResult(int requestCode, int resultCode, Intent data) {
		if (resultCode == 0) {	// if SettingActivity ended
								// TODO Check if changes in settings
								// create new connection

			//createConnection();
			// TODO make something to make server reconnect
			
		}
		
	}
	

	////////////////////////////////////////////////////////////////
	//
	// abstract methods implementation
	
	@Override
    protected void onConnectedService() {
        Toast.makeText(this, R.string.service_connected,
                Toast.LENGTH_SHORT).show();
        getConnectionState();

    }

	@Override
    protected void onDisconnectedService() {
        Toast.makeText(this, R.string.service_disconnected,
               Toast.LENGTH_SHORT).show();

    }

	
	
	@Override
	protected void onAzimuth(float aAzimuth) {
		// TODO Auto-generated method stub
	}
	@Override
	protected void onAccelerometer(float[] aAccelerometer) {
		// TODO Auto-generated method stub
	}
	@Override
	protected void onHost(String aHost) {
		// TODO Auto-generated method stub
		
	}
	@Override
	protected void onPort(int aPort) {
		// TODO Auto-generated method stub
		
	}


	@Override
	protected void onConnectionState(ConnectionState aConnectionState) {
	    //Log.d(LOGTAG, "onConnectionState " + aConnectionState.toString());
		setStatus(aConnectionState);
	}
	
	@Override
	protected void onSensation(Sensation aSensation) {
	    Log.d(LOGTAG, "onSensation " + aSensation.toString());
	    
	    if (aSensation.getSensationType() == Sensation.SensationType.Azimuth) {
	    	Matrix matrix=new Matrix();
	    	mWalleImage.setScaleType(ScaleType.MATRIX);   //required
	    	matrix.postRotate(	(float) Math.toDegrees(-aSensation.getAzimuth()),
	    						mWalleImage.getDrawable().getBounds().width()/2,
	    						mWalleImage.getDrawable().getBounds().height()/2);
	    	mWalleImage.setImageMatrix(matrix);
	    }
	    
	    switch (aSensation.getSensationType())
	    {
	    	case HearDirection:
	        	mHearDirectionSensation = aSensation;
	        	mWorld.invalidate();
	        	break;
	        default:
	        	break;
	    }

	    // don't emit sensation, it makes us call back all sensations Walle sends to us.
    	//emitSensation(aSensation);


	}

	
	/////////////////////////////////////////////////////////////
	//
	// implementation
	
    public void setStatus(ConnectionState aConnectionState) {
    	//Log.d(LOGTAG, "setStatus()");
   }


}
