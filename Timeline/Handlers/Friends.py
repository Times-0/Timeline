from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import Penguin, Request, Friend

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import sample
import json

@GeneralEvent.on('onClientDisconnect')
def handleStopFriendLoopReflush(client):
    friends = list(client['data'].friends) # friends db objects

    for friend in friends:
        friend = client.engine.getPenguinById(friend.id)
        friend.send('fo', '{}|0'.format(client['swid'])) if friend is not None else 0


@PacketEventHandler.onXT('s', 'u#bf', WORLD_SERVER, p_r=False)
@PacketEventHandler.onXT_AS2('s', 'u#bf', WORLD_SERVER, p_r=False)
def handleGetPlayerLocation(client, data):
    client.send('bf', '0', '0')

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#n', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#n', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleNewFriendRequest(client, data):
    swid = data[2][0]

    requested = yield Request.count(where=['penguin_swid = ? AND requested_by = ?', swid, client['swid']])
    requestPending = yield Request.find(where=['penguin_swid=? and requested_by=?', client['swid'], swid])

    if not requested and not requestPending:
        peng = yield Penguin.find(where=['swid=?', swid], limit=1)
        if peng is None:
            return

        (yield Request(penguin_id=peng.id, penguin_swid=swid, requested_by=client['swid']).save()) if not requested else None

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#s', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#s', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleSearchPenguin(client, data):
    searchQuery = data[2][0].strip()
    searchResults = []

    results = yield Penguin.find(where = ['nickname like ?', '%{}%'.format(searchQuery)])

    no_space_query = searchQuery.replace(' ', '')
    if not no_space_query.isalnum():
        searchResults.append({'msg' : 'The search query must contain only alphabets, numbers or a space.', 'nickname':
            'Search Moderator'})

    if len(searchQuery) < 4:
        searchResults.append({'msg' : 'The search query must be atleast 4 characters long.', 'nickname':
            'Search Moderator'})

    if len(searchResults) > 0:
        returnValue(client.send('fs', json.dumps(searchResults)))

    for r in results:
        if r.swid == client['swid'] or client['RefreshHandler'].is_friend(r.swid):
            continue

        a = {'nickname' : r.nickname}
        if hasattr(r, 'search_msg') and r.search_msg is not None and r.search_msg.strip() != '':
            a['msg'] = r.search_msg
        else:
            a['swid'] = r.swid

        searchResults.append(a)

    if len(searchResults) < 1:
        searchResults.append({'msg' : 'Your query yield no result. Search for some other penguin.', 'nickname':
            'Search Moderator'})

    client.send('fs', json.dumps(searchResults))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#bf', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#bf', WORLD_SERVER, p_r = False)
def handleChangeBFFStatus(client, data):
    swid = data[2][0]
    isBFF = int(data[2][1])

    friends = client['data'].getFriends()
    if swid in friends:
        friend = friends[swid]
        friend.bff = isBFF
        friend.save()

        client.send('fbf', swid, isBFF)

'''
AS2 and AS3 Compatibility
'''
@PacketEventHandler.onXT('s', 'f#a', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT('s', 'f#r', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#a', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#r', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleAcceptOrRejectFriendRequest(client, data):
    accepted = data[1][-1] == 'a'
    swid = data[2][0]

    requested = yield client.dbpenguin.requests.get(where=['requested_by = ?', swid]
                                                   , limit=1)
    if not requested:
        return

    requested.delete()
    if not accepted:
        return

    friend = yield Penguin.find(where=['swid = ?', swid], limit=1)

    yield Friend(penguin_id=friend.id, penguin_swid=friend.swid, friend=client['swid']).save()
    yield Friend(penguin_id=client['id'], penguin_swid = client['swid'], friend = swid).save()

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'f#rf', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'f#rf', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleRemoveFriend(client, data):
    swid = data[2][0]

    friend = yield Friend.find(where=['penguin_swid = ? AND friend = ?', swid, client['swid']], limit=1)
    me = yield Friend.find(where=['penguin_swid = ? AND friend = ?', client['swid'], swid], limit=1)

    friend.delete() if friend is not None else 0
    me.delete() if me is not None else 0

