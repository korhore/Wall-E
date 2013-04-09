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
#include "powertunerframe.h"
#include "settingsdialog.h"
#include "ftpclient.h"
#include "tuningbean.h"

/*
#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif
*/

PowerTunerFrame::PowerTunerFrame( QWidget *parent ):
   QFrame( parent )
{
    QWidget *leftWidget = new QWidget(this);
    qDebug() << "mLeftPowerSlider";
    mLeftPowerSlider = new  QwtSlider( leftWidget, Qt::Vertical, QwtSlider::LeftScale );
    //mLeftPowerSlider->setOrientation(  Qt::Vertical, QwtThermo::LeftScale );

    mLeftPowerSlider->setRange( -1.0, 1.0 );
    //mLeftPowerSlider->setFillBrush( Qt::red );

    //mLeftPowerSlider->setAlarmLevel(0.0);
    //mLeftPowerSlider->setAlarmEnabled(true);
    //mLeftPowerSlider->setAlarmBrush( Qt::green );
    mLeftPowerSlider->setScaleMaxMinor( 3 );
    mLeftPowerSlider->setScaleMaxMajor( 5 );
    mLeftPowerSlider->setBorderWidth( 2 );

    qDebug() << "leftLabel";
    QLabel *leftLabel = new QLabel( "Left", leftWidget );
    leftLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "leftLayout";
    QVBoxLayout *leftLayout = new QVBoxLayout( leftWidget );
    leftLayout->setMargin( 3 );
    leftLayout->setSpacing( 2 );
    leftLayout->addWidget( mLeftPowerSlider, 400 );
    leftLayout->addStretch( 5 );
    leftLayout->addWidget( leftLabel );

    // right

    QWidget *rightWidget = new QWidget(this);
    qDebug() << "mRightPowerSlider";
    mRightPowerSlider = new  QwtSlider( rightWidget, Qt::Vertical, QwtSlider::LeftScale );
    //mRightPowerSlider->setOrientation(  Qt::Vertical, QwtThermo::LeftScale );

    mRightPowerSlider->setRange( -1.0, 1.0 );
    //mRightPowerSlider->setFillBrush( Qt::red );

    //mRightPowerSlider->setAlarmLevel(0.0);
    //mRightPowerSlider->setAlarmEnabled(true);
    //mRightPowerSlider->setAlarmBrush( Qt::green );
    mRightPowerSlider->setScaleMaxMinor( 3 );
    mRightPowerSlider->setScaleMaxMajor( 5 );
    mRightPowerSlider->setBorderWidth( 2 );

    qDebug() << "rightLabel";
    QLabel *rightLabel = new QLabel( tr("Right"), rightWidget );
    rightLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "rightLayout";
    QVBoxLayout *rightLayout = new QVBoxLayout( rightWidget );
    rightLayout->setMargin( 3 );
    rightLayout->setSpacing( 2 );
    rightLayout->addWidget( mRightPowerSlider, 400 );
    rightLayout->addStretch( 5 );
    rightLayout->addWidget( rightLabel );



    qDebug() << "powerLayout";
    QWidget *power = new QWidget(this);

    QHBoxLayout *powerLayout = new QHBoxLayout( power );
    powerLayout->setMargin( 3 );
    powerLayout->setSpacing( 2 );
    powerLayout->addWidget( leftWidget );
    powerLayout->addWidget( rightWidget );

    qDebug() << "mainLayout";
    QVBoxLayout *mainLayout = new QVBoxLayout( this );
    mainLayout->setMargin( 3 );
    mainLayout->setSpacing( 2 );
     //mainLayout->addStretch(20);
    mainLayout->addWidget(power, 300);

    setLayout(mainLayout);

    connect(mLeftPowerSlider, SIGNAL(sliderMoved(double)), this, SLOT(handleLeftPowerChange(double)));
    connect(mRightPowerSlider, SIGNAL(sliderMoved(double)), this, SLOT(handleRightPowerChange(double)));


    qDebug() << "end";

}

void PowerTunerFrame::handleLeftPowerChange( double leftPower )
{
    qDebug() << "PowerTunerFrame::handleLeftPowerChange leftPower " << leftPower;
    mLeftPower = leftPower;
    //emit powerChanged( mLeftPower, mRightPower );
    emit tuningChanged(new TuningBean(TuningBean::SCALE_POWERS, mLeftPower, mRightPower, this));

}

void PowerTunerFrame::handleRightPowerChange( double rightPower )
{
    qDebug() << "PowerTunerFrame::handleRightPowerChangee rightPower " << rightPower;
    mRightPower = rightPower;
    //emit powerChanged( mLeftPower, mRightPower );
    emit tuningChanged(new TuningBean(TuningBean::SCALE_POWERS, mLeftPower, mRightPower, this));

}



/*
void PowerTunerFrame::setpower( bool running, double leftPower, double rightPower )
{
    mRunning = running;
    mLeftPower = leftPower;
    mRrightPower = rightPower;

    mLeftPowerSlider->setValue(leftPower);
    mRightPowerSlider->setValue(rightPower);

}
*/

void PowerTunerFrame::setCommand(Command command)
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
void PowerTunerFrame::setPower( double leftPower, double rightPower )
{
    mLeftPower = leftPower;
    mRightPower = rightPower;

    mLeftPowerSlider->setValue(mLeftPower);
    mRightPowerSlider->setValue(mRightPower);

}
*/

void PowerTunerFrame::setTuning( TuningBean* aTuningBean )
{
    qDebug() << "PowerTunerFrame::setTuning";

    mLeftPower = aTuningBean->getLeftPower();
    mRightPower = aTuningBean->getRightPower();

    mLeftPowerSlider->setValue(mLeftPower);
    mRightPowerSlider->setValue(mRightPower);
}


/*
void PowerTunerFrame::setSpeedDirection( double speed, double direction )
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


void PowerTunerFrame::handleSettings()
{
    SettingsDialog settingsDialog(this, QString(SERVERNAME), SERVERPORT);
    settingsDialog.exec();

}

