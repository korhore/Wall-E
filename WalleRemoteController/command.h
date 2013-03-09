#ifndef COMMAND_H
#define COMMAND_H

#include <QObject>

class Command
{
public:
    enum CommandType {Drive='D', Stop='S', Who='W', Unknown='U'};

    explicit Command(QString string="",
                     unsigned int number=-1, CommandType command = Unknown,
                     double leftPower = 0.0, double rightPower = 0.0);
    Command(const Command& other);

    QString toString();

    void setNumber(unsigned int number);
    unsigned int getNumber() const;

    void setCommand(CommandType command);
    CommandType getCommand() const;

    void setLeftPower(double leftPower);
    double getLeftPower() const;

    void setRightPower(double rightPower);
    double getRightPower() const;

    /*
      Is command enough different than other
      This is used to minimize traffic to the server.
      If other coonad is much same than other one, it is not mean to send it to the server
      */

    bool isDifferent(const Command other);

    
signals:
    
public slots:

private:
    unsigned int mNumber;
    CommandType mCommand;
    double mLeftPower;
    double mRightPower;
    
};

#endif // COMMAND_H
