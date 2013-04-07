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
#include "devicemanager.h"

/*
#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif
*/

SliderTunerFrame::SliderTunerFrame( QWidget *parent ):
   TunerFrame( parent )
{
    QWidget *direction = new QWidget(this);
    qDebug() << "mSliderDirection";
    mSliderDirection = new QwtSlider( direction, Qt::Horizontal, QwtSlider::TopScale );
    mSliderDirection->setRange( -90.0, 90.0, 0.1, 45 );
    mSliderDirection->setScaleMaxMinor( 3 );
    mSliderDirection->setScaleMaxMajor( 5 );
    mSliderDirection->setHandleSize( 40, 80 );
    mSliderDirection->setBorderWidth( 2 );

    qDebug() << "directionLabel";
    QLabel *directionLabel = new QLabel( "Direction", direction );
    directionLabel->setAlignment( Qt::AlignCenter );
    direction->setFixedWidth( 5 * directionLabel->sizeHint().width()/3 );


    qDebug() << "directionLayout";
    QVBoxLayout *directionLayout = new QVBoxLayout( direction );
    directionLayout->setMargin( 3 );
    directionLayout->setSpacing( 2 );
    directionLayout->addWidget( mSliderDirection, 500 );
    directionLayout->addStretch( 5 );
    directionLayout->addWidget( directionLabel );

    connect(mSliderDirection, SIGNAL(sliderMoved(double)), this, SLOT(handleDirectionChange(double)));


    QWidget *speed = new QWidget(this);
    qDebug() << "mSliderSpeed";
    mSliderSpeed = new QwtSlider( speed, Qt::Vertical, QwtSlider::LeftScale );
    mSliderSpeed->setRange( -1.0, 1.0 );
    mSliderSpeed->setScaleMaxMinor( 3 );
    mSliderSpeed->setScaleMaxMajor( 5 );
    mSliderSpeed->setHandleSize( 80, 40 );
    mSliderSpeed->setBorderWidth( 2 );

    qDebug() << "speedLabel";
    QLabel *speedLabel = new QLabel( "Speed", speed );
    speedLabel->setAlignment( Qt::AlignCenter );

    qDebug() << "speedLayout";
    QVBoxLayout *speedLayout = new QVBoxLayout( speed );
    speedLayout->setMargin( 3 );
    speedLayout->setSpacing( 2 );
    speedLayout->addWidget( mSliderSpeed, 350 );
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
    mainLayout->addWidget( speed, 50 );
    qDebug() << "mainLayout4";
    mainLayout->addWidget( direction, 200 );
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
