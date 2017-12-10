from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('z', 'zo', WORLD_SERVER, p_r = False)
def handleGameOver(client, data):
    score = int(data[2][0])
    coins = round(score/10.0)

    if coins > 10000:
        client.engine.log("Potential coins manipulation,", current_game, ':', score)
        return

    current_game = client['room']
    if not isinstance(current_game, Game):
        client.engine.log("Game exploitation,", current_game, ':', score)
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
    for room in client['prevRooms'][::-1]:
        if isinstance(room, Place):
            room.append(client)
            return

    #should never get over here
