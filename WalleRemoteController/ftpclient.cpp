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


#include <QtGui>
#include <QtNetwork>
#include <QByteArray>
#include <QDebug>
#include "ftpclient.h"
#include "command.h"
#include "devicemanager.h"



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
    qDebug() << "FtpClient:: " << port << " Init";
    // if we did not find one, use IPv4 localhost
    if (ipAddress.isEmpty())
        ipAddress = QHostAddress(QHostAddress::LocalHost).toString();

    qDebug() << "FtpClient:: " << port << " Init connect";
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


    qDebug() << "FtpClient:: " << port << " Init NetworkConfigurationManager manager";
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

        qDebug() << "FtpClient:: " << port << " Init new QNetworkSession(config, this)";
        networkSession = new QNetworkSession(config, this);
        qDebug() << "FtpClient:: " << port << " Init connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()))";
        connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()));

        qDebug() << "FtpClient:: " << port << " Init networkSession->open()";
        networkSession->open();
    } else {
        qDebug() << "FtpClient:: Init " << port << " tcpSocket->connectToHost())" << " ipAddress " << ipAddress << " port " << port;
        tcpSocket->connectToHost(QHostAddress(ipAddress),  port);
    }

    mInitiated = true;
}

void FtpClient::connectServer()
{
    qDebug() << "FtpClient:: " << port << " connectServer";
    mConnecting = true;
    // if we did not find one, use IPv4 localhost
    if (ipAddress.isEmpty())
        ipAddress = QHostAddress(QHostAddress::LocalHost).toString();

    qDebug() << "FtpClient:: " << port << " connectServer NetworkConfigurationManager manager";
    QNetworkConfigurationManager manager;
    if (manager.capabilities() & QNetworkConfigurationManager::NetworkSessionRequired) {
        qDebug() << "FtpClient:: " << port << " connectServer QNetworkConfigurationManager::NetworkSessionRequired";
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

        qDebug() << "FtpClient:: " << port << " connectServer new QNetworkSession(config, this)";
        networkSession = new QNetworkSession(config, this);
        qDebug() << "FtpClient:: " << port << " connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()))";
        connect(networkSession, SIGNAL(opened()), this, SLOT(handleSessionOpened()));

        qDebug() << "FtpClient:: " << port << " connectServer networkSession->open()";
        networkSession->open();
    } else {
        qDebug() << "FtpClient:: " << port << "connectServer tcpSocket->connectToHost())" << " ipAddress " << ipAddress << " port " << port;
        tcpSocket->connectToHost(ipAddress,  port);

    }
}



// TODO

void FtpClient::handleReadyRead()
{
    qDebug() << "FtpClient:: " << port << " handleReadyRead, available bytes" << tcpSocket->bytesAvailable();
    emit deviceStateChanged(DeviceManager::ReadingState);
    mInBuffer = tcpSocket->readAll();
    emit deviceStateChanged(DeviceManager::ReadState);

    if ((mProsesedCommand.getCommand() == Command::Picture) &&                              // if we are waiting for pisture data
            (mProsesedCommand.getImageSize() > mProsesedCommand.getImageData().size())) {  // and size of inbuffer is what we wait
        qDebug() << "FtpClient:: " << port << " handleReadyRead, reading picture data";
        mProsesedCommand.addImageData(mInBuffer);
        qDebug() << "FtpClient:: " << port << " handleReadyRead picture Command" << mProsesedCommand.toString();
        if (mProsesedCommand.getImageSize() <= mProsesedCommand.getImageData().size())
            emit commandProsessed(mProsesedCommand);

    }
    else {
        qDebug() << "FtpClient:: " << port << " handleReadyRead reading normal command: " << mInBuffer;
        mProsesedCommand = Command(mInBuffer);
        qDebug() << "FtpClient:: " << port << " handleReadyRead Command" << mProsesedCommand.toString();
        emit commandProsessed(mProsesedCommand);
    }
}

void FtpClient::handleAboutToClose()
{
    qDebug() << "FtpClient:: " << port << " handleAboutToClose";
}

void FtpClient::handleBytesWritten( qint64 bytes )
{
     qDebug() << "FtpClient:: " << port << " handleBytesWritten bytes " << bytes << "mOutBuffer.size() " << mOutBuffer.size();
    if (bytes <= mOutBuffer.size())
        mOutBuffer.remove(0,bytes);
    else
        mOutBuffer.clear();

    if (mOutBuffer.isEmpty()) {
        mTransferring = false;
        emit deviceStateChanged(DeviceManager::WrittenState);
     } else
        handleRequests();
}

void FtpClient::handleReadChannelFinished()
{
    qDebug() << "FtpClient:: " << port << " handleReadChannelFinished";
}




