from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, AVAILABLE_XML_PACKET_TYPES, NON_BLACK_HOLE_GAMES, MULTIPLAYER_GAMES
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Plugins.Abstract import ExtensibleObject

from twisted.python.rebuild import rebuild
from twisted.internet import threads

from lxml.etree import fromstring as parseXML
from lxml import etree as XML

from collections import deque
import logging
import os, sys
import json
import traceback

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

    def onInit(self):
        pass

    def deChequeReferences(self):
        for i, k in enumerate(self):
            try:
                k['nickname']
            except ReferenceError:
                del self[i]

    def append(self, client):
        self.deChequeReferences()
        if not isinstance(client, self.roomHandler.engine.protocol):
            return

        if client in self:
            return #client.send('e', 200)

        if len(self) + 1 > self.max:
            return client.send('e', 210)

        if self.member and not client['member']:
            return client.send('e', 999)

        if self.requiredItem is not None:
            for i in self.requiredItem:
                if not client['RefreshHandler'].inInventory(i):
                    return client.send('e', 212)

        super(Room, self).append(client)
        client.penguin.room = self

        client.engine.redis.server.hmset("online:{}".format(client.penguin.id),
                                         {'place': self.ext_id, 'place_name': self.name})

        GeneralEvent.call('joined-room', client, self.id)
        GeneralEvent.call('joined-room-{}'.format(self.ext_id), client, self.ext_id)

        self.onAdd(client)

    def onAdd(self, client):
        try:
            self.deChequeReferences()
            super(Room, self).onAdd(client)
        except:
            pass

    def onRemove(self, client):
        try:
            self.deChequeReferences()
            super(Room, self).onRemove(client)
        except:
            pass

    def remove(self, client):
        self.deChequeReferences()
        if not client in self:
            return

        self.send('rp', client['id'])
        client.penguin.room = None
        client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'place' : 0})

        super(Room, self).remove(client) if client in self else None
        client.penguin['prevRooms'].append(self)
        self.onRemove(client)

    def send(self, *a):
        self.deChequeReferences()
        for c in self:
            c.send(*a)

    def sendExcept(self, e, *a):
        self.deChequeReferences()
        for c in self:
            if not c['id'] == e:
                c.send(*a)

    def __repr__(self):
        return "Room<{}#{}>".format(self.id, self.keyName)

    def __str__(self):
        self.deChequeReferences()
        return '%'.join(map(str, [_ for _ in self if not _['stealth_mode']]))

    def __int__(self):
        return self.id

class Place(Room):

    def onAdd(self, client):
        super(Place, self).onAdd(client)

        client.send('jr', self.ext_id, *((self, ) if len(str(self)) > 0 else []))
        self.send('ap', client) if not client['stealth_mode'] else client.send('ap', client)
        if client['mascot_mode']:
            GeneralEvent("mascot:{}-joined-room".format(client['nickname']), self)

        self.checkForMascotPresence()

    def checkForMascotPresence(self):
        mascots = set(m['nickname'] for m in self if m['mascot_mode'])
        if len(mascots) < 1:
            return

        penguins = [p for p in self if not p['mascot_mode']]

        [GeneralEvent("mascot-joined-room", self, mascot, penguins) for mascot in mascots]
        self.roomHandler.engine.log("info", "Mascot presence found in room: ", self.name)

    def __repr__(self):
        return "Place<{}#{}>".format(self.id, self.keyName)

class Game(Room):
    # Single Player (mostly?)

    game = True
    stamp_id = None

    def onAdd(self, client):
        super(Game, self).onAdd(client)

        client.send('jg', self.ext_id)

        client.penguin.playing = True
        client.penguin.previousGame = self

        client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'playing' : 1})

    def onRemove(self, client):
        client.penguin.playing = False

        client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'playing' : 0})

class Arcade(Game):
    # Non black-hole stuff

    game = True

    def onAdd(self, client):
        super(Arcade, self).onAdd(client)

        client.send('jnbhg', self.ext_id)

        client.penguin.playing = True
        client.penguin.previousGame = self

        client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'playing' : 1})

    def onRemove(self, client):
        client.penguin.playing = False

        client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'playing' : 0})

