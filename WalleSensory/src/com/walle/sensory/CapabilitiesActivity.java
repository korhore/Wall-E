package com.walle.sensory;

import android.content.Context;
import android.content.Intent;
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


    private PowerManager mPowerManager;
    private PowerManager.WakeLock mWakeLock;


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

	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
    	Log.d(LOGTAG, "onCreate()");
    	
    	mConnectionStateColor = toColor(ConnectionState.NOT_CONNECTED);
    	
		setContentView(R.layout.capabilities_main);
		
	    
	    mAzimuthField = (TextView)findViewById(R.id.azimuth_field);
	    
	    mAccelometerXField = (TextView)findViewById(R.id.accelerometer_x_field);
	    mAccelometerYField = (TextView)findViewById(R.id.accelerometer_y_field);
	    mAccelometerZField = (TextView)findViewById(R.id.accelerometer_z_field);
	    
	    mWalleImage = (ImageView)findViewById(R.id.walle_image);
	    
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