void FtpClient::handleError(QAbstractSocket::SocketError socketError)
{
    qDebug() << "FtpClient:: " << port << " handleError()";
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
    case QAbstractSocket::NetworkError:
        qDebug() << tr("An error occurred with the network. "
                                     "Host unreachable.");
    default:
        qDebug() << tr("The following error occurred: %1 %2.")
                                 .arg(tcpSocket->errorString(), QString::number(socketError));
    }

    // emit error
    emit deviceStateChanged(DeviceManager::ErrorState);
    emit deviceError(socketError);

}


void FtpClient::handleSessionOpened()
{
    qDebug() << "FtpClient:: " << port << " sessionOpened()";
    emit deviceStateChanged(DeviceManager::ConnectingState);
    tcpSocket->connectToHost(QHostAddress(ipAddress), port);

}

void FtpClient::handleConnected()
{
    emit deviceStateChanged(DeviceManager::ConnectedState);

    mConnected = true;
    mConnecting = false;
    mTransferring = false;
    qDebug() << "FtpClient:: " << port << " handleConnected()";
    //request(QString(REQUEST_WHO).arg(QString::number(mOutCommandNumber++)));
    // ask picture
    // Nope
    //sendCommand(Command("", -1, Command::Picture));
    //handleRequests();
}

void FtpClient::handleDisconnected()
{
    emit deviceStateChanged(DeviceManager::UnconnectedState);
    mConnected = false;
    mConnecting = false;
    qDebug() << "FtpClient:: " << port << " handleDisconnected";
};

void FtpClient::handleHostFound()
{
    qDebug() << "FtpClient:: " << port << " handleHostFound";
    emit deviceStateChanged(DeviceManager::ErrorState);
    emit deviceError(QAbstractSocket::HostNotFoundError);
};

void FtpClient::handleProxyAuthenticationRequired ( const QNetworkProxy & proxy, QAuthenticator * authenticator )
{
    qDebug() << "FtpClient:: " << port << " handleProxyAuthenticationRequired";
    emit deviceStateChanged(DeviceManager::ErrorState);
    emit deviceError(QAbstractSocket::ProxyAuthenticationRequiredError);
};

void FtpClient::handleStateChanged ( QAbstractSocket::SocketState socketState )
{
    qDebug() << "FtpClient:: " << port << " handleStateChanged";
    switch (socketState) {
    case QAbstractSocket::UnconnectedState:
        qDebug() << tr("UnconnectedState: The socket is not connected.");
        emit deviceStateChanged(DeviceManager::UnconnectedState);
        break;
    case QAbstractSocket::HostLookupState:
        qDebug() << tr("HostLookupState: The socket is performing a host name lookup.");
        emit deviceStateChanged(DeviceManager::UnconnectedState);
        break;
    case QAbstractSocket::ConnectingState:
        qDebug() << tr("ConnectingState: The socket has started establishing a connection.");
        emit deviceStateChanged(DeviceManager::ConnectingState);
        break;
    case QAbstractSocket::ConnectedState:
        qDebug() << tr("ConnectedState: A connection is established.");
        emit deviceStateChanged(DeviceManager::ConnectedState);
        break;
    case QAbstractSocket::BoundState:
        qDebug() << tr("BoundState: The socket is bound to an address and port (for servers).");
        break;
    case QAbstractSocket::ClosingState:
        qDebug() << tr("ClosingState: The socket is about to close (data may still be waiting to be written).");
        emit deviceStateChanged(DeviceManager::ClosingState);
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
    qDebug() << "FtpClient:: " << port << " request " << request;
    //mRequests.append(request);

    // If we are trandferring. we must add this to outbuffer
    // but if we are not trnsferring, then we must not send older bytes
    if (mTransferring)
        mOutBuffer.append(request);
    else
        mOutBuffer= QByteArray(request.toLatin1());
    handleRequests();
}


void FtpClient::sendCommand(Command command)
{
    qDebug() << "FtpClient:: " << port << " sendCommand";
    mCommand = command;
    mCommand.setNumber(mOutCommandNumber++);
    request(QString(REQUEST_COMMAND).arg(mCommand.toString()));
}




void FtpClient::handleRequests()
{
    qDebug() << "FtpClient:: " << port << " handleRequests";

    if (!mInitiated)
        init();
    if ((!mConnected) && (!mConnecting))
        connectServer();

    if (!(mTransferring && !mOutBuffer.isEmpty()) && mInitiated && mConnected)
    {
        qDebug() << "FtpClient:: " << port << " handleRequests size" << mOutBuffer.size() << " " << mOutBuffer;
        mTransferring = true;
        emit deviceStateChanged(DeviceManager::WritingState);
        tcpSocket->write(mOutBuffer);
    }
}




