from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Server.Room import Igloo as IglooRoom
from Timeline.Database.DB import Igloo, IglooFurniture, Coin, Asset, IglooLike

from twisted.internet.defer import inlineCallbacks, returnValue

from twistar.registry import Registry

from collections import deque
import logging, json
from time import time

@GeneralEvent.on('onClientDisconnect')
@inlineCallbacks
def handleLockPenguinIgloo(client):
    if client['igloo'] is not None:
        client['igloo'].opened = False
        client['currentIgloo'].locked = True

        yield client['currentIgloo'].save()

@PacketEventHandler.onXT('s', 'g#gm', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerIgloo(client, _id):
    iglooRoom = yield client['RefreshHandler'].initPenguinIglooRoom(_id)
    if iglooRoom == None:
        return

    igloo = yield Igloo.find(iglooRoom._id)
    likes = yield igloo.get_likes_count()
    furnitures = yield igloo.get_furnitures_string()

    details = [igloo.id, 1, 0, int(bool(igloo.locked)), igloo.music, igloo.floor, igloo.location, igloo.type, likes, furnitures]

    client.send('gm', _id, ':'.join(map(str, details)))

@PacketEventHandler.onXT('s', 'g#aloc', WORLD_SERVER)
@inlineCallbacks
def handleBuyLocation(client, _id):
    location = client.engine.iglooCrumbs.getLocationById(_id)
    if location is None:
        returnValue(client.send('e', 402))

    if client['RefreshHandler'].hasAsset(_id, 'l'):
        returnValue(client.send('e', 400))

    if int(client['coins'] + 1) < location.cost:
        returnValue(client.send('e', 401))

    location_db = Asset(penguin_id = client['id'], item = _id, type = 'l')
    yield location_db.save()

    client['coins'] -= location.cost
    yield Coin(penguin_id = client['id'], transaction = -location.cost, comment = "Spent money on buying location. "
                                                                                  "Location: {}".format(_id)).save()
    client['RefreshHandler'].forceRefresh()


@PacketEventHandler.onXT('s', 'g#gail', WORLD_SERVER)
@inlineCallbacks
def getIglooLayoutList(client, _id):
    if not isinstance(client['room'], IglooRoom) or not _id == (client['room'].ext_id - 1000):
        returnValue(None)

    iglooLayouts = list()
    igloos = client['data'].igloos

    total_likes = 0
    igloo_likes = list()

    for i in xrange(len(igloos)):
        igloo = igloos[i].igloo
        furnitures = yield igloo.get_furnitures_string()
        likes = yield igloo.get_likes_count()

        total_likes += likes

        details = [int(igloo.id), i + 1, 0, int(igloo.locked) if igloo.id != client['currentIgloo'].id else False,
                   int(igloo.music), int(igloo.floor), int(igloo.location),
                   int(igloo.type), likes, furnitures]

        iglooLayouts.append(':'.join(map(str, details)))
        igloo_likes.append('|'.join(map(str, [int(igloo.id), likes])))


    client.send('gail', _id, 0, *iglooLayouts)
    client.send('gaili', total_likes, ','.join(igloo_likes))

@PacketEventHandler.onXT('s', 'g#uic', WORLD_SERVER)
@inlineCallbacks
def updateIglooConfiguration(client, _id, _type, floor, location, music, furnitures):
    if client['currentIgloo'].id != _id or (not client['RefreshHandler'].hasAsset(floor, 'fl') and floor != 0) or \
            (not client['RefreshHandler'].hasAsset(location, 'l') and location != 1) or \
            (not client['RefreshHandler'].hasAsset(_type, 'i') and _type != 1):
        return

    furniture_string = ','.join(map(lambda x: '|'.join(map(str, x)), furnitures))
    furnCount = {i[0]: 0 for i in furnitures}

    yield client['currentIgloo'].iglooFurnitures.clear()

    for furn in furnitures:
        furn_id, x, y, rotate, frame = furn
        furniture_db = client['RefreshHandler'].getAsset(furn_id, 'f')
        if furniture_db is None:
            return

        furnCount[furn_id] += 1
        furniture_config = client.engine.iglooCrumbs.getFurnitureById(furn_id)

        if furnCount[furn_id] > furniture_db.quantity or furnCount[furn_id] > furniture_config.max:
            return

    # set furnitures
    client['RefreshHandler'].skip()
    yield client['currentIgloo'].updateFurnitures(furnitures)
    yield client['RefreshHandler'].forceRefresh()

    igloo = client['currentIgloo']
    igloo.type = _type
    igloo.floor = floor
    igloo.location = location
    igloo.music = music

    furn_str = yield igloo.get_furnitures_string()

    likes = yield igloo.get_likes_count()

    yield igloo.save()

    details = [int(igloo.id), 1, 0, int(bool(igloo.locked)), int(igloo.music), int(igloo.floor), int(igloo.location),
               int(igloo.type), likes, furn_str]
    client['igloo'].send('uvi', client['id'], ':'.join(map(str, details)))

@PacketEventHandler.onXT('s', 'g#af', WORLD_SERVER)
@inlineCallbacks
def handleBuyFurniture(client, _id, deduce_coins = True):
    furniture = client.engine.iglooCrumbs.getFurnitureById(_id)
    if furniture is None:
        returnValue(client.send('e', 402))

    if furniture.is_member and not client['member']:
        returnValue(client.send('e', 999))

    furn = client['RefreshHandler'].getAsset(_id, 'f')
    quantity = furn.quantity if furn is not None else 0

    if quantity > furniture.max:
        returnValue(client.send('e', 403))

    if int(client['coins'] + 1) < furniture.cost:
        returnValue(client.send('e', 401))

    if furn is None:
        furn = Asset(penguin_id=client['id'], item=_id, type='f', quantity=1)
        yield furn.save()
    else:
        furn.quantity = int(furn.quantity) + 1
        furn.save()
        client.send('af', _id, client['coins'])

    yield Coin(penguin_id=client['id'], transaction= -furniture.cost * deduce_coins,
               comment="Spent money buying furniture. Furniture: {}".format(_id)).save()

    client['RefreshHandler'].forceRefresh()

@PacketEventHandler.onXT('s', 'g#ag', WORLD_SERVER)
@inlineCallbacks
def handleBuyFloor(client, _id):
    floor = client.engine.iglooCrumbs.getFloorById(_id)
    if floor is None:
        returnValue(client.send('e', 402))

    if client['RefreshHandler'].hasAsset(_id, 'fl'):
        returnValue(client.send('e', 400))

    if int(client['coins'] + 1) < floor.cost:
        returnValue(client.send('e', 401))

    item = Asset(penguin_id=client['id'], item=_id, type='fl')
    yield item.save()

    yield Coin(penguin_id=client['id'], transaction= -floor.cost,
               comment="Spent money buying floor. Floor: {}".format(_id)).save()

    client['RefreshHandler'].forceRefresh()

@PacketEventHandler.onXT('s', 'g#au', WORLD_SERVER)
@inlineCallbacks
def handleBuyIgloo(client, _id):
    igloo = client.engine.iglooCrumbs.getIglooById(_id)
    if igloo is None:
        returnValue(client.send('e', 402))

    if client['RefreshHandler'].hasAsset(_id, 'i'):
        returnValue(client.send('e', 500))

    if int(client['coins'] + 1) < igloo.cost:
        returnValue(client.send('e', 401))

    item = Asset(penguin_id=client['id'], item=_id, type='i')
    yield item.save()

    yield Coin(penguin_id=client['id'], transaction=-igloo.cost,
               comment="Spent money buying igloo. Igloo: {}".format(_id)).save()

    client['RefreshHandler'].forceRefresh()

@PacketEventHandler.onXT('s', 'g#al', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleAddLayout(client, data):
    if len(client['data'].igloos) > 6:
        returnValue(None)

    if not client['member']:
        returnValue(client.send('e', 999))

    igloo = Igloo(penguin_id=client['id'])
    yield igloo.save()
    client['RefreshHandler'].forceRefresh()

    details = [igloo.id, len(client['data'].igloos)+1, 0, int(bool(igloo.locked)), igloo.music, igloo.floor,
               igloo.location, igloo.type, 0, '']
    client.send('al', client['id'], ':'.join(map(str, details)))

@PacketEventHandler.onXT('s','g#pio', WORLD_SERVER)
@inlineCallbacks
def handleIsIglooOpen(client, _id):
    iglooRoom = yield client['RefreshHandler'].initPenguinIglooRoom(_id)
    if iglooRoom is None:
        return

    client.send('pio', int(iglooRoom.opened or client['moderator']))

@PacketEventHandler.onXT('s', 'g#cli', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleCanLike(client, data):
    igloo_id = client['room']._id
    igloo = yield Igloo.find(igloo_id)

    if igloo is None:
        returnValue(client.send('cli', int(igloo.id), 201, '{"canFuck": true, "periodicity": "Hourly", "nextFuck_msec": 0}'))

    likes = yield igloo.iglooLikes.get()
    iglooLikes = {i.penguin_swid: i for i in likes}

    canLike = False
    nextLike = 0
    if client['swid'] not in iglooLikes:
        canLike = True
    else:
        like_obj = iglooLikes[client['swid']]
        lastLike = like_obj.get_time()
        span = (lastLike + 24*60*60) - time()

        canLike = span < 0
        nextLike = (lastLike + 24*60*60) - time()

    client.send('cli', int(igloo.id), 200, json.dumps({'canLike': canLike,
                'periodicity': 'ScheduleDaily', 'nextLike_msecs': int(nextLike*1000)}))
    returnValue(canLike)

@PacketEventHandler.onXT('s', 'g#uiss', WORLD_SERVER)
@inlineCallbacks
def handleUpdateIglooSlotSummary(client, _id, summary):
    igloos = client['RefreshHandler'].getIgloos()

    if _id not in igloos:
        returnValue(None)

    client['currentIgloo'] = igloos[_id].igloo
    client['RefreshHandler'].setupCJMats()
    
    client['igloo']._id = _id
    client.dbpenguin.igloo = client['currentIgloo'].id
    client.dbpenguin.save()

    for i in summary:
        igloo_id = i[0]
        locked = int(bool(i[1]))

        if not locked and not client['member']:
            client.send('e', 999)
            locked = 1

        if not igloo_id in igloos:
            continue

        igloo = igloos[igloo_id].igloo
        igloo.locked = int((igloo_id == _id) and locked)
        igloo.save()

    client['igloo'].opened = not client['currentIgloo'].locked

    igloo = client['currentIgloo']
    likes = yield client['currentIgloo'].get_likes_count()
    fur_str = yield igloo.get_furnitures_string()

    details = [igloo.id, 1, 0, int(bool(igloo.locked)), int(igloo.music), int(igloo.floor), int(igloo.location),
               int(igloo.type), likes, fur_str]
    client['igloo'].send('uvi', client['id'], ':'.join(map(str, details)))


@PacketEventHandler.onXT('s', 'g#gr', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetOpenIgloos(client, data):
    open_igloos = list()
    myLikes = yield client['currentIgloo'].get_likes_count()
    myPopl = len(client['igloo'])
    friends_by_id = map(lambda x: x.friend, client['data'].friends)
    igloos = list(client.engine.iglooCrumbs.penguinIgloos)

    for igloo in igloos:
        if not client['moderator'] and not igloo.opened \
                and igloo.owner != client['id'] and igloo.owner not in friends_by_id:
                continue

        igloo_id = igloo._id
        owner = igloo.owner

        penguin = client.engine.getPenguinById(owner)
        iglooDB = yield Igloo.find(igloo_id)

        if (not client['moderator'] and penguin is None) or iglooDB is None:
            continue

        iglooLikes = yield iglooDB.get_likes_count()
        open_igloos.append('|'.join(map(str, [int(penguin['id']), penguin['nickname'], iglooLikes, len(igloo), 0])))

    client.send('gr', myLikes, myPopl, *open_igloos)

@PacketEventHandler.onXT('s', 'g#grf', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetFriendIgloos(client, data):
    friends_by_id = map(lambda x: x.friend, client['data'].friends)
    friend_igloos = [i for i in client.engine.iglooCrumbs.penguinIgloos if i.owner in friends_by_id]

    availIgloos = list()

    for igloo in friend_igloos:
        _igloo = yield Igloo.find(igloo._id)
        if _igloo is None:
            continue

        likes = yield _igloo.get_likes_count()

        availIgloos.append('|'.join(map(str, [int(igloo.owner), likes])))

    client.send('grf', *availIgloos) if len(availIgloos) > 0 else client.send('%xt%grf%-1%')

@PacketEventHandler.onXT('s', 'g#gili', WORLD_SERVER)
@inlineCallbacks
def handleGetIglooLikes(client, start, end):
    igloo = yield Igloo.find(client['room']._id)
    if igloo is None:
        returnValue(client.send('gili', 0, 204, '{"about": "I don\' think you notice, I don\'t think you care.!"}'))

    likes = yield igloo.get_likes_count()
    likesList = yield igloo.iglooLikes.get(limit = (end, start))

    like = {
        'likedby': {
            'counts': {
                'count': int(likes),
                'maxCount': 5000,
                'accumCount': int(likes)
            },
            'IDs': map(lambda x: x.penguin_swid, likesList)
        }
    }

    client.send('gili', igloo.id, 200, json.dumps(like))

@PacketEventHandler.onXT('s', 'g#li', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleLikeIgloo(client, data):
    igloo_id = client['room']._id
    igloo = yield Igloo.find(igloo_id)
    if igloo is None:
        return

    can_like = yield handleCanLike(client, [])
    if not can_like:
        returnValue(None)

    penguinIglooLike = yield igloo.iglooLikes.get(where = ['penguin_swid = ?', client['swid']], limit = 1)
    if penguinIglooLike is None:
        penguinIglooLike = yield IglooLike(penguin_swid=client['swid'], igloo_id=igloo_id, likes = 0).save()

    penguinIglooLike.likes = int(penguinIglooLike.likes) + 1
    yield penguinIglooLike.save()

    client['room'].sendExcept(client['id'], 'lue', client['swid'], int(penguinIglooLike.likes))