/* -------------------------------------------

    WalleRemoteContoller is an educational application to control a robot or other device using WLAN

    Copyright (C) 2013 Reijo Korhonen, reijo.korhonen@gmail.com
    All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

--------------------------------------------- */

#include "mainwindow.h"

#include <QtGui/QApplication>
#include <QDebug>
#include "tunercontroller.h"

int main(int argc, char *argv[])
{
    qDebug() << Command("12 D 0.97 0.56").toString();
    qDebug() << Command("13 S").toString();
    qDebug() << Command("13 W").toString();
    qDebug() << Command("18 oho").toString();
    qDebug() << Command("hupsis oli").toString();
    qDebug() << Command("", 99, Command::Drive,  0.77, 0.55).toString();
    qDebug() << Command(Command("", 99, Command::Drive,  0.77, 0.55).toString()).toString();
    qDebug() << Command("100 P 12205").toString();


    QApplication app(argc, argv);
                            // Use MVC-architecture
#ifdef old
    MainWindow mainWindow;  // Visual class
                            // Controller class
                            // Model class
    qDebug() << "main mainWindow.setOrientation";
    mainWindow.setOrientation(MainWindow::ScreenOrientationLockLandscape);
    qDebug() << "main mainWindow.showExpanded()";
    //mainWindow.showExpanded();
    mainWindow.show();
#endif

    // MVC architecture
    // Create only Controller and let it create its Visual and Model workers and set them up to work
    TunerController tunerController;

    qDebug() << "main app.exec()";
    return app.exec();
}
