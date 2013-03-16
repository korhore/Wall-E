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


#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtGui/QMainWindow>
#include <QtGui/QWidget>
#include <QtGui/QPixmap>
#include <QtGui/QLabel>
#include <QCompass> // Add Sensor Class

//#include <background.h>

class QwtSlider;
class QHBoxLayout;
class QVBoxLayout;
class QwtCompass;
class QwtWheel;
class SliderTunerFrame;
class PointerTunerFrame;
class PowerTunerFrame;
class TunerManager;

// add Qt Mobility Project Namespace
QTM_USE_NAMESPACE


class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    enum ScreenOrientation {
        ScreenOrientationLockPortrait,
        ScreenOrientationLockLandscape,
        ScreenOrientationAuto
    };

    explicit MainWindow(QWidget *parent = 0);
    virtual ~MainWindow();

    // Note that this will only have an effect on Symbian and Fremantle.
    void setOrientation(ScreenOrientation orientation);

    void showExpanded();
private slots:
 //   void setTarget(QPoint);


private:
    //BackGround* mBackGround;
    //QHBoxLayout* mHBox;
    //QLabel* mControllerBackground;
    QHBoxLayout* mMainLayout;
    //QPixmap* mOriginalWallePixmap;
    //QLabel* mControlledWallePicture;
    //QLabel* mRealWallePicture;
    //QLabel* mTargetPicture;
    //QwtSlider* mDirectionSlider;
    //QwtSlider* mSpeedSlider;
    SliderTunerFrame* mSliderTunerFrame;
    PointerTunerFrame* mPointerTunerFrame;
    PowerTunerFrame* mPowerTunerFrame;
    TunerManager* mTunerManager;
    //QwtCompass* mQwtCompass;
    //QwtWheel* mQwtWheel;
    //QMatrix mMatrix;

    //int mBackGroundWidthPer2;
    //int mBackGroundHightPer2;

    //int mControlledWallePictureWidthPer2;
    //int mControlledWallePictureHightPer2;

    //int mTargetPictureWidthPer2;
    //int mTargetPictureHightPer2;

    //QCompass* mCompass;

};

#endif // MAINWINDOW_H
