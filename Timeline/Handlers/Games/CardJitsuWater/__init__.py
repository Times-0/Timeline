from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.WaddleHandler import Waddle
from Timeline.Handlers.Games.CardJitsu import Card

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor, task

from collections import deque
import logging
from time import time
from random import choice, shuffle, sample, randint
import math
import numpy as np

logger = logging.getLogger(TIMELINE_LOGGER)

CJ_MATS = {300: 2, 301: 2, 302: 3, 303: 4}

class WaterCard(Card):

	def __str__(self):
		return "{}-{}".format(self.id, self._index)

class WaterCell(object):
	
	ELEMENT_FIRE = 0
	ELEMENT_WATER = 1
	ELEMENT_SNOW = 2
	ELEMENT_EMPTY = 3
	ELEMENT_OBSTACLE = 4

	ELEMENT_VALUE_MAX = 20

	def __init__(self, cell_id, _type, value):
		self.id = cell_id
		self.type = _type if value != 0 else self.ELEMENT_EMPTY
		self.value = min(value, self.ELEMENT_VALUE_MAX) if self.type != self.ELEMENT_EMPTY else 0

		self.penguin = None

	def penguinJump(self, penguin):
		self.penguin = penguin
		self.type = self.ELEMENT_EMPTY
		self.penguin.penguin.water_cell = self

	def canJump(self):
		return self.type != self.ELEMENT_OBSTACLE and self.penguin is None

	def __str__(self):
		return "{}-{}-{}".format(self.id, self.type, self.value)

class WaterRow(object):

	MIN_BOARD_COLS = 5
	MAX_BOARD_COLS = 7

	def __init__(self, n_col, row_index, is_empty = False):
		self.n_col = min(max(n_col, self.MIN_BOARD_COLS), self.MAX_BOARD_COLS)
		self.index = row_index
		self.force_empty_init = is_empty

		self.cells = []
		self.generate_cells()

	def __getitem__(self, i):
		return self.cells[i]

	def generate_cells(self):
		# id => row_col
		self.cells = [WaterCell(int("{}{}".format(self.index, i)), randint(0, 3) if not self.force_empty_init else WaterCell.ELEMENT_EMPTY, randint(0, WaterCell.ELEMENT_VALUE_MAX/2)) for i in range(self.n_col)]

	def __str__(self):
		return ",".join(map(str, self.cells))

