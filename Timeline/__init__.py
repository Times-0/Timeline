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
        self.n = str(n).title()
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
        if (yield self.c.db_nicknameUpdate(n)):
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

class EPFAgent(object):
    def __init__(self, epf, point, client):
        self.e = bool(epf)
        self.p, self.t = map(int, point.split('%'))
        self.c = client

    def __repr__(self):
        return "EPF:{}<{},{}>".format(self.e, self.p, self.t)

    def __int__(self):
        return self.p

    def __bool__(self):
        return self.e

    def __str__(self):
        return "%".join(map(str, [self.e, self.p, self.t]))

    __nonzero__ = __bool__

class Membership(object):

    def __new__(self, d, c):
        x = time.time() < time.mktime(d.timetuple())
        return super(Membership, self).__new__(self, x)

    def __init__(self, d, c):
        self.d = time.mktime(d.timetuple())
        self.c = c

        self.rank = int(bool(self))
        months = int(int(self) * 0.03285) * int(bool(self))
        if months > 0:
            if months > 24:
                self.rank = 5
            else:
                self.rank = int(ceil(months / 6.0))

    def __repr__(self):
        if time.time() > self.d:
            return 0
            
        return int(ceil((self.d - time.time())/(60*60*24.0)))

    def __str__(self):
        return str(self.__repr__())

    def __int__(self):
        return self.__repr__()

    def __bool__(self):
        return self.__repr__() > 0

    __nonzero__ = __bool__

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
        self.age = int(time.mktime(a.timetuple()))
        self.c = c

    def __repr__(self):
        return int(ceil((time.time() - self.age)/(60*60*24.0)))

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
        return int(self.coins)

    def __add__(self, c):
        a = Coins(self.coins, None)
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
        self.coins = int(co)
        self.c = c

    def __update(self):
        if self.c == None:
            return

        self.c.dbpenguin.coins = self.coins
        self.c.dbpenguin.save()
        

class Inventory(list):

    _extend = True

    def __init__(self, penguin, *items):
        super(Inventory, self).__init__()

        self.penguin = penguin
        for item in items:
            self.append(item, False)

    def parseFromString(self, string, delimiter = '%'):
        if string == None or string == '':
            return

        items = str(string).split(delimiter)
        for i in items:
            self.append(i, False)

    def __str__(self):
        return '%'.join(map(str, self))

    def _addItem_(self, item, u = True):
        if self.penguin is None or not u:
            return

        self.penguin.dbpenguin.inventory = '%'.join(map(str, self))

        self.penguin.dbpenguin.save()

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
        elif isinstance(item, list):
            for i in item:
                if not i in self:
                    return False

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

    def append(self, item, u=True):
        if self.penguin is None:
            return super(Inventory, self).append(item)

        if not isinstance(item, Item):
            if isinstance(item, int):
                item = self.penguin.engine.itemCrumbs[item]
                if item is False:
                    return
                return self.append(item, u)
            elif isinstance(item, str):
                try:
                    item = int(item)
                    self.append(item, u)
                except Exception, e:
                    items = self.penguin.engine.itemCrumbs[item]
                    if items is False:
                        return

                    self.append(items, u)

                return
            else:
                return

        if item in self:
            return

        super(Inventory, self).append(item)
        self._addItem_(item, u)

    def insert(self, index, item):
        if isinstance(item, Item):
            super(Inventory, self).insert(index, item)

    def __add__(self, items):
        inv = Inventory(None, *self)
        inv += items

        return inv

    def __iadd__(self, items):
        if isinstance(items, list):
            for item in items:
                self.append(item)
        else:
            self.append(items)

        return self