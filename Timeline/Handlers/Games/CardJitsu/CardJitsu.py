from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Games.CardJitsu import CJ_MATS, CardJitsuGame, CJMat

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setCJMats(ROOM_HANDLER):
	for i in CJ_MATS:
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i] = CJMat(ROOM_HANDLER, i, "JitsuMat", "Card Jitsu Mat", 3, False, False, None)
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddle = i

	logger.debug("Card Jitsu Initiated")

@PacketEventHandler.onXT('z', 'gwcj', WORLD_SERVER, p_r = False)
def handleGetWaddlingCJ(client, data):
	mat = int(data[2][0])
	ROOM_HANDLER = client.engine.roomHandler

	if mat not in ROOM_HANDLER.ROOM_CONFIG.WADDLES:
		return

	users = [str(k['id']) for k in ROOM_HANDLER.ROOM_CONFIG.WADDLES[mat]]
	client.send('%xt%gwcj%-1%'.format('%'.join(users)))