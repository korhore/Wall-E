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
#include "tuningbean.h"
#include "ftpclient.h"


TuningBean::TuningBean( Scale aScale, double aValue1, double aValue2, QObject *parent/*=NULL*/ ):
    QObject( parent ),
    mScale(aScale),
    mValue1(aValue1),
    mValue2(aValue2),

    SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed(NULL),
    SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection(NULL),

    SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed(NULL),
    SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection(NULL),

    mLeftPower(NULL),
    mRightPower(NULL)


{
    //test();
}

#if old

TuningBean::TuningBean( double aLeftPower, double aRrightPower, QObject *parent/*=NULL*/ ):
    QObject( parent ),
    mScale(SCALE_POWERS)
{
    mLeftPower = new double(aLeftPower);
    mRightPower = new double(aRrightPower);
    //test();
}
#endif

TuningBean::~TuningBean(){
    if (SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection != NULL) {
        delete SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection;
        SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection = NULL;
    };
    if (SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed != NULL) {
        delete SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed;
        SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed = NULL;
    };

    if (SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection != NULL) {
        delete SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection;
        SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection = NULL;
    };
    if (SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed != NULL) {
        delete SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed;
        SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed = NULL;
    };

    if (mLeftPower != NULL) {
        delete mLeftPower;
        mLeftPower = NULL;
    };
    if (mRightPower != NULL) {
        delete mRightPower;
        mRightPower = NULL;
    };

}

double TuningBean::getSpeed(TuningBean::Scale aScale)
{
    if (aScale == mScale) { // if we have initial value in right scale
        return mValue1;
    }

    // look if we have converted already
    switch (aScale)
    {
        case SCALE_POSITIVE_SPEED_PLUS_DEGREES:
            if (SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed == NULL) {
                SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed = new double(mValue1);
                SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection = new double(mValue2);
                convert(mScale, mValue1, mValue2, aScale, *SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed, *SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection);
            };
            return *SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed;

        case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES:
            if (SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed == NULL) {
                SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed = new double(mValue1);
                SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection = new double(mValue2);
                convert(mScale, mValue1, mValue2, aScale, *SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed, *SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection);
            };
            return *SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed;

        default:
            Q_ASSERT(false);    // parameter error
            break;
    };

    return 0.0;
}

double TuningBean::getDirection(TuningBean::Scale aScale)
{
    if (aScale == mScale) { // if we have initial value in right scale
        return mValue2;
    }

    // look if we have converted already
    switch (aScale)
    {
        case SCALE_POSITIVE_SPEED_PLUS_DEGREES:
            if (SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection == NULL) {
                SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed = new double(mValue1);
                SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection = new double(mValue2);
                convert(mScale, mValue1, mValue2, aScale, *SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed, *SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection);
            };
            return *SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection;

        case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES:
            if (SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection == NULL) {
                SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed = new double(mValue1);
                SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection = new double(mValue2);
                convert(mScale, mValue1, mValue2, aScale, *SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed, *SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection);
            };
            return *SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection;

        default:
            Q_ASSERT(false);    // parameter error
            break;
    };

    return 0.0;
}

double TuningBean::getLeftPower()
{
    if (SCALE_POWERS == mScale) { // if we have initial value in right scale
        return mValue1;
    }

    // look if we have converted already
    if (mLeftPower == NULL) {
        mLeftPower = new double(mValue1);
        mRightPower = new double(mValue2);
        convert(mScale, mValue1, mValue2, *mLeftPower, *mRightPower);
    };
    return *mLeftPower;
}

double TuningBean::getRightPower()
{
    if (SCALE_POWERS == mScale) { // if we have initial value in right scale
        return mValue2;
    }

    // look if we have converted already
    if (mRightPower == NULL) {
        mLeftPower = new double(mValue1);
        mRightPower = new double(mValue2);
        convert(mScale, mValue1, mValue2, *mLeftPower, *mRightPower);
    };
    return *mRightPower;
}

