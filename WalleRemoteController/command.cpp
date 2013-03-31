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

#include <QList>
#include <QString>
#include <QStringList>
#include <QDebug>
#include <math.h>
#include "command.h"

Command::Command(QString string/*=""*/,
                 unsigned int number/*=-1*/, CommandType command/* = Unknown*/,
                 double leftPower /* = 0.0*/, double rightPower/* = 0.0*/) :
    mNumber(number),
    mCommand(command),
    mLeftPower(leftPower),
    mRightPower(rightPower)
{
    QList<QString> params = string.split(' ');
    qDebug()  << "Command::Command params " << params;
    if ((params.count() >= 1) && (params[0].length() > 0))
    {
        bool ok;
        mNumber = params[0].toUInt(&ok);
        if (!ok)
        {
            mCommand = Unknown;
            return;
        }
        qDebug()  << "Command::Command number " << mNumber;
        if (params.count() >= 2 )
        {
            QCharRef ch = params[1][0];
            if (ch == ( char ) Drive)
            {
                mCommand = Drive;
                qDebug()  << "Command::Command Drive";
                if (params.count() >= 3)
                {
                    mLeftPower = params[2].toDouble();
                    qDebug()  << "Command::Command LeftPower " << mLeftPower;
                    if (params.count() >= 4)
                    {
                        mRightPower = params[3].toDouble();
                        qDebug()  << "Command::Command RightPower " << mRightPower;
                    }
                }
            }
            else
            {
                if (ch == ( char ) Stop)
                {
                    mCommand = Stop;

                }
                else
                {
                    if (ch == ( char ) Who)
                    {
                        mCommand = Who;
                    }
                    else
                    {
                        mCommand = Unknown;
                    }
                }
            }
        }
    }
    qDebug()  << "Command::Command command " << this->toString();
}


Command::Command(const Command& other)
{
    mNumber = other.getNumber();
    mCommand = other.getCommand();
    mLeftPower = other.getLeftPower();
    mRightPower = other.getRightPower();
}


QString Command::toString()
{
    QString s;
    switch (mCommand)
    {
    case Drive:
        s = QString(QString::number(mNumber) + ' ' + char(Drive) + ' ' + QString::number(mLeftPower) + ' ' + QString::number(mRightPower));
        break;
    case Stop:
        s = QString(QString::number(mNumber) + ' ' + char(Stop));
        break;
    case Who:
        s = QString(QString::number(mNumber) + ' ' + char(Who));
        break;
    default:
        s = QString(QString::number(mNumber) + ' ' + (char) Unknown);
        break;
    }

    return s;

}


void Command::setNumber(unsigned int number)
{
    mNumber = number;
}

unsigned int Command::getNumber() const
{
    return mNumber;
}

void Command::setCommand(CommandType command)
{
    mCommand = command;
}

Command::CommandType Command::getCommand() const
{
    return mCommand;
}


void Command::setLeftPower(double leftPower)
{
    mLeftPower = leftPower ;
}

double Command::getLeftPower() const
{
    return mLeftPower;
}

void Command::setRightPower(double rightPower)
{
    mRightPower = rightPower ;
}

double Command::getRightPower() const
{
    return mRightPower;
}

bool Command::isDifferent(const Command other)
{
    if (other.getCommand() != getCommand())
        return true;

    if (getCommand() == Command::Drive)
    {
        if (fabs (other.getLeftPower() - getLeftPower()) > 0.05)
            return true;
        if (fabs (other.getRightPower() - getRightPower()) > 0.05)
            return true;
    }

    return false;
}


