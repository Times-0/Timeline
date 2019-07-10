from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Refresh.Handlers import RefreshHandler
from Timeline.Utils.Refresh.Functions import Functions
from Timeline.Utils.Refresh import PenguinObject
from Timeline.Database.DB import Coin, Igloo, Avatar, Membership, Penguin
from Timeline import Membership as MembershipHandler

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from twistar.registry import Registry

from collections import deque
import logging
import time
import json

class Refresh(RefreshHandler, Functions):

    REFRESH_INTERVAL = 10
    DEBUG = True

    REFRESH_ITEMS = ['inventories', 'assets', 'friends', 'requests', 'ignores', 'careItems', 'stamps', 'mails',
                       'bans', 'puffles', 'stampCovers']

    def __init__(self, penguin):
        self.penguin = penguin
        self.logger = logging.getLogger(TIMELINE_LOGGER)
        
        super(Refresh, self).__init__()

        self.logger.info("Penguin ASync-Refresh service initialized : Penguin - {}".format(self.penguin['nickname']))
        self.RefreshManagerLoop = LoopingCall(self._refresh)
        self.firstTimeCall = True
        self.CacheInitializedDefer = Deferred()
        self.cache = PenguinObject()

        self.penguin.penguin.data = self.cache # for easier access

        self.cacheHandlers = PenguinObject()

        self.logger.info("Penguin ASync-Refresh Loop started, every {}(s) : Penguin - {}".format
                         (self.REFRESH_INTERVAL, self.penguin['nickname']))

        self.RefreshManagerLoop.start(self.REFRESH_INTERVAL)

    @inlineCallbacks
    def _refresh(self, forced = False):
        if self.DEBUG:
            self.logger.info('Penguin ASync-Refresh-ing : Penguin - {}, Forced - {}'.format
                             (self.penguin['nickname'], forced))

        if self.penguin['connectionLost']:
            returnValue(0)

        if self.firstTimeCall:
            yield self._setupCache()
            self.firstTimeCall = False

            returnValue(1)

        # coins update
        self.penguin.penguin.coins = (yield Registry.getConfig(). \
            execute("SELECT SUM(transaction) FROM coins where penguin_id = %s" % self.penguin['id']))[0][0]

        if self.penguin['coins'] is None:
            yield Coin(penguin_id = self.penguin['id'], transaction = 100, comment = "Player went bankrupt. "
                                                                                     "Giving them +100").save()
            self.penguin.penguin.coins = 100

        self.penguin.penguin.coins = int(self.penguin['coins'])
        self.penguin.send('gtc', self.penguin['coins'])

        for item in self.REFRESH_ITEMS:
            if not hasattr(self.penguin.dbpenguin, item):
                continue

            relation = getattr(self.penguin.dbpenguin, item)
            items_o = set(self.cache[item])
            items_ = yield relation.get()
            items_updated = set(items_)
            items_added = items_updated - items_o
            items_removed = items_o - items_updated

            reactor.callFromThread(self.cacheHandlers[item], items_added, items_removed, items_o)

        reactor.callFromThread(self.cacheHandlers['igloos'])
        GeneralEvent('Refresh-Cache', self)  # Refresh cache data for things other than those in here

        if forced:
            reactor.callFromThread(self.RefreshManagerLoop.stop) if self.RefreshManagerLoop.running else None
            reactor.callFromThread(self.RefreshManagerLoop.start, self.REFRESH_INTERVAL, False) if \
                not self.penguin['connectionLost'] else None

    @inlineCallbacks
    def _setupCache(self):
        self.penguin.penguin.recentStamps = []
        database_penguin = self.penguin.dbpenguin

        self.cache.avatar = yield database_penguin.avatar.get()
        if self.cache.avatar is None:
            self.cache.avatar = yield Avatar(penguin_id=self.penguin['id']).save()
            yield self.cache.avatar.refresh()

        self.cache.inventories = yield database_penguin.inventories.get()
        self.cache.assets = yield database_penguin.assets.get()
        self.cache.friends = yield database_penguin.friends.get()
        self.cache.requests = []
        friends_data = []
        for friend in self.cache.friends:
            friendObj = (yield Penguin.find(where=['swid = ?', friend.friend], limit=1))
            if friendObj is None:
                continue

            friend.friend_id = friendObj.id
            friend.onlinePresence = {'online_status': False}
            data = [int(friendObj.id), friendObj.nickname, friendObj.swid, friend.bff]
            friends_data.append('|'.join(map(str, data)))

        self.penguin.send('fl', (yield database_penguin.requests.count()), *friends_data)

        self.cache.ignores = yield database_penguin.ignores.get()
        self.cache.careItems = yield database_penguin.careItems.get()
        self.cache.stamps = yield database_penguin.stamps.get()
        self.cache.mails = yield database_penguin.mails.get()
        self.cache.bans = yield database_penguin.bans.get()
        self.cache.puffles = yield database_penguin.puffles.get()
        self.cache.stampCovers = yield database_penguin.stampCovers.get()
        self.cache.igloos = deque()

        igloos = yield database_penguin.igloos.get(limit=6)
        for igloo in igloos:
            iglooCache = PenguinObject()
            iglooCache.igloo = igloo
            iglooCache.iglooFurnitures = yield igloo.iglooFurnitures.get(limit = 99)
            iglooCache.iglooLikes = yield igloo.iglooLikes.get()

            self.cache.igloos.append(iglooCache)

        self.cache.memberships = yield database_penguin.memberships.get()

        self.cacheHandlers.inventories = self.handleInventory
        self.cacheHandlers.assets = self.handleAssets
        self.cacheHandlers.friends = self.handleFriends
        self.cacheHandlers.requests = self.handleRequests
        self.cacheHandlers.ignores = self.handleIgnores
        self.cacheHandlers.careItems = self.handleCareItems
        self.cacheHandlers.stamps = self.handleStamps
        self.cacheHandlers.mails = self.handleMails
        self.cacheHandlers.bans = self.handleBans
        self.cacheHandlers.puffles = self.handlePuffles
        self.cacheHandlers.stampCovers = self.handleStampCovers
        self.cacheHandlers.igloos = self.handleIgloos

        self.penguin.penguin.coins = (yield Registry.getConfig().\
            execute("SELECT COALESCE(SUM(transaction), 0) FROM coins where penguin_id = %s" % self.penguin['id']))[0][0]

        self.penguin.penguin.igloo = yield self.initPenguinIglooRoom(self.penguin['id'])
        if self.penguin['igloo']._id not in self.getIgloos():
            igloo = yield database_penguin.igloos.get(where=['id = ?', self.penguin['igloo']._id],
                                       limit=1)
            iglooCache = PenguinObject()
            iglooCache.igloo = igloo
            iglooCache.iglooFurnitures = yield igloo.iglooFurnitures.get(limit = 99)
            iglooCache.iglooLikes = yield igloo.iglooLikes.get()

            self.cache.igloos.append(iglooCache)

        self.penguin.penguin.currentIgloo = self.getIgloos()[self.penguin.dbpenguin.igloo].igloo
        self.setupCJMats()

        membership = yield database_penguin.memberships.get(orderby = 'expires desc', limit = 1)
        if membership is None:
            #no membership records, give a free 7 day trial
            trialExpiry = time.time() + 7 * 24 * 60 * 60

            membership = yield \
                Membership(penguin_id=self.penguin['id'],
                           expires=Registry.getDBAPIClass("TimestampFromTicks")(trialExpiry),
                           comments='Redeemed 7-day auto free trial membership. - Timeline Server').save()

        self.penguin.penguin.member = MembershipHandler(membership.expires, self.penguin)
        self.cache.avatar = yield database_penguin.avatar.get()
        if self.cache.avatar is None:
            self.cache.avatar = yield Avatar(penguin_id=self.penguin['id']).save()

        GeneralEvent('Setup-Cache', self)

        self.CacheInitializedDefer.callback(True)

    def forceRefresh(self, reason = 'Force refresh on server command'):
        if self.DEBUG:
            self.logger.info('Penguin ASync-Refresh, Force refresh: Penguin - {}, Reason - {}'.format
                             (self.penguin['nickname'], reason))

        if not self.RefreshManagerLoop.running:
            self.logger.warn('Penguin ASync-Refresh Force refresh already running, called more than once in a row:'
                             ' Penguin - {}, Reason - {}'.format(self.penguin['nickname'], reason)) if self.DEBUG \
                else 0

            return None

        reactor.callFromThread(self.RefreshManagerLoop.stop)
        return self._refresh(True)

    def skip(self, reason = 'Skip refresh on server command'):
        if self.DEBUG:
            self.logger.info('Penguin ASync-Refresh, Skip Refresh: Penguin - {}, Reason - {}'.format
                             (self.penguin['nickname'], reason))

        reactor.callFromThread(self.RefreshManagerLoop.reset)

