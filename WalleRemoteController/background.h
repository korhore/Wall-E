#ifndef BACKGROUND_H
#define BACKGROUND_H

#include <QLabel>
#include <QPoint>

class BackGround : public QWidget
{
    Q_OBJECT
public:
    explicit BackGround(QWidget *parent = 0);


protected:
    // re-implement processing of mouse events
    void mouseReleaseEvent ( QMouseEvent * e );
    void mousePressEvent ( QMouseEvent * e );
    void mouseMoveEvent ( QMouseEvent * e );

    
public:
signals:
    // define mouseClick signal
    void mouseClickEvent(QPoint);

public slots:

private:
    // member variable to store click position
    QPoint m_lastPoint;
    // member variable - flag of click beginning
    //bool m_mouseClick;

};

#endif // BACKGROUND_H
