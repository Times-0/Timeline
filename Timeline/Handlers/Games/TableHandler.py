from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

class TableGame(Multiplayer):

	table = None
	room = None # The base room where this game is attached to

	def __init__(self, *a, **kw):
		super(TableGame, self).__init__(*a, **kw)

		self.Waddling = list()

	def updateTable(self):
		self.room.send('ut', self.table, len(self) + len(self.Waddling))

	def __contains__(self, client):
		return list.__contains__(self, client) or client in self.Waddling

	def leaveGame(self, client):
		try:
			del self[self.index(client)]
			super(TableGame, self).leaveGame(client)
		except:
			pass

	def joinGame(self, client):
		if not client in self.Waddling or list.__contains__(self, client):
			return
		
		self.Waddling.remove(client)

		client.penguin.playing = True
		client.penguin.waddling = False

		list.append(self, client)

		client.send('jz', self.index(client))
		self.send('uz', self.index(client), client['nickname'])

		try:
			super(TableGame, self).joinGame(client)
		except:
			pass

		self.updateTable()

	def remove(self, client):		
		if list.__contains__(self, client):
			self.leaveGame(client)

		elif client in self.Waddling:
			self.Waddling.remove(client)


		self.room.append(self)
		self.onRemove(client)

	def onAdd(self, client):
		self.room.append(client)

		# remove player from game, put it on waddling list
		del self[self.index(client)]
		self.Waddling.append(client)

		client.send('jt', self.table, self.Waddling.index(client))

		client.penguin.playing = False
		client.penguin.waddling = True

		client.penguin.room = self.room
		client.penguin.game = self

		self.updateTable()

	def onRemove(self, client):
		try:
			super(TableGame, self).onRemove(client)
		except:
			pass

		GeneralEvent('Table-Left-{}-{}'.format(client['id'], self.table), client, self)
		GeneralEvent('Table-Left-{}'.format(client['id']), client, self)
		GeneralEvent('Table-Left-{}'.format(self.table), client, self)

		client.penguin.playing = client.penguin.waddling = False
		client.penguin.game = None
		
		self.room.append(self)

		client.penguin.room = self.room # must
		client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'place' : self.room.ext_id})

		self.updateTable()

	def getBoard(self):
		return []

	def __str__(self):
		iterUsers = iter(self + self.Waddling)
		gameStr = [next(iterUsers, {'nickname':''})['nickname'], next(iterUsers, {'nickname':''})['nickname']]

		gameStr.append(','.join(map(str, sum(self.getBoard(), []))))

		return '%'.join(map(str, gameStr))

@PacketEventHandler.onXT('s', 'a#jt', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'a#jt', WORLD_SERVER, p_r = False)
def handleJoinToTable(client, data):
	table = int(data[2][0])

	if client['playing'] or client['waddling']:
		client.send('e', 200)
		if isinstance(client['room'], Game):
			client['room'].remove(client)
			for room in client['prevRooms'][::-1]: 
				if isinstance(room, Place): 
					room.append(client)
					break

		return Event('Leave-Waddling', client)

	Event('JoinTable-{}'.format(table), client, table)

@PacketEventHandler.onXT('s', 'a#lt', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'a#lt', WORLD_SERVER, p_r = False)
def handleLeave(client, data):
	if client['game'] is None:
		return

	table = client['game'].table
	Event('LeaveTable-{}'.format(table), client, table)

@Event.on('Leave-Waddling')
def LeaveWaddling(client):
	if client['playing']:
		client['game'].remove(client)
		client['game'] = None

	if client['waddling']:
		pass # TODO