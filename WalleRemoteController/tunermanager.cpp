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
#include "tunermanager.h"
#include "tuningbean.h"
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

    test();

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


#ifdef old
void TunerManager::setSpeedDirection( TunerManager::Scale scale, double speed, double direction )
{
    qDebug() << "TunerManager.setSpeedDirection";
    // convert values to right scale for us
    TunerManager::convert(scale, speed, direction,
                          TunerManager::SCALE_POSITIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection);
/*
    mSpeed = speed;
    //Q_EMIT speedChanged(speed) ;
    mDirection = direction;
    //Q_EMIT directionChanged(direction);
    */
    calculatePower();
}
#endif

void TunerManager::setTuning(TuningBean* aTuningBean)
{
    mRightPower = aTuningBean->getRightPower();
    mLeftPower = aTuningBean->getLeftPower();

    mCandidateCommand.setLeftPower(mLeftPower);
    mCandidateCommand.setRightPower(mRightPower);
    if (mLastComand.isDifferent(mCandidateCommand)) {
       Q_EMIT powerChanged( mLeftPower, mRightPower );
       qDebug() << "TunerManager:setTuning Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
       mLastComand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastComand);
    }
    else
    {
        qDebug() << "TunerManager:setTuning NO Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
    }

    aTuningBean->deleteLater();

}



/*

  Speed or direction is changeed
  Canculate left and right power

  TODO allow only one method for setSpeedDirection(double speed, double direction)
  to make thing easier    // handle two range cases
    // 1) -180 <=  direcction <= 180, 0.0 <= power <= 1.0
    // 2) -90 <=  direcction <= 90, -1.0 <= power <= 1.0

    if (mDirection > 180.0)  { // value range
        mDirection = 180.0;
    } else
    if (mDirection < -180.0) {
        mDirection = -180.0;
    };

    // if 2) range case, convert it to 1)

    if (mSpeed < 0.0) {
        mSpeed = -mSpeed;
        if (mDirection >= 0.0) {
            mDirection += 90.0;
        } else {
            mDirection -= 90.0;
        }
    }

    if (mSpeed > 1.0) {  // value range
        mSpeed = 1.0;
    }

  TODO emit powerChanged

  */

void TunerManager::calculatePower()
{
    qDebug() << "TunerManager.calculatePower";


    // value range TunerManager::SCALE_POSITIVE_SPEED_PLUS_DEGREES
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

    mCandidateCommand.setLeftPower(mLeftPower);
    mCandidateCommand.setRightPower(mRightPower);
    if (mLastComand.isDifferent(mCandidateCommand)) {
       Q_EMIT powerChanged( mLeftPower, mRightPower );
       qDebug() << "TunerManager:calculatePower Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
       mLastComand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastComand);
    }
    else
    {
        qDebug() << "TunerManager:calculatePower NO Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
    }
}

/*

  Left and right power are changeed
  Canculate Speed and direction left and right power

  TODO emit speedDirectionChanged

  */

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

    // TODO calculate direction and pointer tuners


}

bool TunerManager::convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
                           Scale aDestinationScale, double& aDestinationSpeed, double& aDestinationDirection)
{
    switch (aSourceScale)
    {
        case SCALE_POSITIVE_SPEED_PLUS_DEGREES:
            if (aSourceDirection > 180.0)  { // value range
                aSourceDirection = 180.0;
            } else
            if (aSourceDirection < -180.0) {
                aSourceDirection = -180.0;
            };

            if (aSourceSpeed > 1.0) {  // value range
                aSourceSpeed = 1.0;
            }
            if (aSourceSpeed < 0.0) {  // value range
                aSourceSpeed = 0.0;
            }

            if (aDestinationScale == SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES) {   // if conversion
                if (aSourceDirection < -90.0) {
                    aDestinationSpeed = -aSourceSpeed;
                    aDestinationDirection = -180.0 - aSourceDirection;
                }
                else if (aSourceDirection > 90.0) {
                        aDestinationSpeed = -aSourceSpeed;
                        aDestinationDirection = 180 - aSourceDirection;
                }
                else {
                    aDestinationSpeed = aSourceSpeed;
                    aDestinationDirection = aSourceDirection;
                }
            }
            else {
                aDestinationSpeed = aSourceSpeed;
                aDestinationDirection = aSourceDirection;
            }

            qDebug() << "TunerManager::convert aSourceScale " << aSourceScale << " aSourceSpeed " << aSourceSpeed << " aSourceDirection "  << aSourceDirection << " aDestinationScale " << aDestinationScale << " aDestinationSpeed " << aDestinationSpeed << " aDestinationDirection "  << aDestinationDirection;

            break;
        case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES:
            if (aSourceDirection > 90.0)  { // value range
                aSourceDirection = 90.0;
            } else
            if (aSourceDirection < -90.0) {
                aSourceDirection = -90.0;
            };

            if (aSourceSpeed > 1.0) {  // value range
                aSourceSpeed = 1.0;
            }
            if (aSourceSpeed < -1.0) {  // value range
                aSourceSpeed = -1.0;
            }

            if (aDestinationScale == SCALE_POSITIVE_SPEED_PLUS_DEGREES) {   // if conversion
                if (aSourceSpeed < 0.0) {
                    aDestinationSpeed = -aSourceSpeed;
                    if (aSourceDirection < 0.0) {
                        aDestinationDirection = -aSourceDirection - 180.0;
                    }
                    else {
                        aDestinationDirection = 180.0 - aSourceDirection;
                    }
                }
                else {
                    aDestinationSpeed = aSourceSpeed;
                    aDestinationDirection = aSourceDirection;
                }
            }
            else {
                aDestinationSpeed = aSourceSpeed;
                aDestinationDirection = aSourceDirection;
            }

            qDebug() << "TunerManager::convert aSourceScale " << aSourceScale << " aSourceSpeed " << aSourceSpeed << " aSourceDirection "  << aSourceDirection << " aDestinationScale " << aDestinationScale << " aDestinationSpeed " << aDestinationSpeed << " aDestinationDirection "  << aDestinationDirection;

            break;
        default:
            Q_ASSERT(false);
    }

    return true;

}

