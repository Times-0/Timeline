from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, DIGGABLES, GOLD_DIGGABLES, DIGGABLE_FURN, GOLD_DIGGABLE_FURN
from Timeline.Utils.Puffle import Puffle
from Timeline.Utils.Mails import Mail
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Igloo import handleBuyFurniture
from Timeline.Handlers.Item import handleGetCurrencies

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time
from random import choice, randint, shuffle

PENDING = {}

@GeneralEvent.on('onClientDisconnect')
def handleMakePuffleHomeAlone(client):
	if client['puffleHandler'] is not None:
		for puffle in client['puffleHandler']:
			puffle.walking = 0
			puffle.save()

@PacketEventHandler.onXT('s', 'p#getdigcooldown', WORLD_SERVER, p_r = False)
def handleGetDigCoolDown(client, data):
	if client['puffleHandler'].walkingPuffle is None:
		return

	cmd = max(0, 120 - int(time() - client['lastDig']))
	client.send('getdigcooldown', cmd)

@PacketEventHandler.onXT('s', 'p#revealgoldpuffle', WORLD_SERVER, p_r = False)
def handleCanRevealGP(client, data):
	if client['canAdoptGold']:
		client.send('revealgoldpuffle', client['id'])

@PacketEventHandler.onXT('s', 'p#puffledigoncommand', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT('s', 'p#puffledig', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handlePuffleDig(client, data):
	if client['puffleHandler'].walkingPuffle is None:
		return

	cmd = data[1]
	lDC = 'lastDig'
	if 'oncommand' in cmd:
		lDC += 'OC'
	lastDig = client[lDC]

	cmd = max(0, (40 if 'oncommand' not in cmd else 120) - int(time() - client[lDC]))
	if cmd:
		returnValue(0) # no dig

	digables = range(5)
	setattr(client.penguin, lDC, time())

	digChances = list()
	canDigGold = client['puffleHandler'].walkingPuffle.state == 1
	for i in digables:
		if i is 4 and not canDigGold:
			continue

		elif i is 1 and canDigGold:
			continue

		chance = randint(0, 3 + 4 * int(canDigGold and i is 'gold'))
		digChances += [i for _ in range(chance)]

	dig = choice(digChances)

	if dig == 0:
		coinsDug = int(10 * randint(1, 40))
		client['coins'] += coinsDug

		returnValue(client['room'].send('puffledig', client['id'], client['puffleHandler'].walkingPuffle.id, 0, 0, coinsDug, 0, 0))

	elif dig == 1:
		returnValue(client['room'].send('nodig', client['id'], 1))

	elif dig == 2:
		diggables = DIGGABLE_FURN
		if client['puffleHandler'].walkingPuffle.id == 11:
			diggables += GOLD_DIGGABLE_FURN

		shuffle(diggables)
		for dug in diggables:
			tryDigging = yield handleBuyFurniture(client, dug, False)
			if tryDigging is True:
				returnValue(client['room'].send('puffledig', client['id'], client['puffleHandler'].walkingPuffle.id, 2, dug, 1, 0, 0))

		client['coins'] += 600
		returnValue(client['room'].send('puffledig', client['id'], client['puffleHandler'].walkingPuffle.id, 0, 0, 600, 0, 0))

	elif dig == 3:
		diggables = DIGGABLES
		if client['puffleHandler'].walkingPuffle.id == 11:
			diggables += GOLD_DIGGABLES

		shuffle(diggables)
		for dug in diggables:
			if dug not in client['inventory']:
				client['inventory'].append(dug)

				returnValue(client['room'].send('puffledig', client['id'], client['puffleHandler'].walkingPuffle.id, 3, dug, 1, 0, 0))

		client['coins'] += 500
		returnValue(client['room'].send('puffledig', client['id'], client['puffleHandler'].walkingPuffle.id, 0, 0, 500, 0, 0))

	elif dig == 4:
		dug = randint(1, 3)
		client['currencyHandler'].currencies[1] += dug
		client['currencyHandler'].refreshCurrencies()
		handleGetCurrencies(client, [-1, '', []])

		if client['currencyHandler'].currencies[1] > 14:
			client.penguin.canAdoptGold = True

		returnValue(client['room'].send('puffledig', client['id'], client['puffleHandler'].walkingPuffle.id, 4, 0, dug, 0, 0))


@PacketEventHandler.onXT('s', 'p#pg', WORLD_SERVER)
@inlineCallbacks
def handleGetPuffles(client, _id, isBackyard):
	client['puffleHandler'].refreshPuffleHealth()
	puffles = yield client['puffleHandler'].getPenguinPuffles(_id, isBackyard)

	if puffles is None:
		returnValue(None)

	client.send('pg', len(puffles.split('%')), puffles)

@PacketEventHandler.onXT('s', 'p#pgmps', WORLD_SERVER, p_r = False)
def handleGetMyPuffle(client, data):
	client['puffleHandler'].refreshPuffleHealth()
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
		client['puffleHandler'].walkingPuffle.state = 0
		client['puffleHandler'].walkingPuffle.save()

		client['currencyHandler'].currencies[1] = 0
		client['currencyHandler'].refreshCurrencies()
		client.penguin.canAdoptGold = False

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
	client['puffleHandler'].walkingPuffle.state = 0
	client['puffleHandler'].walkingPuffle.save()

	puffle.walking = 1
	puffle.save()

	client['currencyHandler'].currencies[1] = 0
	client['currencyHandler'].refreshCurrencies()
	client.penguin.canAdoptGold = False

	client['puffleHandler'].walkingPuffle = puffle

	client['room'].send('pufflewalkswap', *map(int, [client['id'], puffle.id, puffle.type, puffle.subtype, puffle.walking, puffle.hat]))

@PacketEventHandler.onXT('s', 'p#puffletrick', WORLD_SERVER)
def handlePuffleTrick(client, trick):
	client['room'].send('puffletrick', int(client['id']), trick)

@PacketEventHandler.onXT('s', 'p#puffleswap', WORLD_SERVER)
def handlePuffleSwapIB(client, puffle, isBackyard):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None:
		return

	if (isBackyard and bool(puffle.backyard)) or (not isBackyard and not bool(puffle.backyard)): # Check if player is in igloo?
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

	if not n_w_s.isalnum() or not (3 < len(name) < 21):
		check = 0

	if client['id'] in PENDING:
		print PENDING
		check = name not in PENDING[client['id']]

	for puffle in client['puffleHandler']:
		if puffle.name == name:
			check = 0
			break

	client.send('checkpufflename', name, check)
	return bool(check)

@PacketEventHandler.onXT('s', 'p#pn', WORLD_SERVER)
@inlineCallbacks
def handleAdopt(client, _type, name, sub_type):
	if not handleCheckPuffleName(client, [0, 0, [name]]):
		return

	if not client['id'] in PENDING:
		PENDING[client['id']] = []

	PENDING[client['id']].append(name)

	puffle = client.engine.puffleCrumbs[sub_type]
	if puffle is None or (_type == 10 and not client['canAdoptRainbow']) or (_type == 11 and not client['canAdoptGold']):
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
	PENDING[client['id']].remove(name)

@PacketEventHandler.onXT('s', 'p#ps', WORLD_SERVER)
def handlePuffleFrame(client, puffle, frame):
	peng = client['room'].owner #Check player in igloo

	# Maybe check for puffle in igloo too?
	client['room'].send('ps', puffle, frame)

@PacketEventHandler.onXT('s', 'p#pm', WORLD_SERVER)
@inlineCallbacks
def handlePuffleMove(client, puffle, x, y):
	peng = client['room'].owner
	peng = client.engine.getPenguinById(peng)

	if peng is not None:
		if peng['puffleHandler'] is not None:
			puffle_db = peng['puffleHandler'].getPuffleById(puffle)
			if puffle_db is None:
				returnValue(None)

			puffle_db.x, puffle_db.y = x, y
			client.engine.redis.server.hmset("puffle:{}".format(puffle), {'x' : x, 'y' : y})
			client['room'].send('pm', puffle, x, y)

	else:
		# Check if puffle in igloo
		puffle_db = yield Puffle.find(where = ['id = ? AND owner = ? AND walking = 0', puffle, client['room'].owner], limit = 1)
		if puffle_db is None:
			returnValue(None)

		client['room'].send('pm', puffle, x, y)
		client.engine.redis.server.hmset("puffle:{}".format(puffle), {'x' : x, 'y' : y})

@PacketEventHandler.onXT('s', 'p#pb', WORLD_SERVER)
def handlePuffleBath(client, puffle):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None:
		return

	max_rest = int(client.engine.puffleCrumbs.defautPuffles[int(puffle.type)][2])

	puffle.rest = (puffle.rest * max_rest + 5)/max_rest * 100
	if puffle.rest > 100:
		puffle.rest = max_rest

	puffle.clean = int(client.engine.puffleCrumbs.defautPuffles[int(puffle.type)][0])
	puffle.save()

	client['room'].send('pb', client['id'], client['coins'], puffle, 100)

@PacketEventHandler.onXT('s', 'p#pp', WORLD_SERVER)
def handlePufflePlay(client, puffle):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None:
		return

	health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[int(puffle.type)])

	if puffle.rest < 10 or puffle.clean < 10 or puffle.food < 10:
		return

	rx = choice(range(10, rest-10))
	cx = choice(range(0, health - 10))
	fx = choice(range(10, hunger))

	PX = chocie(range(10, 100))

	puffle.rest = max(0, int(puffle.rest)*rest - rx)/rest * 100
	puffle.clean = max(0, int(puffle.clean)*health - cx)/health * 100
	puffle.food = max(0, int(puffle.food)*hunger - fx)/hunger * 100
	puffle.play = min(100, int(puffle.play) + PX)

	puffle.save()

	client['room'].send('pp', client['id'], puffle, 27) #TODO: Play type

@PacketEventHandler.onXT('s', 'p#pr', WORLD_SERVER)
def handlePuffleRest(client, puffle):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None:
		return

	health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[int(puffle.type)])

	if puffle.rest < 10 or puffle.clean < 10 or puffle.food < 10:
		return

	cx = choice(range(0, health - 10))
	fx = choice(range(10, 30))


	puffle.rest = rest
	puffle.clean = max(0, int(puffle.clean)*health - cx) / health * 100
	puffle.food = max(0, int(puffle.food)*hunger - fx) / hunger * 100
	puffle.play = min(0, int(puffle.play) - 10)

	puffle.save()

	client['room'].send('pr', client['id'], puffle)

