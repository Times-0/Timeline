from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, RAINBOW_QUEST_ITEMS
from Timeline.Utils.Puffle import Puffle
from Timeline.Utils.Mails import Mail
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time
from random import choice
import json

@PacketEventHandler.onXT('s', 'p#revealgoldpuffle', WORLD_SERVER, p_r = False)
def handleRevealGP(client, data):
	if client['canAdoptGold']:
		client.send('revealgoldpuffle', client['id'])

@PacketEventHandler.onXT('s', 'rpq#rpqd', WORLD_SERVER, p_r = False)
def handleGetRawRBCData(client, data):
	client.send('rpqd', json.dumps(client['currencyHandler'].quest['puffle']['rainbow']))

@PacketEventHandler.onXT('s', 'rpq#rpqtc', WORLD_SERVER, p_r = False)
def handleComplateRBQuest(client, data):
	questID = int(data[2][0])
	if not 0 <= questID < len(client['currencyHandler'].quest['puffle']['rainbow']['tasks']):
		return

	iTask = client['currencyHandler'].quest['puffle']['rainbow']['tasks'][questID]
	if iTask['completed'] or client['currencyHandler'].quest['puffle']['rainbow']['questsDone'] != questID:
		return

	iTask['completed'] = True
	qD = client['currencyHandler'].quest['puffle']['rainbow']['questsDone']
	client['currencyHandler'].quest['puffle']['rainbow']['currTask'] = client['currencyHandler'].quest['puffle']['rainbow']['questsDone'] = min(4, qD + 1)
	print 'currentTask', min(4, qD + 1)

	if client['currencyHandler'].quest['puffle']['rainbow']['questsDone'] > 3:
		client.penguin.canAdoptRainbow = client['currencyHandler'].quest['puffle']['rainbow']['cannon'] = True
		client['currencyHandler'].quest['puffle']['rainbow']['bonus'] = 1
		client['currencyHandler'].quest['puffle']['rainbow']['currTask'] = 3

	client['currencyHandler'].refreshCurrencies()

@PacketEventHandler.onXT('s', 'rpq#rpqcc', WORLD_SERVER, p_r = False)
def handleCollectRBQCoins(client, data):
	questID = int(data[2][0])
	if not 0 <= questID < len(client['currencyHandler'].quest['puffle']['rainbow']['tasks']):
		return

	iTask = client['currencyHandler'].quest['puffle']['rainbow']['tasks'][questID]
	if not iTask['completed'] or iTask['coin'] > 1:
		return

	iTask['coin'] = 2
	client['coins'] += 100 + 10 * questID
	client['currencyHandler'].refreshCurrencies()
	client.send('rpqcc', questID, 2, client['coins'])

@PacketEventHandler.onXT('s', 'rpq#rpqic', WORLD_SERVER, p_r = False)
def handleCollectRBQItem(client, data):
	questID = int(data[2][0])
	if not 0 <= questID < len(client['currencyHandler'].quest['puffle']['rainbow']['tasks']):
		return

	iTask = client['currencyHandler'].quest['puffle']['rainbow']['tasks'][questID]
	item = RAINBOW_QUEST_ITEMS[questID]

	if not iTask['completed'] or iTask['item'] > 1 or not client['member'] or item in client['inventory']:
		return

	iTask['item'] = 2
	client['inventory'] += item
	client['currencyHandler'].refreshCurrencies()
	client.send('ai', item, client['coins'])

@PacketEventHandler.onXT('s', 'rpq#rpqbc', WORLD_SERVER, p_r = False)
def handleCollectRBQBonus(client, data):
	if not client['currencyHandler'].quest['puffle']['rainbow']['bonus']:
		return

	if not 5220 in client['inventory']:
		client['inventory'].append(5220)
		client.send('ai', 5220, client['coins'])

	client['currencyHandler'].quest['puffle']['rainbow']['bonus'] = 2
	client['currencyHandler'].refreshCurrencies()