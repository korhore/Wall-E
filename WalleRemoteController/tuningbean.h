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


#ifndef TUNINGBEAN_H
#define TUNINGBEAN_H


/*

Bean class that handles tuning value

*/

#include <QObject>

class TuningBean : public QObject
{
    //Q_OBJECT
public:

    enum Scale {SCALE_POSITIVE_SPEED_PLUS_DEGREES, SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES, SCALE_POWERS};
    explicit TuningBean(Scale aScale, double aValue1, double aValue2, QObject *parent=NULL);
//    explicit TuningBean( double aLeftPower, double aRightPower, QObject *parent=NULL );
    virtual ~TuningBean();

    // getters
    double getSpeed(TuningBean::Scale aScale);
    double getDirection(TuningBean::Scale aScale);
    double getLeftPower();
    double getRightPower();



    bool test();




private:
    /* conversions between different scales od speed + direction
       from speed to power and opposite */

    bool static convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
                        Scale aDestinationScale, double& aDestinationSpeed, double& aDestinationeDirection);
    bool static convert(Scale aSourceScale, double aSourceSpeed, double aSourceDirection,
                        double& aDestinationeLeftPower, double& aDestinationeRightPower );


private:

    Scale mScale;

    // Slider tuner
    double mValue1; // mSpeed/mLeftPower;
    double mValue2; // mDirection/mRightPower;

    double* SCALE_POSITIVE_SPEED_PLUS_DEGREES_mSpeed;
    double* SCALE_POSITIVE_SPEED_PLUS_DEGREES_mDirection;

    double* SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mSpeed;
    double* SCALE_POSITIVE_NEGATIVE_SPEED_PLUS_DEGREES_mDirection;

    // Power
    double* mLeftPower;
    double* mRightPower;


};

#endif // TUNINGBEAN_H





