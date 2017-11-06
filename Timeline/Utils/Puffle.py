from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Mails import Mail

from twisted.internet.defer import inlineCallbacks, returnValue
from twistar.dbobject import DBObject

from collections import deque
import logging
import time, json

class Puffle(DBObject):
	x = y = 0

	def adopt(self):
		return int(time.mktime(self.adopted.timetuple()))

	def __str__(self):
		#puffle id|type|sub_type|name|adoption|food|play|rest|clean|hat|x|y|is_walking
		return '|'.join(map(str, [int(self.id), int(self.type), int(self.subtype), self.name, self.adopt(), int(self.food), int(self.play), int(self.rest), int(self.clean), int(self.hat), int(self.x), int(self.y), int(self.walking)]))

class PuffleHandler(list):

	def __init__(self, penguin):
		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.setup()

	@inlineCallbacks
	def setup(self):
		self.walkingPuffle = None
		self.inventory = list()

		yield self.fetchPuffles()
		self.updateInventory()

		self.penguin.send('pgu', self)

	def getPuffleItem(self, _id):
		_id = int(_id)
		for k in self.inventory:
			if k[0] == _id:
				return k

		return None

	def updateInventory(self):
		inventory = str(self.penguin.dbpenguin.care).split('%')
		for inv in inventory:
			if inv == '':
				continue
			i = inv.split('|')
			self.inventory.append((int(i[0]), int(i[1])))

	@inlineCallbacks
	def fetchPuffles(self):
		puffles = yield Puffle.find(where = ['owner = ?', self.penguin['id']])

		for puffle in puffles:
			walking = bool(puffle.walking)
			if self.walkingPuffle is not None and walking:
				puffle.walking = 0
				puffle.save()

			if self.penguin.engine.puffleCrumbs[puffle.subtype] is None:
				continue

			puffle.x = puffle.y = 0

			self.append(puffle)
			if bool(puffle.walking):
				self.walkingPuffle = puffle

			yield self.setupPuffle(puffle)

	def puffleStr(self, backyard = False):
		puffles = [k for k in self if bool(k.backyard) is backyard]

		string = map(str, puffles)

		return '%'.join(string)

	def __str__(self):
		return '%'.join(map(str, self))

	@inlineCallbacks
	def setupPuffle(self, puffle):
		care_history = json.loads(puffle.lastcare)
		if care_history is None or len(care_history) < 1 or bool(int(puffle.backyard)):
			return # ULTIMATE PUFFLE <indefinite health and energy>

		now = int(time.time())
		
		last_fed = care_history['food']
		last_played = care_history['play']
		last_bathed = care_history['bath']

		food, play, clean = int(puffle.food), int(puffle.play), int(puffle.clean)

		puffleCrumb = self.penguin.engine.puffleCrumbs[puffle.subtype]
		max_food, max_play, max_clean = puffleCrumb.hunger, 100, puffleCrumb.health

		puffle.rest = puffleCrumb.rest # It's in the igloo all this time?
		puffle.member = puffleCrumb.member
		puffle.save()

		if not int(puffle.id) in self.penguin.engine.puffleCrumbs.defautPuffles:
			return # They aren't to be taken care of

		'''
		if remaining % < 10 : send a postcard blaming (hungry, dirty, or unhappy)
		if remaining % < 2 : move puffle to pet store, delete puffle, send a postcard, sue 1000 coins as penalty
		'''

		fed_percent = int((max_food - ((now - last_fed) * 0.05 * max_food / (24 * 60 * 60))) * 100 / max_food)
		play_percent = int((max_play - ((now - last_played) * 0.05 * max_play / (24 * 60 * 60))) * 100 / max_play)
		clean_percent = int((max_clean - ((now - last_bathed) * 0.05 * max_clean / (24 * 60 * 60))) * 100 / max_clean)

		total_percent = (fed_percent + play_percent + clean_percent)/3

		if fed_percent < 3 or total_percent < 6:
			# remove
			self.SendPuffleBackToTheWoods(puffle)
			returnValue(None)

		if fed_percent < 10:
			yield Mail(to_user = self.penguin['id'], from_user = 0, type = 110, description = str(puffle.name)).save()
			self.penguin['mail'].refresh()

		puffle.food = fed_percent * max_food / 100
		puffle.play = play_percent * max_play / 100
		puffle.clean = clean_percent * max_clean / 100

		care_history['food'] = care_history['play'] = care_history['bath'] = now
		puffle.lastcare = json.dumps(care_history)

		puffle.save()

	@inlineCallbacks
	def SendPuffleBackToTheWoods(self, puffle):
		if not puffle in self:
			return

		post_id = 100 + int(puffle.type)
		if puffle.type == 7:
			post_id = 169
		elif puffle.type == 8:
			post_id += 1
		self.remove(puffle)

		yield Mail(to_user = self.penguin['id'], from_user = 0, type = post_id, description = str(puffle.name)).save()
		self.penguin['coins'] -= 1000 # HAHAHAHA!

		self.penguin['mail'].refresh()

		yield puffle.delete()

	@inlineCallbacks
	def getPenguinPuffles(self, _id, backyard = False):
		_id = int(_id)

		exists = yield self.penguin.db_penguinExists(value = _id)
		if not exists:
			returnValue(None)

		if _id is self.penguin['id']:
			returnValue(self.puffleStr(backyard))

		puffles = yield Puffle.find(where = ['owner = ?', _id])
		returnValue('%'.join(map(str, [k for k in puffles if bool(k.backyard) is backyard])))

	def __contains__(self, key):
		if isinstance(key, Puffle):
			key = int(puffle.id)

		return self.getPuffleById(key) is not None

	def owns(self, puffle):
		return puffle in self

	def getPuffleById(self, _id):
		_id = int(_id)
		for p in self:
			if int(p.id) == _id:
				return p

		return None


	def append(self, key):
		if not isinstance(key, Puffle):
			return

		super(PuffleHandler, self).append(key)

	def __iadd__(self, key):
		if isinstance(key, Puffle):
			self.append(puffle)
		elif isinstance(key, list):
			for i in key:
				self.append(i)

		return self