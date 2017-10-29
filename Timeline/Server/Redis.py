"""
Timeline's memory based redis databases' handler
"""

from Timeline.Server.Constants import LOGIN_SERVER, WORLD_SERVER



import txredisapi as redis
import json

from twisted.internet.defer import Deferred, inlineCallbacks, returnValue


class Redis(object):
    def __init__(self, engine):
        self.engine = engine
        self.server = None
        
        redis.Connection(host = '127.0.0.1', reconnect = True).addCallback(self.initPenguins)
        
    @inlineCallbacks
    def initPenguins(self, pool):
        self.server = pool
        
        self.log("info", "Setting redis data...")

        if self.engine.type == WORLD_SERVER:
            name = "server:{0}".format(self.engine.id)
            yield self.server.hmset(name, {
                'name' : self.engine.name,
                'max' : self.engine.maximum,
                'population' : 0
                
            })
            
            yield self.server.sadd("servers", self.engine.id)
        
        
        self.log("info", "Setup memcache data successful!")
    
    
    @inlineCallbacks     
    def getWorldServers(self):
        servers = yield self.server.smembers("servers")
        s = dict({})
        
        for sid in servers:
            s[sid] = yield self.server.hgetall("server:{0}".format(self.engine.id))
        
        returnValue(s)
        
    def log(self, k, *a):
        msg = ["(Redis)"] + list(a)
        self.engine.log(k, *msg)

        
        name = "server:{0}".format(self.engine.id)
        yield self.server.hmset(name, {
            'name' : self.engine.name,
            'max' : self.engine.maximum,
            'population' : 0
        })
        
        yield self.server.sadd("servers", self.engine.id)
        
        self.log("info", "Setup memcache data successful!")
    
        
    def getWorldServers(self):
        with open("crumbs/servers.json", 'r') as file:
            return json.loads(file.read())
        
    def log(self, k, *a):
        msg = ["(Redis)"] + list(a)
        self.engine.log(k, *msg)

