from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Crumbs.Postcards import Postcard

from twisted.internet.defer import inlineCallbacks, returnValue
from twistar.dbobject import DBObject

from collections import deque
import logging
import time

class Mail(DBObject):

	@inlineCallbacks
	def str(self, db):
		peng = yield db.db_getPenguin('ID = ?', self.from_user)
		if peng is None:
			peng = 'Club Penguin Team'

		data = [peng, self.from_user, int(self.type), self.description, int(time.mktime(self.sent_on.timetuple())), int(self.id), int(self.opened)]
		returnValue('|'.join(map(str, data)))

	def __int__(self):
		return int(self.id)

class MailHandler(list):

	def __init__(self, penguin):
		super(MailHandler, self).__init__([])

		self.penguin = penguin
		self.fetchPostcards()

	def getMail(self, _id):
		if isinstance(_id, str):
			try:
				_id = int(_id)
			except:
				return None

		elif isinstance(_id, Mail):
			_id = int(_id.id)

		_id = int(_id)
		for mail in self:
			if int(mail.id) == _id:
				return mail

		return None

	def clear(self):
		del self[:]

	@inlineCallbacks
	def fetchPostcards(self):
		self.clear()

		mails = yield Mail.find(where = ['to_user = ? AND junk != 1', self.penguin['id']], orderby = 'sent_on DESC')
		self += mails

	@inlineCallbacks
	def sendMail(self, to, _id):
		postcard = self.penguin.engine.postcardHandler[_id]
		if postcard is None:
			self.penguin.send('ms', self.penguin['coins'], 0)
			returnValue(None)

		if not self.penguin['coins'] + 1 > 10:
			self.penguin.send('ms', self.penguin['coins'], 2)
			returnValue(None)

		mail = yield self.createNewMail(postcard, to)
		if mail is not  None:
			self += mail
		
		self.penguin['coins'] -= 10
		self.penguin.send('ms', self.penguin['coins'], int(mail is not None))

		is_o = yield self.penguin.engine.redis.isPenguinOnlineOnServer(to, self.penguin.engine.id)
		if is_o:
			peng = self.penguin.engine.getPenguinById(to)
			if peng['mail'] is not None:
				peng['mail'].refresh()

	@inlineCallbacks
	def deleteMail(self, _id, ref = True):
		_id = int(_id)
		if not _id in self:
			returnValue(None)

		mail = self.getMail(_id)
		mail.junk = 1
		yield mail.save()
		self.remove(mail)

		if ref:
			yield self.refresh()

	@inlineCallbacks
	def setMailsChecked(self):
		for mail in self:
			mail.opened = 1
			yield mail.save()

	@inlineCallbacks
	def deleteAllMail(self):
		for mail in list(self):
			yield self.deleteMail(mail, False)

		self.penguin.send('mdp', len(self))
		self.refresh()

	@inlineCallbacks
	def refresh(self):
		old = list(self)
		yield self.fetchPostcards()

		new = list(self)
		for i in old:
			if i in new:
				new.remove(i)

		self.receivedNewMails(new)

	@inlineCallbacks
	def receivedNewMails(self, mails):
		for mail in mails:
			peng = yield self.penguin.db_getPenguin('ID = ?', mail.from_user)
			if peng is None:
				peng = 'Club Penguin Team'

			sent_on = int(time.mktime(mail.sent_on.timetuple()))
			self.penguin.send('mr', peng, int(mail.from_user), int(mail.type), mail.description, sent_on, int(mail.id), mail.opened)

	def append(self, postcard):
		if not isinstance(postcard, Mail):
			return

		super(MailHandler, self).append(postcard)

	@inlineCallbacks
	def createNewMail(self, postcard, to):
		if not isinstance(postcard, Postcard):
			returnValue(None)

		m = yield Mail(to_user = to, from_user = self.penguin['id'], type = int(postcard), description = str(postcard)).save()
		returnValue(m)

	def __repr__(self):
		return 'MailHandler<{}#{}>'.format(self.penguin['id'], self.penguin['nickname'])

	def __contains__(self, k):
		if isinstance(k, list):
			for i in k:
				if not k in self:
					return False

			return True

		elif isinstance(k, int):
			for i in self:
				if int(i.id) == k:
					return True

			return False

		elif isinstance(k, Mail):
			return int(Mail.id) in self

		else:
			return False

	@inlineCallbacks
	def str(self):
		data = list()
		for i in self:
			d = yield i.str(self.penguin)
			data.append(d)

		returnValue('%'.join(data))

	def __iadd__(self, mail):
		if isinstance(mail, list):
			for m in mail:
				self.append(m)
		else:
			self.append(mail)

		return self

@GeneralEvent.on('joined-room')
def handleRefreshMail(client, event):
	if len(client['prevRooms']) < 2:
		return
		
	if client['mail'] is not None:
		client['mail'].refresh()