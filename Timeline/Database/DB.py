from Timeline.Server.Constants import TIMELINE_LOGGER

from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twistar.dbobject import DBObject

from collections import deque
import logging

class Penguin (DBObject):
    pass 

class Ban(DBObject):
    pass

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