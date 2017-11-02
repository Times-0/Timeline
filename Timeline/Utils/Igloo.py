from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Postcards import Postcard

from twisted.internet.defer import inlineCallbacks, returnValue
from twistar.dbobject import DBObject

from collections import deque
import logging
import time

class Igloo(DBObject):
	pass

class IglooHandler(object):

	def __init__(self, penguin, package = 'configs/crumbs/')
		self.penguin = penguin
		self.package = package
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.setup()

	def setup(self):
		pass