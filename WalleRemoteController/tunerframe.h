#ifndef TUNERFRAME_H
#define TUNERFRAME_H

#include <QFrame>

class QwtWheel;
class QwtSlider;
class TuningThermo;

class TunerFrame : public QFrame
{
    Q_OBJECT
public:
    TunerFrame( QWidget *p );

Q_SIGNALS:
    void directionChanged( double direction );
    void speedChanged( double speed );

public Q_SLOTS:
    virtual void setDirection( double direction ) = 0;
    virtual void setSpeed( double speed ) = 0;
};

#endif // TUNERFRAME_H





