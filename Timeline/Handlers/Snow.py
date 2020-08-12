from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, AS2_PROTOCOL, AVATARS, MULTIPLAYER_GAMES
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game
from Timeline.Plugins.Commands.Commands import Commands

from twisted.internet.defer import inlineCallbacks, returnValue

import logging

logger = logging.getLogger(TIMELINE_LOGGER)

class SnowRoom(Game):
    # Multiplayer!

    game = True
    waddle = None

    def onAdd(self, client):
        super(SnowRoom, self).onAdd(client)


MULTIPLAYER_GAMES[996] = SnowRoom