from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, GOLD_RUSH_DIGGABLES, PROBS, AS2_PROTOCOL, AS3_PROTOCOL
from Timeline import Username, Password
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Igloo
from Timeline.Database.DB import Coin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
import random

logger = logging.getLogger(TIMELINE_LOGGER)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'j#js', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'j#js', WORLD_SERVER)
@inlineCallbacks
def handleJoinServer(client, _id, passd, lang):
    if _id != client.penguin.id or passd != client.penguin.password:
        client.send('e', 101)
        returnValue(client.disconnect())

    # User logged in!
    yield client.engine.redis.server.hincrby('server:{}'.format(client.engine.id), 'population', 1)
    yield client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'joined' : 1})
    yield client.engine.redis.server.sadd("users:{}".format(client.engine.id), client['swid'])

    client.initialize()
    yield client['RefreshHandler'].CacheInitializedDefer
    GeneralEvent.call("penguin-logged", client.selfRefer)

    # 47 -> all lang except russian, 111 -> all incl russian; russian lang is deprecated and no longer exists
    # to get support for any lang, use bitmask = LANG1_BITMASK ^ LANG2_BITMASK ^ ...
    client.penguin.lang_allowed = bool(lang & client['data'].avatar.language)
    client.penguin.language = client['data'].avatar.language if not client['moderator'] else 47

    # todo: epf
    client.send('js', *(map(int, [0, client['RefreshHandler'].inInventory(428), client['moderator']])))
    client.send('gps', client['id'], '|'.join([str(k.stamp) for k in client['data'].stamps]))

    client.canRecvPacket = True # Start receiving XT Packets

    member = int(client['member']) if int(client['member']) > 0 else 0
    if client.Protocol == AS3_PROTOCOL:
        client.send('lp', client, client['coins'], 0, 1024, int(time() * 1000), client['age'], 0, client['age'], member, '', client['cache'].playerWidget, client['cache'].mapCategory, client['cache'].igloo)
    elif client.Protocol == AS2_PROTOCOL:
        # #user_str%coins%issafe%egg%time%age%banned%minplay%memdays
        client.send('lp', client, client['coins'], 0, 1024, int(time() * 1000), client['age'], 0, int(client['age'])/60, member, 0)
    
    client.engine.roomHandler.joinRoom(client, 'dojo', 'name') # TODO Check for max-users limit

@GeneralEvent.on('onClientDisconnect')
def handleRemoveClient(client):
    if client['room'] is not None:
        client['room'].remove(client)

    if client['playing'] or client['game'] is not None or client['waddling']:
        client['game'].remove(client)

@GeneralEvent.on('onBuildClient')
def handleSetGoldenRushDigging(client):
    client.penguin.lastGoldenRushDig = int(time()) - 3

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'j#jr', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'j#jr', WORLD_SERVER)
def handleJoinRoom(client, _id, x, y):
    client.penguin.x, client.penguin.y = x, y

    client.engine.roomHandler.joinRoom(client, _id, 'ext')

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'j#grs', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'j#grs', WORLD_SERVER, p_r = False)
def handleRefreshRoom(client, data):
    if client['room'] is None:
        return

    client['room'].onAdd(client)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'j#jp', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'j#jp', WORLD_SERVER)
@inlineCallbacks
def handleJoinIgloo(client, _id, _type):
    room = yield client['RefreshHandler'].initPenguinIglooRoom(_id)
    if room is None:
        returnValue(None)

    if client['waddling'] or client['playing']:
        client.send('e', 200)

    if client['room'] is not None:
        client['room'].remove(client)

    if _type == 'igloo':
        room.append(client)
        returnValue(None)

    if _type == 'backyard':
        if client['prevRooms'][-1] == room:
            if room.backyard is None:
                room.backyard = Igloo(client.engine.roomHandler, room.ext_id, room.keyName, "{}'s Backyard".format(room.name), 150, False, False, None)
                room.backyard.type = 'backyard'
                room.backyard.opened = True
                room.backyard.owner = room.owner
                room.backyard._id = room._id

            if room.owner == client['id']:
                room.backyard.append(client)
                returnValue(None)

    #client['prevRooms'][-1].append(client)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'r#gtc', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'r#gtc', WORLD_SERVER, p_r = False)
def handleGetTotalPlayerCoins(client, data):
    client.send('gtc', client['coins'])

def random_picks(sequence, relative_odds):
    table = [ z for x, y in zip(sequence, relative_odds) for z in [x]*y ]
    while True:
        yield random.choice(table)

DIGGABLE = random_picks(GOLD_RUSH_DIGGABLES, PROBS)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'r#cdu', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'r#cdu', WORLD_SERVER, p_r = False)
def handleGoldRushDig(client, data):
    cannotDig = max(0, 3 - int(time() - client['lastGoldenRushDig']))
    dcoin = DIGGABLE.next() * int(not cannotDig)
    if dcoin:
        setattr(client.penguin, 'lastGoldenRushDig', int(time()))
        Coin(penguin_id = client['id'], transaction = dcoin,
             comment = "Earned coin by digging in the Golde Mine. "
                       "Player in Golde Mine = {}".format(client['room'].ext_id == 813)).save()
        client['coins'] += dcoin

    client.send('cdu', dcoin, client['coins'])

def init():
    logger.debug('Join(j) Packet handlers initiated!')