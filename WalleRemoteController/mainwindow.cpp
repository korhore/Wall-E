#include "mainwindow.h"
#include "qwt_slider.h"
#include "qwt_compass.h"
//#include "qwt_compass_rose.h"
#include "qwt_wheel.h"
#include "pointertunerframe.h"
#include "slidertunerframe.h"
#include "powertunerframe.h"
#include "tunermanager.h"
#include <QDebug>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <math.h>


#include <QtCore/QCoreApplication>

#define PI 3.14159265

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
      //mOriginalWallePixmap(NULL),
      //mMatrix()
{



    setWindowTitle(tr("Walle Remote Controller"));
    QWidget* background = new QWidget(this);
    setCentralWidget(background);
/*
    mBackGround = new BackGround(this);
    //mBackGround ->setText("Walle Go Go!");
    mBackGround ->setAutoFillBackground(true);
    mBackGround->setStyleSheet("QLabel { background-color : gray; color : blue; }");
    setCentralWidget(mBackGround);
    //mBackGroundWidthPer2 = mBackGround->width()/2;
    mBackGroundWidthPer2 = width()/2;
    qDebug() << "mBackGroundWidthPer2 " << mBackGroundWidthPer2;
    //mBackGroundHightPer2 = mBackGround->height()/2;
    mBackGroundHightPer2 = height()/2;
    qDebug() << "mBackGroundHightPer2 " << mBackGroundHightPer2;

    mMainLayout = new QHBoxLayout(mBackGround);
    mBackGround->setLayout(mMainLayout);
    */
    mMainLayout = new QHBoxLayout(background);
    //setLayout(mMainLayout);



    /*
    mOriginalWallePixmap = new QPixmap(":/pictures/pirate-200x200.png");


    mControlledWallePicture = new QLabel(mBackGround);
    mControlledWallePicture->setPixmap(*mOriginalWallePixmap);
//    mControlledWallePicture->setPixmap(QPixmap(":/pictures/pirate-300x300.png"));
    //mControlledWallePictureWidthPer2 = mControlledWallePicture->width()/2;
    mControlledWallePictureWidthPer2 = 150;
    qDebug() << "mControlledWallePictureWidthPer2 " << mControlledWallePictureWidthPer2;
    //mControlledWallePictureHightPer2 = mControlledWallePicture->height()/2;
    mControlledWallePictureHightPer2 = 150;
    qDebug() << "mControlledWallePictureHightPer2 " << mControlledWallePictureHightPer2;

    //mControlledWallePicture->move(mBackGroundWidthPer2-mControlledWallePictureWidthPer2,mBackGroundHightPer2-mControlledWallePictureHightPer2);
    mMainLayout->addWidget(mControlledWallePicture, 350, Qt::AlignCenter);
*/

    mPointerTunerFrame = new PointerTunerFrame( background );
    mPointerTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    mMainLayout->addWidget(mPointerTunerFrame, 200 /*Qt::AlignCenter*/);
//    mMainLayout->addWidget(mPointerTunerFrame/*, 300 /*Qt::AlignCenter*/);
    // Test
    //mMainLayout->addWidget(new QLabel("Test",this) /*350, Qt::AlignCenter*/);

    mSliderTunerFrame = new SliderTunerFrame(background);
    mSliderTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
//    mMainLayout->addWidget(mSliderTunerFrame, 400 /*Qt::AlignCenter*/);
    mMainLayout->addWidget(mSliderTunerFrame/*, 400 /*Qt::AlignCenter*/);
    //connect( mSliderTunerFrame, SIGNAL( fieldChanged( double ) ),
    //    this, SLOT( setMaster( double ) ) );

    mSliderTunerFrame->setDirection( 0.0 );
    mSliderTunerFrame->setSpeed( 1.0 );
    mPointerTunerFrame->setDirection( 0.0 );
    mPointerTunerFrame->setSpeed( 1.0 );

    /**/
    mPowerTunerFrame = new PowerTunerFrame(background);
    mPowerTunerFrame->setFrameStyle( QFrame::Panel | QFrame::Raised );
    //mPowerTunerFrame->setpower(true,-1.0, 0.0 );
    mMainLayout->addWidget(mPowerTunerFrame);
/**/

    qDebug() << "mainwindow.setPalette";
    setPalette( QPalette( QColor( 192, 192, 192 ) ) );



    /*
mTargetPicture = new QLabel(mBackGround);
    mTargetPicture->setPixmap(QPixmap(":/pictures/target.png"));
//    mTargetPictureWidthPer2 = mTargetPicture->width()/2;
    mTargetPictureWidthPer2 = 15;
    qDebug() << "mTargetPictureWidthPer2 " << mTargetPictureWidthPer2;
//    mTargetPictureHightPer2 = mTargetPicture->height()/2;
    mTargetPictureHightPer2 = 15;
    qDebug() << "mTargetPictureHightPer2 " << mTargetPictureHightPer2;
    mTargetPicture->move(mBackGroundWidthPer2-mTargetPictureWidthPer2,0);
*/

 /*
   // Try our slider
    //mVBox = new QVBoxLayout();
    //mControllerBackground = new QLabel(mBackGround);
    //mControllerBackground->setLayout(mVBox);
    //mVBox->addWidget(mControllerBackground);
//    mDirectionSlider = new QwtSlider(mBackGround, Qt::Vertical);
    mDirectionSlider = new QwtSlider(this, Qt::Vertical);
    mDirectionSlider->setRange(-180.0, 180.0);
    mDirectionSlider->setBaseSize(50,300);
    mDirectionSlider->setValue(50.0);
    mVBox->addWidget(mDirectionSlider, 0, Qt::AlignCenter);


    mSpeedSlider = new QwtSlider(this, Qt::Horizontal);
    mSpeedSlider->setRange(0.0, 100.0);
    mSpeedSlider->setBaseSize(300,50);
    mSpeedSlider->setValue(50.0);
    mVBox->addWidget(mSpeedSlider, 50, Qt::AlignCenter);

/*
    // Try our compass
//    mQwtCompass = new QwtCompass(mBackGround);
    mQwtCompass = new QwtCompass(this);
    mQwtCompass->setRange(-180.0, 180.0);
    mQwtCompass->setValue(0.0);
    //mQwtCompass->setRose(new QwtCompassRose(mQwtCompass));
    mVBox->addWidget(mQwtCompass, 0, Qt::AlignCenter);

//    mQwtWheel = new QwtWheel(mBackGround);
    mQwtWheel = new QwtWheel(this);
    mQwtWheel->setWheelWidth(300);
    mQwtWheel->setRange(-180.0, 180.0);
    mQwtWheel->setValue(0.0);
    //mQwtCompass->setRose(new QwtCompassRose(mQwtCompass));
    mVBox->addWidget(mQwtWheel, 50, Qt::AlignCenter);
*/


    //        self.controlledWallePicture=QtGui.QLabel(self.picture)
    //        self.controlledWallePicture.setPixmap(self.mOriginalWallePixmap)

    // Test
    /*
    mControlledWallePicture = new QLabel(mBackGround);
    mControlledWallePicture->setPixmap(QPixmap(":/pictures/pirate-300x300.png"));
    mControlledWallePicture->move(100,50);
    */

    // Test
    /*
    mMatrix.rotate(45);
    QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(mMatrix);
    mControlledWallePicture->setPixmap(rotatedControlledPixmap);
    */

    // Test AUTS, N900 does not have compass
    /*
    mCompass= new QCompass(this);
    // start the sensor
    if (!mCompass->isActive())
        mCompass->start();

    if (!mCompass->isActive())
    {
        qDebug() << "Compas Sensor didn't start!" << endl;
    }
    */

    mTunerManager = new  TunerManager(this);

    //connect(mBackGround,SIGNAL(mouseClickEvent(QPoint)),this,SLOT(setTarget(QPoint)));
    qDebug() << "mainwindow.connect(mPointerTunerFrame,directionChanged";
    connect(mPointerTunerFrame,SIGNAL(directionChanged(double)),mSliderTunerFrame,SLOT(setDirection(double)));
    qDebug() << "mainwindow.connect(mPointerTunerFrame,speedChanged";
    connect(mPointerTunerFrame,SIGNAL(speedChanged(double)),mSliderTunerFrame,SLOT(setSpeed(double)));

    qDebug() << "mainwindow.connect(mTunerManager,directionChanged";
    connect(mPointerTunerFrame,SIGNAL(directionChanged(double)),mTunerManager,SLOT(setDirection(double)));
    qDebug() << "mainwindow.connect(mTunerManagere,speedChanged";
    connect(mPointerTunerFrame,SIGNAL(speedChanged(double)),mTunerManager,SLOT(setSpeed(double)));

    qDebug() << "mainwindow.connectmPowerTunerFrame,powerChanged";
    connect(mPowerTunerFrame,SIGNAL(powerChanged(double,double)),mTunerManager,SLOT(setPower(double,double)));

    qDebug() << "mainwindow.connect(mSliderTunerFrame,directionChanged";
    connect(mSliderTunerFrame,SIGNAL(directionChanged(double)),mPointerTunerFrame,SLOT(setDirection(double)));
    qDebug() << "mainwindow.connect(mSliderTunerFrame,speedChanged";
    connect(mSliderTunerFrame,SIGNAL(speedChanged(double)),mPointerTunerFrame,SLOT(setSpeed(double)));

    qDebug() << "mainwindow.connect(,mTunerManager,powerChanged";
    //connect(mTunerManager,SIGNAL(powerChanged(bool,double,double)),mPowerTunerFrame,SLOT(setpower(bool,double,double)));
    connect(mTunerManager, SIGNAL(commandProsessed(Command)), mPowerTunerFrame, SLOT(setCommand(Command)));

    qDebug() << "mainwindow end";
}

