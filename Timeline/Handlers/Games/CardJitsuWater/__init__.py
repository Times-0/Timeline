from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.WaddleHandler import Waddle
from Timeline.Handlers.Games.CardJitsu import Card

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

from collections import deque
import logging
from time import time
from random import choice, shuffle, sample, randint

logger = logging.getLogger(TIMELINE_LOGGER)

CJ_MATS = {300: 2, 301: 2, 302: 3, 303: 4}

class WaterCell(object):
	
	ELEMENT_FIRE = 0
	ELEMENT_WATER = 1
	ELEMENT_SNOW = 2
	ELEMENT_EMPTY = 3
	ELEMENT_OBSTACLE = 4

	ELEMENT_VALUE_MAX = 20

	def __init__(self, cell_id, _type, value):
		self.id = cell_id
		self.type = _type
		self.value = min(value, self.ELEMENT_VALUE_MAX) if self.type != self.ELEMENT_EMPTY else 0

		self.penguin = None

class WaterRow(object):

	MIN_BOARD_COLS = 5
	MAX_BOARD_COLS = 7

	def __init__(self, n_col, row_index):
		self.n_col = min(max(n_col, self.MIN_BOARD_COLS), MAX_BOARD_COLS)
		self.index = row_index

		self.cells = []
		self.generate_cells()

	def generate_cells(self):
		pass

class CardJitsuGame(Multiplayer):
	waddle = -1 # Waddle id
	MAX_BOARD_SPACES = 16

	MAX_BOARD_ROWS = 9
	CARD_AMOUNT = 7

	def __init__(self, rh):
		super(CardJitsuGame, self).__init__(rh, 995, "Fire", "Game: Card Jitsu Water", 4, False, False, None)
		self.Playing = [None, None, None, None]
		self.GameStarted = False

		self.GameCards = None
		self.GameDeck = None
		self.GameBoard = None

	def gameOver(self, playerLeft = None, cz = 1):			
		if playerLeft is not None:
			if playerLeft in self.Playing:
				i = self.Playing.index(playerLeft)
				playerLeft = self.Playing[i]
				print 'Meow'
			else:
				playerLeft.engine.roomHandler.joinRoom(playerLeft, 'dojowater', 'name')

			if len(self.Playing) < 2:
				self.gameOver()

			return

		print 'GO'

	def sendGameOver(self, removedPlayers):
		print 'GameOver'

	def play(self, client, param, tab = -1):
		if not self.GameStarted or client not in self.Playing:
			return client.send('e', 'ABCDE-ee-FU')

		move = param[0]
		client = self.Playing[self.Playing.index(client)]
		print 'zm', move

		return True
		

	def onAdd(self, client):
		client.penguin.game = self
		client.penguin.room = self
		client.penguin.waddling = False
		client.penguin.playing = True

	def joinGame(self, client):
		if client not in self:
			return

		client.penguin.game = client.penguin.room = self
		client.penguin.fire_rank = client.penguin.ir = None

		self.Playing[client['game_index']] = client
		client.send('jz', client['game_index'], client['nickname'], client['data'].avatar.color, client['ninjaHandler'].ninja.fire)
		self.updateGame()

		if None not in self.Playing[:CJ_MATS[self.waddle]]:
			self.startGame()

	def startGame(self):
		if self.GameStarted:
			return

		self.noPlaying = CJ_MATS[self.waddle]
		self.Playing = self[:self.noPlaying]

		self.GameStarted = True
		self.GameCards = [None] * self.noPlaying
		self.GameDeck = [None] * self.noPlaying

		self.sendStartGameMessage()
	
	def sendStartGameMessage(self):
		print "StartGame"


	def updateGame(self):
		uzString = list()
		for i in range(CJ_MATS[self.waddle]):
			user = self.Playing[i]
			if user is None:
				continue
			# seat|nickname|peng_color|belt
			uzString.append('|'.join(map(str, [i, user['nickname'], user['data'].avatar.color, user['ninjaHandler'].ninja.water])))

		self.send('uz', len(uzString), '%'.join(uzString))

	def getGame(self, client):
		client.send('gz', self)

		self.joinGame(client)

	def __str__(self):
		return '{}%{}'.format(CJ_MATS[self.waddle], len([k for k in self.Playing if k is not None]))

	def onRemove(self, client):
		client.penguin.game_index = client.penguin.game = client.penguin.room = None
		client.penguin.waddling = client.penguin.playing = False

		self.gameOver(client)


class CJMat(Waddle):
	stamp = 34
	room = None
	game = CardJitsuGame

	waddles = 2 # No of players waddling.
	waddle = None # waddle id

	def __init__(self, *a, **kw):
		super(CJMat, self).__init__(*a, **kw)

		self.room = self.roomHandler.getRoomByExtId(816)

	# CJMS
	def startWaddle(self):
		clients = list(self[:self.waddles])
		cjms = [0]*self.waddles*3 # no of players * 3

		for i in range(self.waddles):
			cjms[i + 0 * self.waddles] = clients[i]['data'].avatar.color
			cjms[i + 1 * self.waddles] = clients[i]['ninjaHandler'].ninja.belt
			cjms[i + 2 * self.waddles] = clients[i]['id']

		for c in clients:
			c.send('cjms', self.waddle, 995, -995, 2, *cjms)
			c.penguin.game_index = clients.index(c)

		super(CJMat, self).startWaddle()