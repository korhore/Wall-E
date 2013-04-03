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


#ifndef TUNERFRAME_H
#define TUNERFRAME_H

#include <QFrame>
#include "tunermanager.h"
#include "tuningbean.h"

class QwtWheel;
class QwtSlider;
class TuningThermo;

class TunerFrame : public QFrame
{
    Q_OBJECT
public:
    TunerFrame( QWidget *p );

Q_SIGNALS:
    //virtual void speedDirectionChanged(TunerManager::Scale scale, double speed, double direction ) = 0;
    virtual void tuningChanged(TuningBean* aTuningBean ) = 0;


public Q_SLOTS:
    //virtual void setSpeedDirection(TunerManager::Scale scale, double speed, double direction ) = 0;
    virtual void setTuning(TuningBean* aTuningBean ) = 0;
    virtual void setPower( double leftPower, double rightPower ) = 0;
};

#endif // TUNERFRAME_H





