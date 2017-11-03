from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Utils.Igloo import Igloo, PenguinIglooItem, PenguinFurnitureItem, PenguinFloorItem, PenguinLocationItem
from Timeline.Server.Room import Igloo as IglooRoom

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time

@PacketEventHandler.onXT('s', 'g#gm', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerIgloo(client, _id):
	iglooRoom = yield client['iglooHandler'].createPenguinIgloo(_id)
	if iglooRoom == None:
		return

	igloo = yield Igloo.find(iglooRoom._id)
	likes = 0
	if igloo.likes != '' and igloo.likes != None:
		j = json.loads(igloo.likes)
		for i in j:
			likes += i['count']

	details = [igloo.id, 1, 0, int(bool(igloo.locked)), igloo.music, igloo.floor, igloo.location, igloo.type, likes, igloo.furniture]

	client.send('gm', _id, ':'.join(map(str, details)))

@PacketEventHandler.onXT('s', 'g#aloc', WORLD_SERVER)
@inlineCallbacks
def handleBuyLocation(client, _id):
	location = client.engine.iglooCrumbs.getLocationById(_id)
	if location is None:
		returnValue(client.send('e', 402))

	if client['iglooHandler'].hasLocation(_id):
		returnValue(client.send('e', 400))

	if client['coins'] + 1 < location.cost:
		returnValue(client.send('e', 401))

	item = PenguinLocationItem(location.id, location.name, location.cost)
	item.date = int(time())

	client['iglooHandler'].locations.append(item)
	client.dbpenguin.locations = ','.join(map(lambda x: '|'.join(map(str, [x.id, x.date])), client['iglooHandler'].locations))
	yield client.dbpenguin.save()

	client['coins'] -= location.cost
	client.send('aloc', _id, client['coins'])


@PacketEventHandler.onXT('s', 'g#gail', WORLD_SERVER)
@inlineCallbacks
def getIglooLayoutList(client, _id):
	if not isinstance(client['room'], IglooRoom) or not _id == (client['room'].ext_id - 1000):
		returnValue(None)

	iglooLayouts = list()
	igloos = yield Igloo.find(where = ['owner = ?', _id])

	total_likes = 0
	igloo_likes = list()

	ix = 0

	for i in igloos:
		locked = True
		ix += 1
		if i.id == client['igloo']._id:
			locked = i.locked

		likes = 0
		for j in json.loads(i.likes):
			likes += j['count']

		total_likes += likes

		details = [i.id, ix, 0, locked, i.music, i.floor, i.location, i.type, likes, i.furniture]
		iglooLayouts.append(':'.join(map(str, details)))
		igloo_likes.append('|'.join(map(str, [i.id, likes])))

	client.send('gail', _id, 0, *iglooLayouts)
	client.send('gaili', total_likes, ','.join(igloo_likes))

@PacketEventHandler.onXT('s', 'g#uic', WORLD_SERVER)
@inlineCallbacks
def updateIglooConfiguration(client, _id, _type, floor, location, music, furnitures):
	furniture_string = ','.join(map(lambda x: '|'.join(map(str, x))), furnitures)
	fbyid = {}
	for f in furnitures:
		furn = f[0]

		if not client['iglooHandler'].hasFurniture(furn):
			return

		if not furn in fbyid:
			fbyid[furn] = 0

		if fbyid[furn] + 1 > client['iglooHandler'].getFurniture(furn).max:
			return

	if not client['igloo']._id == _id:
		return # ban?

	if not client['iglooHandler'].hasFloor(floor) or not client['iglooHandler'].hasLocation(location) or not client['iglooHandler'].hasMusic(music):
		return

	igloo = client['iglooHandler'].currentIgloo
	igloo.type = _type
	igloo.floor = floor
	igloo.location = location
	igloo.music = music
	igloo.furniture = furniture

	yield igloo.save()

	details = [igloo.id, 1, 0, int(bool(igloo.locked)), igloo.music, igloo.floor, igloo.location, igloo.type, likes, igloo.furniture]
	client['igloo'].send('uvi', client['id'], ':'.join(map(str, details)))

@PacketEventHandler.onXT('s', 'g#af', WORLD_SERVER)
@inlineCallbacks
def handleBuyFurniture(client, _id):
	furniture = client.engine.iglooCrumbs.getFurnitureById(_id)
	if furniture is None:
		returnValue(client.send('e', 402))

	if furniture.is_member and not client['member']:
		returnValue(client.send('e', 999))

	quantity = 0
	furn = None
	if client.hasFurniture(_id):
		furn = client.getFurniture(_id)
		quantity = furn.quantity

	if quantity > 98:
		returnValue(client.send('e', 403))

	if client['cost'] + 1 < furniture.cost:
		returnValue(client.send('e', 401))

	if furn is None:
		furn = PenguinFurnitureItem(furniture.id, furniture.type, furniture.cost, furniture.name, furniture.is_member, furniture.max)
		furn.date = int(time())
		client['iglooHandler'].furnitures.append(furn)

	furn.quantity += 1
	client['coins'] -= furniture.cost

	client.dbpenguin.furnitures = ','.join(map(lambda x: '|'.join(map(str, [x.id, x.date, x.quantity])), client['iglooRoom'].furnitures))
	yield client.dbpenguin.save()

	client.send('af', _id, client['coins'])

@PacketEventHandler.onXT('s', 'g#ag', WORLD_SERVER)
@inlineCallbacks
def handleBuyFloor(client, _id):
	floor = client.engine.iglooCrumbs.getFloorById(_id)
	if floor is None:
		returnValue(client.send('e', 402))

	if client['iglooHandler'].hasFloor(_id):
		returnValue(client.send('e', 400))

	if client['coins'] + 1 < floor.cost:
		returnValue(client.send('e', 401))

	item = PenguinFloorItem(floor.id, floor.name, floor.cost)
	item.date = int(time())

	client['iglooHandler'].floors.append(item)
	client.dbpenguin.floors = ','.join(map(lambda x: '|'.join(map(str, [x.id, x.date])), client['iglooHandler'].floors))
	yield client.dbpenguin.save()

	client['coins'] -= floor.cost
	client.send('ag', _id, client['coins'])

@PacketEventHandler.onXT('s', 'g#au', WORLD_SERVER)
@inlineCallbacks
def handleBuyIgloo(client, _id):
	igloo = client.engine.iglooCrumbs.getIglooById(_id)
	if igloo is None:
		returnValue(client.send('e', 402))

	if client['iglooHandler'].hasIgloo(_id):
		returnValue(client.send('e', 500))

	if client['coins'] + 1 < igloo.cost:
		returnValue(client.send('e', 401))

	item = PenguinIglooItem(igloo.id, igloo.name, igloo.cost)
	item.date = int(time())

	client['iglooHandler'].igloos.append(item)
	client.dbpenguin.igloos = ','.join(map(lambda x: '|'.join(map(str, [x.id, x.date])), client['iglooHandler'].igloos))
	yield client.dbpenguin.save()

	client['coins'] -= igloo.cost
	client.send('au', _id, client['coins'])

@PacketEventHandler.onXT('s', 'g#al', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleAddLayout(client, data):
	igloos = yield Igloo.find(where = ['owner = ?', client['id']])
	if len(igloos) > 2:
		returnValue(None)

	igloo = yield Igloo(owner = client['id'], location = 1, furniture = '', likes = '[]').save()
	details = [igloo.id, len(igloos)+1, 0, int(bool(igloo.locked)), igloo.music, igloo.floor, igloo.location, igloo.type, likes, igloo.furniture]
	client.send('al', client['id'], ':'.join(map(str, details)))

@PacketEventHandler.onXT('s','g#pio', WORLD_SERVER)
@inlineCallbacks
def handleIsIglooOpen(client, _id):
	iglooRoom = yield client['iglooHandler'].createPenguinIgloo(_id)
	if iglooRoom == None:
		return

	igloo = yield Igloo.find(iglooRoom._id)
	client.send('pio', int(not bool(int(igloo.locked))))

@PacketEventHandler.onXT('s', 'g#cli', WORLD_SERVER)
@inlineCallbacks
def handleCanLike(client, _id):
	iglooRoom = yield client['iglooHandler'].createPenguinIgloo(_id)
	if iglooRoom == None:
		return

	igloo = yield Igloo.find(iglooRoom._id)
	likes = json.loads(igloo.likes)

	like_str = {'canLike' : True, 'periodicity' : 'ScheduleDaily', 'nextLike_msecs' : 0}
	now = int(time())

	for i in likes:
		if i['id'] != client['swid']:
			continue

		last_like = int(i['time'])
		span = last_like - 24*60*60
		if not span > 1:
			like_str['canLike'] = False
			like_str['nextLike_msecs'] = span * 1000

		break

	client.send('cli', int(igloo.id), 200, json.dumps(like_str))

@PacketEventHandler.onXT('s', 'g#uiss', WORLD_SERVER)
@inlineCallbacks
def handleUpdateIglooSlotSummary(client, _id, summary):
	if _id != client['igloo']._id:
		return

	for i in summary:
		_i = i[0]
		locked = int(bool(i[1]))

		igloo = yield Igloo.find(_i)
		igloo.locked = locked
		igloo.save()

	igloo = client['iglooHandler'].currentIgloo

	details = [igloo.id, 1, 0, int(bool(igloo.locked)), igloo.music, igloo.floor, igloo.location, igloo.type, likes, igloo.furniture]
	client['igloo'].send('uvi', client['id'], ':'.join(map(str, details)))

@PacketEventHandler.onXT('s', 'g#gr', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetOpenIgloos(client, data):
	open_igloos = list()

	for igloo in client.engine.iglooCrumbs.penguinIgloos:
		# pid|nickname|igloo_id
		if igloo.owner == client.id:
			open_igloos.append('|'.join(map(str, [int(penguin['id']), penguin['nickname'], _id])))
			continue

		if not igloo.opened:
			continue

		_id = igloo._id
		owner = igloo.owner

		penguin =  client.engine.getPenguinById(owner)
		if penguin is None:
			continue

		open_igloos.append('|'.join(map(str, [int(penguin['id']), penguin['nickname'], _id])))


	client.send('gr', *open_igloos)