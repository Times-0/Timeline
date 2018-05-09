'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Login.py handles the incoming XML Packet used to login to server. Packets may not necessarily be `login packet`
'''
from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, AS3_PROTOCOL, AS2_PROTOCOL
from Timeline import Username, Password, Nickname
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent

from Timeline.Utils.Friends import Friend

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging

logger = logging.getLogger(TIMELINE_LOGGER)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXML('verChk', LOGIN_SERVER)
@PacketEventHandler.onXML('verChk', WORLD_SERVER)
@PacketEventHandler.onXML_AS2('verChk', LOGIN_SERVER)
@PacketEventHandler.onXML_AS2('verChk', WORLD_SERVER)
def APIVersionCheck(client, version):
	if version != 153:
		client.send(client.PacketHandler.buildXML({"msg" : {'t' : 'sys', 'body' : {'action' : 'apiKO', 'r' : '0'} } }))
		return client.disconnect()

	client.send(client.PacketHandler.buildXML({"msg" : {'t' : 'sys', 'body' : {'action' : 'apiOK', 'r' : '0'} } }))
	if client.handshakeStage < 1:
		client.handshakeStage = 1 # Just a note that API version is verified!

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXML('rndK', LOGIN_SERVER, p_r = False)
@PacketEventHandler.onXML('rndK', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXML_AS2('rndK', LOGIN_SERVER, p_r = False)
@PacketEventHandler.onXML_AS2('rndK', WORLD_SERVER, p_r = False)
def GetPenguinRandomKey(client, body):
	client.send(client.PacketHandler.buildXML({"msg" : {'t' : 'sys', 'body' : {'action' : 'rndK', 'r' : '-1', 'k' : list([client.CryptoHandler.randomKey]) } } }))


'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXML('login', LOGIN_SERVER)
@PacketEventHandler.onXML_AS2('login', LOGIN_SERVER)
@inlineCallbacks
def HandlePrimaryPenguinLogin(client, user, passd):
	exist = yield client.db_penguinExists('username', user)
	
	if not exist:
		client.send("e", 101)
		returnValue(client.disconnect())
	
	client.penguin.username = user

	yield client.db_init()

	client.penguin.username = Username(client.dbpenguin.username, client)
	client.penguin.password = Password(client.dbpenguin.password, client)
	if not client.checkPassword(passd):
		client.send('e', 101)
		returnValue(client.disconnect())

	client.penguin.id = client.dbpenguin.id

	banned = yield client.banned()
	if banned:
		returnValue(0)
		
	client.penguin.swid = client.dbpenguin.swid
	
	key = client.CryptoHandler.confirmHash()
	confh = client.CryptoHandler.bcrypt(key)
	fkey = client.CryptoHandler.md5(key)
	
	client.engine.redis.server.set("conf:{0}".format(client.dbpenguin.id), key, 15*60)

	world = list()

	w, wu = yield client.engine.redis.getWorldServers()

	for k in w:
		p = w[k]
		bars = int(int(p['population']) * 5 / int(p['max']))
		world.append("{},{}".format(k, bars))
		
	world = '|'.join(world)

	if client.Protocol == AS3_PROTOCOL:
		player_data = "{}|{}|{}|{}|NULL|45|2".format(client.dbpenguin.id, client.dbpenguin.swid, client.dbpenguin.nickname, client.CryptoHandler.bcrypt(key))
		email = client.dbpenguin.email[0] + '***@' + client.dbpenguin.email.split('@')[1]
	
		client.send('l', player_data, confh, fkey, world, email)

	elif client.Protocol == AS2_PROTOCOL:
		friendsDB = yield Friend.find(where = ['swid = ?', client.dbpenguin.swid], limit = 1)
		friends = map(lambda x: x.split('|')[0], friendsDB.friends.split(',')) if friendsDB is not None else []
		friends = set(friends)

		'''
		World = {user1, user2, ...}
		Friends = {user_p, user_q, ...}

		if Friends in World, then, World - Friends will be a set such that n(W-F) < n(W)
		'''
		worldsWithFriends = list(i for i in wu if len(wu[i]) != len(wu[i] - friends))
		wwf = '|'.join(worldsWithFriends)

		client.send('l', client.dbpenguin.id, confh, wwf, world)
	
	returnValue(client.disconnect())
	

'''
AS2 Specific World Server Login Handler
'''
@PacketEventHandler.onXML_AS2('login', WORLD_SERVER)
@inlineCallbacks
def HandleWorldPenguinLoginAS2(client, user, confirmHash, loginkey):
	exist = yield client.db_penguinExists('username', user)

	if not exist:
		client.send('e', 101)
		returnValue(client.disconnect())

	penguin = yield client.db_getPenguin('username = ?', user)

	yield HandleWorldPenguinLogin(client, penguin.nickname, penguin.id, penguin.swid, confirmHash, confirmHash, loginkey+confirmHash)

@PacketEventHandler.onXML('login', WORLD_SERVER)
@inlineCallbacks
def HandleWorldPenguinLogin(client, nickname, _id, swid, password, confirmHash, loginkey):
	exist = yield client.db_penguinExists(value = _id)
	
	if not exist:
		client.send("e", 101)
		returnValue(client.disconnect())

	client.penguin.nickname = Nickname(nickname, client)
	client.penguin.password = password
	client.penguin.id = _id
	client.penguin.swid = swid

	yield client.db_init()
	client.penguin.username = Username(client.dbpenguin.username, client)
	if not client.dbpenguin.swid == swid or not client.dbpenguin.nickname == nickname:
		client.send('e', 101)
		returnValue(client.disconnect())

	banned = yield client.banned()
	if banned:
		returnValue(0)
	a = yield client.engine.redis.server.ping()
	print a
	isLoggedIn = yield client.engine.redis.isPenguinLoggedIn(client.penguin.id)
	if isLoggedIn:
		client.send('e', 3)
		returnValue(client.disconnect())

	details = yield client.engine.redis.getPlayerKey(client.penguin.id)
	if not details:
		client.send('e', 101)
		returnValue(client.disconnect())

	if not client.CryptoHandler.bcheck(details, loginkey[32:]) or not client.CryptoHandler.bcheck(details, confirmHash) or not client.CryptoHandler.bcheck(details, password):
		client.send('e', 101)
		print loginkey, loginkey[32:]
		returnValue(client.disconnect())
	
	yield client.engine.redis.server.delete("conf:{}".format(client.penguin.id))
	yield client.engine.redis.server.hmset("online:{}".format(client.penguin.id), {
		'server' : client.engine.id,
		'place'  : 0,
		'playing': 0,
		'waddling': 0,
		'joined' : 0
		})

	client.ReceivePacketEnabled = True

	client.send('l', 'timeline')


def init():
	logger.debug('Login Server::Login initiated!')
	logger.debug('World Server::Login initiated!')