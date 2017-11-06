#-*-coding: utf-8-*-
from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Postcards import Postcard

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
import time, os, sys, json

class IglooItem(object):
	def __init__(self, _id, name, cost):
		self.id = int(_id)
		self.name = str(name)
		self.cost = int(cost)

	def __str__(self):
		return str(self.id)

	def __repr__(self):
		return "IglooItem<{}#{}>".format(self.name, self.id)

	def __int__(self):
		return self.id

class FloorItem(object):
	def __init__(self, _id, name, cost):
		self.id = int(_id)
		self.name = str(name)
		self.cost = int(cost)

	def __str__(self):
		return str(self.id)

	def __repr__(self):
		return "FloorItem<{}#{}>".format(self.name, self.id)

	def __int__(self):
		return self.id

class FurnitureItem(object):
	def __init__(self, _id, _type, cost, name, is_member, _max):
		self.id = int(_id)
		self.type = int(_type)
		self.cost = int(cost)
		self.name = str(name)
		self.is_member = bool(is_member)
		self.max = int(_max)

	def __str__(self):
		return str(self.id)

	def __int__(self):
		return self.id

	def __repr__(self):
		return "FurnitureItem<{}#{}>".format(self.name, self.id)

class LocationItem(object):
	def __init__(self, _id, name, igloo, cost):
		self.id = int(_id)
		self.name = str(name)
		self.igloo = int(igloo)
		self.cost = int(cost)

class IglooHandler(object):

	def __init__(self, engine, package = 'configs/crumbs/'):
		self.engine = engine
		self.package = package
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.igloos = deque()
		self.furnitures = deque()
		self.floors = deque()
		self.locations = deque()

		self.penguinIgloos = deque()

		self.setup()

	def getPenguinIgloo(self, _id):
		_id = int(_id)
		for igloo in list(self.penguinIgloos):
			if igloo.owner == _id:
				return igloo

		return None

	def setup(self):
		self.loadIglooCrumbs()
		self.loadFurnCrumbs()
		self.loadFloorCrumbs()
		self.loadLocationCrumbs()

	def getIglooById(self, _id):
		_id = int(_id)
		for i in self.igloos:
			if i.id == _id:
				return i

		return None

	def getFurnitureById(self, _id):
		_id = int(_id)
		for i in self.furnitures:
			if i.id == _id:
				return i

		return None

	def getFloorById(self, _id):
		_id = int(_id)
		for i in self.floors:
			if i.id == _id:
				return i

		return None

	def getLocationById(self, _id):
		_id = int(_id)
		for i in self.locations:
			if i.id == _id:
				return i

		return None

	def loadIglooCrumbs(self):
		package = self.package + 'igloos.json'
		if not os.path.exists(package):
			self.log('error', 'igloos.json not found in path :', package)
			sys.exit()

		with open(package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for _id in crumbs:
					igloo = crumbs[_id]
					self.igloos.append(IglooItem(igloo['igloo_id'], igloo['name'], igloo['cost']))

			except Exception, e:
				self.log('error', 'Error parsing JSON. E :', e)

		self.log('info', 'Loaded', len(self.igloos), 'Igloo(s)')

	def loadFurnCrumbs(self):
		package = self.package + 'furniture_items.json'
		if not os.path.exists(package):
			self.log('error', 'furniture_items.json not found in path :', package)
			sys.exit()

		with open(package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for furn in crumbs:
					_id = furn['furniture_item_id']
					_t = furn['type']
					cost = furn['cost']
					name = furn['label']
					im = int(furn['is_member_only'])
					_max = furn['max_quantity']

					self.furnitures.append(FurnitureItem(_id, _t, cost, name, im, _max))

			except Exception, e:
				self.log('error', 'Error parsing JSON. E :', e)

		self.log('info', 'Loaded', len(self.furnitures), 'Furniture(s)')

	def loadFloorCrumbs(self):
		package = self.package + 'igloo_floors.json'
		if not os.path.exists(package):
			self.log('error', 'igloo_floors.json not found in path :', package)
			sys.exit()

		with open(package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for floor in crumbs:
					self.floors.append(FloorItem(floor['igloo_floor_id'], floor['label'], floor['cost']))

			except Exception, e:
				self.log('error', 'Error parsing JSON. E :', e)

		self.log('info', 'Loaded', len(self.floors), 'Floor(s)')

	def loadLocationCrumbs(self):
		package = self.package + 'igloo_locations.json'
		if not os.path.exists(package):
			self.log('error', 'igloo_locations.json not found in path :', package)
			sys.exit()

		with open(package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for location in crumbs:
					self.locations.append(LocationItem(location['igloo_location_id'], location['name'], location['igloo_id'], location['cost']))

			except Exception, e:
				self.log('error', 'Error parsing JSON. E :', e)

		self.log('info', 'Loaded', len(self.floors), 'Location(s)')

	def log(self, l, *a):
		self.engine.log(l, '[Crumbs::Igloo]', *a)