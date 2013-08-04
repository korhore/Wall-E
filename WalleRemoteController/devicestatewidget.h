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

#ifndef DEVICESTATEWIDGET_H
#define DEVICESTATEWIDGET_H

#include <QWidget>
#include <QLabel>
#include "command.h"
#include "devicemanager.h"

class TuningBean;

class DeviceStateWidget : public QLabel
{
    Q_OBJECT

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

public:
    explicit DeviceStateWidget(QWidget *parent = 0);

    void paintEvent(QPaintEvent *);

    
signals:
    
public slots:
    // tries to change power and send command to device
    void showPowerChanged( double leftPower, double rightPower );
    // device has processed command and set it to this status
    void showCommandProsessed(Command command);
    // device has processed command and set it to this tuning
    void showDeviceStateChanged(TuningBean* aTuningBean);
    // device state has changed
    void showDeviceStateChanged(DeviceManager::DeviceState aDeviceState);
    // if device state error, also error is emitted
    void showDeviceError(QAbstractSocket::SocketError socketError);


private:
    bool mPowerChanged;
    QAbstractSocket::SocketError mSocketError;
    DeviceManager::DeviceState mDeviceState;



};

#endif // DEVICESTATEWIDGET_H
