#ifndef POINTERTUNERFRAME_H
#define POINTERTUNERFRAME_H

#include <QFrame>
#include "tunerframe.h"
#include "background.h"

class QwtSlider;

class PointerTunerFrame : public TunerFrame
{
    Q_OBJECT
public:
    PointerTunerFrame( QWidget *p=NULL );

protected:
    // re-implement processing of mouse events
    virtual void mouseReleaseEvent ( QMouseEvent * e );
    virtual void mousePressEvent ( QMouseEvent * e );
    virtual void mouseMoveEvent ( QMouseEvent * e );


public:
signals:
    // define mouseClick signal
    void mouseClickEvent(QPoint);


Q_SIGNALS:
    void directionChanged( double direction );
    void speedChanged( double speed );

public Q_SLOTS:
    virtual void setDirection( double direction );
    virtual void setSpeed( double speed );

private Q_SLOTS:
    void handleDirectionChange( double direction );
    void handleSpeedChange( double speed );

private slots:
    void setTarget(QPoint);



private:
    //int backGroundMiddleX();
    //int backGroundMiddleY();

    BackGround* mBackGround;
    QLabel* mControlledWallePicture;
    QLabel* mTargetPicture;
    QPixmap* mOriginalWallePixmap;
    QPixmap* mOriginalEwaPixmap;
    QPixmap* mScaledEwaPixmap;

    double mDirection;
    double mSpeed;


    int mBackGroundWidthPer2;
    int mBackGroundHightPer2;
    int mBackGroundWidth;
    int mBackGroundHight;
    int mBackGroundMiddleX;
    int mBackGroundMiddleY;

    int mControlledWallePictureSize;
    int mControlledWallePictureWidthPer2;
    int mControlledWallePictureHightPer2;

    //int mTargetPictureSize;
    //int mTargetPictureSizePer2;
    //int mTargetPictureWidthPer2;
    //int mTargetPictureHightPer2;

    // member variable to store click position
    QPoint m_lastPoint;


};

#endif //POINTERTUNERFRAME_H




