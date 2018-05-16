from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.TableHandler import TableGame

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

from numpy.random import choice

logger = logging.getLogger(TIMELINE_LOGGER)

HUNT_TABLES = {422:range(300, 308)}

class Treasure(object):
	TYPE = 0
	VALUE = 0
	FOUND = False
	RARITY = 0 # 0 - 1, less rare, more the occurrance

	def __init__(self, x, y):
		self.coordinates = (x, y)
		self.player = None # Treasure revealed by player x

		self.layer = -1
		self.maxLayer = 1

	def __repr__(self):
		return "Treasure<{}#{}>".format(self.__class__.__name__, self.VALUE)

class Coin(Treasure):
	TYPE = 1
	VALUE = 1
	RARITY = 0.149

class Gem(Treasure):
	TYPE = 2
	VALUE = 25
	RARITY = 0.149

class GemPiece(Gem):
	TYPE = 3
	RARITY = 0 # Substitute for Gem around it's 3 neighbouring sand digs
	VALUE = 0

	def __init__(self, x, y, p, q):
		super(GemPiece, self).__init__(x, y)
		self.GemCoordinate = (p, q)

class RareGem(Gem):
	TYPE = 4
	RARITY = 0.049
	VALUE = 100

class NoTreasure(Treasure):
	TYPE = 0
	VALUE = 0
	RARITY = 0.653

class TreasurePath(object):
	def __init__(self, lc, _map, *ts):
		self.treasures = list(ts)
		self.map = _map
		self.dug = False

		self.player = None

		self.layerCoordinate = lc

	def dig(self, client):
		assert self.dug is False

		for t in self.treasures:
			assert t.layer < t.maxLayer
			t.layer += 1

			if t.layer == t.maxLayer:
				t.player = client

		self.dug = True

	def getTreasureDug(self, client = None):
		tdug = {} # (x, y) : Coin/Gem
		if not self.dug:
			return tdug

		for t in self.treasures:
			if not t.layer == t.maxLayer:
				continue

			if isinstance(t, Coin) and (client is None or self.map.raw_map[t.coordinates[0]][t.coordinates[0]].player == client):
				tdug[t.coordinates] = t

			elif isinstance(t, GemPiece) and t.GemCoordinate not in tdug and self.map.isGemRevealed(t.coordinates)[1]:
				x, y = t.GemCoordinate
				if (client is None or self.map.raw_map[x][y].player == client):
					tdug[t.GemCoordinate] = self.map.raw_map[x][y]

			elif isinstance(t, Gem) and not isinstance(t, GemPiece) and t.coordinates not in tdug and self.map.isGemRevealed(t.coordinates)[1]:
				if (client is None or self.map.raw_map[t.coordinates[0]][t.coordinates[0]].player == client):
					tdug[t.coordinates] = t

		return tdug


	def __mod__(self, path):
		if not isinstance(path, TreasurePath):
			return set()

		return set(self.treasures).intersection(path.treasures)

class Row(TreasurePath):
	pass

class Column(TreasurePath):
	pass

