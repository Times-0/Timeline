from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Games.SledRacing import SLED_TRACKS, SledRacingGame, SledTrack

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setCJMats(ROOM_HANDLER):
	for i in SLED_TRACKS:
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i] = SledTrack(ROOM_HANDLER, i, "Sled Track", "Sled Racing Track", SLED_TRACKS[i], False, False, None)
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddle = i
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddles = SLED_TRACKS[i]

	logger.debug("Sled Racing' Tracks Initiated")