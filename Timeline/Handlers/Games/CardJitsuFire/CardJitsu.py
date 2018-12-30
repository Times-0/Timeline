from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, FIRE_STARTER_DECK
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Games.CardJitsuFire import CJ_MATS, CJMat
from Timeline.Handlers.Games.CardJitsuFire.Sensei import CardJitsuFireSenseiGame
from Timeline.Handlers.Games.CardJitsu.CardJitsu import getSensei

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import choice

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setCJMats(ROOM_HANDLER):
    for i in CJ_MATS:
        ROOM_HANDLER.ROOM_CONFIG.WADDLES[i] = CJMat(ROOM_HANDLER, i, "FireJitsuMat", "Card Jitsu Fire Mat", CJ_MATS[i], False, False, None)
        ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddle = i
        ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddles = CJ_MATS[i]

    logger.debug("Card Jitsu Fire Initiated")

@PacketEventHandler.onXT('z', 'jsen', WORLD_SERVER, p_r = False)
def handleJoinSenseiCJ(client, data):
    ROOM_HANDLER = client.engine.roomHandler

    if client['room'].ext_id != 953:
        return

    gameMat = CJMat(ROOM_HANDLER, 997, "JitsuMat", "Card Jitsu Mat", 3, False, False, None)
    gameMat.waddle = 997
    gameMat.game = CardJitsuFireSenseiGame
    senseiRoom = client['room']

    sensei = getSensei(client.engine)

    gameMat.append(sensei)
    gameMat.append(client)

    game = client['game']
    game.send('scard', game.ext_id, 997, 2)

    sensei.penguin.game_index = 0
    game.joinGame(sensei)
    list.remove(senseiRoom, client)

@GeneralEvent.on('add-item:8006')
@inlineCallbacks
def AddFireStarterDeck(client):
    [(yield client.addItem(i)) for i in [821, 3032]]
    yield client['RefreshHandler'].forceRefresh()

    cardsToAdd = [client.engine.cardCrumbs[k] for k in FIRE_STARTER_DECK + [choice([250,250,250,250,352])]]

    for c in cardsToAdd:
        if c is None:
            continue

        if c.id not in client['ninjaHandler'].cards:
            client['ninjaHandler'].cards[c.id] = [c, 0]

        client['ninjaHandler'].cards[c.id][1] += 1

    client['ninjaHandler'].ninja.cards = '|'.join(map(lambda x: "{},{}".format(x, client['ninjaHandler'].cards[x][1]), client['ninjaHandler'].cards))
    client['ninjaHandler'].ninja.save()