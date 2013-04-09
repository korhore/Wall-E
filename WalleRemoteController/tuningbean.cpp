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

#include <QDebug>
#include <math.h>
#include "tuningbean.h"


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
    switch (mScale)
    {
        case SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES:    // destination == source
            if (mValue1 > 1.0) {  // value range
                mValue1 = 1.0;
            }
            if (mValue1 < -1.0) {
                mValue1 = -1.0;
            }

            if (mValue2 > 90.0)  { // value range
                mValue2 = 90.0;
            } else
            if (mValue2 < -90.0) {
                mValue2 = -90.0;
            };
            break;
        case SCALE_POSITIVE_SPEED_PLUS_DEGREES:
            if (mValue1 > 1.0) {  // value range
                mValue1 = 1.0;
            }
            if (mValue1 < 0.0) {
                mValue1 = 0.0;
            }

            if (mValue2 > 180.0)  { // value range
                mValue2 = 180.0;
            } else
            if (mValue2 < -180.0) {
                mValue2 = -180.0;
            };

            break;
        case SCALE_POWERS:
            if (mValue1 > 1.0) {  // value range
                mValue1 = 1.0;
            }
            if (mValue1 < -1.0) {
                mValue1 = -1.0;
            }

            if (mValue2 > 1.0) {  // value range
                mValue2 = 1.0;
            }
            if (mValue2 < -1.0) {
                mValue2 = -1.0;
            }
            break;
        default:
            Q_ASSERT(false);
    }

    //test();
}


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

    switch (aScale)
    {
        case SCALE_POSITIVE_SPEED_PLUS_DEGREES:
            if (SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed == NULL) {     // look if we have converted already
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
                            aDestinationDirection = 180.0 - aSourceDirection;
                    }
                    else {
                        aDestinationSpeed = aSourceSpeed;
                        aDestinationDirection = aSourceDirection;
                    }
                    break;
                default:            // no conversion from SCALE_POWERS to SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES
                //Q_ASSERT(false);// can be made, but not needed this application yet
                // use right names
                    double aLeftPower = aSourceSpeed;
                    double aRightPower = aSourceDirection;
                    if (fabs(aLeftPower) >= fabs(aRightPower)) { // motor that is running faster, mean direction and angle comes fron slower motor
                        qDebug() << "TuningBean::convert turning right (fabs(aLeftPower) >= fabs(aRightPower) " << (fabs(aLeftPower) >= fabs(aRightPower));
                        aDestinationSpeed = aLeftPower;
                        if (aLeftPower >= 0)
                        {
                            qDebug() << "TuningBean::convert pos. power direction 0 - 90";
                            if (aLeftPower == 0) {
                                aDestinationDirection = 0.0;
                            }
                            else {
                                aDestinationDirection  = 45.0 - (45.0 * aRightPower)/aLeftPower;
                            }
                        } else { // backward, convert pos. power direction 0 - 90";
                            qDebug() << "TuningBean::convert direction 90 - 180";
                            aDestinationDirection  = 45.0 + (45.0 * aRightPower)/aLeftPower;
                        }
                    }
                    else { // turning left
                        qDebug() << "TuningBean::convert turning left";
                        aDestinationSpeed = aRightPower;
                        if (aRightPower >= 0)
                        {
                            qDebug() << "TuningBean::convert pos. power direction -0 - -90";
                            if (aRightPower == 0) {
                                aDestinationDirection = -90.0;
                            }
                            else {
                                aDestinationDirection  = - 45.0 + (45.0 * aLeftPower)/aRightPower;
                            }
                        } else { // backward, convert direction -90 - -180";
                            qDebug() << "TuningBean::convert pos. power direction -0 - -90";
                            aDestinationDirection  = -45.0 - (45.0 * aLeftPower)/aRightPower;
                        }
                    }

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
                    //Q_ASSERT(false);// can be made, but not needed this application yet
                    // use right names
                    double aLeftPower = aSourceSpeed;
                    double aRightPower = aSourceDirection;
                    if (fabs(aLeftPower) >= fabs(aRightPower)) { // motor that is running faster, mean direction and angle comes fron slower motor
                        qDebug() << "TuningBean::convert turning right";
                        aDestinationSpeed = fabs(aLeftPower);
                        if (aLeftPower >= 0)
                        {
                            qDebug() << "TuningBean::convert direction 0 - 90";
                            if (aLeftPower == 0) {
                                aDestinationDirection = 0.0;
                            }
                            else {
                                aDestinationDirection  = 45.0 - (45.0 * aRightPower)/aLeftPower;
                            }
                        } else { // backward, convert direction 90 - 180";
                            qDebug() << "TuningBean::convert direction 90 - 180";
                            aDestinationDirection  = 135.0 + (45.0 * aRightPower)/aLeftPower;
                        }
                    }
                    else { // turning left
                        qDebug() << "TuningBean::convert turning left";
                        aDestinationSpeed = fabs(aRightPower);
                        if (aRightPower >= 0)
                        {
                            qDebug() << "TuningBean::convert direction -0 - -90";
                            if (aRightPower == 0) {
                                aDestinationDirection = -90.0;
                            }
                            else {
                                aDestinationDirection  = - 45.0 + (45.0 * aLeftPower)/aRightPower;
                            }
                        } else { // backward, convert direction -90 - -180";
                            qDebug() << "TuningBean::convert direction -90 - -180";
                            aDestinationDirection  = -135.0 - (45.0 * aLeftPower)/aRightPower;
                        }
                    }

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

    qDebug() << "TuningBean::convert(aSourceScale " << aSourceScale << " aSourceSpeed " << aSourceSpeed << " aSourceDirection " << aSourceDirection << " aDestinationScale " << aDestinationScale << " aDestinationSpeed " << aDestinationSpeed << " aDestinationDirection " << aDestinationDirection;

    return true;

}


