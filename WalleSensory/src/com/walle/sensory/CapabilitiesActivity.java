package com.walle.sensory;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.drawable.ShapeDrawable;
import android.graphics.drawable.shapes.OvalShape;
import android.os.Bundle;
import android.os.PowerManager;
import android.util.AttributeSet;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ImageView.ScaleType;
import android.widget.TextView;
import android.widget.Toast;

import com.walle.sensory.server.Sensation;
import com.walle.sensory.server.WalleSensoryServer.ConnectionState;
import com.walle.sensory.server.WalleSensoryServerClient;


public class CapabilitiesActivity extends WalleSensoryServerClient  {
	final static String LOGTAG="CapabilitiesActivity";
	
/*
	#define PowerChangedColor QColor(Qt::green)
	#define UnconnectedStateColor QColor(Qt::gray)
	#define HostLookupStateColor QColor(Qt::magenta)
	#define ConnectingStateColor QColor(Qt::darkMagenta)
	#define ConnectedStateColor QColor(Qt::darkYellow)
	#define WritingStateColor QColor(Qt::blue)
	#define WrittenStateColor QColor(Qt::darkBlue)
	#define ReadingStateColor QColor(Qt::cyan)
	#define ReadStateColor QColor(Qt::darkCyan)
	#define ErrorStateColor QColor(Qt::red)
	#define ClosingStateColor QColor(Qt::darkGray)
*/
	final static int boundary=2;
	

	private TextView mAzimuthField;
	
	private TextView mAccelometerXField;
	private TextView mAccelometerYField;
	private TextView mAccelometerZField;
	
	private static int mConnectionStateColor;
	private static ConnectionState mConnectionState;
	
	private static ImageView mWalleImage;
	private static ImageView mEwaImage;
	
	private static Sensation mDriveSensation;
	private static Sensation mHearDirectionSensation;
	private static Sensation mAzimuthSensation;
	private static Sensation mAccelerationSensation;
	private static Sensation mObservationSensation;
	private static Sensation mPictureSensation;
	
	private static float mTestObservationDirection = (float)-Math.PI;


    private PowerManager mPowerManager;
    private PowerManager.WakeLock mWakeLock;
    
	private static Button mTestButton;



	private static class StatusView extends View {
	    //private ShapeDrawable mDrawable;
		private Paint p;

	 
		// CONSTRUCTOR
		public StatusView(Context context) {
			super(context);
	    	Log.d(LOGTAG, "StatusView(Context context)");
			setFocusable(true);
 		}
		
	    public StatusView(Context context, AttributeSet attr) {
		    super(context, attr);
	    	Log.d(LOGTAG, "StatusView(Context context, AttributeSet attr)");
			setFocusable(true);
	   }
	    
 
		@Override
		protected void onDraw(Canvas canvas) {
 
			//canvas.drawColor(Color.CYAN);
			if (p == null) {
				p = new Paint();
				// smooth
				p.setAntiAlias(true);
				p.setStyle(Paint.Style.FILL); 
			}
			//canvas.drawColor(Color.GRAY);
			p.setColor(mConnectionStateColor);
			//canvas.drawCircle(20, 20, 5, p);
			p.setStrokeWidth((float) this.getHeight()/2);
			canvas.drawCircle(this.getWidth()/2, this.getHeight()/2, this.getHeight()/4, p);
//			canvas.drawOval(new RectF(0, 0, this.getWidth(), this.getHeight()), p);
			
	    	//mDrawable.draw(canvas);

		}
 
	}
	
	private StatusView mStatusView;
	

	



	private static class World extends View {
		
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
	        
	        if (mAzimuthSensation != null)
	        {
		        canvas.save(); //Save the position of the canvas.
		        canvas.rotate((float) Math.toDegrees(mAzimuthSensation.getAzimuth()), X, Y); //Rotate the canvas.
		        canvas.drawBitmap(mWalle, X - (walleW / 2.0f), Y - (walleH / 2.0f), null); //Draw the Walle on the rotated canvas.
		        canvas.restore(); //Rotate the canvas back so that it looks like Walle has rotated.
	        }
	
	        //Draw Hearing
	        if ((mAzimuthSensation != null) && (mHearDirectionSensation != null))
	        {
	        	double angle = (double) (mAzimuthSensation.getAzimuth() + mHearDirectionSensation.getHearDirection()) - Math.PI/2.0d; // convert azimuth coordination to drawing coordination
	        	float x = (float) ((float)X + (hearingDistance * Math.cos(angle)) - (earW / 2.0f));
	        	float y = (float) ((float)Y + (hearingDistance * Math.sin(angle)) - (earH / 2.0f));
		        canvas.drawBitmap(	mEar,
    					x,
    					y,
						null); //Draw the mEva on the rotated canvas.
	        }

