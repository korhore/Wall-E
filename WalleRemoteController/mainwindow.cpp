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
#include <QDir>

#if defined(Q_WS_S60)
#define POINTER_TUNER_WIDTH         250
#define SLIDER_TUNER_WIDTH          250
#else
#define POINTER_TUNER_WIDTH         400
#define SLIDER_TUNER_WIDTH          250
#endif

#if defined(Q_WS_S60)
#define SCREEN_WIDTH                640
#define SCREEN_HIGHT                360
#else
#define SCREEN_WIDTH                800
#define SCREEN_HIGHT                480
#endif

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
#if defined(Q_WS_S60)
    setAttribute( Qt::WA_LockLandscapeOrientation, true );
#endif
    setWindowTitle(tr("Wall-E Remote Controller"));
    mBackground = new QLabel(this);
    mBackground->setScaledContents(true);
    mBackground->setMinimumSize (SCREEN_WIDTH, SCREEN_HIGHT);
    mBackground->setMaximumSize (SCREEN_WIDTH, SCREEN_HIGHT);


    QFile f(QDir::tempPath () + "/image.jpg");
    if (f.open(QIODevice::ReadOnly)) {
        qDebug() << "file size " << f.size() << endl;

        QByteArray imageData = f.readAll();
        qDebug() << "MainWindow::MainWindow; read " << imageData.size() << " bytes";
        setBackgroundImage(imageData);

    }


    setCentralWidget(mBackground);
    mMainLayout = new QHBoxLayout(mBackground);

    mPointerTunerFrame = new PointerTunerFrame( mBackground );
    // Test
    //mPointerTunerFrame->setOpacity(0.20);
    mPointerTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mPointerTunerFrame, POINTER_TUNER_WIDTH /*Qt::AlignCenter*/);

    mSliderTunerFrame = new SliderTunerFrame(mBackground);
    // Test
    //mSliderTunerFrame->setOpacity(0.20);
    mSliderTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mSliderTunerFrame, SLIDER_TUNER_WIDTH /*Qt::AlignCenter*/);

    mPowerTunerFrame = new PowerTunerFrame(mBackground);
    // Test
    //mPowerTunerFrame->setOpacity(1.0);
    mPowerTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mPowerTunerFrame);

    TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, 0.0, 0.0, this);
    mSliderTunerFrame->setTuning( tuningbean );
    mPointerTunerFrame->setTuning( tuningbean );
    mPowerTunerFrame->setTuning( tuningbean );
    tuningbean->deleteLater();


    qDebug() << "mainwindow.setPalette";
    setPalette( QPalette( QColor( 192, 192, 192 ) ) );

// TODO Connect visual thing together here
// and let tunings to be signaled out

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

    connect(mSliderTunerFrame,SIGNAL(cameraToggled(bool)), this, SLOT(handleCameraToggled(bool)));

    qDebug() << "mainwindow.connectmPowerTunerFrame,powerChanged";
    // Power tuner
     // Control device
    connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), this,SLOT(setTuning(TuningBean*)));
    // Let other tuners handle change
    connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mPointerTunerFrame,SLOT(setTuning(TuningBean*)));
    connect(mPowerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mSliderTunerFrame,SLOT(setTuning(TuningBean*)));

    qDebug() << "mainwindow end";
}

void MainWindow::setBackgroundImage(const QByteArray& aImageData)
{
    qDebug() << "MainWindow::setBackgroundImage read " << aImageData.size() << " bytes";

    QImage image;
    QPixmap mBackGroundPixmax;
    if (image.loadFromData ( aImageData, "JPG" )) {
        qDebug() << "MainWindow::setBackgroundImage load image from data succeeded, load pixmax  from that image";
        mBackGroundPixmax = QPixmap::fromImage(image);
        mBackground->setPixmap(mBackGroundPixmax);
    } else {
        qDebug() << "MainWindow::setBackgroundImage load image failed";
    }

}

void MainWindow::setTuning(TuningBean* aTuningBean)
{
    // export private tuningt signaling it
    emit tuningChanged(aTuningBean);
}

void MainWindow::handleCameraToggled(bool checked)
{
    qDebug() << "MainWindow::handleCameraToggled " << checked;
    qreal opacity= checked ? 0.20 : 1.0;

    mPointerTunerFrame->setOpacity(opacity);
    mSliderTunerFrame->setOpacity(opacity);
    mPowerTunerFrame->setOpacity(opacity);

    emit cameraToggled(checked);
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

// tries to change power and send comand to device
void MainWindow::showPowerChanged( double leftPower, double rightPower )
{
    mSliderTunerFrame->showPowerChanged( leftPower, rightPower );
}

// device has processed command and set it to this status
void MainWindow::showCommandProsessed(Command command)
{
    if (command.getCommand() == Command::Picture)
    {
        showPicture(command);
    }
    else
    {
        mSliderTunerFrame->showCommandProsessed(command);
    }
}

// show camera state
// camera device has taken a picture and it should be shown
void MainWindow::showCameraCommandProsessed(Command command)
{
    if (command.getCommand() == Command::Picture)
    {
        showPicture(command);
    }

}



void MainWindow::showPicture(Command command)
{
    if (command.getImageSize() == command.getImageData().size()) // if we have right size imagedata
        setBackgroundImage(command.getImageData());
}


// device has processed command and set it to this tuning
void MainWindow::showDeviceStateChanged(TuningBean* aTuningBean)
{
    mSliderTunerFrame->showDeviceStateChanged(aTuningBean);
}

// device state has changed
void MainWindow::showDeviceStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "MainWindow::showDeviceStateChanged";
    mSliderTunerFrame->showDeviceStateChanged(aDeviceState);
}

// if device state error, also error is emitted
void MainWindow::showDeviceError(QAbstractSocket::SocketError socketError)
{
    qDebug() << "MainWindow::showDeviceError";
    mSliderTunerFrame->showDeviceError(socketError);
}

// camera device state has changed
void MainWindow::showCameraStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "MainWindow::showCameraStateChanged";
    mSliderTunerFrame->showCameraStateChanged(aDeviceState);
}

// if camera device state error, also error is emitted
void MainWindow::showCameraError(QAbstractSocket::SocketError socketError)
{
    qDebug() << "MainWindow::showCameraError";
    mSliderTunerFrame->showCameraError(socketError);
}




