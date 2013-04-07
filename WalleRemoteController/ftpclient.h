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

#ifndef FTPCLIENT_H
#define FTPCLIENT_H

#include <QObject>
#include <QTcpSocket>
#include <QList>
#include <QString>
#include "command.h"
#include "devicemanager.h"



#define SERVERNAME "192.168.1.7"
#define SERVERPORT 2000

#define REQUEST_WHO "%1 W |"
#define ANSWER_WHO_WALLE "Wall-E |"
#define ANSWER_WHO_REMOTECONTROLLER "RemoteController for Wall-E |"

#define REQUEST_CONTROL "%1 D %2 %3 |"
#define REQUEST_COMMAND "%1 |"
//#define REQUEST_CONTROL "Control Left 0.5 Right -0.5"


class QNetworkSession;
class QByteArray;
//class Command;

class FtpClient : public QObject
{
    Q_OBJECT

public:

    FtpClient(QObject* parent = 0, QString ipAddr="192.168.1.7", int p=2000);
    void sendCommand(Command command);

signals:
    void deviceStateChanged(DeviceManager::DeviceState aDeviceState);
    void deviceError(QAbstractSocket::SocketError socketError);
    void commandProsessed(Command command);

private:
    void init();
    void connectServer();
    void request(QString request);
    void handleRequests();

private slots:
    //void requestNewFortune();
    void handleError(QAbstractSocket::SocketError socketError);
    void handleSessionOpened();

    void handleConnected ();
    void handleDisconnected ();
    void handleHostFound ();
    void handleProxyAuthenticationRequired ( const QNetworkProxy & proxy, QAuthenticator * authenticator );
    void handleStateChanged ( QAbstractSocket::SocketState socketState );

    // for QIODevice
    void handleAboutToClose ();
    void handleBytesWritten ( qint64 bytes );
    void handleReadChannelFinished ();
    void handleReadyRead ();


private:
    bool mInitiated;
    bool mConnected;
    bool mConnecting;
    bool mTransferring;
    QString ipAddress;
    int port;
    QTcpSocket *tcpSocket;
    //QString currentFortune;
    quint16 blockSize;
    Command mCommand;
    Command mProsesedCommand;

    QNetworkSession *networkSession;

//    QList<QString> mRequests;
    QByteArray mOutBuffer;
    unsigned int mOutCommandNumber;
    QByteArray mInBuffer;
    unsigned int mInCommandNumber;
};
//! [0]

#endif
