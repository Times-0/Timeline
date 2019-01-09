from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Utils.Crumbs.Items import Pin, Award
from Timeline.Database.DB import Penguin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'l#mg', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'l#mg', WORLD_SERVER, p_r = False)
@inlineCallbacks
def handleGetMail(client, data):
    mails = client['data'].mails

    mailstr = []
    for mail in mails:
        nick = yield Penguin.find(mail.from_user)
        nick = nick.nickname if nick is not None else 'Timeline Team'

        mailstr.append('|'.join(map(str, [nick, int(mail.from_user), int(mail.type), mail.description, mail.get_sent_on(), int(mail.id), int(mail.opened)])))

    client.send('mg', *mailstr) if len(mailstr) > 0 else client.send('%xt%mg%-1%')

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'l#mst', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'l#mst', WORLD_SERVER, p_r = False)
def handleStartMail(client, data):
    GeneralEvent.call('mail-start', client)

    unread = len([k for k in client['data'].mails if not k.opened])
    client.send('mst', unread, len(client['data'].mails))

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'l#ms', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'l#ms', WORLD_SERVER)
@inlineCallbacks
def handleSendMail(client, to, _id):
    to_peng = yield Penguin.find(to)

    if to_peng is None :
        returnValue(client.send('ms', client['coins'], 0))

    client['RefreshHandler'].sendMail(to, _id)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'l#mc', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'l#mc', WORLD_SERVER, p_r = False)
def handleMaildRead(client, data):
    for mail in client['data'].mails:
        mail.opened = 1
        mail.save()

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'l#md', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'l#md', WORLD_SERVER)
def handleDeleteMail(client, _id):
    mail = [i for i in client['data'].mails if i.id == _id][0]
    mail.junk = 1
    mail.save()

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'l#mdp', WORLD_SERVER, p_r = False)
@PacketEventHandler.onXT_AS2('s', 'l#mdp', WORLD_SERVER, p_r = False)
def handleDeleteAllFromUser(client, data):
    for mail in client['data'].mails:
        mail.junk = 1
        mail.save()

    client['RefreshHandler'].forceRefresh()

