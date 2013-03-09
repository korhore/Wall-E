#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtGui/QMainWindow>
#include <QtGui/QWidget>
#include <QtGui/QPixmap>
#include <QtGui/QLabel>
#include <QCompass> // Add Sensor Class

//#include <background.h>

class QwtSlider;
class QHBoxLayout;
class QVBoxLayout;
class QwtCompass;
class QwtWheel;
class SliderTunerFrame;
class PointerTunerFrame;
class PowerTunerFrame;
class TunerManager;

// add Qt Mobility Project Namespace
QTM_USE_NAMESPACE


class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    enum ScreenOrientation {
        ScreenOrientationLockPortrait,
        ScreenOrientationLockLandscape,
        ScreenOrientationAuto
    };

    explicit MainWindow(QWidget *parent = 0);
    virtual ~MainWindow();

    // Note that this will only have an effect on Symbian and Fremantle.
    void setOrientation(ScreenOrientation orientation);

    void showExpanded();
private slots:
 //   void setTarget(QPoint);


private:
    //BackGround* mBackGround;
    //QHBoxLayout* mHBox;
    //QLabel* mControllerBackground;
    QHBoxLayout* mMainLayout;
    //QPixmap* mOriginalWallePixmap;
    //QLabel* mControlledWallePicture;
    //QLabel* mRealWallePicture;
    //QLabel* mTargetPicture;
    //QwtSlider* mDirectionSlider;
    //QwtSlider* mSpeedSlider;
    SliderTunerFrame* mSliderTunerFrame;
    PointerTunerFrame* mPointerTunerFrame;
    PowerTunerFrame* mPowerTunerFrame;
    TunerManager* mTunerManager;
    //QwtCompass* mQwtCompass;
    //QwtWheel* mQwtWheel;
    //QMatrix mMatrix;

    //int mBackGroundWidthPer2;
    //int mBackGroundHightPer2;

    //int mControlledWallePictureWidthPer2;
    //int mControlledWallePictureHightPer2;

    //int mTargetPictureWidthPer2;
    //int mTargetPictureHightPer2;

    //QCompass* mCompass;

};

#endif // MAINWINDOW_H