@PacketEventHandler.onXT('s', 'p#pf', WORLD_SERVER)
def handlePuffleFeed(client, puffle):
	pass

@PacketEventHandler.onXT('s', 'p#pcid', WORLD_SERVER)
def handlePuffleCareItemDelivered(client, puffle, cid):
	puffle = client['puffleHandler'].getPuffleById(puffle)
	if puffle is None:
		return
	
	_type_ = int(puffle.type)
	if _type_ > 9:
		_type_ = 0
		
	health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[_type_])
	if cid not in client.engine.puffleCrumbs.puffleItems:
		return client.send('e', 402)

	item_details = client.engine.puffleCrumbs.puffleItems[cid]

	only_purchase = bool(item_details['only_purchase'])
	is_member = bool(int(item_details['is_member_only']))

	if is_member and not client['member']:
		return

	if only_purchase:
		item = client['puffleHandler'].getPuffleItem(cid)
		if item is None:
			return

		available_quantity = client['puffleHandler'].inventory[item][1]

		if available_quantity < 1:
			return

	is_food = item_details['consumption'] != 'none'
	if is_food:
		client['room'].send('carestationmenuchoice', client['id'], puffle.id)

	if cid == 126:
		client['room'].send('oberry', client['id'], puffle.id)
		puffle.state = 1

	fx, rx, px, cx = map(int, [item_details['effect'][k] for k in ['food', 'rest', 'play', 'clean'] ])
	puffle.food = min(hunger, puffle.food*hunger + fx)/hunger * 100
	puffle.clean = min(health, puffle.clean*health + cx)/health * 100
	puffle.rest = min(rest, puffle.rest*rest + rx)/rest * 100
	puffle.play = min(100, puffle.play + px)

	puffle.save()

	client['room'].send('pcid', client['id'], '|'.join(map(str, [puffle.id, puffle.food, puffle.play, puffle.rest, puffle.clean, int(all(x == 100 for x in [puffle.food, puffle.clean, puffle.rest, puffle.play]))])))