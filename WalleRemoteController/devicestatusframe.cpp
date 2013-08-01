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

#include <qlayout.h>
#include <qlabel.h>
#include <QPushButton>
#include <QPixmap>

#include <qwt_wheel.h>
#include <qwt_slider.h>
#include <qwt_thermo.h>
#include <qwt_math.h>
#include "devicestatusframe.h"
#include "settingsdialog.h"
#include "ftpclient.h"
#include "tuningbean.h"
#include "devicestatewidget.h"

/*
#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif
*/
#if defined(Q_WS_S60)
#define WIDTH     20
#else
#define WIDTH     30
#endif

DeviceStatusFrame::DeviceStatusFrame( QWidget *parent ):
   QFrame( parent )
{
    // in the top "led" that shows devices state
    // ans setting button

    mDeviceStateWidget = new DeviceStateWidget(this);

#if defined(Q_WS_S60)
    QPushButton* mSettingsButton = new QPushButton(tr("Set"), this);
    mSettingsButton->setPalette( QPalette( QColor( 128, 128, 128 ) ) );
#else
    QPushButton* mSettingsButton = new QPushButton(tr("Sett."), this);
#endif
    mSettingsButton->setIcon(QIcon(QPixmap(":pictures/settings.png")));
    mSettingsButton->setIconSize(QSize(WIDTH,WIDTH));
    connect(mSettingsButton, SIGNAL(clicked(bool)), this, SLOT(handleSettings()));

    QWidget *device = new QWidget(this);
    QHBoxLayout *deviceLayout = new QHBoxLayout( device );
    deviceLayout->setMargin( 1 );
    deviceLayout->setSpacing( 1 );
    deviceLayout->addWidget( mDeviceStateWidget );
    deviceLayout->addWidget( mSettingsButton );


    // below camera state button

    QPushButton* mCameraButton = new QPushButton(this);
    mCameraButton->setIcon(QIcon(QPixmap(":pictures/settings.png")));
    mCameraButton->setIconSize(QSize(WIDTH,WIDTH));
    mCameraButton->setCheckable ( true );
    mCameraButton->setChecked ( true );
    mCameraButton->setPalette( QPalette( QColor( 128, 128, 128 ) ) );
    connect(mCameraButton, SIGNAL(toggled(bool)), this, SLOT(handleCamaraToggled(bool)));


    // Left power

    QWidget *leftWidget = new QWidget(this);
    qDebug() << "mLeftPowerSlider";
    mLeftPowerSlider = new  QwtSlider( leftWidget, Qt::Vertical, QwtSlider::LeftScale );

    mLeftPowerSlider->setRange( -1.0, 1.0 );
    mLeftPowerSlider->setScaleMaxMinor( 2 );
    mLeftPowerSlider->setScaleMaxMajor( 3 );
    mLeftPowerSlider->setBorderWidth( 1 );
    mLeftPowerSlider->setEnabled(false);

    qDebug() << "leftLabel";
    QLabel *leftLabel = new QLabel( "Left", leftWidget );
    leftLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "leftLayout";
    QVBoxLayout *leftLayout = new QVBoxLayout( leftWidget );
    leftLayout->setMargin( 2 );
    leftLayout->setSpacing( 1 );
    leftLayout->addWidget( mLeftPowerSlider, WIDTH );
    leftLayout->addStretch(3);
    leftLayout->addWidget( leftLabel );

    // Right Power

    QWidget *rightWidget = new QWidget(this);
    qDebug() << "mRightPowerSlider";
    mRightPowerSlider = new  QwtSlider( rightWidget, Qt::Vertical, QwtSlider::LeftScale );

    mRightPowerSlider->setRange( -1.0, 1.0 );
    mRightPowerSlider->setScaleMaxMinor( 2 );
    mRightPowerSlider->setScaleMaxMajor( 3 );
    mRightPowerSlider->setBorderWidth( 1 );
    mRightPowerSlider->setEnabled(false);



    qDebug() << "rightLabel";
    QLabel *rightLabel = new QLabel( tr("Right"), rightWidget );
    rightLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "rightLayout";
    QVBoxLayout *rightLayout = new QVBoxLayout( rightWidget );
    rightLayout->setMargin( 2 );
    rightLayout->setSpacing( 1 );
    rightLayout->addWidget( mRightPowerSlider, WIDTH );
    rightLayout->addStretch( 1 );
    rightLayout->addWidget( rightLabel );


    qDebug() << "powerLayout";
    QWidget *power = new QWidget(this);

    QHBoxLayout *powerLayout = new QHBoxLayout( power );
    powerLayout->setMargin( 1 );
    powerLayout->setSpacing( 1 );
    powerLayout->addWidget( leftWidget );
    powerLayout->addWidget( rightWidget );

    // Combine all to main layout

    qDebug() << "mainLayout";
    QVBoxLayout *mainLayout = new QVBoxLayout( this );
    mainLayout->setMargin( 2 );
    mainLayout->addWidget(device/*mDeviceStateWidget /*, WIDTH , 0, Qt::AlignCenter*/);

    mainLayout->addWidget(mCameraButton );

    mainLayout->addWidget(power);

    qDebug() << "DeviceLabel";
    QLabel *deviceLabel = new QLabel( "Device Status", this );
    deviceLabel->setAlignment( Qt::AlignCenter );
    mainLayout->addWidget(deviceLabel);
    mainLayout->addStretch(20);

    setLayout(mainLayout);


    qDebug() << "end";

}

