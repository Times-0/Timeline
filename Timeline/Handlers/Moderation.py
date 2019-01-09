from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Penguin import Penguin
from Timeline.Database.DB import Ban

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'o#k', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'o#m', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'o#k', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'o#m', WORLD_SERVER)
def SendMessageRule(data):
    return [[int(data[2][0])], {}]

def GetPenguin(engine, client, identify = 'id'):
    identify = identify.strip().lower()
    if identify == 'nick' or identify == 'nickname':
        identify = 'nickname'

    elif identify == 'user' or identify == 'username' or identify == 'name':
        identify = 'username'

    elif identify == 'id' or isinstance(client, int):
        identify = 'id'
        client = int(client)

    elif isinstance(identify, Penguin):
        identify = None

    else:
        raise NotImplementedError("Unable to recognize penguin's property: %s", identify)

    if identify != None:
        _client = None
        for u in list(engine.users):
            if u[identify] == client:
                _client = u
                break

        client = _client
        if client is None:
            raise LookupError("User with property %s:%s not found on server %s", identify, client, engine)

    return client


@GeneralEvent.on('mute-player')
def MutePlayerCommand(client, reason):
    client.engine.log('info', "Penguin %suted: %s", "Un-m" if client['mutes'] else 'M', reason)
    client.penguin.muted = not client['muted']

    client.send('moderatormessage', 2)

@GeneralEvent.on('kick-player')
def KickPlayerCommand(client, reason):
    client.engine.log('info', "Penguin", client['nickname'],"Kicked:", reason)
    client.canRecvPacket = client.ReceivePacketEnabled = False

    client.send('moderatormessage', 3)
    client.disconnect()

@GeneralEvent.on('ban-player')
@inlineCallbacks
def BanPlayerCommand(client, by_id, reason = 'Cheating/Hacking/Manipulation/Rude/Against Rules', hours = 1, type = 1, ban_type = 601):
    '''
    client: Penguin object to be banned
    by_id : Id of moderator banning client, 0 for system
    reason[Cheating/Hacking/Manipulation/Rude/Against Rules] : reason for ban
    hours[1]: No of hours banned
    type[1]: Type of ban
        1 => Banned in game, via packets
        2 => Banned by control panel
        3 => Banned by Server, auto banned
    ban_type[601]: Type of ban
        601: normal ban
        610: auto ban
        hacking auto ban: 611
    '''
    seconds = hours * 60 * 60 if hours > 0 else 946080000
    expire = int(time() + seconds)

    client.engine.log('info', 'Penguin Banned: %s banned for next %s hour(s) by staff id: %s, reason: %s', client['nickname'], hours, by_id, reason)
    yield Ban(player = client['id'], moderator = by_id, comment = reason, expire = expire, type = type).save()
    client['RefreshHandler'].forceRefresh()

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'o#k', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'o#k', WORLD_SERVER)
def handleKickPlayer(client, _id):
    if not client['moderator']:
        client.engine.log('warn', '%s tried to kick %s. %s is not a moderator.', client['nickname'], _id)
        return GeneralEvent('ban-player', client, 0, 'Hacking or Manipulating server. Unauthorized kick {}, while not a moderator.'.format(_id), 1, 3)

    _kickable = GetPenguin(client.engine, _id)
    if _kickable['moderator']:
        return client.send('e', 800)
    GeneralEvent('kick-player', _kickable, '{} kicked {} on {}'.format(client['nickname'], _kickable['nickname'], client.engine))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'o#m', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'o#m', WORLD_SERVER)
def handleMutePlayer(client, _id):
    if not client['moderator']:
        client.engine.log('warn', '%s tried to (un)mute %s. %s is not a moderator.', client['nickname'], _id)
        return GeneralEvent('ban-player', client, 0, 'Hacking or Manipulating server. Unauthorized (un)muting {}, while not a moderator.'.format(_id), 1, 3)

    _mutable = GetPenguin(client.engine, _id)
    if _mutable['moderator']:
        return client.send('e', 800)
    GeneralEvent('mute-player', _mutable, '{} (un)muted {} on {}'.format(client['nickname'], _mutable['nickname'], client.engine))