class TreasureMap(object):
	'''
	The raw map for Treasure Hunt game. Default size of the board = 10 x 10

	Example of the map:
	 _______________
	|__|__|__|__|__|          
	|__|_^|^_|__|__|   Gem:  ^^      
	|__|_\|/_|__|()|         \/      
	|()|__|__|__|__|          
	|__|__|__|__|__|  Coin:  ()        
	|__|__|__|()|__|          
	'''

	TREASURES = [NoTreasure, Coin, Gem, RareGem]
	TreasureGenerator = lambda self: choice([_ for _ in TreasureMap.TREASURES], p = [_.RARITY for _ in TreasureMap.TREASURES])

	def __init__(self, height = 10, width = 10):
		'''
		__init__(height = 10, width = 10)

		Builds the Treasure Map, sets the locations for hunt (Coins, Gems),
		of size height x width

		Parameters
		----------
		height (optional): Sets the no of rows of the map
		width (optional): Sets the no of columns of the map

		Raises
		------
			None
		'''
		self.h = height
		self.w = width

		self.raw_map = [[NoTreasure(-1, -1)] * self.w for _ in range(self.h)]
		self.availableCoordinates = [(x, y) for x in range(self.h) for y in range(self.w)]
		self.setup()

	def getHiddenTreasureCount(self):
		hiddenCount = {Coin: 0, Gem:0}

		for t in sum(self.raw_map, []):
			if isinstance(t, Coin):
				hiddenCount[Coin] += 1

			elif isinstance(t, Gem) and not isinstance(t, GemPiece):
				hiddenCount[Gem] += 1

		return hiddenCount

	def isGemRevealed(self, (x, y)):
		'''
		isGemRevealed(coordinate)
		
		Check if the Gem (or part of Gem) in
		the position of the coordinate is completely
		dug up and Gem is revealed.
		ie, all layers of gem has been revealed.

		Parameters
		----------
			coordinate (x, y) : The tuple(x, y) coordinate of the position
								you want to check


		Raises
		------
			None

		Returns
		-------
			Boolean. True if all parts of gem is revealed.
					 False is there is no gem, or when parts 
					 	   of gem are not revealed

		'''

		CoordinateDugUp = (x, y) in self.availableCoordinates and self.rows[x].dug and self.columns[x].dug
		if not CoordinateDugUp or not isinstance(self.raw_map[x][y], Gem):
			return [(x, y), False]

		gem = self.raw_map[x][y]
		if isinstance(gem, GemPiece):
			x, y = gem.GemCoordinate
			gem = self.raw_map[x][y]

		gemPieces = [(x, y), (x+1, y), (x+1, y+1), (x, y+1)]

		return [(x, y), all([self.raw_map[p][q].layer == self.raw_map[p][q].maxLayer for p, q in gemPieces])] # ie all 4 gem pieces are dug up.

	def setup(self):
		'''
		setup()

		Generates Treasure map and set's the treasures ready to hunt

		Prameters
		---------
			None

		Raises
		---------
			None

		Returns
		---------
			None
		'''

		self.generateTreasure()

		self.generateRows()
		self.generateColumns()

		self.gem_map = [g.coordinates for g in self.raw_map if isinstance(g, Gem)]

	def generateTreasure(self):
		'''
		generateTreasure()

		Generates Treasure map

		Prameters
		---------
			None

		Raises
		---------
			None

		Returns
		---------
			None
		'''

		rareGemFound = False
		for x in range(self.h):
			for y in range(self.w):
				if isinstance(self.raw_map[x][y], GemPiece):
					continue

				treasure = self.TreasureGenerator()(x, y)
				if isinstance(treasure, Gem):
					requiredMapAxis = [(x+1, y), (x+1, y+1), (x, y+1)]

					isGemPossible = all([(p, q) in self.availableCoordinates and not isinstance(self.raw_map[p][q], Gem) for p, q in requiredMapAxis])
					gemInNeighbourhood = any([(p, q) in self.availableCoordinates and isinstance(self.raw_map[p][q], Gem) for p, q in requiredMapAxis])
					
					if not isGemPossible or (rareGemFound and isinstance(treasure, RareGem)):
						treasure = NoTreasure(x, y) if not gemInNeighbourhood else Coin(x, y)
						rareGemFound = isinstance(treasure, RareGem)
					else:
						for p, q in requiredMapAxis:
							self.raw_map[p][q] = GemPiece(p, q, x, y)
						

				self.raw_map[x][y] = treasure

	def generateRows(self):
		'''
		generateRows()

		Generates Row map

		Prameters
		---------
			None

		Raises
		---------
			None

		Returns
		---------
			None
		'''

		self.rows = [None] * self.h
		for x in range(self.h):
			row = self.raw_map[x]

			self.rows[x] = Row(x, self, *row)

	def generateColumns(self):
		'''
		generateColumns()

		Generates Column map

		Prameters
		---------
			None

		Raises
		---------
			None

		Returns
		---------
			None
		'''

		self.columns = [None] * self.w
		for y in range(self.w):
			column = [self.raw_map[x][y] for x in range(self.h)]

			self.columns[y] = Column(y, self, *column)


