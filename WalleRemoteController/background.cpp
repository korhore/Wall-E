#include "background.h"
#include <QMouseEvent>
#include <QDebug>

BackGround::BackGround(QWidget *parent) :
    QWidget(parent)
    //m_mouseClick(false)
{
}

void BackGround::mousePressEvent ( QMouseEvent * e )
{
    qDebug() << "BackGround::mousePressEven" << endl;
    // store click position
    m_lastPoint = e->pos();
    emit mouseClickEvent(m_lastPoint);
}

void BackGround::mouseReleaseEvent ( QMouseEvent * e )
{
    qDebug() << "BackGround::mouseReleaseEvent" << endl;
    // store click position
    m_lastPoint = e->pos();
    emit mouseClickEvent(m_lastPoint);
}

void BackGround::mouseMoveEvent ( QMouseEvent * e )
{
    qDebug() << "BackGround::mouseMoveEvent" << endl;
    // store click position
    m_lastPoint = e->pos();
    emit mouseClickEvent(m_lastPoint);
}

