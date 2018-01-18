'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Engine is the main reactor, based on Twisted which starts the server and listens to given details
'''
from Timeline.Server.Constants import TIMELINE_LOGGER, WORLD_SERVER
from Timeline.Server.Redis import Redis
from Timeline.Utils.Events import Event, GeneralEvent
from Timeline.Utils.Crumbs import Items, Postcards, Igloo, Puffle, Stamps, Cards
from Timeline.Server.Room import RoomHandler
from Timeline.Utils.Plugins import getPlugins
from Timeline.Utils.Plugins.Abstract import ExtensibleObject

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor

from collections import deque
import logging

class AClient(Protocol):
	def makeConnection(self, t):
		t.write("%xt%e%-1%211%\x00")
		t.pauseProducing()
		t.loseConnection()

class Engine(Factory, ExtensibleObject):
	
	"""
	Implements the base class for reactor. Here is where things get sorted up!
	"""
	
	def __init__(self, protocol, _type, _id, name="World Server 1", _max=300):
		self.protocol = protocol
		self.type = _type
		self.id = _id
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.name = name
		self.users = deque() # Thread safe
		self.dbDetails = dict()
		self.maximum = _max - 1
		
		self.redis = Redis(self)

		self.log("info", "Timeline Factory Started!")
		self.log("info", "Running:", self.name)
		self.log("info", "Maximum users:", self.maximum)

		if self.type == WORLD_SERVER:
			self.initializeWorld()

		GeneralEvent('onEngine', self)

	def initializeWorld(self):
		# Set item crumbs
		self.itemCrumbs = Items.PaperItems(self)
		# Rooms handler!
		self.roomHandler = RoomHandler(self)
		# Postcards
		self.postcardHandler = Postcards.PostcardHandler(self)
		# igloo crumbs
		self.iglooCrumbs = Igloo.IglooHandler(self)
		# puffle handler
		self.puffleCrumbs = Puffle.PuffleCrumbHandler(self)
		# stamo handler
		self.stampCrumbs = Stamps.StampHandler(self)
		# CJ Card handler
		self.cardCrumbs = Cards.CardsHandler(self)

	def __repr__(self):
		return "<{}:{}#{}>".format(self.name, self.id, len(self.users))

	def getPenguinById(self, _id):
		_id = int(_id)
		for peng in self.users:
			if peng['id'] == _id:
				return peng

		return None

	def run(self, ip, port):
		self.ip, self.port = ip, port

		reactor.listenTCP(self.port, self, interface = ip)
		self.log("info", self.name, "listening on", "{0}:{1}".format(ip, port))

	def disconnect(self, client):
		if client in self.users:
			self.users.remove(client)

			return True

		self.redis.server.hmset("server:{}".format(self.id), {'population':len(self.users)})

		return False

	def buildProtocol(self, address):
		if len(self.users) > self.maximum:
			protocol = AClient()
			protocol.factory = self
			self.log("warn", "Client count overload, disposing it!")
			return protocol

		user = self.protocol(self)

		self.log("info", "Built new protocol for user#{0}".format(len(self.users)))
		self.users.append(user)

		self.redis.server.hmset("server:{}".format(self.id), {'population':len(self.users)})

		return user

	def log(self, type, *a):
		a = map(str, a)
		message = " ".join(a)
		message = "[{1}:{0}] {2}".format(self.name, self.type, message)
		
		if type == "info":
			self.logger.info(message)
		elif type == "warn":
			self.logger.warn(message)
		elif type == "error":
			self.logger.error(message)
		else:
			self.logger.debug(message)

	def connectionLost(self, reason):
		self.log('error', "Server exited! reason:", reason)
		
		self.redis.server.hmset("server:{}".format(self.id), {'population':0})