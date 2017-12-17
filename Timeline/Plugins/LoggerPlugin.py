from Timeline.Utils.Plugins.IPlugin import IPlugin, IPluginAbstractMeta, Requirement
from Timeline.Utils.Plugins import extend

from Timeline.Server.Penguin import Penguin

from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging

class LoggerPlugin(IPlugin):
    """extends penguin object to log new penguin initialization and disconnect"""

    __metaclass__ = IPluginAbstractMeta

    name = "LoggingPlugin"
    developer = "Dote"

    requirements = [Requirement(**{'name' : 'LoginNotification', 'developer' : 'Dote'})]

    @classmethod
    def onBuild(cls):
        extend(Penguin, cls)

    def makeConnection(self, transport):
        self.engine.log("info", "New client connection:", self.client)

    def connectionLost(self, reason):
        self.engine.log("info", self.getPortableName(), "Disconnected")

    def lineReceived(self, line):
        me = self.getPortableName()
        self.engine.log("debug", "[RECV]", me, line)

