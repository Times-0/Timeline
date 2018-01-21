from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Igloo import IglooItem, FurnitureItem, FloorItem, LocationItem
from Timeline.Server.Room import Igloo as IglooRoom
from Timeline.Handlers.Games.CardJitsu import CJMat

from twisted.internet.defer import inlineCallbacks, returnValue
from twistar.dbobject import DBObject

from collections import deque
import logging
import time

class Igloo(DBObject):
	pass

class PenguinIglooItem(IglooItem):
	def __str__(self):
		return '|'.join(map(str, [self.id, self.date]))

class PenguinFurnitureItem(FurnitureItem):
	def __str__(self):
		return '|'.join(map(str, [self.id, self.date, self.quantity]))

class PenguinFloorItem(FloorItem):
	def __str__(self):
		return '|'.join(map(str, [self.id, self.date]))

class PenguinLocationItem(LocationItem):
	def __str__(self):
		return '|'.join(map(str, [self.id, self.date]))


class PenguinIglooHandler(list):

	def __init__(self, penguin):
		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.igloos = deque()
		self.currentIgloo = None

		self.furnitures = deque()
		self.floors = deque()
		self.locations = deque()

		self.setup()

	def getFurniture(self, _id):
		_id = int(_id)
		for i in self.furnitures:
			if i.id == _id:
				return i

		return None

	def hasFurniture(self, _id):
		return self.getFurniture(_id) != None

	def hasLocation(self, _id):
		return self.getLocation(_id) != None

	def getLocation(self, _id):
		_id = int(_id)
		for i in self.locations:
			if i.id == _id:
				return i

		return None

	def hasFloor(self, _id):
		return self.getFloor(_id) != None

	def getFloor(self, _id):
		_id = int(_id)
		for i in self.floors:
			if i.id == _id:
				return i

		return None

	def hasIgloo(self, _id):
		return self.getIgloo(_id) != None

	def getIgloo(self, _id):
		_id = int(_id)
		for i in self.igloos:
			if i.id == _id:
				return i

		return None

	@inlineCallbacks
	def setup(self):
		floors = self.penguin.dbpenguin.floors
		igloos = self.penguin.dbpenguin.igloos
		furnitures = self.penguin.dbpenguin.furnitures
		locations = self.penguin.dbpenguin.locations

		if floors == '' or floors == None:
			self.penguin.dbpenguin.floors = '0|{}'.format(self.penguin['age'].age)

		if igloos == '' or igloos == None:
			self.penguin.dbpenguin.igloos = '0|{0},1|{0}'.format(self.penguin['age'].age)

		if furnitures == '' or furnitures == None:
			self.penguin.dbpenguin.furnitures = '793|{}|1'.format(self.penguin['age'].age)

		if locations == '' or locations == None:
			self.penguin.dbpenguin.locations = '1|{}'.format(self.penguin['age'].age)

		self.penguin.dbpenguin.save() # for any updates?

		yield self.loadIgloos()
		yield self.loadCurrentIgloo()

		self.loadIglooDetails()

	@inlineCallbacks
	def createPenguinIgloo(self, _id):
		igloo = self.penguin.engine.iglooCrumbs.getPenguinIgloo(_id)
		if igloo is not None:
			returnValue(igloo)

		exists = yield self.penguin.db_getPenguin('id = ?', _id)
		if exists is None:
			returnValue(None)

		igloo = exists.igloo
		if igloo == 0:
			igloo = yield Igloo(owner = exists.id, location = 1, furniture = '', likes = '[]').save()
			exists.igloo = igloo.id
			exists.save()
		else:
			igloo = yield Igloo.find(igloo)


		iglooRoom = IglooRoom(self.penguin.engine.roomHandler, (1000 + exists.id), '{} igloo'.format(exists.id), "{}'s Igloo".format(exists.nickname), 100, False, False, None)
		iglooRoom.owner = int(exists.id)
		iglooRoom.opened = not bool(igloo.locked)
		iglooRoom._id = int(igloo.id)

		self.penguin.engine.iglooCrumbs.penguinIgloos.append(iglooRoom)

		returnValue(iglooRoom)


	@inlineCallbacks
	def loadIgloos(self):
		igloos = yield Igloo.find(where = ['owner = ?', self.penguin['id']], orderby = 'id DESC')

		for i in igloos:
			self.append(i)

	@inlineCallbacks
	def loadCurrentIgloo(self):
		if self.find(self.penguin.dbpenguin.igloo) is None:
			igloo = yield Igloo(owner = self.penguin['id'], location = 1, furniture = '', likes = '[]').save()
			yield igloo.refresh()
			self.penguin.dbpenguin.igloo = igloo.id
			self.penguin.dbpenguin.save()
			
		else:
			igloo = self.find(self.penguin.dbpenguin.igloo)

		self.currentIgloo = igloo

		iglooRoom = self.penguin.engine.iglooCrumbs.getPenguinIgloo(self.penguin['id'])
		if iglooRoom == None:
			iglooRoom = IglooRoom(self.penguin, (1000 + self.penguin['id']), '{} igloo'.format(self.penguin['id']), "{}'s Igloo".format(self.penguin['nickname']), 100, False, False, None)
			iglooRoom.owner = int(self.penguin['id'])
			
			iglooRoom.opened = not bool(self.currentIgloo.locked)
			iglooRoom._id = int(self.currentIgloo.id)

			self.penguin.engine.iglooCrumbs.penguinIgloos.append(iglooRoom)

		self.penguin.penguin.igloo = iglooRoom
		self.filterCJMats()

	def __contains__(self, key):
		if isinstance(key, Igloo):
			key = igloo.id

		return self.find(key) != None

	def find(self, _id):
		_id = int(_id)
		for igloo in self:
			if int(igloo.id) == _id:
				return igloo

		return None

	def __iadd__(self, a):
		if isinstance(a, list):
			for k in a:
				self.append(a)
		elif isinstance(a, Igloo):
			self.append(a)

		return self

	def append(self, igloo):
		if not isinstance(igloo, Igloo):
			return

		super(PenguinIglooHandler, self).append(igloo)

	def loadIglooDetails(self):
		floors = str(self.penguin.dbpenguin.floors).split(',')
		igloos = str(self.penguin.dbpenguin.igloos).split(',')
		furnitures = str(self.penguin.dbpenguin.furnitures).split(',')
		locations = str(self.penguin.dbpenguin.locations).split(',')

		for floor in floors:
			_id, date = map(int, floor.split('|'))
			floor = self.penguin.engine.iglooCrumbs.getFloorById(_id)
			if floor is None:
				continue

			floor = PenguinFloorItem(floor.id, floor.name, floor.cost)
			floor.date = date

			self.floors.append(floor)

		for igloo in igloos:
			_id, date = map(int, igloo.split('|'))
			igloo = self.penguin.engine.iglooCrumbs.getIglooById(_id)
			if igloo is None:
				continue

			igloo = PenguinIglooItem(igloo.id, igloo.name, igloo.cost)
			igloo.date = date

			self.igloos.append(igloo)

		for location in locations:
			_id, date = map(int, location.split('|'))
			location = self.penguin.engine.iglooCrumbs.getLocationById(_id)
			if location is None:
				continue

			location = PenguinLocationItem(location.id, location.name, location.igloo, location.cost)
			location.date = date

			self.floors.append(location)

		for furniture in furnitures:
			_id, date, quantity = map(int, furniture.split('|'))
			furniture = self.penguin.engine.iglooCrumbs.getFurnitureById(_id)
			if furniture is None:
				continue

			furniture = PenguinFurnitureItem(furniture.id, furniture.type, furniture.cost, furniture.name, furniture.is_member, furniture.max)
			furniture.date = date
			furniture.quantity = quantity

			self.furnitures.append(furniture)

	def filterCJMats(self):
		CardJitsuWaddleId = 200
		self.penguin.engine.roomHandler.ROOM_CONFIG.WADDLES[self.penguin['igloo'].id] = []

		furnitures = map(lambda x: int(x.split('|')[0]), self.currentIgloo.furniture.split(',')) if self.currentIgloo.furniture != '' and self.currentIgloo.furniture is not None else []
		
		for f in furnitures:
			if f == 786:
				self.addCJMat(CardJitsuWaddleId)
				CardJitsuWaddleId += 1

	def addCJMat(self, wid):
		WADDLES = self.penguin.engine.roomHandler.ROOM_CONFIG.WADDLES
		if self.penguin['igloo'].id not in WADDLES:
			WADDLES[self.penguin['igloo'].id] = list()

		Mat = CJMat(self.penguin.engine.roomHandler, wid, "JitsuMat", "Card Jitsu Mat", 3, False, False, None)
		Mat.waddle = wid
		Mat.room = self.penguin['igloo']

		WADDLES[self.penguin['igloo'].id].append(Mat)

		self.logger.info("Added CardJitsu-Mat [%s] to %s's igloo.", wid, self.penguin['nickname'])