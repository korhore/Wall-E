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


#ifndef SETTINGSDIALOG_H
#define SETTINGSDIALOG_H

#include <QDialog>
#include "ftpclient.h"

#define SETTING_STR             "Wall-E"
#define SETTING_HOST_IP_STR     "IP"
#define SETTING_PORT_STR        "PORT"
#define SETTING_CAMERA_PORT_STR "CAMERA_PORT"

class IPNumberWidget;
class QLineEdit;

class SettingsDialog : public QDialog
{
    Q_OBJECT
public:
    explicit SettingsDialog(QWidget *parent, QString hostIP=SERVERNAME, int port=SERVERPORT, int cameraPort=SERVERCAMERAPORT);
    
signals:
    
public slots:

private slots:
    void hostIPChanged(QString hostIP);
    void portChanged(const QString port);
    void cameraPortChanged(const QString port);

private:
    IPNumberWidget* mIPNumberWidget;
    QLineEdit* mPortNumber;
    QLineEdit* mCameraPortNumber;

};

#endif // SETTINGSDIALOG_H
