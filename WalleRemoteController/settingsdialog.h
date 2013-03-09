#ifndef SETTINGSDIALOG_H
#define SETTINGSDIALOG_H

#include <QDialog>
class IPNumberWidget;
class QLineEdit;

class SettingsDialog : public QDialog
{
    Q_OBJECT
public:
    explicit SettingsDialog(QWidget *parent, QString hostIP="", int port=0);
    
signals:
    
public slots:

private slots:
    void hostIPChanged(QString hostIP);
    void portChanged(const QString port);

private:
    IPNumberWidget* mIPNumberWidget;
    QLineEdit* mPortNumber;
    
};

#endif // SETTINGSDIALOG_H
