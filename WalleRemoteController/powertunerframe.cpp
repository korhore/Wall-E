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

#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif


PowerTunerFrame::PowerTunerFrame( QWidget *parent ):
   QFrame( parent )
{
    // Setrting buttun

    QPushButton* mSettingsButton = new QPushButton(tr("Settings"), this);
    mSettingsButton->setIcon(QIcon(QPixmap(":pictures/settings.png")));
    mSettingsButton->setIconSize(QSize(50,50));
    // left
    connect(mSettingsButton, SIGNAL(clicked(bool)), this, SLOT(handleSettings()));

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
    mainLayout->addWidget(mSettingsButton, 20);
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
    emit powerChanged( mLeftPower, mRightPower );

}

void PowerTunerFrame::handleRightPowerChange( double rightPower )
{
    qDebug() << "PowerTunerFrame::handleRightPowerChangee rightPower " << rightPower;
    mRightPower = rightPower;
    emit powerChanged( mLeftPower, mRightPower );
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


void PowerTunerFrame::handleSettings()
{
    SettingsDialog settingsDialog(this, QString(SERVERNAME), SERVERPORT);
    settingsDialog.exec();

}

