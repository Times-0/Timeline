from Timeline.Server.Constants import TIMELINE_LOGGER

from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twistar.dbobject import DBObject
from twistar.registry import Registry

from collections import deque
import logging, time, json

class Penguin(DBObject):
    HASONE = ['avatar', 'currency', 'ninja']
    HASMANY = ['assets', 'bans', 'careItems', 'coins', 'friends', 'ignores', 'requests', 'inventories', 'mails', 'memberships',
               'musicTracks', 'puffles', 'stamps', 'stampCovers', 'igloos']

class Coin(DBObject):
    pass

class Igloo(DBObject):
    HASMANY = ['iglooFurnitures', 'iglooLikes']

    @inlineCallbacks
    def get_likes_count(self):
        likes = yield Registry.getConfig().execute("SELECT COALESCE(SUM(likes), 0) FROM igloo_likes where "
                                                   "igloo_id = %s" % (self.id))

        returnValue(likes[0][0])

    @inlineCallbacks
    def get_furnitures(self):
        furnitures = yield self.iglooFurnitures.get()

        returnValue(furnitures)

    @inlineCallbacks
    def get_furnitures_string(self):
        furnitures = yield self.get_furnitures()
        furn_data = map(lambda i: '|'.join(map(str, map(int, [i.furn_id, i.x, i.y, i.rotate, i.frame]))), furnitures)

        returnValue(','.join(furn_data))

    @inlineCallbacks
    def updateFurnitures(self, furnitures):
        yield self.refresh()
        yield IglooFurniture.deleteAll(where=['igloo_id = ?', self.id])

        furn = [IglooFurniture(igloo_id=self.id, furn_id=x[0], x=x[1], y=x[2], rotate=x[3], frame=x[4])
                for x in furnitures]
        [(yield i.save()) for i in furn]

        yield self.iglooFurnitures.set(furn)


class IglooFurniture(DBObject):
    pass


class IglooLike(DBObject):


    def get_time(self):
        return int(time.mktime(self.time.timetuple()))


class Avatar(DBObject):
    pass


class Currency(DBObject):
    pass


class Ninja(DBObject):
    pass


class Asset(DBObject):
    def getPurchasedTimestamp(self):
        return int(time.mktime(self.purchased.timetuple()))


class Ban(DBObject):

    def banned(self):
        return hours > 0

    def hours(self):
        expire = int(time.mktime(self.expire.timetuple()))
        hours = (expire - time.time()) / (60 * 60.0) if expire > time.time() else 0

        return hours


class CareItem(DBObject):
    pass


class Friend(DBObject):
    friend_id = -1


class Ignore(DBObject):
    pass


class Request(DBObject):
    pass


class Inventory(DBObject):
    pass


class Mail(DBObject):

    def get_sent_on(self):
        return int(time.mktime(self.sent_on.timetuple()))


class Membership(DBObject):
    pass


class MusicTrack(DBObject):
    shared = False

    def __len__(self):
        return self.length

    def __str__(self, withNotes = False):
        if not withNotes:
            return '|'.join(map(str, [self.id, self.name, int(self.shared), self.likes]))

        return '%'.join(map(str, [self.id, self.name, int(self.shared), self.notes, self.hash, self.likes]))

    def __int__(self):
        return self.id