#ifdef old
void TuningBean::setSpeedDirection( TuningBean::Scale scale, double speed, double direction )
{
    qDebug() << "TuningBean.setSpeedDirection";
    // convert values to right scale for us
    TuningBean::convert(scale, speed, direction,
                          TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection);
/*
    mSpeed = speed;
    //Q_EMIT speedChanged(speed) ;
    mDirection = direction;
    //Q_EMIT directionChanged(direction);
    */
    calculatePower();
}
#endif


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
#ifdef old
void TuningBean::calculatePower()
{
    qDebug() << "TuningBean.calculatePower";


    // value range TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES
    // turning left if direction is 0 - -180
    // forward if -90 -> 90
    //
    //double fraction = 0.0;
    // turning right forWard
    // full with left motor, rifht motor goes from (0) 1.0 to (90) -1.0
    if ((mDirection >= 0.0) && (mDirection < 90.0)){
        Q_ASSERT(mSpeed >= 0.0);
        *mLeftPower = mSpeed;
        *mRightPower = mSpeed * (45.0 - mDirection)/45.0;
        // turning right backward
        // full back with right motor,left motor goes from (90) 1.0 to (180) -1.0
    } else if ((mDirection >= 90.0) && (mDirection < 180.0)){
        //Q_ASSERT(mSpeed <= 0.0);
        // ignore changes where speed is not properly set yet
//        if (mSpeed <= 0.0) {
            *mRightPower = -mSpeed;
            *mLeftPower = mSpeed * (135.0 - mDirection)/45.0;
//        }
        // turning left backward
        // full back with left motor Right motor goes from (90) -1.0 to -(270) 1.0
    } else if ((mDirection < -90.0 ) && (mDirection >= -180)){
        //Q_ASSERT(mSpeed <= 0.0);
        // ignore changes where speed is not properly set yet
//        if (mSpeed <= 0.0) {
            *mLeftPower = -mSpeed;
            *mRightPower = -mSpeed * (-135.0 - mDirection)/45.0;
//        }
        // turning left forward
        // full back with right motor,left motor goes from (90) 1.0 to (180) -1.0
    } else if ((mDirection < 0.0) && (mDirection >= -90.0)){
        Q_ASSERT(mSpeed >= 0.0);
        *mRightPower = mSpeed;
        *mLeftPower  = -mSpeed * (-45.0 - mDirection)/45.0;
    }

    if (*mLeftPower < -1.0)
        *mLeftPower = -1.0;
    if (*mLeftPower > 1.0)
        *mLeftPower = 1.0;
    if (*mRightPower < -1.0)
        *mRightPower = -1.0;
    if (*mRightPower > 1.0)
        *mRightPower = 1.0;

    mCandidateCommand.setLeftPower(*mLeftPower);
    mCandidateCommand.setRightPower(*mRightPower);
    if (mLastComand.isDifferent(mCandidateCommand)) {
       Q_EMIT powerChanged( *mLeftPower, *mRightPower );
       qDebug() << "TuningBean:calculatePower Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << *mLeftPower <<" mRightPower " << *mRightPower;
       mLastComand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastComand);
    }
    else
    {
        qDebug() << "TuningBean:calculatePower NO Change mSpeed" << mSpeed << " mDirection " << mDirection <<" mLeftPower " << *mLeftPower <<" mRightPower " << *mRightPower;
    }
}

/*

  Left and right power are changeed
  Canculate Speed and direction left and right power

  TODO emit speedDirectionChanged

  */

void TuningBean::setPower( double leftPower, double rightPower )
{
    mLeftPower = leftPower;
    mRightPower = rightPower;

    mCandidateCommand.setLeftPower(mLeftPower);
    mCandidateCommand.setRightPower(mRightPower);

    if (mLastComand.isDifferent(mCandidateCommand)) {
       qDebug() << "TuningBean:setPower mLeftPower " << mLeftPower <<" mRightPower " << mRightPower;
       mLastComand =  mCandidateCommand;
       mFtpClient->sendCommand(mLastComand);
    }

    // TODO calculate direction and pointer tuners


}
#endif

bool TuningBean::convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
                        Scale aDestinationScale, double& aDestinationSpeed, double& aDestinationDirection)
{
    switch (aDestinationScale)
    {
        case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES:
            switch (aSourceScale)
            {
                case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES:    // destination == source
                    aDestinationSpeed = aSourceSpeed;
                    aDestinationDirection = aSourceDirection;
                    break;
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
                    break;
                default:            // no conversion from SCALE_POWERS to SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES
                    Q_ASSERT(false);// can be made, but not needed this application yet
                    break;
            }
            break;

        case SCALE_POSITIVE_SPEED_PLUS_DEGREES:
            switch (aSourceScale)
            {
                case SCALE_POSITIVE_SPEED_PLUS_DEGREES:    // destination == source
                    aDestinationSpeed = aSourceSpeed;
                    aDestinationDirection = aSourceDirection;
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
                    break;

                default:            // no conversion from SCALE_POWERS to SCALE_POSITIVE_SPEED_PLUS_DEGREES
                    Q_ASSERT(false);// can be made, but not needed this application yet
                    break;
            }
            break;

        // destination power case
            // speed = leftpower
            // direction = rightpower
        case SCALE_POWERS:
            Q_ASSERT(false);// can be made, but not needed this application yet
            break;
        default:
            Q_ASSERT(false);
    }

    return true;

}