bool TunerManager::convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
             double& aDestinationeLeftPower, double& aDestinationeRightPower )
{
    return false;
}

bool TunerManager::convert(double aSourceLeftPower, double& aDSourceRightPower,
             Scale aDestinationScale, double& aDestinationSpeed, double& aDestinationeDirection )
{
    return false;
}


bool TunerManager::test()
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
        ret = convert(SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        qDebug() << "TunerManager::test" << " sourceSpeed " << sourceSpeed << " sourceDirection "  << sourceDirection << " destinationSpeed " << destinationSpeed << " destinationDirection "  << destinationDirection;
        Q_ASSERT(ret);
        // destination == source
        qDebug() << "TunerManager::test (fabs(sourceSpeed-destinationSpeed)) " << (fabs(sourceSpeed-destinationSpeed));

        Q_ASSERT((fabs(sourceSpeed-destinationSpeed) < 0.1));
        Q_ASSERT(fabs(sourceDirection-destinationDirection) < 0.1);

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
        ret = convert(SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        Q_ASSERT(ret);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+destinationSpeed) < 0.1);
        Q_ASSERT(fabs(-180.0 - sourceDirection -destinationDirection) < 0.1);

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(-180.0 - sourceDirection - tuningbean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;
    }
    for (i=91; i <= 180; i++) {
        sourceSpeed = abs(double(i)/180.0);
        sourceDirection = i;
        ret = convert(SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        Q_ASSERT(ret);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+destinationSpeed) < 0.1);
        Q_ASSERT(fabs(180.0 - sourceDirection -destinationDirection)  < 0.1);

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
        ret = convert(SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        qDebug() << "TunerManager::test" << " sourceSpeed " << sourceSpeed << " sourceDirection "  << sourceDirection << " destinationSpeed " << destinationSpeed << " destinationDirection "  << destinationDirection;
        Q_ASSERT(ret);
        // destination == source
        qDebug() << "TunerManager::test (fabs(sourceSpeed-destinationSpeed)) " << (fabs(sourceSpeed-destinationSpeed));

        Q_ASSERT((fabs(sourceSpeed-destinationSpeed) < 0.1));
        Q_ASSERT(fabs(sourceDirection-destinationDirection) < 0.1);

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
        ret = convert(SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        Q_ASSERT(ret);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+destinationSpeed) < 0.1);
        Q_ASSERT(fabs(-sourceDirection-180.0-destinationDirection) < 0.1);

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(-sourceDirection-180.0-tuningbean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;
    }
    for (i=0; i <= 90; i++) {
        sourceSpeed = -double(i+0.001)/90.0;
        sourceDirection = i;
        ret = convert(SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        Q_ASSERT(ret);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+destinationSpeed) < 0.1);
        Q_ASSERT(fabs(180.0-sourceDirection-destinationDirection) < 0.1);

        TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        Q_ASSERT(fabs(180.0-sourceDirection-tuningbean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES)) < 0.1);
        delete tuningbean;

    }


    sourceSpeed = 0.5;
    sourceDirection = 135.0;
    ret = convert(SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                  SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
    Q_ASSERT(ret);
    // destination == source
    Q_ASSERT(sourceSpeed == -destinationSpeed);
    Q_ASSERT(sourceDirection == destinationDirection + 90.0);

    TuningBean* tuningbean = new TuningBean (TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection, this);
    // destination == source
    Q_ASSERT(sourceSpeed == -tuningbean->getSpeed(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES));
    Q_ASSERT(sourceDirection == tuningbean->getDirection(TuningBean::SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES) + 90.0);
    delete tuningbean;

    return ret;
}


