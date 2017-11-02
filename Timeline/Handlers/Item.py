from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'i#gi', WORLD_SERVER, p_r = False)
def handleGetInventory(client, data):
	client.send('gi', *map(int, client['inventory']))

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
		client.send('ai', item, client['coins'])
		GeneralEvent.call('add-item:{}'.format(item))

@PacketEventHandler.onXT('s', 'i#qpp', WORLD_SERVER)
@inlineCallbacks
def handleGetPins(client, _id):
	penguin = yield client.db_getPenguin('ID = ?', _id)

	if penguin == None:
		returnValue(None)

	inventory = Inventory(client)
	inventory.parseFromString(penguin.inventory)
	inventory.penguin = None

	pins = map(lambda x: map(int, [x.id, x.release, x.is_member]), inventory.itemsByType(Pin))
	
	client.send('qpp', _id, *(map(lambda x: '|'.join(map(str, x)), pins)))

@PacketEventHandler.onXT('s', 'i#qpa', WORLD_SERVER)
@inlineCallbacks
def handleGetAwards(client, _id):
	penguin = yield client.db_getPenguin('ID = ?', _id)

	if penguin is None:
		return

	inventory = Inventory(client)
	inventory.parseFromString(penguin.inventory)
	inventory.penguin = None

	awards = inventory.itemsByType(Award)

	client.send('qpa', _id, *awards)