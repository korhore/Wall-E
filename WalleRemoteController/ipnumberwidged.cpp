#include "ipnumberwidged.h"
#include <sstream>
#include <QDebug>

class IPItemValidator : public QIntValidator
{
public:
    IPItemValidator( QObject* parent) : QIntValidator( parent )
    {
        setRange( 0, UCHAR_MAX );
    }
    ~IPItemValidator() {}

    virtual void fixup( QString & input ) const
    {
        if ( input.isEmpty() )
            input = "0";
    }
};

IPNumberWidget::IPNumberWidget(QWidget *parent, QString hostIP/*=""*/, int /*ipnumber=0*/)
    :baseClass(parent)
{
    QList<QString> IPFragments = hostIP.split('.');
    setFrameShape( QFrame::StyledPanel );
    setFrameShadow( QFrame::Sunken );
    setMinimumWidth(300);

    QHBoxLayout* pLayout = new QHBoxLayout( this );
    setLayout( pLayout );
    pLayout->setContentsMargins( 0, 0, 0, 0 );
    pLayout->setSpacing( 0 );

    for ( int i = 0; i != QTUTL_IP_SIZE; ++i )
    {
        if ( i != 0 )
        {
            QLabel* pDot = new QLabel( ".", this );
            pDot->setStyleSheet( "background: white" );
            pLayout->addWidget( pDot );
            pLayout->setStretch( pLayout->count(), 0 );
        }

        m_pLineEdit[i] = new QLineEdit( this );
        QLineEdit* pEdit = m_pLineEdit[i];
        pEdit->installEventFilter( this );
        if (IPFragments.count() > i)
            pEdit->setText(IPFragments[i]);
        //pEdit->setMinimumSize(100,50);
        //pEdit->setBaseSize(100,50);

        pLayout->addWidget( pEdit, 100 );
        //pLayout->setStretch( pLayout->count(), 1 );


        pEdit->setFrame( false );
        pEdit->setAlignment( Qt::AlignCenter );

        QFont font = pEdit->font();
        font.setStyleHint( QFont::Monospace );
        font.setFixedPitch( true );
        pEdit->setFont( font );

        pEdit->setValidator( new IPItemValidator( pEdit ) );
    }

    setMaximumWidth( 30 * QTUTL_IP_SIZE );

    connect( this, SIGNAL(signalTextChanged(QLineEdit*)),
             this, SLOT(slotTextChanged(QLineEdit*)),
             Qt::QueuedConnection );
}

IPNumberWidget::~IPNumberWidget()
{

}

std::string IPNumberWidget::getIPItemStr( unsigned char item )
{
    std::stringstream str;
    str << (int) item;
    str << std::ends;
    return str.str();
}

void IPNumberWidget::slotTextChanged( QLineEdit* pEdit )
{
    qDebug()<<"IPNumberWidget::slotTextChanged " << pEdit->text();
    for ( unsigned int i = 0; i != QTUTL_IP_SIZE; ++i )
    {
        if ( pEdit == m_pLineEdit[i] )
        {
            if ( pEdit->text().size() == getIPItemStr( UCHAR_MAX ).size() &&
                 pEdit->text().size() == pEdit->cursorPosition() )
            {
                // auto-move to next item
                if ( i+1 != QTUTL_IP_SIZE )
                {
                   m_pLineEdit[i+1]->setFocus();
                   m_pLineEdit[i+1]->selectAll();
                }
            }
        }
    }

    handleTextChanged();
}

void IPNumberWidget::handleTextChanged()
{
    QString IPNumber;
    for ( int i = 0; i != QTUTL_IP_SIZE; ++i )
    {
        if (i != 0)
            IPNumber += '.';
        IPNumber += m_pLineEdit[i]->text();
    }

    emit signalTextChanged(IPNumber);
}


bool IPNumberWidget::eventFilter(QObject *obj, QEvent *event)
{
    bool bRes = baseClass::eventFilter(obj, event);

    if ( event->type() == QEvent::KeyPress )
    {
        QKeyEvent* pEvent = dynamic_cast<QKeyEvent*>( event );
        if ( pEvent )
        {
            for ( unsigned int i = 0; i != QTUTL_IP_SIZE; ++i )
            {
                QLineEdit* pEdit = m_pLineEdit[i];
                if ( pEdit == obj )
                {
                    switch ( pEvent->key() )
                    {
                    case Qt::Key_Left:
                        {
                            if ( pEdit->cursorPosition() == 0 )
                            {
                                // user wants to move to previous item
                                if ( i != 0 )
                                {
                                    m_pLineEdit[i-1]->setFocus();
                                    m_pLineEdit[i-1]->setCursorPosition( m_pLineEdit[i-1]->text().size() );
                                }
                            }
                            break;
                        }
                    case Qt::Key_Right:
                        {
                            if ( pEdit->text().isEmpty() ||
                                 (pEdit->text().size() == pEdit->cursorPosition()) )
                            {
                                // user wants to move to next item
                                if ( i+1 != QTUTL_IP_SIZE )
                                {
                                    m_pLineEdit[i+1]->setFocus();
                                    m_pLineEdit[i+1]->setCursorPosition( 0 );
                                }
                            }
                            break;
                        }
                    default:
                        {
                            emit signalTextChanged( pEdit );
                        }
                    }

                    break;
                }
            }
        }
    }

    return bRes;
}
