from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'i#ai', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'i#ai', WORLD_SERVER)
def AddItemRule(data):
	param = data[2]

	item = param[0]

	return [[int(item)], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'i#qpp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'i#qpp', WORLD_SERVER)
def GetPinsRule(data):
	return [[int(data[2][0])], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'i#qpa', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'i#qpa', WORLD_SERVER)
def GetAwardsRule(data):
	return [[int(data[2][0])], {}]