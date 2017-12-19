from Timeline.Utils.Plugins.IPlugin import IPlugin

from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import Penguin
from Timeline.Server.Penguin import Penguin as Bot

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging

class Commands(IPlugin):
    """Commands Plugin"""


    requirements = list()
    name = 'Commands'
    developer = 'Dote'

    __commands__ = ["jr"]

    def __init__(self):
        super(FindFourAI, self).__init__()

        self.logger = logging.getLogger(TIMELINE_LOGGER)

        GeneralEvent.on('before-message', self)
        GeneralEvent.on('after-message-muted', self.deMute)

        self.setup()

        self.logger.debug("Player Commands Active!")

    def setup(self):
        GeneralEvent.on('command=jr', self.JoinRoomByExtId)

    def JoinRoomByExtId(self, client, param):
        try:
            _id = int(param[0])

            client.engine.roomHandler.joinRoom(client, _id, 'ext')
        except:
            pass

    def deMute(self, client, *a):
        if client['muted'] and client['muted_for_command']:
            client.penguin.muted_for_command = client.penguin.muted = False

    def __call__(self, client, message):
        if not message.startswith('!') or client['muted']:
            return

        msg_packets = message[1:].split(' ')
        command = msg_packets[0].lower()
        params = msg_packets[1:]

        __commands__ = [str(k).lower() for k in self.__commands__]
        
        if command in __commands__:
            client.penguin.muted = True
            client.penguin.muted_for_command = True
            GeneralEvent('command={}'.format(command), client, params)
