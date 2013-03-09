#ifndef POWERTUNERFRAME_H
#define POWERTUNERFRAME_H

#include <QFrame>
#include "command.h"

class QwtThermo;
class QwtSlider;

class PowerTunerFrame : public QFrame
{
    Q_OBJECT
public:
    PowerTunerFrame( QWidget *p=NULL );

signals:
    void powerChanged( double leftPower, double rightPower );

public Q_SLOTS:
    //void setpower( bool running, double leftPower, double rightPower );
    void setCommand(Command command);

private Q_SLOTS:
    void handleSettings();
    void handleLeftPowerChange( double leftPower );
    void handleRightPowerChange( double rightPower );


private:
/*    QwtThermo *mLeftThermoUp;
    QwtThermo *mLeftThermoDown;
    QwtThermo *mRightThermoUp;
    QwtThermo *mRightThermoDown;
*/
    QwtSlider *mLeftPowerSlider;
    QwtSlider *mRightPowerSlider;

    bool mRunning;
    double mLeftPower;
    double mRightPower;
};

#endif // POWERTUNERFRAME_H




