'''
Timeline base classes defined in here
'''

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
    def value(self, n):
        if self.c.db_nicknameUpdate(n):
            self.n = n
