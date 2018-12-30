from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, AS2_PROTOCOL, AVATARS
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Plugins.Commands.Commands import Commands

from twisted.internet.defer import inlineCallbacks, returnValue

import logging

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'pt#spts', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'pt#spts', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleAvatarTranformation(client, data):
    avatarId = int(data[2][0])

    if not client.engine.avatarHandler[avatarId] or (avatarID not in AVATARS and not client['moderator']):
        returnValue(0)

    client['data'].avatar.avatar = avatarId
    yield client['data'].avatar.save()

    client['room'].send('spts', client['id'], avatarId)
    if client.Protocol == AS2_PROTOCOL:
        client['room'].onAdd(client)

@Commands.onCommand('avatar')
def handleTransform(client, param):
    avatarID = int(param[0])
    handleAvatarTranformation(client, ['sp#spts', -1, [avatarID]])

@Commands.onCommand('avatar', AS2_PROTOCOL)
def handleTransformAS2(client, param):
    avatarID = int(param[0])
    handleAvatarTranformation(client, ['sp#spts', -1, [avatarID]])