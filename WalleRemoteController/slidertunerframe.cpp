#include <qlayout.h>
#include <qlabel.h>
#include <qwt_wheel.h>
#include <qwt_slider.h>
#include <qwt_thermo.h>
#include <qwt_math.h>
#include "slidertunerframe.h"

#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif


SliderTunerFrame::SliderTunerFrame( QWidget *parent ):
   TunerFrame( parent )
{
    QWidget *direction = new QWidget(this);
    qDebug() << "mSliderDirection";
    mSliderDirection = new QwtSlider( direction, Qt::Horizontal, QwtSlider::TopScale );
    mSliderDirection->setRange( -180.0, 180.0, 0.1, 45 );
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
    mSliderSpeed->setRange( 0.0, 100.0, 0.1, 10 );
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


void SliderTunerFrame::setDirection( double direction )
{
    qDebug() << "SliderTunerFrame.setDirection";
    mSliderDirection->setValue( direction );
}

void SliderTunerFrame::setSpeed( double speed )
{
    qDebug() << "SliderTunerFrame.setSpeed";
    mSliderSpeed->setValue( 100.0 * speed );
}

void SliderTunerFrame::handleDirectionChange( double direction )
{
    qDebug() << "SliderTunerFrame.handleDirectionChange";
    Q_EMIT directionChanged(direction) ;
}

void SliderTunerFrame::handleSpeedChange( double speed )
{
    qDebug() << "SliderTunerFrame.handleSpeedChange";
    qDebug() << "SliderTunerFrame.handleSpeedChange _EMIT speedChanged " << speed/100.0;
    Q_EMIT speedChanged(speed/100.0) ;
}
