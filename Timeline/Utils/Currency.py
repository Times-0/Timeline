from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Database.DB import Currency

from twisted.internet.defer import inlineCallbacks, returnValue
from twistar.dbobject import DBObject

from collections import deque
import logging
import time
import json

class CurrencyHandler(object):

	availableCurrencies = {1:'GOLDEN_NUGGETS'}

	def __init__(self, penguin):
		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.setup()
	
	@inlineCallbacks	
	def setup(self):
		self.currency = yield self.penguin.dbpenguin.currency.get()
		
		if self.currency is None:
			self.currency = Currency(penguin_id = self.penguin['id'], quest = '{}')
			yield self.currency.save()

		self.setupCurrencies()
		self.setupQuests()

	def setupCurrencies(self):
		self.currencies = {}
		ts = []
		for c in self.availableCurrencies:
			if hasattr(self.currency, self.availableCurrencies[c]):
				self.currencies[c] = getattr(self.currency, self.availableCurrencies[c])
				ts.append("{}|{}".format(c, self.currencies[c]))

		self.penguin.send('currencies', ','.join(ts))

	def refreshCurrencies(self):
		for c in self.currencies:
			setattr(self.currency, self.availableCurrencies[c], self.currencies[c])

		self.currency.quest = json.dumps(self.quest)
		self.currency.save()

	def setupQuests(self):
		self.quest = json.loads(self.currency.quest)
		up = 0

		if not 'puffle' in self.quest:
			self.quest['puffle'] = {}
			up = 1

		if not 'rainbow' in self.quest['puffle']:
			self.quest['puffle']['rainbow'] = \
			{
				'cookieID':'rainbowPuffleQuest', 'currTask' : 0, 'questsDone' : 0, 
				'tasks' : [{'completed' : False, 'coin' : 1, 'item' : 1} for k in range(4)],
				'cannon' : False, 'bonus' : 0, 'taskAvail' : None, 'hoursRemaining' :None, 'minutesRemaining' : None
			}
			up = 1

		if up: self.currency.quest = json.dumps(self.quest); self.currency.save()
		self.penguin.penguin.canAdoptRainbow = self.quest['puffle']['rainbow']['cannon']