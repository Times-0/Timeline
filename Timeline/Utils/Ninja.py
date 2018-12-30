from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event
from Timeline.Utils.Events import GeneralEvent
from Timeline.Database.DB import Ninja

from twisted.internet.defer import inlineCallbacks, returnValue

from random import choice
from math import ceil
from collections import deque
import logging
import time

class NinjaHandler(object):

    items = [4025,4026,4027,4028,4029,4030,4031,4032,4033,104]
    powers = [[0], [2], [3], [4, 5], [6], [7, 8, 9], [10], [11, 12], [13, 14, 15], [16, 17, 18]]

    fire_items = [-1, 6025, 4120, 2013, 1086]

    def __init__(self, penguin):
        self.penguin = penguin
        self.logger = logging.getLogger(TIMELINE_LOGGER)

        self.cards = dict()
        self.matchesWon = dict() # against_id : won_or_not, ID = -1 for sensei
        self.wonMatchCount = 0
        self.progress = 0 # in percentage %

        self.elementalWins = {'f' : {'won': 0, 'progress': 0}}

        self.setup()

    @inlineCallbacks
    def setup(self):
        self.ninja = yield self.penguin.dbpenguin.ninja.get()

        if self.ninja is None:
            print self.penguin['id']
            self.ninja = Ninja(penguin_id = self.penguin['id'], cards = '', matches = '', belt = 0)
            yield self.ninja.save()
            yield self.ninja.refresh()

        self.setupCards()
        self.setupWonMatches()

    def setupWonMatches(self):
        matches = self.ninja.matches
        if matches == None or matches == '':
            self.ninja.matches = ''
            return self.ninja.save()

        won = matches.strip(',').split(',')
        for i in won:
            against, isWon = i.split('|')
            isWon = isWon == '1'
            self.matchesWon[against] = isWon

            self.wonMatchCount += isWon

        self.progress = 1.0*self.wonMatchCount / self.nOfWins(self.ninja.belt + 1) * 100 if self.ninja.belt < 9 else (50 if self.ninja.belt < 10 else 100)

        self.setElementalMatches()

    def setElementalMatches(self):
        f_matches = self.ninja.fire_matches
        if f_matches == None or f_matches == '':
            return

        self.elementalWins['f']['won'] = len(f_matches.split(','))
        self.elementalWins['f']['progress'] = (self.elementalWins['f']['won'] * 100.0 / (self.nOfWins(self.ninja.fire + 1) if self.ninja.fire != 4 else self.elementalWins['f']['won'] / 90.0)) if self.ninja.fire < 5 else 100

    def handleEarnedStamps(self, stampGroup = 38):
        stamps = self.penguin['recentStamps']
        g_stamps = self.penguin.engine.stampCrumbs.getStampsByGroup(stampGroup)
        e_stamps = list(set(self.penguin['stampHandler']).intersection(g_stamps))

        stamps = list(set(stamps).intersection(g_stamps))

        earned = len(e_stamps)
        total = len(g_stamps)

        self.penguin.send('cjsi', '|'.join(map(str, map(int, stamps))), earned, total, total)

    @inlineCallbacks
    def addFireWin(self, noOfPlayer):
        print 'won', self.penguin['nickname'], noOfPlayer
        self.ninja.fire_matches = "{},{}".format(self.ninja.fire_matches, noOfPlayer)

        self.elementalWins['f']['won'] += 1
        self.elementalWins['f']['progress'] = (self.elementalWins['f']['won'] * 100.0 / (
            self.nOfWins(self.ninja.fire + 1) if self.ninja.fire != 4 else self.elementalWins['f'][
                                                                               'won'] / 90.0)) if self.ninja.fire < 5 \
            else 100

        if self.elementalWins['f']['progress'] > 99 and self.ninja.fire < 4:
            self.ninja.fire = int(self.ninja.fire) + 1
            self.penguin.send('zm', 'nr', 'f', self.ninja.fire)

            [(yield self.penguin.addItem(i, 'Increase Fire Rank')) for i in self.fire_items[self.ninja.fire]]

        self.ninja.save()

    def promoteToBlackBelt(self):
        if self.ninja.belt > 9:
            return

        self.ninja.belt = 10
        self.penguin.send('cza', self.ninja.belt)
        self.penguin.addItem(104, 'Earned black belt.')

        eligiblePowers = sum(self.powers[:self.ninja.belt], [])
        eligibleCards = [k for k in self.penguin.engine.cardCrumbs.cards if k.power in eligiblePowers]
        for i in range(int(ceil(len(self.penguin.engine.cardCrumbs.cards) * 0.1))):
            randomCard = choice(eligibleCards)
            card_id = randomCard.id
            if card_id not in self.cards:
                self.cards[card_id] = [randomCard, 0]

            self.cards[card_id][1] += 1

        self.ninja.cards = '|'.join(map(lambda x: "{},{}".format(x, self.cards[x][1]), self.cards))

        yield self.ninja.save()

    def nOfWins(self, x):
        return round(-1.622372913*(10**-4) *(x**9) + 6.533381492*(10**-3) *(x**8) - 1.105542254*(10**-1) *(x**7) + 1.022742012 *(x**6) - 5.637499669 *(x**5) + 18.90474287 *(x**4) - 37.58260513 *(x**3) + 40.9564338 *(x**2) - 12.58127091 *(x**1)- 1.785941688*(10**-2))

    @inlineCallbacks
    def promoteNinja(self):
        maxBelt = self.ninja.belt
        belt = maxBelt + int(self.wonMatchCount >= self.nOfWins(maxBelt + 1))

        if belt > maxBelt and maxBelt < 10:
            self.ninja.belt = maxBelt + 1
            self.penguin.send('cza', self.ninja.belt)

            yield self.penguin.addItem(self.items[self.ninja.belt], 'Promoting ninja to: {}'.format(self.ninja.belt))
            self.penguin['RefreshHandler'].forceRefresh()

            # Give him some cards :P like 5 of them (1% of all cards)
            eligiblePowers = sum(self.powers[:self.ninja.belt], [])
            eligibleCards = [k for k in self.penguin.engine.cardCrumbs.cards if k.power in eligiblePowers]
            for i in range(int(ceil(len(self.penguin.engine.cardCrumbs.cards) * 0.1))):
                randomCard = choice(eligibleCards)
                card_id = randomCard.id
                if card_id not in self.cards:
                    self.cards[card_id] = [randomCard, 0]

                self.cards[card_id][1] += 1

            self.ninja.cards = '|'.join(map(lambda x: "{},{}".format(x, self.cards[x][1]), self.cards))

        self.progress = 1.0*self.wonMatchCount / self.nOfWins(self.ninja.belt + 1) * 100 if self.ninja.belt < 9 else (50 if self.ninja.belt < 10 else 100)
        yield self.ninja.save()

    @inlineCallbacks
    def addWin(self, against, isWon):
        isWon = bool(isWon)
        self.matchesWon[against] = isWon
        self.wonMatchCount += int(isWon)

        self.progress = 1.0*self.wonMatchCount / self.nOfWins(self.ninja.belt + 1) * 100 if self.ninja.belt < 9 else (50 if self.ninja.belt < 10 else 100)

        self.ninja.matches = "{},{}|{}".format(self.ninja.matches, against, int(isWon))
        yield self.ninja.save()

    def setupCards(self):
        cards = self.ninja.cards
        if cards == '' or cards == None:
            self.ninja.cards = '|'.join(map(lambda x: "{},1".format(x), [1, 6, 9, 14, 17, 20, 22, 23, 2673, 89, 81]))
            self.ninja.save()

        cards = self.ninja.cards.split('|')
        for c in cards:
            card_id, limit = map(int, c.split(","))
            card = self.penguin.engine.cardCrumbs[card_id]
            if card is None:
                continue

            self.cards[card_id] = [card, limit]