from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Server.Penguin import Penguin
from Timeline.Handlers.Games.CardJitsu import CardJitsuGame

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import choice, shuffle, sample, randint

logger = logging.getLogger(TIMELINE_LOGGER)


class Sensei(Penguin):
	username = '$ensei'

	def send(self, *x):
		pass

	def disconnect(self, *x):
		pass

	def makeConnection(self, *x):
		pass


class CardJitsuSensei(CardJitsuGame):

	def __init__(self, rh):
		super(CardJitsuSensei, self).__init__(rh)
		self.Playing = [None, None]
		self.GameStarted = False
		self.cards = [None, None] # [tuple(cards), tuple(cards)]

		self.gameCards = [[], []]
		self.gamePicks = [[], []]

		self.canWin = False # Determines if player can win Sensei or not

	def gameOver(self, playerLeft = None, playerWon = None, winCards = None):
		if playerWon == 1:
			self.Playing[1]['ninjaHandler'].promoteToBlackBelt()

		sensei = self.Playing[0]
		client = self.Playing[1]
		super(CardJitsuSensei, self).gameOver(playerLeft, playerWon, winCards)
		sensei['room'].remove(sensei)

		del sensei

	def pickSenseiCard(self, canWin, card):
		sfw = {'s':'f', 'f':'w', 'w':'s'}
		pickedElement = card[0].element
		deathElement = sfw[pickedElement]
		pickedCard = None
		if not canWin:
			for c in self.gameCards[0]:
				if c[0].element == deathElement:
					pickedCard = c
					break

		if pickedCard is None:
			pickedCard = choice(self.gameCards[0])

		self.play(self.Playing[0], ['pick', pickedCard[0]._index])


	def pickCard(self, client, card):
		if not client['canPickCard']:
			return

		super(CardJitsuSensei, self).pickCard(client, card)
		if client == self.Playing[0]:
			return

		pickedCard = client['picked']
		canWin = randint(0, 1) * self.canWin
		self.pickSenseiCard(canWin, pickedCard)

	def play(self, client, param):
		super(CardJitsuSensei, self).play(client, param)
		if param[0] == 'deal':
			self.send('zm', 'deal', 0, *map(lambda x: x[0], self.gameCards[0][:int(param[1])]))

	def setupSenseiCards(self):
		needed = {'s', 'f', 'w'}
		colors = set()
		ix = 0
		cards = list(self.cards[0])
		shuffle(cards)
		for card in cards:
			color = card[0].element
			missingColors = needed.symmetric_difference(colors)
			if color in missingColors or len(missingColors) < 1:
				self.gameCards[0][ix] = card
				colors.update(color)
				ix += 1

			if ix > 4:
				return

	def selectSenseiCard(self):
		currentColors = set([k[0].element for k in self.gameCards[0]])
		availableCards = [k for k in self.cards[0] if k[1] > 0 and k not in self.gameCards[0] + self.Playing[0]['winCards']]
		colors = {'s', 'f', 'w'}
		colorsNeeded = currentColors.symmetric_difference(colors)

		pickableCard = None
		for c in availableCards:
			if c[0].element in colors:
				pickableCard = c
				break

		if len(colorsNeeded) < 1 or pickableCard is None:
			self.gameCards[0].insert(0, choice(availableCards))
		else:
			self.gameCards[0].insert(0, pickableCard)

	def updateCards(self):
		n_unavail = 0

		for i in range(len(self.Playing)):
			if self.Playing[i]['picked'] in self.gameCards[i]:
				self.gameCards[i].remove(self.Playing[i]['picked'])
			availableCards = [k for k in self.cards[i] if k[1] > 0 and k not in self.gameCards[i] + self.Playing[i]['winCards']]
			if len(availableCards) < 1:
				n_unavail += 10**i
				continue

			if i != 0:
				self.gameCards[i].insert(0, choice(availableCards))
			else:
				self.selectSenseiCard()

		if n_unavail > 0:
			if n_unavail == 11:
				# TIE
				self.gameOver(None, -1)
			else:
				self.gameOver(None, len(str(n_unavail)) % 2) # Forced to leave?

			return

	def startGame(self):
		super(CardJitsuSensei, self).startGame()
		
		client = self.Playing[1]
		self.canWin = client['ninjaHandler'].ninja.belt > 8
		self.setupSenseiCards()