MainWindow::~MainWindow()
{
    //delete mOriginalWallePixmap;
    //mOriginalWallePixmap = NULL;
}

void MainWindow::setOrientation(ScreenOrientation orientation)
{
#if defined(Q_OS_SYMBIAN)
    // If the version of Qt on the device is < 4.7.2, that attribute won't work
    if (orientation != ScreenOrientationAuto) {
        const QStringList v = QString::fromAscii(qVersion()).split(QLatin1Char('.'));
        if (v.count() == 3 && (v.at(0).toInt() << 16 | v.at(1).toInt() << 8 | v.at(2).toInt()) < 0x040702) {
            qWarning("Screen orientation locking only supported with Qt 4.7.2 and above");
            return;
        }
    }
#endif // Q_OS_SYMBIAN

    Qt::WidgetAttribute attribute;
    switch (orientation) {
#if QT_VERSION < 0x040702
    // Qt < 4.7.2 does not yet have the Qt::WA_*Orientation attributes
    case ScreenOrientationLockPortrait:
        attribute = static_cast<Qt::WidgetAttribute>(128);
        break;
    case ScreenOrientationLockLandscape:
        attribute = static_cast<Qt::WidgetAttribute>(129);
        break;
    default:
    case ScreenOrientationAuto:
        attribute = static_cast<Qt::WidgetAttribute>(130);
        break;
#else // QT_VERSION < 0x040702
    case ScreenOrientationLockPortrait:
        attribute = Qt::WA_LockPortraitOrientation;
        break;
    case ScreenOrientationLockLandscape:
        attribute = Qt::WA_LockLandscapeOrientation;
        break;
    default:
    case ScreenOrientationAuto:
        attribute = Qt::WA_AutoOrientation;
        break;
#endif // QT_VERSION < 0x040702
    };
    setAttribute(attribute, true);
}

