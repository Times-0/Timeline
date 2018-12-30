from Timeline.Server.Constants import TIMELINE_LOGGER, AVATARS
from twisted.internet.defer import Deferred

from collections import deque
import logging
import json
import os, sys

class AvatarHandler(object):
    def __init__(self, engine, package='configs/crumbs/mascots.json'):
        self.engine = engine
        self.logger = logging.getLogger(TIMELINE_LOGGER)
        self.package = package

        self.avatars = deque()
        self.setup()

    def setup(self):
        self.avatars.clear()

        if not os.path.exists(self.package):
            self.log("error", "mascots.json not found in path :", self.package)
            sys.exit()  # OOps!

        with open(self.package, 'r') as file:
            try:
                crumbs = json.loads(file.read())
                self.avatars = deque(crumbs.keys())
                
                [self.avatars.append(i) for i in AVATARS]

            except Exception, e:
                self.log("error", "Error parsing JSON. E:", e)
                sys.exit()

        self.log('info', "Loaded", len(self.avatars), "Avatar(s)")

    def __getitem__(self, key):
        key = int(key)
        return key in self.avatars

    def log(self, l, *a):
        self.engine.log(l, '[Crumbs::Avatar]', *a)

