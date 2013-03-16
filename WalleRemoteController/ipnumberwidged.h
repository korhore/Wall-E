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

#ifndef IPNUMBERWIDGED_H
#define IPNUMBERWIDGED_H

#include <QFrame>
#include <QLineEdit>
#include <QIntValidator>
#include "stdint.h"
#include <QHBoxLayout>
#include <QFont>
#include <QLabel>
#include <QKeyEvent>


class IPNumberWidget : public QFrame // QWidget //
{
//    typedef QWidget baseClass;
    typedef QFrame baseClass;

    Q_OBJECT

public:
    IPNumberWidget(QWidget *parent, QString hostIP="", int portnumber=0);
    ~IPNumberWidget();

#define QTUTL_IP_SIZE 4

    virtual bool eventFilter( QObject *obj, QEvent *event );

public:
signals:
    void signalTextChanged( QString hostIP );

private:
signals:
    void signalTextChanged( QLineEdit* pEdit );
private slots:
    void slotTextChanged( QLineEdit* pEdit );


private:
    void handleTextChanged();

    QLineEdit *(m_pLineEdit[QTUTL_IP_SIZE]);

    static std::string getIPItemStr( unsigned char item );
};


#endif // IPNUMBERWIDGED_H
