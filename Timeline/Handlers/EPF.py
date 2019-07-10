from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import EPFCom

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#epfga', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#epfga', WORLD_SERVER, p_r = False)
def handleGetEPFStatus(client, data):
	client.send('epfga', int(bool(client['epf'])))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#epfsa', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#epfsa', WORLD_SERVER, p_r = False)
def handlePromoteAgent(client, data):
	if client['epf']:
		return

	client['epf'].e = True
	client.dbpenguin.agent = 1
	client.dbpenguin.save()

	client.send('epfsa', 1)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'epfgr', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'epfgr', WORLD_SERVER, p_r = False)
def handleGetEPFP(client, data):
	client.send('epfgr', client['epf'].p, client['epf'].t)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'f#epfai', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'f#epfai', WORLD_SERVER)
def EPFAIRule(data):
	return [[int(data[2][0])], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#epfai', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'f#epfai', WORLD_SERVER)
def handleAddEPFItem(client, _id):
	item = client.engine.itemCrumbs[_id]
	
	if item is None:
		return client.send('e', 402)

	if not item.is_epf:
		return client.send('e', 402)

	if client['RefreshHandler'].inInventory(item):
		return client.send('e', 400)

	if client['epf'].p < item.cost:
		return client.send('e', 405)

	client['epf'].p -= item.cost
	client.dbpenguin.epf = '{}%{}'.format(client['epf'].p, client['epf'].t)

	client.addItem(item, 'Add EPF Item')

	client.dbpenguin.save()
	client.send('epfai', client.epfai.p)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#epfgm', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#epfgm', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetCOM(client, data):
	Messages = yield EPFCom.find(limit = 10, orderby = 'time DESC')

	client.send('epfgm', 0, *map(str, Messages))