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


#include "tunerframe.h"

#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif


TunerFrame::TunerFrame( QWidget *parent ):
    QFrame( parent )
{
}

/*
void TunerFrame::handleDirectionChange( double direction )
{
    qDebug() << "handleDirectionChange";
    Q_EMIT directionChanged(direction) ;
}

void TunerFrame::handleSpeedChange( double speed )
{
    qDebug() << "handleSpeedChange";
    Q_EMIT speedChanged(speed) ;
}
*/
