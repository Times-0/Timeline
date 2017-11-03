from Timeline.Server.Constants import TIMELINE_LOGGER
from twisted.internet.defer import Deferred

from collections import deque
import logging
import json
import os, sys

class Postcard(object):
	def __init__(self, _id, sub, avail, categ):
		self.id = _id
		self.subject = sub
		self.available = avail
		self.category = categ

	def __repr__(self):
		return "Postcard<{1}#{0}>".format(self.id, self.subject)

	def __int__(self):
		return self.id

	def __str__(self):
		return str(self.subject)


class PostcardHandler(object):
	def __init__(self, engine, package = 'configs/crumbs/postcards.json'):
		self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.package = package

		self.postcards = deque()
		self.setup()

	def setup(self):
		self.postcards.clear()

		if not os.path.exists(self.package):
			self.log("error", "postcards.json not found in path :", self.package)
			sys.exit() # OOps!

		with open(self.package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for posts in crumbs:
					for post in crumbs[posts]:
						if post == 'order_position':
							continue

						_id = int(post)
						sub = crumbs[posts][post]['subject']
						avail = crumbs[posts][post]['in_catalog']

						self.postcards.append(Postcard(_id, sub, avail, posts))

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()

		self.log('info', "Loaded", len(self.postcards), "Postcard(s)")

	def __getitem__(self, key):
		key = int(key)
		for post in self.postcards:
			if int(post) == key:
				return post

		return None

	def getPostcard(self, _id):
		return self[_id]

	def __contains__(self, _id):
		return self[_id] is not None

	def log(self, l, *a):
		self.engine.log(l, '[Crumbs:Post]', *a)