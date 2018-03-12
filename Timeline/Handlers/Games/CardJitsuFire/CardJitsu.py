from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, FIRE_STARTER_DECK
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Games.CardJitsuFire import CJ_MATS, CJMat

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

@GeneralEvent.on('add-item:8006')
def AddFireStarterDeck(client):
	client['inventory'] += [821, 3032]
	client.send('%xt%ai%-1%821%{0}%\x00%xt%ai%-1%3032%{0}%'.format(client['coins']))

	cardsToAdd = [client.engine.cardCrumbs[k] for k in FIRE_STARTER_DECK] + [choice([250,250,250,250,352])]

	for c in cardsToAdd:
		if c is None:
			continue

		if c.id not in client['ninjaHandler'].cards:
			client['ninjaHandler'].cards[c.id] = [c, 0]

		client['ninjaHandler'].cards[c.id][1] += 1

	client['ninjaHandler'].ninja.cards = '|'.join(map(lambda x: "{},{}".format(x, client['ninjaHandler'].cards[x][1]), client['ninjaHandler'].cards))
	client['ninjaHandler'].ninja.save()