from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, DIGGABLES, GOLD_DIGGABLES, DIGGABLE_FURN, GOLD_DIGGABLE_FURN
from Timeline.Utils.Puffle import Puffle
from Timeline.Utils.Mails import Mail
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Igloo import handleBuyFurniture
from Timeline.Handlers.Item import handleGetCurrencies

from Timeline.Handlers.Puffle import handleAdopt, handlePufflePlay, handlePuffleRest, handlePuffleWalk

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time
from random import choice, randint, shuffle

def getAS2PuffleString(client, puffles):
	puffles_as2_str = list()
	for puffle in puffles:
		p_id, p_type, p_sub_type, p_name, p_adopt, p_food, \
		p_play, p_rest, p_clean, p_hat, p_x, p_y, is_walking = puffle.split('|')

		p_crumb = client.engine.puffleCrumbs[p_sub_type]

		p_max_food, p_max_clean, p_max_health = map(str, (p_crumb.hunger, 100, p_crumb.health))
		p_as2 = '|'.join((p_id, p_name, p_type, p_clean, p_food, p_rest, p_max_health, p_max_food, '100', p_x, p_y, p_hat, is_walking))

		puffles_as2_str.append(p_as2)

	return '%'.join(puffles_as2_str)

@PacketEventHandler.onXT_AS2('s', 'p#pg', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerPuffles(client, _id, sendPacket = True):
	client['puffleHandler'].refreshPuffleHealth()
	puffles = yield client['puffleHandler'].getPenguinPuffles(_id, 0)

	puffles = puffles.split('%') if puffles != '' else []

	(client.send('pg', getAS2PuffleString(client, puffles)) if len(puffles) > 0 else client.send('%xt%pg%-1%')) if sendPacket else None

	returnValue(puffles)

@PacketEventHandler.onXT_AS2('s', 'p#pgu', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetMyPlayerPuffles(client, data):
	clientPuffles = yield handleGetPlayerPuffles(client, client['id'], False)
	client.send('pgu', getAS2PuffleString(client, clientPuffles)) if len(clientPuffles) > 0 else client.send('%xt%pgu%-1%')

@PacketEventHandler.onXT_AS2('s', 'p#pn', WORLD_SERVER)
@inlineCallbacks
def handleAS2PuffleAdopt(client, _type, name):
	puffleAdopted = yield handleAdopt(client, _type, name, _type)
	if puffleAdopted is not None:
		client.send('pn', client['coins'], getAS2PuffleString(client, [puffle_db]))

@PacketEventHandler.onXT_AS2('s', 'p#pip', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'p#pir', WORLD_SERVER)
def handleInitiateInteraction(client, data):
	puffle, x, y = map(int, data[2])
	if client['puffleHandler'].getPuffleById(puffle) is None:
		return

	client.send(data[1], puffle, x, y)

@PacketEventHandler.onXT_AS2('s', 'p#ip', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'p#ir', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'p#pp', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'p#pr', WORLD_SERVER, p_r = False)
def handlePuffleInteract(client, data):
	function = handlePuffleRest if data[1].endswith('r') else handlePufflePlay
	puffle = int(data[2][0])
	puffle = function(client, puffle, False)

	if puffle is not None:
		client['room'].send(data[1] , getAS2PuffleString(client, [puffle]), *(map(int, data[2][1:])))

@PacketEventHandler.onXT_AS2('s', 'p#if', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'p#pf', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'p#pb', WORLD_SERVER, p_r = False)
def handleFeedPuffle(client, data):
	puffle = client['puffleHandler'].getPuffleById(int(data[2][0]))
	if puffle is None:
		return

	health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[int(puffle.type)])

	if puffle.rest < 10 or puffle.clean < 10:
		return

	feeding = data[1].endswith('f')
	bathing = data[1].endswith('b')
	treating = data[1].endswith('t')

	fx, rx, px, cx = (50, -5, -5, 0) if feeding else (-5, -5, 10, 100)
	puffle.food = min(hunger, puffle.food*hunger + fx)/hunger * 100
	puffle.clean = min(health, puffle.clean*health + cx)/health * 100
	puffle.rest = min(rest, puffle.rest*rest + rx)/rest * 100
	puffle.play = min(100, puffle.play + px)

	puffle.save()
	
	client.send(data[1], client['coins'], getAS2PuffleString(client, [puffle]), *(map(int, data[2][1:])))

@PacketEventHandler.onXT_AS2('s', 'p#pw', WORLD_SERVER, p_r = False)
def handlePuffleWalk(client, data):
	puffle, isWalking = map(int, data[2])

	success = handlePuffleWalk(client, puffle, isWalking, False)
	if success:
		client.send('pw', client['id'], getAS2PuffleString(client, [puffle]))