void MainWindow::showExpanded()
{
#if defined(Q_OS_SYMBIAN) || defined(Q_WS_SIMULATOR)
    showFullScreen();
#elif defined(Q_WS_MAEMO_5)
    showMaximized();
#else
    show();
#endif
}
/*
void MainWindow::setTarget(QPoint p)
{
    mTargetPicture->move(p.x()-mTargetPictureWidthPer2,p.y()-mTargetPictureHightPer2);


    int x = p.x() - mBackGroundWidthPer2;
    int y = p.y() - mBackGroundHightPer2;
    if (false //x == 0**) {
        mControlledWallePicture->setPixmap(*mOriginalWallePixmap);
    } else {
        QMatrix matrix;
        double value = atan2 (x,-y) * 180.0 / PI;
        qDebug() << "MainWindow::setTarget " << value;

        matrix.rotate(value);
        QPixmap rotatedControlledPixmap = mOriginalWallePixmap->transformed(matrix);
        mControlledWallePicture->setPixmap(rotatedControlledPixmap);

        //mDirectionSlider->setValue(value);
        //mQwtCompass->setValue(value);
        //mQwtWheel->setValue(value);

        // TODO Speed
        //mSpeedSlider->setValue(value);

        mSliderTunerFrame->setDirection( value );
        mSliderTunerFrame->setSpeed( 100.0 * sqrt((x*x) + (y*y))/mBackGroundWidthPer2 );
    }

}
*/
