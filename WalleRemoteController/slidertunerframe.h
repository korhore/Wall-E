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


#ifndef SLIDERTUNERFRAME_H
#define SLIDERTUNERFRAME_H

#include <QFrame>
#include "tunerframe.h"

class QwtSlider;
class DeviceStatusFrame;

class SliderTunerFrame : public TunerFrame
{
    Q_OBJECT
public:
    SliderTunerFrame( QWidget *p=NULL );

Q_SIGNALS:
    virtual void tuningChanged(TuningBean* aTuningBean );

public Q_SLOTS:
    virtual void setTuning(TuningBean* aTuningBean);
    virtual void setPower( double leftPower, double rightPower );
    void setCommand(Command command);

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
    void handleDirectionChange( double direction );
    void handleSpeedChange( double speed );


private:
    DeviceStatusFrame* mDeviceStatusFrame;

    QwtSlider *mSliderSpeed;
    QwtSlider *mSliderDirection;

    double mSpeed;
    double mDirection;
};

#endif // SLIDERTUNERFRAME_H




