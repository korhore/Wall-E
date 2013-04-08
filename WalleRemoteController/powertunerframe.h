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


#ifndef POWERTUNERFRAME_H
#define POWERTUNERFRAME_H

#include <QFrame>
#include "command.h"
#include "tuningbean.h"

class QwtSlider;

class PowerTunerFrame : public QFrame
{
    Q_OBJECT
public:
    PowerTunerFrame( QWidget *p=NULL );

signals:
    //void powerChanged( double leftPower, double rightPower );
    virtual void tuningChanged(TuningBean* aTuningBean );

public Q_SLOTS:
    //void setpower( bool running, double leftPower, double rightPower );
    void setCommand(Command command);
    //virtual void setPower( double leftPower, double rightPower );
    virtual void setTuning(TuningBean* aTuningBean);
    //virtual void setSpeedDirection( double speed, double direction );

private Q_SLOTS:
    void handleSettings();
    void handleLeftPowerChange( double leftPower );
    void handleRightPowerChange( double rightPower );


private:
/*    QwtThermo *mLeftThermoUp;
    QwtThermo *mLeftThermoDown;
    QwtThermo *mRightThermoUp;
    QwtThermo *mRightThermoDown;
*/
    QwtSlider *mLeftPowerSlider;
    QwtSlider *mRightPowerSlider;

    bool mRunning;
    double mLeftPower;
    double mRightPower;
};

#endif // POWERTUNERFRAME_H