class TreasureHunt(TableGame):
	'''
	TreasureHunt : Two player table game.
				   Each player digs in sucession in a particular direction.
				   Intersection of any 2 digs, will reveal the hidden treasure, if any.
	
	Player 1 direction: right     (left to right)
	Player 2 direction: down    (top to bottom)
	
	Treasures:
		Coin 	 : 1 point 		occurs: 30%
		Gem  	 : 25 points	occurs: 15%
		Rare Gem : 25 points	occurs: 5%

	'''

	def __init__(self, rh, table_id, base_room):
		self.table = table_id
		self.room = rh.getRoomByExtId(base_room)
		
		super(TreasureHunt, self).__init__(rh, self.room.id, "TreasureHunt", "TreasureHunt Game", self.room.max, False, False, None)

		self.reset()

	def swap(self):
		self.Player = (self.Player + 1) % 2

	def play(self, client, move):
		if not client in self.Players or not self.HuntStarted or not client is self.currentPlayer() or len(move) < 3:
			return client.send('e', 'Keep tryin!')

		# rightbutton7_mc%right%7%

		moveDirection = 'right' if self.Player == 0 else 'down'
		movePath = self.Map.rows if moveDirection is 'right' else self.Map.columns
		pathKey = int(move[2])

		button_mc = "{}button{}_mc".format(moveDirection, pathKey)

		if not -1 < pathKey < len(movePath) or move[0] != button_mc or movePath[pathKey].dug:
			return client.send('e', 'Back of the well')

		Path = movePath[pathKey]
		Path.dig(client)

		self.digRecord.append((button_mc, moveDirection, pathKey))
		self.send('zm', *move)

		coinsDug, gemsDug, rareGemDug = 0, 0, 0
		for c, t in Path.getTreasureDug(client).iteritems():
			if isinstance(t, Coin):
				coinsDug += 1
			elif isinstance(t, RareGem):
				rareGemDug += 1
			elif isinstance(t, Gem):
				gemsDug += 1

		self.Points[self.Player] += coinsDug * Coin.VALUE + gemsDug * Gem.VALUE + rareGemDug * RareGem.VALUE

		gameOver = all(t.dug for t in (self.Map.rows + self.Map.columns))
		self.turns += 1

		if gameOver or self.turns >= self.maxTurns:
			self.gameOver()
			self.clear()
			self.reset()

			return

		self.swap()

		print move

	def leaveGame(self, client):
		if self.HuntStarted and client in self[:2]:
			self.gameOver(client)
			self.reset()

		super(TreasureHunt, self).leaveGame(client)

		self.updateTable()

	def gameOver(self, playerLeft = None):
		totalPoints = self.Points[0] + self.Points[1]
		if playerLeft is not None and playerLeft in self[:2]:
			self.send('cz', playerLeft['nickname'])

			opponent, OIndex = (self[0], 0) if self[1] is playerLeft else (self[1], 1)
			opponent['coins'] += totalPoints

		else:
			self[0]['coins'] += totalPoints
			self[1]['coins'] += totalPoints

		for peng in list(self):
			peng.send('zo', peng['coins'])
			del self[self.index(peng)]

			self.onRemove(peng)

	def joinGame(self, client):
		super(TreasureHunt, self).joinGame(client)

		if len(self) > 1:
			self.start()

	def start(self):
		if self.HuntStarted:
			return

		self.HuntStarted = True
		self.Player = 0

		self.Players = self[:2]

		self.send('sz', self)

	def __str__(self):
		CoinNumHidden, GemNumHidden = self.Map.getHiddenTreasureCount().values()
		gems = [_ for _ in sum(self.Map.raw_map, []) if isinstance(_, Gem) and not isinstance(_, GemPiece)]
		gemLocations = ','.join(map(lambda g: ','.join(map(str, g.coordinates)), gems))
		raw_map = ','.join(map(lambda t: str(t.TYPE), sum(self.Map.raw_map, [])))

		nicknames = '%'.join(map(lambda x: x['nickname'] if x is not None else '', [self[i] if i < len(self) else None for i in range(2)]))

		coinsDug, gemsDug, rareGemDug = 0, 0, 0
		for Path in self.Map.rows:
			for c, t in Path.getTreasureDug().iteritems():
				coinsDug += int(isinstance(t, Coin))
				rareGemDug += int(isinstance(t, RareGem))
				gemsDug += int(isinstance(t, Gem))
		
		dig = '%'.join([','.join(map(lambda x: str(x[0]), self.digRecord)), 
					','.join(map(lambda x: str(x[1]), self.digRecord)), 
					','.join(map(lambda x: str(x[2]), self.digRecord))])

		return '%'.join(map(str, (nicknames, self.Map.w, self.Map.h, CoinNumHidden, GemNumHidden, 
			self.getTurnsRemaining(), Gem.VALUE, Coin.VALUE, gemLocations, raw_map, coinsDug, gemsDug, rareGemDug, dig)))

	def getTurnsRemaining(self):
		return self.maxTurns - self.turns

	def getBoard(self):
		return self.TreasureMap.raw_map

	def currentPlayer(self):
		return self.Players[self.Player] if self.Player > -1 else None

	def onRemove(self, client):
		super(TreasureHunt, self).onRemove(client)

	def reset(self):
		self.clear()

		self.HuntStarted = False
		self.Players = [None] * 2
		self.Player = -1
		self.Points = {0:0, 1:0}
		self.Map = TreasureMap()

		self.digRecord = [] # (button_name, button_dir, button_no)

		self.maxTurns = 12
		self.turns = 0

	def clear(self):
		del self[:]