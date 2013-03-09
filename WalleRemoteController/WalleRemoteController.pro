# Add files and directories to ship with the application 
# by adapting the examples below.
# file1.source = myfile
# dir1.source = mydir
DEPLOYMENTFOLDERS = # file1 dir1

symbian:TARGET.UID3 = 0xE219C740

# Smart Installer package's UID
# This UID is from the protected range 
# and therefore the package will fail to install if self-signed
# By default qmake uses the unprotected range value if unprotected UID is defined for the application
# and 0x2002CCCF value if protected UID is given to the application
#symbian:DEPLOYMENT.installer_header = 0x2002CCCF

# Allow network access on Symbian
symbian:TARGET.CAPABILITY += NetworkServices

# If your application uses the Qt Mobility libraries, uncomment
# the following lines and add the respective components to the 
# MOBILITY variable. 
# CONFIG += mobility
# MOBILITY +=

CONFIG += mobility
MOBILITY = sensors
QT     += network


## qwt lib
INCLUDEPATH += ../qwt/src

HEADERS += \
    ../qwt/src/qwt.h \
    ../qwt/src/qwt_abstract_scale_draw.h \
    ../qwt/src/qwt_interval_symbol.h \
    ../qwt/src/qwt_clipper.h \
    ../qwt/src/qwt_color_map.h \
    ../qwt/src/qwt_compat.h \
    ../qwt/src/qwt_column_symbol.h \
    ../qwt/src/qwt_interval.h \
    ../qwt/src/qwt_dyngrid_layout.h \
    ../qwt/src/qwt_global.h \
    ../qwt/src/qwt_math.h \
    ../qwt/src/qwt_magnifier.h \
    ../qwt/src/qwt_null_paintdevice.h \
    ../qwt/src/qwt_painter.h \
    ../qwt/src/qwt_panner.h \
    ../qwt/src/qwt_picker.h \
    ../qwt/src/qwt_picker_machine.h \
    ../qwt/src/qwt_point_3d.h \
    ../qwt/src/qwt_point_polar.h \
    ../qwt/src/qwt_round_scale_draw.h \
    ../qwt/src/qwt_scale_div.h \
    ../qwt/src/qwt_scale_draw.h \
    ../qwt/src/qwt_scale_engine.h \
    ../qwt/src/qwt_scale_map.h \
    ../qwt/src/qwt_spline.h \
    ../qwt/src/qwt_symbol.h \
    ../qwt/src/qwt_system_clock.h \
    ../qwt/src/qwt_text_engine.h \
    ../qwt/src/qwt_text_label.h \
    ../qwt/src/qwt_text.h \
    ipnumberwidged.h \
    settingsdialog.h \
    command.h

SOURCES += \
    ../qwt/src/qwt_abstract_scale_draw.cpp \
    ../qwt/src/qwt_interval_symbol.cpp \
    ../qwt/src/qwt_clipper.cpp \
    ../qwt/src/qwt_color_map.cpp \
    ../qwt/src/qwt_column_symbol.cpp \
    ../qwt/src/qwt_interval.cpp \
    ../qwt/src/qwt_dyngrid_layout.cpp \
    ../qwt/src/qwt_math.cpp \
    ../qwt/src/qwt_magnifier.cpp \
    ../qwt/src/qwt_panner.cpp \
    ../qwt/src/qwt_null_paintdevice.cpp \
    ../qwt/src/qwt_painter.cpp \
    ../qwt/src/qwt_picker.cpp \
    ../qwt/src/qwt_round_scale_draw.cpp \
    ../qwt/src/qwt_scale_div.cpp \
    ../qwt/src/qwt_scale_draw.cpp \
    ../qwt/src/qwt_scale_map.cpp \
    ../qwt/src/qwt_spline.cpp \
    ../qwt/src/qwt_text_engine.cpp \
    ../qwt/src/qwt_text_label.cpp \
    ../qwt/src/qwt_text.cpp \
    ../qwt/src/qwt_event_pattern.cpp \
    ../qwt/src/qwt_picker_machine.cpp \
    ../qwt/src/qwt_point_3d.cpp \
    ../qwt/src/qwt_point_polar.cpp \
    ../qwt/src/qwt_scale_engine.cpp \
    ../qwt/src/qwt_symbol.cpp \
    ../qwt/src/qwt_system_clock.cpp \
    ipnumberwidged.cpp \
    settingsdialog.cpp \
    command.cpp

## qwt widgets

    HEADERS += \
        ../qwt/src/qwt_abstract_slider.h \
        ../qwt/src/qwt_abstract_scale.h \
        ../qwt/src/qwt_arrow_button.h \
        ../qwt/src/qwt_analog_clock.h \
        ../qwt/src/qwt_compass.h \
        ../qwt/src/qwt_compass_rose.h \
        ../qwt/src/qwt_counter.h \
        ../qwt/src/qwt_dial.h \
        ../qwt/src/qwt_dial_needle.h \
        ../qwt/src/qwt_double_range.h \
        ../qwt/src/qwt_knob.h \
        ../qwt/src/qwt_slider.h \
        ../qwt/src/qwt_thermo.h \
        ../qwt/src/qwt_wheel.h

SOURCEPATH += ../qwt/src
    SOURCES += \
        ../qwt/src/qwt_abstract_slider.cpp \
        ../qwt/src/qwt_abstract_scale.cpp \
        ../qwt/src/qwt_arrow_button.cpp \
        ../qwt/src/qwt_analog_clock.cpp \
        ../qwt/src/qwt_compass.cpp \
        ../qwt/src/qwt_compass_rose.cpp \
        ../qwt/src/qwt_counter.cpp \
        ../qwt/src/qwt_dial.cpp \
        ../qwt/src/qwt_dial_needle.cpp \
        ../qwt/src/qwt_double_range.cpp \
        ../qwt/src/qwt_knob.cpp \
        ../qwt/src/qwt_slider.cpp \
        ../qwt/src/qwt_thermo.cpp \
        ../qwt/src/qwt_wheel.cpp


## application is here ######

SOURCES += main.cpp mainwindow.cpp \
    background.cpp \
    tunerframe.cpp \
    slidertunerframe.cpp \
    pointertunerframe.cpp \
    powertunerframe.cpp \
    tunermanager.cpp \
    ftpserver.cpp \
    ftpserverthread.cpp \
    ftpclient.cpp

HEADERS += mainwindow.h \
    background.h \
    tunerframe.h \
    slidertunerframe.h \
    pointertunerframe.h \
    powertunerframe.h \
    tunermanager.h \
    ftpserver.h \
    ftpserverthread.h \
    ftpclient.h

# FORMS += mainwindow.ui


# Please do not modify the following two lines. Required for deployment.
include(deployment.pri)
qtcAddDeployment()

OTHER_FILES += \
    qtc_packaging/debian_fremantle/rules \
    qtc_packaging/debian_fremantle/README \
    qtc_packaging/debian_fremantle/copyright \
    qtc_packaging/debian_fremantle/control \
    qtc_packaging/debian_fremantle/compat \
    qtc_packaging/debian_fremantle/changelog \
    pictures/pirate-600x600.png \
    pictures/target.png \
    TODO.TXT

RESOURCES += \
    resource.qrc
