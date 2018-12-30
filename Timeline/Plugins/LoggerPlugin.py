from Timeline.Utils.Plugins.IPlugin import IExtender, IPluginAbstractMeta, Requirement
from Timeline.Utils.Plugins import extend

from Timeline.Server.Penguin import Penguin

from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging

class LoggerPlugin(IExtender):
    """extends penguin object to log new penguin initialization and disconnect"""

    name = "LoggingPlugin"
    developer = "Dote"

    __extends__ = [Penguin]


    def makeConnection(self, transport):
        self.engine.log("info", "New client connection:", self.client)

    def connectionLost(self, reason):
        self.engine.log("info", self.getPortableName(), "Disconnected", "Reason:", reason)

    def lineReceived(self, line):
        me = self.getPortableName()
        self.engine.log("debug", "[RECV]", me, line)

