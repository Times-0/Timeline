from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Puffle import Puffle
from Timeline.Utils.Mails import Mail
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time

@PacketEventHandler.onXT('s', 'p#pg', WORLD_SERVER)
@inlineCallbacks
def handleGetPuffles(client, _id, isBackyard):
	puffles = yield client['puffleHandler'].getPenguinPuffles(_id, isBackyard)

	if puffles is None:
		returnValue(None)

	client.send('pg', len(puffles.split('%')), puffles)

@PacketEventHandler.onXT('s', 'p#pgmps', WORLD_SERVER, p_r = False)
def handleGetMyPuffle(client, data):
	puffles = str(client['puffleHandler']).split('%')

	client.send('pgmps', ','.join(puffles))

@PacketEventHandler.onXT('s', 'p#pw', WORLD_SERVER)
def handlePuffleWalk(client, puffle, isWalking):
	puffle = client['puffleHandler'].getPuffleById(puffle)

	if puffle is None:
		return None

	is_walking = bool(int(puffle.walking))
	if is_walking is isWalking:
		return None

	if client['puffleHandler'].walkingPuffle is not None:
		if client['puffleHandler'].walkingPuffle.id is puffle.id and isWalking:
			return None

		client['puffleHandler'].walkingPuffle.walking = 0
		client['puffleHandler'].walkingPuffle.save()

	puffle.walking = int(isWalking)
	puffle.save()

	client['puffleHandler'].walkingPuffle = puffle if isWalking else None

	client['room'].send('pw', client['id'], puffle.id, puffle.type, puffle.subtype, int(isWalking), puffle.hat)

@PacketEventHandler.onXT('s', 'p#pufflewalkswap', WORLD_SERVER)
def handlePuffleSwap(client, puffle):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None: # Check for penguin in igloo too?
		return

	if client['puffleHandler'].walkingPuffle is None:
		return # You can't just swap like that LOL

	if client['puffleHandler'].walkingPuffle.id == puffle.id:
		return # Shitty user

	client['puffleHandler'].walkingPuffle.walking = 0 
	client['puffleHandler'].walkingPuffle.save()

	puffle.walking = 1
	puffle.save()

	client['puffleHandler'].walkingPuffle = puffle

	client['room'].send('pufflewalkswap', *map(int, [client['id'], puffle.id, puffle.type, puffle.subtype, puffle.walking, puffle.hat]))

@PacketEventHandler.onXT('s', 'p#puffletrick', WORLD_SERVER)
def handlePuffleTrick(client, trick):
	client['room'].send('puffletrick', int(client['id']), trick)

@PacketEventHandler.onXT('s', 'p#puffleswap', WORLD_SERVER)
def handlePuffleSwap(client, puffle, isBackyard):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None:
		return

	if (isBackyard and bool(puffle.backyard)) or (not backyard and not bool(puffle.backyard)): # Check if player is in igloo?
		return #CRAZY!

	if bool(puffle.walking):
		puffle.walking = 0
		client['puffleHandler'].walkingPuffle = None

	puffle.backyard = isBackyard
	puffle.save()

	client['room'].send('puffleswap', int(puffle.id), 'backyard' if isBackyard else 'igloo')

@PacketEventHandler.onXT('s', 'p#pgpi', WORLD_SERVER, p_r = False)
def handlePuffleCareInventory(client, data):
	client.send('pgpi', client.dbpenguin.care)

@PacketEventHandler.onXT('s', 'p#papi', WORLD_SERVER)
def handleAddPuffleItem(client, _id):
	if _id not in client.engine.puffleCrumbs.puffleItems:
		return client.send('e', 402)

	item_details = client.engine.puffleCrumbs.puffleItems[_id]

	cost = int(item_details['cost'])
	is_member = bool(int(item_details['is_member_only']))
	quantity = int(item_details[quantity])

	if is_member and not client['member']:
		return client.send('e', 999)
	if cost > int(client['coins']):
		return client.send('e', 401)

	client['coins'] -= cost

	item = client['puffleHandler'].getPuffleItem(_id)
	if item is None:
		item = (_id, 0)
		client['puffleHandler'].append(item)

	index = client['puffleHandler'].inventory.index(item)
	client['puffleHandler'].inventory[index][1] += quantity

	client.dbpenguin.care = '%'.join(map(lambda x: '|'.join(map(str, x)), client['puffleHandler'].inventory))
	client.dbpenguin.save()

	client.send('papi', client['coins'], _id, quantity)

@PacketEventHandler.onXT('s', 'p#phg', WORLD_SERVER, p_r = False)
def handleGetStatus(client, data):
	client.send('phg', int(client['puffleHandler'] is not None))

@PacketEventHandler.onXT('s', 'p#puphi', WORLD_SERVER)
def handleHatUpdate(client, puffle, hat):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	item = client['puffleHandler'].getPuffleItem(hat)
	if item is None or puffle is None:
		return

	index = client['puffleHandler'].inventory.index(item)
	available_quantity = client['puffleHandler'].inventory[item][1]

	if available_quantity < 1:
		return

	hat_prev = puffle.hat
	if hat_prev != 0:
		index = client['puffleHandler'].inventory.index(hat_prev)
		client['puffleHandler'].inventory[item][1] += 1

	client['puffleHandler'].inventory[item][1] -= 1
	puffle.hat = hat

	client.dbpenguin.care = '%'.join(map(lambda x: '|'.join(map(str, x)), client['puffleHandler'].inventory))
	client.dbpenguin.save()

	client['room'].send('puphi', int(puffle.id), hat)

@PacketEventHandler.onXT('s', 'p#pcn', WORLD_SERVER, p_r = False)
def handlePuffleCheckName(client, data):
	client.send('pcn', data[2][0]) # TODO

@PacketEventHandler.onXT('s', 'p#checkpufflename', WORLD_SERVER, p_r = False)
def handleCheckPuffleName(client, data):
	name = data[2][0].strip()
	n_w_s = name.replace(' ', '')

	check = 1

	if not n_w_s.isalnum() or not (4 < len(name) < 21):
		check = 0

	client.send('checkpufflename', name, check)
	return bool(check)

@PacketEventHandler.onXT('s', 'p#pn', WORLD_SERVER)
@inlineCallbacks
def handleAdopt(client, _type, name, sub_type):
	if not handleCheckPuffleName(client, [0, 0, [name]]):
		return

	puffle = client.engine.puffleCrumbs[sub_type]
	if puffle is None:
		returnValue(None)

	cost = 800
	if sub_type in client.engine.puffleCrumbs.defautPuffles:
		cost = 400

	if puffle.member and not client['member']:
		returnValue(client.send('e', 999))

	now = int(time())
	care = '{"food" : {now},"play" : {now},"bath" : {now}}'.replace('{now}', str(now))
	puffle_db = yield Puffle(owner = client['id'], name = name, type = _type, subtype = sub_type, food = puffle.hunger, play = 100, rest = puffle.rest, clean = puffle.health, lastcare = care).save()
	yield puffle_db.refresh()

	client['puffleHandler'].append(puffle_db)

	client['coins'] -= cost

	mail = yield Mail(to_user = client['id'], from_user = 0, type = 111, description = name).save()	
	client['mail'].refresh()

	client['puffleHandler'].append(puffle)

	client.send('pn', client['coins'], puffle_db)