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


#ifndef TUNERCONTROLLER_H
#define TUNERCONTROLLER_H


/*

Controller class that handles Visual and Model classes  and
knows their capabilities, but not how they implement it.

*/

#include <QWidget>
#include "command.h"
class FtpClient;
class TuningBean;
class MainWindow;
class PointerTunerFrame;
class SliderTunerFrame;
class PowerTunerFrame;
class DeviceManager;

class TunerController : public QWidget
{
    Q_OBJECT
public:

    explicit TunerController(QWidget *p=NULL );
    virtual ~TunerController();

private:
    MainWindow* mMainWindow;
    SliderTunerFrame* mSliderTunerFrame;
    PointerTunerFrame* mPointerTunerFrame;
    PowerTunerFrame* mPowerTunerFrame;
    DeviceManager* mDeviceManager;

};

#endif // TUNERCONTROLLER_H





