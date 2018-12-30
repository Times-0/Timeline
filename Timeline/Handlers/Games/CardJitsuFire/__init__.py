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

class FireCard(Card):
	_n = 0 # No of cards available

	def __init__(self, card, i, n):
		self._n = n
		super(FireCard, self).__init__(card, i)

class CJFirePlayer(object):
	def __init__(self, penguin, _id, energy, score, cards, deck):
		self.penguin = penguin
		self.index = _id
		self.energy = energy
		self.score = score
		self.cards = cards
		self.deck = deck

		self.position = -1
		self.penguin.penguin.findex = self.index

	def send(self, *a):
		self.penguin.send(*a)

	def __getitem__(self, key):
		return self.penguin[key]

	def __eq__(self, p):
		return self.penguin == p

	def __ne__(self, p):
		return self.penguin != p

class Tile(object):
	def __init__(self, position):
		self.i = position
		self.players = list()
		self.player = None
		self.resetBattleType = self.resetSymbol = False
		self.battleStarted = False

		self.battlers = list()

	def __int__(self):
		return self.i

class CardJitsuGame(Multiplayer):
	waddle = -1 # Waddle id
	MAX_BOARD_SPACES = 16

	def __init__(self, rh):
		super(CardJitsuGame, self).__init__(rh, 997, "Fire", "Game: Card Jitsu Fire", 4, False, False, None)
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
				playerLeft.penguin.penguin.fire_rank = len(self.Playing)
				self.Playing.remove(playerLeft)

				playerLeft.card = playerLeft.deck = []
				playerLeft.energy = 0

				if self.tabMatch is not None and playerLeft in self.tabMatch.battlers:
					self.tabMatch.battlers.remove(playerLeft)

				playerLeft = playerLeft.penguin

				list.append(self, playerLeft)
				playerLeft.penguin.game = playerLeft.penguin.room = self


				self.send('zm', 'cz', playerLeft['findex'] if playerLeft['findex'] is not None else -1) if cz else 0
				playerLeft.send('zm', 'zo', self.getPlayerRank([playerLeft]))

				self.decideGameMove(playerLeft, i)
			else:
				playerLeft.engine.roomHandler.joinRoom(playerLeft, 'dojo', 'name')
				playerLeft.engine.roomHandler.joinRoom(playerLeft, 'dojofire', 'name')

			if len(self.Playing) < 2:
				self.gameOver()

			return

		gameWon = len(self.Playing) > 0
		winner = self.Playing[0] if gameWon else None
		if winner is not None:
			winner['ninjaHandler'].addFireWin(CJ_MATS[self.waddle])

		rankList = [-1, -1, -1, -1]
		for p in self:
			if p['fire_rank'] is not None:
				rankList[p['findex']] = p['fire_rank']

		del self.Playing[:]
		[p['ninjaHandler'].handleEarnedStamps(32) for p in list(self)]
		self.send('zm', 'zo', ','.join(map(str, rankList)))
		self.GameStarted = False

		if self.boardTimeoutHandler is not None and not self.boardTimeoutHandler.cancelled:
			self.boardTimeoutHandler.cancel()
			self.boardTimeoutHandler = None

		if self.battleTimeoutHandler is not None and not self.battleTimeoutHandler.cancelled:
			self.battleTimeoutHandler.cancel()
			self.battleTimeoutHandler = None

	def decideGameMove(self, playerLeft, i):
		if len(self.Playing) < 2:
			return

		nexPlayer = self.Playing[(i + 1) % self.noPlaying]
		if playerLeft == self.slotPlayer or playerLeft == self.tabPlayer:
			if not self.boardTimeoutHandler.cancelled:
				self.boardTimeoutHandler.cancel()

			self.slotPlayer = self.tabPlayer = nexPlayer
			self.send('zm', 'tb')
			self.checkGameStatus()

		if self.tabMatch is None:
			return

		if playerLeft == self.tabMatch.player:
			self.tabMatch.player = nexPlayer

		if playerLeft in self.tabMatch.battlers:
			self.tabMatch.battlers.remove(playerLeft)

	def sendGameOver(self, removedPlayers):
		PlayingList = self.getPlayerRank()
		[self.gameOver(k.penguin, 0) for k in removedPlayers]

	def play(self, client, param, tab = -1):
		if not self.GameStarted or client not in self.Playing:
			return client.send('e', 'ABCDE-ee-FU')

		move = param[0]
		client = self.Playing[self.Playing.index(client)]

		if move == 'is':
			playerIndex = int(param[1])
			spinIndex = int(param[2])

			if client is not self.slotPlayer or playerIndex != self.slotPlayer.index or not 1 <= spinIndex <= 6 or self.tabMatch is not None:
				return client.send('e', "I'ot hot sa'ce in my bag!")

			self.send('zm', 'is', playerIndex, spinIndex)
			self.slotPlayer = None

		elif move == 'cb':
			tabIndex = int(param[1])
			if self.slotPlayer is not None or self.tabPlayer is not client or self.tabMatch is not None:
				return client.send('e', "Y'ot the paw'r")

			availableTabs = self.moveSpins[1:]
			if tabIndex not in availableTabs:
				return client.send('e', 'ABCDE=ee=FU')

			self.tabPlayer = None
			self.tabMatch = self.GameBoard[tabIndex]
			self.tabMatch.player = client

			self.send('zm', 'cb', client.index, tabIndex)			
			self.jumpToPosition(client, tabIndex, tab)

			self.startBattle()

		elif move == 'ct':
			if self.tabMatch.player != client or self.tabMatch.battle == 'be' or self.tabMatch.symbol != 'n':
				return client.send('e', "You went to_0 far'o")

			ables = ['s', 'f', 'w']
			symbolChosen = param[1]
			if symbolChosen not in ables:
				return client.send('e', "I don't really care!")

			self.tabMatch.symbol = symbolChosen
			self.tabMatch.resetSymbol = True
			self.startBattle()

		elif move == 'cc':
			if not self.tabMatch.battleStarted or client['picked'] is not None:
				return client.send('e', "Let nuggin' begin'")

			cardIndex = int(param[1])
			if not 0 <= cardIndex <= 4:
				return client.send('e', "Boy who mobes.!.")

			client.penguin.penguin.picked = client.deck[cardIndex]
			self.cardPick(client, client['picked'])

		elif move == 'co':
			if self.tabMatch.player != client or self.tabMatch.battle != 'be' or len(self.tabMatch.battlers) > 0:
				return client.send('e', "I got you")

			opponentIndex = int(param[1])
			opponent = self.getPlayer(opponentIndex)
			battlers = [k.index for k in self.tabMatch.players]
			if opponent is None or (opponentIndex not in battlers and len(battlers) > 1):
				return client.send('e', 'All to you!')

			self.tabMatch.battlers = [client, opponent]
			#self.jumpToPosition(opponent, client.position)
			self.startBattle()

		elif move == 'ir':
			client.penguin.penguin.ir = True
			allClientSynced = sum(map(lambda x: bool(x['ir']), self.Playing)) == len(self.Playing)

			if not allClientSynced or self.boardTimeoutHandler is not None:
				return None

			moveSpins = ','.join(map(str, self.moveSpins))
			for p in self:
				pCards = ''
				if p in self.Playing:
					pCards = ','.join(map(str, map(int, self.Playing[self.Playing.index(p)].deck)))
				p.send('zm', 'nt', self.slotPlayer.index, moveSpins, pCards)

			self.boardTimeoutHandler = reactor.callLater(22, self.checkGameStatus)

		return True
		

	def getPlayer(self, index):
		for _ in self.Playing:
			if _.index == index:
				return _

		return None

	def cardPick(self, client, picked):
		self.sendExcept(client['id'], 'zm', 'ic', client.index, 'p5')
		canJudgeGame = sum(map(lambda x: x['picked'] is not None, self.tabMatch.battlers)) == len(self.tabMatch.battlers) and len(self.tabMatch.battlers) > 0

		if canJudgeGame:
			if self.battleTimeoutHandler is not None:
				self.battleTimeoutHandler.cancel()
				self.battleTimeoutHandler = None
			self.resolveBattle()

	def determineTrumpWin(self):
		trumpSymbol = self.tabMatch.symbol
		battlers = self.tabMatch.battlers

		playerCards = [_['picked'] for _ in battlers]
		playerCardValues = [(i, j.value if j.element == trumpSymbol else 0) for i, j in enumerate(playerCards)]
		playerCardValues.sort(key = lambda x: x[1], reverse = 1)
		
		canTie = playerCardValues[0][1] == playerCardValues[1][1]
		maxValue = playerCardValues[0][1]

		battleStatus = [0 for _ in battlers]
		for i, p in enumerate(battlers):
			if maxValue == 0:
				battleStatus[i] = 1
				p.energy -= 1
				continue

			battleStatus[i] = (3 - int(canTie)) if p['picked'].value == maxValue and p['picked'].element == trumpSymbol else 1
			p.energy -= int(battleStatus[i] == 1)

		return [battleStatus, trumpSymbol]

	def determineCJWin(self):
		b1, b2 = self.tabMatch.battlers

		b1Card, b2Card = [x['picked'] for x in self.tabMatch.battlers]
		ranks = {'f':1, 'w':2, 's':3}
		winner = (3 + ranks[b1Card.element] - ranks[b2Card.element]) % 3 - 1
		if winner == -1 and b1Card.value != b2Card.value:
			winner = 0 + int(b2Card.value > b1Card.value)

		if winner == -1:
			return [[2, 2], 'n']

		battleStatus = [0, 0]
		for i, p in enumerate(self.tabMatch.battlers):
			p.energy += 1 - 2 * int(i != winner)
			battleStatus[i] = 4 - 3 * int(i != winner)

		winSymbol = self.tabMatch.battlers[winner]['picked'].element

		return [battleStatus, winSymbol]

	def resolveBattle(self):
		arenaType = self.tabMatch.symbol
		isCJ = arenaType == 'n'

		self.tabMatch.battleStarted = False
		
		battlingSeatIds = ','.join(map(lambda x: str(x.index), self.tabMatch.battlers))
		cardListIds = ','.join(map(lambda x: str(int(x['picked'])), self.tabMatch.battlers))

		if isCJ:
			battleStatus = self.determineCJWin()
		else:
			battleStatus = self.determineTrumpWin()

		energyList = ','.join(map(lambda x: str(x.energy), self.tabMatch.battlers))
		tmpArray = ','.join([self.tabMatch.battle, battleStatus[1]])
		battlers = list(self.tabMatch.battlers)
		positionList = ','.join(map(lambda x: str(x.position), self.tabMatch.battlers))
		playerPosition = []

		currentSlotPlayer = self.tabMatch.player
		prevPlayingList = list(self.Playing)

		self.resetBattleArena()
		PlayingList = self.getPlayerRank()
		for p in self:
			pCards = ''
			if p in self.Playing:
				pCards = ','.join(map(str, map(int, self.Playing[self.Playing.index(p)].deck)))
			p.send('zm', 'rb', battlingSeatIds, cardListIds, energyList, ','.join(map(str, battleStatus[0])), tmpArray, pCards, PlayingList)

		self.updateSlot(currentSlotPlayer, prevPlayingList)

	def getPlayerRank(self, pll=[]):
		maxRank = len(self.Playing)
		pbr = sorted(self.Playing, key = lambda x: x.energy)

		ranks = [-1] * CJ_MATS[self.waddle]
		for i, p in enumerate(pbr):
			p.penguin.penguin.fire_rank = i + 1 if p.energy != pbr[i-1].energy or len(pbr) < 2 else pbr[i-1]['fire_rank']
			ranks[p.index] = p['fire_rank']

		rankList = [-1, -1, -1, -1]
		plist = list(self) + pll
		for p in plist:
			if p['fire_rank'] is not None:
				rankList[p['findex']] = p['fire_rank']

		return ','.join(map(str, rankList))

	def updateSlot(self, pastPlayer, playerList):
		if len(self.Playing) < 2:
			return self.gameOver()

		nextIndex = (playerList.index(pastPlayer) + 1) % len(playerList)
		player = playerList[nextIndex]
		while player not in self.Playing:
			nextIndex += 1
			player = playerList[nextIndex % len(playerList)]

		self.slotPlayer = self.tabPlayer = player
		self.setSpins()

	def resetBattleArena(self):
		toRemove = []
		for p in self.tabMatch.battlers:
			cIndex = p.deck.index(p['picked'])
			availableCards = [_ for _ in p.cards if _ not in p.deck]
			p.deck[cIndex] = choice(availableCards)
			p.penguin.penguin.picked = None
			p.penguin.penguin.ir = False

			if p.energy < 1:
				p.cards = p.deck = list()
				if p in self.Playing:
					p.penguin.penguin.fire_rank = len(self.Playing)
					toRemove.append(p)

		self.sendGameOver(toRemove)

		self.tabMatch.battlers = list()
		self.tabMatch.battleStarted = False
		self.tabMatch.player = None
		if self.tabMatch.resetSymbol:
			self.tabMatch.symbol = 'n'

		if self.tabMatch.resetBattleType:
			self.tabMatch.battle = 'bt'
			self.tabMatch.resetBattleType = False

		self.tabMatch = None

	def startBattle(self):
		battleType = self.tabMatch.battle
		if len(self.tabMatch.players) > 1:
			battleType = self.tabMatch.battle = 'be'
			self.tabMatch.resetBattleType = True
			
		symbol = self.tabMatch.symbol
		isCJMatch = battleType == 'be'

		if not isCJMatch:
			self.tabMatch.battlers = list(self.Playing)

		battlingPlayers = ','.join(map(lambda x: str(x.index), self.tabMatch.battlers))
		
		client = self.tabMatch.player
		if not isCJMatch and symbol == 'n':
			return client.send('zm', 'ct')

		if isCJMatch and len(self.tabMatch.battlers) < 1:
			availableOpponents = ','.join(map(lambda x: str(x.index), [_ for _ in (self.Playing if len(self.tabMatch.players) < 2 else self.tabMatch.players) if _ is not client]))
			return client.send('zm', 'co', availableOpponents)

		self.tabMatch.battleStarted = True

		if self.boardTimeoutHandler is not None:
			self.boardTimeoutHandler.cancel()
			self.boardTimeoutHandler = None

		self.battleTimeoutHandler = reactor.callLater(22, self.checkBattleStatus)

		self.send('zm', 'sb', battleType, battlingPlayers, symbol)

	def checkBattleStatus(self):
		try:
			self.battleTimeoutHandler = None
			if self.tabMatch is None or not self.tabMatch.battleStarted or len(self.tabMatch.battlers) < 1 or self.slotPlayer is not None:
				return

			for p in list(self.tabMatch.battlers):
				if not p['picked']:
					self.play(p, ['cc', choice(range(5))])
					if self.slotPlayer is not None:
						return
		except ReferenceError:
			pass

	def checkGameStatus(self):
		try:
			self.boardTimeoutHandler = None

			if not self.GameStarted or len(self.Playing) < 1:
				return
			tab = -1
			if self.slotPlayer is not None:
				self.slotPlayer.send('zm', 'tb', self.slotPlayer.index, 'p3')
				tab = self.moveSpins[0]
				client = self.slotPlayer

				self.play(self.slotPlayer, ['is', self.slotPlayer.index, tab])

			if self.tabPlayer is not None:
				self.play(self.tabPlayer, ['cb', choice(self.moveSpins[1:])], tab)

			if self.tabMatch is not None and self.tabMatch.battle == 'bt' and self.tabMatch.symbol == 'n':
				self.play(self.tabMatch.player, ['ct', choice(['s', 'w', 'f'])])

			if self.tabMatch is not None and self.tabMatch.battle == 'be' and len(self.tabMatch.battlers) < 1:
				opponents = [_ for _ in self.Playing if _ is not self.tabMatch.player]
				opponent = choice(opponents)
				self.play(self.tabMatch.player, ['co', opponent.index])

		except ReferenceError:
			pass

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
		self.GameBoard = map(Tile, range(self.MAX_BOARD_SPACES))
		self.moveSpins = [-1, -1, -1]

		self.setupCards()
		self.setupBattleArena()

		self.Playing = map(lambda i: CJFirePlayer(self.Playing[i], i, 6, 0, self.GameCards[i], self.GameDeck[i]), range(len(self.Playing)))
		self.slotPlayer = self.Playing[0]
		self.tabPlayer = self.Playing[0]
		self.tabMatch = None

		self.setupBoardPosition()
		self.sendStartGameMessage()

		self.boardTimeoutHandler = reactor.callLater(22, self.checkGameStatus)
		self.battleTimeoutHandler = None
	
	def sendStartGameMessage(self):
		'sz, ActiveSeatId, NicknamesDelimiteBy(,), ColorsDelimitedBy(,)[9674916 for SENSEI], PlayerEnergyDelimitedBy(,), ActiveBoardId, MyCardList, [spinAmount, MoveClockWise, MoveCounterClockWise], PlayerRanksDelimitedBy(,), PlayerScoreDelimitedBy(,)'
		
		Nicknames = ','.join(map(lambda x: str(x.penguin['nickname']), self.Playing))
		Colors = ','.join(map(lambda x: str(x.penguin['data'].avatar.color), self.Playing))
		Energies = ','.join(map(lambda x: str(x.energy), self.Playing))
		Scores = ','.join(map(lambda x: str(x.score), self.Playing))
		Ranks = ','.join(map(lambda x: '1', self.Playing))
		Spins = ','.join(map(str, self.moveSpins))
		#Ranks = ','.join(map(lambda x: str(x.penguin['ninjaHandler'].ninja.fire), self.Playing))
		PlayerBoardPositions = ','.join(map(lambda x: str(x.position), self.Playing))
		ActivePlayer = self.slotPlayer.index

		for peng in self.Playing:
			CardList = ','.join(map(str, map(int, peng.deck)))
			peng.send('sz', ActivePlayer, Nicknames, Colors, Energies, PlayerBoardPositions, CardList, Spins, Ranks, Scores)

	def jumpToPosition(self, peng, position, tab = -1):
		if peng.position != -1:
			self.GameBoard[peng.position].players.remove(peng)

		peng.position = position
		self.GameBoard[position].players.append(peng)

		self.send('zm', 'ub', peng.index, ','.join(map(lambda x: str(x.position), self.Playing)), tab)

	def setupBoardPosition(self):
		availableBoardTiles = map(int, self.GameBoard)
		for i, peng in enumerate(self.Playing):
			position = randint(0, len(availableBoardTiles) - 1)
			peng.position = position

			self.GameBoard[position].players.append(peng)

		self.setSpins()

	def setSpins(self):
		self.moveSpins[0] = randint(1, 6)
		moveSpin1 = (self.moveSpins[1] + randint(1, self.MAX_BOARD_SPACES - 1)) % 16
		self.moveSpins[1] = moveSpin1 if moveSpin1 != self.slotPlayer.position else (moveSpin1 + 1) % 16
		moveSpin2 = (self.moveSpins[0] + self.moveSpins[1] + randint(1, self.MAX_BOARD_SPACES - 1)) % 16
		self.moveSpins[2] = moveSpin2 if moveSpin2 != self.slotPlayer.position else (moveSpin2 + 1) % 16

	def setupBattleArena(self):
		elementIndex = lambda x: int(round(-1.145434939*(10**-9) *(x**6) + 6.73083819*(10**-3) *(x**5) - 3.365401484*(10**-1) *(x**4) + 6.508325611 *(x**3) - 60.63388984 *(x**2) + 271.3578765 *(x**1)- 464.1965785))
		defaultArena = [['be', 'n'], ['bt', 's'], ['bt', 'w'], ['bt', 'f'], ['bt', 'n']]

		for i, arena in enumerate(defaultArena):
			self.GameBoard[i].battle = arena[0]
			self.GameBoard[i].symbol = arena[1]

		for i in range(5, 16):
			similarArena = self.GameBoard[elementIndex(i)]
			self.GameBoard[i].battle = similarArena.battle
			self.GameBoard[i].symbol = similarArena.symbol

	def setupCards(self):
		for i in range(len(self.Playing)):
			peng = self.Playing[i]
			cardsAvailable = list(peng['ninjaHandler'].cards.values())
			shuffle(cardsAvailable)

			self.GameCards[i] = [FireCard(cardsAvailable[k][0], k, cardsAvailable[k][1]) for k in range(len(cardsAvailable))]
			self.GameDeck[i] = list(sample(self.GameCards[i], 5))

			peng.penguin.canPickCard = True
			peng.penguin.winCards = []


	def updateGame(self):
		uzString = list()
		for i in range(CJ_MATS[self.waddle]):
			user = self.Playing[i]
			if user is None:
				continue
			# seat|nickname|peng_color|belt
			uzString.append('|'.join(map(str, [i, user['nickname'], user['data'].avatar.color, user['ninjaHandler'].ninja.fire])))

		self.send('uz', len(uzString), '%'.join(uzString))

	def getGame(self, client):
		client.send('gz', self)

		self.joinGame(client)

	def __str__(self):
		return '{}%{}'.format(CJ_MATS[self.waddle], len([k for k in self.Playing if k is not None]))

	def onRemove(self, client):
		client.penguin.game_index = client.penguin.game = client.penguin.room = client.penguin.fire_rank = client.penguin.picked = client.penguin.ir = client.penguin.fcoins = None
		client.penguin.waddling = client.penguin.playing = False

		self.gameOver(client)



class CJMat(Waddle):
	stamp = 32
	room = None
	game = CardJitsuGame

	waddles = 2 # No of players waddling.
	waddle = None # waddle id

	def __init__(self, *a, **kw):
		super(CJMat, self).__init__(*a, **kw)

		self.stamp = self.roomHandler.getRoomByExtId(997).stamp_id
		self.room = self.roomHandler.getRoomByExtId(812)

	# CJMS
	def startWaddle(self):
		clients = list(self[:self.waddles])
		cjms = [0]*self.waddles*3 # no of players * 3

		for i in range(self.waddles):
			cjms[i + 0 * self.waddles] = clients[i]['data'].avatar.color
			cjms[i + 1 * self.waddles] = clients[i]['ninjaHandler'].ninja.belt
			cjms[i + 2 * self.waddles] = clients[i]['id']

		for c in clients:
			c.send('cjms', self.waddle, 997, -997, 2, *cjms)
			c.penguin.game_index = clients.index(c)

		super(CJMat, self).startWaddle()