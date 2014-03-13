package com.walle.sensory;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Menu;
import android.widget.EditText;

public class SettingsActivity extends Activity {
	final String LOGTAG="SettingsActivity";

	
	private static final String IP_PATTERN = 
	        "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
	        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
	        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
	        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$";



    private EditText mHostField;
    private EditText mPortField;
	private SharedPreferences mPrefs;
	private SettingsModel mSettingsModel;

	
	public static boolean validate(final String ip){          
	      Pattern pattern = Pattern.compile(IP_PATTERN);
	      Matcher matcher = pattern.matcher(ip);
	      return matcher.matches();             
	}


	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		mPrefs = this.getSharedPreferences(
			      "com.walle.sensory", Context.MODE_PRIVATE);
		mSettingsModel = new SettingsModel(mPrefs);
		
		setContentView(R.layout.capabilities_settings);
		
	    mHostField = (EditText)findViewById(R.id.host_field);
	    mHostField.setText(mSettingsModel.getHost());
	    mHostField.addTextChangedListener((new TextWatcher() {

			@Override
			public void afterTextChanged(Editable s) {
				// TODO Auto-generated method stub
				if (!validate(s.toString()))
					mHostField.setError("IP Format FINAL error");
				else
					mSettingsModel.setHost(s.toString());
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
					mSettingsModel.setHost(mHostField.getText().toString());

				
			}
	    	
	    }));
	    
	    mPortField = (EditText)findViewById(R.id.port_field);
	    mPortField.setText(String.valueOf(mSettingsModel.getPort()));
	    mPortField.addTextChangedListener((new TextWatcher() {

			@Override
			public void afterTextChanged(Editable s) {
				 mSettingsModel.setPort(Integer.parseInt(s.toString()));
			}

			@Override
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				// TODO Auto-generated method stub
				
			}

			@Override
			public void onTextChanged(CharSequence s, int start, int before,
					int count) {
				mSettingsModel.setPort(Integer.parseInt(mPortField.getText().toString()));
			}
	    	
	    }));
	    

	}
	

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.capabilities, menu);
		return true;
	}
	
	protected void onResume() {
	    super.onResume();
	}
		 
	protected void onPause() {
	    super.onPause();
	}
	
	protected void onDestroy() {
		super.onDestroy();
	}
		 
		 
		  
	


}
