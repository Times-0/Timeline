from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.WaddleHandler import Waddle

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

from collections import deque
import logging
from time import time
from random import choice, shuffle, sample

logger = logging.getLogger(TIMELINE_LOGGER)

SLED_TRACKS = {100:4, 101:3, 102:2, 103:2}

class SledRacingGame(Multiplayer):
	waddle = -1 # Waddle id

	def __init__(self, rh):
		super(SledRacingGame, self).__init__(rh, 999, "Sled", "Game: Sled Racing", 4, False, False, None)
		self.Playing = [None, None, None, None]
		self.GameStarted = False

	def gameOver(self, playerLeft = None, client = None):
		self.GameStarted = False

		if playerLeft is not None:
			self.send('cz', playerLeft['nickname'])
			for u in list(self):
				self.remove(u)
				self.room.append(u)

			return

		client['coins'] += 10 + client['isFirst'] * 50
		client.send('zo', client['coins'])
		
		if client in self: self.remove(client)

	def checkForFirstPlace(self):
		firstPlace, leastTime = self[0], self[0]['time']

		for i in list(self):
			if i['time'] < leastTime:
				leastTime = i['time']
				firstPlace = i

			i.penguin.isFirst = False

		firstPlace.penguin.isFirst = True


	def play(self, client, param):
		seat, x, y, time = map(int, param)
		if seat != client['game_index']:
			return

		client.penguin.time = time
		self.send('zm', seat, x, y, time)
		self.checkForFirstPlace()

	def onAdd(self, client):
		client.penguin.game = self
		client.penguin.room = self
		client.penguin.waddling = False
		client.penguin.playing = True
		client.penguin.time = 0

	def joinGame(self, client):
		if client not in self:
			return

		client.penguin.game = client.penguin.room = self
		client.penguin.isFirst = False

		self.Playing[client['game_index']] = client
		client.send('jz', client['game_index'], client['nickname'], client['color'], user['tube'])
		self.updateGame()

		if None not in self.Playing[:SLED_TRACKS[self.waddle]]:
			self.startGame()

	def startGame(self):
		if self.GameStarted:
			return

		self.GameStarted = True
		self.send('sz', 'Sled')


	def updateGame(self):
		uzString = list()
		for i in range(SLED_TRACKS[self.waddle]):
			user = self.Playing[i]
			if user is None:
				continue
			# seat|nickname|peng_color|belt
			uzString.append('|'.join(map(str, [user['nickname'], user['color'], user['tube'], user['nickname']])))

		self.send('uz', len(uzString), '%'.join(uzString))

	def getGame(self, client):
		client.send('gz', self)

	def __str__(self):
		return '{}%{}'.format(SLED_TRACKS[self.waddle], len([k for k in self.Playing if k is not None]))

	def onRemove(self, client):
		client.penguin.time = client.penguin.game_index = client.penguin.game = None
		client.penguin.isFirst = client.penguin.waddling = client.penguin.playing = False

		if self.GameStarted:
			self.gameOver(client)



class SledTrack(Waddle):
	stamp = -1 # no stamps
	room = None
	game = SledRacingGame

	waddles = 2 # No of players waddling.
	waddle = None # waddle id

	def __init__(self, *a, **kw):
		super(SledTrack, self).__init__(*a, **kw)

		self.room = self.roomHandler.getRoomByExtId(230)

	def startWaddle(self):
		clients = list(self)
		for i in clients:
			i.penguin.game_index = clients.index(i)

		super(SledTrack, self).startWaddle()