#ifndef THERMOTUNERFRAME_H
#define THERMOTUNERFRAME_H

#include <QFrame>
#include "tunerframe.h"

class QwtThermo;

class ThermoTunerFrame : public TunerFrame
{
    Q_OBJECT
public:
    ThermoTunerFrame( QWidget *p=NULL );

Q_SIGNALS:
    void directionChanged( double speed );
    void speedChanged( double speed );

public Q_SLOTS:
    virtual void setDirection( double direction );
    virtual void setSpeed( double speed );
    void setpower( bool running, double leftPower, double rightPower );


private Q_SLOTS:
    void handleDirectionChange( double direction );
    void handleSpeedChange( double speed );


private:
    QwtThermo *mLeftThermoUp;
    QwtThermo *mLeftThermoDown;
    QwtThermo *mRightThermoUp;
    QwtThermo *mRightThermoDown;

    bool mRunning;
    double mLeftPower;
    double mRrightPower;
};

#endif // THERMOTUNERFRAME_H




