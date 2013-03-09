/*
#include <qlayout.h>
#include <qlabel.h>
#include <qwt_wheel.h>
#include <qwt_slider.h>
#include <qwt_thermo.h>
#include <qwt_math.h>
*/
#include "tunerframe.h"

#if QT_VERSION < 0x040600
#define qFastSin(x) ::sin(x)
#define qFastCos(x) ::cos(x)
#endif


TunerFrame::TunerFrame( QWidget *parent ):
    QFrame( parent )
{
}

/*
void TunerFrame::handleDirectionChange( double direction )
{
    qDebug() << "handleDirectionChange";
    Q_EMIT directionChanged(direction) ;
}

void TunerFrame::handleSpeedChange( double speed )
{
    qDebug() << "handleSpeedChange";
    Q_EMIT speedChanged(speed) ;
}
*/
