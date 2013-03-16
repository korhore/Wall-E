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


#include <QtGui>
#include <QtNetwork>
#include <QByteArray>
#include <QDebug>
#include "ftpclient.h"
#include "command.h"



FtpClient::FtpClient(QObject *parent, QString ipAddr, int p)
:   QObject(parent),
    ipAddress(ipAddr),
    port(p),
    networkSession(0),
    mInitiated(false),
    mConnected(false),
    mTransferring(false),
    mOutCommandNumber(0),
    mInCommandNumber(0)
{
    qDebug() << "FtpClient::FtpClient";

    qDebug() << "FtpClient::FtpClient QTcpSocket(this)";
    tcpSocket = new QTcpSocket(this);

}

void FtpClient::init()
{
    qDebug() << "FtpClient::Init";
    // if we did not find one, use IPv4 localhost
    if (ipAddress.isEmpty())
        ipAddress = QHostAddress(QHostAddress::LocalHost).toString();

    qDebug() << "FtpClient::Init connect";
    // from abtractsocket
    connect(tcpSocket, SIGNAL(error(QAbstractSocket::SocketError)),
            this, SLOT(handleError(QAbstractSocket::SocketError)));
    connect(tcpSocket, SIGNAL(connected()), this, SLOT(handleConnected()));
    connect(tcpSocket, SIGNAL(disconnected()), this, SLOT(handleDisconnected()));
    connect(tcpSocket, SIGNAL(hostFound()), this, SLOT(handleHostFound()));
    connect(tcpSocket, SIGNAL(proxyAuthenticationRequired(const QNetworkProxy&,QAuthenticator*)), this, SLOT(handleProxyAuthenticationRequired(const QNetworkProxy&,QAuthenticator*)));
    connect(tcpSocket, SIGNAL(stateChanged(QAbstractSocket::SocketState)), this, SLOT(handleStateChanged(QAbstractSocket::SocketState)));
    // from QIODevice
    connect(tcpSocket, SIGNAL(aboutToClose()), this, SLOT(handleAboutToClose()));
    connect(tcpSocket, SIGNAL(bytesWritten(qint64)), this, SLOT(handleBytesWritten(qint64)));
    connect(tcpSocket, SIGNAL(readChannelFinished()), this, SLOT(handleReadChannelFinished()));
    connect(tcpSocket, SIGNAL(readyRead()), this, SLOT(handleReadyRead()));


    qDebug() << "FtpClient::Init NetworkConfigurationManager manager";
    QNetworkConfigurationManager manager;
    if (manager.capabilities() & QNetworkConfigurationManager::NetworkSessionRequired) {
        qDebug() << "FtpClient::Init QNetworkConfigurationManager::NetworkSessionRequired";
        // Get saved network configuration
        QSettings settings(QSettings::UserScope, QLatin1String("Wall-E"));
        settings.beginGroup(QLatin1String("QtNetwork"));
        const QString id = settings.value(QLatin1String("DefaultNetworkConfiguration")).toString();
        settings.endGroup();

        // If the saved network configuration is not currently discovered use the system default
        QNetworkConfiguration config = manager.configurationFromIdentifier(id);
        if ((config.state() & QNetworkConfiguration::Discovered) !=
            QNetworkConfiguration::Discovered) {
            config = manager.defaultConfiguration();
        }

        qDebug() << "FtpClient::Init new QNetworkSession(config, this)";
        networkSession = new QNetworkSession(config, this);
        qDebug() << "FtpClient::Init connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()))";
        connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()));

        qDebug() << "FtpClient::Init networkSession->open()";
        networkSession->open();
    } else {
        qDebug() << "tcpSocket->connectToHost())" << " ipAddress " << ipAddress << " port " << port;
        tcpSocket->connectToHost(QHostAddress(ipAddress),  port);

 /*       qDebug() << "FtpClient::Init new QNetworkSession()";
        networkSession = new QNetworkSession();
        qDebug() << "FtpClient::Init connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()))";
        connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()));

        qDebug() << "FtpClient::Init networkSession->open()";
        networkSession->open();
        */
    }

    mInitiated = true;
}

