from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.TableHandler import TableGame

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

MANCALA_TABLES = {111:range(100, 105)}

class MancalaGame(TableGame):
	def __init__(self, rh, table_id, base_room):
		self.table = table_id
		self.room = rh.getRoomByExtId(base_room)

		super(MancalaGame, self).__init__(rh, self.room.id, "Mancala", "Mancala Game", self.room.max, False, False, None)

		self.reset()

	def leaveGame(self, client):
		if self.MancalaStarted and client in self[:2]:
			self.gameOver(client)
			self.reset()

		super(MancalaGame, self).leaveGame(client)

		self.updateTable()

	def gameOver(self, playerLeft = None):
		if playerLeft is not None and playerLeft in self[:2]:
			self.send('cz', playerLeft['nickname'])

			opponent, OIndex = (self[0], 0) if self[1] is playerLeft else (self[1], 1)
			opponent['coins'] += self.Points[OIndex]

		else:
			self[0]['coins'] += self.Points[0]
			self[1]['coins'] += self.Points[1]

		for peng in list(self):
			peng.send('zo', peng['coins'])
			del self[self.index(peng)]

			self.onRemove(peng)

	def joinGame(self, client):
		super(MancalaGame, self).joinGame(client)

		if len(self) > 1:
			self.start()

	def currentPlayer(self):
		return self[self.Player] if self.Player > -1 else None

	def clear(self):
		del self[:]

	def swap(self):
		self.Player = (self.Player + 1) % 2

	def reset(self):
		self.clear()

		self.MancalaGame = \
		[
			[4, 4, 4, 4, 4, 4, 0],
			[4, 4, 4, 4, 4, 4, 0]
		]
		self.Player = -1
		self.Players = None
		self.Points = {0:0, 1:0}
		self.CupCache = [-1, -1]

		self.MancalaStarted = False

	def getBoard(self):
		return self.MancalaGame

	def start(self):
		if self.MancalaStarted:
			return

		self.MancalaStarted = True
		self.Player = 0

		self.Players = self[:2]

		self.send('sz', 0)

	def isValidChip(self, x, y):
		if not -1 < x < 2 or not -1 < y < 6:
			return False

		return self.MancalaGame[x][y] != 0 and x == self.Player

	def isBank(self, x, y):
		return y == 6

	def isOpponentBank(self, x, y):
		return self.isBank(x, y) and x != self.Player

	def placeChip(self, x, y):
		index = 7 * x + y

		chips = self.MancalaGame[x][y]
		self.MancalaGame[x][y] = 0
		while chips > 0:
			if y > 5:
				y = -1
				x = (x + 1) % 2
			
			y += 1			
			if self.isOpponentBank(x, y):
				continue

			chips -= 1
			self.MancalaGame[x][y] += 1

		ix = (x + 1) % 2
		iy = 5 - y
		
		if self.isBank(x, y):
			# free turn
			return 'f'

		if self.MancalaGame[ix][iy] != 0 and self.MancalaGame[x][y] == 1:
			# capture
			captured = self.MancalaGame[x][y] + self.MancalaGame[ix][iy]
			self.MancalaGame[x][y] = self.MancalaGame[ix][iy] = 0

			self.MancalaGame[x][6] += captured
			return 'c'

		return 'd'

	def won(self):
		b1 = sum(self.MancalaGame[0][:6]) == 0
		b2 = sum(self.MancalaGame[0][:6]) == 0

		gameOver = b1 or b2
		if gameOver:
			self.Points[0] = self.MancalaGame[0][6] * 10
			self.Points[1] = self.MancalaGame[1][6] * 10

		return gameOver


	def play(self, client, move):
		if not client in self.Players or not self.MancalaStarted or not client is self.currentPlayer():
			return client.send('e', 'Fraud Work!')

		index = int(move[0])
		x, y = index / 7, index % 7

		if not self.isValidChip(x, y):
			return

		gamePos = self.placeChip(x, y)
		self.send('zm', self.Player, index, gamePos)

		won = self.won()
		if won:
			self.gameOver()
			self.reset()
			return

		if gamePos != 'f':
			self.swap()
