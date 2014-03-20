package com.walle.sensory;

import android.content.Context;
import android.content.Intent;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.drawable.ShapeDrawable;
import android.graphics.drawable.shapes.OvalShape;
import android.os.Bundle;
import android.os.PowerManager;
import android.util.AttributeSet;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.walle.sensory.server.WalleSensoryServerClient;


public class CapabilitiesActivity extends WalleSensoryServerClient  {
	final static String LOGTAG="CapabilitiesActivity";
	final static int boundary=2;
	

	private TextView mAzimuthField;
	
	private TextView mAccelometerXField;
	private TextView mAccelometerYField;
	private TextView mAccelometerZField;



    private PowerManager mPowerManager;
    private PowerManager.WakeLock mWakeLock;


	private static class StatusView extends View {
	    private ShapeDrawable mDrawable;
	 
		// CONSTRUCTOR
		public StatusView(Context context) {
			super(context);
	    	Log.d(LOGTAG, "StatusView(Context context)");
			setFocusable(true);
 		}
		
	    public StatusView(Context context, AttributeSet attr) {
		    super(context);
	    	Log.d(LOGTAG, "StatusView(Context context, AttributeSet attr)");
			setFocusable(true);
	   }
	    
	    public void setStatus() {
	    	Log.d(LOGTAG, "setStatus()");
			
		    int x = boundary;
		    int y = boundary;
		    int width = this.getWidth()-boundary;
		    int height = this.getHeight()-boundary;
		    
		    mDrawable = new ShapeDrawable(new OvalShape());
		    mDrawable.getPaint().setColor(0xff74AC23);
		    mDrawable.setBounds(x, y, x + width, y + height);
	   }


 
		@Override
		protected void onDraw(Canvas canvas) {
 
			//canvas.drawColor(Color.CYAN);
			Color color = new Color();
			color.argb(0x10, 0x10, 0x10, 0x10);
			canvas.drawColor(0x10101010);
			Paint p = new Paint();
			// smooths
			p.setAntiAlias(true);
			p.setColor(Color.RED);
			p.setStyle(Paint.Style.STROKE); 
			p.setStrokeWidth(4.5f);
			// opacity
			//p.setAlpha(0x80); //
			canvas.drawCircle(10, 10, 10, p);
			
	    	//mDrawable.draw(canvas);

		}
 
	}
	
	private StatusView mStatusView;

	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
    	Log.d(LOGTAG, "onCreate()");
		setContentView(R.layout.capabilities_main);
		
	    
	    mAzimuthField = (TextView)findViewById(R.id.azimuth_field);
	    
	    mAccelometerXField = (TextView)findViewById(R.id.accelerometer_x_field);
	    mAccelometerYField = (TextView)findViewById(R.id.accelerometer_y_field);
	    mAccelometerZField = (TextView)findViewById(R.id.accelerometer_z_field);
	    
	    mPowerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
	    mWakeLock = mPowerManager.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "CapabilitiesActivity");
	    mWakeLock.acquire();
	    
    	Log.d(LOGTAG, "onCreate() (StatusView) findViewById(R.id.statusview)");
	    mStatusView = (StatusView) findViewById(R.id.statusview);
    	Log.d(LOGTAG, "onCreate() mStatusView.setStatus()");
	    //mStatusView.setStatus();
    	Log.d(LOGTAG, "onCreate() done");
	    
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
		 
		 

	


}
