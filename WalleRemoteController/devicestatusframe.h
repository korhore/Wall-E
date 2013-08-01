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


#ifndef DEVICESTATUSFRAME_H
#define DEVICESTATUSFRAME_H

#include <QFrame>
#include "command.h"
#include "tuningbean.h"
#include "devicemanager.h"

class QwtSlider;
class DeviceStateWidget;

class DeviceStatusFrame : public QFrame
{
    Q_OBJECT
public:
    DeviceStatusFrame( QWidget *p=NULL );

signals:
    //void powerChanged( double leftPower, double rightPower );
    virtual void tuningChanged(TuningBean* aTuningBean );
    void camaraToggled(bool checked);

public Q_SLOTS:
    //void setpower( bool running, double leftPower, double rightPower );
    void setCommand(Command command);
    //virtual void setPower( double leftPower, double rightPower );
    virtual void setTuning(TuningBean* aTuningBean);
    //virtual void setSpeedDirection( double speed, double direction );

    // show device state
    // tries to change power and send comand to device
    void showPowerChanged( double leftPower, double rightPower );
    // device has processed command and set it to this status
    void showCommandProsessed(Command command);
    // device has processed command and set it to this tuning
    void showDeviceStateChanged(TuningBean* aTuningBean);
    // device state has changed
    void showDeviceStateChanged(DeviceManager::DeviceState aDeviceState);
    // if device state error, also error is emitted
    void showDeviceError(QAbstractSocket::SocketError socketError);


private Q_SLOTS:
    void handleSettings();
    void handleCamaraToggled(bool checked);
    void handleLeftPowerChange( double leftPower );
    void handleRightPowerChange( double rightPower );


private:
    QwtSlider *mLeftPowerSlider;
    DeviceStateWidget *mDeviceStateWidget;
    QwtSlider *mRightPowerSlider;

    bool mRunning;
    double mLeftPower;
    double mRightPower;
};

#endif // DEVICESTATUSFRAME_H





