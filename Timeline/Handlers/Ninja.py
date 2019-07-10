from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import Penguin, Ninja, Coin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import sample

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'cd#gcd', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'cd#gcd', WORLD_SERVER, p_r = False)
def handleGetPenguinCards(client, data):
    cards = client['ninjaHandler'].cards
    m = int(bool(client['member']))
    client.send('gcd', '|'.join(map(lambda x: '{},{},{}'.format(x, cards[x][1], 0 if not m else cards[x][1]), cards)))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'ni#gnl', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'ni#gnl', WORLD_SERVER, p_r = False)
def handleGetNinjaLevel(client, data):
    client.send('gnl', client['ninjaHandler'].ninja.belt, int(round(client['ninjaHandler'].progress)), 10)

@PacketEventHandler.onXT('s', 'ni#gfl', WORLD_SERVER, p_r = False)
def handleGetFireLevel(client, data):
    client.send('gfl', client['ninjaHandler'].ninja.fire, int(client['ninjaHandler'].elementalWins['f']['progress']), 5)

@PacketEventHandler.onXT('s', 'ni#gwl', WORLD_SERVER, p_r = False)
def handleGetWaterLevel(client, data):
    client.send('gwl', client['ninjaHandler'].ninja.water, (client['ninjaHandler'].ninja.water) * 10)

@PacketEventHandler.onXT('s', 'ni#gsl', WORLD_SERVER, p_r = False)
def handleGetSnowLevel(client, data):
    client.send('gsl', client['ninjaHandler'].ninja.snow, (client['ninjaHandler'].ninja.snow) * 10)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'ni#gnr', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'ni#gnr', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetNinjaRank(client, data):
    _id = int(data[2][0])
    ninja = yield Ninja.find(where = ['penguin_id = ?', _id], limit = 1)
    if ninja is None:
        returnValue(client.send('gnr', _id))

    client.send('gnr', _id, ninja.belt, ninja.fire, ninja.water, ninja.snow)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'cd#bpc', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'cd#bpc', WORLD_SERVER, p_r = False)
def handleBuyPowerCard(client, data):
    if not client['member']:
        return client.send('e', 999)

    if int(client['coins']) < 1500:
        return client.send('bpc', 401)

    cardsBought = list()
    availablePowerCards = [k for k in client.engine.cardCrumbs.cards if k.power > 0]
    cards = list(sample(availablePowerCards, 3))

    Coin(penguin_id = client['id'], transaction = -1500, comment = "Money spent on buying [3] CJ Power Card. Item: {}".format(','.join(map(repr, cards)))).save()
    
    client['coins'] -= 1500
    client.send('bpc', ','.join(map(str, map(int, cards))), client['coins'])

    for card in cards:
        if card.id not in client['ninjaHandler'].cards:
            client['ninjaHandler'].cards[card.id] = [card, 0]

        client['ninjaHandler'].cards[card.id][1] += 1

    client['ninjaHandler'].ninja.cards = '|'.join(map(lambda x: "{},{}".format(x, client['ninjaHandler'].cards[x][1]), client['ninjaHandler'].cards))
    client['ninjaHandler'].ninja.save()
