from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

@PacketEventHandler.XTPacketRule('s', 'p#pg', WORLD_SERVER)
def GetPufflesRule(data):
	param = data[2]

	return [[int(param[0]), param[1] == 'backyard'], {}]

@PacketEventHandler.XTPacketRule('s', 'p#pw', WORLD_SERVER)
def PuffleWalkRule(data):
	param = data[2]

	return [[int(param[0]), bool(int(param[1]))], {}]

@PacketEventHandler.XTPacketRule('s', 'p#pufflewalkswap', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'p#puffletrick', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'p#papi', WORLD_SERVER)
def PuffleSwapRule(data):
	return[[int(data[2][0])], {}]

@PacketEventHandler.XTPacketRule('s', 'p#puphi', WORLD_SERVER)
def PuffleUpdateRule(data):
	return [[int(param[0]), int(param[1])], {}]

@PacketEventHandler.XTPacketRule('s', 'p#puffleswap', WORLD_SERVER)
def PuffleRule(data):
	param = data[2]

	_id = int(param[0])
	room = param[1]

	if room not in ['igloo', 'backyard']:
		raise Exception("[TE333] Wrong room typo")

	return [[_id, room == 'backyard'], {}]

@PacketEventHandler.XTPacketRule('s', 'p#pn', WORLD_SERVER)
def AdoptRule(data):
	param = data[2]

	_t = int(param[0])
	name = str(param[1])
	_s = int(param[2])

	return [[_t, name, _s], {}]
