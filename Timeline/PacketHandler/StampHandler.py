from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

@PacketEventHandler.XTPacketRule('s', 'st#gsbcd', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'st#gps', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'st#sse', WORLD_SERVER)
def GetSBCoverRule(data):
	return [[int(data[2][0])], {}]

@PacketEventHandler.XTPacketRule('s', 'st#ssbcd', WORLD_SERVER)
def SBCoverRule(data):
	param = data[2]

	color = int(param[0])	
	highlight = int(param[1])
	pattern = int(param[2])
	icon = int(param[3])

	stamps = list()

	# 1|607|406|177|45|16%1|608|267|262|300|17%1|606|533|266|315|15

	if len(param) > 4:
		for stamp_detail in param[4:]:
			details = stamp_detail.split('|')

			item_type = int(details[0])
			item_id = int(details[1])
			x = int(details[2])
			y = int(details[3])
			rotation = int(details[4])
			depth = int(details[5])

			stamps.append((item_type, item_id, x, y, rotation, depth))

	return [[color, highlight, pattern, icon, stamps], {}]