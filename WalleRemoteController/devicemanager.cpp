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

#include <QWidget>
#include <QSettings>
#include <QDebug>
#include <math.h>
#include "devicemanager.h"
#include "tuningbean.h"
#include "ftpclient.h"
#include "settingsdialog.h"


DeviceManager::DeviceManager( QObject *parent ):
    QObject( parent ),
    mLastCommand("",-1,Command::Drive),
    mCandidateCommand("",-1,Command::Drive),
    //mPictureCommand("",-1,Command::Picture),
    mCameraOn(false)
{
    // Get saved network configuration
    QSettings settings(QSettings::UserScope, QLatin1String(SETTING_STR));
    settings.beginGroup(QLatin1String("Host"));
    mIPAddress = settings.value(QLatin1String(SETTING_HOST_IP_STR), SERVERNAME).toString();
    mIPPort = settings.value(QLatin1String(SETTING_PORT_STR), SERVERPORT).toInt();
    mCameraIPPort = settings.value(QLatin1String(SETTING_CAMERA_PORT_STR), SERVERCAMERAPORT).toInt();
    settings.endGroup();


    mFtpClient  = new FtpClient(this, mIPAddress, mIPPort);
    connect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));
    connect( mFtpClient, SIGNAL(deviceStateChanged(DeviceManager::DeviceState)), this, SLOT(handleDeviceStateChanged(DeviceManager::DeviceState)));

    test();

    mFtpCameraClient  = new FtpClient(this, mIPAddress, mCameraIPPort);
    // cameras device has taken as picture and it should be shown
    connect( mFtpCameraClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCameraCommandProsessed(Command)));
    // camera device state is handled separately
    connect( mFtpCameraClient, SIGNAL(deviceStateChanged(DeviceManager::DeviceState)), this, SLOT(handleCameraStateChanged(DeviceManager::DeviceState)));


}

DeviceManager::~DeviceManager(){

    disconnect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));
    disconnect( mFtpClient, SIGNAL(deviceStateChanged(DeviceManager::DeviceState)), this, SLOT(handleDeviceStateChanged(DeviceManager::DeviceState)));
    delete mFtpClient;
    mFtpClient = NULL;

    disconnect( mFtpCameraClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCameraCommandProsessed(Command)));
    disconnect( mFtpCameraClient, SIGNAL(deviceStateChanged(DeviceManager::DeviceState)), this, SLOT(handleCameraStateChanged(DeviceManager::DeviceState)));
    delete mFtpCameraClient;
    mFtpCameraClient = NULL;

}

void DeviceManager::setHost( QString ipAddr, int p)
{
    qDebug() << "DeviceManager::setHost";

    mIPAddress = ipAddr;
    mIPPort = p;

    disconnect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));
    delete mFtpClient;
    mFtpClient  = new FtpClient(this, mIPAddress, mIPPort);
    connect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));


}


void DeviceManager::handleCommandProsessed(Command command)
{
    qDebug() << "DeviceManager::handleCommandProsessed";

    emit commandProsessed(command);
}

void DeviceManager::handleDeviceStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "DeviceManager::handleDeviceStateChanged";

    emit deviceStateChanged(aDeviceState);
}



void DeviceManager::setTuning(TuningBean* aTuningBean)
{
    mRightPower = aTuningBean->getRightPower();
    mLeftPower = aTuningBean->getLeftPower();

    mCandidateCommand.setLeftPower(mLeftPower);
    mCandidateCommand.setRightPower(mRightPower);
    if (mLastCommand.isDifferent(mCandidateCommand)) {
       Q_EMIT powerChanged( mLeftPower, mRightPower );
       qDebug() << "DeviceManager:setTuning Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
       mLastCommand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastCommand);
    }
    else
    {
        qDebug() << "DeviceManager:setTuning NO Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
    }

    aTuningBean->deleteLater();

}





bool DeviceManager::test()
{
    bool ret;
    double sourceSpeed = 0.5;
    double sourceDirection = 45.0;
    double destinationSpeed;
    double destinationDirection;

    // positive case SCALE_POSITIVE_SPEED_PLUS_DEGREES -> SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES
    // forward
    int i;
    for (i=-90; i <= 90; i++) {
        sourceSpeed = abs(double(i)/90.0);
        sourceDirection = i;

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT((fabs(sourceSpeed-tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1));
        Q_ASSERT(fabs(sourceDirection-tuningbean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;
    }
    // positive case
    // backward
    for (i=-91; i >= -180; i--) {
        sourceSpeed = abs(double(i)/180.0);
        sourceDirection = i;

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(-180.0 - sourceDirection - tuningbean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;
    }
    for (i=91; i <= 180; i++) {
        sourceSpeed = abs(double(i)/180.0);
        sourceDirection = i;

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(180.0 - sourceDirection -tuningbean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES))  < 0.1);
        delete tuningbean;
    }

    // positive case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES -> SCALE_POSITIVE_SPEED_PLUS_DEGREES
    // forward
    for (i=-90; i <= 90; i++) {
        sourceSpeed = abs(double(i)/90.0);
        sourceDirection = i;

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT((fabs(sourceSpeed-tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1));
        Q_ASSERT(fabs(sourceDirection-tuningbean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;
    }

    // positive case
    // backward
    for (i=-90; i < 0; i++) {
        sourceSpeed = double(i)/90.0;
        sourceDirection = i;

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(-sourceDirection-180.0-tuningbean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;
    }
    for (i=0; i <= 90; i++) {
        sourceSpeed = -double(i+0.001)/90.0;
        sourceDirection = i;

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(180.0-sourceDirection-tuningbean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;

    }


    sourceSpeed = 0.5;
    sourceDirection = 135.0;
    TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
    // destination == source
    Q_ASSERT(sourceSpeed == -tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES));
    Q_ASSERT(sourceDirection == tuningbean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES) + 90.0);
    delete tuningbean;

    return ret;
}

void DeviceManager::handleCamara(bool on)
{
    qDebug() << "DeviceManager::handleCamara " << on;
    mCameraOn = on;
    // if camera is set on, then ask picture
    // if camera is set off, then we don't ask more pictures in handlePictureCommandProsessed method
    mFtpCameraClient->setCameraOn(on);
    //mFtpCameraClient->sendCommand(mPictureCommand);
}

void DeviceManager::handleCameraCommandProsessed(Command command)
{
    qDebug() << "DeviceManager::handleCameraCommandProsessed";

    // tell that we have got picture, it is in the command
    emit cameraCommandProsessed(command);
    // if camera is set on, then ask next picture
    // otherwise this is last one
    /* if (mCameraOn)
    {
        qDebug() << "DeviceManager::handleCameraCommandProsessed mFtpCameraClient->sendCommand(mPictureCommand)";
        mFtpCameraClient->sendCommand(mPictureCommand);
    }
    */

}

void DeviceManager::handleCameraStateChanged(DeviceManager::DeviceState aDeviceState)
{
    qDebug() << "DeviceManager::handleDeviceStateChanged";

    emit cameraStateChanged(aDeviceState);
}




