'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Penguin is a extension of LineReceiver, protocol. Implements the base of Client Object
'''

from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, WORLD_SERVER
from Timeline.Utils.Events import Event
from Timeline.Utils.Cryptography import Crypto
from Timeline.Server.Packets import PacketHandler
from Timeline.Database.DB import PenguinDB
from Timeline import Username, Password, Nickname, Inventory, Membership, Coins, Age, Cache
from Timeline.Utils.Mails import MailHandler
from Timeline.Utils.Igloo import PenguinIglooHandler
from Timeline.Utils.Crumbs.Items import Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo, Award

from twisted.protocols.basic import LineReceiver
from twisted.internet import threads
from twisted.internet.defer import Deferred, inlineCallbacks

from repr import Repr
from collections import deque
import logging

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

		self.penguin = PenguinObject() # POvalue should be penguin name. Sooner.
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
		self.penguin.mail = MailHandler(self)

		self.penguin.member = Membership(self.dbpenguin.membership, self)
		self.penguin.moderator = False #:P
		self.penguin.epf = False #TODO

		self.penguin.x = self.penguin.y = self.penguin.frame = self.penguin.avatar = 0 #TODO

		self.penguin.coins = Coins(self.dbpenguin.coins, self)
		self.penguin.age = Age(self.dbpenguin.create, self)

		self.penguin.cache = Cache(self)
		
		clothing = [Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo]
		for cloth in clothing:
			name = cloth.__name__.lower()
			self.penguin[name] = cloth(0, 0, name + " item", False, False, False)

		self.penguin.iglooHandler = PenguinIglooHandler(self)

	def checkPassword(self, password):
		return self.CryptoHandler.loginHash() == password
		
	def banned(self):
		return False #TODO

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
		if self.coins < cost:
			self.send('e', 401)
			return False

		if item in self.penguin.inventory:
			return False

		self.penguin.inventory += item
		return True

	def __str__(self):
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

			int(self['member'] > 0),#Is member
			self['member'],			#Membership days remaining

			self['avatar'],			#wtf?
			None,
			None,					#Party Info

			'', '' #Walking puffle's id and item. TODO
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