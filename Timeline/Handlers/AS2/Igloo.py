from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Server.Room import Igloo as IglooRoom

from Timeline.Handlers.Igloo import handleBuyFurniture, handleBuyFloor, handleBuyIgloo, updateIglooConfiguration
from Timeline.Database.DB import Igloo

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time

@PacketEventHandler.onXT_AS2('s', 'g#gm', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerIgloo(client, _id):
    iglooRoom = yield client['RefreshHandler'].initPenguinIglooRoom(_id)
    if iglooRoom == None:
        return

    igloo = yield Igloo.find(iglooRoom._id)

    #player_id % igloo_type % music_id % floor_id % furniture_list(,)
    client.send('gm', _id, igloo.type, igloo.music, igloo.floor, (yield igloo.get_furnitures_string()))

@PacketEventHandler.onXT_AS2('s', 'g#gr', WORLD_SERVER, p_r = False)
def handleGetOpenIgloos(client, data):
    openIgloos = [client.engine.getPenguinById(i.owner) for i in client.engine.iglooCrumbs.penguinIgloos if i.owner != client['id'] and client.engine.getPenguinById(i.owner) is not None]
    if len(openIgloos) < 1:
        return client.send('%xt%gr%-1%')

    # Sorts the penguins alphabatically acc to their nickname
    igloos = sorted(openIgloos, lambda x, y: 1 - 2 * int(str(x['nickname']) < str(y['nickname'])) if str(x['nickname']) != str(y['nickname']) else 0)
    openIgloos = map(lambda p: '{}|{}'.format(p['id'], p['nickname']), igloos)

    client.send('gr', *openIgloos)

@PacketEventHandler.onXT_AS2('s', 'g#go', WORLD_SERVER, p_r = False)
def handleGetPlayerIgloos(client, data):
    client.send('go', '|'.join(map(str, client['iglooHandler'].igloos)))

@PacketEventHandler.onXT_AS2('s', 'g#af', WORLD_SERVER)
def handleBuyFurnitureAS2(client, _id):
    handleBuyFurniture(client, _id)

@PacketEventHandler.onXT_AS2('s', 'g#ag', WORLD_SERVER)
def handleBuyFloorAS2(client, _id):
    handleBuyFloor(client, _id)

@PacketEventHandler.onXT_AS2('s', 'g#au', WORLD_SERVER)
def handleBuyIglooAS2(client, _id):
    handleBuyIgloo(client, _id)

@PacketEventHandler.onXT_AS2('s', 'g#gf', WORLD_SERVER, p_r = False)
def handleGetFurnitires(client, data):
    client.send('gf', *(map(lambda f: '{}|{}'.format(int(f), f.quantity), client['iglooHandler'].furnitures)))

@PacketEventHandler.onXT_AS2('s', 'g#um', WORLD_SERVER)
def handleActivateIgloo(client, music):
    if client['iglooHandler'].currentIgloo is None:
        return

    client['iglooHandler'].currentIgloo.music = music
    client['iglooHandler'].currentIgloo.save()

@PacketEventHandler.onXT_AS2('s', 'g#ao', WORLD_SERVER)
def handleSetIgloo(client, igloo):
    if client['iglooHandler'].currentIgloo is None or not client['iglooHandler'].hasIgloo(igloo):
        return

    client['iglooHandler'].currentIgloo.type = igloo
    client['iglooHandler'].currentIgloo.save()

@PacketEventHandler.onXT_AS2('s', 'g#ur', WORLD_SERVER)
def handleSaveFurnitureConfiguration(client, furns):
    updateIglooConfiguration(client, igloo.id, igloo.type, igloo.floor, igloo.location, igloo.music, furns)

@PacketEventHandler.onXT_AS2('s', 'g#cr', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'g#or', WORLD_SERVER, p_r = False)
def handleLockAndOpenIgloo(client, data):
    client['iglooHandler'].currentIgloo.locked = int(data[1][-2] == 'c')