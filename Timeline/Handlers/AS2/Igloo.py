from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Utils.Igloo import Igloo, PenguinIglooItem, PenguinFurnitureItem, PenguinFloorItem, PenguinLocationItem
from Timeline.Server.Room import Igloo as IglooRoom

from Timeline.Handlers.Igloo import handleBuyFurniture, handleBuyFloor, handleBuyIgloo

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time

@PacketEventHandler.onXT_AS2('s', 'g#gm', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerIgloo(client, _id):
	iglooRoom = yield client['iglooHandler'].createPenguinIgloo(_id)
	if iglooRoom == None:
		return

	igloo = yield Igloo.find(iglooRoom._id)

	#player_id % igloo_type % music_id % floor_id % furniture_list(,)
	client.send('gm', _id, igloo.type, igloo.music, igloo.floor, igloo.furniture)

@PacketEventHandler.onXT_AS2('s', 'g#gr', WORLD_SERVER, p_r = False)
def handleGetOpenIgloos(client, data):
	openIgloos = [client.engine.getPenguinById(i.owner) for i in client.engine.iglooCrumbs.penguinIgloos if i.owner != client['id'] and client.engine.getPenguinById(i.owner) is not None]
	if len(openIgloos) < 1:
		return client.send('%xt%gr%-1%')

	# Sorts the penguins alphabatically acc to their nickname
	igloos = sorted(openIgloos, lambda x, y: 1 - 2 * int(str(x['nickname']) < str(y['nickname'])) if str(x['nickname']) != str(y['nickname']) else 0)
	openIgloos = map(lambda p: '{}|{}'.format(p['id'], p['nickname']), igloos)

	client.send('gr', *openIgloos)

@PacketEventHandler.onXT_AS2('s', 'g#go', WORLD_SERVER, p_r = False)
def handleGetPlayerIgloos(client, data):
	client.send('go', '|'.join(map(str, client['iglooHandler'].igloos)))

@PacketEventHandler.onXT_AS2('s', 'g#af', WORLD_SERVER)
def handleBuyFurnitureAS2(client, _id):
	handleBuyFurniture(client, _id)

@PacketEventHandler.onXT_AS2('s', 'g#ag', WORLD_SERVER)
def handleBuyFloorAS2(client, _id):
	handleBuyFloor(client, _id)

@PacketEventHandler.onXT_AS2('s', 'g#au', WORLD_SERVER)
def handleBuyIglooAS2(client, _id):
	handleBuyIgloo(client, _id)

@PacketEventHandler.onXT_AS2('s', 'g#gf', WORLD_SERVER, p_r = False)
def handleGetFurnitires(client, data):
	client.send('gf', *(map(lambda f: '{}|{}'.format(int(f), f.quantity), client['iglooHandler'].furnitures)))

@PacketEventHandler.onXT_AS2('s', 'g#um', WORLD_SERVER)
def handleActivateIgloo(client, music):
	if client['iglooHandler'].currentIgloo is None:
		return

	client['iglooHandler'].currentIgloo.music = music
	client['iglooHandler'].currentIgloo.save()

@PacketEventHandler.onXT_AS2('s', 'g#ao', WORLD_SERVER)
def handleSetIgloo(client, igloo):
	if client['iglooHandler'].currentIgloo is None or not client['iglooHandler'].hasIgloo(igloo):
		return

	client['iglooHandler'].currentIgloo.type = igloo
	client['iglooHandler'].currentIgloo.save()

@PacketEventHandler.onXT_AS2('s', 'g#ur', WORLD_SERVER)
def handleSaveFurnitureConfiguration(client, furns):
	furniture_string = ','.join(map(lambda x: '|'.join(map(str, x)), furnitures))
	fbyid = {}
	for f in furnitures:
		furn = f[0]

		if not client['iglooHandler'].hasFurniture(furn):
			return

		fbyid[furn] = fbyid[furn] + 1 if furn in fbyid else 1

		if fbyid[furn] > client['iglooHandler'].getFurniture(furn).max or fbyid[furn] > client['iglooHandler'].getFurniture(furn).quantity:
			return

	client['iglooHandler'].currentIgloo.furniture = furniture_string
	yield client['iglooHandler'].currentIgloo.save()

@PacketEventHandler.onXT_AS2('s', 'g#cr', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'g#or', WORLD_SERVER, p_r = False)
def handleLockAndOpenIgloo(client, data):
	client['iglooHandler'].currentIgloo.locked = int(data[1][-2] == 'c')