from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER, SERVER_ONLY_STAMP_GROUP
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import Penguin, StampCover, Coin, Stamp

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'st#gsbcd', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'st#gsbcd', WORLD_SERVER)
@inlineCallbacks
def handleGetSBCoverDetails(client, _id):
    peng = (yield Penguin.find(_id)) if _id != client['id'] else client.dbpenguin
    if peng is None:
        returnValue(client.send('gsbcd', '', '', '', '', '', ''))

    colourID, highlightID, patternID, claspIconArtID = peng.cover_color, peng.cover_highlight, peng.cover_pattern, \
                                                       peng.cover_icon

    pengCoverItems = yield peng.stampCovers.get()
    rest = map(lambda x: '{i.type}|{i.stamp}|{i.x}|{i.y}|{i.rotation}|{i.depth}'.format(i=x), pengCoverItems)

    client.send('gsbcd', colourID, highlightID, patternID, claspIconArtID, *rest)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'st#gps', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'st#gps', WORLD_SERVER)
@inlineCallbacks
def handleGetPlayerStamps(client, _id):
    peng_stamps = (yield ((yield Penguin.find(_id))).stamps.get()) if _id != client['id'] else client['data'].stamps
    stamps = [k.stamp for k in peng_stamps]

    client.send('gps', _id, *stamps)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'st#gmres', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'st#gmres', WORLD_SERVER, p_r = False)
def handleGetRecentStamps(client, data):
    client.send('gmres', '|'.join(map(str, client['recentStamps'])))
    client.penguin.recentStamps = list()

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'st#ssbcd', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'st#ssbcd', WORLD_SERVER)
@inlineCallbacks
def handleSBCoverUpdate(client, color, highlight, pattern, icon, stamps):
    coverCrumb = client.engine.stampCrumbs.cover

    if not client['member']:
        returnValue(client.send('e', 999))

    if not color in coverCrumb['colors'] or not highlight in coverCrumb['highlights'] or not pattern in coverCrumb['patterns'] or not icon in coverCrumb['icons']:
        returnValue(None)

    stamps_used = list()
    stamps_earned = [i.stamp for i in client['data'].stamps]

    for stamp in stamps:
        item_type, item_id, x, y, rotation, depth = stamp
        # check for item_type: currently not sure of exact values it can hold

        # check if item is a stamp
        stamp = client.engine.stampCrumbs[item_id]
        if stamp is None:
            # check if it's a pin and in inventory
            item = client.engine.itemCrumbs[item_id]
            if item is None:
                returnValue(None)  # doesn't exists at all!

            if not(item.type == 8 and client['RefreshHandler'].inInventory(int(item))): #pin
                returnValue(None)

            stamp = item
        else:
            # check for stamp earned?
            if int(stamp) not in stamps_earned:
                returnValue(None)

        if item_id in stamps_used:
            returnValue(None)  # oops!

        stamps_used.append(item_id)

    yield StampCover.deleteAll(where=['penguin_id=?', client['id']])
    client.dbpenguin.cover_color, client.dbpenguin.cover_highlight, client.dbpenguin.cover_pattern, client.dbpenguin.cover_icon = color, highlight, pattern, icon
    client.dbpenguin.save()

    stampCovers = [StampCover(penguin_id=client['id'], type=x[0], stamp=x[1], x=x[2], y=x[3], rotation=x[4], depth=x[5])
                   for x in stamps]

    [(yield x.save()) for x in stampCovers]

    client.send('ssbcd', 'success')

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'st#sse', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'st#sse', WORLD_SERVER)
@inlineCallbacks
def handleStampEarned(client, _id, fromServer = False):
    stamp = client.engine.stampCrumbs[_id]
    if stamp is None:
        return

    if stamp.group in SERVER_ONLY_STAMP_GROUP and not fromServer:
        client.engine.log("warn", client['username'], "trying to manipulate Stamp System.")
        # ban?
        return

    stamps = [x.stamp for x in client['data'].stamps]

    if int(stamp) in stamps:
        return # lol

    #You earned a stamp, earn a penny now B-)
    client['coins'] += 1
    yield Coin(penguin_id=client['id'], transaction=1,
               comment="Earned money by earning stamp. Stamp: {}".format(stamp)).save()
    yield Stamp(penguin_id=client['id'], stamp=int(stamp)).save()

    client['recentStamps'].append(stamp)

'''
Handler to award user stamp, if he's in same room as a mascot. 
'''
@GeneralEvent.on("mascot-joined-room")
def handleAwardMascotStamp(room, mascot_name, penguins):
    availableMascotStamps = room.roomHandler.engine.stampCrumbs.getStampsByGroup(6)
    mascotStamps = {str(stamp.name).strip():stamp.id for stamp in availableMascotStamps}
    mascotToSearch = str(mascot_name).strip()

    if mascotToSearch in mascotStamps:
        stampId = mascotStamps[mascotToSearch]
        [handleStampEarned(client, stampId, True) for client in penguins]