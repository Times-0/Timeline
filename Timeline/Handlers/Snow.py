from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, AS2_PROTOCOL, AVATARS, MULTIPLAYER_GAMES
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game
from Timeline.Plugins.Commands.Commands import Commands

from twisted.internet.defer import inlineCallbacks, returnValue

import logging

logger = logging.getLogger(TIMELINE_LOGGER)

class SnowRoom(Game):
    game = True
    waddle = None

    @inlineCallbacks
    def generate_cjs_loginKey(self, client):
        key = (client.CryptoHandler.random(10) + "-" + client.CryptoHandler.random(10)).encode('hex')
        
        yield client.engine.redis.server.set("mp_session:{0}".format(client['swid']), key, 5*60) # authenticate for next 5 mins
        client.send('mpsk', client.CryptoHandler.bcrypt(key), 'smart')

    def onAdd(self, client):
        self.generate_cjs_loginKey(client).addCallback(lambda *x: super(SnowRoom, self).onAdd(client))


MULTIPLAYER_GAMES[996] = SnowRoom