	        //Draw mEva
	        if (mObservationSensation != null)
	        {
	        	float h = mObservationSensation.getObservationDistance() * screen/DISTANCE; // hypotenusa as pixels
	        	double angle = mObservationSensation.getObservationDirection() - Math.PI/2.0d; // convert azimuth coordination to drawing coordination
	        	float x = (float) ((float)X + (h * Math.cos(angle)) - (evaW / 2.0f));
	        	float y = (float) ((float)Y + (h * Math.sin(angle)) - (evaH / 2.0f));
		        canvas.drawBitmap(	mEva,
    					x,
    					y,
						null); //Draw the mEva on the rotated canvas.
	        }

	        //invalidate();
	    }
	}
	
	private World mWorld;

	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
    	Log.d(LOGTAG, "onCreate()");
    	
    	mDriveSensation = null;
    	mHearDirectionSensation = null;
    	mAzimuthSensation = null;
    	mAccelerationSensation = null;
    	mObservationSensation = null;
    	mPictureSensation = null;

    	
    	mConnectionStateColor = toColor(ConnectionState.NOT_CONNECTED);
    	
		setContentView(R.layout.capabilities_main);
		
	    
	    mAzimuthField = (TextView)findViewById(R.id.azimuth_field);
	    
	    mAccelometerXField = (TextView)findViewById(R.id.accelerometer_x_field);
	    mAccelometerYField = (TextView)findViewById(R.id.accelerometer_y_field);
	    mAccelometerZField = (TextView)findViewById(R.id.accelerometer_z_field);
	    
	    mWalleImage = (ImageView)findViewById(R.id.walle_image);
	    mEwaImage = (ImageView)findViewById(R.id.walle_image);
		mWorld = (World)findViewById(R.id.world);
		
		mTestButton = (Button)findViewById(R.id.test_button);
		mTestButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
            	mTestObservationDirection += (float) Math.PI/36.0f;
            	if (mTestObservationDirection > (float) Math.PI)
            		mTestObservationDirection = (float) -Math.PI;
            	onSensation(new Sensation(0, Sensation.Memory.Working, Sensation.Direction.In, Sensation.SensationType.Observation, mTestObservationDirection, 4.0f));
                // Perform action on click
            }
        });

	    
	    mPowerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
	    mWakeLock = mPowerManager.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "CapabilitiesActivity");
	    mWakeLock.acquire();
	    
    	Log.d(LOGTAG, "onCreate() (StatusView) findViewById(R.id.statusview)");
	    mStatusView = (CapabilitiesActivity.StatusView) findViewById(R.id.statusview);
    	Log.d(LOGTAG, "onCreate() done");
	    
	}
	
	@Override
	protected void onResume() {
		super.onResume();
		mStatusView.invalidate();
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
		mAzimuthField.setText(String.format("%5.2f", aAzimuth));
		// TODO Auto-generated method stub
		
	}
	@Override
	protected void onAccelerometer(float[] aAccelerometer) {
		mAccelometerXField.setText(String.format("%5.2f", aAccelerometer[0]));
		mAccelometerYField.setText(String.format("%5.2f", aAccelerometer[1]));
		mAccelometerZField.setText(String.format("%5.2f", aAccelerometer[2]));
		
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
	    Log.d(LOGTAG, "onConnectionState " + aConnectionState.toString());
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
	    	case Drive:
	        	mDriveSensation = aSensation;
	        	break;
	    	case HearDirection:
	        	mHearDirectionSensation = aSensation;
	        	mWorld.invalidate();
	        	break;
	    	case Azimuth:
	        	mAzimuthSensation = aSensation;
	        	mWorld.invalidate();
	        	break;
	    	case Acceleration:
	        	mAccelerationSensation = aSensation;
	        	break;
	    	case Observation:
	        	mObservationSensation = aSensation;
	        	mWorld.invalidate();
	        	break;
	    	case Picture:
	        	mPictureSensation = aSensation;
	        	break;
	    }

	}

	
	/////////////////////////////////////////////////////////////
	//
	// implementation
	
    public void setStatus(ConnectionState aConnectionState) {
    	Log.d(LOGTAG, "setStatus()");
    	
    	mConnectionState = aConnectionState;
    	mConnectionStateColor = toColor(mConnectionState);
   		mStatusView.invalidate();
   }

   private int toColor(ConnectionState aConnectionState) {
    	Log.d(LOGTAG, "toColor()");
    	int color = Color.GRAY;
    	
    	switch (aConnectionState) {
    		case NOT_CONNECTED:
    			color = Color.GRAY;
    			break;
    		case CONNECTING:
    			color = Color.YELLOW;
    			break;
    		case CONNECTED:
    			color = Color.GREEN;
    			break;
    		case WRITING:
    			color = Color.BLUE;
    			break;
    		case READING:
    			color = Color.BLACK;
    			break;
    		case NO_HOST:
    			color = Color.MAGENTA;
    			break;
    		case SOCKET_ERROR:
    			color = Color.RED;
    			break;
    		case IO_ERROR:
    			color = Color.CYAN;
    		default:
    			break;
    	}
    	
    	return color;
   }

}
