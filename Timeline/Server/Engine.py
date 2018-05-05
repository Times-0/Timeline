'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Engine is the main reactor, based on Twisted which starts the server and listens to given details
'''
from Timeline.Server.Constants import TIMELINE_LOGGER, WORLD_SERVER
from Timeline.Server.Redis import Redis
from Timeline.Utils.Events import Event, GeneralEvent
from Timeline.Utils.Crumbs import Items, Postcards, Igloo, Puffle, Stamps, Cards
from Timeline.Server.Music import MusicTrackEngine
from Timeline.Server.Room import RoomHandler
from Timeline.Utils.Plugins import getPlugins
from Timeline.Utils.Plugins.Abstract import ExtensibleObject

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

from collections import deque
import logging
import weakref

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
		self._listening = False
		self._portListener = None

		self.proxyReference = weakref.proxy(self)

		self.redis = Redis(self)

		self.log("info", "Timeline Factory Started!")
		self.log("info", "Running:", self.name)
		self.log("info", "Maximum users:", self.maximum)

		if self.type == WORLD_SERVER:
			self.initializeWorld()

		self.redis.redisConnectionDefer.addCallback(lambda *x: GeneralEvent('onEngine', self))

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
		# SoundStudio music handler
		self.musicHandler = MusicTrackEngine(self)

	def __repr__(self):
		return "<{}:{}#{}>".format(self.name, self.id, len(self.users))

	def getPenguinById(self, _id):
		_id = int(_id)
		users = list(self.users)
		for peng in users:
			if peng['id'] == _id:
				return peng.selfRefer

		return None

	def run(self, ip, port):
		if self._listening:
			raise Exception("%s already listening. An engine can only listen to 1 TCP/IP/PORT.", self)

		self.ip, self.port = ip, port

		self._portListener = reactor.listenTCP(self.port, self, interface = ip)
		self.log("info", self.name, "listening on", "{0}:{1}".format(ip, port))
		self._listening = True

	@inlineCallbacks
	def disconnect(self, client):
		GeneralEvent('onClientRemove', client.selfRefer)

		if client in self.users:
			self.users.remove(client)
			yield self.redis.server.hmset("server:{}".format(self.id), {'population':len(self.users)})

			returnValue(True)

		returnValue(False)

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

	@inlineCallbacks
	def connectionLost(self, reason):
		self.log('warn', "Server exiting! reason:", reason)
		
		#yield self._portListener.stopListening()

		user = None
		for user in list(self.users):
			self.users.remove(user)
			user.canRecvPacket = user.ReceivePacketEnabled = False
			user.disconnect()
			yield user.cleanConnectionLost

		yield self.redis.server.hmset("server:{}".format(self.id), {'population':0})