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

#include "tunercontroller.h"
#include "mainwindow.h"
#include "pointertunerframe.h"
#include "slidertunerframe.h"
#include "powertunerframe.h"
#include "devicemanager.h"
#include <QDebug>
#include <QHBoxLayout>
#include <QVBoxLayout>


#include <QtCore/QCoreApplication>


TunerController::TunerController(QWidget *parent /*=NULL*/)
    : QWidget(parent)
{
    // MVC architecture
    // We are Controller
    // Create Visual and Model workers and set them up to work

    // We handle tuning produced by Visual systen
    // let deviceManager to control device using these tunings

    // We borrow bean concept from Java and we we have most flexible architecture
    // MVC + Bean
    // To tune all kind of devices with all king of tunings

    // This is very high level controller and
    // dependeces are nimimized

    // Get workers

    // First Visual classes
    mMainWindow = new MainWindow (this);
    // Model class
    mDeviceManager = new DeviceManager(this);

//#ifdef newcode
    connect(mMainWindow,SIGNAL(tuningChanged(TuningBean*)), mDeviceManager,SLOT(setTuning(TuningBean*)));
    connect(mMainWindow,SIGNAL(hostChanged(QString, int)), mDeviceManager,SLOT(setHost(QString, int)));
    connect(mDeviceManager, SIGNAL(commandProsessed(Command)), mMainWindow, SLOT(setCommand(Command)));

//#endif
#ifdef oldcode
    mPointerTunerFrame = mMainWindow->getPointerTunerFrame();
    mSliderTunerFrame = mMainWindow->getSliderTunerFrame();
    mPowerTunerFrame = mMainWindow->getPowerTunerFrame();

    // Get Model class

    mDeviceManager = new DeviceManager(this);

    // Make workers work together
    // As a controller we are boss and we know workers duties ans capabilitis
    // even if we are not interrested how they will implement it

    // TODO Handle only tunings here
    // and let Visual connection be handled be mainwindow


    qDebug() << "TunerController.connect(mPointerTunerFrame,directionSpeedChanged";
    // Pointer tuner
    // Control device
    connect(mPointerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mDeviceManager,SLOT(setTuning(TuningBean*)));
    // Let other tuners handle change
    connect(mPointerTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mSliderTunerFrame,SLOT(setTuning(TuningBean*)));

    qDebug() << "TunerController.connect(mSliderTunerFrame,directionSpeedChanged";
    // Slider tuner
    // Control device
    connect(mSliderTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mDeviceManager,SLOT(setTuning(TuningBean*)));
    // Let other tuners handle change
    connect(mSliderTunerFrame,SIGNAL(tuningChanged(TuningBean*)), mPointerTunerFrame,SLOT(setTuning(TuningBean*)));

    qDebug() << "TunerController.connectmPowerTunerFrame,powerChanged";
    // Power tuner
    // Control device
    // TODO
    connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)),mDeviceManager,SLOT(setPower(double,double)));
    // Let other tuners handle change
    connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)), mPointerTunerFrame,SLOT(setPower(double,double)));
    connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)), mSliderTunerFrame,SLOT(setPower(double,double)));


    qDebug() << "TunerController.connect(mDeviceManager, commandProsessed";
    connect(mDeviceManager,SIGNAL(powerChanged(double,double)),mPowerTunerFrame,SLOT(setPower(double,double)));
    connect(mDeviceManager, SIGNAL(commandProsessed(Command)), mPowerTunerFrame, SLOT(setCommand(Command)));
#endif
    // set mainwindow show its content
    mMainWindow->setOrientation(MainWindow::ScreenOrientationLockLandscape);
    //qDebug() << "main mainWindow.showExpanded()";
    //mMainWindow->showExpanded();
    qDebug() << "mMainWindow->show()";
    mMainWindow->show();



    // Thats it, that is boss job
    // Static controlling is enough in this case, workers can handle job themselves
    // and we are needed just ti put things to run

    // this is place to add more functionality, if you need it
    // just add more workers or ad capabilities to old ones

    qDebug() << "TunerController end";
}

TunerController::~TunerController()
{
    // deleting is not needed
    // We own only mMainWindow, mDeviceManager and Qt's autodeting handles it
}

