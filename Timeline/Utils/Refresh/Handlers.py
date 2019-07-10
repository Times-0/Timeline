from Timeline.Server.Constants import TIMELINE_LOGGER, AS3_PROTOCOL
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Handlers.AS2.Puffle import getAS2PuffleString

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from Timeline.Database.DB import Penguin, IglooFurniture
from Timeline.Utils.Refresh import PenguinObject

import logging
from collections import deque

class RefreshHandler(object):

    def __init__(self):
        self.logger = logging.getLogger(TIMELINE_LOGGER)

        super(RefreshHandler, self).__init__()

    def handleInventory(self, itemAdded, itemRemoved, itemsOriginal):
        for item in itemAdded:
            self.penguin.send('ai', int(item.item), self.penguin['coins'])

        self.cache.inventories = list(itemsOriginal.union(itemAdded) - itemRemoved)

    @inlineCallbacks
    def handleAssets(self, assetAdded, assetRemoved, originalAssets):
        assetType = {'i': 'au', 'f': 'af', 'l': 'aloc', 'fl': 'ag'}
        for asset in assetAdded:
            self.penguin.send(assetType[asset.type], int(asset.item), self.penguin['coins'])

        self.cache.assets = list(originalAssets.union(assetAdded) - assetRemoved)

        for asset in self.cache.assets:
            if asset.type == 'f':
                yield asset.refresh()
                furn = self.penguin.engine.iglooCrumbs.getFurnitureById(asset.item)

                if asset.quantity > furn.max:
                    asset.quantity = furn.max
                    asset.save()

    @inlineCallbacks
    def handleFriends(self, newFriends, friendRemoved, originalFriends):
        self.cache.friends = list(originalFriends.union(newFriends) - friendRemoved)

        for friend in newFriends:
            friendObj = (yield Penguin.find(where=['swid = ?', friend.friend], limit=1))
            if friendObj is None:
                friend.delete()
                continue

            friend.friend_id = friendObj.id

            friendOnline = (yield self.penguin.engine.redis.server.hmget("online:{}".format(int(friendObj.id)),
                                                                         ['place_name']))
            if not self.penguin['moderator'] and friendObj.moderator == 2:
                friendOnline = None

            friendOnline = friendOnline[0] if friendOnline is not None \
                else 'N/A'

            data = [int(friendObj.id), friendObj.nickname, friendObj.swid, friend.bff, int(friendOnline != 'N/A'),
                    friendOnline]

            self.penguin.send('fb', '|'.join(map(str, data)))

        for friend in friendRemoved:
            self.penguin.send('frf', friend.friend)

        for friend in self.cache.friends:
            friendObj = (yield Penguin.find(where=['swid = ?', friend.friend], limit=1))
            if friendObj is None:
                friend.delete()
                continue

            friendOnline, roomId, worldId = (yield self.penguin.engine.redis.server.hmget("online:{}".format(int(friendObj.id)),
                                                                         ['place_name', 'place', 'world']))
            if not self.penguin['moderator'] and friendObj.moderator == 2:
                friendOnline = None


            friendOnline = friendOnline if friendOnline is not None \
                else 'N/A'
            friend.onlinePresence = {
                'online_status': friendOnline != 'N/A',
                'roomId': roomId,
                'worldId': worldId
            }

            self.penguin.send('fo', '|'.join(map(str, [friend.friend, (roomId or 0), friendOnline, friendObj.id, (worldId or -1)])))

    @inlineCallbacks
    def handleRequests(self, newRequests, removedRequests, originalRequests):
        self.cache.requests = list(originalRequests.union(newRequests) - removedRequests)

        for request in newRequests:
            penguin = yield Penguin.find(where = ['swid = ?', request.requested_by], limit=1)
            self.penguin.send('fn', penguin.nickname, penguin.swid) if penguin is not None else 0

    def handleIgnores(self, newIgnores, removedIgnores, originalIgnores):
        pass

    def handleStamps(self, stampAdded, stampRemoved, originalStamps):
        self.penguin.penguin.recentStamps = (self.penguin['recentStamps'] if self.penguin['recentStamps'] is not None
                                             else []) + list(stampAdded)

        for stamp in stampAdded:
            self.penguin.send('aabs', int(stamp.stamp))

        self.cache.stamps = list(originalStamps.union(stampAdded) - stampRemoved)

    def handleCareItems(self, itemAdded, itemRemoved, originalItems):
        for item in itemAdded:
            self.penguin.send('papi', self.penguin['coins'], int(item.item), int(item.quantity))

        self.cache.careItems = list(originalItems.union(itemAdded) - itemRemoved)

    @inlineCallbacks
    def handleMails(self, mailArrived, mailBurnt, originalMails):
        for mail in mailArrived:
            nickname = 'Timeline Team'
            peng = yield Penguin.find(mail.from_user)
            if peng is not None:
                nickname = peng.nickname

            self.penguin.send('mr', nickname, int(mail.from_user), int(mail.type), mail.description, mail.get_sent_on()
                              , int(mail.id), int(mail.opened))

        self.cache.mails = list(originalMails.union(mailArrived) - mailBurnt)

        mails = [((yield i.refresh()), i)[-1] for i in self.cache.mails]
        self.cache.mails = [i for i in mails if not i.junk]

        if len(self.cache.mails) < 1 and len(originalMails) > 0:
            self.penguin.send('mdp', 0)

    def handleBans(self, newBans, unBans, bans):
        for ban in newBans:
            if ban.banned():
                self.penguin.send('e', ban.type, ban.hours())
                return self.penguin.disconnect()

    def handlePuffles(self, adoptedPuffles, puffleToWoods, puffleHostaged):
        for puffle in adoptedPuffles:
            self.penguin.send('pn',
                              self.penguin['coins'],
                              puffle if self.penguin.Protocol == AS3_PROTOCOL else
                              getAS2PuffleString(self.penguin, [puffle]))

        for puffle in puffleToWoods:
            self.penguin['igloo'].send('prp', int(puffle.id))
            self.penguin['igloo'].backyard.send('prp', int(puffle.id))

        self.cache.puffles = list(puffleHostaged.union(adoptedPuffles) - puffleToWoods)

        for puffle in self.cache.puffles:
            puffle.updatePuffleStats(self.penguin.engine)

    def handleStampCovers(self, coverAdded, coverRemoved, coverPresent):
        self.cache.stampCovers = list(coverPresent.union(coverAdded) - coverRemoved)

        for cover in self.cache.stampCovers[6:]:
            cover.delete()

        self.cache.stampCovers = self.cache.stampCovers[:6]

    @inlineCallbacks
    def handleIgloos(self):
        igloos = yield self.penguin.dbpenguin.igloos.get()
        o_igloos = set(map(lambda x: x.igloo.id, self.cache.igloos))
        n_igloos = set(map(lambda x: x.id, igloos))

        #added_igloos = n_igloos - o_igloos
        #removed_igloos = o_igloos - n_igloos

        igloo_config = {i.igloo.id: i for i in self.cache.igloos}

        for igloo in igloos:
            if igloo.id not in igloo_config:
                iglooCache = PenguinObject()
                iglooCache.igloo = igloo
                self.cache.igloos.append(iglooCache)
            else:
                iglooCache = igloo_config[igloo.id]

            iglooCache.iglooFurnitures = yield igloo.iglooFurnitures.get()
            iglooCache.iglooLikes = yield igloo.iglooLikes.get()

            removeFurns = tuple(map(lambda x: x.id, iglooCache.iglooFurnitures[99:]))
            if len(removeFurns) > 0:
                yield IglooFurniture.deleteAll(where = ['igloo_id = ? AND id in ?', igloo.id, removeFurns])