/////// old /////////
#ifdef old
bool TuningBean::convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
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

            qDebug() << "TuningBean::convert aSourceScale " << aSourceScale << " aSourceSpeed " << aSourceSpeed << " aSourceDirection "  << aSourceDirection << " aDestinationScale " << aDestinationScale << " aDestinationSpeed " << aDestinationSpeed << " aDestinationDirection "  << aDestinationDirection;

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

            qDebug() << "TuningBean::convert aSourceScale " << aSourceScale << " aSourceSpeed " << aSourceSpeed << " aSourceDirection "  << aSourceDirection << " aDestinationScale " << aDestinationScale << " aDestinationSpeed " << aDestinationSpeed << " aDestinationDirection "  << aDestinationDirection;

            break;
        default:
            Q_ASSERT(false);
    }

    return true;

}
#endif
bool TuningBean::convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
                        double& aDestinationeLeftPower, double& aDestinationeRightPower )
{
    switch (aSourceScale)
    {
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
            if (aSourceSpeed < -1.0) {
                aSourceSpeed = -1.0;
            }

            if (aSourceSpeed >= 0) {    // forward, turning right
                if (aSourceDirection >= 0.0){
                    aDestinationeLeftPower = aSourceSpeed;
                    aDestinationeRightPower = aSourceSpeed * (45.0 - aSourceDirection)/45.0;
                } else {
                    Q_ASSERT(aSourceSpeed >= 0.0);
                    aDestinationeRightPower = aSourceSpeed;
                    aDestinationeLeftPower  = -aSourceSpeed * (-45.0 - aSourceDirection)/45.0;
                }
            } else {    // turning right backward
                if (aSourceDirection >= 0.0) {
                    aDestinationeRightPower = aSourceSpeed;
                    aDestinationeLeftPower = -aSourceSpeed * (45.0 - aSourceDirection)/45.0;
                // turning left backward
                } else {
                    aDestinationeLeftPower = aSourceSpeed;
                    aDestinationeRightPower = aSourceSpeed * (-45.0 - aSourceDirection)/45.0;
                }
            }
            break;
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
            if (aSourceSpeed < 0.0) {
                aSourceSpeed = 0.0;
            }

            if ((aSourceDirection >= 0.0) && (aSourceDirection < 90.0)) {
                aDestinationeLeftPower = aSourceSpeed;
                aDestinationeRightPower = aSourceSpeed * (45.0 - aSourceDirection)/45.0;
            } else if ((aSourceDirection >= 90.0) && (aSourceDirection < 180.0)){
                aDestinationeRightPower = -aSourceSpeed;
                aDestinationeLeftPower = aSourceSpeed * (135.0 - aSourceDirection)/45.0;
            } else if ((aSourceDirection < -90.0 ) && (aSourceDirection >= -180)){
                aDestinationeLeftPower = -aSourceSpeed;
                aDestinationeRightPower = -aSourceSpeed * (-135.0 - aSourceDirection)/45.0;
            } else if ((aSourceDirection < 0.0) && (aSourceDirection >= -90.0)){
                aDestinationeRightPower = aSourceSpeed;
                aDestinationeLeftPower  = -aSourceSpeed * (-45.0 - aSourceDirection)/45.0;
            }
            break;
      default:
            Q_ASSERT(false);
            break;
    }

    if (aDestinationeLeftPower < -1.0)     // value range
        aDestinationeLeftPower = -1.0;
    if (aDestinationeLeftPower > 1.0)
        aDestinationeLeftPower = 1.0;
    if (aDestinationeRightPower < -1.0)
        aDestinationeRightPower = -1.0;
    if (aDestinationeRightPower > 1.0)
        aDestinationeRightPower = 1.0;

    return true;
}

#ifdef old
bool TuningBean::convert(double aSourceLeftPower, double& aSourceRightPower,
             Scale aDestinationScale, double& aDestinationSpeed, double& aDestinationeDirection )
{
    return false;
}
#endif

bool TuningBean::test()
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
        qDebug() << "TuningBean::test" << " sourceSpeed " << sourceSpeed << " sourceDirection "  << sourceDirection << " destinationSpeed " << destinationSpeed << " destinationDirection "  << destinationDirection;
        Q_ASSERT(ret);
        // destination == source
        qDebug() << "TuningBean::test (fabs(sourceSpeed-destinationSpeed)) " << (fabs(sourceSpeed-destinationSpeed));

        Q_ASSERT((fabs(sourceSpeed-destinationSpeed) < 0.1));
        Q_ASSERT(fabs(sourceDirection-destinationDirection) < 0.1);
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
    }

    // positive case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES -> SCALE_POSITIVE_SPEED_PLUS_DEGREES
    // forward
    for (i=-90; i <= 90; i++) {
        sourceSpeed = abs(double(i)/90.0);
        sourceDirection = i;
        ret = convert(SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        qDebug() << "TuningBean::test" << " sourceSpeed " << sourceSpeed << " sourceDirection "  << sourceDirection << " destinationSpeed " << destinationSpeed << " destinationDirection "  << destinationDirection;
        Q_ASSERT(ret);
        // destination == source
        qDebug() << "TuningBean::test (fabs(sourceSpeed-destinationSpeed)) " << (fabs(sourceSpeed-destinationSpeed));

        Q_ASSERT((fabs(sourceSpeed-destinationSpeed) < 0.1));
        Q_ASSERT(fabs(sourceDirection-destinationDirection) < 0.1);
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
    }


    sourceSpeed = 0.5;
    sourceDirection = 135.0;
    ret = convert(SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                  SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
    Q_ASSERT(ret);
    // destination == source
    Q_ASSERT(sourceSpeed == -destinationSpeed);
    Q_ASSERT(sourceDirection == destinationDirection + 90.0);


    return ret;
}


