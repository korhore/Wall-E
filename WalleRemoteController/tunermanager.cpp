/* -------------------------------------------

    WalleRemoteContoller is an educational application to control a robot or other device using WLAN

    Copyright (C) 2013 Reijo Korhonen, reijo korhonen@gmail.com
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
#include "tunermanager.h"
#include "ftpclient.h"


TunerManager::TunerManager( QWidget *parent ):
    QObject( parent ),
    mLastComand("",-1,Command::Drive),
    mCandidateCommand("",-1,Command::Drive)
{
    // Get saved network configuration
    QSettings settings(QSettings::UserScope, QLatin1String("Wall-E"));
    settings.beginGroup(QLatin1String("Host"));
    ipAddress = settings.value(QLatin1String("IP"), SERVERNAME).toString();
    port = settings.value(QLatin1String("PORT"), SERVERPORT).toInt();
    settings.endGroup();


    mFtpClient  = new FtpClient(this, ipAddress, port);
    connect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));

}

TunerManager::~TunerManager(){

    disconnect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));
    delete mFtpClient;
    mFtpClient = NULL;
}

void TunerManager::setHost( QString ipAddr, int p)
{
    ipAddress = ipAddr;
    port = p;

    disconnect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));
    delete mFtpClient;
    mFtpClient  = new FtpClient(this, ipAddress, port);
    connect( mFtpClient, SIGNAL(commandProsessed(Command)), this, SLOT(handleCommandProsessed(Command)));


}


void TunerManager::handleCommandProsessed(Command command)
{
    emit commandProsessed(command);
}



void TunerManager::setDirection( double direction )
{
    qDebug() << "TunerManager.setDirection";
    mDirection = direction;
    Q_EMIT directionChanged(direction);
    calculatePower();
}

void TunerManager::setSpeed( double speed )
{
    qDebug() << "TunerManager.setSpeed";
    mSpeed = speed;
    Q_EMIT speedChanged(speed) ;
    calculatePower();
}



void TunerManager::calculatePower()
{
    qDebug() << "TunerManager.calculatePower";
    // turning left if direction is 0 - -180
    // forward if -90 -> 90
    //
    //double fraction = 0.0;
    // turning right forWard
    // full with left motor, rifht motor goes from (0) 1.0 to (90) -1.0
    if ((mDirection >= 0.0) && (mDirection < 90.0)){
        Q_ASSERT(mSpeed >= 0.0);
        mLeftPower = mSpeed;
        mRightPower = mSpeed * (45.0 - mDirection)/45.0;
        // turning right backward
        // full back with right motor,left motor goes from (90) 1.0 to (180) -1.0
    } else if ((mDirection >= 90.0) && (mDirection < 180.0)){
        //Q_ASSERT(mSpeed <= 0.0);
        // ignore changes where speed is not properly set yet
//        if (mSpeed <= 0.0) {
            mRightPower = -mSpeed;
            mLeftPower = mSpeed * (135.0 - mDirection)/45.0;
//        }
        // turning left backward
        // full back with left motor Right motor goes from (90) -1.0 to -(270) 1.0
    } else if ((mDirection < -90.0 ) && (mDirection >= -180)){
        //Q_ASSERT(mSpeed <= 0.0);
        // ignore changes where speed is not properly set yet
//        if (mSpeed <= 0.0) {
            mLeftPower = -mSpeed;
            mRightPower = -mSpeed * (-135.0 - mDirection)/45.0;
//        }
        // turning left forward
        // full back with right motor,left motor goes from (90) 1.0 to (180) -1.0
    } else if ((mDirection < 0.0) && (mDirection >= -90.0)){
        Q_ASSERT(mSpeed >= 0.0);
        mRightPower = mSpeed;
        mLeftPower  = -mSpeed * (-45.0 - mDirection)/45.0;
    }

    if (mLeftPower < -1.0)
        mLeftPower = -1.0;
    if (mLeftPower > 1.0)
        mLeftPower = 1.0;
    if (mRightPower < -1.0)
        mRightPower = -1.0;
    if (mRightPower > 1.0)
        mRightPower = 1.0;
    //Q_EMIT powerChanged( true, mLeftPower, mRightPower );
    //qDebug() << "TunerManager:calculatePower mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;

    //mFtpClient->request(REQUEST_CONTROL.arg(mLeftPower).arg(mRightPower));
    // TODO
//    mFtpClient->request(QString(REQUEST_CONTROL).arg(QString::number(mLeftPower), QString::number(mRightPower)));
//    mFtpClient->command(true, mLeftPower, mRightPower);
//    qDebug() << QString("%1/%3-%2.txt").arg("~", mLeftPower, mRightPower);
    mCandidateCommand.setLeftPower(mLeftPower);
    mCandidateCommand.setRightPower(mRightPower);
    if (mLastComand.isDifferent(mCandidateCommand)) {
//       Q_EMIT powerChanged( true, mLeftPower, mRightPower );
       qDebug() << "TunerManager:calculatePower Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
       mLastComand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastComand);
    }
    else
    {
        qDebug() << "TunerManager:calculatePower NO Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
    }
}

void TunerManager::setPower( double leftPower, double rightPower )
{
    mLeftPower = leftPower;
    mRightPower = rightPower;

    mCandidateCommand.setLeftPower(mLeftPower);
    mCandidateCommand.setRightPower(mRightPower);

    if (mLastComand.isDifferent(mCandidateCommand)) {
       qDebug() << "TunerManager:setPower mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
       mLastComand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastComand);
    }

    // TODO calculate durection and pointer tuners


}

