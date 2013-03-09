#ifndef IPNUMBERWIDGED_H
#define IPNUMBERWIDGED_H

#include <QFrame>
#include <QLineEdit>
#include <QIntValidator>
#include "stdint.h"
#include <QHBoxLayout>
#include <QFont>
#include <QLabel>
#include <QKeyEvent>


class IPNumberWidget : public QFrame // QWidget //
{
//    typedef QWidget baseClass;
    typedef QFrame baseClass;

    Q_OBJECT

public:
    IPNumberWidget(QWidget *parent, QString hostIP="", int portnumber=0);
    ~IPNumberWidget();

#define QTUTL_IP_SIZE 4

    virtual bool eventFilter( QObject *obj, QEvent *event );

public:
signals:
    void signalTextChanged( QString hostIP );

private:
signals:
    void signalTextChanged( QLineEdit* pEdit );
private slots:
    void slotTextChanged( QLineEdit* pEdit );


private:
    void handleTextChanged();

    QLineEdit *(m_pLineEdit[QTUTL_IP_SIZE]);

    static std::string getIPItemStr( unsigned char item );
};


#endif // IPNUMBERWIDGED_H
