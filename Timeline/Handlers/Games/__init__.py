from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'w#jx', WORLD_SERVER, p_r = False)
def handleJoinGame(client, data):
    if client['room'] is not None and isinstance(client['room'], Multiplayer):
        client.send('jx', client['room'].ext_id)
        
        reactor.callLater(1, lambda *x:client['game'].getGame(client)) # client takes time to load

@PacketEventHandler.onXT('z', 'gz', WORLD_SERVER, p_r = False)
def handleGetGame(client, data):
    if client['game'] is None:
        return client.send('gz', '-')

    client.send('gz', client['game'])

@PacketEventHandler.onXT('z', 'uz', WORLD_SERVER, p_r = False)
def handleGetUpdateGame(client, data):
    if client['game'] is None:
        return client.send('gz', 'zzzZ')

    client['game'].updateGame()

@PacketEventHandler.onXT('z', 'jz', WORLD_SERVER, p_r = False)
def handleJoinGame(client, data):
    if client['game'] is None:
        return client.send('jz', '-')

    client['game'].joinGame(client)

@PacketEventHandler.onXT('z', 'lz', WORLD_SERVER, p_r = False)
def handleLeaveGame(client, data):
    if not client['playing'] or client['game'] is None:
        return client.send('lz', '-')

    client['game'].remove(client)

@PacketEventHandler.onXT('z', 'zm', WORLD_SERVER, p_r = False)
def handleSendMoveToGame(client, data):
    if not client['playing'] or client['game'] is None:
        return client.send('e', '?Cheating!')

    client['game'].play(client, data[2])

@PacketEventHandler.onXT('z', 'zo', WORLD_SERVER, p_r = False)
def handleGameOver(client, data):
    score = int(data[2][0])
    coins = round(score/10.0)

    client.penguin.playing = False

    if coins > 10000:
        client.engine.log('warn', "Potential coins manipulation,", current_game, ':', score)
        return

    current_game = client['room']
    if not isinstance(current_game, Game) or isinstance(current_game, Multiplayer):
        try:
            current_game.gameOver(client = client)
        except:
            client.engine.log('warn', "Game exploitation,", current_game.name, ':', score)
        return

    stamps = client['recentStamps']
    g_stamps = client.engine.stampCrumbs.getStampsByGroup(current_game.stamp_id)
    e_stamps = list(set(client['stampHandler']).intersection(g_stamps))

    stamps = list(set(stamps).intersection(g_stamps))

    earned = len(e_stamps)
    total = len(g_stamps)

    if total == earned:
        coins *= 2

    client['coins'] += coins

    client.send('zo', client['coins'], '|'.join(map(str, map(int, stamps))), earned, total, total)
    client['room'].remove(client)

    for room in client['prevRooms'][::-1]:
        if isinstance(room, Place):
            room.append(client)
            return

    #should never get over here