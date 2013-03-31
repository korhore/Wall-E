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

#include <QPushButton>
#include <QLineEdit>
#include <QLabel>
#include <QSettings>
#include <QDebug>
#include "settingsdialog.h"
#include "ipnumberwidged.h"



SettingsDialog::SettingsDialog(QWidget *parent, QString hostIP/*=""*/, int port/*=0*/) :
    QDialog(parent)
{
     QPushButton *closeButton = new QPushButton(tr("Close"));

     connect(closeButton, SIGNAL(clicked()), this, SLOT(close()));

     QLabel* hostLabel = new QLabel(tr("IP of the Wall-E Host"), this);

     // Get saved network configuration
     QSettings settings(QSettings::UserScope, QLatin1String("Wall-E"));
     settings.beginGroup(QLatin1String("Host"));
     hostIP = settings.value(QLatin1String("IP"), hostIP).toString();
     port = settings.value(QLatin1String("PORT"), port).toInt();
     settings.endGroup();

     mIPNumberWidget = new IPNumberWidget(this, hostIP);
     connect(mIPNumberWidget, SIGNAL(signalTextChanged(QString)), this, SLOT(hostIPChanged(QString)));

     QWidget *hostWidget= new QWidget(this);
     QHBoxLayout *hostlLayout = new QHBoxLayout(hostWidget);
     hostlLayout->addWidget(hostLabel,100);
     hostlLayout->addWidget(mIPNumberWidget, 700, Qt::AlignRight);

     QLabel* portLabel = new QLabel(tr("Port"), this);
     mPortNumber = new QLineEdit(this);
     mPortNumber->setText(QString::number(port));
     connect(mPortNumber, SIGNAL(textEdited (const QString)), this, SLOT(portChanged(const QString)));

     QWidget *portWidget= new QWidget(this);
     QHBoxLayout *portlLayout = new QHBoxLayout(portWidget);
     portlLayout->addWidget(portLabel);
     portlLayout->addWidget(mPortNumber, 200, Qt::AlignRight );

     QVBoxLayout *mainLayout = new QVBoxLayout;
     mainLayout->addWidget(hostWidget);
     //mainLayout->addStretch(1);
     //mainLayout->addSpacing(12);
     mainLayout->addWidget(portWidget);

     mainLayout->addWidget(closeButton, 20, Qt::AlignRight);
     setLayout(mainLayout);

     setWindowTitle(tr("Settings"));

}

void SettingsDialog::hostIPChanged(QString hostIP)
{
    // Saved network configuration
    qDebug() << "SettingsDialog::hostIPChanged " << hostIP;
    QSettings settings(QSettings::UserScope, QLatin1String("Wall-E"));
    settings.beginGroup(QLatin1String("Host"));
    settings.setValue(QLatin1String("IP"), hostIP);
    settings.endGroup();

}

void SettingsDialog::portChanged(const QString port)
{
    // Saved network configuration
    qDebug() << "SettingsDialog::portChanged " << port;
    QSettings settings(QSettings::UserScope, QLatin1String("Wall-E"));
    settings.beginGroup(QLatin1String("Host"));
    settings.setValue(QLatin1String("PORT"), port.toInt());
    settings.endGroup();

}

