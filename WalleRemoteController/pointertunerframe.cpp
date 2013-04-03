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

#include <qlayout.h>
#include <qlabel.h>
#include <QMouseEvent>
#include <qwt_wheel.h>
#include <qwt_slider.h>
#include <qwt_thermo.h>
#include <qwt_math.h>
#include "pointertunerframe.h"

#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif

#define PI 3.14159265


PointerTunerFrame::PointerTunerFrame( QWidget *parent ):
   TunerFrame( parent )
{
    setAutoFillBackground(true);
    setStyleSheet("QLabel { background-color : gray; color : blue; }");

    //mBackGroundWidthPer2 = mBackGround->width()/2;
    mBackGroundWidthPer2 = width()/2;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    mBackGroundWidthPer2 = 130;
    mBackGroundWidth = 2*130;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    mBackGroundHightPer2 = height()/2;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;
    mBackGroundHightPer2 = 200;
    mBackGroundHight = 2*200;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;

    mOriginalWallePixmap = new QPixmap(":pictures/wall-e-200x200.png");

    mControlledWallePicture = new QLabel(this);
    mControlledWallePicture->setPixmap(*mOriginalWallePixmap);
    mControlledWallePictureWidthPer2 = 100;
    qDebug() << "mControlledWallePictureWidthPer2 " << mControlledWallePictureWidthPer2;
    mControlledWallePictureHightPer2 = 100;
    mControlledWallePictureSize = 200;
    qDebug() << "mControlledWallePictureHightPer2 " << mControlledWallePictureHightPer2;
    setFrameRect(QRect(0,mControlledWallePictureWidthPer2 *2, 0,mControlledWallePictureWidthPer2*2));
    mControlledWallePicture->move(mBackGroundWidthPer2-mControlledWallePictureWidthPer2,mBackGroundHightPer2-mControlledWallePictureHightPer2);


    mTargetPicture = new QLabel(this);
    mOriginalEwaPixmap = new QPixmap(":pictures/eva-50x50.png");
    mTargetPicture->setPixmap(*mOriginalEwaPixmap);
    mTargetPicture->setScaledContents(true);
    mTargetPicture->setMinimumSize (50, 50);


    mBackGroundMiddleX = mBackGroundWidth/2;
    mBackGroundMiddleY = mBackGroundHight/2;

    mTargetPicture->move(mBackGroundWidthPer2-mTargetPicture->width()/2,0);

    connect(this,SIGNAL(mouseClickEvent(QPoint)),this,SLOT(setTarget(QPoint)));

}

#ifdef old
void PointerTunerFrame::setSpeedDirection( TunerManager::Scale scale, double speed, double direction )
{
    qDebug() << "PointerTunerFrame::setSpeedDirection speed" << speed << "direction"  << direction;

    // convert values to right scale for us
    TunerManager::convert(scale, speed, direction,
                          TunerManager::SCALE_POSITIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection);


    // scale targed
    int size = (50 + (1.0 - mSpeed)*100.0);
    mTargetPicture->resize(size, size);

    int x =  mBackGroundMiddleX  - (size/2) + ((sin(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
//    qDebug() << "backGroundMiddleX()" << backGroundMiddleX();
    int y =  mBackGroundMiddleY - (size/2) - ((cos(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
    qDebug() << "PointerTunerFrame::setSpeed x" << x << " y " << y;

    mTargetPicture->move(x,y);

    mDirection = direction;
    QMatrix matrix;
    matrix.rotate(direction);
    QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(matrix);
    mControlledWallePicture->setPixmap(rotatedControlledPixmap);

}
#endif

void PointerTunerFrame::setTuning( TuningBean* aTuningBean )
{
    qDebug() << "SliderTunerFrame.setTuning";

    mSpeed =  aTuningBean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES);
    mDirection =  aTuningBean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES);

    // scale targed
    int size = (50 + (1.0 - mSpeed)*100.0);
    mTargetPicture->resize(size, size);

    int x =  mBackGroundMiddleX  - (size/2) + ((sin(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
//    qDebug() << "backGroundMiddleX()" << backGroundMiddleX();
    int y =  mBackGroundMiddleY - (size/2) - ((cos(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
    qDebug() << "PointerTunerFrame::setSpeed x" << x << " y " << y;

    mTargetPicture->move(x,y);

    QMatrix matrix;
    matrix.rotate(mDirection);
    QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(matrix);
    mControlledWallePicture->setPixmap(rotatedControlledPixmap);
}


void PointerTunerFrame::setPower( double leftPower, double rightPower )
{
    qDebug() << "PointerTunerFrame::setPower leftPower " << leftPower << " rightPower "  << rightPower;
    // TODO
    // set powers to direction and speed
}




void PointerTunerFrame::setTarget(QPoint p)
{
    qDebug() << "PointerTunerFrame::setTarget" << endl;
    mTargetPicture->move(p.x()-(mTargetPicture->width()/2),p.y()-(mTargetPicture->height()/2));

    int x = p.x() - mBackGroundWidthPer2;
    int y = p.y() - mBackGroundHightPer2;
    if (false /*x == 0*/) {
        mControlledWallePicture->setPixmap(*mOriginalWallePixmap);
    } else {
        QMatrix matrix;
        mDirection = atan2 (x,-y) * 180.0 / PI;
        qDebug() << "PointerTunerFrame::setTarget direction " << mDirection;

        // rotate Waller
        matrix.rotate(mDirection);
        QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(matrix);
        mControlledWallePicture->setPixmap(rotatedControlledPixmap);

        mSpeed = sqrt((x*x) + (y*y))/mBackGroundWidthPer2;
        // scale Ewa target
        int size = (50 + (1.0 - mSpeed)*100.0);
        mTargetPicture->resize(size, size);
        qDebug() << "PointerTunerFrame::setTarget speed " << mSpeed;

        //emit speedDirectionChanged(TunerManager::SCALE_POSITIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection);
        emit tuningChanged(new TuningBean(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection, this));
    }
}

void PointerTunerFrame::mousePressEvent ( QMouseEvent * e )
{
    qDebug() << "PointerTunerFrame::mousePressEvent" << endl;
    // store click position
    m_lastPoint = e->pos();
    emit mouseClickEvent(m_lastPoint);
}

void PointerTunerFrame::mouseReleaseEvent ( QMouseEvent * e )
{
    qDebug() << "PointerTunerFrame::mouseReleaseEvent" << endl;
    // store click position
    m_lastPoint = e->pos();
    emit mouseClickEvent(m_lastPoint);
}

void PointerTunerFrame::mouseMoveEvent ( QMouseEvent * e )
{
    qDebug() << "PointerTunerFrame::mouseMoveEvent" << endl;
    // store click position
    m_lastPoint = e->pos();
    emit mouseClickEvent(m_lastPoint);
}

