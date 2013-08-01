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
//#include <qwt_wheel.h>
//#include <qwt_slider.h>
//#include <qwt_thermo.h>
//#include <qwt_math.h>
#include <math.h>
#include "pointertunerframe.h"

#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif

#define PI 3.14159265

#if defined(Q_WS_S60)
#define TARGET_SIZE                 50
#define WALLE_WIDTH                 100
#define WALLE_WIDTH_DOUBLE          100.0
#define BACKGROUND_WIDTH_PER_2      100
#define BACKGROUND_HEIGHT_PER_2     150
#else
#define TARGET_SIZE                 50
#define WALLE_WIDTH                 100
#define WALLE_WIDTH_DOUBLE          100.0
#define BACKGROUND_WIDTH_PER_2      130
#define BACKGROUND_HEIGHT_PER_2     200
#endif


PointerTunerFrame::PointerTunerFrame( QWidget *parent ):
   TunerFrame( parent )
{
    mBackGroundWidthPer2 = width()/2;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    mBackGroundWidthPer2 = BACKGROUND_WIDTH_PER_2;
    mBackGroundWidth = 2*BACKGROUND_WIDTH_PER_2;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    mBackGroundHightPer2 = height()/2;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;
    mBackGroundHightPer2 = BACKGROUND_HEIGHT_PER_2;
    mBackGroundHight = 2*BACKGROUND_HEIGHT_PER_2;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;

    mOriginalWallePixmap = new QPixmap(":pictures/wall-e-200x200.png");

    mControlledWallePicture = new QLabel(this);
    mControlledWallePicture->setPixmap(*mOriginalWallePixmap);
    mControlledWallePictureWidthPer2 = WALLE_WIDTH;
    qDebug() << "mControlledWallePictureWidthPer2 " << mControlledWallePictureWidthPer2;
    mControlledWallePictureHightPer2 = WALLE_WIDTH;
    mControlledWallePictureSize = BACKGROUND_HEIGHT_PER_2;
    qDebug() << "mControlledWallePictureHightPer2 " << mControlledWallePictureHightPer2;
    setFrameRect(QRect(0,mControlledWallePictureWidthPer2 *2, 0,mControlledWallePictureWidthPer2*2));
    mControlledWallePicture->move(mBackGroundWidthPer2-mControlledWallePictureWidthPer2,mBackGroundHightPer2-mControlledWallePictureHightPer2);


    mTargetPicture = new QLabel(this);
    mOriginalEwaPixmap = new QPixmap(":pictures/eva-50x50.png");
    mTargetPicture->setPixmap(*mOriginalEwaPixmap);
    mTargetPicture->setScaledContents(true);
    mTargetPicture->setMinimumSize (TARGET_SIZE, TARGET_SIZE);


    mBackGroundMiddleX = mBackGroundWidth/2;
    mBackGroundMiddleY = mBackGroundHight/2;

    mTargetPicture->move(mBackGroundWidthPer2-mTargetPicture->width()/2,0);


    connect(this,SIGNAL(mouseClickEvent(QPoint)),this,SLOT(setTarget(QPoint)));

}




void PointerTunerFrame::setTuning( TuningBean* aTuningBean )
{
    qDebug() << "SliderTunerFrame.setTuning";

    mSpeed =  aTuningBean->getSpeed(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES);
    mDirection =  aTuningBean->getDirection(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES);

    // scale targed
    int size = (TARGET_SIZE + (1.0 - mSpeed)*WALLE_WIDTH_DOUBLE);
    mTargetPicture->resize(size, size);

    int x =  mBackGroundMiddleX  - (size/2) + ((sin(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
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
    QMatrix matrix;
    mDirection = atan2 ((double)x,(double)-y) * 180.0 / PI;
    qDebug() << "PointerTunerFrame::setTarget direction " << mDirection;

    // rotate Walle
    matrix.rotate(mDirection);
    QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(matrix);
    mControlledWallePicture->setPixmap(rotatedControlledPixmap);

    mSpeed = sqrt((double)(x*x) + (double)(y*y))/(double)mBackGroundWidthPer2;
    // scale Ewa target
    int size = (TARGET_SIZE + (1.0 - mSpeed)*WALLE_WIDTH_DOUBLE);
    mTargetPicture->resize(size, size);
    qDebug() << "PointerTunerFrame::setTarget speed " << mSpeed;

    emit tuningChanged(new TuningBean(TuningBean::SCALE_POSITIVE_SPEED_PLUS_DEGREES, mSpeed, mDirection, this));
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

