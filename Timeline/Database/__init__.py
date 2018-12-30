"""
Timeline's DB System
"""
from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Database.DB import Penguin

from collections import deque
import logging


from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbconfig.mysql import ReconnectingMySQLConnectionPool

from Timeline.Database.DB import Penguin, Igloo, Avatar, Currency, Ninja, Asset, Ban, CareItem, Friend, Request, \
    Ignore, Inventory, Mail, Membership, MusicTrack, Puffle, Stamp, StampCover, IglooFurniture, IglooLike, Coin

class DBManagement(object):
    
    def __init__(self, user, passd, db):
        self.db_data = (user, db)
        self.logger = logging.getLogger(TIMELINE_LOGGER)
        self.conn = False
        
        if self.setupRegistry(passd):
            self.logger.info("MySQL Database pool setup successfully")
        else:
            self.logger.info("Unable to setup MySQL Pool")
        
    def setupRegistry(self, passd):
        user, db = self.db_data
        self.logger.info("Starting MySQL DB Pool... @{0}:{1}".format(*self.db_data))
        try:
            Registry.register(Penguin, Igloo, Avatar, Currency, Ninja, Asset, Ban, CareItem, Friend, Request, Ignore,
                              Inventory, Mail, Membership, MusicTrack, Puffle, Stamp, StampCover, Coin)
            Registry.register(Igloo, IglooFurniture, IglooLike)

            Registry.DBPOOL = ReconnectingMySQLConnectionPool('MySQLdb', user=user, passwd=passd, db=db, cp_reconnect=True)
            self.conn = True
    
        except Exception, e:
            self.logger.error("Unable to start MySQL Pool on given details. (E:{0})".format(e))
            self.conn = False
        
        return self.conn
        

def validateNickname(peng):
    peng.nickname = peng.nickname.strip()
    n = peng.nickname
    m = n.replace(' ', '')
    
    if len(n) > 20: 
        peng.errors.add('nickname', "Nickname should be less than 21 characters")
    
    if not m.isalnum():
        peng.errors.add('nickname', "Nickname should be alpha numeric")

def validateInventory(peng):
    peng.inventory = peng.inventory.strip('%')
        

Penguin.addValidator(validateNickname)