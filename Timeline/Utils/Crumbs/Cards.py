from Timeline.Server.Constants import TIMELINE_LOGGER
from twisted.internet.defer import Deferred

from collections import deque
import logging
import json
import os, sys

class Card(object):
	def __init__(self, _id, set_id, power, element, name, value, glow, desc):
		self.id = _id
		self.set = set_id
		self.power = power
		self.element = element
		self.name = name
		self.value = value
		self.glow = glow
		self.powerOnScore = desc[13] == 's' if self.power else False

	def __repr__(self):
		return "Card<{}#{}>".format(self.name, self.id)

	def __str__(self):
		return "{c.id}|{c.element}|{c.value}|{c.glow}|{c.power}".format(c = self)

	def __int__(self):
		return int(self.id)

	def __eq__(self, card):
		if isinstance(card, int):
			return self.id == card

		elif isinstance(card, Card):
			return self.id == card.id

		elif isinstance(card, str):
			try:
				return self.id == int(card)
			except:
				pass

		return False

class CardsHandler(object):
	def __init__(self, engine, package = 'configs/crumbs/cards.json'):
		self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.package = package

		self.cards = deque()
		self.fireCards = deque()

		self.setup()

	def setup(self):
		self.cards.clear()

		if not os.path.exists(self.package):
			self.log("error", "cards.json not found in path :", self.package)
			sys.exit() # OOps!

		with open(self.package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for card in crumbs:
					self.cards.append(Card(int(card['card_id']), int(card['set_id']), int(card['power_id']), card['element'], card['name'], int(card['value']), card['color'], card['description']))

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()

		self.log('info', "Loaded", len(self.cards), "Card(s)")

	def getCardById(self, _id):
		_id = int(_id)
		for card in self.cards:
			if card.id == _id:
				return card

		return None

	def __getitem__(self,item):
		return self.getCardById(item)

	def log(self, l, *x):
		self.engine.log(l, '[Crumbs::Cards]', *x)