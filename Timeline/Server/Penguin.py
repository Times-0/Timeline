'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Penguin is a extension of LineReceiver, protocol. Implements the base of Client Object
'''

from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, WORLD_SERVER
from Timeline.Utils.Events import Event
from Timeline.Utils.Cryptography import Crypto
from Timeline.Server.Packets import PacketHandler
from Timeline.Database.DB import PenguinDB, Ban
from Timeline import Username, Password, Nickname, Inventory, Membership, Coins, Age, Cache, EPFAgent
from Timeline.Utils.Mails import MailHandler
from Timeline.Utils.Igloo import PenguinIglooHandler
from Timeline.Utils.Puffle import PuffleHandler
from Timeline.Utils.Stamps import StampHandler
from Timeline.Utils.Crumbs.Items import Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo, Award

from twisted.protocols.basic import LineReceiver
from twisted.internet import threads
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue

from repr import Repr
from collections import deque
import logging
import time
from math import ceil

class Penguin(LineReceiver, PenguinDB):

	delimiter = chr(0)

	def __init__(self, engine):
		super(Penguin, self).__init__()
		
		self.factory = self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.errored = None

		self.buildPenguin()

	def buildPenguin(self):
		self.handshakeStage = -1

		self.canRecvPacket = False
		self.ReceivePacketEnabled = True # Penguin can receive packet only if both this and self.canRecvPacket is true.

		# Some XT packets are sent before J#JS to make sure client is alive, just to make sure to ignore it ;)
		# ('category', 'handler', 0 or 1 : execute : don't execute)
		self.ignorableXTPackets = [('s', 'j#js', 1), ('s', 'p#getdigcooldown', 0), ('s', 'u#h', 0)] 

		self.penguin = PenguinObject()
		self.penguin.name = None
		self.penguin.id = None

		self.penguin.room = None
		self.penguin.prevRooms = list()

		# Initiate Packet Handler
		self.PacketHandler = PacketHandler(self)
		self.CryptoHandler = Crypto(self)

	def initialize(self):
		self.penguin.nickname = Nickname(self.dbpenguin.nickname, self)
		self.penguin.inventory = Inventory(self)
		self.penguin.inventory.parseFromString(self.dbpenguin.inventory)

		self.penguin.member = Membership(self.dbpenguin.membership, self)
		self.penguin.moderator = False #:P
		self.penguin.epf = False #TODO

		self.penguin.x = self.penguin.y = self.penguin.frame = self.penguin.avatar = 0

		self.penguin.coins = Coins(self.dbpenguin.coins, self)
		self.penguin.age = Age(self.dbpenguin.create, self)

		self.penguin.cache = Cache(self)
		self.penguin.muted = False

		self.penguin.epf = EPFAgent(self.dbpenguin.agent, str(self.dbpenguin.epf), self)
		
		clothing = [Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo]
		for cloth in clothing:
			name = cloth.__name__.lower()
			self.penguin[name] = cloth(0, 0, name + " item", False, False, False)

		self.penguin.mail = MailHandler(self)
		self.penguin.iglooHandler = PenguinIglooHandler(self)
		self.penguin.puffleHandler = PuffleHandler(self)
		self.penguin.stampHandler = StampHandler(self)

		self.loadClothing()

	def loadClothing(self):
		clothing = [Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo]
		for c in clothing:
			name = c.__name__.lower()

			db_c = getattr(self.dbpenguin, name)
			if self.engine.itemCrumbs.itemByIdIsType(db_c, c):
				self.penguin[name] = self.engine.itemCrumbs[db_c]


	def checkPassword(self, password):
		return self.CryptoHandler.loginHash() == password
		
	@inlineCallbacks
	def banned(self):
		bans = yield Ban.find(where = ['player = ? AND expire > CURRENT_TIMESTAMP', self['id']], limit = 1)
		if bans is None:
			returnValue(False)

		now = int(time.time())
		expire = int(time.mktime(bans.expire.timetuple()))
		hours = (expire - now)/(60*60.0)

		if 0 < hours < 1:
			# only minutes left
			minutes = int(hours * 60)
			self.send('e', 602, minutes)
			returnValue(True)

		if hours <= 0:
			returnValue(False) # who knows, a millisencond counts too! LOL

		self.send('e', 601, int(hours))
		self.disconnect()

		returnValue(True)

	def handleCrossDomainPolicy(self):
		self.send("<cross-domain-policy><allow-access-from domain='*' to-ports='{0}' /></cross-domain-policy>".format(self.engine.port))
		self.disconnect()

	def getPortableName(self):
		if self["username"] == None and self["id"] == None:
			return self.client

		if self["username"] != None:
			return self["username"]

		if self["id"] != None:
			return self["id"]

		return self["username"]

	def addItem(self, item):
		if isinstance(item, int):
			item = self.engine.itemCrumbs[item]
		elif isinstance(item, str):
			try:
				item = self.engine.itemCrumbs[int(item)]
			except:
				item = None

		if item is None:
			return False

		cost = item.cost
		if int(self.penguin.coins) < cost:
			self.send('e', 401)
			return False

		if item in self.penguin.inventory:
			return False

		self.penguin.inventory.append(item)
		self.penguin.coins -= cost
		return True

	def __str__(self):
		walking_id = walking_item = walking_type = walking_subtype = ''
		
		if self['puffleHandler'].walkingPuffle is not None:
			puffle = self['puffleHandler'].walkingPuffle

			walking_id = int(puffle.id)
			walking_item = int(puffle.hat)
			walking_type = int(puffle.type)
			walking_subtype = int(puffle.subtype)

		data = [
			self['id'],			
			self['nickname'],

			45,						#Language, 45=English

			self['color'],		
			self['head'],
			self['face'],
			self['neck'],
			self['body'],
			self['hand'],
			self['feet'],
			self['photo'],
			self['pin'],

			self['x'],				#Cached coordinates
			self['y'],				#Cached coordinates
			self['frame'],

			int(int(self['member']) > 0),#Is member
			int(self['member']),			#Membership days remaining

			self['avatar'],			#wtf?
			None,
			None,					#Party Info

			walking_id, 
			walking_item, 
			walking_type,
			walking_subtype,
			0 # DEFAULT_STATE #TODO Add golden state
		]

		return '|'.join(map(str, data))


	# Easy access to penguin properties
	def __getitem__(self, prop):
		return getattr(self.penguin, prop)

	def __setitem__(self, prop, val):
		self.penguin[prop] = val

	def checkForExceptions(self, err):
		self.errored = err
		self.engine.log("error", self.getPortableName(), self.errored.getErrorMessage())

	def lineReceived(self, line):
		me = self.getPortableName()
		self.engine.log("debug", "[RECV]", me, line)

		receivedPacketDefer = self.PacketHandler.handlePacketReceived(line)
		receivedPacketDefer.addErrback(self.checkForExceptions)
		# Defer some other stuff? Probably?

	def send(self, *args):
		buffers = list(args)
		if len(buffers) < 1:
			return

		if len(buffers) == 1:
			self.engine.log("debug", "[SEND]", self.getPortableName(), buffers[0])
			return self.sendLine(buffers[0])

		server_internal_id = "-1"
		if self.penguin.room != None:
			server_internal_id = int(self.penguin.room)

		buffering = ['', PACKET_TYPE]
		buffering.append(buffers[0])
		buffering.append(server_internal_id)

		buffering += buffers[1:]
		buffering.append('')

		buffering = PACKET_DELIMITER.join(list(map(str, buffering)))
		self.engine.log("debug", "[SEND]", self.getPortableName(), buffering)
		return self.sendLine(buffering)
		
	def log(self, l, *a):
		self.engine.log(l, self.getPortableName(), *a)


	def disconnect(self):
		self.transport.loseConnection()
		return

	@inlineCallbacks
	def connectionLost(self, reason):
		self.engine.log("info", self.getPortableName(), "Disconnected!")

		if not self.penguin.room is None:
			self.penguin.room.remove(self)

		if self.engine.type == WORLD_SERVER and self.penguin.id != None:
			yield self.engine.redis.server.delete("online:{}".format(self.penguin.id))
			yield self.engine.redis.server.hincrby('server:{}'.format(self.engine.id), 'population', -1)

			if self['igloo'] is not None:
				self['igloo'].opened = False
				self['iglooHandler'].currentIgloo.locked = True

				yield self['iglooHandler'].currentIgloo.save()

			if self['puffleHandler'] is not None:
				for puffle in self['puffleHandler']:
					puffle.walking = 0
					puffle.save()


		self.engine.disconnect(self)

	def makeConnection(self, transport):
		self.transport = self.client = transport
		self.connectionMade = True

		self.engine.log("info", "New client connection:", self.client)

class PenguinObject(dict):

	def __init__(self, value=None):
		dict.__init__(self)
		self.POvalue = value

	def __repr__(self):
		values = list()

		for i, j in dict.iteritems(self):
			values.append("{0}={1}".format(i, j))

		values = ", ".join(values)
		return "<{0}: {1}>".format(self.__class__.__name__, values)

	def __getitem__(self, key):
		try:
			value = (dict.__getitem__(self, key))
		except:
			value = None
			dict.__setitem__(self, key, value)
		finally:
			return value

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)

	def __setattr__(self, attr, value):

		dict.__setitem__(self, attr, value)
		object.__setattr__(self, attr, value)

	def __getattr__(self, attr):
		try:
			value = (dict.__getitem__(self, attr))
		except:
			value = None
			dict.__setitem__(self, attr, value)
		finally:
			return value