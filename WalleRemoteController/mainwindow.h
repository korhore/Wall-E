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


#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtGui/QMainWindow>
#include <QtGui/QMainWindow>
#include "devicemanager.h"

class QHBoxLayout;
class SliderTunerFrame;
class PointerTunerFrame;
class PowerTunerFrame;
//class DeviceManager;
class TuningBean;


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

    // Getters for Visual classes

    SliderTunerFrame* getSliderTunerFrame() { return mSliderTunerFrame; };
    PointerTunerFrame* getPointerTunerFrame() { return mPointerTunerFrame; };
    PowerTunerFrame* getPowerTunerFrame() { return mPowerTunerFrame; };

Q_SIGNALS:
    void tuningChanged(TuningBean* aTuningBean);
    void hostChanged(QString ipAddress, int port);
public Q_SLOTS:
    void setDeviceState(TuningBean* aTuningBean);
    void setDeviceState(DeviceManager::DeviceState aDeviceState);


private Q_SLOTS:
    void setTuning(TuningBean* aTuningBean);


private:
    QHBoxLayout* mMainLayout;
    SliderTunerFrame* mSliderTunerFrame;
    PointerTunerFrame* mPointerTunerFrame;
    PowerTunerFrame* mPowerTunerFrame;
//    DeviceManager* mTunerManager;
};

#endif // MAINWINDOW_H
