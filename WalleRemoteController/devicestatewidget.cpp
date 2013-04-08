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

#include <QPen>
#include <QPainter>
#include <QLinearGradient>
#include <QRectF>
#include <QPainterPath>

#include "devicestatewidget.h"
#include "devicemanager.h"

DeviceStateWidget::DeviceStateWidget(QWidget *parent) :
    QWidget(parent),
    mPowerChanged(false),
    mDeviceState(DeviceManager::UnconnectedState )

{
    //drawState();
}

// tries to change power and send comand to device
void DeviceStateWidget::showPowerChanged( double leftPower, double rightPower )
{
    mPowerChanged = true;
    update();
}

// device has processed command and set it to this status
void DeviceStateWidget::showCommandProsessed(Command command)
{
    mPowerChanged = true;
    update();
}

// device has processed command and set it to this tuning
void DeviceStateWidget::showDeviceStateChanged(TuningBean* aTuningBean)
{
    mPowerChanged = true;
    update();
}

// device state has changed
void DeviceStateWidget::showDeviceStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "DeviceStateWidget::showDeviceStateChanged";
    mDeviceState=aDeviceState;
    update();
}

// if device state error, also error is emitted
void DeviceStateWidget::showDeviceError(QAbstractSocket::SocketError socketError)
{
    mSocketError = socketError;
    update();
}

void DeviceStateWidget::paintEvent(QPaintEvent *)
{
    qDebug() << "DeviceStateWidget::paintEvent";
    QPainter painter(this);


    QLinearGradient myGradient(0.0, 0.0, 12.0, 15.0);
    QPen myPen;
    QRectF boundingRectangle(0.0, 0.0,  12.0, 30.0);

    QPainterPath myPath;
    myPath.addEllipse(boundingRectangle);

    //QPainter painter(this);
    //painter.setBrush(myGradient);
    if (mPowerChanged) {
        painter.setBrush(PowerChangedColor);
        mPowerChanged = false;
    } else {
        switch (mDeviceState) {
            case DeviceManager::UnconnectedState:
                painter.setBrush(UnconnectedStateColor);
                break;
            case DeviceManager::HostLookupState:
                painter.setBrush(UnconnectedStateColor);
                break;
            case DeviceManager::ConnectingState:
                painter.setBrush(ConnectingStateColor);
                break;
            case DeviceManager::ConnectedState:
                painter.setBrush(ConnectedStateColor);
                break;
            case DeviceManager::WritingState:
                painter.setBrush(WritingStateColor);
                break;
            case DeviceManager:: WrittenState:
                painter.setBrush(WrittenStateColor);
                break;
            case DeviceManager::ReadingState:
                painter.setBrush(ReadingStateColor);
                break;
            case DeviceManager::ReadState:
                painter.setBrush(ReadStateColor);
                break;
            case DeviceManager::ErrorState:
                painter.setBrush(ErrorStateColor);
                break;
            case DeviceManager::ClosingState:
                painter.setBrush(ClosingStateColor);
                break;
            default:
                Q_ASSERT(false); // Logic error

        }
    }

    painter.setPen(myPen);
    painter.drawPath(myPath);
#ifdef old
    QPainterPath path;
    path.addRect(20, 20, 60, 60);

    path.moveTo(0, 0);
    path.cubicTo(99, 0,  50, 50,  99, 99);
    path.cubicTo(0, 99,  50, 50,  0, 0);

    painter.fillRect(0, 0, 100, 100, Qt::white);
    painter.setPen(QPen(QColor(79, 106, 25), 1, Qt::SolidLine,
                        Qt::FlatCap, Qt::MiterJoin));
    painter.setBrush(QColor(122, 163, 39));

    painter.drawPath(path);
#endif

}

