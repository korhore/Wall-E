
#ifndef FTPCLIENT_H
#define FTPCLIENT_H

#include <QObject>
#include <QTcpSocket>
#include <QList>
#include <QString>
#include "command.h"



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
    FtpClient(QObject* parent = 0, QString ipAddr="localhost", int p=2000);
//    void request(QString request);
    //void command(bool aRunning, double aLeftPower, double aRightPower);
    void sendCommand(Command command);

signals:
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
