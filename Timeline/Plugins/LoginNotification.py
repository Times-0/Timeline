from Timeline.Utils.Plugins.IPlugin import IPlugin

from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging

class LoginNotification(IPlugin):
    """Display's name of penguin logging in"""


    requirements = list()
    name = 'LoginNotification'
    developer = 'Dote'

    def __init__(self):
        super(LoginNotification, self).__init__()

        self.logger = logging.getLogger(TIMELINE_LOGGER)
        self.logger.info("Login Notification activated!")

        PacketEventHandler.onXML('login', LOGIN_SERVER, function = self.loginNotice)

    def loginNotice(self, client, user, passd):
        self.logger.info("%s is attempting to login", user)