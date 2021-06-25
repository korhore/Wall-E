#Wall-E Project

##Introduction

Wall-E -project studies robots and controllers for them.

###Robot

Robot-project is newes and most ambitious.
It models human kognitive-capabilities as application ones.
####Architercture 
Architercture is planned to work in a network and to be fully congugurable,
so that Robot is biud by same kind elements- called Robots - that can be in same
computer or in another computer in the network and there can be as many Robots
in the network as you want, communicating with each other and with hunam beings also.

Sounds scifi? Yes, this project was my hobby project to implement all kind
scifi-films nightmare. Basic lines in films are individual very capable robots
or networking robots that is everywhere and controls everything and of course
tries to destroy all humans, because humans tru to destroy it. This the was at the first
beginning of Robot-scifi from the first one 1968: A Space Odyssey.

OK, Robot from this project cant destroy anyone, but can be fun ans if you take
it seriously, it can be scientifically valuable.
####Robot

Robot represents and models our senses and mucles. Robot can hear, see, movee, speak, ect.
Robot can own other Robots, so one of them is main Robot. All Robots including one logical
main Robot know their main name which is same, so main Robot can be build logically in one computer or many.
There ab be many main Robots in a network and they con communicate each other if they wan't.
Main Robots cam also share sub Robots if they wan't. Robots have always very tiny API

    def process(self, sensation)
Robot can always process sensations. Sensation gives information to a Robot what to do and Robot perform actions needen
Robot can also create new sensations given to other Robots.

    def route(self, transferDirection, sensation)
Called inside process. This routes sensation to thos Robots that are *capable* to process it.

    def sense(self)
Frameworks calls this if this is sense-type Robot, like hearing-Robot. If this is muscle type Robot
like speking Robot, this method does nothing and method canSense return False.

####Capabilities
Each Robot advitices in it capabilities what kind sensations they are interested of. If Roboty is logical
main Robot it defines its subRobots, meanic senses ns muscles sthat will bew started in tyhis computer for it.
For networking main Robot also defines computers in the networh that it connects. With capabilies same Robot-components
can be used in many kind configurations.

####Sensation
Sensation can tranfer all information about seen or heard things, what they names are etc. Sensations are transferred by axons, ame way
than humans do, but we use direct transfer from Robot to Robots, because we do so and it is more efficient way.

####Memory
Main Robot owns memory. Memory consist of Sensations connected with associations, same way than in human being.
Association has feeling element so our Root can also feel. This makes fun for pour project. Robots fall in love!
If Robots gets responses what it says, it likes more of the object and of responses it uses, so feelings guide
Robot what to do with different kind objects.

In practice remembering function needs alo forgetting function. We human beeings can remember important things only because we cam forget less
important things, human memory capacity is not limitless as previously thought and the same applies to computers and robots built with them.
This is implemented using feelings. The Robot tries to gain pleasure and forget about observations where it has not been liked.

####Exposure
Main pronsiple is not to help any kimd Robot to observe world and what are objects names and what they say etc. Nothing
is build in. But we mimic human beings so that, when main Robot starts it gets a directory where are basuv inages of itself
and basic phrases it says. Little baby startr to study itself and Robot does same.

Next thing bady does is study to world. Robot gets also directory where are images and voices of one thing Robot sees and hears first.
With humans this thing is mother. With this projects that can be anything you want Robot to react certain way. Robot tryes to speak voices it has got
and hears responses so those are associated in its memory with positive feelings.

That is all we help our robot and each run of the Robot(s) are different, depending what they see and what they hear.


####Theory of Robots

Robot implementation based on research domains including developmental psychology, cognitive neuroscience, and cognitive psycology, very popular areas
stydy with robotics.

#####Events Perception

Robot can notice events using its sensories.

#####Goal driven action

Robot has goals, it makes decisions what actions are it makes to reach its goals. Implementation uses circle of event-decision-action to
make tasks to reach goals. Some Goals are more important than others, so we implement Maslow's Hierarchy of Needs to guide robots actions,
but robot itself has higher needs, its thinks is most important.

#####Starting point of Wall-E

This comes from Wall-E film. Wall-E likes to watch people dancing and thinks it would be nice to hold
on hands with a girl robot. One day it see Eve, very graceful being, it can't set eyes off her. Here we gat most important goal of Wall-E,
hold Eve's hand. OK, we must build a robot that can find out Eve. So we must build at least hearing and seeing as a start.

#####Concept

We must have sensorys. Project implements sensory framework sor simultaneous percertons
like we human can do, Axons to corry these percetions from interbaö sensorys and from exterbal sensorys to the brain.
Framewrk is veru flexible so Wall-E xan use all suitable devices we can offers (cheap devices we allreasy have or buy).

OK Lets Start, project has already object positioning using hearing and turning using position
sensory (azimuth) to that direction. Demo will be made to youtube.
Next target will be object recognize using seeing.




###WalleRobotoController

WalleRobotoController is a legacy projecticluding same basic elements as
Robots-projects has, but it is more contrete. It works with robots car run
by arduino, Car can be controller by a mobile device. Anorher one is put
in the cat. Controil-mobile and device-mobile are connected by wlan and
device-mobile in connectoted to arduini by usb.

It is based on Adruino Pirate 4WD car, which carries Raprberry-PI to control it.
Remote controller is mobile phone like Android one or Maemo one or E7 ...
All parts are cheap and we use everything we already own.

All devices are programmed with their own native programming language.

####Arduino Pirate 4WD car

Role as Robot device, its "muscles"

This device is run by Romeo. Romeo is microcontroller and runs programs that are originally
written in C, compiled in host computer and uploaded by USB to the device. On this project we want
control Arduino by Raspberry PI computer, which native programming language is Python, so we load
pyfirmata sketch 1) to it.

####Raspberry PI

Role as Robot logic, it's "brains".

Raspberry PI computer is very small and very cheap. But is real computer running Linux.
We connect Raspberry PI and Arduino Romeo board by USB and set up Python server listening command
that come from WLAN from remote controller. We need a cheap WLAN USB-stick.
Python has fine libraries to read WLAN connections and handle serial line devices
that Romeo is seen in USB connection. Raspberry PI has two USB connection and we use them both, but we don't need
USB-HUB.

Raspberry PI carries also some integrated capabilities. We have two usb-microphones connected in 180 degrees angle,
so we have implemented position hearing, capability to know in what angle sound comes. We have learned Wall-E to turn to that direction.
It is very interested of it'sd environment, hoping to meet and see Eva, hoping to hold her hand one day (I haven't duid hands to Wall-E yet
but please don't tell that to Wall-E, maybe one day he has hands.)

Raspberry PI also has it's official camera, so we can see in remote controller what Wall-E sees.
Later we can use camera to recognize objects.


####N900

Role as remote controller

N900 is Maemo mobile phone which runs Linux. It's native programming language is Qt C++, which is ideal to make
applications with graphical UI and WLAN-client. We study fancy logics how to control devices, so this as fine
platform to make them.


####E7 or other Qt Phone
--------------------

Role as remote controller

####E7 is mobile phone which runs Qt above Symbian. It runs same source code as N900 does.


####Android Phone

Role as external Senses or remote controller

Android phone has many sensors we can use. Now position sense is ready.
Wall-E carries Android cheap and little phone, which t tells what is device's angle from north (azimuth).
This capability is needed to turn Wall-E toward the sounds it hears.

Android Phone's role can also same than N900, we can use it as remote controller. Android is programmed by Java and it has fine graphic libraries
and it can use WLAN connections. Unfortunately remote controller is not programmed for Android yet.

