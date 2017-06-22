'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Login.py handles the incoming XML Packet used to login to server. Packets may not necessarily be `login packet`
'''
from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from collections import deque
import logging

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXML('verChk', LOGIN_SERVER)
@PacketEventHandler.onXML('verChk', WORLD_SERVER)
def APIVersionCheck(client, body):
	version = str(body.find("ver").get('v'))
	if version != '153':
		client.send(client.PacketHandler.buildXML({"msg" : {'t' : 'sys', 'body' : {'action' : 'apiKO', 'r' : '0'} } }))
		return client.disconnect()

	client.send(client.PacketHandler.buildXML({"msg" : {'t' : 'sys', 'body' : {'action' : 'apiOK', 'r' : '0'} } }))
	if client.handshakeStage < 1:
		client.handshakeStage = 1 # Just a note that API version is verified!

@PacketEventHandler.onXML('rndK', LOGIN_SERVER)
@PacketEventHandler.onXML('rndK', WORLD_SERVER)
def GetPenguinRandomKey(client, body):
	client.send(client.PacketHandler.buildXML({"msg" : {'t' : 'sys', 'body' : {'action' : 'rndK', 'r' : '-1', 'k' : list([client.CryptoHandler.randomKey]) } } }))

def init():
	logger.debug('Login Server::Login initiated!')
	logger.debug('World Server::Login initiated!')