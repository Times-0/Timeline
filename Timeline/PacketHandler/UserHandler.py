from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

@PacketEventHandler.XTPacketRule('s', 'u#pbi', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#sf', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#sa', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#u#se', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#ss', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#gp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#bf', WORLD_SERVER)
def UserRules(data):

	return [[int(data[2][0])], {}]

@PacketEventHandler.XTPacketRule('s', 'u#sp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#sb', WORLD_SERVER)
def SendCoordinatesRule(data):

	return [[int(data[2][0]), int(data[2][1])], {}]

@PacketEventHandler.XTPacketRule('s', 'u#pbn', WORLD_SERVER)
def UsernameRule(data):
	username = data[2][0].strip()

	u_w_s = username.replace(' ', '')
	if not u_w_s.isalnum():
		raise Exception("[TE012] Invalid characters found in username : {}".format(username))

	return [[username], {}]