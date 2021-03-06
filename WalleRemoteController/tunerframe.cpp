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


#include "tunerframe.h"
#include <QGraphicsOpacityEffect>


TunerFrame::TunerFrame( QWidget *parent ):
    QFrame( parent ),
    mOpacity(1.0)
{
    mGraphicsOpacityEffect = new QGraphicsOpacityEffect(this);
}

void TunerFrame::setOpacity(qreal aOpacity)
{
    mOpacity = aOpacity;
    mGraphicsOpacityEffect->setOpacity(mOpacity);
    setGraphicsEffect(mGraphicsOpacityEffect);
}

