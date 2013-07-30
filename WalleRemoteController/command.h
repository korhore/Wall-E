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


#ifndef COMMAND_H
#define COMMAND_H

#include <QObject>
#include <QByteArray>

class Command
{
public:
    enum CommandType {Drive='D', Stop='S', Who='W', Picture='P', Unknown='U'};

    explicit Command(QString string="",
                     unsigned int number=-1, CommandType command = Unknown,
                     double leftPower = 0.0, double rightPower = 0.0,
                     unsigned int imageSize = 0);
    Command(const Command& other);

    QString toString();

    void setNumber(unsigned int number);
    unsigned int getNumber() const;

    void setCommand(CommandType command);
    CommandType getCommand() const;

    void setLeftPower(double leftPower);
    double getLeftPower() const;

    void setRightPower(double rightPower);
    double getRightPower() const;

    void setImageSize(unsigned int imageSize);
    unsigned int getImageSize() const;

    void setImageData(const QByteArray& aImageData);
    void addImageData(const QByteArray& aImageData);
    const QByteArray& getImageData() const;


    /*
      Is command enough different than other
      This is used to minimize traffic to the server.
      If other coonad is much same than other one, it is not mean to send it to the server
      */

    bool isDifferent(const Command other);

    
signals:
    
public slots:

private:
    unsigned int mNumber;
    CommandType mCommand;
    double mLeftPower;
    double mRightPower;
    unsigned int mImageSize;
    QByteArray mImageData;
    
};

#endif // COMMAND_H
