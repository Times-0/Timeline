from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Server.Room import Igloo as IglooRoom
from Timeline.Handlers.Games.CardJitsu import CJMat
from Timeline.Database.DB import Igloo, Penguin, Mail, Coin

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from twistar.registry import Registry

from collections import deque
import logging
import time
import json


class Functions(object):

    def __init__(self):
        self.logger = logging.getLogger(TIMELINE_LOGGER)

        super(Functions, self).__init__()

    def inInventory(self, i):
        i = int(i)
        return i in list(map(lambda x: int(x.item), self.cache.inventories))

    @inlineCallbacks
    def sendMail(self, to, mail):
        postcard = self.penguin.engine.postcardHandler[mail]
        if postcard is None:
            self.penguin.send('ms', self.penguin['coins'], 0)
            returnValue(None)

        if not (int(self.penguin['coins']) > 10):
            self.penguin.send('ms', self.penguin['coins'], 2)
            returnValue(None)

        yield Mail(penguin_id=to, from_user=self.penguin['id'], type=mail, description=str(postcard)).save()
        yield Coin(penguin_id=self.penguin['id'], transaction=-10,
                   comment="Postal Stamp charges. Mail sent: {}, to {}".format(mail, to)).save()

        self.penguin['coins'] -= 10
        self.penguin.send('ms', self.penguin['coins'], 1)

    def is_friend(self, swid):
        return swid in self.getFriends()

    def getFriends(self):
        return dict({i.friend: i for i in self.cache['friends']})

    def hasAsset(self, asset_id, asset_type):
        assets = self.getAssetsByType(asset_type)

        return asset_id in assets

    def getAsset(self, asset_id, asset_type):
        assets = self.getAssetsByType(asset_type)

        return assets[asset_id] if asset_id in assets else None

    def getAssetsByType(self, asset_type):
        assets = {}
        for a in self.cache.assets:
            if a.type == asset_type:
                assets[a.item] = a

        return assets

    def getIgloos(self):
        return dict({i.igloo.id: i for i in self.cache['igloos']})

    def hasIgloo(self, iglooId):
        return iglooId in self.getIgloos()

    @inlineCallbacks
    def initPenguinIglooRoom(self, penguin_id):
        penguin = (yield Penguin.find(penguin_id)) if penguin_id != self.penguin['id'] else self.penguin.dbpenguin
        if penguin is None:
            returnValue(None)

        iglooRoom = self.penguin.engine.iglooCrumbs.getPenguinIgloo(penguin_id)

        currentIgloo = int(penguin.igloo)
        igloo = yield Igloo.find(currentIgloo)
        if igloo is None:
            igloo = Igloo(penguin_id = penguin_id)
            yield igloo.save()

            currentIgloo = penguin.igloo = int(igloo.id)
            yield penguin.save()
            yield igloo.refresh()

        if iglooRoom is None:
            iglooRoom = IglooRoom(self.penguin.engine.roomHandler, (1000 + penguin_id), '{} igloo'.format(penguin_id),
                              "{}'s Igloo".format(penguin.nickname), 100, False, False, None)

            self.penguin.engine.iglooCrumbs.penguinIgloos.append(iglooRoom)
            self.penguin.engine.roomHandler.rooms.append(iglooRoom)

        iglooRoom.owner = int(penguin_id)
        iglooRoom.opened = not bool(igloo.locked)
        iglooRoom._id = int(igloo.id)

        returnValue(iglooRoom)

    def setupCJMats(self):
        CardJitsuWaddleId = 200
        currentIgloo = self.getIgloos()[self.penguin['currentIgloo'].id]
        igloo_room = self.penguin['igloo']
        mats_in_igloo = [k for k in currentIgloo.iglooFurnitures if k.furn_id == 786]

        for i in range(len(mats_in_igloo)):
            wid = CardJitsuWaddleId+i
            
            WADDLES = self.penguin.engine.roomHandler.ROOM_CONFIG.WADDLES
            if self.penguin['igloo'].id not in WADDLES:
                WADDLES[self.penguin['igloo'].id] = list()

            Mat = CJMat(self.penguin.engine.roomHandler, wid, "JitsuMat", "Card Jitsu Mat", 3, False, False, None)
            Mat.waddle = wid
            Mat.room = self.penguin['igloo']

            WADDLES[self.penguin['igloo'].id].append(Mat)

            self.logger.info("Added CardJitsu-Mat [%s] to %s's igloo.", wid, self.penguin['nickname'])
