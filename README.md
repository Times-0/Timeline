# Timeline
AS2 & AS3 CPPS Emulator, written in Python.
Timeline is built heavily on Twisted and is even-driven, most of the methods are Deferred too!

**Timeline docs now live at** https://times-0.github.io/

# Firebase Integration
**Timeline v7.2** or later supports the integrated Firebase, autologin system. To use this, make sure you have compatible client setup already. You can visit docs for detailed guide on how to setup Firebase login system. 

_This integration is optional, yet recommended. No data loss, or account loss will be experienced during this integration. Any account not using firebase, will be automatically converted upon login_

## Real-time Message Filter \[Perspective API]
**Timeline v7.1** or later, supports real-time filtering of messages, based on toxicity in the content of speech. Using the Google's intelligent AI based _Perspective API_, it's now made possible to have more child-friendly environment.

The **Perspective API Key** provided by default is just for **testing/development/educational** purpose. Please **don't** use the same key for your **production server**. You **must** get yourself **whitelisted** from Google, and get yourself **a key for your server**. 

Visit this [Quickstart Guide to Perspective](https://github.com/conversationai/perspectiveapi/blob/master/quickstart.md) to get yourself a key. _Don't worry, you'll mostly get whitelisted within a day_. 
Look into [Timeline > Handlers > Messages # Line 76](https://github.com/Times-0/Timeline/blob/master/Timeline/Handlers/Messages.py#L76) for more details, on how to effectively use your key.

## Important Upgrade Notice (From Timeline v>= 7)
From the **version 7 of Timeline**, there is a strict implementation, forcing you to follow a database convention, in order to make it easy to upgrade to newer database sturcture without any chaos. All new database, using new database structure should follow the nomenclature: **database name should end with `line`**. Example, `timeline`, `waddle-line`, `waddleupline`, and so on.

Everyone who started using v7, and want to migrate data from older version, are requested to use the python script `DatabasePort.py` to port all your old data into the new database structure.

**Note** It is recommended to run the script as **sudo** (on UNIX server). ie, `sudo python DatabasePort.py`, in-order to have an error free, and smooth experience.

**Of all the chaos what do you yet?** *You get a sweet, charm, more flexible, server, which has __on-the air, real-time updation of data__. And everyone's favourite __CJ Fire v/s Sensei__. What more you think could suffice this? Oh yeah, some bugs and filaments are cleaned up too :~)*

*Oh and, **upgrade Twisted** module if you haven't already :~D*

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
  - [colorlog](https://github.com/borntyping/python-colorlog)
  - A Python MySQL Connector. (Timeline uses MySQLdb by default, you can change this in Database/\_\_init\_\_.py : 31)
  - mysql-connector-python : `pip install mysql-connector-python`
  - mysql-python, Ref: [Installing MySQL-Python](#installing-mysql-python-mysqldb)
  
# Extras
- [Timeflex Webserver](https://github.com/Times-0/TimeFlex) and a brand new [automated login system](https://times-0.github.io/member)
- [Register for Timeline](https://github.com/Times-0/Register/) - Official Register/signup utility for Timeline. This comes in with, email verify tool builtin (both email checkup and account authentication).
- [Friends list](https://github.com/Times-0/Friends) HTML-based original CP styled Friends list.
- ~~[Timid](https://github.com/Times-0/Timid) - Automated AS3 CPPS Setup utility, which does the hard work of creating CPPS for you!~~

You can use the following to add more features and customization to your CPPS:
  - [FindFour AI](https://github.com/Times-0/Timeline-FindFourAI/) - An intelligent, human like bot, with whom you can play FindFour matches with.
  - [Commands](https://github.com/Times-0/Timeline/blob/master/Timeline/Plugins/Commands) - Comes with Timeline by default. Enables users to use shortcut commands with the chat system.
  
*Note: There maybe many other plugins not listed in the above list, the above are ones officially tested and found to be working and 100% legit*

# Installation and Usage
Download **Timeline**, put it in an accessible and readable directory. Navigate to that directory using CMD or Shell or any console client. Run `Start.py`. The server will start running.

You can edit `Start.py` to change `Handlers` module scope, `TCP` IP/Port endpoints, Logger etc. You can also add new methods!

Make sure you run **MySQL** and **Redis** server before starting the server.

Please run `DatabasePort.py` to create tables in your database. It also auto recreated db for you, you just need a spare databse beforehand. (ie, old dbname as spare db, new db name as the one you want to create)

# Installing mysql-python (MySQLdb)
Who hadn't had trouble installing MySQLdb (MySQL-python) package for Python on Windows!

If you are on UNIX environment (ie Ubuntu, Linux, etc), the following should work just fine
```
sudo pip install MySQL-python
```
But, the same in Windows, should be a lot messy, so instead try executing the following command instead. Before that, move the command console into the directory in which you have installed Timeline (eg: `cd C:\Users\Times\Desktop\Timeline-master`
```
pip install MySQL_python-1.2.5-cp27-none-win_amd64.whl
```
if that didn't work, try this
```
pip install MySQL_python-1.2.5-cp27-none-win32.whl
```
That's it. All the connectors are baked. :~)

# Default
* Default **database**          : **timeline**
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
- Card Jitsu Fire v/s Sensei           \[AS3] *todo as2*

# Support
If you have any issue, found any bug or error or issue, or want to suggest some improvemnt, you are free to open an issue or request a pull request.