class Puffle(DBObject):
    state = x = y = 0

    def __str__(self):
        # puffle id|type|sub_type|name|adoption|food|play|rest|clean|hat|x|y|is_walking
        return '|'.join(map(str, [int(self.id), int(self.type), self.subtype if int(self.subtype) != 0 else '',
                                  self.name, self.adopt(), int(self.food), int(self.play), int(self.rest),
                                  int(self.clean), int(self.hat), int(self.x), int(self.y), int(self.walking)]))

    def adopt(self):
        return int(time.mktime(self.adopted.timetuple()))

    def updatePuffleStats(self, engine):
        care_history = json.loads(self.lastcare)
        now = time.time()

        if care_history is None or len(care_history) < 1 or bool(int(self.backyard)) or self.walking:
            care_history['food'] = care_history['play'] = care_history['bath'] = now
            self.lastcare = json.dumps(care_history)
            self.save()

            return  # ULTIMATE PUFFLE <indefinite health and energy>

        last_fed = care_history['food']
        last_played = care_history['play']
        last_bathed = care_history['bath']

        food, play, clean = int(self.food), int(self.play), int(self.clean)

        puffleCrumb = engine.puffleCrumbs[self.subtype]
        max_food, max_play, max_clean = puffleCrumb.hunger, 100, puffleCrumb.health

        self.rest = 100  # It's in the igloo all this time?
        self.save()

        ''' It afterall is a poor creature to be taken care of.
        if not int(puffle.id) in self.penguin.engine.puffleCrumbs.defautPuffles:
            return # They aren't to be taken care of
        '''

        '''
        if remaining % < 10 : send a postcard blaming (hungry, dirty, or unhappy)
        if remaining % < 2 : move puffle to pet store, delete puffle, send a postcard, sue 1000 coins as penalty
        '''

        fed_percent = food - 5 * ((now - last_fed)/86400) # delta_food = -5% per day
        play_percent = play - 5 * ((now - last_played)/86400) # delta_play = -5% per day
        clean_percent = clean - 10 * ((now - last_bathed)/86400) # delta_clean = -10% per day

        total_percent = (fed_percent + play_percent + clean_percent) / 3.0

        if fed_percent < 3 or total_percent < 6:
            self.backyard = 1
            self.food = 100
            self.play = 100
            self.clean = 100
            self.save()

            return

        if fed_percent < 10:
            pid = self.penguin_id
            pname = self.name
            def sendMail(mail):
                if mail is not None:
                    sent = mail.sent_on
                    delta = (time.time() - sent)/3600/12
                    if delta < 1:
                        return

                Mail(penguin_id=pid, from_user=0, type=110, description=str(pname)).save()


            last_mail = Mail.find(where=['penguin_id = ? AND type = 110 AND description = ?', self.penguin_id, self.name], orderby='sent_on DESC', limit=1).addCallback(sendMail)

        self.food = fed_percent
        self.play = play_percent
        self.clean = clean_percent

        care_history['food'] = care_history['play'] = care_history['bath'] = now
        self.lastcare = json.dumps(care_history)

        self.save()


class Stamp(DBObject):

    def __int__(self):
        return int(self.stamp)


class StampCover(DBObject):
    pass


class EPFCom(DBObject):
    TABLENAME = 'epfcoms'
    
    def getTime(self):
        return int(time.mktime(self.time.timetuple()))

    def __str__(self):
        return '|'.join(map(str, [self.message, self.getTime(), self.mascot]))


class PenguinDB(object):
    """
    <Server.Penguin> will extend this to get db operations
    Syntax:
        def db_<FunctionName> (*a, **kwa): << must be deferred and mustreturn a defer
           > recommended to use with inlineCallbacks 
    """
    
    def __init__(self):
        self.logger = logging.getLogger(TIMELINE_LOGGER)
        
        self.dbpenguin = None
    
    @inlineCallbacks
    def db_init(self):

        if self.dbpenguin is None:
            column, value = 'username', self.penguin.username
            if not self.penguin.id is None:
                column, value = 'ID', self.penguin.id
            elif not self.penguin.swid is None:
                column, value = 'swid', self.penguin.swid

            self.dbpenguin = yield Penguin.find(where = ['%s = ?' % column, value], limit = 1)
            
            if self.dbpenguin is None:
                raise Exception("[TE201] Penguin not found with {1} - {0}".format(value, column))
        
        returnValue(True)
    
    @inlineCallbacks
    def db_nicknameUpdate(self, nick):
        p_nickname = self.dbpenguin.nickname
        self.dbpenguin.nickname = nick
        
        done = self.dbpenguin.save()
        if len(done.errors) > 0:
            self.dbpenguin.nickname = p_nickname
            
            for error in done.errors:
                self.log('error', "[TE200] MySQL update nickname failed. Error :", error)
                
            returnValue(False)
        else:
            returnValue(True)
    
    @inlineCallbacks 
    def db_penguinExists(self, criteria = 'ID', value = None):
        exists = yield Penguin.exists(["`%s` = ?" % criteria, value])
        
        returnValue(exists)
        
    @inlineCallbacks 
    def db_getPenguin(self, criteria, *values):
        wh = [criteria] + list(values)
        
        p = yield Penguin.find(where = wh, limit = 1)
        
        returnValue(p)
        
    @inlineCallbacks 
    def db_refresh(self):
        yield self.dbpenguin.refresh()
