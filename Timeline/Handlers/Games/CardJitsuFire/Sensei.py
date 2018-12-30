from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Server.Room import Game, Place, Multiplayer
from Timeline.Server.Penguin import Penguin
from Timeline.Handlers.Games.CardJitsuFire import CardJitsuGame

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time
from random import choice, shuffle, sample, randint

logger = logging.getLogger(TIMELINE_LOGGER)


class CardJitsuFireSenseiGame(CardJitsuGame):

    def play(self, client, param, tab = -1):
        gameStatus = super(CardJitsuFireSenseiGame, self).play(client, param, tab)
        if param[0] == 'ir':
            super(CardJitsuFireSenseiGame, self).play(client, ['ir'])

            if self.tabPlayer == self.Playing[0]:  # sensei
                self.checkGameStatus()

        if param[0] == 'cc' and gameStatus:
            self.checkBattleStatus(True)

    def pickSenseiCard(self, canWin, card, e):
        sfw = {'s': 'f', 'f': 'w', 'w': 's'}
        pickedElement = e
        deathElement = sfw[pickedElement]
        pickedCard = None
        if not canWin:
            for c in card:
                if c.element == deathElement:
                    pickedCard = c
                    break

        if pickedCard is None:
            pickedCard = choice(card)

        return pickedCard

    def checkBattleStatus(self, senseiOnly = False):
        if not senseiOnly:
            return super(CardJitsuFireSenseiGame, self).checkBattleStatus()

        if self.tabMatch is None or not self.tabMatch.battleStarted or \
                len(self.tabMatch.battlers) < 1 or self.slotPlayer is not None:
            return

        match = self.tabMatch.symbol
        cards = [k for k in self.Playing[0].deck if k.element == match]
        isCJ = self.tabMatch.battle == 'be'

        opponentPicked = self.Playing[1]['picked']
        canWin = self.Playing[1]['ninjaHandler'].ninja.fire > 4
        if isCJ:
            self.play(self.Playing[0], ['cc', self.Playing[0].deck.index(self.pickSenseiCard(canWin, cards, opponentPicked.element))])
        else:
            card = self.Playing[0].deck[0]
            for c in cards:
                if c.value > card.value:
                    card = c

            self.play(self.Playing[0], ['cc', self.Playing[0].deck.index(card)])