class Multiplayer(Game, ExtensibleObject):
    # Multiplayer!

    game = True
    waddle = None

    def onAdd(self, client):
        super(Multiplayer, self).onAdd(client)

        client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {'playing' : 1, 'waddling' : 0})


class Igloo(Place):
    # Igloo room...

    opened = False
    type = 'igloo'
    owner = 0
    _id = 0
    backyard = None

    def append(self, client):
        clientFriends = [i.friend_id for i in client['data'].friends]

        if (not self.opened and not client['id'] == self.owner and self.owner not in clientFriends) and not client['moderator']:
            return client['prevRooms'][-1].append(client)

        super(Igloo, self).append(client)

    def onAdd(self, client):
        client.send('jp', client['id'], self.ext_id, self.type)
        super(Igloo, self).onAdd(client)

    def __repr__(self):
        return "Igloo<{}#{}>".format(self.name, self.ext_id)


class RoomHandler (object):

    def __init__(self, engine, package = 'configs/crumbs/rooms.json'):
        self.engine = engine
        self.logger = logging.getLogger(TIMELINE_LOGGER)
        self.package = package

        self.rooms = deque()
        self.details = dict({Place:0, Arcade:0, Multiplayer:0, Game:0})

        self.setup()

    def joinRoom(self, client, _room, _type = 'ext'):
        if client is None:
            return

        room = None
        if _type == 'ext':
            room = self.getRoomByExtId(_room)
        elif _type == 'int':
            room = self.getRoomById(_room)
        elif _type == 'name':
            room = self.getRoomByName(_room)

        if room is None or isinstance(room, Multiplayer): # You cannot join multiplayer games, you waddle and enter the gane
            return client.send('e', 213)

        if client['room'] is not None:
            client['room'].remove(client)

        if client['waddling'] or client['playing']:
            client.send('e', 200)
            client['game'].remove(client)

        client.penguin.frame = 1
        room.append(client)

    def removeFromAnyRoom(self, client, *args):
        for room in list(self.rooms):
            room.remove(client) if client in room else None

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

            except Exception, e:
                self.log("error", "Error parsing JSON. E:", e)
                sys.exit()


            self.log('info', 'Loaded a total of', len(self.rooms), 'Room(s)')

        if not os.path.exists("configs/crumbs/games.json"):
            self.log('error', 'games.json not found in path : ', 'configs/crumbs/games.json')
            sys.exit() # meow!!

        with open('configs/crumbs/games.json', 'r') as file:
            try:
                crumbs = json.loads(file.read())
                for game_detail in crumbs:
                    key = game_detail
                    room = crumbs[key]

                    _id = int(room['room_id'])
                    name = room['name']
                    maxu = 800
                    jump = False
                    item = None
                    member = False
                    stamp = int(room['stamp_group_id'])

                    is_non_black_hole = bool(room['show_player_in_room'])

                    roomObj = None

                    if _id is 0:
                        continue # Table games?

                    if is_non_black_hole:
                        roomObj = Arcade(self, _id, key, name, maxu, member, jump, item)
                        self.details[Arcade] += 1

                    elif _id > 990 or _id in MULTIPLAYER_GAMES:
                        roomObj = (Multiplayer if _id not in MULTIPLAYER_GAMES else MULTIPLAYER_GAMES[_id])(self, _id, key, name, maxu, member, jump, item)
                        self.details[Multiplayer] += 1
                    else:
                        roomObj = Game(self, _id, key, name, max, member, jump, item)
                        self.details[Game] += 1

                    roomObj.stamp_id = stamp
                    self.rooms.append(roomObj)

            except Exception, e:
                    self.log('error', 'Error parsing JSON. E:', e)
                    sys.exit()

        for r in self.details:
                self.log('info', 'Loaded', self.details[r], '{}(s)'.format(r.__name__))

        self.ROOM_CONFIG = type('RoomConfig', (object,), {'ROOM_HANDLER' : self})() # user editable, flexible attribute. Used by each game as desired
        GeneralEvent('Room-handler', self)

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
                return room

        return None

    def getRoomByDisplayName(self, name):
        name = name.lower().strip()
        for room in self.rooms:
            if room.name.lower() == name:
                return room

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