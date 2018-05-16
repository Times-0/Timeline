from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.TreasureHunt import HUNT_TABLES, TreasureHunt


from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time, sleep

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setFourMats(ROOM_HANDLER):
	ROOM_HANDLER.ROOM_CONFIG.HuntGame = {}
	for i in HUNT_TABLES:
		ROOM_HANDLER.ROOM_CONFIG.HuntGame[i] = {}
		for j in HUNT_TABLES[i]:
			ROOM_HANDLER.ROOM_CONFIG.HuntGame[i][j] = TreasureHunt(ROOM_HANDLER, j, i) # new game

	logger.debug("TreasureHunt Tables Loaded")

@Event.on('JoinTable-300')
@Event.on('JoinTable-301')
@Event.on('JoinTable-302')
@Event.on('JoinTable-303')
@Event.on('JoinTable-304')
@Event.on('JoinTable-305')
@Event.on('JoinTable-306')
@Event.on('JoinTable-307')
def handleJoinTable(client, table):
	ROOM_HANDLER = client.engine.roomHandler
	room = client['room'].ext_id

	if room not in ROOM_HANDLER.ROOM_CONFIG.HuntGame or table not in ROOM_HANDLER.ROOM_CONFIG.HuntGame[room]:
		return client.send('e', 402)

	ROOM_HANDLER.ROOM_CONFIG.HuntGame[room][table].append(client)

@Event.on('LeaveTable-300')
@Event.on('LeaveTable-301')
@Event.on('LeaveTable-302')
@Event.on('LeaveTable-303')
@Event.on('LeaveTable-304')
@Event.on('LeaveTable-305')
@Event.on('LeaveTable-306')
@Event.on('LeaveTable-307')
def handleLeaveTable(client, table):
	ROOM_HANDLER = client.engine.roomHandler
	room = client['game'].room.ext_id

	if room not in ROOM_HANDLER.ROOM_CONFIG.HuntGame or table not in ROOM_HANDLER.ROOM_CONFIG.HuntGame[room]:
		return client.send('e', 402)

	ROOM_HANDLER.ROOM_CONFIG.HuntGame[room][table].remove(client)
	# ROOM_HANDLER.ROOM_CONFIG.FourGame[room][table].room.append(client)