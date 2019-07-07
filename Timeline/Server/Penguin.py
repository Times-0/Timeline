'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Penguin is a extension of LineReceiver, protocol. Implements the base of Client Object
'''

from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, WORLD_SERVER, AS3_PROTOCOL, AS2_PROTOCOL
from Timeline.Utils.Events import Event, GeneralEvent
from Timeline.Utils.Cryptography import Crypto
from Timeline.Server.Packets import PacketHandler
from Timeline.Database.DB import PenguinDB, Ban, Inventory, Coin
from Timeline import Username, Password, Nickname, Membership, Age, Cache, EPFAgent

from Timeline.Utils.Ninja import NinjaHandler
from Timeline.Utils.Currency import CurrencyHandler

from Timeline.Utils.Refresh.Refresh import Refresh
from Timeline.Utils.Refresh import PenguinObject

from Timeline.Utils.Plugins.Abstract import ExtensibleObject

from twisted.protocols.basic import LineReceiver
from twisted.protocols.policies import TimeoutMixin
from twisted.internet import threads
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue

from repr import Repr
from collections import deque
import logging
import time
from math import ceil
import weakref
import datetime as dt

class LR(LineReceiver, TimeoutMixin):
    def makeConnection(self, transport):
        pass

    def connectionLost(self, reason):
        pass

    def lineReceived(self, line):
        pass
    
    def send(*a):
        pass


class Penguin(PenguinDB, ExtensibleObject, LR):
    '''
    AS2 + AS3 Protocol Implementation
    '''

    delimiter = chr(0)
    TIMEOUT = 70  # idle timeout 70 seconds

    def __init__(self, engine):
        super(Penguin, self).__init__()

        self.Protocol = engine.server_protocol
        self.factory = self.engine = engine
        self.logger = logging.getLogger(TIMELINE_LOGGER)
        self.cleanConnectionLost = Deferred()

        self.errored = None

        self.buildPenguin()

    def __del__(self):
        self.logger.warn('Discarding Penguin<%s> Object: %s : %s', self.engine.server_protocol, str(self.client), self.getPortableName())

    def buildPenguin(self):
        self.handshakeStage = -1

        self.canRecvPacket = False
        self.ReceivePacketEnabled = True # Penguin can receive packet only if both this and self.canRecvPacket is true.

        # Some XT packets are sent before J#JS to make sure client is alive, just to make sure to ignore it ;)
        # ('category', 'handler', 0 or 1 : execute : don't execute)
        self.ignorableXTPackets = [('s', 'j#js', 1), ('s', 'p#getdigcooldown', 0), ('s', 'u#h', 0), ('s', 'f#epfgf', 0), ('l', 'login', 1)]

        self.penguin = PenguinObject()
        self.penguin.name = None
        self.penguin.id = None

        self.penguin.room = None
        self.penguin.prevRooms = list()

        self.ref = weakref.proxy(self)

        # Initiate Packet Handler
        self.PacketHandler = PacketHandler(self.ref)
        self.CryptoHandler = Crypto(self.ref)

    def initialize(self):
        self.penguin.nickname = Nickname(self.dbpenguin.nickname, self.ref)
        self.penguin.swid = self.dbpenguin.swid

        #TODO: figure out why the hell EPF even exists.
        self.penguin.epf = EPFAgent(self.dbpenguin.agent, str(self.dbpenguin.epf), self.ref)

        self.penguin.RefreshHandler = Refresh(self.ref)

        self.penguin.moderator = int(self.dbpenguin.moderator)
        self.penguin.stealth_mode = self['moderator'] == 2
        self.penguin.mascot_mode = self['moderator'] == 3

        self.penguin.x = self.penguin.y = self.penguin.frame = 0
        self.penguin.age = Age(self.dbpenguin.create, self.ref)
        self.penguin.muted = False

        self.penguin.cache = Cache(self.ref)
        self.penguin.ninjaHandler = NinjaHandler(self.ref)
        self.penguin.currencyHandler = CurrencyHandler(self.ref)

        self.engine.musicHandler.init(self.ref)

        GeneralEvent('onBuildClient', self.ref)


    def checkPassword(self, password):
        return self.CryptoHandler.loginHash() == password

    def activationStatus(self):
        activation_data = self.dbpenguin.hash or ''
        activation_pending = ';' in activation_data

        if not activation_pending:
            return None

        expires = self.dbpenguin.create + dt.timedelta(days=7)
        expired = dt.datetime.now() > expires
        hours_left = ((expires - dt.datetime.now()).total_seconds())/3600

        if expired:
            self.send('loginMustActivate', 0, None, None, self.dbpenguin.email)
            self.disconnect()

        return '{}|7|{}'.format(hours_left, hours_left)

    @inlineCallbacks
    def banned(self):
        bans = yield self.dbpenguin.bans.get(where = ['expire > CURRENT_TIMESTAMP'], limit = 1)
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
        # self.disconnect()

    def getPortableName(self):
        if self["username"] == None and self["id"] == None:
            return "{}, {}".format(repr(self.client), self.Protocol)

        if self["username"] != None:
            return "{}, {}".format(self["username"], self.Protocol)

        if self["id"] != None:
            return "{}, {}".format(self["id"], self.Protocol)

        return "{}, {}".format(self["username"], self.Protocol)

    @inlineCallbacks
    def addItem(self, item, comment = "Added via catalog"):
        if isinstance(item, int):
            item = self.engine.itemCrumbs[item]
        elif isinstance(item, str):
            try:
                item = self.engine.itemCrumbs[int(item)]
            except:
                item = None

        if item is None:
            returnValue(False)

        cost = item.cost
        if int(self.penguin.coins) < cost:
            self.send('e', 401)
            returnValue(False)

        if self['RefreshHandler'].inInventory(item):
            returnValue(False)

        yield Inventory(penguin_id = self['id'], item = int(item), comments = comment).save()
        yield Coin(penguin_id = self['id'], transaction = -cost,
                   comment = "Money spent on adding item ({}). Item: {}".format(comment, int(item))).save()

        self.penguin.coins -= cost
        returnValue(True)

    def __str__(self):
        '''
        AS2 Compatible
        '''

        walking_id = walking_item = walking_type = walking_subtype = ''
        walking_state = 0

        if self['walkingPuffle'] is not None:
            puffle = self['walkingPuffle']

            walking_id = int(puffle.id)
            walking_item = int(puffle.hat)
            walking_type = int(puffle.type)
            walking_subtype = int(puffle.subtype)
            walking_state = int(puffle.state)

        data = [
            self['id'],
            self['nickname'],

            self['language'],

            self['data'].avatar.color,
            self['data'].avatar.head,
            self['data'].avatar.face,
            self['data'].avatar.neck,
            self['data'].avatar.body,
            self['data'].avatar.hand,
            self['data'].avatar.feet,
            self['data'].avatar.pin,
            self['data'].avatar.photo,

            self['x'],				# Cached coordinates
            self['y'],				# Cached coordinates
            self['frame'],

            self['member'].rank,    # Member/Player rank
            int(self['member']),	# Membership days remaining

            self['data'].avatar.avatar,			# avatar id
            None,
            None,					# Party Info

            walking_id,
            walking_type,
            walking_subtype,
            walking_item,
            walking_state
        ][:-8 if self.Protocol == AS2_PROTOCOL else None]

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
        '''
        Extended plugins can overload this function.
        If you want to override this function, raise NotImplementedError
        '''

        self.resetTimeout()  # reset idle-timeout ticks

        try:
            super(Penguin, self).lineReceived(line)
        except NotImplementedError:
            return

        receivedPacketDefer = self.PacketHandler.handlePacketReceived(line)
        receivedPacketDefer.addErrback(self.checkForExceptions)
        # Defer some other stuff? Probably?

    def send(self, *args):
        super(Penguin, self).send(*args)

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
        loseDefer = self.transport.loseConnection()
        return

    @inlineCallbacks
    def connectionLost(self, reason):
        super(Penguin, self).connectionLost(reason)
        self.penguin.connectionLost = True

        # decentralize and make disconnection more flexible
        if self.engine.type == WORLD_SERVER and self.penguin.id != None:
            # sending self just to make sure it doesn't throw weak-reference error
            if self['RefreshHandler'] is not None:
                self['RefreshHandler'].RefreshManagerLoop.stop() if self['RefreshHandler'].RefreshManagerLoop.running else 0

                yield self.engine.redis.server.srem("users:{}".format(self.engine.id), self['swid'])

            yield GeneralEvent('onClientDisconnect', self.ref)
            if self['RefreshHandler'] is not None:
                del self.penguin.RefreshHandler

        yield self.engine.redis.server.delete("online:{}".format(self['id']))

        yield self.engine.disconnect(self)

        self.cleanConnectionLost.callback(True)

    def makeConnection(self, transport):
        self.transport = transport
        self.client = self.transport
        self.connectionMade = True

        self.send("<cross-domain-policy><allow-access-from domain='*' to-ports='{0}' /></cross-domain-policy>".format(self.engine.port))
        self.setTimeout(self.TIMEOUT)
