from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Postcards import Postcard

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
from twistar.dbobject import DBObject

from collections import deque
import logging
import time
import json

class Friend(DBObject):
	pass

class FriendsHandler(object):

	def __init__(self, penguin):
		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)

		self.friends = deque()
		self.requests = deque()
		self.ignored = deque() # TODO

		self.friendsDBReflushLoopingCall = None

		self.setup()

	@inlineCallbacks
	def setup(self):
		self.friendsDB = yield Friend.find(where = ['swid = ?', self.penguin['swid']], limit = 1)
		if self.friendsDB is None:
			self.friendsDB = Friend(swid = self.penguin['swid'], friends = '', requests = '', ignored = '')
			yield self.friendsDB.save()

		yield self.fetchFriends(False)		
		yield self.fetchRequests(False)

		#TODO: ignores

		friend_data = yield self.getFriendDetail()
		self.penguin.send('fl', len(self.requests), *(map(lambda x: '|'.join(map(str, x)), friend_data)))

		online_data = [k for k in friend_data if len(k) > 4]

		if len(online_data) > 0:
			self.penguin.send('fo', *(map(lambda x: '|'.join(map(str, [x[2], x[-2], x[-1], 1])), online_data)))

		for request in self.requests:
			self.penguin.send('fn', request[-1], request[0])

		room = self.penguin['room'].name if self.penguin['room'] is not None else '*Hidden'
		for friend in self.friends:
			penguinOnline = self.penguin.engine.getPenguinById(friend[1])
			if penguinOnline is not None:
				penguinOnline.send('fo', '{}|1|{}|1'.format(self.penguin['swid'], room))

		if self.penguin['dontReFlushFriends']:
			returnValue(0)
			
		self.friendsDBReflushLoopingCall = LoopingCall(self.reflushDatabase)
		self.friendsDBReflushLoopingCall.start(30) # for each 30 seconds

		self.logger.info("Started looping friends reflush for %s", self.penguin['nickname'])

	@inlineCallbacks
	def reflushDatabase(self):
		try:
			self.logger.info("Flushing friends for %s", self.penguin['nickname'])

			yield self.friendsDB.refresh()
			yield self.fetchFriends()
			yield self.fetchRequests()
		except ReferenceError:
			pass

	@inlineCallbacks
	def removeFriend(self, swid):
		if not self.isFriend(swid):
			returnValue(None)

		formerFriend = yield self.invalidateFriendRow(swid)
		myFriends = []
		myFriendsString = self.friendsDB.friends.split(',')
		for f in myFriendsString:
			friend_data = f.split('|')
			if friend_data[0] == swid:
				continue

			myFriends.append(f)

		self.friendsDB.friends = ','.join(myFriends)

		formerFriend_Friends = []
		for f in formerFriend.friends.split(','):
			friend_data = f.split('|')
			if friend_data[0] == self.penguin['swid']:
				continue

			formerFriend_Friends.append(f)

		formerFriend.friends = ','.join(formerFriend_Friends)

		yield self.friendsDB.save()
		yield formerFriend.save()

	@inlineCallbacks
	def friendRequestResponse(self, swid, accepted):
		request = None
		for k in list(self.requests):
			if k[0] == swid:
				request = k
				break

		if request is None:
			returnValue(None)

		self.requests.remove(request)
		self.friendsDB.requests = ','.join(map(lambda x: x[0], self.requests))
		self.friendsDB.save()

		if not accepted:
			returnValue(None)

		#request = tuple(list(request) + [0])
		#self.friends.append(request)

		self.friendsDB.friends = ('{},{}|0'.format(self.friendsDB.friends, swid)).strip(',')
		self.friendsDB.save()

		friendRow = yield self.invalidateFriendRow(swid)
		friendRow.friends = ('{},{}|0'.format(friendRow.friends, self.penguin['swid'])).strip(',')
		friendRow.save()

	@inlineCallbacks
	def handleChangeBFF(self, swid, isBFF):
		if not self.isFriend(swid):
			returnValue(None)

		friend, i = self.getFriend(swid)
		a = list(friend)
		a[3] = int(isBFF)

		self.friends[i] = tuple(a)

		self.friendsDB.friends = ','.join(map(lambda x: '|'.join(map(str, [x[0], x[-1]])), self.friends))
		self.penguin.send('fbf', swid, a[3])

		yield self.friendsDB.save()

	@inlineCallbacks
	def addRequest(self, swid):
		penguin = yield self.penguin.db_getPenguin('swid = ?', swid)
		if penguin is None:
			returnValue(None)

		if self.isFriend(swid) or swid == self.penguin['swid']:
			returnValue(None)

		if swid not in self.friendsDB.requests.split(','):
			self.requests.append((swid, penguin.id, penguin.nickname))
			self.penguin.send('fn', penguin.nickname, swid)

			self.friendsDB.requests = ('{},{}'.format(self.friendsDB.requests, swid)).strip(',')
			yield self.friendsDB.save()

	@inlineCallbacks
	def sendRequest(self, swid):
		penguin = yield self.penguin.db_getPenguin('swid = ?', swid)
		if penguin is None:
			returnValue(None)

		if self.isFriend(swid) or swid == self.penguin['swid']:
			returnValue(None)

		requestFriendRow = yield self.invalidateFriendRow(swid)
		penguinOnline = self.penguin.engine.getPenguinById(penguin.id)

		if penguinOnline is not None:
			yield penguinOnline['friendsHandler'].addRequest(self.penguin['swid'])

		elif not self.penguin['swid'] in requestFriendRow.requests.split(','):
			requestFriendRow.requests = ('{},{}'.format(requestFriendRow.requests, self.penguin['swid'])).strip(',')
			yield requestFriendRow.save()

	def isFriend(self, swid):
		for p in list(self.friends):
			if p[0] == swid:
				return True

		return False

	def getFriend(self, swid):
		ff = list(self.friends)
		for i in range(len(ff)):
			p = ff[i]
			if p[0] == swid:
				return [p, i]

		return [None, -1]

	@inlineCallbacks
	def getFriendDetail(self):
		details = []

		for friend in list(self.friends):
			data = [friend[1], friend[2], friend[0], friend[3]]
			isOnline = yield self.penguin.engine.redis.isPenguinLoggedIn(friend[1])

			if isOnline:
				player_room = yield self.getPlayerRoom(f[1])
				data.append(1)
				data.append(player_room)

			details.append(data)

		returnValue(details)

	@inlineCallbacks
	def fetchRequests(self, checkForChanges = True):
		try:
			if self.friendsDB.requests is None or self.friendsDB.requests == '':
				returnValue(None)

			prev_requests = set(list(self.requests))

			requests = self.friendsDB.requests.split(',')
			dupRequests = list()

			for swid in requests:
				penguin = yield self.penguin.db_getPenguin('swid = ?', swid)
				if penguin is None:
					continue

				self.invalidateFriendRow(swid)
				dupRequests.append((swid, penguin.id, penguin.nickname))

			self.requests.clear()
			self.requests.extend(dupRequests)

			if not checkForChanges:
				returnValue(None)

			cur_requests = set(list(self.requests))
			new_requests = cur_requests - prev_requests

			for r in new_requests:
				self.penguin.send('fn', r[-1], r[0])
		except ReferenceError:
			pass

	@inlineCallbacks
	def getPlayerRoom(self, id):
		online = (yield self.penguin.engine.redis.server.hmget("online:{}".format(id), ['place']))[0]
		online = self.penguin.engine.roomHandler.getRoomByExtId(online) if online else '*Hidden'

		returnValue(online)

	@inlineCallbacks
	def fetchFriends(self, checkForChanges = True):
		try:
			prev_friends = set(list(self.friends))
			prev_friends_swid = [k[0] for k in self.friends]

			if self.friendsDB.friends is None or self.friendsDB.friends == '':
				friends = []
			else:
				friends = self.friendsDB.friends.split(',')

			dupFriends = list()

			for friend in friends:
				swid, isBFF = friend.split('|')
				penguin = yield self.penguin.db_getPenguin('swid = ?', swid)
				if penguin is None:
					continue

				self.invalidateFriendRow(swid)

				dupFriends.append((swid, int(penguin.id), penguin.nickname, int(isBFF)))

			self.friends.clear()
			self.friends.extend(dupFriends)

			if not checkForChanges:
				returnValue(None)

			cur_friends = set(list(self.friends))

			new_friends = cur_friends - prev_friends
			assumed_removed_friends = prev_friends - cur_friends
			
			removed_friends = []
			cur_friends_swid = [k[0] for k in cur_friends]

			for k in assumed_removed_friends:
				if k[0] not in cur_friends_swid:
					removed_friends.append(k)

			for f in new_friends:
				isOnline = yield self.penguin.engine.redis.isPenguinLoggedIn(f[1])

				data = [f[1], f[2], f[0], f[3]]
				player_room = None
				if isOnline:
					player_room = yield self.getPlayerRoom(f[1])
					data.append(1)
					data.append(player_room)

				self.penguin.send('fb', '|'.join(map(str, data)))
				if isOnline:
					self.penguin.send('fo', '|'.join(map(str, [f[0], 1, player_room, 1])))

			for f in removed_friends:
				self.penguin.send('frf', f[0])

			for f in cur_friends:
				isOnline = yield self.penguin.engine.redis.isPenguinLoggedIn(f[1])
				player_room = yield self.getPlayerRoom(f[1])

				self.penguin.send('fo', '|'.join(map(str, [f[0], isOnline, player_room, 0])))
		except ReferenceError:
			pass

	@inlineCallbacks
	def invalidateFriendRow(self, swid):
		row = yield Friend.find(where = ['swid = ?', swid], limit = 1)
		if row is None:
			row = Friend(swid = swid, friends = '', requests = '', ignored = '')
			yield row.save()

		returnValue(row)

	@inlineCallbacks
	def haveRequested(self, player_requesting, player_requested):
		penguin = yield self.penguin.db_getPenguin('swid = ?', player_requested)
		if penguin is None:
			returnValue(True) # so as to make sure it doesn't happen

		friend = yield self.invalidateFriendRow(player_requested)
		requests = []
		
		if friend.requests != '' and friend.requests is not None:
			requests = friend.requests.split(',')

		returnValue(player_requested in requests)