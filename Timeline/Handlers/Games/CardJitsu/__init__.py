from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.WaddleHandler import Waddle
from Timeline.Utils.Crumbs.Cards import Card as CJCard

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import choice, shuffle, sample

logger = logging.getLogger(TIMELINE_LOGGER)

CJ_MATS = range(200, 204) # Igloo mats handled separately. Mats gets created on runtime.

class Card(CJCard):
	_index = 0
	_user = 0

	_id = 0

	def __init__(self, card, i):
		super(Card, self).__init__(card.id, card.set, card.power, card.element, card.name, card.value, card.glow, ['' for _ in range(14)])
		self.powerOnScore = card.powerOnScore
		self._index = i

		self._id = int(i)

	def __str__(self):
		return "{}|{}".format(self._id, super(Card, self).__str__())

class CardJitsuGame(Multiplayer):
	def __init__(self, rh):
		super(CardJitsuGame, self).__init__(rh, 998, "CardJitsu", "Game: Card Jitsu", 2, False, False, None)
		self.Playing = [None, None]
		self.GameStarted = False
		self.cards = [None, None] # [tuple(cards), tuple(cards)]

		self.gameCards = [[], []]
		self.gamePicks = [[], []]

	def gameOver(self, playerLeft = None, playerWon = None, winCards = None):
		self.GameStarted = False
		if winCards == None:
			winCards = []

		if playerLeft is not None:
			self.send('cz', playerLeft['nickname'])
			for u in list(self):
				self.remove(u)
				self.room.append(u)

			return

		for i in list(self):
			i['ninjaHandler'].handleEarnedStamps()
			i.send('czo', i['coins'], playerWon, *winCards)
			
			i['ninjaHandler'].promoteNinja()

			ix = self.Playing.index(i)
			i['ninjaHandler'].addWin(self[ix % 2]['id'], ix == playerWon)

	def checkForSameElementWin(self, user, cards):
		won = {'f' : [], 'w' : [], 's' : []}
		wonCards = None
		for c in cards:
			color = [c[0].glow, c]
			colors = [k[0] for k in won[c[0].element]]
			if color[0] not in colors:
				won[c[0].element].append(color)

			if len(won[c[0].element]) > 2:
				wonCards =map(lambda x: x[1], won[c[0].element])
				break

		return (wonCards != None, wonCards)

	def checkForMixElement(self, user, cards):
		won = {'f':None, 'w':None, 's':None}

		for c in cards:
			e = c[0].element
			color = c[0].glow
			colors = [k[0].glow for k in won.values() if k is not None]

			if won[e] == None and color not in colors:
				won[e] = c

		w = None not in won.values()
		return (w, won.values() if w else None)

	def judgeGame(self):
		#ckeck for wins, the card count is already checked
		won = 0
		wonCards = None
		for i in range(len(self.Playing)):
			user = self.Playing[i]
			userWonCards = user['winCards']

			a1, x1 = self.checkForSameElementWin(user, userWonCards)
			a2, x2 = self.checkForMixElement(user, userWonCards)

			wonCards = wonCards or (x1 or x2)
			won += (10**i)*(a1 or a2)

		if won > 0:
			if won == 11:
				self.gameOver(None, -1, [''])
			else:
				self.gameOver(None, len(str(won)) - 1, map(lambda x: x[0]._id, wonCards))

	def pickCard(self, client, card):
		if not client['canPickCard']:
			return

		client.penguin.canPickCard = False
		user = client['game_index']
		cardIndex = int(card)

		if user != client['game_index'] or not 0 <= cardIndex < len(self.cards[user]):
			return client.send('e', 'Cannot pick that')# invalid move?

		card = self.cards[user][cardIndex]

		if card not in self.gameCards[user]:
			return client.send('e', 'Cannot pick that')

		self.gamePicks[user].append(card)

		client.penguin.picked = card
		client.penguin.canJudge = True

		self.send('zm', 'pick', user, card[0]._id)

	def judgePlayerPower(self, p, won, opponent_card):
		if not p['hasPower']:
			return False

		r_won = False
		isSameElementPicked = p['picked'][0].element == opponent_card.element

		myValue = p['picked'][0].value
		opValue = opponent_card.value

		if p['power'] == 1:
			# When this card is played, lower values win ties the next round.
			if won != p and opValue < myValue:
				r_won = None # TIE

		elif (p['power'] == 2 or p['power'] == 3) and isSameElementPicked:
			# When this is scored, your card gets +2 for the next round
			myValue += 2 * (p['power'] == 2)
			opValue -= 2 * (p['power'] == 3)

			if myValue > opValue:
				r_won = p
			elif myValue == opValue:
				r_won = None

		elif p['power'] in [16, 17, 18]:
			px = {16 : ['w', 'f'], 17 : ['s', 'w'], 18 : ['f', 's']}
			myCard = p['picked'][0]
			elementChange = px[p['power']]
			if opponent_card.element == elementChange[0]:
				opponent_card.element = elementChange[1]

				winner = self.findWon()
				r_won = self.Playing[winner] if winner != -1 else None

				opponent = self.Playing[(p['game_index'] + 1) % 2]
				opponent.penguin.resetGameCards = [opponent_card, elementChange[0]]

		if p['hadPower'] in [13, 14, 15]:
			for i in range(len(self.Playing)):
				if self.Playing[i]['resetGameCards'] is None:
					continue

				[self.gameCards[i].append(k) for k in self.Playing[i]['resetGameCards']]
				self.Playing[i].penguin.resetGameCards = None

		elif p['hadPower'] in [16, 17, 18]:
			for i in range(len(self.Playing)):
				if self.Playing[i]['resetGameCards'] is None:
					continue

				self.Playing[i]['resetGameCards'][0].element = self.Playing[i]['resetGameCards'][1]
				self.Playing[i].penguin.resetGameCards = None


		p.penguin.hasPower = False
		p.penguin.power = None

		return r_won

	def judgePower(self, p1, p2, won):
		p1Power = self.judgePlayerPower(p1, won, p2['picked'][0])
		p2Power = self.judgePlayerPower(p2, won, p1['picked'][0])

		if p1Power == False and p2Power != False:
			won = p2Power

		elif p2Power == False and p1Power != False:
			won = p1Power

		return won

	def findWon(self):
		cj_vaules = {'f' : 1, 'w' : 2, 's' : 3}
		p1 = self.Playing[0]['picked'][0]
		p2 = self.Playing[1]['picked'][0]

		won = (3 + cj_vaules[p1.element] - cj_vaules[p2.element]) % 3 - 1
		if won == -1 and p1.value != p2.value:
			won = 0 if p1.value - p2.value > 0 else 1

		return won

	def updateCards(self):
		n_unavail = 0

		for i in range(len(self.Playing)):
			if self.Playing[i]['picked'] in self.gameCards[i]:
				self.gameCards[i].remove(self.Playing[i]['picked'])
			availableCards = [k for k in self.cards[i] if k[1] > 0 and k not in self.gameCards[i] + self.Playing[i]['winCards']]
			if len(availableCards) < 1:
				n_unavail += 10**i
				continue

			self.gameCards[i].insert(0, choice(availableCards))

		if n_unavail > 0:
			if n_unavail == 11:
				# TIE
				self.gameOver(None, -1)
			else:
				self.gameOver(None, len(str(n_unavail)) % 2) # Forced to leave?

			return

	def manipulatePower(self, p, o, c):
		doNothing = [1]

		pl = p
		p = pl['power']
		if p in doNothing:
			return #self.send('zm', 'power', pl['game_index'], -1, p)

		restData = list()
		powerReceiver = o['game_index']

		if p == 2:
			powerReceiver = pl['game_index']

		elif p in [4, 5, 6]:
			px = {4:'s', 5:'f', 6:'w'}
			e = px[p]
			opponentWonCards = [k for k in o['winCards'] if k[0].element == e]
			if len(opponentWonCards) > 0:
				cardToEliminate = choice(opponentWonCards)
				o['winCards'].remove(cardToEliminate)

				restData.append(cardToEliminate[0]._id)

		elif p in [7, 8, 9, 10, 11, 12]:
			px = {7:'r', 8:'b', 9:'g', 10:'y', 11:'o', 12:'p'}
			g = px[p]
			opponentWonCards = [k for k in o['winCards'] if k[0].glow == g]
			if len(opponentWonCards) > 0:
				cardToEliminate = choice(opponentWonCards)
				o['winCards'].remove(cardToEliminate)

				restData.append(cardToEliminate[0]._id)

		elif p in [13, 14, 15]:
			px = {13:'s', 14:'f', 15:'s'}
			i = powerReceiver
			cardsToEliminate = [k for k in self.gameCards[i] if k[0].element == px[p]]
			for c in cardsToEliminate:
				self.gameCards[i].remove(c) # remove that card

			self.Playing[i].penguin.resetGameCards = cardsToEliminate

			#powerReceiver = -1

		self.send('zm', 'power', pl['game_index'], powerReceiver, p, *restData)


	def playJitsu(self):
		won = self.findWon()

		won = self.Playing[won] if won != -1 else None
		p1 = self.Playing[0]
		p2 = self.Playing[1]

		prev_winner = won

		for i in [p1, p2]:
			if i['picked'][0].power in [16, 17, 18]:
				i.penguin.hadPower = i.penguin.power = i['picked'][0].power
				i.penguin.hasPower = True

		won = self.judgePower(p1, p2, won)

		if p1['picked'][0].power > 0:
			if p1['picked'][0].powerOnScore and won == p1 or not p1['picked'][0].powerOnScore:
				p1.penguin.hadPower = p1.penguin.power = p1['picked'][0].power
				p1.penguin.hasPower = True

		if p2['picked'][0].power > 0:
			if p2['picked'][0].powerOnScore and won == p2 or not p2['picked'][0].powerOnScore:
				p2.penguin.hadPower = p2.penguin.power = p2['picked'][0].power
				p2.penguin.hasPower = True

		if won == None:
			self.send('zm', 'judge', -1)
		else:
			winner = self.Playing[won['game_index']]
			opponent = self.Playing[(won['game_index'] + 1) % 2]

			winner['winCards'].append(winner['picked'])

			if winner['hadPower'] is not None:
				self.send('zm', 'power1', winner['game_index'], won['game_index'], winner['hadPower'])

			if winner['hasPower']:
				self.manipulatePower(winner, opponent, winner['picked'][0])
			
			self.send('zm', 'judge', won['game_index'])

		self.updateCards()

		p1.penguin.picked = p2.penguin.picked = None
		p1.penguin.canJitsu = p2.penguin.canJudge = False
		p1.penguin.canPickCard = p2.penguin.canPickCard = True

	def play(self, client, param):
		move = param[0]
		if not self.GameStarted:
			return

		if move == 'deal':
			i = self.Playing.index(client)
			n = int(param[1])
			return self.send('zm', 'deal', i, *map(lambda x: x[0], self.gameCards[i][:n]))

		elif move == 'pick':
			card = int(param[1])
			self.pickCard(client, card)
			canJitsu = sum(map(lambda x: x['picked'] != None, self.Playing)) == len(self.Playing)

			if canJitsu:
				self.playJitsu()
				self.judgeGame()

	def onAdd(self, client):
		client.penguin.game = self
		client.penguin.room = self
		client.penguin.waddling = False
		client.penguin.playing = True

	def joinGame(self, client):
		if client not in self:
			return

		client.penguin.game = client.penguin.room = self

		self.Playing[client['game_index']] = client
		client.send('jz', client['game_index'], client['nickname'], client['data'].avatar.color, client['ninjaHandler'].ninja.belt)
		self.updateGame()

		if None not in self.Playing:
			self.startGame()

	def startGame(self):
		if self.GameStarted:
			return

		self.GameStarted = True
		self.setupCards()

		self.send('sz', 'CardJitsu')

	def setupCards(self):
		for i in range(len(self.Playing)):
			self.cards[i] = list([list(k) for k in self.Playing[i]['ninjaHandler'].cards.values() if k[1] > 0])

			shuffle(self.cards[i])
			for ix in self.cards[i]:
				ix[0] = Card(ix[0], self.cards[i].index(ix))

			self.gameCards[i] = list(sample(self.cards[i], 5))
			for card in self.gameCards[i]:
				card[1] -= 1

			self.Playing[i].penguin.canPickCard = True
			self.Playing[i].penguin.winCards = []


	def updateGame(self):
		uzString = list()
		for i in range(len(self.Playing)):
			user = self.Playing[i]
			if user is None:
				continue
			# seat|nickname|peng_color|belt
			uzString.append('|'.join(map(str, [i, user['nickname'], user['data'].avatar.color, user['ninjaHandler'].ninja.belt])))

		self.send('uz', '%'.join(uzString))

	def getGame(self, client):
		client.send('gz', self)

	def __str__(self):
		return '2%{}'.format(len([k for k in self.Playing if k is not None]))

	def onRemove(self, client):
		client.penguin.winCards = client.penguin.picked = client.penguin.canJudge = client.penguin.game_index = client.penguin.game = None
		client.penguin.waddling = client.penguin.playing = False

		if self.GameStarted:
			self.gameOver(client)


class CJMat(Waddle):
	stamp = 38
	room = None
	game = CardJitsuGame

	waddles = 2 # No of players waddling.
	waddle = None # waddle id

	def __init__(self, *a, **kw):
		super(CJMat, self).__init__(*a, **kw)

		self.stamp = self.roomHandler.getRoomByExtId(998).stamp_id # save stamp to set for CJ Game
		self.room = self.roomHandler.getRoomByExtId(320)

	# CJMS
	def startWaddle(self):
		clients = list(self[:2])
		cjms = [0]*self.waddles*3 # no of players * 3

		for i in range(self.waddles):
			cjms[i + 0 * self.waddles] = clients[i]['data'].avatar.color
			cjms[i + 1 * self.waddles] = clients[i]['ninjaHandler'].ninja.belt
			cjms[i + 2 * self.waddles] = clients[i]['id']

		for c in clients:
			c.send('cjms', self.waddle, 998, -998, 2, *cjms)
			c.penguin.game_index = clients.index(c)

		super(CJMat, self).startWaddle()