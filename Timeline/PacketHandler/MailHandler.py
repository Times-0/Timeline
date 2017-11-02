from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

@PacketEventHandler.XTPacketRule('s', "l#ms", WORLD_SERVER)
def handleSendMailRule(data):
	param = data[2]

	to = int(param[0])
	post = int(param[1])

	return [[to, post], {}]

@PacketEventHandler.XTPacketRule('s', 'l#md', WORLD_SERVER)
def handleDeleteMailRule(data):
	return [[int(data[2][0])], {}]