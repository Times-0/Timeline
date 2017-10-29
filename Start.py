#-*-coding: utf-8-*-
'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Below shows examples of starting a World-Server and Login-Server
'''

'''
Basic imports : These are mandatory to import before starting any server.
'''
import Timeline
from Timeline.Server import Constants
from Timeline.Database import DBManagement as DBM
from Timeline.Server.Engine import Engine
from Timeline.Server.Penguin import Penguin
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Modules import ModuleHandler
from Timeline import Handlers
from Timeline import PacketHandler
from twisted.internet import reactor
import logging
import os, sys

'''
global -> TIMELINE_LOGGER : Defines the name of logging class used globally!
'''
Constants.TIMELINE_LOGGER = 'Timeline'

'''
InitiateLogger : This is function initiates the logger accessed all along Timeline.
@dependencies : logging
@param[name]->optional : Defines the name of the logger you are going to use all along, default - Timeline
'''
def InitiateLogger(name="Timeline"):
	Constants.TIMELINE_LOGGER = name
	Timeline_logger = logging.getLogger(name)
	
	Timeline_stream = logging.StreamHandler()
	LogFormat = logging.Formatter("%(asctime)s [%(levelname)s]\t : %(message)s", "%H:%M")
	Timeline_stream.setFormatter(LogFormat)
	Timeline_logger.addHandler(Timeline_stream)

	Timeline_logger.setLevel(logging.DEBUG)

	Timeline_logger.debug("Timeline Logger::Initiated")

print \
"""
 _______
|__   __|
   | |  #   _ _     __  ||  #  __     __  py 
   | | | | | | |  / //| || || |  |  / //|     
   | | | | | | | |_||/  || || |  | |_||/          
   |_| |_| | | |  \__   || || |  |  \__     
----------------------------------------------
> AS3 CPPS Emulator. Written in Python
> Developer : Dote
> Version   : 2.0x (Development)
> Updates   : [+] Database
              [+] on memory Redis Server
              [+] Login handler 
              [+] Errors fixed
              [-] Bugs fixed and deferred
_______________________________________________
"""

# Example of starting the logger!
InitiateLogger()

# Example of initiating the ModuleHandler which deals extensively with Modifications of modules at runtime.
MHandler = ModuleHandler(Handlers)
MHandler.startLoadingModules()

# Initiating PacketHandler which deals with modification  of Packet Rule handlers
PHandler = ModuleHandler(PacketHandler)
PHandler.startLoadingModules()

#Checking database, databas details once set cannot be change during runtime
DBMS = DBM(user = "root", passd = "", db = "times-cp")
if not DBMS.conn:
	sys.exit()

# Example of initiating server to listen to given endpoint.
'''
LOGIN_SERVER => Initiates Engine to be a Login server
WORLD_SERVER => Initiates Engine to be a World Server

The type of server *must* be sent to Engine as a parameter!
'''
LoginServer = Engine(Penguin, Constants.LOGIN_SERVER, 100, "Login")
LoginServer.run('127.0.0.1', 6112)

reactor.run()
