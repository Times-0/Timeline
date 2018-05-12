from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer, Igloo

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

class Waddle(Multiplayer):
	stamp = None
	room = None
	game = None

	waddles = 2 # No of players waddling.
	waddle = None # waddle id

	def __init__(self, *a, **kw):
		super(Waddle, self).__init__(*a, **kw)

		self.logger = logging.getLogger(TIMELINE_LOGGER)
		if self.waddles < 2:
			self.waddles = 2 # must be atleast 2 for a multiplayer? LOL

	def updateWaddle(self, client = None):
		users = self[:self.waddles]
		if client is not None:
			self.room.send('uw', self.waddle, self.index(client), client['nickname'], client['id'])

		if len(users) >= self.waddles:
			self.startWaddle()

		try:
			super(Waddle, self).updateWaddle(client)
		except:
			pass

	def startWaddle(self):
		users = list(self[:self.waddles])
		if self.game is None:
			return # shit you!

		game = self.game(self.roomHandler)
		game.stamp_id = self.stamp
		game.room = self.room
		game.waddle = self.waddle
		for user in users:
			user['room'].remove(user)
			game.append(user)

			del self[self.index(user)]

		game.send('sw', game.ext_id, self.waddle, self.waddles)

		try:
			super(Waddle, self).startWaddle()
		except:
			pass

		self.updateWaddle()

	def remove(self, client):
		if not client in self:
			return

		self.send('rp', client['id'])
		client.penguin.waddling = False
		client.penguin.game = None
		client.penguin.game_index = None

		self.room.send('uw', self.waddle, self.index(client))

		client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'place' : self.room.ext_id})
		try:
			super(Waddle, self).remove(client)
		except:
			pass

		client.penguin['prevRooms'].append(self)

		try:
			self.onRemove(client)
		except:
			pass

		client.penguin.room = self.room


	# onAdd is complately overidden, if you want to extend onAdd, overload updateWaddle() instead
	def onAdd(self, client):
		client.penguin.waddling = True
		client.penguin.playing = False
		client.penguin.room = self.room
		client.penguin.game = self
		client.penguin.game_index = None

		client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'playing' : 0, 'waddling' : 1})

		client.send('jw', self.index(client))
		self.updateWaddle(client)

@GeneralEvent.on('Room-handler')
def setRoomHandler(ROOM_HANDLER):
	ROOM_HANDLER.ROOM_CONFIG.WADDLES = {}

@PacketEventHandler.onXT('z', 'jw', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'jw', WORLD_SERVER, p_r = False)
def handleJoinWaddling(client, data):
    wid = int(data[2][0])

    if client['waddling'] or client['game'] is not None:
        return client.send('e', 'Freak!')

    # find the waddable place
    WADDLES = client.engine.roomHandler.ROOM_CONFIG.WADDLES

    if isinstance(client['room'], Igloo):
        if not client['room'].id in WADDLES:
            return client.send('e', 'End Game!')

        WADDLES = {x.waddle : x for x in WADDLES[client['room'].id]}

    if wid not in WADDLES:
        return

    WADDLE_ROOM = WADDLES[wid]
    if not client['room'] is WADDLE_ROOM.room:
    	return client.send("e", "Santa' on the way!")

    WADDLE_ROOM.append(client) # JoinWaddle

@PacketEventHandler.onXT('z', 'lw', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'lw', WORLD_SERVER, p_r = False)
def handleLeaveWaddling(client, data):
    if not client['waddling'] or client['game'] is None or client['playing']:
        return

    client['game'].remove(client) #leaveWaddling

@PacketEventHandler.onXT('z', 'gw', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('z', 'gw', WORLD_SERVER, p_r = False)
def handleGetWaddling(client, data):
	waddle_ids = map(int, data[2])
	gw = list()
	WADDLES = client.engine.roomHandler.ROOM_CONFIG.WADDLES
	if isinstance(client['room'], Igloo):
		if not client['room'].id in WADDLES:
			return

		WADDLES = {x.waddle : x for x in WADDLES[client['room'].id]}

	for i in waddle_ids:
		if i not in WADDLES:
			gw.append('{}|'.format(i))
			continue

		WADDLE_ROOM = WADDLES[i]
		gwx = list()
		for ix in range(WADDLE_ROOM.waddles):
			if ix < len(WADDLE_ROOM):
				gwx.append(WADDLE_ROOM[ix]['nickname'])
			else:
				gwx.append('')
		gwx = ','.join(gwx)
		gw.append('{}|{}'.format(i, gwx))

	client.send('gw', '%'.join(gw))