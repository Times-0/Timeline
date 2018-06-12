# Timeline
AS2 & AS3 CPPS Emulator, written in Python.
Timeline is built heavily on Twisted and is even-driven, most of the methods are Deferred too!

## AS2 and AS3 Cross-Compatibility
**The flexibility of Timeline, makes sure it's cross-compatible with both AS2 and AS3 clients.** 

From the version 6 of Timeline, Timeline can run both AS2 and AS3 Servers at once. One solution for multiple problems. AS2 is integrated into the AS3 Piece of pie, with some tweaks and added extra flavors. *No loss of performance, experience, and stability has been made during this compatibility upgrade. It indeed works better than ever before*. Timeline v6 is ready for production too.

*For convenience, here, we refer both Timeline AS2 and AS3 as Timeline.*

For detailed information, [visit here](https://aureus.pw/topic/1619-timeline-stable-as3-cpps-server/)

Visit the official test server, where you can see, test and try all features of current version of Timeline, in real time: https://timeline.valid22.pw

# Contribution
Timeline is a free, open-source project. You can always support this by funding through [PayPal](https://www.paypal.me/valid22).

# Requirements
* Software:
  - Python 2.7.X
  - MySQL, with MySQL-c and MySQL-python connector
  - Redis server

* Python Modules: 
  - [Twisted](https://twistedmatrix.com)
  - [Watchdog](http://pythonhosted.org/watchdog/)
  - [txredisapi](https://github.com/fiorix/txredisapi)
  - [Twistar](http://findingscience.com/twistar/)
  - [BCrypt](https://pypi.python.org/pypi/bcrypt/)
  - [lxml](http://lxml.de/installation.html)
  - [numpy](http://www.numpy.org/)
  - OPTIONAL : [colorlog](https://github.com/borntyping/python-colorlog)
  - A Python MySQL Connector. (Timeline uses MySQLdb by default, you can change this in Database/\_\_init\_\_.py : 31)
  
# Extras
- [Register for Timeline](https://github.com/Times-0/Register/) - Official Register/signup utility for Timeline. This comes in with, email verify tool builtin (both email checkup and account authentication).
- [Timid](https://github.com/Times-0/Timid) - Automated AS3 CPPS Setup utility, which does the hard work of creating CPPS for you!

You can use the following to add more features and customization to your CPPS:
  - [FindFour AI](https://github.com/Times-0/Timeline-FindFourAI/) - An intelligent, human like bot, with whom you can play FindFour matches with.
  - [Commands](https://github.com/Times-0/Timeline/blob/master/Timeline/Plugins/Commands) - Comes with Timeline by default. Enables users to use shortcut commands with the chat system.
  
*Note: There maybe many other plugins not listed in the above list, the above are ones officially tested and found to be working and 100% legit*

# Installation and Usage
Download **Timeline**, put it in an accessible and readable directory. Navigate to that directory using CMD or Shell or any console client. Run `Start.py`. The server will start running.

You can edit `Start.py` to change `Handlers` module scope, `TCP` IP/Port endpoints, Logger etc. You can also add new methods!

Make sure you run **MySQL** and **Redis** server before starting the server.

You can query/run **database.sql** to build tables in your db.

# Default
* Default **database**          : **times-cp**
* Default **user**              : *username:* **test**, *password:* **password**
* Default **crumbs** directory  : **./configs/crumbs/**

**IMPORTANT :** 
    By default Timeline uses colored logger, so you must install _'colorlog'_. If you wish not to use it and go by classical logger, change the following line
```py
TimelineLogger = InitiateColorLogger()
```
to
```py
TimelineLogger = InitiateLogger()
```

# Features
Timeline is almost complete, covering support for all features present in native CP and any classical CPPS. Below is an adaptive list briefing such features:
- Login                 \[AS2, AS3]
- Inventory             \[AS2, AS3]
- Purchasing            \[AS2, AS3]
- Clothing              \[AS2, AS3]
- Moderator             \[AS2, AS3]
- Stealth Moderator     \[AS3]  *AS2 client natively doesn't support stealth mod, even if Timeline does*
- Mascots               \[AS2, AS3]
- Rooms (spawning)      \[AS2, AS3]
- Postcards             \[AS2, AS3]
- EPF                   \[AS2, AS3]
- Chatting              \[AS2, AS3]
- Stamps                \[AS2, AS3]
- Puffles               \[AS2, AS3]
- Puffle adoption       \[AS2, AS3]
- Puffle digging        \[AS3] *Puffle Digging is AS3 exclusive feature, AS2 client doesn't support it*
- Rainbow puffle quest  \[AS3] *Rainbow puffle is AS2 only, AS2 client doesn't support it*
- Gold puffle quest     \[AS3] *Golden puffle is AS3 only,*
- Golden nuggets        \[AS3] *       AS2 client doesn't support it*
- Igloo                 \[AS2, AS3]
- Player actions        \[AS2, AS3]
- Player interactions   \[AS2, AS3]
- Player movements      \[AS2, AS3]
- Player informatics    \[AS2, AS3]
- Sound Studio (Music)  \[AS3] *Sound studio is an AS3 exclusive feature, AS2 client doesn't support it*
- Friends               \[AS2, AS3]
- Games (Single Player) \[AS2, AS3]
- Find Four (Multiplayer-Table)         \[AS3]
- Mancala (Multiplayer-Table)           \[AS3]
- TreasureHunt (Multiplayer-Table) \[AS2, AS3]
- Sled Racing (Multiplayer-Waddle)      \[AS3] *todo as2*
- Card Jitsu (Multiplayer-Waddle)       \[AS3] *todo as2*
- Card Jitsu v/s Sensei (Single Player) \[AS3] *todo as2*
- Card Jitsu Fire (Multiplayer-Waddle)  \[AS3] *todo as2*

# Support
If you have any issue, found any bug or error or issue, or want to suggest some improvemnt, you are free to open an issue or request a pull request.
