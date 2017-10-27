"""
Timeline's memory based redis databases' handler
"""

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
