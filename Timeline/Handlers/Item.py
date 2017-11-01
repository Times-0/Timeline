from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'i#gi', WORLD_SERVER, p_r = False)
def handleGetInventory(client, data):
	client.send('gi', client['inventory'])

@PacketEventHandler.onXT('s', 'i#ai', WORLD_SERVER)
def handleAddItem(client, item):
	item = client.engine.itemCrumbs[item]

	if item is None:
		return client.send('e', 402)

	if item.is_bait and not client['moderator']:
		# Ban the player?
		client.log('error', '[Exploit detected] Player trying to add a bait item :', item.id)
		return client.send('e', 410)

	if item in client['moderator']:
		return client.send('e', 400)

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_epf and not client['epf']:
		#Suspecious?
		return client.send('e', 410)

	if client.addItem(item):
		client.send('ai', item)
		GeneralEvent.call('add-item:{}'.format(item))