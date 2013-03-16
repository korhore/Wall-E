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


#ifndef SLIDERTUNERFRAME_H
#define SLIDERTUNERFRAME_H

#include <QFrame>
#include "tunerframe.h"

class QwtSlider;

class SliderTunerFrame : public TunerFrame
{
    Q_OBJECT
public:
    SliderTunerFrame( QWidget *p=NULL );

Q_SIGNALS:
    void directionChanged( double speed );
    void speedChanged( double speed );

public Q_SLOTS:
    virtual void setDirection( double direction );
    virtual void setSpeed( double speed );

private Q_SLOTS:
    void handleDirectionChange( double direction );
    void handleSpeedChange( double speed );


private:
    QwtSlider *mSliderDirection;
    QwtSlider *mSliderSpeed;
};

#endif // SLIDERTUNERFRAME_H




