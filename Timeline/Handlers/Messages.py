from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Database.DB import Penguin

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'u#sma', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'u#sma', WORLD_SERVER)
def SendMascotMessageRule(data):
    return [[int(data[2][0])], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'u#sma', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'u#sma', WORLD_SERVER)
def handleSendMessage(client, _id):
    client['room'].send('sma', client['id'], _id) if client['mascot_mode'] else None

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.XTPacketRule('s', 'm#sm', WORLD_SERVER)
@PacketEventHandler.XTPacketRule_AS2('s', 'm#sm', WORLD_SERVER)
def SendMessageRule(data):
    return [[int(data[2][0]), str(data[2][1])], {}]

'''
AS2 and AS3 Compatible
'''
@PacketEventHandler.onXT('s', 'm#sm', WORLD_SERVER)
@PacketEventHandler.onXT_AS2('s', 'm#sm', WORLD_SERVER)
def handleSendMessage(client, _id, message):
    if not client['id'] == _id:
        return

    message = message.strip(' ').replace('|', '\\|')

    GeneralEvent.call('before-message', client, message)

    if client['muted']:
        GeneralEvent.call('after-message-muted', client, message)
        return

    if client['stealth_mode'] or client['mascot_mode']:
        return

    toxic = Toxicity(message)
    if toxic > 60:
        # wow toxic...
        if toxic > 90:
            # he's a racist, ban him
            GeneralEvent('ban-player', client, 0, 'Rude. Toxicity [{}] message: {}'.format(toxic, message), type=3, ban_type=610)
        elif toxic > 80:
            # Kick'em 
            GeneralEvent('kick-player', client, 'Rude. Toxicity [{}] message: {}'.format(toxic, message))
        else:
            GeneralEvent('mute-player', client, 'Rude. Toxicity [{}] message: {}'.format(toxic, message))

        return


    client['room'].send('sm', _id, message)

    GeneralEvent.call('after-message', client, message)

'''
Uses Google' Perspective API to check Toxicity of a text.
Visit: https://github.com/conversationai/perspectiveapi/blob/master/quickstart.md
and get your Perspective API key.
'''
PERSPECTIVE_API_KEY = 'AIzaSyD9XvjmhqsWlWR_5bhqeBWa6Eo9kRgqdXU'  # for testing purpose only. Get yourself a key from google.
TOXICITY_FILTER = 60 # filter texts with toxicity more than 60%
API_ACTIVE = False
TOXIC_FILTER = 'SEVERE_TOXICITY' # use TOXICITY to filter any TOXIC message
try:
    from googleapiclient import discovery
    service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=PERSPECTIVE_API_KEY)
    API_ACTIVE = True
except Exception, e:
    logger.error("Unable to setup Prespective API. Error: %s", e)

def Toxicity(text):
    if not API_ACTIVE:
        logger.info("Perspective API not active. Message not filtered.")
        return 0

    try:
        analyze_request = {'comment': { 'text': text}, 'requestedAttributes': {TOXIC_FILTER: {}} }
        response = service.comments().analyze(body=analyze_request).execute()

        toxicity = round(100 * float(response['attributeScores'][TOXIC_FILTER]['summaryScore']['value']))
        
        logger.info("Perspective API: Message filtered. Toxicity [%s]. Message [%s]", str(toxicity), text)

        return toxicity

    except Exception, e:
        print 'Error,', e
        logger.info("Unable to filter message via Perspective API. Message not filtered.")

    return 0