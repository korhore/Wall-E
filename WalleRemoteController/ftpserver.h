
#ifndef FTPSERVER_H
#define FTPSERVER_H

#include <QStringList>
#include <QTcpServer>

//! [0]
class FtpServer : public QTcpServer
{
    Q_OBJECT

public:
    FtpServer(QObject *parent = 0);

protected:
    void incomingConnection(int socketDescriptor);

private:
    QStringList fortunes;
};
//! [0]

#endif
