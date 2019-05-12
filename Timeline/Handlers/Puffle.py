from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, DIGGABLES, GOLD_DIGGABLES, DIGGABLE_FURN, GOLD_DIGGABLE_FURN
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Igloo import handleBuyFurniture
from Timeline.Handlers.Item import handleGetCurrencies
from Timeline.Database.DB import Puffle, Coin, CareItem, Mail

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging, json
from time import time
from random import choice, randint, shuffle

PENDING = {}

@GeneralEvent.on('penguin-logged')
def setPuffleDigRest(client):
    client.penguin.lastDig = time()
    client.penguin.lastDigOC = time()

    client.send('pgu', *client['data'].puffles) if len(client['data'].puffles) > 0 \
        else client.send('%xt%pgu%-1%')


@GeneralEvent.on('onClientDisconnect')
def handleMakePuffleHomeAlone(client):
    if client['walkingPuffle'] is not None:
        client['walkingPuffle'].walking = 0
        client['walkingPuffle'].save()

@PacketEventHandler.onXT('s', 'p#getdigcooldown', WORLD_SERVER, p_r = False)
def handleGetDigCoolDown(client, data):
    if client['walkingPuffle'] is None:
        return

    cmd = max(0, 120 - int(time() - client['lastDig']))
    client.send('getdigcooldown', cmd)

@PacketEventHandler.onXT('s', 'p#revealgoldpuffle', WORLD_SERVER, p_r = False)
def handleCanRevealGP(client, data):
    if client['canAdoptGold']:
        client['room'].send('revealgoldpuffle', client['id'])

