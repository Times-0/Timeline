# Timeline
AS3 CPPS Emulator, written in Python.
Timeline is built heavily on Twisted and is even-driven, most of methods are Deferred too!

For detailed information, [visit here](https://aureus.pw/topic/1619-timeline-stable-as3-cpps-server/)

# Requirements
* Softwares:
  - Python >= 2.7
  - MySQL, with MySQL-c and MySQL-python connector
  - Redis server

* Python Modules: 
  - [Twisted](https://twistedmatrix.com)
  - [Watchdog](http://pythonhosted.org/watchdog/)
  - [txredisapi](https://github.com/fiorix/txredisapi)
  - [Twistar](http://findingscience.com/twistar/)
  - [BCrypt](https://pypi.python.org/pypi/bcrypt/)
  - [lxml](http://lxml.de/installation.html)
  - OPTIONAL : [colorlog](https://github.com/borntyping/python-colorlog)
  
# Extras
You can use the following to add more features and customization to your cpps:
  - [FindFour AI](https://github.com/Times-0/Timeline-FindFourAI/) - An intelligent, human like bot, with whom you can play FindFour matches with.
  - [Commands](https://github.com/Times-0/Timeline/blob/master/Timeline/Plugins/Commands) - Comes with Timeline by default. Enables users to use shortcut commands with the chat system.
  
*Note: There maybe many other plugins not listed in the above list, the above are ones officially tested and found to be working and 100% legit*

# Installation and Usage
Download **Timeline**, put it in an accessable and readable directory. Navigate to that directory using CMD or Shell or any console client. Run `Start.py`. The server will start running.

You can edit `Start.py` to change `Handlers` module scope, `TCP` IP/Port endpoints, Logger etc. You can also add new methods!

Make sure you run **MySQL** and **Redis** server before starting the server.

You can query/run **database.sql** to build tables in your db.

# Default
* Default **database**          : **times-cp**
* Default **user**              : *username:* **test**, *password:* **password**
* Default **crumbs** directory  : **./configs/crumbs/**

**IMPORTANT :** By default Timeline uses colored logger, so you must install _'colorlog'_. If you wish not to use it and go by classical logger, change the following line
```py
TimelineLogger = InitiateColorLogger()
```
to
```py
TimelineLogger = InitiateLogger()
```

# Support
If you have any issue, found any bug or error or issue, or want to suggest some improvemnt, you are free to open an issue or request a pull request.
