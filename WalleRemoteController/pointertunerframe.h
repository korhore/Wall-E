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


#ifndef POINTERTUNERFRAME_H
#define POINTERTUNERFRAME_H

#include <QFrame>
#include "tunerframe.h"
#include "background.h"

class QwtSlider;

class PointerTunerFrame : public TunerFrame
{
    Q_OBJECT
public:
    PointerTunerFrame( QWidget *p=NULL );

protected:
    // re-implement processing of mouse events
    virtual void mouseReleaseEvent ( QMouseEvent * e );
    virtual void mousePressEvent ( QMouseEvent * e );
    virtual void mouseMoveEvent ( QMouseEvent * e );


public:
signals:
    // define mouseClick signal
    void mouseClickEvent(QPoint);


Q_SIGNALS:
    virtual void tuningChanged(TuningBean* aTuningBean );

public Q_SLOTS:
    virtual void setTuning(TuningBean* aTuningBean );
    virtual void setPower( double leftPower, double rightPower );



private slots:
    void setTarget(QPoint);



private:

    BackGround* mBackGround;
    QLabel* mControlledWallePicture;
    QLabel* mTargetPicture;
    QPixmap* mOriginalWallePixmap;
    QPixmap* mOriginalEwaPixmap;
    QPixmap* mScaledEwaPixmap;

    double mDirection;
    double mSpeed;


    int mBackGroundWidthPer2;
    int mBackGroundHightPer2;
    int mBackGroundWidth;
    int mBackGroundHight;
    int mBackGroundMiddleX;
    int mBackGroundMiddleY;

    int mControlledWallePictureSize;
    int mControlledWallePictureWidthPer2;
    int mControlledWallePictureHightPer2;


    // member variable to store click position
    QPoint m_lastPoint;


};

#endif //POINTERTUNERFRAME_H




