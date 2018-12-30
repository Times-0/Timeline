from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Database.DB import Inventory

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'i#gi', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'i#gi', WORLD_SERVER, p_r = False)
def handleGetInventory(client, data):
    client.send('gi', *map(lambda x: x.item, client['data'].inventories))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'g#gii', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'g#gii', WORLD_SERVER, p_r = False)
def handleGetIglooInventory(client, data):
    assets = client['data'].assets
    furnitures = ','.join(map(lambda x: '{x.item}|{x.purchased}|{x.quantity}'.format(x=x),
                              [k for k in assets if k.type == 'f']))
    igloos = ','.join(map(lambda x: '{x.item}|{x.purchased}'.format(x=x),
                              [k for k in assets if k.type == 'i']))
    locations = ','.join(map(lambda x: '{x.item}|{x.purchased}'.format(x=x),
                              [k for k in assets if k.type == 'l']))
    floors = ','.join(map(lambda x: '{x.item}|{x.purchased}'.format(x=x),
                              [k for k in assets if k.type == 'fl']))

    client.send('gii', furnitures, floors, igloos, locations)

@PacketEventHandler.onXT('s', 'i#currencies', WORLD_SERVER, p_r = False)
def handleGetCurrencies(client, data):
    currencies = client['currencyHandler'].currencies
    cry = ["{}|{}".format(k, currencies[k]) for k in currencies]
    client.send('currencies', ','.join(cry))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'i#ai', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'i#ai', WORLD_SERVER)
@inlineCallbacks
def handleAddItem(client, item):
    item = client.engine.itemCrumbs[item]

    if item is None:
        returnValue(client.send('e', 402))

    if item.is_bait and not client['moderator']:
        # Ban the player?
        client.log('warn', '[Exploit detected] Player trying to add a bait item :', item.id)
        returnValue(client.send('e', 410))

    if client['RefreshHandler'].inInventory(int(item)):
        returnValue(client.send('e', 400))

    if item.is_member and not client['member']:
        returnValue(client.send('e', 999))

    if item.is_epf and not client['epf']:
        #Suspecious?
        returnValue(client.send('e', 410))

    added = yield client.addItem(item)
    if added:
        client['RefreshHandler'].forceRefresh()

        GeneralEvent.call('add-item:{}'.format(item), client)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'i#qpp', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'i#qpp', WORLD_SERVER)
@inlineCallbacks
def handleGetPins(client, _id):
    inventory = yield Inventory.find(where=['penguin_id=?', _id])
    pins = [client.engine.itemCrumbs.getItemById(i.item) for i in inventory
            if client.engine.itemCrumbs.itemByIdIsType(i.item, Pin)]
    pins = map(lambda x: '|'.join(map(str, [x.id, x.release, int(x.is_member)])), pins)

    client.send('qpp', *pins) if len(pins) > 0 else client.send("%xt%qpp%-1%")

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'i#qpa', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'i#qpa', WORLD_SERVER)
@inlineCallbacks
def handleGetAwards(client, _id):
    inventory = yield Inventory.find(where=['penguin_id=?', _id])
    awards = [int(i.item) for i in inventory
            if client.engine.itemCrumbs.itemByIdIsType(i.item, Award)]

    client.send('qpa', *awards) if len(awards) > 0 else client.send("%xt%qpa%-1%")