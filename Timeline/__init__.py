'''
Timeline base classes defined in here
'''

 
from twisted.internet.defer import inlineCallbacks

class Username(str):
    def __new__(self, u, c):
        return super(Username, self).__new__(self, u)
    
=======
class Username(object):

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
    
=======
class Nickname(object):

    def __init__(self, n, c):
        self.n = n
        self.c = c
    
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
=======
    def value(self, n):
        if self.c.db_nicknameUpdate(n):
            self.n = n

