
#ifndef FTPSERVERTHREAD_H
#define FTPSERVERTHREAD_H

#include <QThread>
#include <QTcpSocket>

//! [0]
class FtpServerThread : public QThread
{
    Q_OBJECT

public:
    FtpServerThread(int socketDescriptor, const QString &fortune, QObject *parent);

    void run();

signals:
    void error(QTcpSocket::SocketError socketError);

private:
    int socketDescriptor;
    QString text;
};
//! [0]

#endif
