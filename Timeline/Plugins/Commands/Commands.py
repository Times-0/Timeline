from Timeline.Utils.Plugins.IPlugin import IPlugin

from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Constants import AS2_PROTOCOL, AS3_PROTOCOL
from Timeline.Utils.Plugins import PLUGIN_OBJECTS

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
        super(Commands, self).__init__()

        self.logger = logging.getLogger(TIMELINE_LOGGER)

        GeneralEvent.on('before-message', self)
        GeneralEvent.on('after-message-muted', self.deMute)

        self.setup()

        self.logger.debug("Player Commands Active!")

    def setup(self):
        GeneralEvent.on('command=jr', self.JoinRoomByExtId)

    @staticmethod
    def onCommand(command, protocol = AS3_PROTOCOL, function = None):
        command_ext = 'command[{}]={}'.format(protocol, command)
        
        commandPlugin = [i for i in PLUGIN_OBJECTS if isinstance(i, Commands)][-1]
        commandPlugin.__commands__.append(command) if command not in commandPlugin.__commands__ else None

        return GeneralEvent.on(command_ext, function=function)

    @staticmethod
    def onCommandAS2(command):
        return Commands.onCommand(command, AS2_PROTOCOL)

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
            client.penguin.muted_for_command = True if client['muted_for_command'] is None \
                else client['muted_for_command']
            GeneralEvent('command={}'.format(command), client, params)
            GeneralEvent('command[{}]={}'.format(client.Protocol, command), client, params)
