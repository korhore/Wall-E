#ifndef SLIDERTUNERFRAME_H
#define SLIDERTUNERFRAME_H

#include <QFrame>
#include "tunerframe.h"

class QwtSlider;

class SliderTunerFrame : public TunerFrame
{
    Q_OBJECT
public:
    SliderTunerFrame( QWidget *p=NULL );

Q_SIGNALS:
    void directionChanged( double speed );
    void speedChanged( double speed );

public Q_SLOTS:
    virtual void setDirection( double direction );
    virtual void setSpeed( double speed );

private Q_SLOTS:
    void handleDirectionChange( double direction );
    void handleSpeedChange( double speed );


private:
    QwtSlider *mSliderDirection;
    QwtSlider *mSliderSpeed;
};

#endif // SLIDERTUNERFRAME_H




