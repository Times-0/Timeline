from Timeline.Server.Constants import TIMELINE_LOGGER
from twisted.internet.defer import Deferred

from collections import deque
import logging
import json
import os, sys

class PuffleCrumb(object):
	def __init__(self, _id, type, n, h, hu, r, m):
		self.type = int(_id)
		self.sub_type = int(type)
		self.name = n + ' Puffle'
		self.health = int(h)
		self.hunger = int(hu)
		self.rest = int(r)
		self.member = bool(m)

	def __str__(self):
		return str(self.id)

	def __int__(self):
		return self.id

	def __repr__(self):
		return "{}<{}#{}>".format(self.name, self.type, self.sub_type)

class PuffleCrumbHandler(object):
	def __init__(self, engine, package = 'configs/crumbs/puffles.json'):
		self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.package = package

		self.puffles = deque()
		self.defautPuffles = dict({})

		self.puffleItems = dict({})

		self.setup()

	def setup(self):
		self.puffles.clear()
		self.defautPuffles.clear()

		if not os.path.exists(self.package):
			self.log("error", "puffles.json not found in path :", self.package)
			sys.exit() # OOps!

		with open(self.package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for puffle in crumbs['default']:
					_id = int(puffle['puffle_id'])
					maxhe, maxhu, maxr = int(puffle['max_health']), int(puffle['max_hunger']), int(puffle['max_rest'])

					self.defautPuffles[_id] = (maxhe, maxhu, maxr)

				for puffle in crumbs['all']:
					sub_type = int(puffle['puffle_id'])
					_type = int(puffle['parent_puffle_id'])
					name = puffle['description']
					member = bool(puffle['is_member_only'])

					if not _type in self.defautPuffles:
						maxhe, maxhu, maxr = 100, 100, 100
					else:
						maxhe, maxhu, maxr = self.defautPuffles[_type]
						
					self.puffles.append(PuffleCrumb(_type, sub_type, name, maxhe, maxhu, maxr, member))

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()

		self.log('info', "Loaded", len(self.puffles), "Type of Puffle(s)")
		self.loadPuffleItems()

	def loadPuffleItems(self):
		self.puffleItems.clear()
		package = self.package.replace('puffles.json', 'puffle_items.json')

		if not os.path.exists(package):
			self.log("error", "puffle_items.json not found in path :", package)
			sys.exit() # OOps!

		with open(package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for puffle in crumbs:
					self.puffleItems[int(puffle['puffle_item_id'])] = puffle

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()

		self.log('info', "Loaded", len(self.puffles), "Puffle item(s)")

	def getPuffleBySubType(self, st):
		st = int(st)
		for puffle in self.puffles:
			if puffle.sub_type == st:
				return puffle

		return None

	def __getitem__(self, key):
		return self.getPuffleBySubType(key)

	def log(self, l, *x):
		self.engine.log(l, '[Crumbs::Puffle]', *x)