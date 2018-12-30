from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, EMOTES
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Color, Head, Face, Neck, Body, Hand, Feet, Pin, Photo, Award
from Timeline.Database.DB import Penguin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@PacketEventHandler.onXT('s', 'u#followpath', WORLD_SERVER)
def handlePlayerSliding(client, slide):
    client['room'].send('followpath', client['id'], slide)

@PacketEventHandler.onXT('s', 'u#pbi', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerById(client, _id):
    penguin = yield client.db_getPenguin('ID = ?', _id)
    if penguin is None:
        returnValue(0)

    client.send('pbi', penguin.swid, _id, penguin.nickname)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#sf', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#sf', WORLD_SERVER)
def handleSendFrame(client, frame):
    #TODO Check frame
    client.penguin.frame = frame
    client['room'].send('sf', client['id'], client['frame'])

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#sa', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#sa', WORLD_SERVER)
def handleSendAction(client, action):
    client['room'].send('sf', client['id'], action)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#se', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#se', WORLD_SERVER)
def handleSendEmote(client, emote):
    GeneralEvent('Handle-Emote', client, emote) if emote not in EMOTES \
        else client['room'].send('se', client['id'], emote)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#ss', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#ss', WORLD_SERVER)
def handleSendSafeMsg(client, safe):
    # really necessary to check?
    client['room'].send('ss', client['id'], safe)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#gp', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#gp', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayer(client, _id):
    penguin = yield client.db_getPenguin('ID = ?', _id)
    if penguin is None:
        returnValue(0)

    avatar = yield penguin.avatar.get()

    client.send('gp', '|'.join(map(str, [_id, penguin.nickname, 45, avatar.color, avatar.head, avatar.face,
                                         avatar.neck, avatar.body, avatar.hand, avatar.feet, avatar.pin,
                                         avatar.photo])))

@PacketEventHandler.onXT('s', 'u#pbs', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetPlayerBySWID(client, data):
    swid = str(data[2][0])
    penguin = yield client.db_getPenguin('swid = ?', swid)
    if penguin is None:
        returnValue(0)

    client.send('pbs', penguin.username, penguin.id)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#sp', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#sp', WORLD_SERVER)
def handleSendCoordinates(client, x, y):
    client.penguin.x, client.penguin.y = x, y
    client['room'].send('sp', client['id'], x, y)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#sb', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#sb', WORLD_SERVER)
def handleSnowBall(client, x, y):
    client['room'].send('sb', client['id'], x, y)

@PacketEventHandler.onXT('s', 'u#bf', WORLD_SERVER)
def handle(client, _id):
    # check if id is friend
    # check if id is online
    # check if id is moderator
    # and more...
    pass

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#pbsu', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#pbsu', WORLD_SERVER)
@inlineCallbacks
def handleGetUsernames(client, swid):
    usernames = list()
    for s in swid:
        user = yield Penguin.find(where = ['swid = ?', s], limit = 1)
        if user is None:
            usernames.append('')
        else:
            usernames.append(str(user.nickname))

    client.send('pbsu', ','.join(usernames))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#h', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'u#h', WORLD_SERVER, p_r = False)
def handleHeartBeat(client, data):
    client.send('h', 'pong')

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upc', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upc', WORLD_SERVER)
def handleUpdateColor(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or not item:
        return

    if item.type is not Color.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.color = int(item)
    client['data'].avatar.save()

    client['room'].send('upc', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#uph', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#uph', WORLD_SERVER)
def handleUpdateHead(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.head = 0
        client['data'].avatar.save()

        return client['room'].send('uph', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or not item:
        return

    if item.type is not Head.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.head = int(item)
    client['data'].avatar.save()

    client['room'].send('uph', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upf', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upf', WORLD_SERVER)
def handleUpdateFace(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.face = int(0)
        client['data'].avatar.save()

        return client['room'].send('upf', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Face.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.face = int(item)
    client['data'].avatar.save()

    client['room'].send('upf', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upn', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upn', WORLD_SERVER)
def handleUpdateNeck(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.neck = int(0)
        client['data'].avatar.save()

        return client['room'].send('upn', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Neck.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.neck = int(item)
    client['data'].avatar.save()

    client['room'].send('upn', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upb', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upb', WORLD_SERVER)
def handleUpdateBody(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.body = int(0)
        client['data'].avatar.save()

        return client['room'].send('upb', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Body.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.body = int(item)
    client['data'].avatar.save()

    client['room'].send('upb', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upa', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upa', WORLD_SERVER)
def handleUpdateHand(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.hand = int(0)
        client['data'].avatar.save()

        return client['room'].send('upa', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Hand.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.hand = int(item)
    client['data'].avatar.save()

    client['room'].send('upa', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upe', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upe', WORLD_SERVER)
def handleUpdateFeet(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.feet = int(0)
        client['data'].avatar.save()

        return client['room'].send('upe', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Feet.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.feet = int(item)
    client['data'].avatar.save()

    client['room'].send('upe', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upp', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upp', WORLD_SERVER)
def handleUpdatePhoto(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    print "Photo:", _id
    if _id == 0:
        client['data'].avatar.photo = int(0)
        client['data'].avatar.save()

        return client['room'].send('upp', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Photo.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.photo = int(item)
    client['data'].avatar.save()

    client['room'].send('upp', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 's#upl', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 's#upl', WORLD_SERVER)
def handleUpdateFlag(client, _id): # check if penguin room type is place too.. can he change clothes when he play? LOL!
    if _id == 0:
        client['data'].avatar.pin = int(0)
        client['data'].avatar.save()

        return client['room'].send('upl', int(client['id']), _id)

    item = client.engine.itemCrumbs[_id]
    if not client['RefreshHandler'].inInventory(_id) or item == False:
        return

    if item.type is not Pin.type:
        return # suspecius? Log it, probably?

    if item.is_member and not client['member']:
        return client.send('e', 999)

    if item.is_bait and not client['moderator']:
        return # raise issue, ban the player? :P

    if item.is_epf and not client['epf']:
        return # shit on him!

    client['data'].avatar.pin = int(item)
    client['data'].avatar.save()

    client['room'].send('upl', int(client['id']), int(item))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#gbffl', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'u#gbffl', WORLD_SERVER, p_r = False)
def handleGetBFFList(client, data):
    friends = [k.id for k in client['data'].friends if k.bff]

    client.send('gbffl', ','.join(friends))