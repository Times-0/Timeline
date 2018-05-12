from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

'''
AS2 Igloo packet rules
'''

@PacketEventHandler.XTPacketRule_AS2('s', 'g#gm', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'g#af', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'g#ag', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'g#au', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'g#ao', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'g#um', WORLD_SERVER)
def GetPlayerIglooRule(data):
	return [[int(data[2][0])], {}]

@PacketEventHandler.XTPacketRule_AS2('s', 'g#ur', WORLD_SERVER)
def UpdateFurnituresRule(data):
	furn_items = data[2]

	furnitures = list()
	for furn in furn_items:
		f_id, x, y, f1, f2 = map(int, furn.split('|'))

		furnitures.append((f_id, x, y, f1, f2))

	return [[furnitures], {}]

'''
AS2 Puffle Packet rules
'''

@PacketEventHandler.XTPacketRule_AS2('s', 'p#pg', WORLD_SERVER)
def GetPlayerIglooRule(data):
	return [[int(data[2][0])], {}]