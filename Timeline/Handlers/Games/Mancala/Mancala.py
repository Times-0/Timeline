from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Handlers.Games.Mancala import MANCALA_TABLES, MancalaGame


from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setFourMats(ROOM_HANDLER):
	ROOM_HANDLER.ROOM_CONFIG.MancalaGame = {}
	for i in MANCALA_TABLES:
		ROOM_HANDLER.ROOM_CONFIG.MancalaGame[i] = {}
		for j in MANCALA_TABLES[i]:
			ROOM_HANDLER.ROOM_CONFIG.MancalaGame[i][j] = MancalaGame(ROOM_HANDLER, j, i) # new game

	logger.debug("Mancala Tables Loaded")

@Event.on('JoinTable-100')
@Event.on('JoinTable-101')
@Event.on('JoinTable-102')
@Event.on('JoinTable-103')
@Event.on('JoinTable-104')
def handleJoinTable(client, table):
	ROOM_HANDLER = client.engine.roomHandler
	room = client['room'].ext_id

	if room not in ROOM_HANDLER.ROOM_CONFIG.MancalaGame or table not in ROOM_HANDLER.ROOM_CONFIG.MancalaGame[room]:
		return client.send('e', 402)

	ROOM_HANDLER.ROOM_CONFIG.MancalaGame[room][table].append(client)

@Event.on('LeaveTable-100')
@Event.on('LeaveTable-101')
@Event.on('LeaveTable-102')
@Event.on('LeaveTable-103')
@Event.on('LeaveTable-104')
def handleLeaveTable(client, table):
	ROOM_HANDLER = client.engine.roomHandler
	room = client['game'].room.ext_id

	if room not in ROOM_HANDLER.ROOM_CONFIG.MancalaGame or table not in ROOM_HANDLER.ROOM_CONFIG.MancalaGame[room]:
		return client.send('e', 402)

	ROOM_HANDLER.ROOM_CONFIG.MancalaGame[room][table].remove(client)
	# ROOM_HANDLER.ROOM_CONFIG.FourGame[room][table].room.append(client)