/* -------------------------------------------

    WalleRemoteContoller is an educational application to control a robot or other device using WLAN

    Copyright (C) 2013 Reijo Korhonen, reijo.korhonen@gmail.com
    All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

--------------------------------------------- */


#ifndef DEVICEMANAGER_H
#define DEVICEMANAGER_H


/*

Model class that controls device, is this case Ealle-E robot.
Takes tuning as input and produces command that it sends using wlan
to the device

*/

#include <QObject>
#include <QAbstractSocket>
#include "command.h"
class FtpClient;
class TuningBean;

class DeviceManager : public QObject
{
    Q_OBJECT
public:

    // Devices State
    enum DeviceState { UnconnectedState, // The socket is not connected
                       HostLookupState,  // The socket is performing a host name lookup
                       ConnectingState,  // The socket has started establishing a connection
                       ConnectedState,   // A connection is established
                       WritingState,     // A connection is wrting
                       WrittenState,     // A connection has written all
                       ReadingState,     // A connection has something to read
                       ReadState,        // A connection has read all
                       ErrorState,       // Error in connection
                       ClosingState      // The socket is about to close (data may still be waiting to be written).
                     };


    explicit DeviceManager( QObject *p );
    virtual ~DeviceManager();


    bool test();

Q_SIGNALS:
    // tries to change power and send comand to device
    void powerChanged( double leftPower, double rightPower );
    // device has processed command and set it to this status
    void commandProsessed(Command command);
    // device has processed command and set it to this tuning
    void deviceStateChanged(TuningBean* aTuningBean);
    // device state has changed
    void deviceStateChanged(DeviceManager::DeviceState aDeviceState);
    // if device state error, also error is emitted
    void deviceError(QAbstractSocket::SocketError socketError);


public Q_SLOTS:
    virtual void setTuning(TuningBean* aTuningBean );
    void setHost(QString ipAddress, int port);

private Q_SLOTS:
    void handleCommandProsessed(Command command);
    void handleDeviceStateChanged(DeviceManager::DeviceState aDeviceState);



private:
    // Slider tuner
    double mDirection;
    double mSpeed;


    // Power
    double mLeftPower;
    double mRightPower;
    //bool mRunning;      // is car moving or topped

    FtpClient* mFtpClient;
    QString ipAddress;
    int port;
    Command mLastComand;
    Command mCandidateCommand;


};

#endif // DEVICEMANAGER_H





