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

	def updateValue(self, dv):
		self.value = max(0, min(self.value + dv, self.ELEMENT_VALUE_MAX))

		if self.value == 0:
			self.type = WaterCell.ELEMENT_EMPTY

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
		self.cells = [WaterCell(int("{}{}".format(self.index, i)), randint(0, 2) if not self.force_empty_init else WaterCell.ELEMENT_EMPTY, randint(0, WaterCell.ELEMENT_VALUE_MAX/2)) for i in range(self.n_col)]

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

	AVAILABLE_CARDS = set({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595})

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
				self.Playing.remove(playerLeft)

			playerLeft.engine.roomHandler.joinRoom(playerLeft, 'dojowater', 'name')

			if len(self.Playing) < 1:
				self.gameOver()

			return

		if self.VelocityLoop is not None and self.VelocityLoop.running:
			self.VelocityLoop.stop()
			self.VelocityLoop = None

		self.GameStarted = False
		players = self.Playing
		position = len(players)
		self.Playing = []

		for p in players:
			if not p['won_water_game']:
				self.send_zm('pd', p['game_index'], position, '00', 'false')

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

		if move == self.REQ_CARD_SELECT:
			card_id = int(param[1])
			card = self.getPlayerCard(client, card_id)
			if card is None:
				return self.send_zm_client(client, 'cp')

			self.GameCardPicked[client['game_index']] = card
			self.send_zm_client(client, 'cp', card)
			return 


		if move == self.REQ_PLAYER_MOVE or move == self.REQ_PLAYER_THROW:
			cell_id = int(param[1])

			available_cells = self.get_playable_cells(client)
			available_cells_by_id = {i.id: i for i in available_cells}

			if cell_id not in available_cells_by_id:
				print(cell_id, available_cells_by_id.keys(), client['water_cell'].id)
				return self.send_zm_client(client, 'pf', '{}-{}'.format(client['game_index'], cell_id), 'lmao')

			cell = available_cells_by_id[cell_id]
			if (move == self.REQ_PLAYER_MOVE and cell.type != WaterCell.ELEMENT_EMPTY) or \
				(move == self.REQ_PLAYER_THROW and self.GameCardPicked[client['game_index']] is None) or \
				not cell.canJump():

				return self.send_zm_client(client, 'pf', '{}-{}'.format(client['game_index'], cell_id), 'lmao')


			if move == self.REQ_PLAYER_THROW:
				cj_vaules = {'f' : 1, 'w' : 2, 's' : 3}
				card = self.GameCardPicked[client['game_index']]
				won = ((3 + cj_vaules[card.element] - (cell.type+1)) % 3 - 1) if cell.type != WaterCell.ELEMENT_EMPTY else -1

				print("CJ WIN:", card.element, cell.type, cj_vaules.keys()[cell.type-1], won)

				if won > 0:
					return self.send_zm_client(client, 'pf', '{}-{}'.format(client['game_index'], cell_id))

				self.GameCardPicked[client['game_index']] = None

				value_del = card.value * (-1 if won != -1 else 1)
				cell.updateValue(value_del)
				if cell.type == WaterCell.ELEMENT_EMPTY and cell.value > 0:
					cell.type = cj_vaules[card.element]-1

				print("ValDel:", value_del, cell.value)

				row, col = cell.id/10, cell.id%10
				cells = [i for i in self.get_nearby_cells(row, col)[:6] if i.canJump() and i.id != client['water_cell'].id]
				for i in cells:
					cell_win = ((3 + cj_vaules[card.element] - (i.type+1)) % 3 - 1) if i.type != WaterCell.ELEMENT_EMPTY else -1
					if cell_win < 1:
						i.type = cell.type if i.type == WaterCell.ELEMENT_EMPTY else i.type
						i.updateValue(value_del * (-1 if cell_win == -1 else 1))

				cells.insert(0, cell)
				self.send_zm('pt', client['game_index'], '{}-{}'.format(cj_vaules[card.element]-1, cell.id), '|'.join(map(str, cells)))

			else:
				# move player
				if cell.type != WaterCell.ELEMENT_EMPTY:
					return self.send_zm_client(client, 'pf', '{}-{}'.format(client['game_index'], cell_id), 'not empty?')

				
				client['water_cell'].penguin = None
				client.penguin.water_cell = None
				cell.penguinJump(client)

				self.send_zm('pm', '{}-{}'.format(client['game_index'], cell.id))

				last_row = self.GameBoard[-1]
				row = cell.id / 10
				if last_row.index - 2 == row:
					# he won the game
					progress, rank = client['ninjaHandler'].addWaterWin(CJ_MATS[self.waddle])
					self.send_zm("gw", client['game_index'], 1, '{}{}'.format(int(progress), rank), 'false')

					client.penguin.won_water_game = True
					self.GameStarted = False

					return self.gameOver()


	def get_playable_cells(self, client):
		cell = client['water_cell']
		row, col = cell.id/10, cell.id%10

		return self.get_nearby_cells(row, col)

	def get_nearby_cells(self, row, col):

		if row not in self.RowsById:
			return set()

		row_ref = self.RowsById[row]
		playable_cells = set()
		
		for i in range(max(0, col-1), min(self.GameCols, col+2)):
			if row+1 in self.RowsById:
				playable_cells.add(self.RowsById[row+1][i])

			if row-1 in self.RowsById:
				playable_cells.add(self.RowsById[row-1][i])

			if i != col:
				playable_cells.add(self.RowsById[row][i])

		return list(playable_cells)


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
		self.initiatePlayerCards()

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
		self.GameBoard = deque()
		self.GameCardPicked = [None] * self.noPlaying
		self.RowsById = {}
		self.CardsById = {}

		self.RowCount = 0

		[self.generateRow(empty=True) for i in range(2)]
		[self.generateRow() for i in range(4)]

		self.initiateVelocity()
		self.send_zm("bi", self.GameCols, self.serializeBoard())

		[self.getCell(1, i*2).penguinJump(self.Playing[i]) for i in range(self.noPlaying)]

	def initiatePlayerPosition(self):
		pi_data = []
		available_pos = range(self.GameCols)
		for p in self.Playing:
			cellId = p['water_cell'].id
			row, col = 4, cellId%10

			pi_data.append("|".join([str(p['game_index']), p['nickname'], str(p['data'].avatar.color), "{},{}".format(col, row)]))

		self.send_zm("pi", *pi_data)

	def initiatePlayerCards(self):
		for peng in self.Playing:
			index = peng['game_index']

			peng.penguin.cardGenerator = self.playerCardGenerator(peng)
			self.GameCards[index] = deque([WaterCard(*(peng['cardGenerator'].next())) for i in range(self.CARD_AMOUNT)])

			self.send_zm_client(peng, "ci", '|'.join(map(str, self.GameCards[index])))

	def velocityUpdateVector(self, vel, f=50):		
		vel = np.array(vel)

		a = np.linalg.norm(vel) / 1000.0
		b = 1000.0 / f
		vel *= a / vel.max()
		b = np.linalg.norm(vel) / b
		vel *= b / vel.max()

		return vel

	def setVelocity(self):
		# slope = y/x = 1/2
		# multiplier = 0.5
		# update ratio, x : y = 1 : 0.5
		self.GameVelocity += self.GameVelocityDelta
		#self.CardVelocity[0] += self.GameVelocityDelta / 2.0
		VelocityVector = (self.GameVelocity / self.GameVelocitySlope, self.GameVelocity)

		'''
		R: y = 0.5x + 186
		T: y = -2x + 1226
		int: (416, 394) => R(9)

		time = (Y - y) / updateF  * 0.05
		'''
		updateFreq = self.velocityUpdateVector(VelocityVector)[1]
		posDelta = 394 - self.GameBoardPosition

		if posDelta <= 0:
			self.cycleRow()
			self.GameBoardPosition = 278

		updateCardFreq = self.velocityUpdateVector(self.CardVelocity)[0]
		cardPosDelta = 128 - self.GameCardPosition
		if cardPosDelta <= 0:
			self.cycleCard()
			self.GameCardPosition = 0

		self.GameBoardPosition += updateFreq * 100
		self.GameCardPosition  += updateCardFreq * 100


		self.send_zm("bv", *VelocityVector)
		self.send_zm("cv", *self.CardVelocity)

	def cycleRow(self):
		def slipUsersOnTheEdge(row):
			players_in_row = [self.RowsById[row][i].penguin for i in range(self.GameCols) if self.RowsById[row][i].penguin is not None] if row in self.RowsById else []
			position = len(self.Playing)
			return self.send_zm(":".join(map(lambda p: 'pk&{}&{}&00&false'.format(p['game_index'], position), players_in_row)))

		dropped, drop_row = self.generateRow()
		if dropped:
			players_in_row = [drop_row[i].penguin for i in range(self.GameCols) if drop_row[i].penguin is not None]
			reactor.callLater(0.03, slipUsersOnTheEdge, drop_row.index+1)

			[(self.send_zm_client(p, 'gf'), self.gameOver(p)) for p in players_in_row]

		self.send_zm("br", self.GameBoard[-1])

	def cycleCard(self):
		for p in self.Playing:
			if self.GameCards[p['game_index']] is None:
				continue

			card = WaterCard(*(p['cardGenerator'].next()))

			if len(self.GameCards[p['game_index']]) > (self.CARD_AMOUNT+2):
				pop_card = self.GameCards[p['game_index']].popleft()

				if self.GameCardPicked[p['game_index']] is not None and \
					pop_card._index == self.GameCardPicked[p['game_index']]._index:

					self.GameCardPicked[p['game_index']] = None

			self.GameCards[p['game_index']].append(card)
			self.send_zm_client(p, 'ca', card)


	def initiateVelocity(self):
		self.GameVelocityDelta = 200.0 # update y component
		self.GameVelocity = 3000 - self.GameVelocityDelta # initial velocity
		self.GameVelocitySlope = 0.5 # dy / dx
		self.CardVelocity = np.array((60000.0, 0.0))
		self.GameCardPosition = 0

		self.GameBoardPosition = 278 # R(8)
		self.GameBoardRowDestroyTime = -1

		self.VelocityLoop = task.LoopingCall(self.setVelocity)

		self.send_zm("bv", self.GameVelocity / self.GameVelocitySlope , self.GameVelocity)
		self.send_zm("cv", *self.CardVelocity)

	def getPlayerCard(self, peng, uid):
		for i in self.GameCards[peng['game_index']]:
			if i._index == uid:
				return i

		return None

	def playerCardGenerator(self, peng):
		cardsAvailable = filter(lambda x: x[0].id in self.AVAILABLE_CARDS, list(peng['ninjaHandler'].cards.values()))

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
		if len(self.GameBoard) > self.MAX_BOARD_ROWS:
			pop_row = self.GameBoard.popleft()
			if pop_row.index in self.RowsById:
				del self.RowsById[pop_row.index]

			return True, pop_row

		self.RowCount += 1
		row = WaterRow(self.GameCols, self.RowCount, is_empty = empty)

		self.GameBoard.append(row)
		self.RowsById[row.index] = row

		return False, None

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
