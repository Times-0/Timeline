from Timeline.Server.Constants import TIMELINE_LOGGER
from twisted.internet.defer import Deferred

from collections import deque
import logging
import json
import os, sys

class Stamp(object):
	def __init__(self, sid, name, difficulty, rank, im, desc, group, parent, parent_name):
		self.id = int(sid)
		self.name = str(name)
		self.difficulty = type('StampDifficulty', (object, ), {'token' : str(difficulty), 'rank' : int(rank)})
		self.member = bool(int(im))
		self.description = str(desc)
		self.group = int(group)
		self.parent = type('StampParent', (object, ), {'id' : int(parent), 'name' : str(parent_name)})

	def __repr__(self):
		return "Stamp<{}#{}>".format(self.name, self.id)

	def __str__(self):
		return str(self.id)

	def __int__(self):
		return self.id

class StampHandler(object):
	def __init__(self, engine, package = 'configs/crumbs/stamps.json'):
		self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.package = package

		self.stamps = deque()
		self.cover = dict({})
		self.setup()

	def setup(self):
		self.stamps.clear()

		if not os.path.exists(self.package):
			self.log("error", "stamps.json not found in path :", self.package)
			sys.exit() # OOps!

		with open(self.package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for stamp in crumbs:
					p_id = stamp['parent_group_id']
					group = stamp['group_id']
					p_name = stamp['name']

					for s in stamp['stamps']:
						s_id = s['stamp_id']
						name = s['name']
						im = s['is_member']
						rank = s['rank']
						token = s['rank_token']
						desc = s['description']

						self.stamps.append(Stamp(s_id, name, token, rank, im, desc, group, p_id, p_name))

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()

		if not os.path.exists('configs/crumbs/cover.json'):
			self.log('error', "cover.json not found in path : configs/crumbs/cover.json")
			sys.exit()

		with open('configs/crumbs/cover.json', 'r') as file:
			try:
				crumbs = json.loads(file.read())

				self.cover['patterns'] = map(int, crumbs['pattern'])
				self.cover['icons'] = map(int, crumbs['clasp'])
				self.cover['highlights'] = map(int, crumbs['highlight'].keys())
				self.cover['colors'] = map(int, crumbs['color_logo'].keys())

			except:
				self.log("error", "Error parsing JSON. E:", e)

		self.log('info', "Loaded", len(self.stamps), "Stamp(s)")
		self.log("info", 'Loaded Stampbook cover details')

	def __getitem__(self, key):
		key = int(key)

		for stamp in self.stamps:
			if int(stamp) == key:
				return stamp

		return None

	def log(self, l, *a):
		self.engine.log(l, '[Crumbs::Stamps]', *a)