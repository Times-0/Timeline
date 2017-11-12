from Timeline.Server.Constants import TIMELINE_LOGGER
from twisted.internet.defer import Deferred

from collections import deque
import logging
import json
import os, sys

class Item(object):
	type = 0
	cost = 0
	id = -1
	name = None
	is_epf = False
	is_bait = False
	is_member = True

	item_by_type = dict({})

	def __init__(self, i, c, n, ie, ib, im):
		self.cost, self.id, self.name, self.is_epf, self.is_bait, self.is_member = c, i, n, ie, ib, im

	def __int__(self):
		return self.id

	def __repr__(self):
		return "Item<{}#{}>".format(self.name, self.id)

	def __str__(self):
		return str(self.id)

	def __eq__(self, i):
		if isinstance(i, int):
			return self.id == i
		elif isinstance(i, Item):
			return self.id == i.id
		elif isinstance(i, str):
			try:
				return self.id == int(i)
			except:
				pass

		return False

class Color(Item):
	type = 1

class Head(Item):
	type = 2

class Face(Item):
	type = 3

class Neck(Item):
	type = 4

class Body(Item):
	type = 5

class Hand(Item):
	type = 6

class Feet(Item):
	type = 7

class Pin(Item):
	type = 8

class Photo(Item):
	type = 9

class Award(Item):
	type = 10

for i in [Color,Head,Face,Neck,Body,Hand,Feet,Pin,Photo,Award]:
	Item.item_by_type[i.type] = i

class PaperItems(object):

	def __init__(self, engine, package = 'configs/crumbs/paper_items.json'):
		self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.items = deque()
		self.details = {i:0 for i in Item.item_by_type}

		self.package = package
		self.setup()

	def setup(self):
		self.items.clear()

		if not os.path.exists(self.package):
			self.log("error", "paper_items.json not found in path :", self.package)
			sys.exit() # OOps!

		with open(self.package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for paper in crumbs:
					_id = paper['paper_item_id']
					_type = paper['type']
					cost = paper['cost']
					im = paper['is_member']
					name = paper['label']
					ie = False if 'is_epf' not in paper else paper['is_epf'] == '1'
					ib = False if 'is_bait' not in paper else paper['is_bait'] == '1'

					self.items.append(Item.item_by_type[_type](_id, cost, name, ie, ib, im))
					self.details[_type] += 1

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()

		for t in self.details:
			self.log('info', "Loaded", self.details[t], Item.item_by_type[t].__name__, "Items")

		self.loadPins()

	def loadPins(self):
		package = 'configs/crumbs/pins.json'
		if not os.path.exists(package):
			self.log('error', "pins.json not found in path :", self.package)
			sys.exit()

		with open(package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for pin in crumbs:
					_id = pin['paper_item_id']
					time = pin['unix']

					pin_obj = self[_id]
					if pin_obj:
						pin_obj.release = time

			except Exception, e:
				self.log('error', "Error parsing JSON. E:", e)
				sys.exit()

	def getEPFItems(self):
		return [k for k in self.items if k.is_epf]

	def itemIsEPF(self, item):
		item = self.getItemById(item)
		if item is None:
			return False

		return item in self.getEPFItems()

	def getItemsByType(self, _type):
		if issubclass(_type, Item):
			_type = _type.type

		if not _type in Item.item_by_type:
			raise Exception("[TE5100] Unable to find any type with type-id {}".format(_type))

		items = list()
		for item in list(self.items):
			if item.type == _type:
				items.append(item)

		return items

	def getItemById(self, _id):
		_id = int(_id)

		for i in self.items:
			if i.id == _id:
				return i

		return None

	def getItemsByTypeName(self, name):
		_t = None
		_items = list()

		for i in Item.item_by_type:
			if Item.item_by_type[i].__name__.lower() == name.lower().strip():
				_t = Item.item_by_type[i].type
				break

		if not _t is None:
			_items = getItemsByType(_t)

		return _items

	def __getitem__(self, item):
		if isinstance(item, Item):
			item = self.getItemById(item.id)
		elif isinstance(item, str):
			try:
				item = int(item)
			except:
				item = str(item)
				item = self.getItemsByTypeName(item)
				return item if len(item) > 0 else False


		if item is None:
			return False

		item = self.getItemById(item)
		return item if item is not None else False

	def itemByIdIsType(self, _id, _type):
		item = self.getItemById(_id)
		if item == None:
			return False

		if isinstance(_type, int):
			_item = self.getItemById(_type)
			if _item == None:
				return False

			_type = Item.item_by_type[_item.type]

		elif isinstance(_type, str):
			_t = _type.lower().strip()
			_type = None

			for i in Item.item_by_type:
				if Item.item_by_type[i].__name__.lower() == _t:
					_type = Item.item_by_type[i]
					break

			if _type == None:
				return False

		elif not issubclass(_type, Item):
			return False

		return isinstance(item, _type)

	def log(self, l, *a):
		m = ['[Crumbs::Item]'] + list(a)
		self.engine.log(l, *m)