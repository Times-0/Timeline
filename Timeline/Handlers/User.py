from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award

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