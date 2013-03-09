#ifndef TUNERMANAGER_H
#define TUNERMANAGER_H


/*

Converrsion from one controllerr to other and power controlling output



  */

#include <QObject>
#include "command.h"
class FtpClient;

class TunerManager : public QObject
{
    Q_OBJECT
public:
    explicit TunerManager( QWidget *p );
    virtual ~TunerManager();

Q_SIGNALS:
    void directionChanged( double direction );
    void speedChanged( double speed );
 //   void powerChanged( bool running, double leftPower, double rightPower );

    void commandProsessed(Command command);


public Q_SLOTS:
    virtual void setDirection( double direction );
    virtual void setSpeed( double speed );
    void setPower( double leftPower, double rightPower );
    void setHost( QString ipAddress, int port);

private Q_SLOTS:
    void handleCommandProsessed(Command command);


    //virtual void setPoint(QPoint point);
    //virtual void setSize(QSize size);

private:
    void calculatePower();


private:
    // Slider tuner
    double mDirection;
    double mSpeed;

    // pointer tiner
    // member variable to store click position
    //QPoint mPoint;
    //QSize mSize;

    // Power
    double mLeftPower;
    double mRightPower;
    bool mRunning;      // is car moving or topped

    FtpClient* mFtpClient;
    QString ipAddress;
    int port;
    Command mLastComand;
    Command mCandidateCommand;


};

#endif // TUNERMANAGER_H