@PacketEventHandler.onXT('s', 'p#puffledigoncommand', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT('s', 'p#puffledig', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handlePuffleDig(client, data):
    if client['walkingPuffle'] is None:
        return

    cmd = data[1]
    lDC = 'lastDig'
    if 'oncommand' in cmd:
        lDC += 'OC'
    lastDig = client[lDC]

    cmd = max(0, (40 if 'oncommand' not in cmd else 120) - int(time() - client[lDC]))
    if cmd:
        returnValue(0) # no dig

    digables = range(5)
    setattr(client.penguin, lDC, time())

    digChances = list()
    canDigGold = client['walkingPuffle'].state == 1
    for i in digables:
        if i is 4 and not canDigGold:
            continue

        elif i is 1 and canDigGold:
            continue

        chance = randint(0, 3 + 4 * int(canDigGold and i is 'gold'))
        digChances += [i for _ in range(chance)]

    dig = choice(digChances)

    if dig == 0:
        coinsDug = int(10 * randint(1, 40))
        Coin(penguin_id=client['id'], transaction=coinsDug, comment="Coins earned by puffle dig. Puffle: {}".format(client['walkingPuffle'].id)).save()
        client['coins'] += coinsDug

        returnValue(client['room'].send('puffledig', client['id'], client['walkingPuffle'].id, 0, 0, coinsDug, 0, 0))

    elif dig == 1:
        returnValue(client['room'].send('nodig', client['id'], 1))

    elif dig == 2:
        diggables = DIGGABLE_FURN
        if client['puffleHandler'].walkingPuffle.id == 11:
            diggables += GOLD_DIGGABLE_FURN

        shuffle(diggables)
        for dug in diggables:
            tryDigging = yield handleBuyFurniture(client, dug, False)
            if tryDigging is True:
                returnValue(client['room'].send('puffledig', client['id'], client['walkingPuffle'].id, 2, dug, 1, 0, 0))

        Coin(penguin_id=client['id'], transaction=600, comment="Coins earned by puffle dig. Puffle: {}".format(client['walkingPuffle'].id)).save()
        client['coins'] += 600
        returnValue(client['room'].send('puffledig', client['id'], client['walkingPuffle'].id, 0, 0, 600, 0, 0))

    elif dig == 3:
        diggables = DIGGABLES
        if client['walkingPuffle'].id == 11:
            diggables += GOLD_DIGGABLES

        shuffle(diggables)
        for dug in diggables:
            if not client['RefreshHandler'].inInventory(dug):
                client.addItem(dug, 'Dug item')

                returnValue(client['room'].send('puffledig', client['id'], client['walkingPuffle'].id, 3, dug, 1, 0, 0))

        Coin(penguin_id=client['id'], transaction=500, comment="Coins earned by puffle dig. Puffle: {}".format(client['walkingPuffle'].id)).save()
        returnValue(client['room'].send('puffledig', client['id'], client['walkingPuffle'].id, 0, 0, 500, 0, 0))

    elif dig == 4:
        dug = randint(1, 3)
        client['currencyHandler'].currencies[1] += dug
        client['currencyHandler'].refreshCurrencies()
        handleGetCurrencies(client, [-1, '', []])

        if client['currencyHandler'].currencies[1] > 14:
            client.penguin.canAdoptGold = True

        returnValue(client['room'].send('puffledig', client['id'], client['walkingPuffle'].id, 4, 0, dug, 0, 0))


@PacketEventHandler.onXT('s', 'p#pg', WORLD_SERVER)
@inlineCallbacks
def handleGetPuffles(client, _id, isBackyard):
    puffles = client['data'].puffles if _id == client['id'] else (yield Puffle.find(where=['penguin_id=?', _id]))
    puffles = [str(i) for i in puffles if i.backyard == isBackyard]

    client.send('pg', len(puffles), *puffles)

@PacketEventHandler.onXT('s', 'p#pgmps', WORLD_SERVER, p_r = False)
def handleGetMyPuffle(client, data):
    #ID, Food, Play, Rest, Clean

    puffles = ['{x.id}|{x.food}|{x.play}|{x.rest}|{x.clean}'.format(x=i) for i in client['data'].puffles]

    client.send('pgmps', ','.join(puffles)) if len(puffles) > 0 else client.send('%xt%pgmps%-1%')

@PacketEventHandler.onXT('s', 'p#pw', WORLD_SERVER)
def handlePuffleWalk(client, puffle, isWalking, sendPacket = True):
    puffleById = {i.id : i for i in client['data'].puffles}

    if puffle not in puffleById or puffleById[puffle].walking == isWalking:
        return

    puffle = puffleById[puffle]

    if client['walkingPuffle'] is not None:
        if client['walkingPuffle'].id is puffle.id and isWalking:
            return None

        client['walkingPuffle'].walking = 0
        client['walkingPuffle'].state = 0
        client['walkingPuffle'].save()

        client['currencyHandler'].currencies[1] = 0
        client['currencyHandler'].refreshCurrencies()
        client.penguin.canAdoptGold = False

    puffle.walking = int(isWalking)
    puffle.save()

    client['walkingPuffle'] = puffle if isWalking else None

    client['room'].send('pw', client['id'], puffle.id, puffle.type, puffle.subtype, int(isWalking), puffle.hat) \
        if sendPacket else None

@PacketEventHandler.onXT('s', 'p#pufflewalkswap', WORLD_SERVER)
def handlePuffleSwap(client, puffle):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None
    if client['walkingPuffle'] is None or puffle is None or client['walkingPuffle'].id == puffle.id:
        return

    client['walkingPuffle'].walking = 0
    client['walkingPuffle'].state = 0
    client['walkingPuffle'].save()

    puffle.walking = 1
    puffle.save()

    client['currencyHandler'].currencies[1] = 0
    client['currencyHandler'].refreshCurrencies()
    client.penguin.canAdoptGold = False

    client['walkingPuffle'] = puffle

    client['room'].send('pufflewalkswap', *map(int, [client['id'], puffle.id, puffle.type, puffle.subtype, puffle.walking, puffle.hat]))

@PacketEventHandler.onXT('s', 'p#puffletrick', WORLD_SERVER)
def handlePuffleTrick(client, trick):
    client['room'].send('puffletrick', int(client['id']), trick)

@PacketEventHandler.onXT('s', 'p#puffleswap', WORLD_SERVER)
def handlePuffleSwapIB(client, puffle, isBackyard):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    if puffle is None:
        return

    if (isBackyard and bool(puffle.backyard)) or (not isBackyard and not bool(puffle.backyard)): # Check if player is in igloo?
        return #CRAZY!

    if bool(puffle.walking):
        puffle.walking = 0
        client['walkingPuffle'] = None

    puffle.backyard = isBackyard
    puffle.save()

    client['room'].send('puffleswap', int(puffle.id), 'backyard' if isBackyard else 'igloo')

@PacketEventHandler.onXT('s', 'p#pgpi', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handlePuffleCareInventory(client, data):
    careItems = yield client.dbpenguin.careItems.get()
    items = ['{i.item}|{i.quantity}'.format(i=k) for k in careItems]

    client.send('pgpi', *items) if len(items) > 0 else client.send('%xt%pgpi%-1%')

@PacketEventHandler.onXT('s', 'p#papi', WORLD_SERVER)
@inlineCallbacks
def handleAddPuffleItem(client, _id):
    if _id not in client.engine.puffleCrumbs.puffleItems:
        returnValue(client.send('e', 402))

    item_details = client.engine.puffleCrumbs.puffleItems[_id]

    cost = int(item_details['cost'])
    is_member = bool(int(item_details['is_member_only']))
    quantity = int(item_details['quantity'])

    if is_member and not client['member']:
        returnValue(client.send('e', 999))
    if cost > int(client['coins']):
        returnValue(client.send('e', 401))

    yield Coin(penguin_id=client['id'], transaction= -cost, comment="Spent money buying puffle care item. Item: {}"
               .format(_id))
    client['coins'] -= cost

    careItems = yield client.dbpenguin.careItems.get()
    careItemsById = {i.id : i for i in careItems}
    if _id not in careItemsById:
        yield CareItem(penguin_id=client['id'], item=_id, quantity=quantity).save()
    else:
        careItemsById[_id].quantity = int(careItemsById[_id].quantity) + quantity
        yield careItemsById[_id].save()

    client['RefreshHandler'].forceRefresh()

@PacketEventHandler.onXT('s', 'p#phg', WORLD_SERVER, p_r = False)
def handleGetStatus(client, data):
    client.send('phg', 1)

@PacketEventHandler.onXT('s', 'p#puphi', WORLD_SERVER)
def handleHatUpdate(client, puffle, hat):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    careItems = yield client.dbpenguin.careItems.get()
    careItemsById = {i.id: i for i in careItems}

    item = client['puffleHandler'].getPuffleItem(hat)

    if puffle is None or (item is None and hat != 0) or hat not in careItemsById:
        return

    hat_prev = int(puffle.hat)
    if hat_prev != 0 and hat_prev in careItemsById and hat_prev != puffle.hat:
        careItemsById[hat_prev].quantity = int(careItemsById[hat_prev].quantity) + 1
        careItemsById[hat_prev].save()

    if hat == 0:
        puffle.hat = 0
        puffle.save()
    else:
        curr_hat = careItemsById[hat]
        if curr_hat.quantity < 1:
            return

        curr_hat.quantity = int(curr_hat.quantity) - 1
        curr_hat.save()

    client['room'].send('puphi', int(puffle.id), hat)

@PacketEventHandler.onXT('s', 'p#pcn', WORLD_SERVER, p_r = False)
def handlePuffleCheckName(client, data):
    client.send('pcn', data[2][0]) # TODO

@PacketEventHandler.onXT('s', 'p#checkpufflename', WORLD_SERVER, p_r = False)
def handleCheckPuffleName(client, data):
    name = data[2][0].strip()
    n_w_s = name.replace(' ', '')

    check = 1

    if not n_w_s.isalnum() or not (3 < len(name) < 21):
        check = 0

    if client['id'] in PENDING:
        print PENDING
        check = int(name not in PENDING[client['id']])

    for puffle in client['data'].puffles:
        if puffle.name == name:
            check = 0
            break

    client.send('checkpufflename', name, check)
    return bool(check)

@PacketEventHandler.onXT('s', 'p#pn', WORLD_SERVER)
@inlineCallbacks
def handleAdopt(client, _type, name, sub_type, sendPuffleAdopt = True):
    if not handleCheckPuffleName(client, [0, 0, [name]]):
        returnValue(None)

    if not client['id'] in PENDING:
        PENDING[client['id']] = []

    PENDING[client['id']].append(name)

    puffle = client.engine.puffleCrumbs[sub_type]
    if puffle is None or (_type == 10 and not client['canAdoptRainbow']) or (_type == 11 and not client['canAdoptGold']):
        PENDING[client['id']].remove(name)
        returnValue(None)

    cost = 800
    if sub_type in client.engine.puffleCrumbs.defautPuffles:
        cost = 400

    if puffle.member and not client['member']:
        PENDING[client['id']].remove(name)
        client.send('e', 999)
        returnValue(None)

    now = int(time())
    care = '{"food" : {now},"play" : {now},"bath" : {now}}'.replace('{now}', str(now))
    puffle_db = yield Puffle(penguin_id = client['id'], name = name, type = _type, subtype = sub_type,
                             food = puffle.hunger, play = 100, rest = puffle.rest, clean = puffle.health,
                             lastcare = care).save()

    yield Coin(penguin_id=client['id'], transaction= -cost,
               comment="Pet Puffle Adoption. Puffle: {}".format(sub_type)).save()
    client['coins'] -= cost
    yield Mail(penguin_id=client['id'], from_user=0, type=111, description=name).save()

    client['RefreshHandler'].forceRefresh()

    PENDING[client['id']].remove(name)
    returnValue(puffle_db)

@PacketEventHandler.onXT('s', 'p#prp', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleSendPuffleBackToTheWoods(client, data):
    puffle = int(data[2][0])

    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    if puffle is None:
        returnValue(0)

    pMonths = int((time() - puffle.adopt())/60/60/24/30.5)
    dcoins = 500 + 10 * pMonths
    if int(client['coins']) < dcoins:
        dcoins = int(client['coins'])

    yield Coin(penguin_id=client['id'], transaction=-dcoins,
               comment="Penalized for abandoning adopted puffle. Puffle: {}, ID: {}".format(puffle.type, puffle.id))

    client['coins'] -= dcoins

    handlePuffleWalk(client, int(puffle.id), False)
    post_id = 100 + int(puffle.type)
    if puffle.type == 7:
        post_id = 169
    elif puffle.type == 8:
        post_id += 1

    yield Mail(penguin_id=client['id'], from_user=0, type=post_id, description=str(puffle.name)).save()
    yield puffle.delete()

    client['RefreshHandler'].forceRefresh()

@PacketEventHandler.onXT('s', 'p#ps', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'p#ps', WORLD_SERVER)
def handlePuffleFrame(client, puffle, frame):
    peng = client['room'].owner #Check player in igloo

    # Maybe check for puffle in igloo too?
    client['room'].send('ps', puffle, frame)

@PacketEventHandler.onXT('s', 'p#pm', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'p#pm', WORLD_SERVER)
@inlineCallbacks
def handlePuffleMove(client, puffle, x, y):
    peng = client['room'].owner
    peng = client.engine.getPenguinById(peng)

    if peng is not None:
        puffleById = {i.id: i for i in client['data'].puffles}
        puffle = puffleById[puffle] if puffle in puffleById else None
        if puffle is None:
            returnValue(0)

        puffle.x, puffle.y = x, y
        client.engine.redis.server.hmset("puffle:{}".format(puffle), {'x' : x, 'y' : y})
        client['room'].send('pm', puffle, x, y)

    else:
        # Check if puffle in igloo
        puffle = yield Puffle.find(where = ['id = ? AND penguin_id = ? AND walking = 0', puffle, client['room'].owner], limit = 1)
        if puffle is None:
            returnValue(None)

        client['room'].send('pm', puffle, x, y)
        client.engine.redis.server.hmset("puffle:{}".format(puffle), {'x' : x, 'y' : y})

@PacketEventHandler.onXT('s', 'p#pb', WORLD_SERVER)
def handlePuffleBath(client, puffle):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    if puffle is None:
        return

    max_rest = int(client.engine.puffleCrumbs.defautPuffles[int(puffle.type)][2])

    puffle.rest = (puffle.rest * max_rest + 5)/max_rest * 100
    if puffle.rest > 100:
        puffle.rest = max_rest

    puffle.clean = int(client.engine.puffleCrumbs.defautPuffles[int(puffle.type)][0])
    puffle.save()

    client['room'].send('pb', client['id'], client['coins'], puffle, 100)

@PacketEventHandler.onXT('s', 'p#pp', WORLD_SERVER)
def handlePufflePlay(client, puffle, sendPacket = True):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    if puffle is None:
        return

    health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[int(puffle.type)])

    if puffle.rest < 10 or puffle.clean < 10 or puffle.food < 10:
        return

    rx = choice(range(10, rest-10))
    cx = choice(range(0, health - 10))
    fx = choice(range(10, hunger))

    PX = choice(range(10, 100))

    puffle.rest = min(rest, int(puffle.rest)*rest - rx)/rest * 100
    puffle.clean = min(health, int(puffle.clean)*health - cx)/health * 100
    puffle.food = min(hunger, int(puffle.food)*hunger - fx)/hunger * 100
    puffle.play = min(100, int(puffle.play) + PX)

    puffle.save()

    client['room'].send('pp', client['id'], puffle, 27) if sendPacket else None #TODO: Play type

    return puffle

@PacketEventHandler.onXT('s', 'p#pr', WORLD_SERVER)
def handlePuffleRest(client, puffle, sendPacket = True):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    if puffle is None:
        return

    health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[int(puffle.type)])

    if puffle.rest < 10 or puffle.clean < 10 or puffle.food < 10:
        return

    cx = choice(range(0, health - 10))
    fx = choice(range(10, 30))


    puffle.rest = 100
    puffle.clean = min(health, int(puffle.clean)*health - cx) / health * 100
    puffle.food = min(hunger, int(puffle.food)*hunger - fx) / hunger * 100
    puffle.play = max(0, int(puffle.play) - 10)

    puffle.save()
    print puffle.clean, puffle.food, puffle.play
    client['room'].send('pr', client['id'], puffle) if sendPacket else None

    return puffle

@PacketEventHandler.onXT('s', 'p#pf', WORLD_SERVER)
def handlePuffleFeed(client, puffle):
    pass

@PacketEventHandler.onXT('s', 'p#pcid', WORLD_SERVER)
def handlePuffleCareItemDelivered(client, puffle, cid):
    puffleById = {i.id: i for i in client['data'].puffles}
    puffle = puffleById[puffle] if puffle in puffleById else None

    if puffle is None:
        return

    _type_ = int(puffle.type)
    if _type_ > 9:
        _type_ = 0

    health, hunger, rest = map(int, client.engine.puffleCrumbs.defautPuffles[_type_])
    if cid not in client.engine.puffleCrumbs.puffleItems:
        return client.send('e', 402)

    item_details = client.engine.puffleCrumbs.puffleItems[cid]

    only_purchase = bool(item_details['only_purchase'])
    is_member = bool(int(item_details['is_member_only']))

    if is_member and not client['member']:
        return

    careItemsById = {i.id: i for i in client['data'].careItems}

    if only_purchase:
        item = careItemsById[cid] if cid in careItemsById else None

        if item is None:
            return

        available_quantity = item.quantity

        if available_quantity < 1:
            return

    is_food = item_details['consumption'] != 'none'
    if is_food:
        client['room'].send('carestationmenuchoice', client['id'], puffle.id)

    if cid == 126:
        client['room'].send('oberry', client['id'], puffle.id)
        puffle.state = 1

    fx, rx, px, cx = map(int, [item_details['effect'][k] for k in ['food', 'rest', 'play', 'clean'] ])
    puffle.food = min(hunger, puffle.food*hunger + fx)/hunger * 100
    puffle.clean = min(health, puffle.clean*health + cx)/health * 100
    puffle.rest = min(rest, puffle.rest*rest + rx)/rest * 100
    puffle.play = min(100, puffle.play + px)

    puffle.save()

    client['room'].send('pcid', client['id'],
                        '|'.join(map(str, [puffle.id, puffle.food, puffle.play, puffle.rest, puffle.clean,
                                           int(all(x == 100 for x in [puffle.food,
                                                                      puffle.clean, puffle.rest, puffle.play]))])))