class CardJitsuGame(Multiplayer):
	waddle = -1 # Waddle id
	MAX_BOARD_SPACES = 16

	MAX_BOARD_ROWS = 9
	CARD_AMOUNT = 7

	REQ_GAME_TIME = 100
	REQ_GAME_INIT = 101
	REQ_PLAYER_INIT = 102
	REQ_GAME_START = 103
	REQ_GAME_ABORT = 104
	REQ_CARD_SELECT = 110
	REQ_PLAYER_MOVE = 120
	REQ_PLAYER_THROW = 121

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

	def play(self, client, param):
		if not self.GameStarted or client not in self.Playing:
			return client.send('e', 'ABCDE-ee-FU')

		move = int(param[0])
		if move == self.REQ_GAME_START:
			if self.BattleStarted:
				pass #todo: check logic
			else:
				client.penguin.game_board_ready = True

			return

		if not self.BattleStarted:
			return client.send('e', 'How jobless are you?')

		print "zm", param
		

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

		client.send('jz', client['game_index'], client['nickname'], client['data'].avatar.color, client['ninjaHandler'].ninja.water)
		self.send_zm_client(client, "po", client['game_index'])
		self.updateGame()

		if None not in self.Playing[:CJ_MATS[self.waddle]]:
			self.startGame()

	def startGame(self):
		if self.GameStarted:
			return

		self.noPlaying = CJ_MATS[self.waddle]
		self.Playing = self[:self.noPlaying]
		self.GameStarted = True
		self.BattleStarted = False
		self.GameCards = [None] * self.noPlaying
		self.GameCols  = 3 + self.noPlaying  # 5 + (n - 2)

		self.initiateGameVector()
		#self.initiatePlayerPosition()
		self.initiatePlayerCards()
		self.initiateVelocity()

		self.boardReadyTickHandler = task.LoopingCall(self.initiateGameStart)
		self.boardReadyTick = 60
		self.boardReadyTickHandler.start(1.0) # run every second
	
	def initiateGameStart(self):
		self.send_zm("tt", self.boardReadyTick)
		self.boardReadyTick -= 1

		# check if all players are ready
		if self.boardReadyTick < 1 or all(map(lambda p: p['game_board_ready'], self.Playing)):
			self.boardReadyTickHandler.stop()
			self.boardReadyTickHandler = None

			if all(map(lambda p: p['game_board_ready'], self.Playing)):
				self.BattleStarted = True
				self.initiatePlayerPosition()
				self.VelocityLoop.start(1)
			
			elif self.boardReadyTick < 1:
				self.send_zm("ge")
				self.gameOver()

	def initiateGameVector(self):
		self.GameBoard = []
		[self.generateRow(empty=True) for i in range(2)]
		[self.generateRow() for i in range(7)]

		[self.getCell(7, i*2).penguinJump(self.Playing[i]) for i in range(self.noPlaying)]

		self.send_zm("bi", self.GameCols, self.serializeBoard())

	def initiatePlayerPosition(self):
		pi_data = []
		available_pos = range(self.GameCols)
		for p in self.Playing:
			cellId = p['water_cell'].id
			row, col = cellId/10, cellId%10

			pi_data.append("|".join([str(p['game_index']), p['nickname'], str(p['data'].avatar.color), "{},{}".format(col, row)]))

		self.send_zm("pi", *pi_data)

	def initiatePlayerCards(self):
		for peng in self.Playing:
			index = peng['game_index']

			peng.penguin.cardGenerator = self.playerCardGenerator(peng)
			self.GameCards[index] = [WaterCard(*(peng['cardGenerator'].next())) for i in range(self.CARD_AMOUNT)]

			self.send_zm_client(peng, "ci", '|'.join(map(str, self.GameCards[index])))

	def setVelocity(self):
		# slope = y/x = 1/2
		# multiplier = 0.5
		# update ratio, x : y = 1 : 0.5
		self.GameVelocity += self.GameVelocityDelta
		VelocityVector = (self.GameVelocity / self.GameVelocitySlope, self.GameVelocity)

		self.send_zm("bv", *VelocityVector)
		self.send_zm("cv", *self.CardVelocity)

	def initiateVelocity(self):
		self.GameVelocityDelta = 200 # update y component
		self.GameVelocity = 3000 - self.GameVelocityDelta # initial velocity
		self.GameVelocitySlope = 0.5 # dy / dx
		self.CardVelocity = np.array((0, 1000))

		self.VelocityLoop = task.LoopingCall(self.setVelocity)

		self.send_zm("bv", self.GameVelocity / self.GameVelocitySlope , self.GameVelocity)
		self.send_zm("cv", *self.CardVelocity)

	def getPlayerCard(self, peng, uid):
		for i in self.GameCards[pemg['game_index']]:
			if i._index == uid:
				return i

		return None

	def playerCardGenerator(self, peng):
		cardsAvailable = list(peng['ninjaHandler'].cards.values())

		i = 0
		while True:
			i += 1
			yield (choice(cardsAvailable)[0], i)

	def send_zm(self, *args):
		return self.send("zm", "&".join(map(str, args)))

	def send_zm_client(self, client, *args):
		return client.send("zm", "&".join(map(str, args)))

	def getCell(self, y, x):
		return self.GameBoard[y][x]

	def serializeBoard(self):
		return '|'.join(map(str, self.GameBoard))

	def generateRow(self, empty = False):
		index = min(7, len(self.GameBoard))
		row = WaterRow(self.GameCols, index, is_empty = empty)

		self.GameBoard.append(row)
		if len(self.GameBoard) > self.MAX_BOARD_ROWS:
			self.GameBoard.pop(0)

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
		client.penguin.game_board_ready = client.penguin.game_index = client.penguin.game = client.penguin.room = None
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
