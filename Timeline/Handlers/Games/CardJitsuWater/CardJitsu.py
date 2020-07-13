from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, FIRE_STARTER_DECK
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Games.CardJitsuWater import CJ_MATS, CJMat
#from Timeline.Handlers.Games.CardJitsuWater.Sensei import CardJitsuWaterSenseiGame
from Timeline.Handlers.Games.CardJitsu.CardJitsu import getSensei

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import choice

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('Room-handler')
def setCJMats(ROOM_HANDLER):
    for i in CJ_MATS:
        ROOM_HANDLER.ROOM_CONFIG.WADDLES[i] = CJMat(ROOM_HANDLER, i, "WaterJitsuMat", "Card Jitsu Water Mat", CJ_MATS[i], False, False, None)
        ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddle = i
        ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddles = CJ_MATS[i]

    logger.debug("Card Jitsu Fire Initiated")