bool TuningBean::convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
                        double& aDestinationLeftPower, double& aDestinationRightPower )
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

            if (aSourceDirection >= 0.0){     // turning right
                aDestinationLeftPower = aSourceSpeed;
                aDestinationRightPower = aSourceSpeed * (45.0 - aSourceDirection)/45.0;
            } else {                          // turning left
                aDestinationRightPower = aSourceSpeed;
                aDestinationLeftPower  = -aSourceSpeed * (-45.0 - aSourceDirection)/45.0;
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
                aDestinationLeftPower = aSourceSpeed;
                aDestinationRightPower = aSourceSpeed * (45.0 - aSourceDirection)/45.0;
            } else if ((aSourceDirection >= 90.0) && (aSourceDirection < 180.0)){
                aDestinationRightPower = -aSourceSpeed;
                aDestinationLeftPower = aSourceSpeed * (135.0 - aSourceDirection)/45.0;
            } else if ((aSourceDirection < -90.0 ) && (aSourceDirection >= -180)){
                aDestinationLeftPower = -aSourceSpeed;
                aDestinationRightPower = -aSourceSpeed * (-135.0 - aSourceDirection)/45.0;
            } else if ((aSourceDirection < 0.0) && (aSourceDirection >= -90.0)){
                aDestinationRightPower = aSourceSpeed;
                aDestinationLeftPower  = -aSourceSpeed * (-45.0 - aSourceDirection)/45.0;
            }
            break;
      default:
            Q_ASSERT(false);
            break;
    }

    if (aDestinationLeftPower < -1.0)     // value range
        aDestinationLeftPower = -1.0;
    if (aDestinationLeftPower > 1.0)
        aDestinationLeftPower = 1.0;
    if (aDestinationRightPower < -1.0)
        aDestinationRightPower = -1.0;
    if (aDestinationRightPower > 1.0)
        aDestinationRightPower = 1.0;

    return true;
}


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
        sourceSpeed = fabs(double(i)/90.0);
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
        sourceSpeed = fabs(double(i)/180.0);
        sourceDirection = i;
        ret = convert(SCALE_POSITIVE_SPEED_PLUS_DEGREES, sourceSpeed, sourceDirection,
                      SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, destinationSpeed, destinationDirection);
        Q_ASSERT(ret);
        // destination == source
        Q_ASSERT(fabs(sourceSpeed+destinationSpeed) < 0.1);
        Q_ASSERT(fabs(-180.0 - sourceDirection -destinationDirection) < 0.1);
    }
    for (i=91; i <= 180; i++) {
        sourceSpeed = fabs(double(i)/180.0);
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
        sourceSpeed = fabs(double(i)/90.0);
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


