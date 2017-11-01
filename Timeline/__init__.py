'''
Timeline base classes defined in here
'''

from Timeline.Utils.Crumbs.Items import Item

from twisted.internet.defer import inlineCallbacks
from collections import deque

import time
from math import ceil

class Username(str):
    def __new__(self, u, c):
        return super(Username, self).__new__(self, u)
    
    def __init__(self, username, client):
        self.u = username
        self.c = client
        
    @property
    def username(self):
        return self.u
    
    @property 
    def name(self):
        return self.u 
    
    @property 
    def value(self):
        return self.u

 
class Password (str):
    def __new__(self, p, c):
        return super(Password, self).__new__(self, p.upper())
        
    def __init__(self, p, c):
        self.p = p
        self.c = c
    
    @property
    def value(self):
        return self.p
        
class Nickname(str):
    def __new__(self, n, c):
        return super(Nickname, self).__new__(self, n)
    
    def __init__(self, n, c):
        self.n = n
        self.c = c

    def __str__(self):
        return self.n

    def __repr__(self):
        return self.n
    
    @property
    def nickname(self):
        return self.n 
    
    @nickname.setter
    def nickname(self, n):
        if self.c.db_nicknameUpdate(n):
            self.n = n
            
    @property
    def value(self):
        return self.n 
        
    @value.setter
 
    @inlineCallbacks
    def value(self, n):
        x = yield self.c.db_nicknameUpdate(n)
        
        if x:
            self.n = n

    def value(self, n):
        if self.c.db_nicknameUpdate(n):
            self.n = n

class Membership(int):

    def __new__(self, d, c):
        x = time.time() < time.mktime(d.timetuple())
        return super(Membership, self).__new__(self, x)

    def __init__(self, d, c):
        self.d = time.mktime(d.timetuple())
        self.c = c

    def __repr__(self):
        if time.time() > self.d:
            return 0

        return ceil((self.d - time.time())/(60*24.0))

    def __str__(self):
        return str(self.__repr__())

    def __int__(self):
        return self.__repr__()

# TODO : Attach this to redis server and implement cache
class Cache(object):
    def __init__(self, client):
        self.playerWidget = ''
        self.mapCategory = ''
        self.NX = ''
        self.igloo = ''
        self.GAS = ''

class Age(object):
    def __init__(self, a, c):
        self.age = time.mktime(a.timetuple())
        self.c = c

    def __repr__(self):
        return int(ceil((time.time() - self.age)/(60*24.0)))

    def __str__(self):
        return str(self.__repr__())

    def __int__(self):
        return self.__repr__()

class Coins(object):

    def __repr__(self):
        return self.coins

    def __str__(self):
        return str(self.coins)

    def __int__(self):
        return self.coins

    def __add__(self, c):
        a = Coins(self.coins)
        a += c
        return a

    def __iadd__(self, c):
        if self.coins + c < 1:
            return self # dont!

        self.coins += c
        self.__update()
        return self

    def __sub__(self, c):
        return self + (-c)

    def __isub__(self, c):
        self += -c
        return self

    def __init__(self, co, c):
        self.coins = co
        self.c = c

    def __update(self):
        if self.c == None:
            return

        self.c.dbpenguin.coins = self.coins
        self.c.dbpenguin.save()
        

class Inventory(list):

    def __init__(self, penguin, *items):
        super(Inventory, self).__init__()

        self.penguin = penguin

        self += items

    def parseFromString(self, string, delimiter = '%'):
        if string == None or string == '':
            return

        items = string.split(delimiter)
        self += items

    def __str__(self):
        return '%'.join(str(i.id) for i in self)

    def __addItem(self, item):
        if self.penguin is None:
            return

        self.dbpenguin.inventory += '%{}'.format(item)
        self.dbpenguin.save()

    def itemsByType(self, _type):
        if issubclass(_type, Item):
            _type = _type.type

        items = list()
        for item in self:
            if item.type == _type:
                items.append(item)

        return Inventory(None, *items)

    def __contains__(self, item):
        if isinstance(item, int):
            return self.hasItem(item)

        elif isinstance(item, Item):
            return self.hasItem(item.id)

        elif isinstance(item, str):
            try:
                i = int(item)
                return self.hasItem(i)
            except:
                for i in self:
                    if i.__name__.lower() == item.lower().strip():
                        return True

        return False

    def hasType(self, _t):
        for item in self:
            if item.type == _t:
                return True

        return False

    def hasItem(self, _id):
        for item in self:
            if item.id == _id:
                return True

        return False

    def append(self, item):
        if self.penguin is None:
            return super(Inventory, self).append(item)
            
        if isinstance(item, Item):
            if item.is_bait and not self.penguin.penguin.isModerator:
                raise Exception("Penguin {} using a bait item!".format(self.penguin.getPortableName()))

        elif isinstance(item, int):
            item = self.penguin.engine.itemCrumbs[item]
            if not item:
                return
        elif isinstance(item, str):
            try:
                item = int(item)
                self.append(item)
            except:
                item = str(item)
                item = self.penguin.engine.itemCrumbs[item]
                if item == False:
                    return

                self += item
            finally:
                return

        if item in self:
            return

        super(Inventory, self).append(item)
        self.__addItem(item)

    def insert(self, index, item):
        if isinstance(item, Item):
            super(Inventory, self).insert(index, item)

    def __add__(self, items):
        inv = Inventory(None, *self)
        inv += items

        return inv

    def __iadd__(self, items):
        for item in items:
            self.append(item)

        return self