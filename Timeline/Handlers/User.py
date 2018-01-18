from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo, Award
from Timeline.Database.DB import Penguin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'u#followpath', WORLD_SERVER)
def handlePlayerSliding(client, slide):
	client['room'].send('followpath', client['id'], slide)

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

@PacketEventHandler.onXT('s', 'u#se', WORLD_SERVER)
def handleSendEmote(client, emote):
	client['room'].send('se', client['id'], emote)

@PacketEventHandler.onXT('s', 'u#ss', WORLD_SERVER)
def handleSendSafeMsg(client, safe):
	# really necessary to check?
	client['room'].send('ss', client['id'], safe)

@PacketEventHandler.onXT('s', 'u#gp', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayer(client, _id):
	penguin = yield client.db_getPenguin('ID = ?', _id)
	if penguin is None:
		returnValue(0)

	client.send('gp', '|'.join(map(str, [_id, penguin.nickname, 45, penguin.color, penguin.head, penguin.face, penguin.neck, penguin.body, penguin.hand, penguin.feet, penguin.pin, penguin.photo])))

@PacketEventHandler.onXT('s', 'u#pbs', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetPlayerBySWID(client, data):
	swid = str(data[2][0])
	penguin = yield client.db_getPenguin('swid = ?', swid)
	if penguin is None:
		returnValue(0)

	client.send('pbs', penguin.username, penguin.id)

@PacketEventHandler.onXT('s', 'u#sp', WORLD_SERVER)
def handleSendCoordinates(client, x, y):
	client.penguin.x, client.penguin.y = x, y
	client['room'].send('sp', client['id'], x, y)

@PacketEventHandler.onXT('s', 'u#sb', WORLD_SERVER)
def handleSnowBall(client, x, y):
	client['room'].send('sb', client['id'], x, y)

@PacketEventHandler.onXT('s', 'u#bf', WORLD_SERVER)
def handle(client, _id):
	# check if id is friend
	# check if id is online
	# check if id is moderator
	# and more...
	pass

@PacketEventHandler.onXT('s', 'u#pbsu', WORLD_SERVER)
@inlineCallbacks
def handleGetUsernames(client, swid):
	usernames = list()
	for s in swid:
		user = yield Penguin.find(where = ['swid = ?', s], limit = 1)
		if user is None:
			usernames.append('')
		else:
			usernames.append(str(user.nickname))

	client.send('pbsu', ','.join(usernames))

@PacketEventHandler.onXT('s', 'u#h', WORLD_SERVER, p_r = False)
def handleHeartBeat(client, data):
	client.send('h', 'pong')

@PacketEventHandler.onXT('s', 's#upc', WORLD_SERVER)
def handleUpdateColor(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
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
def handleUpdateHead(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.head = _id
		name = Head.__name__.lower()
		client.penguin.head = Head(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('uph', int(client['id']), _id)

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
def handleUpdateFace(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.face = _id
		name = Face.__name__.lower()
		client.penguin.face = Face(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upf', int(client['id']), _id)

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
def handleUpdateNeck(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.neck = _id
		name = Neck.__name__.lower()
		client.penguin.neck = Neck(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upn', int(client['id']), _id)

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
def handleUpdateBody(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.body = _id
		name = Body.__name__.lower()
		client.penguin.body = Body(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upb', int(client['id']), _id)

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
def handleUpdateHand(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.hand = _id
		name = Hand.__name__.lower()
		client.penguin.hand = Hand(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upa', int(client['id']), _id)

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
def handleUpdateFeet(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.feet = _id
		name = Feet.__name__.lower()
		client.penguin.feet = Feet(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upe', int(client['id']), _id)

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
def handleUpdatePhoto(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	print "Photo:", _id
	if _id == 0:
		client.dbpenguin.photo = _id
		name = Photo.__name__.lower()
		client.penguin.photo = Photo(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upp', int(client['id']), _id)

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
def handleUpdateFlag(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
	if _id == 0:
		client.dbpenguin.pin = _id
		name = Pin.__name__.lower()
		client.penguin.pin = Pin(0, 0, name + " item", False, False, False)
		client.dbpenguin.save()

		return client['room'].send('upl', int(client['id']), _id)

	item = client.engine.itemCrumbs[_id]
	if not _id in client['inventory'] or item == False:
		return

	if item.type is not Pin.type:
		return # suspecius? Log it, probably?

	if item.is_member and not client['member']:
		return client.send('e', 999)

	if item.is_bait and not client['moderator']:
		return # raise issue, ban the player? :P

	if item.is_epf and not client['epf']:
		return # shit on him!

	client.penguin.pin = item
	client.dbpenguin.pin = int(item)

	client['room'].send('upl', int(client['id']), int(item))

	client.dbpenguin.save()
