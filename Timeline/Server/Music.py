from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Postcards import Postcard
from Timeline.Database.DB import MusicTrack

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet import reactor

import txredisapi as redis

from collections import deque
from math import ceil
import logging
import time
import json


class MusicRedis(object):

    def __init__(self, engine):
        self.engine = engine
        self.server = None

        redis.Connection(host = '127.0.0.1', reconnect = True).addCallback(self.set)

    def set(self, pool):
        self.server = pool
        self.engine.setup()


class MusicEngine(list):

    def __init__(self):
        self.logger = logging.getLogger(TIMELINE_LOGGER)

        self.shareQueue = deque()
        self.broadcasting = False
        self.currentMusic = None
        self.broadcastDefer = Deferred()

        self.redis = MusicRedis(self)

    @inlineCallbacks
    def setup(self):
        tracks = yield MusicTrack.find(where = ['deleted = 0'])

        for track in tracks:
            self.set(track)
            self.append(track)

        self.logger.info('Musics loaded!')
        self.logger.debug('Music handle alive!')

    def set(self, track, engine = None):
        data = track.data.split(',')
        track.name = data[0]
        track.notes = ','.join(data[1:])
        track.length = int(data[-1].split('|')[1], 16) # milliseconds
        track.penguin = engine.getPenguinById(track.penguin_id) if engine is not None else None
        if track.penguin is not None:
            track.pengNick = str(track.penguin['nickname'])
            track.pengSWID = track.penguin['swid']

        self.redis.server.hmset('music:sharing', {track.id : int(track.shared)})
        self.redis.server.hmset('music:likes', {track.id : track.likes})

    def unset(self, track):
        track.deleted = 1
        track.penguin = None
        track.save()

        self.redis.server.hdel('music:sharing', track.id)
        self.redis.server.hdel('music:likes', track.id)

        if track in self:
            self.remove(track)

    def get(self, engine, track, p = None):
        if p is not None and isinstance(p, engine.protocol):
            p = p['id']

        for t in self:
            if t.id == track:
                return t if (not p or (t.penguin_id == p)) else None

        return None

    def share(self, track, isSharing = True):
        track.shared = isSharing
        self.redis.server.hmset('music:sharing', {track.id : int(track.shared)})

        if isSharing:
            self.refresh().addCallback(lambda *x: self.broadcastMusic(False))

    def deShare(self, penguin, engine):
        if isinstance(penguin, engine.protocol):
            penguin = penguin['id']

        for track in self.getTracksByPenguin(penguin, engine):
            if track.shared:
                self.share(track, 0)

    @inlineCallbacks
    def new(self, penguin, name, data, encoded):
        data = '{},{}'.format(name, data)
        track = MusicTrack(penguin_id = penguin['id'], data = data, hash = encoded, deleted = 0, likes = 0)
        yield track.save()

        self.set(track, penguin.engine)
        self.append(track)

        returnValue(track)

    def getTracksByPenguin(self, penguin, engine):
        if isinstance(penguin, engine.protocol):
            penguin = penguin['id']

        return [t for t in self if t.penguin_id == penguin]

    def deInit(self, penguin):
        for t in self.getTracksByPenguin(penguin, penguin.engine):
            t.penguin = None
            t.shared = False

            t.save()
            self.redis.server.hmset('music:sharing', {int(t) : 0})

    def init(self, penguin):
        tracks = self.getTracksByPenguin(penguin, penguin.engine)
        data = list()
        for track in tracks:
            track.penguin = penguin
            track.pengNick = str(penguin['nickname'])
            track.pengSWID = penguin['swid']

            data.append('|'.join(str(track).split('|')[:4]))

            track.refresh()

        penguin.send('getmymusictracks', len(data), ','.join(data))

    @inlineCallbacks
    def refresh(self):
        for track in list(self):
            yield track.refresh()

            if track.deleted:
                self.unset(track)

                if track in self.shareQueue:
                    self.shareQueue.remove(track)

        sharedTracks = yield self.redis.server.hgetall("music:sharing")
        Queued = set(map(int, self.shareQueue))
        Waiting = set()
        for s in sharedTracks:
            if sharedTracks[s]:
                Waiting.add(s)

        newTracks = list(Waiting - Queued)
        for track in list(self):
            if track.id in newTracks and track not in self.shareQueue:
                self.shareQueue.append(track)
                newTracks.remove(track.id)

    def broadcastMusic(self, nextMusic = False):
        if self.broadcasting and not nextMusic:
            return 0

        if self.currentMusic is not None:
            self.currentMusic.shared = False
            self.shareQueue.remove(self.currentMusic)

        if len(self.shareQueue) < 1: # try once
            self.currentMusic = None
            self.broadcasting = False

            GeneralEvent('music:broadcast', self, None)
            self.redis.server.set('music:broadcasting', None)
            return 0 # No more queue

        self.broadcasting = True
        self.currentMusic = self.shareQueue[0]

        self.redis.server.hmset('music:sharing', {self.currentMusic.id : int(0)})

        t = ceil(self.currentMusic.length / 1000)
        self.redis.server.set('music:broadcasting', int(self.currentMusic))
        GeneralEvent('music:broadcast', self, self.currentMusic)

        self.logger.info('Broadcasting "%s" by %s, %i seconds until next music!', self.currentMusic.name, self.currentMusic.pengNick, t)

        self.broadcastDefer = reactor.callLater(t, self.broadcastMusic, True)

        self.refresh()

    def __str__(self):
        Queue = list(self.shareQueue)
        return ','.join(map(lambda x: '|'.join(map(str, [x.penguin_id, x.pengNick, x.pengSWID, x.id, x.likes])), Queue))

    def __call__(self, engine):
        return self


MusicTrackEngine = MusicEngine()
