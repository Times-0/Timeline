from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Stamps import Stamp

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
import time


class StampHandler(list):
	def __init__(self, penguin):
		self.penguin = penguin

		self.penguin.penguin.recentStamps = list()

		self.setup()

	def __str__(self):
		return '|'.join(map(str, self))

	def setup(self):
		stamps = str(self.penguin.dbpenguin.stamps).split('|')
		for stamp in stamps:
			if stamp == '':
				continue
				
			_id, date = stamp.split(",")

			stamp = self.penguin.engine.stampCrumbs[_id]
			if stamp is None:
				continue

			self.append(stamp)

		self.penguin.send('gps', self.penguin['id'], self)

	def append(self, key):
		if not isinstance(key, Stamp):
			return

		super(StampHandler, self).append(key)

	def __iadd__(self, key):
		if isinstance(key, list):
			for i in key:
				self.append(i)

		else:
			self.append(key)

		return self