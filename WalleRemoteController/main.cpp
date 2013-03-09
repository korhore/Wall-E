#include "mainwindow.h"

#include <QtGui/QApplication>
#include <QDebug>
#include "command.h"

int main(int argc, char *argv[])
{
    qDebug() << Command("12 D 0.97 0.56").toString();
    qDebug() << Command("13 S").toString();
    qDebug() << Command("13 W").toString();
    qDebug() << Command("18 oho").toString();
    qDebug() << Command("hupsis oli").toString();
    qDebug() << Command("", 99, Command::Drive,  0.77, 0.55).toString();
    qDebug() << Command(Command("", 99, Command::Drive,  0.77, 0.55).toString()).toString();

    QApplication app(argc, argv);

    MainWindow mainWindow;
    qDebug() << "main mainWindow.setOrientation";
    mainWindow.setOrientation(MainWindow::ScreenOrientationLockLandscape);
    qDebug() << "main mainWindow.showExpanded()";
    //mainWindow.showExpanded();
    mainWindow.show();

    qDebug() << "main app.exec()";
    return app.exec();
}