void FtpClient::connectServer()
{
    qDebug() << "FtpClient::connectServer";
    mConnecting = true;
    // if we did not find one, use IPv4 localhost
    if (ipAddress.isEmpty())
        ipAddress = QHostAddress(QHostAddress::LocalHost).toString();

    qDebug() << "FtpClient::connectServer NetworkConfigurationManager manager";
    QNetworkConfigurationManager manager;
    if (manager.capabilities() & QNetworkConfigurationManager::NetworkSessionRequired) {
//    if (false) {
        qDebug() << "FtpClient::Init QNetworkConfigurationManager::NetworkSessionRequired";
        // Get saved network configuration
        QSettings settings(QSettings::UserScope, QLatin1String("Wall-E"));
        settings.beginGroup(QLatin1String("QtNetwork"));
        const QString id = settings.value(QLatin1String("DefaultNetworkConfiguration")).toString();
        settings.endGroup();

        // If the saved network configuration is not currently discovered use the system default
        QNetworkConfiguration config = manager.configurationFromIdentifier(id);
        if ((config.state() & QNetworkConfiguration::Discovered) !=
            QNetworkConfiguration::Discovered) {
            config = manager.defaultConfiguration();
        }

        qDebug() << "FtpClient::connectServer new QNetworkSession(config, this)";
        networkSession = new QNetworkSession(config, this);
        qDebug() << "FtpClient::Init connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()))";
        connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()));

        qDebug() << "FtpClient::connectServer networkSession->open()";
        networkSession->open();
    } else {
        qDebug() << "FtpClient::connectServer tcpSocket->connectToHost())" << " ipAddress " << ipAddress << " port " << port;
        tcpSocket->connectToHost(ipAddress,  port);

 /*       qDebug() << "FtpClient::Init new QNetworkSession()";
        networkSession = new QNetworkSession();
        qDebug() << "FtpClient::Init connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()))";
        connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()));

        qDebug() << "FtpClient::Init networkSession->open()";
        networkSession->open();
        */
    }
}





void FtpClient::handleReadyRead()
{
    qDebug() << "FtpClient::handleReadyRead " << tcpSocket->bytesAvailable();
    mInBuffer = tcpSocket->readAll();

    qDebug() << "FtpClient::handleReadyRead " << mInBuffer;
    mProsesedCommand = Command(mInBuffer);
    qDebug() << "FtpClient::handleReadyRead Command" << mProsesedCommand.toString();
    emit commandProsessed(mProsesedCommand);
}

void FtpClient::handleAboutToClose()
{
    qDebug() << "FtpClient::handleAboutToClose";
}

void FtpClient::handleBytesWritten( qint64 bytes )
{
     qDebug() << "FtpClient::handleBytesWritten bytes " << bytes << "mOutBuffer.size() " << mOutBuffer.size();
    if (bytes <= mOutBuffer.size())
        mOutBuffer.remove(0,bytes);
    else
        mOutBuffer.clear();

    if (mOutBuffer.isEmpty())
        mTransferring = false;
    else
        handleRequests();
}

void FtpClient::handleReadChannelFinished()
{
    qDebug() << "FtpClient::handleReadChannelFinished";
}




void FtpClient::handleError(QAbstractSocket::SocketError socketError)
{
    qDebug() << "FtpClient::handleError()";
    switch (socketError) {
    case QAbstractSocket::RemoteHostClosedError:
        qDebug() << tr("RemoteHostClosedError");
        break;
    case QAbstractSocket::HostNotFoundError:
        qDebug() << tr("The host was not found. Please check the "
                                    "host name and port settings.");
        break;
    case QAbstractSocket::ConnectionRefusedError:
       qDebug() << tr("The connection was refused by the peer. "
                                    "Make sure the Wall-E server is running, "
                                    "and check that the host name and port "
                                    "settings are correct.");
        break;
    default:
        qDebug() << tr("The following error occurred: %1.")
                                 .arg(tcpSocket->errorString());
    }
}


void FtpClient::handleSessionOpened()
{
    qDebug() << "FtpClient::sessionOpened()";
    /*
    // Save the used configuration
    QNetworkConfiguration config = networkSession->configuration();
    QString id;
    if (config.type() == QNetworkConfiguration::UserChoice)
        id = networkSession->sessionProperty(QLatin1String("UserChoiceConfiguration")).toString();
    else
        id = config.identifier();

    QSettings settings(QSettings::UserScope, QLatin1String("Trolltech"));
    settings.beginGroup(QLatin1String("QtNetwork"));
    settings.setValue(QLatin1String("DefaultNetworkConfiguration"), id);
    settings.endGroup();

    statusLabel->setText(tr("This examples requires that you run the "
                            "Fortune Server example as well."));

    enableGetFortuneButton();
*/
    tcpSocket->connectToHost(QHostAddress(ipAddress), port);

}

