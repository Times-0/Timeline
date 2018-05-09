from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'u#pbi', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#sf', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#sa', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#se', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#ss', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#gp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#bf', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upc', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#uph', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upf', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upn', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upb', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upa', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upe', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 's#upl', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#followpath', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#sf', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#sa', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#se', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#ss', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#gp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upc', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#uph', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upf', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upn', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upb', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upa', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upe', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 's#upl', WORLD_SERVER)
def UserRules(data):
	return [[int(data[2][0])], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'u#sp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule('s', 'u#sb', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#sp', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#sb', WORLD_SERVER)
def SendCoordinatesRule(data):

	return [[int(data[2][0]), int(data[2][1])], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'u#pbn', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#pbn', WORLD_SERVER)
def UsernameRule(data):
	username = data[2][0].strip()

	u_w_s = username.replace(' ', '')
	if not u_w_s.isalnum():
		raise Exception("[TE012] Invalid characters found in username : {}".format(username))

	return [[username], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'u#pbsu', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#pbsu', WORLD_SERVER)
def SWIDListRule(data):
	return [[map(str, data[2][0].split(','))], {}]