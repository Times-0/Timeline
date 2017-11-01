from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

@PacketEventHandler.XTPacketRule('s', 'j#js', WORLD_SERVER)
def JoinServerRule(data):
	param = data[2]

	_id = int(param[0])
	pword = str(param[1])
	lang = str(param[2])

	if lang not in ['en']:
		raise Exception("[TE601] Language {} not supported!".format(lang))


	return [[_id, pword, lang], {}]