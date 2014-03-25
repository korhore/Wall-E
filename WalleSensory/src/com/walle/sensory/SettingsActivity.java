package com.walle.sensory;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.EditText;

import com.walle.sensory.server.WalleSensoryServer.ConnectionState;
import com.walle.sensory.server.WalleSensoryServerClient;

public class SettingsActivity extends WalleSensoryServerClient {
	final String LOGTAG="SettingsActivity";

	
	private static final String IP_PATTERN = 
	        "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
	        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
	        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
	        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$";



    private EditText mHostField;
    private EditText mPortField;

	
	public static boolean validate(final String ip){          
	      Pattern pattern = Pattern.compile(IP_PATTERN);
	      Matcher matcher = pattern.matcher(ip);
	      return matcher.matches();             
	}


	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
	
		setContentView(R.layout.capabilities_settings);
		
	    mHostField = (EditText)findViewById(R.id.host_field);
	    mHostField.addTextChangedListener((new TextWatcher() {

			@Override
			public void afterTextChanged(Editable s) {
				// TODO Auto-generated method stub
				if (!validate(s.toString()))
					mHostField.setError("IP Format FINAL error");
				else
					setHost(s.toString());
			}

			@Override
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				// TODO Auto-generated method stub
				
			}

			@Override
			public void onTextChanged(CharSequence s, int start, int before,
					int count) {
				if (!validate(mHostField.getText().toString()))
						mHostField.setError("IP Format editing error");
				else
					setHost(mHostField.getText().toString());

				
			}
	    	
	    }));
	    
	    mPortField = (EditText)findViewById(R.id.port_field);
	    mPortField.addTextChangedListener((new TextWatcher() {

			@Override
			public void afterTextChanged(Editable s) {
				 setPort(Integer.parseInt(s.toString()));
			}

			@Override
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				// TODO Auto-generated method stub
				
			}

			@Override
			public void onTextChanged(CharSequence s, int start, int before,
					int count) {
				setPort(Integer.parseInt(mPortField.getText().toString()));
			}
	    	
	    }));
	    

	}
	


	///////////////////////////
	//
	// abstract methods implementation

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
		mHostField.setText(aHost);		
	}


	@Override
	protected void onPort(int aPort) {
	    mPortField.setText(String.valueOf(aPort));
	}


	@Override
	protected void onConnectedService() {
		// get data from service
	    getHost();
	    getPort();
	}


	@Override
	protected void onDisconnectedService() {
		// TODO Auto-generated method stub
		
	}


	@Override
	protected void onConnectionState(ConnectionState aConnectionState) {
		// TODO Auto-generated method stub
		
	}
		 
		 
		  
	


}
