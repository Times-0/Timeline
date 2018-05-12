from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import Penguin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import sample
import json

@GeneralEvent.on('onClientDisconnect')
def handleStopFriendLoopReflush(client):
	if client['friendsHandler'] is not None and client['friendsHandler'].friendsDBReflushLoopingCall is not None:
		if client['friendsHandler'].friendsDBReflushLoopingCall.running:
			client['friendsHandler'].friendsDBReflushLoopingCall.stop()

		friends = list(client['friendsHandler'].friends)
		for f in friends:
			friend = client.engine.getPenguinById(f[1])
			if friend is None:
				continue

			friend.send('fo', '{}|0'.format(client['swid'])) # not necessary

@GeneralEvent.on('joined-room')
def handlePenguinRoomSwap(client, rid):
	friends = list(client['friendsHandler'].friends)
	canShowNotif = len(client['prevRooms']) < 1
	for f in friends:
		friend = client.engine.getPenguinById(f[1])
		if friend is None:
			continue

		friend.send('fo', '{}|1|{}|{}'.format(client['swid'], client['room'].name, canShowNotif))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#n', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#n', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleNewFriendRequest(client, data):
	swid = data[2][0]

	requested = yield client['friendsHandler'].haveRequested(client['swid'], swid)
	if requested:
		return

	client['friendsHandler'].sendRequest(swid)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#s', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#s', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleSearchPenguin(client, data):
	searchQuery = data[2][0].strip()
	searchResults = []

	results = yield Penguin.find(where = ['nickname like ?', '%{}%'.format(searchQuery)])

	no_space_query = searchQuery.replace(' ', '')
	if not no_space_query.isalnum():
		searchResults.append({'msg' : 'The search query must contain only alphabets, numbers or a space.', 'nickname' : 'Search Bot 1'})

	if len(searchQuery) < 4:
		searchResults.append({'msg' : 'The search query must be atleast 4 characters long.', 'nickname' : 'Search Bot 2'})

	if len(searchResults) > 0:
		returnValue(client.send('fs', json.dumps(searchResults)))

	for r in results:
		if r.swid == client['swid'] or client['friendsHandler'].isFriend(r.swid):
			continue

		a = {'nickname' : r.nickname}
		if hasattr(r, 'search_msg') and r.search_msg is not None:
			a['msg'] = r.search_msg
		else:
			a['swid'] = r.swid

		searchResults.append(a)

	if len(searchResults) < 1:
		searchResults.append({'msg' : 'Your query yield no result. Search for some other penguin.', 'nickname' : 'Search Bot 3'})

	client.send('fs', json.dumps(searchResults))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#bf', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#bf', WORLD_SERVER, p_r = False)
def handleChangeBFFStatus(client, data):
	swid = data[2][0]
	isBFF = int(data[2][1])

	client['friendsHandler'].handleChangeBFF(swid, isBFF)

'''
AS2 and AS3 Compatibility
'''
@PacketEventHandler.onXT('s', 'f#a', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT('s', 'f#r', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#a', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#r', WORLD_SERVER, p_r = False)
def handleAcceptOrRejectFriendRequest(client, data):
	accepted = data[1][-1] == 'a'
	swid = data[2][0]

	client['friendsHandler'].friendRequestResponse(swid, accepted)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#rf', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#rf', WORLD_SERVER, p_r = False)
def handleRemoveFriend(client, data):
	swid = data[2][0]

	client['friendsHandler'].removeFriend(swid)