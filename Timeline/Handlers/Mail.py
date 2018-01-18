from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Utils.Mails import Mail

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

@PacketEventHandler.onXT('s', 'l#mg', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetMail(client, data):
	if client['mail'] is None:
		returnValue(client.send('mg', -1))

	if len(client['mail']) < 1:
		client.send('mg', '')

	else:
		mail = yield client['mail'].str()
		print mail, '?'
		client.send('mg', mail)

@PacketEventHandler.onXT('s', 'l#mst', WORLD_SERVER, p_r = False)
def handleStartMail(client, data):
	if client['mail'] is None:
		return client.send('mst', -1, -1)
		
	GeneralEvent.call('mail-start', client)

	unread = len([k for k in client['mail'] if k.opened < 1])
	client.send('mst', unread, len(client['mail']))

@PacketEventHandler.onXT('s', 'l#ms', WORLD_SERVER)
@inlineCallbacks
def handleSendMail(client, to, _id):
	if client['mail'] is None or not client.db_penguinExists(value = to):
		returnValue(client.send('ms', client['coins'], 0))

	send_mail_inbox = yield Mail.find(where = ['to_user = ? and junk != 1', to])
	if len(send_mail_inbox) > 99:
		returnValue(client.send('ms', client['coins'], 0))

	client['mail'].sendMail(to, _id)

@PacketEventHandler.onXT('s', 'l#mc', WORLD_SERVER, p_r = False)
def handleMaildRead(client, data):
	if client['mail'] is None:
		returnValue(None)

	client['mail'].setMailsChecked()

@PacketEventHandler.onXT('s', 'l#md', WORLD_SERVER)
def handleDeleteMail(client, _id):
	if client['mail'] is None:
		returnValue(None)

	client['mail'].deleteMail(_id)

@PacketEventHandler.onXT('s', 'l#mdp', WORLD_SERVER, p_r = False)
def handleDeleteAllFromUser(client, data):
	if client['mail'] is None:
		returnValue(None)

	client['mail'].deleteAllMail()