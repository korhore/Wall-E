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
    //mBackGround = new BackGround(this);
    //mBackGround ->setAutoFillBackground(true);
    //mBackGround->setStyleSheet("QLabel { background-color : gray; color : blue; }");

    setAutoFillBackground(true);
    setStyleSheet("QLabel { background-color : gray; color : blue; }");

    //mBackGroundWidthPer2 = mBackGround->width()/2;
    mBackGroundWidthPer2 = width()/2;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    mBackGroundWidthPer2 = 150;
    mBackGroundWidth = 2*150;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    //mBackGroundHightPer2 = mBackGround->height()/2;
    mBackGroundHightPer2 = height()/2;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;
    mBackGroundHightPer2 = 200;
    mBackGroundHight = 2*200;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;

    mOriginalWallePixmap = new QPixmap(":pictures/wall-e-200x200.png");

    /**/
    //mControlledWallePicture = new QLabel(mBackGround);
    mControlledWallePicture = new QLabel(this);
    mControlledWallePicture->setPixmap(*mOriginalWallePixmap);
//    mControlledWallePicture->setPixmap(QPixmap(":/pictures/pirate-300x300.png"));
    //mControlledWallePictureWidthPer2 = mControlledWallePicture->width()/2;
    mControlledWallePictureWidthPer2 = 100;
    qDebug() << "mControlledWallePictureWidthPer2 " << mControlledWallePictureWidthPer2;
    //mControlledWallePictureHightPer2 = mControlledWallePicture->height()/2;
    mControlledWallePictureHightPer2 = 100;
    mControlledWallePictureSize = 200;
    qDebug() << "mControlledWallePictureHightPer2 " << mControlledWallePictureHightPer2;
    setFrameRect(QRect(0,mControlledWallePictureWidthPer2 *2, 0,mControlledWallePictureWidthPer2*2));
    mControlledWallePicture->move(mBackGroundWidthPer2-mControlledWallePictureWidthPer2,mBackGroundHightPer2-mControlledWallePictureHightPer2);


    //mTargetPicture = new QLabel(mBackGround);

    mTargetPicture = new QLabel(this);
    mOriginalEwaPixmap = new QPixmap(":pictures/eva-50x50.png");
    mTargetPicture->setPixmap(*mOriginalEwaPixmap);
    mTargetPicture->setScaledContents(true);
    mTargetPicture->setMinimumSize (50, 50);


//    mTargetPicture = new QPixmap(":pictures/eva-50x50.png");
    //mTargetPictureWidthPer2 = mOriginalEwaPixmap->width()/2;
    //mTargetPictureWidthPer2 = 25;
    //qDebug() << "mTargetPictureWidthPer2 " << mTargetPictureWidthPer2;
    //mTargetPictureHightPer2 = mOriginalEwaPixmap->height()/2;
    //mTargetPictureHightPer2 = 25;
    //mTargetPictureSize = mOriginalEwaPixmap->width();//50;
    //mTargetPictureSizePer2 = mOriginalEwaPixmap->width()/2;//25;
    //qDebug() << "mTargetPictureHightPer2 " << mTargetPictureHightPer2;
    mBackGroundMiddleX = mBackGroundWidth/2;
    mBackGroundMiddleY = mBackGroundHight/2;

    mTargetPicture->move(mBackGroundWidthPer2-mTargetPicture->width()/2,0);

    //connect(mBackGround,SIGNAL(mouseClickEvent(QPoint)),this,SLOT(setTarget(QPoint)));
    // TODO
    connect(this,SIGNAL(mouseClickEvent(QPoint)),this,SLOT(setTarget(QPoint)));

}

/*
int PointerTunerFrame::backGroundMiddleX() {
    return mBackGroundWidth - mTargetPicture->width()/2;
}

int PointerTunerFrame::backGroundMiddleY() {
    return mBackGroundHight - mTargetPicture->height()/2;
}
*/

void PointerTunerFrame::setDirection( double direction )
{
    qDebug() << "PointerTunerFrame::setDirection speed" << mSpeed << "direction"  << direction;
    mDirection = direction;
    QMatrix matrix;
    matrix.rotate(direction);
    QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(matrix);
    mControlledWallePicture->setPixmap(rotatedControlledPixmap);
    setSpeed( mSpeed );
}

void PointerTunerFrame::setSpeed( double speed )
{
    qDebug() << "PointerTunerFrame::setSpeed speed" << speed << "direction"  << mDirection;
    mSpeed = speed;
    // scale targed
    int size = (50 + (1.0 - speed)*100.0);
    mTargetPicture->resize(size, size);

    int x =  mBackGroundMiddleX  - (size/2) + ((sin(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
//    qDebug() << "backGroundMiddleX()" << backGroundMiddleX();
    int y =  mBackGroundMiddleY - (size/2) - ((cos(mDirection * PI/180.0) *  mSpeed * mBackGroundMiddleX));
    qDebug() << "PointerTunerFrame::setSpeed x" << x << " y " << y;

    mTargetPicture->move(x,y);
}

void PointerTunerFrame::handleDirectionChange( double direction )
{
    qDebug() << "PointerTunerFrame.handleDirectionChange";
    //Q_EMIT directionChanged(direction) ;
}

void PointerTunerFrame::handleSpeedChange( double speed )
{
    qDebug() << "PointerTunerFrame.handleSpeedChange";
    //Q_EMIT speedChanged(speed) ;
}

void PointerTunerFrame::setTarget(QPoint p)
{
    qDebug() << "PointerTunerFrame::setTarget" << endl;
    //mTargetPicture->move(p.x()-mBackGroundWidthPer2-(mTargetPicture->width()/2),p.y()-(mTargetPicture->height()/2));
    mTargetPicture->move(p.x()-(mTargetPicture->width()/2),p.y()-(mTargetPicture->height()/2));

/**/
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

        emit directionChanged(mDirection );
        emit speedChanged( mSpeed );
    }
    /**/
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

