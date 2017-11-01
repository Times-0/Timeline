from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, AVAILABLE_XML_PACKET_TYPES, NON_BLACK_HOLE_GAMES, MULTIPLAYER_GAMES
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.python.rebuild import rebuild
from twisted.internet import threads

from lxml.etree import fromstring as parseXML
from lxml import etree as XML

from collections import deque
import logging
import os, sys
import json

class Room (list):
	game = False

	def __init__(self, rh, _id, key, name, maxu, im, jump, item):
		super(Room, self).__init__()

		self.roomHandler = rh
		self.id = -int(_id)
		self.ext_id = int(_id)
		self.keyName = key
		self.name = name
		self.max = maxu
		self.member = bool(im)
		self.jumpable = jump
		self.requiredItem = item # Must be a list of items

	def append(self, client):
		if not isinstance(client, self.roomHandler.engine.protocol):
			return

		if client in self:
			return client.send('e', 200)

		if len(self) + 1 > self.max:
			return client.send('e', 210)

		if self.member and not client['member']:
			return client.send('e', 999)

		if self.requiredItem is not None:
			if not self.requiredItem in client['inventory']:
				return client.send('e', 212)

		super(Room, self).append(client)
		client.penguin.room = self

		self.onAdd(client)

	def onAdd(self, client):
		pass

	def onRemove(self, client):
		pass

	def remove(self, client):
		if not client in self:
			return

		self.send('rp', client.id)
		client.penguin.room = None

		super(Room, self).remove(client)
		self.onRemove(client)

	def send(self, *a):
		for c in self:
			c.send(*a)

	def __repr__(self):
		return "Room<{}#{}>".format(self.id, self.keyName)

	def __str__(self):
		return '%'.join(map(str, self))

	def __int__(self):
		return self.id

class Place(Room):

	def onAdd(self, client):
		client.send('jr', self.ext_id, self)
		self.send('ap', client)

	def __repr__(self):
		return "Place<{}#{}>".format(self.id, self.keyName)

class Game(Room):
	# Single Player (mostly?)

	game = True

	def onAdd(self, client):
		client.send('jg', self.ext_id)

class Arcade(Room):
	# Non black-hole stuff

	game = True

	def onAdd(self, client):
		client.send('jnbhg', self.ext_id)

class Multiplayer(Room):
	# Multiplayer? Know this is crazy, still :P

	game = True

'''
"110": {
	"room_id": 110,
	"room_key": "coffee",
	"name": "Coffee Shop",
	"display_name": "Coffee Shop",
	"music_id": 944,
	"is_member": 0,
	"path": "coffee.swf",
	"max_users": 80,
	"jump_enabled": false,
	"jump_disabled": true,
	"required_item": null,
	"short_name": "Coffee Shop"
	}
'''

class RoomHandler (object):

	def __init__(self, engine, package = 'configs/crumbs/rooms.json'):
		self.engine = engine
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.package = package

		self.rooms = deque()
		self.details = dict({Place:0, Arcade:0, Multiplayer:0, Game:0})

		self.setup()

	def setup(self):
		self.rooms.clear()

		if not os.path.exists(self.package):
			self.log("error", "rooms.json not found in path : ", self.package)
			sys.exit() # OOps!

		with open(self.package, 'r') as file:
			try:
				crumbs = json.loads(file.read())
				for r in crumbs:
					room = crumbs[r]
					_id = int(room['room_id'])
					key = room['room_key']
					name = room['display_name']
					maxu = room['max_users']
					jump = room['jump_enabled']
					item = room['required_item']
					member = room['is_member']

					game = key == ''

					if not game:
						self.rooms.append(Place(self, _id, key, name, maxu, member, jump, item))
						self.details[Place] += 1
						continue

					if _id in NON_BLACK_HOLE_GAMES:
						self.rooms.append(Arcade(self, _id, key, name, maxu, member, jump, item))
						self.details[Arcade] += 1
					elif _id > 990 or _id in MULTIPLAYER_GAMES:
						self.rooms.append(Multiplayer(self, _id, key, name, maxu, member, jump, item))
						self.details[Multiplayer] += 1
					else:
						self.rooms.append(Game(self, _id, key, name, max, member, jump, item))
						self.details[Game] += 1

			except Exception, e:
				self.log("error", "Error parsing JSON. E:", e)
				sys.exit()


			self.log('info', 'Loaded a total of', len(self.rooms), 'Room(s)')
			for r in self.details:
				self.log('info', 'Loaded', self.details[r], '{}(s)'.format(r.__name__))

	def log(self, l, *a):
		self.engine.log(l, '[RoomHandler] ', *a)

	def getRoomByExtId(self, _id):
		for room in self.rooms:
			if room.ext_id == _id:
				return room

		return None

	def getRoomById(self, _id):
		for room in self.rooms:
			if int(room) == _id:
				return room

		return None

	def getRoomByName(self, name):
		name = name.lower().strip()
		for room in self.rooms:
			if room.keyName.lower() == name:
				return rooms

		return None

	def __call__(self, key):
		return self.getRoomById(key)
	
	def __getitem__(self, key):
		if isinstance(key, int):
			return self.getRoomByExtId(key)
		elif isinstance(key, str):
			try:
				return self[int(key)]
			except:
				return self.getRoomByName(key)

		return None
