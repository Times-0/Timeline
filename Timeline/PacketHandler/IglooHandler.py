from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

@PacketEventHandler.XTPacketRule('s', 'g#gm', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'g#aloc', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'g#af', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'g#ag', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'g#au', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'g#pio', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'g#cli', WORLD_SERVER)
def getIglooRule(data):
	return [[int(data[2][0])], {}]

@PacketEventHandler.XTPacketRule('s', 'g#uiss', WORLD_SERVER)
def SlotSummaryRule(data):
	param = data[2]
	_id = int(param[0])

	slots = param[3].split(',')
	summary = map(lambda x: map(int, x.split('|')), slots)

	return [[_id, summary], {}]

@PacketEventHandler.XTPacketRule('s', 'g#uic', WORLD_SERVER)
def IglooConfigurationRule(data):
	param = data[2]
	
	_id = int(param[0])
	_type = int(param[1])
	floor = int(param[2])
	location = int(param[3])
	music = int(param[4])

	furnitures = map(lambda x: map(int, x.split('|')), param[5].split(','))

	return [[_id, _type, floor, location, music, furnitures], {}]