void FtpClient::handleConnected()
{

    mConnected = true;
    mConnecting = false;
    mTransferring = false;
    qDebug() << "FtpClient::handleConnected()";
    //request(QString(REQUEST_WHO).arg(QString::number(mOutCommandNumber++)));
    handleRequests();
}

void FtpClient::handleDisconnected()
{
    mConnected = false;
    mConnecting = false;
    qDebug() << "FtpClient::handleDisconnected";
};

void FtpClient::handleHostFound()
{
    qDebug() << "FtpClient::handleHostFound";
};

void FtpClient::handleProxyAuthenticationRequired ( const QNetworkProxy & proxy, QAuthenticator * authenticator )
{
    qDebug() << "FtpClient::handleProxyAuthenticationRequired";
};

void FtpClient::handleStateChanged ( QAbstractSocket::SocketState socketState )
{
    qDebug() << "FtpClient::handleStateChanged";
    switch (socketState) {
    case QAbstractSocket::UnconnectedState:
        qDebug() << tr("UnconnectedState: The socket is not connected.");
        break;
    case QAbstractSocket::HostLookupState:
        qDebug() << tr("HostLookupState: The socket is performing a host name lookup.");
        break;
    case QAbstractSocket::ConnectingState:
        qDebug() << tr("ConnectingState: The socket has started establishing a connection.");
        break;
    case QAbstractSocket::ConnectedState:
        qDebug() << tr("ConnectedState: A connection is established.");
        break;
    case QAbstractSocket::BoundState:
        qDebug() << tr("BoundState: The socket is bound to an address and port (for servers).");
        break;
    case QAbstractSocket::ClosingState:
        qDebug() << tr("ClosingState: The socket is about to close (data may still be waiting to be written).");
        break;
    case QAbstractSocket::ListeningState:
        qDebug() << tr("ListeningState (For internal use only.)");
        break;
    default:
        qDebug() << tr("Unknown socket state");
        break;

    }
}

void FtpClient::request(QString request)
{
    qDebug() << "FtpClient::request " << request;
    //mRequests.append(request);

    // If we are trandferring. we must add this to outbuffer
    // but if we are not trnsferring, then we must not send older bytes
    if (mTransferring)
        mOutBuffer.append(request);
    else
        mOutBuffer= QByteArray(request.toLatin1());
    handleRequests();
}

/*
void FtpClient::command(bool aRunning, double aLeftPower, double aRightPower)
{
    request(QString(REQUEST_CONTROL).arg(QString::number(mOutCommandNumber++), QString::number(aLeftPower), QString::number(aRightPower)));
}
*/

void FtpClient::sendCommand(Command command)
{
    mCommand = command;
    mCommand.setNumber(mOutCommandNumber++);
    request(QString(REQUEST_COMMAND).arg(mCommand.toString()));
}




void FtpClient::handleRequests()
{
    qDebug() << "FtpClient::handleRequests";
    /*
    while ((!mRequests.isEmpty()) && mInitiated && mConnected)
    {
        QString request = mRequests.takeFirst();
        qDebug() << "FtpClient::handleRequests";
        qDebug() << "FtpClient::handleRequests " << request;
        QByteArray block;
        QDataStream out(&block, QIODevice::WriteOnly);
        out.setVersion(QDataStream::Qt_4_0);
        out << (quint16)0;
        out << request;
        out.device()->seek(0);
        out << (quint16)(block.size() - sizeof(quint16));

        qDebug() << "FtpClient::handleRequests write(block) " << block.size();
        tcpSocket->write(block);
    }
*/

    if (!mInitiated)
        init();
    if ((!mConnected) && (!mConnecting))
        connectServer();

    if (!(mTransferring && !mOutBuffer.isEmpty()) && mInitiated && mConnected)
    {
        qDebug() << "FtpClient::handleRequests size" << mOutBuffer.size() << " " << mOutBuffer;
        mTransferring = true;
        tcpSocket->write(mOutBuffer);
    }
}




