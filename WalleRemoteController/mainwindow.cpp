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

#include "mainwindow.h"
#include "pointertunerframe.h"
#include "slidertunerframe.h"
#include "powertunerframe.h"
//#include "devicemanager.h"
#include <QDebug>
#include <QHBoxLayout>
#include <QVBoxLayout>


#include <QtCore/QCoreApplication>


MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{



    setWindowTitle(tr("Walle Remote Controller"));
    QWidget* background = new QWidget(this);
    setCentralWidget(background);
    mMainLayout = new QHBoxLayout(background);

    mPointerTunerFrame = new PointerTunerFrame( background );
    mPointerTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mPointerTunerFrame, 200 /*Qt::AlignCenter*/);
    mSliderTunerFrame = new SliderTunerFrame(background);
    mSliderTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mSliderTunerFrame/*, 400 Qt::AlignCenter*/);

    TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, 0.0, 0.0, this);
    mSliderTunerFrame->setTuning( tuningbean );
    mPointerTunerFrame->setTuning( tuningbean );
    tuningbean->deleteLater();

    mPowerTunerFrame = new PowerTunerFrame(background);
    mPowerTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mPowerTunerFrame);

    qDebug() << "mainwindow.setPalette";
    setPalette( QPalette( QColor( 192, 192, 192 ) ) );

// TODO Connect visual thing together here
// and let tunings to be signaled out

//#ifdef old
//    mTunerManager = new  DeviceManager(this);

    qDebug() << "mainwindow.connect(mPointerTunerFrame,directionSpeedChanged";
    // Pointer tuner
    // Control device
    connect(mPointerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), this,SLOT(setTuning(TuningBean*)));
    // Let other tuners handle change
    connect(mPointerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mSliderTunerFrame,SLOT(setTuning(TuningBean*)));
    connect(mPointerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mPowerTunerFrame,SLOT(setTuning(TuningBean*)));

    qDebug() << "mainwindow.connect(mSliderTunerFrame,directionSpeedChanged";
    // Slider tuner
    // Control device
    connect(mSliderTunerFrame,SIGNAL(tuningChanged(TuningBean*)), this,SLOT(setTuning(TuningBean*)));
    // Let other tuners handle change
    connect(mSliderTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mPointerTunerFrame,SLOT(setTuning(TuningBean*)));
    connect(mSliderTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mPowerTunerFrame,SLOT(setTuning(TuningBean*)));

    qDebug() << "mainwindow.connectmPowerTunerFrame,powerChanged";
    // Power tuner
    // Control device
    // TODO
    //connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), this,SLOT(setTuning(TuningBean*)));
    //connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)),mTunerManager,SLOT(setPower(double,double)));
    // Let other tuners handle change
    //connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)), mPointerTunerFrame,SLOT(setPower(double,double)));
    //connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)), mSliderTunerFrame,SLOT(setPower(double,double)));

    // Control device
    connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), this,SLOT(setTuning(TuningBean*)));
    // Let other tuners handle change
    connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mPointerTunerFrame,SLOT(setTuning(TuningBean*)));
    connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mSliderTunerFrame,SLOT(setTuning(TuningBean*)));



    qDebug() << "mainwindow.connect(mTunerManager, commandProsessed";
//    connect(mTunerManager,SIGNAL(powerChanged(double,double)),mPowerTunerFrame,SLOT(setPower(double,double)));
//    connect(mTunerManager, SIGNAL(commandProsessed(Command)), mPowerTunerFrame, SLOT(setCommand(Command)));
//#endif

    qDebug() << "mainwindow end";
}

void MainWindow::setTuning(TuningBean* aTuningBean)
{
    // export private tuningt signaling it
    emit tuningChanged(aTuningBean);
}

// visualize device state
void MainWindow::setDeviceState(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "MainWindow::setDeviceState " << aDeviceState;
    // TODO
}

// visualize device state
void MainWindow::setDeviceState(TuningBean* aTuningBean)
{
    qDebug() << "MainWindow::setDeviceState";
    // TODO
}

void MainWindow::setCommand(Command command)
{
    mSliderTunerFrame->setCommand(command);
}



MainWindow::~MainWindow()
{
    //delete mOriginalWallePixmap;
    //mOriginalWallePixmap = NULL;
}

void MainWindow::setOrientation(ScreenOrientation orientation)
{
#if defined(Q_OS_SYMBIAN)
    // If the version of Qt on the device is < 4.7.2, that attribute won't work
    if (orientation != ScreenOrientationAuto) {
        const QStringList v = QString::fromAscii(qVersion()).split(QLatin1Char('.'));
        if (v.count() == 3 && (v.at(0).toInt() << 16 | v.at(1).toInt() << 8 | v.at(2).toInt()) < 0x040702) {
            qWarning("Screen orientation locking only supported with Qt 4.7.2 and above");
            return;
        }
    }
#endif // Q_OS_SYMBIAN

    Qt::WidgetAttribute attribute;
    switch (orientation) {
#if QT_VERSION < 0x040702
    // Qt < 4.7.2 does not yet have the Qt::WA_*Orientation attributes
    case ScreenOrientationLockPortrait:
        attribute = static_cast<Qt::WidgetAttribute>(128);
        break;
    case ScreenOrientationLockLandscape:
        attribute = static_cast<Qt::WidgetAttribute>(129);
        break;
    default:
    case ScreenOrientationAuto:
        attribute = static_cast<Qt::WidgetAttribute>(130);
        break;
#else // QT_VERSION < 0x040702
    case ScreenOrientationLockPortrait:
        attribute = Qt::WA_LockPortraitOrientation;
        break;
    case ScreenOrientationLockLandscape:
        attribute = Qt::WA_LockLandscapeOrientation;
        break;
    default:
    case ScreenOrientationAuto:
        attribute = Qt::WA_AutoOrientation;
        break;
#endif // QT_VERSION < 0x040702
    };
    setAttribute(attribute, true);
}

void MainWindow::showExpanded()
{
#if defined(Q_OS_SYMBIAN) || defined(Q_WS_SIMULATOR)
    showFullScreen();
#elif defined(Q_WS_MAEMO_5)
    showMaximized();
#else
    show();
#endif
}

