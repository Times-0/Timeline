'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
This packet handler file implements XML Handlers - apiChk, rndK, login
'''
from Timeline.Server.Constants import TIMELINE_LOGGER, PACKET_TYPE, PACKET_DELIMITER, LOGIN_SERVER, WORLD_SERVER, LOGIN_SERVER_ALLOWED
from Timeline.Utils.Events import PacketEventHandler

from twisted.internet import threads
from twisted.internet.defer import Deferred

from collections import deque
import logging

'''
Example:
@PacketEventHandler._PacketRule('action/category', 'type/handler')
def handler(data):
	// do something

	return  list([list(args), dict(kwargs)])
'''


'''
Rule : Version = int version, else error.
'''
@PacketEventHandler.XMLPacketRule('verChk', LOGIN_SERVER)
@PacketEventHandler.XMLPacketRule('verChk', WORLD_SERVER)
def XMLVersionCheckRule(data):
	version = data.find("ver").get("v")
	v = int(version)
	
	return [[v], {}]

@PacketEventHandler.XMLPacketRule('login', LOGIN_SERVER)
def XMLoginLiteralsRule(data):
	login = data.find("login")

	username = login.find("nick").text.rstrip(' ').lstrip(' ')
	password = login.find("pword").text

	login_arena = login.get("z")
	if login_arena not in LOGIN_SERVER_ALLOWED:
		raise Exception("[TE010] Unknown login server : {0}".format(login_arena))

	username_length = len(username)
	if username_length < 4 or username_length > 12:
		raise Exception("[TE011] Invalid username length - {0}".format(len(username)))

	username_w_space = username.replace(" ", '')
	if not username_w_space.isalnum():
		raise Exception("[TE012] Invalid characters found in username - {0}".format(username))

	# Is password check necessary?
	password_length = len(password)
	if password_length != 32:
		raise Exception("[TE013] Invalid MD5 hash (length) - {0} [{1}]".format(password, password_length))

	# Check for hexadecimal validity
	try: int(password, 16)
	except: raise Exception("[TE014] Invalid md5 hash (hexadecimal check) - {0}".format(password))

	return [[username, password], {}]

@PacketEventHandler.XMLPacketRule('login', WORLD_SERVER)
def XMLWorldLiteralsRule(data):
	login = data.find('login')

	nick = login.find('nick').text.strip()
	passd = login.find('pword').text

	_id, swid, user, pwd = nick.split('|')[:4]

	_id = int(_id)
	swid = str(swid)

	if not (swid.startswith('{') and swid.endswith('}') and len(swid) == 38):
		raise Exception("[TE015] Invalid SWID : {}".format(swid))

	username_length = len(user)
	if username_length < 4 or username_length > 20:
		raise Exception("[TE011] Invalid username length - {0}".format(len(user)))

	username_w_space = user.replace(" ", '')
	if not username_w_space.isalnum():
		raise Exception("[TE012] Invalid characters found in username - {0}".format(user))

	loginKey, confirmHash = passd.split('#')
	if loginKey == '' or confirmHash == '' or loginKey == None or confirmHash == None:
		raise Exception("[TE016] Invalid LoginKey or ConfirmationHash : {}, {}".format(loginKey, confirmHash))

	return [[_id, user, swid, pwd, confirmHash, loginKey], {}]