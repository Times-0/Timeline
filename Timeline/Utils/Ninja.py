from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Database.DB import Ninja

from twisted.internet.defer import inlineCallbacks, returnValue

from random import choice
from math import ceil
from collections import deque
import logging
import time

class NinjaHandler(object):

	items = [4025,4026,4027,4028,4029,4030,4031,4032,4033,104]
	powers = [[0], [2], [3], [4, 5], [6], [7, 8, 9], [10], [11, 12], [13, 14, 15], [16, 17, 18]]

	def __init__(self, penguin):
		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.cards = dict()
		self.matchesWon = dict() # against_id : won_or_not, ID = -1 for sensei
		self.wonMatchCount = 0
		self.progress = 0 # in percentage %

		self.setup()

	@inlineCallbacks
	def setup(self):
		self.ninja = yield Ninja.find(where = ['pid = ?', self.penguin['id']], limit = 1)
		
		if self.ninja is None:
			self.ninja = Ninja(pid = self.penguin['id'], cards = '')
			yield self.ninja.save()

		yield self.setupCards()
		self.setupWonMatches()

	def setupWonMatches(self):
		matches = self.ninja.matches
		if matches == None or matches == '':
			self.ninja.matches = ''
			return self.ninja.save()

		won = matches.strip(',').split(',')
		for i in won:
			against, isWon = i.split('|')
			isWon = isWon == '1'
			self.matchesWon[against] = isWon

			self.wonMatchCount += isWon

		self.progress = self.wonMatchCount / len(self.matchesWon) * 100

	def handleEarnedStamps(self):		
		stamps = self.penguin['recentStamps']
		g_stamps = self.penguin.engine.stampCrumbs.getStampsByGroup(38)
		e_stamps = list(set(self.penguin['stampHandler']).intersection(g_stamps))

		stamps = list(set(stamps).intersection(g_stamps))

		earned = len(e_stamps)
		total = len(g_stamps)

		if total == earned:
			coins *= 2

		self.penguin.send('cjsi', '|'.join(map(str, map(int, stamps))), earned, total, total)
		

	@inlineCallbacks
	def promoteNinja(self):
		maxBelt = self.ninja.belt
		belt = self.progress / 10

		if belt > maxBelt and maxBelt < 10:
			self.ninja.belt = maxBelt + 1
			self.penguin.send('cza', self.ninja.belt)

			if self.items[self.ninja.belt] not in self.penguin['inventory']:
				self.penguin['inventory'].append(self.items[self.ninja.belt])

			# Give him some cards :P like 5 of them (1% of all cards)
			eligiblePowers = sum(self.powers[:self.ninja.belt], [])
			eligibleCards = [k for k in self.penguin.engine.cardCrumbs.cards if k.power in eligiblePowers]
			for i in range(int(ceil(len(self.penguin.engine.cardCrumbs.cards) * 0.1))):
				randomCard = choice(eligibleCards)
				card_id = randomCard.id
				if card_id not in self.cards:
					self.cards[card_id] = [randomCard, 0]

				self.cards[card_id][1] += 1

			self.ninja.cards = '|'.join(map(lambda x: "{},{}".format(x, self.cards[x][1]), self.cards))

		yield self.ninja.save()

	@inlineCallbacks
	def addWin(self, against, isWon):
		isWon = bool(isWon)
		self.matchesWon[against] = isWon
		self.wonMatchCount += isWon

		self.progress = self.wonMatchCount / max(len(self.matchesWon), 250) * 100

		self.ninja.matches = "{},{}|{}".format(self.ninja.matches, against, int(isWon))
		yield self.ninja.save()

	def setupCards(self):
		cards = self.ninja.cards
		if cards == '' or cards == None:
			self.ninja.cards = '|'.join(map(lambda x: "{},1".format(x), [1, 6, 9, 14, 17, 20, 22, 23, 2673, 89, 81]))
			self.ninja.save()

		cards = self.ninja.cards.split('|')
		for c in cards:
			card_id, limit = map(int, c.split(","))
			card = self.penguin.engine.cardCrumbs[card_id]
			if card is None:
				continue

			self.cards[card_id] = [card, limit]
