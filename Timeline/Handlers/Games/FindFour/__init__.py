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

FOUR_TABLES = {220:range(205, 208), 221:[]}

class FindFour(TableGame):
	def __init__(self, rh, table_id, base_room):
		self.table = table_id
		self.room = rh.getRoomByExtId(base_room)

		super(FindFour, self).__init__(rh, self.room.id, "FindFour", "FindFour Game", self.room.max, False, False, None)

		self.reset()

	def leaveGame(self, client):
		if self.FourStarted and client in self[:2]:
			self.gameOver(client)
			self.reset()

		super(FindFour, self).leaveGame(client)

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
		super(FindFour, self).joinGame(client)

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

		self.FourGame = [[0] * 7 for k in range(6)]
		self.Player = -1
		self.Players = None
		self.Points = {0:0, 1:0}
		self.WinChip = (-1, -1, 0)

		self.FourStarted = False

	def getBoard(self):
		return self.FourGame

	def start(self):
		if self.FourStarted:
			return

		self.FourStarted = True
		self.Player = 0

		self.Players = self[:2]

		self.send('sz', 'FindFour')

	def isValidChip(self, x, y):
		if not (0 <= x < len(self.FourGame) and 0 <= y < len(self.FourGame[0])):
			return False

		if 0 <= x < len(self.FourGame) - 1:
			if self.FourGame[x + 1][y] == -1:
				return False


		return self.FourGame[x][y] == 0

	def placeChip(self, x, y):
		self.FourGame[x][y] = self.Player + 1
		self.Points[self.Player] += 1

	def checkWin(self, player = -1, x = 0, y = 0, dx = 1, dy = 1):
		dw = 0

		while 0 <= x < len(self.FourGame) and 0 <= y < len(self.FourGame[x]):
			advantage = self.FourGame[x][y] == player
			dw = dw * advantage + advantage

			if dw > 3:
				return True

			x += dx
			y += dy

		return False

	def won(self, player = -1):

		# horizontal win
		for i in range(len(self.FourGame)):
			if self.checkWin(player, i, 0, 0, 1):
				return 1

		# vertical win
		for i in range(len(self.FourGame[0])):
			if self.checkWin(player, 0, i, 1, 0):
				return 2

		# diagonal win
		for i in range(len(self.FourGame)):
			for j in range(len(self.FourGame[i])):
				if self.checkWin(player, i, j, 1, 1) or self.checkWin(player, i, j, -1, -1) or self.checkWin(player, i, j, -1, 1) or self.checkWin(player, i, j, 1, -1):
					return 3

		# Tie
		if 0 not in sum(self.FourGame, []):
			return -1

		return 0


	def play(self, client, move):
		if not client in self.Players or not self.FourStarted or not client is self.currentPlayer():
			return client.send('e', 'Fraud Work!')

		x, y = map(int, move) # any error? lol it's his fault!
		if not self.isValidChip(y, x):
			return

		self.placeChip(y, x)
		self.send('zm', self.Player, x, y)

		won = self.won(self.Player + 1)
		if won:
			self.gameOver()
			self.reset()
			return

		self.swap()

	# automatically calculate the next best move
	def minimax(self, player = 0, depth = 0):
		if player == 0:
			player = self.Player

		currentPlayer = self[player]
		opponent = self[(player + 1) % 2]
		sign = -1 if player < 1 else 1

		playerOrder = sign * 10
		opponentOrder = -playerOrder

		for i in [player, opponent]:
			iWon = self.won(i + 1)
			iSign = -1 if i < 1 else 1
			iOrder = iSign * 10

			if iWon:
				if iWon < 0:
					return ((-1, -1), 0) # tie

				return ((-1, -1), depth - iOrder) # score

		emptySlots = self.playableChips()
		bestMove = (emptySlots[0], playerOrder) # move, score for current move

		for move in emptySlots:
			self.FourGame[x][y] = player + 1 # try the move
			result = self.minimax(opponent, depth + 1) # test the move for opponents advantage
			self.FourGame[x][y] = 0 # undo the move

			if sign < 0 and result[1] > bestMove[1] or sign > 0 and result[1] < bestMove[1]:
				bestMove = result

		return bestMove # tuple(row, column), int(score)

	def playableChips(self):
		chips = list()

		for i in range(len(self.FourGame)):
			for j in range(len(self.FourGame[i])):
				if self.isValidChip(i, j):
					chips.append((i, j))

		return chips
