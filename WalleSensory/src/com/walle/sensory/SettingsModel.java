package com.walle.sensory;

import android.content.SharedPreferences;

public class SettingsModel {
	private static final String TAG = "SettingsModel";
	
    public static final String SETTINGS_PREFS_NAME = "WalleCapabilitiesSettingsPrefs";
    //private static final String FALSE = "false";
    private static final String HOST_NAME = "host";
    private static final String PORT_NAME = "port";
    
	final private int PORT = 2000;
	final private String HOST = "10.0.0.55";

	private int mPort = PORT ;
	private String mHost = HOST;
	
	SharedPreferences mPrefs;
	
	SettingsModel(SharedPreferences aPrefs) {
		
		mPrefs = aPrefs;
	
		mHost = mPrefs.getString(HOST_NAME, (String) HOST);
		mPort = mPrefs.getInt(PORT_NAME, PORT);
	}
	

	public int getPort() {
		return mPort;
	}

	public void setPort(int mPort) {
		this.mPort = mPort;
		mPrefs.getInt(PORT_NAME, PORT);
		// save permanently
        SharedPreferences.Editor editor = mPrefs.edit();
        editor.putInt(PORT_NAME, mPort);

        // Commit the edits!
        editor.commit();
	}

	public String getHost() {
		return mHost;
	}

	public void setHost(String mHost) {
		this.mHost = mHost;
		// save permanently
        SharedPreferences.Editor editor = mPrefs.edit();
        editor.putString(HOST_NAME, mHost);

        // Commit the edits!
        editor.commit();
	}


}
