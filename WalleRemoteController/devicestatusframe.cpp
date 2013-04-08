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

/*
#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif
*/

DeviceStatusFrame::DeviceStatusFrame( QWidget *parent ):
   QFrame( parent )
{
    setBaseSize(50,50);
    QWidget *leftWidget = new QWidget(this);
    qDebug() << "mLeftPowerSlider";
    mLeftPowerSlider = new  QwtSlider( leftWidget, Qt::Vertical, QwtSlider::LeftScale );

    mLeftPowerSlider->setRange( -1.0, 1.0 );
    mLeftPowerSlider->setScaleMaxMinor( 2 );
    mLeftPowerSlider->setScaleMaxMajor( 3 );
    mLeftPowerSlider->setBorderWidth( 1 );

    qDebug() << "leftLabel";
    QLabel *leftLabel = new QLabel( "Left", leftWidget );
    leftLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "leftLayout";
    QVBoxLayout *leftLayout = new QVBoxLayout( leftWidget );
    leftLayout->setMargin( 2 );
    leftLayout->setSpacing( 1 );
    leftLayout->addWidget( mLeftPowerSlider, 40 );
    leftLayout->addStretch( 3);
    leftLayout->addWidget( leftLabel );

    // right

    QWidget *rightWidget = new QWidget(this);
    qDebug() << "mRightPowerSlider";
    mRightPowerSlider = new  QwtSlider( rightWidget, Qt::Vertical, QwtSlider::LeftScale );

    mRightPowerSlider->setRange( -1.0, 1.0 );
    mRightPowerSlider->setScaleMaxMinor( 2 );
    mRightPowerSlider->setScaleMaxMajor( 3 );
    mRightPowerSlider->setBorderWidth( 1 );

    qDebug() << "rightLabel";
    QLabel *rightLabel = new QLabel( tr("Right"), rightWidget );
    rightLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "rightLayout";
    QVBoxLayout *rightLayout = new QVBoxLayout( rightWidget );
    rightLayout->setMargin( 2 );
    rightLayout->setSpacing( 1 );
    rightLayout->addWidget( mRightPowerSlider, 40 );
    rightLayout->addStretch( 3 );
    rightLayout->addWidget( rightLabel );



    qDebug() << "powerLayout";
    QWidget *power = new QWidget(this);

    QHBoxLayout *powerLayout = new QHBoxLayout( power );
    powerLayout->setMargin( 1 );
    powerLayout->setSpacing( 1 );
    powerLayout->addWidget( leftWidget );
    powerLayout->addWidget( rightWidget );

    qDebug() << "mainLayout";
    QVBoxLayout *mainLayout = new QVBoxLayout( this );
    mainLayout->setMargin( 2 );
    //mainLayout->addStretch(20);
    mainLayout->addWidget(power, 30);

    qDebug() << "DeviceLabel";
    QLabel *deviceLabel = new QLabel( "Device Status", leftWidget );
    deviceLabel->setAlignment( Qt::AlignCenter );
    mainLayout->addWidget(deviceLabel, 30);

    setLayout(mainLayout);

    setEnabled(false);


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


/*
void DeviceStatusFrame::setSpeedDirection( double speed, double direction )
{
    qDebug() << "SliderTunerFrame.setSpeedDirection";
    // convert values to
    // -90.0 <= direction <= 90.0
    // -1.0 <= speed <= 1.0

    if (direction > 180.0)  { // value range
        direction = 180.0;
    } else
    if (direction < -180.0) {
        direction = -180.0;
    };

    if (speed > 1.0) {  // value range
        speed = 1.0;
    } else
    if (speed < -1.0) {
        speed = -1.0;
    };

    if (direction > 90.0) { // turnning right, backward
        direction -= 90.0;
        speed = -speed;
    } else
    if (direction < -90.0) { // turnning left, backward
        direction += 90.0;
        speed = -speed;
    };

    Q_ASSERT((-90.0 <= direction) && (direction <= 90.0) && (-1.0 <= speed) && (speed <= 1.0));

    mSliderSpeed->setValue( speed );
    mSliderDirection->setValue( direction );
}
*/


void DeviceStatusFrame::handleSettings()
{
    SettingsDialog settingsDialog(this, QString(SERVERNAME), SERVERPORT);
    settingsDialog.exec();

}

