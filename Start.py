'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Below shows examples of starting a World-Server and Login-Server
'''

'''
Basic imports : These are mandatory to import before starting any server.
'''
import Timeline
from Timeline.Server import Constants
from Timeline.Server.Engine import Engine
from Timeline.Server.Penguin import Penguin
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Modules import ModuleHandler
from Timeline import Handlers
from twisted.internet import reactor
import logging
import os

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
_________________________________________________________
|                      TIMELINE                         |
|          AS3 CPPS Emulator, Written in Python         |
|          Developer: Dote                              |
|_______________________________________________________|
|                                                       |
|         Version : 0.1 [Development]                   |
|         Updates : Added logger, Added handlers        |
|_______________________________________________________|
"""

# Example of starting the logger!
InitiateLogger()

# Example of initiating the ModuleHandler which deals extensively with Modifications of modules at runtime.
MHandler = ModuleHandler(Handlers)
MHandler.startLoadingModules()

# Example of initiating server to listen to given endpoint.
Server = Engine(Penguin)
Server.run('127.0.0.1', 6112)

reactor.run()
