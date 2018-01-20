from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, RAINBOW_QUEST_ITEMS
from Timeline.Utils.Puffle import Puffle
from Timeline.Utils.Mails import Mail
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time
from random import choice
import json

ENGINES = []

@GeneralEvent.on('onEngine')
def handleAddEngine(engine):
	if engine.type is WORLD_SERVER:
		ENGINES.append(engine)

@PacketEventHandler.onXT('s', 'musictrack#getmymusictracks', WORLD_SERVER, p_r = False)
def handleGetPlayerMusics(client, data):
	client.engine.musicHandler.init(client)

@PacketEventHandler.onXT('s', 'musictrack#canliketrack', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleCanLikeTrack(client, data):
	peng, track = map(int, data[2])
	track = client.engine.musicHandler.get(client.engine, track, peng)
	if track is None or peng == client['id']: # You cannot like your own track lol!
		client.send('canliketrack', int(track), 0)
		returnValue(False)

	likeKey = 'music:liked:{}|{}'.format(client['id'], track.id)
	lastLike = yield client.engine.redis.server.get(likeKey)
	print lastLike
	if lastLike is None:
		client.send('canliketrack', int(track), 1)
		returnValue(True)

	diff = (time() - lastLike)/(60*60)
	if diff < 24:
		client.send('canliketrack', int(track), 0)
		returnValue(False)

	client.send('canliketrack', int(track), 1)
	returnValue(True)

@PacketEventHandler.onXT('s', 'musictrack#liketrack', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleLikeTrack(client, data):
	peng, track = map(int, data[2])
	track = client.engine.musicHandler.get(client.engine, track, peng)
	canLike = yield handleCanLikeTrack(client, ['', '', [peng, track]])

	if not canLike:
		returnValue(0)

	likeKey = 'music:liked:{}|{}'.format(client['id'], track.id)
	client.engine.redis.server.set(likeKey, int(time()))

	likes = yield client.engine.redis.server.hmget('music:likes', track.id) + 1
	yield client.engine.redis.server.hmset('music:likes', {track.id : likes})

	track.likes = likes
	yield track.save()

	client.engine.roomHandler.getRoomByName('dance').send('liketrack', peng, int(track), likes)


@PacketEventHandler.onXT('s', 'musictrack#savemymusictrack', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleSaveTrack(client, data):
	if not client['member']:
		returnValue(client.send('e', 999))
	name, data, encoded = map(str, data[2])

	if data == '0' or data.split(',')[-1].split('|')[0] != 'FFFF':
		returnValue(0)

	track = yield client.engine.musicHandler.new(client, name, data, encoded)
	client.send('savemymusictrack', int(track))

@PacketEventHandler.onXT('s', 'musictrack#getlikecountfortrack', WORLD_SERVER, p_r = False)
def handleGetLikesForTrack(client, data):
	peng, track = map(int, data[2])
	track = client.engine.musicHandler.get(client.engine, track, peng)
	if track is not None:
		client.send('getlikecountfortrack', peng, int(track), track.likes)

@PacketEventHandler.onXT('s', 'musictrack#refreshmytracklikes', WORLD_SERVER, p_r = False)
def handleRefreshLikes(client, data):
	tracks = client.engine.musicHandler.getTracksByPenguin(client, client.engine)
	for track in tracks:
		client.send('getlikecountfortrack', client['id'], int(track), track.likes)

@PacketEventHandler.onXT('s', 'musictrack#loadmusictrack', WORLD_SERVER, p_r = False)
def handleGetTrack(client, data):
	peng, track = map(int, data[2])
	track = client.engine.musicHandler.get(client.engine, track, peng)
	if track is not None:
		trackData = track.__str__(True)
		client.send('loadmusictrack', trackData)

@PacketEventHandler.onXT('s', 'musictrack#sharemymusictrack', WORLD_SERVER, p_r = False)
def handleShareTrack(client, data):
	if not client['member']:
		return client.send('e', 999)

	track, shareOn = map(int, data[2])
	track = client.engine.musicHandler.get(client.engine, track, client)

	if track is not None:
		client.engine.musicHandler.deShare(client, client.engine)
		client.engine.musicHandler.share(track, shareOn)
		client.send('sharemymusictrack', 1)
		return

	client.send('sharemymusictrack', 0)

@PacketEventHandler.onXT('s', 'musictrack#getsharedmusictracks', WORLD_SERVER, p_r = False)
def handleGetSharedTracks(client, data):
	musicHandler = client.engine.musicHandler
	broadcastString = str(musicHandler)
	Queue = [musicHandler.currentMusic] + list(musicHandler.shareQueue)
	if None in Queue:
		Queue.remove(None)
	sharedCount = len(Queue)

	client.send('getsharedmusictracks', sharedCount, broadcastString)

@PacketEventHandler.onXT('s', 'musictrack#deletetrack', WORLD_SERVER, p_r = False)
def handleDeleteTrack(client, data):
	track = int(data[2][0])
	track = client.engine.musicHandler.get(client.engine, track, client)

	if track is None:
		return client.send('deletetrack', 0)

	client.engine.musicHandler.unset(track)
	client.send('deletetrack', 1)

@PacketEventHandler.onXT('s', 'musictrack#broadcastingmusictracks', WORLD_SERVER, p_r = False)
def handleGetBroadcastingTracks(client, data):
	musicHandler = client.engine.musicHandler
	broadcastString = str(musicHandler)
	Queue = list(musicHandler.shareQueue)

	sharedCount = len(Queue)

	myIndex = -1
	for i in range(sharedCount):
		track = Queue[i]
		if track.penguin is client:
			myIndex = i + 1
			break

	client.send('broadcastingmusictracks', sharedCount, myIndex, broadcastString)


@GeneralEvent.on('music:broadcast')
def handleSendBroadcast(musicHandler, broadcastTrack):
	if broadcastTrack is None:
		for engine in ENGINES:
			for penguin in engine.roomHandler.getRoomByName('dance'):
				penguin.send('broadcastingmusictracks', 0, -1, '')

		return

	broadcastingPenguins = [None]
	broadcastString = str(musicHandler)
	Queue = list(musicHandler.shareQueue)

	sharedCount = len(Queue)

	for i in range(sharedCount):
		track = Queue[i]
		if track.penguin not in broadcastingPenguins:
			penguin = track.penguin
			penguin.send('broadcastingmusictracks', sharedCount, i+1, broadcastString)

			broadcastingPenguins.append(penguin)

	broadcastingPenguins = set(broadcastingPenguins)
	for engine in ENGINES:
		danceClub = set(engine.roomHandler.getRoomByName('dance'))
		restPenguins = list(danceClub - broadcastingPenguins)
		for penguin in restPenguins:
			penguin.send('broadcastingmusictracks', sharedCount, -1, broadcastString)