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


#ifndef TUNERMANAGER_H
#define TUNERMANAGER_H


/*

Converrsion from one controllerr to other and power controlling output



  */

#include <QObject>
#include "command.h"
class FtpClient;

class TunerManager : public QObject
{
    Q_OBJECT
public:
    explicit TunerManager( QWidget *p );
    virtual ~TunerManager();

Q_SIGNALS:
    void directionChanged( double direction );
    void speedChanged( double speed );
 //   void powerChanged( bool running, double leftPower, double rightPower );

    void commandProsessed(Command command);


public Q_SLOTS:
    virtual void setDirection( double direction );
    virtual void setSpeed( double speed );
    void setPower( double leftPower, double rightPower );
    void setHost( QString ipAddress, int port);

private Q_SLOTS:
    void handleCommandProsessed(Command command);


    //virtual void setPoint(QPoint point);
    //virtual void setSize(QSize size);

private:
    void calculatePower();


private:
    // Slider tuner
    double mDirection;
    double mSpeed;

    // pointer tiner
    // member variable to store click position
    //QPoint mPoint;
    //QSize mSize;

    // Power
    double mLeftPower;
    double mRightPower;
    bool mRunning;      // is car moving or topped

    FtpClient* mFtpClient;
    QString ipAddress;
    int port;
    Command mLastComand;
    Command mCandidateCommand;


};

#endif // TUNERMANAGER_H





