'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Cryptography is a tool which helps in calculating the cyrpto-algorithemic functions.
'''
from Timeline.Server.Constants import TIMELINE_LOGGER, AS3_PROTOCOL
from Timeline.Utils.Events import Event

from collections import deque
from string import *
from random import shuffle, choice
import string
from hashlib import md5 as MD5
import bcrypt
import logging

class Crypto(object):

	def __init__(self, penguin):
		super(Crypto, self).__init__()

		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.random_literals = list(ascii_letters + str(digits) + "+_=/_@#$%^&*()-':;!?,.`~\|<>{}")
		self.randomKey = self.random(5) + "-" + self.random(4)
		self.salt = "a1ebe00441f5aecb185d0ec178ca2305Y(02.>'H}t\":E1_root" if self.penguin.Protocol == AS3_PROTOCOL else "Y(02.>'H}t\":E1"

	def swap(self, text, length):
		return text[length:] + text[:length]

	def md5(self, text):
		return MD5(text).hexdigest()
		
	def bcrypt(self, text):
		return bcrypt.hashpw(text, '$2b$12$xxcjQIy5KifXvMdfSdq25O')
		
	def bcheck(self, psd, h):
		return bcrypt.hashpw(str(psd), '$2b$12$xxcjQIy5KifXvMdfSdq25O') == h

	def pureMD5(self, text):
		return MD5(text)

	def random(self, length = 10):
		shuffle(self.random_literals)
		letters = [choice(self.random_literals) for _ in range(length)]

		return join(letters, "")

	def loginHash(self):
		if self.penguin["password"] == None:
			return None

		_hash = self.swap(self.penguin["password"], 16)
		_hash += self.randomKey
		_hash += self.salt

		return self.swap(self.md5(_hash),16)
		
	def confirmHash(self):
		if self.penguin["swid"] == None:
			return None
			
		adkey = self.randomKey.split('-')[1]
		antekey = self.penguin["swid"][1:-1].split('-')
		
		usab = antekey[0][:4] + antekey[-1][:6]
		
		h = usab + adkey
		
		return h