void DeviceStatusFrame::handleLeftPowerChange( double leftPower )
{
    qDebug() << "DeviceStatusFrame::handleLeftPowerChange leftPower " << leftPower;
    mLeftPower = leftPower;
    //emit powerChanged( mLeftPower, mRightPower );
    emit tuningChanged(new TuningBean(TuningBean::SCALE_POWERS, mLeftPower, mRightPower, this));

}

void DeviceStatusFrame::handleRightPowerChange( double rightPower )
{
    qDebug() << "DeviceStatusFrame::handleRightPowerChangee rightPower " << rightPower;
    mRightPower = rightPower;
    //emit powerChanged( mLeftPower, mRightPower );
    emit tuningChanged(new TuningBean(TuningBean::SCALE_POWERS, mLeftPower, mRightPower, this));

}



/*
void DeviceStatusFrame::setpower( bool running, double leftPower, double rightPower )
{
    mRunning = running;
    mLeftPower = leftPower;
    mRrightPower = rightPower;

    mLeftPowerSlider->setValue(leftPower);
    mRightPowerSlider->setValue(rightPower);

}
*/

void DeviceStatusFrame::setCommand(Command command)
{
    if (command.getCommand() == Command::Drive)
    {
        mLeftPower = command.getLeftPower();
        mRightPower = command.getRightPower();

        mLeftPowerSlider->setValue(mLeftPower);
        mRightPowerSlider->setValue(mRightPower);
    }
}

/*
void DeviceStatusFrame::setPower( double leftPower, double rightPower )
{
    mLeftPower = leftPower;
    mRightPower = rightPower;

    mLeftPowerSlider->setValue(mLeftPower);
    mRightPowerSlider->setValue(mRightPower);

}
*/

void DeviceStatusFrame::setTuning( TuningBean* aTuningBean )
{
    qDebug() << "DeviceStatusFrame::setTuning";

    mLeftPower = aTuningBean->getLeftPower();
    mRightPower = aTuningBean->getRightPower();

    mLeftPowerSlider->setValue(mLeftPower);
    mRightPowerSlider->setValue(mRightPower);
}




void DeviceStatusFrame::handleSettings()
{
    SettingsDialog settingsDialog(this, QString(SERVERNAME), SERVERPORT);
    settingsDialog.exec();

}

void DeviceStatusFrame::handleCamaraToggled(bool checked)
{
    emit camaraToggled(checked);
}

// tries to change power and send comand to device
void DeviceStatusFrame::showPowerChanged( double leftPower, double rightPower )
{
    mDeviceStateWidget->showPowerChanged( leftPower, rightPower );
}

// device has processed command and set it to this status
void DeviceStatusFrame::showCommandProsessed(Command command)
{
    mDeviceStateWidget->showCommandProsessed(command);
}

// device has processed command and set it to this tuning
void DeviceStatusFrame::showDeviceStateChanged(TuningBean* aTuningBean)
{
    mDeviceStateWidget->showDeviceStateChanged(aTuningBean);
}

// device state has changed
void DeviceStatusFrame::showDeviceStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "DeviceStatusFrame::showDeviceStateChanged";
    mDeviceStateWidget->showDeviceStateChanged(aDeviceState);
}

// if device state error, also error is emitted
void DeviceStatusFrame::showDeviceError(QAbstractSocket::SocketError socketError)
{
    mDeviceStateWidget->showDeviceError(socketError);
}


