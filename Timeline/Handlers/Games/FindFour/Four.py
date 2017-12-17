from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.FindFour import FOUR_TABLES, FindFour


from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setRoomHandler(ROOM_HANDLER):
	ROOM_HANDLER.ROOM_CONFIG.FourGame = {}
	for i in FOUR_TABLES:
		ROOM_HANDLER.ROOM_CONFIG.FourGame[i] = {}
		for j in FOUR_TABLES[i]:
			ROOM_HANDLER.ROOM_CONFIG.FourGame[i][j] = FindFour(ROOM_HANDLER, j, i) # new game

	logger.debug("FindFour Tables Loaded")

@Event.on('JoinTable-205')
@Event.on('JoinTable-206')
@Event.on('JoinTable-207')
def handleJoinTable(client, table):
	ROOM_HANDLER = client.engine.roomHandler
	room = client['room'].ext_id

	if room not in ROOM_HANDLER.ROOM_CONFIG.FourGame or table not in ROOM_HANDLER.ROOM_CONFIG.FourGame[room]:
		return client.send('e', 402)

	ROOM_HANDLER.ROOM_CONFIG.FourGame[room][table].append(client)

@Event.on('LeaveTable-205')
@Event.on('LeaveTable-206')
@Event.on('LeaveTable-207')
def handleLeaveTable(client, table):
	ROOM_HANDLER = client.engine.roomHandler
	room = client['game'].room.ext_id

	if room not in ROOM_HANDLER.ROOM_CONFIG.FourGame or table not in ROOM_HANDLER.ROOM_CONFIG.FourGame[room]:
		return client.send('e', 402)

	ROOM_HANDLER.ROOM_CONFIG.FourGame[room][table].remove(client)
	# ROOM_HANDLER.ROOM_CONFIG.FourGame[room][table].room.append(client)