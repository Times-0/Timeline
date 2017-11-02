from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo, Award

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'u#pbi', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerById(client, _id):
	penguin = yield client.db_getPenguin('ID = ?', _id)
	if penguin is None:
		returnValue(0)

	client.send('pbi', penguin.swid, _id, penguin.nickname)

@PacketEventHandler.onXT('s', 'u#sf', WORLD_SERVER)
def handleSendFrame(client, frame):
	#TODO Check frame
	client.penguin.frame = frame
	client['room'].send('sf', client['id'], client['frame'])

@PacketEventHandler.onXT('s', 'u#sa', WORLD_SERVER)
def handleSendAction(client, action):
	client['room'].send('sf', client['id'], action)

@PacketEventHandler.onXT('s', 'u#u#se', WORLD_SERVER)
def handleSendEmote(client, emote):
	client['room'].send('se', client['id'], emote)

@PacketEventHandler.onXT('s', 'u#ss', WORLD_SERVER)
def handleSendSafeMsg(client, safe):
	# really necessary to check?
	client['room'].send('ss', client['id'], safe)

@PacketEventHandler.onXT('s', 'u#gp', WORLD_SERVER)
def handleGetPlayer(client, _id):
	penguin = yield client.db_getPenguin('ID = ?', _id)
	if penguin is None:
		returnValue(0)

	client.send('gp', _id, penguin.nickname, penguin.color, penguin.head, penguin.face, penguin.neck, penguin.body, penguin.hand, penguin.feet, penguin.pin, penguin.photo)

@PacketEventHandler.onXT('s', 'u#bf', WORLD_SERVER)
def handle(client, _id):
	# check if id is friend
	# check if id is online
	# check if id is moderator
	# and more...
	pass

@PacketEventHandler.onXT('s', 'u#h', WORLD_SERVER, p_r = False)
def handleHeartBeat(client, data):
	client.send('u#h', 'pong')

@PacketEventHandler.onXT('s', 's#upc', WORLD_SERVER)
def handleUpdateColor(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Color.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.color = item
	client.dbpenguin.color = int(item)

	client['room'].send('upc', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#uph', WORLD_SERVER)
def handleUpdateHead(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Head.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.head = item
	client.dbpenguin.head = int(item)

	client['room'].send('uph', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upf', WORLD_SERVER)
def handleUpdateFace(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Face.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.face = item
	client.dbpenguin.face = int(item)

	client['room'].send('upf', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upn', WORLD_SERVER)
def handleUpdateNeck(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Neck.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.neck = item
	client.dbpenguin.neck = int(item)

	client['room'].send('upn', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upb', WORLD_SERVER)
def handleUpdateBody(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Body.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.body = item
	client.dbpenguin.body = int(item)

	client['room'].send('upb', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upa', WORLD_SERVER)
def handleUpdateHand(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Hand.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.hand = item
	client.dbpenguin.hand = int(item)

	client['room'].send('upa', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upe', WORLD_SERVER)
def handleUpdateFeet(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Feet.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.feet = item
	client.dbpenguin.feet = int(item)

	client['room'].send('upe', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upp', WORLD_SERVER)
def handleUpdatePhoto(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Photo.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.photo = item
	client.dbpenguin.photo = int(item)

	client['room'].send('upp', int(client['id']), int(item))

	client.dbpenguin.save()

@PacketEventHandler.onXT('s', 's#upl', WORLD_SERVER)
def handleUpdateFlag(client, _id):
	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Flag.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.flag = item
	client.dbpenguin.flag = int(item)

	client['room'].send('upl', int(client['id']), int(item))

	client.dbpenguin.save()
