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
#include <qwt_wheel.h>
#include <qwt_slider.h>
#include <qwt_thermo.h>
#include <qwt_math.h>
#include "slidertunerframe.h"
#include "devicestatusframe.h"
#include "devicemanager.h"

/*
#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif
*/
#if defined(Q_WS_S60)
#define SLIDERHIGHT     400
#define SLIDERWIDTH     20
#define HANDLE_HEIGHT   50
#define HANDLE_WIDTH    30
#define SPEED_WIDTH     30
#define DIRECTION_WIDTH 50
#define STRECH          5
#else
#define SLIDERHIGHT     500
#define SLIDERWIDTH     350
#define HANDLE_HEIGHT   60
#define HANDLE_WIDTH    40
#define SPEED_WIDTH     40
#define DIRECTION_WIDTH 200
#define STRECH          20
#endif
SliderTunerFrame::SliderTunerFrame( QWidget *parent ):
   TunerFrame( parent )
{
    QWidget *direction = new QWidget(this);
    qDebug() << "mSliderDirection";
    mSliderDirection = new QwtSlider( direction, Qt::Horizontal, QwtSlider::TopScale );
    mSliderDirection->setRange( -90.0, 90.0, 0.1, 45 );
    mSliderDirection->setScaleMaxMinor( 3 );
    mSliderDirection->setScaleMaxMajor( 5 );
    mSliderDirection->setHandleSize( HANDLE_HEIGHT, HANDLE_WIDTH );
    mSliderDirection->setBorderWidth( 2 );

    qDebug() << "directionLabel";
    QLabel *directionLabel = new QLabel( "Direction", direction );
    directionLabel->setAlignment( Qt::AlignCenter );
    direction->setFixedWidth( 5 * directionLabel->sizeHint().width()/3 );

    mDeviceStatusFrame = new DeviceStatusFrame(direction);

    qDebug() << "directionLayout";
    QVBoxLayout *directionLayout = new QVBoxLayout( direction );
    directionLayout->setMargin( 3 );
    directionLayout->setSpacing( 2 );
    directionLayout->addWidget( mDeviceStatusFrame );
    directionLayout->addStretch( STRECH );
    directionLayout->addWidget( mSliderDirection, SLIDERWIDTH );
    directionLayout->addWidget( directionLabel );

    connect(mSliderDirection, SIGNAL(sliderMoved(double)), this, SLOT(handleDirectionChange(double)));


    QWidget *speed = new QWidget(this);
    qDebug() << "mSliderSpeed";
    mSliderSpeed = new QwtSlider( speed, Qt::Vertical, QwtSlider::LeftScale );
    mSliderSpeed->setRange( -1.0, 1.0 );
    mSliderSpeed->setScaleMaxMinor( 3 );
    mSliderSpeed->setScaleMaxMajor( 5 );
    mSliderSpeed->setHandleSize( HANDLE_WIDTH, HANDLE_HEIGHT );
    mSliderSpeed->setBorderWidth( 2 );

    qDebug() << "speedLabel";
    QLabel *speedLabel = new QLabel( "Speed", speed );
    speedLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "speedLayout";
    QVBoxLayout *speedLayout = new QVBoxLayout( speed );
    speedLayout->setMargin( 3 );
    speedLayout->setSpacing( 2 );
    speedLayout->addWidget( mSliderSpeed, SLIDERHIGHT );
    speedLayout->addStretch( 5 );
    speedLayout->addWidget( speedLabel );

    connect(mSliderSpeed, SIGNAL(sliderMoved(double)), this, SLOT(handleSpeedChange(double)));

    qDebug() << "mainLayout";
    QHBoxLayout *mainLayout = new QHBoxLayout( this );
    qDebug() << "mainLayout1";
    mainLayout->setMargin( 3 );
    qDebug() << "mainLayout2";
    mainLayout->setSpacing( 2 );
    qDebug() << "mainLayout3";
    mainLayout->addWidget( speed/*, SPEED_WIDTH*/ );
    qDebug() << "mainLayout4";
    mainLayout->addWidget( direction/*, DIRECTION_WIDTH*/ );
    qDebug() << "mainLayout5";

    setLayout(mainLayout);

    qDebug() << "end";

}



void SliderTunerFrame::setTuning( TuningBean* aTuningBean )
{
    qDebug() << "SliderTunerFrame.setTuning";

    mSpeed = aTuningBean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES);
    mDirection = aTuningBean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES);

    mSliderSpeed->setValue( mSpeed );
    mSliderDirection->setValue( mDirection );
}


void SliderTunerFrame::setPower( double leftPower, double rightPower )
{
    qDebug() << "SliderTunerFrame::setSpeedDirection leftPower " << leftPower << " rightPower "  << rightPower;
    // TODO
    // set powers to direction and speed
}

void SliderTunerFrame::setCommand(Command command)
{
    mDeviceStatusFrame->setCommand(command);
}

void SliderTunerFrame::handleDirectionChange( double direction )
{
    qDebug() << "SliderTunerFrame.handleDirectionChange";
    mDirection = direction;
    emit tuningChanged(new TuningBean(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection, this));

}

void SliderTunerFrame::handleSpeedChange( double speed )
{
    qDebug() << "SliderTunerFrame.handleSpeedChange";
    mSpeed = speed;
    emit tuningChanged(new TuningBean(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection, this));
}

// tries to change power and send comand to device
void SliderTunerFrame::showPowerChanged( double leftPower, double rightPower )
{
    mDeviceStatusFrame->showPowerChanged( leftPower, rightPower );
}

// device has processed command and set it to this status
void SliderTunerFrame::showCommandProsessed(Command command)
{
    mDeviceStatusFrame->showCommandProsessed(command);
}

// device has processed command and set it to this tuning
void SliderTunerFrame::showDeviceStateChanged(TuningBean* aTuningBean)
{
    qDebug() << "SliderTunerFrame::showDeviceStateChanged";
    mDeviceStatusFrame->showDeviceStateChanged(aTuningBean);
}

// device state has changed
void SliderTunerFrame::showDeviceStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "SliderTunerFrame::showDeviceStateChanged";
    mDeviceStatusFrame->showDeviceStateChanged(aDeviceState);
}

// if device state error, also error is emitted
void SliderTunerFrame::showDeviceError(QAbstractSocket::SocketError socketError)
{
    mDeviceStatusFrame->showDeviceError(socketError);
}


