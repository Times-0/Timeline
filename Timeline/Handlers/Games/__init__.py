from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Database.DB import Coin

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

ICE_RINK_MESS = [0, 1, -1, -1]  # todo: Make ice-rink game a Multiplayer game object, and add user to it automatically

'''
ICE RINK MESS
'''
@PacketEventHandler.onXT('z', 'm', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'm', WORLD_SERVER, p_r = False)
def handleIceRinkMess(client, data):
    global ICE_RINK_MESS
    ICE_RINK_MESS = map(int, data[2])[:4]

    client['room'].send('zm', client['id'], *ICE_RINK_MESS)

@PacketEventHandler.onXT('s', 'w#jx', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'w#jx', WORLD_SERVER, p_r = False)
def handleJoinGame(client, data):
    if client['room'] is not None and isinstance(client['room'], Multiplayer):
        client.send('jx', client['room'].ext_id)
        
        #reactor.callLater(4, lambda *x:client['game'].getGame(client)) # client takes time to load

@PacketEventHandler.onXT('z', 'gz', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'gz', WORLD_SERVER, p_r = False)
def handleGetGame(client, data):
    if client['room'].ext_id == 802:
        # ice rink mess
        client.send('gz', *ICE_RINK_MESS)
        return

    if client['game'] is None:
        return client.send('gz', '-')

    if hasattr(client['game'], 'getGame'):
        client['game'].getGame(client)
    else:
        client.send('gz', client['game'])

@PacketEventHandler.onXT('z', 'uz', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'uz', WORLD_SERVER, p_r = False)
def handleGetUpdateGame(client, data):
    if client['game'] is None:
        return client.send('gz', 'zzzZ')

    client['game'].updateGame()

@PacketEventHandler.onXT('z', 'jz', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'jz', WORLD_SERVER, p_r = False)
def handleJoinGame(client, data):
    if client['game'] is None:
        return client.send('jz', '-')

    client['game'].joinGame(client)

@PacketEventHandler.onXT('z', 'lz', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'lz', WORLD_SERVER, p_r = False)
def handleLeaveGame(client, data):
    if not client['playing'] or client['game'] is None:
        return client.send('lz', '-')

    client['game'].remove(client)

@PacketEventHandler.onXT('z', 'zm', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'zm', WORLD_SERVER, p_r = False)
def handleSendMoveToGame(client, data):
    if not client['playing'] or client['game'] is None:
        return client.send('e', '?Cheating!')

    client['game'].play(client, data[2])

@PacketEventHandler.onXT('z', 'zo', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'zo', WORLD_SERVER, p_r = False)
def handleGameOver(client, data):
    score = int(data[2][0])
    coins = round(score/10.0)

    client.penguin.playing = False
    current_game = client['room']

    if coins > 10000:
        client.engine.log('warn', "Potential coins manipulation,", current_game, ':', score)
        return

    if not isinstance(current_game, Game) or isinstance(current_game, Multiplayer):
        try:
            current_game.gameOver(client = client)
        except:
            client.engine.log('warn', "Game exploitation,", current_game.name, ':', score)
        return

    stamps = map(int, client['recentStamps'])
    g_stamps = map(int, client.engine.stampCrumbs.getStampsByGroup(current_game.stamp_id))
    e_stamps = list(set(map(lambda x: int(x.stamp), client['data'].stamps)).intersection(g_stamps))

    stamps = list(set(stamps).intersection(g_stamps))

    earned = len(e_stamps)
    total = len(g_stamps)

    if total == earned and total != 0:
        coins *= 2

    Coin(player_id = client['id'], transaction = coins, comment = "Coins earned by playing game. Game: {}".format(current_game.name)).save()
    client['coins'] += coins

    client.send('zo', client['coins'], '|'.join(map(str, stamps)), earned, total, total)
    GeneralEvent("Game-Over", client, score, current_game)
    
    client['room'].remove(client)

    for room in client['prevRooms'][::-1]:
        if isinstance(room, Place):
            room.append(client)
            return

    #should never get over here