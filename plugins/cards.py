#!/usr/bin/env python2
from collections import OrderedDict
import json
import copy
import random

HAND_SIZE = 10
MIN_PLAYERS = 2
HISTORY_LEN = 100
MIN_PLAYERS = 2
JOIN_MSG = "Type %%join to join the game. Players: %s"
CARDS = {}
cards_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
   "plugins",
   "cards.json"
)

with open(cards_file) as f:
    CARDS = json.loads(f.read())

class Stage:
    setup = 0 # players can join in, pre-deal
    players = 1 # players pick
    czar = 2 # czar picks

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.hand = []
        self.selection = []
    def __str__(self):
        return self.name

class Game:
    
    def random_balanced_sets(self, deck):
        i = 0
        max_retries = 10
        if deck not in self.history:
            self.history[deck] = []
        while True:
            set_id = random.randint(0,len(self.cards[deck].keys())-1)
            set_name = tuple(self.cards[deck].keys())[set_id]
            card = random.choice(self.cards[deck][set_name]).encode('ascii','ignore')
            self.history[deck] = self.history[deck][-HISTORY_LEN:]
            if card not in self.history[deck] or i >= max_retries:
                self.history[deck] += [card]
                break
            i += 1
        return card
    
    def __init__(self):
        
        self.players = {}
        self.inited = False
        self.turn = -1 # who is czar?
        self.black = "" # current black card text
        self.black_blanks = 1
        self.czar = ""
        self.cards = CARDS
        self.rid = []
        self.history = {}
        self.random_alg = self.random_balanced_sets
        
        random.seed()

        self.stage = Stage.setup

    def poll(self):
        
        if self.stage == Stage.players:
            for p in self.players.values():
                if p.name != self.czar and len(p.selection) < self.black_blanks:
                    return # someone not ready
                
            # remove all the blank placeholder cards used to prevent IDs from changing during multiselection
            for p in self.players.values():
                p.hand = filter(lambda card: card, p.hand)
            
            self.rid = copy.copy([p for p in self.players.keys() if p != self.czar])
            random.shuffle(self.rid)
            for r in range(len(self.rid)):
                serv.broadcast('%s) %s' % (r+1, ', '.join(self.players[self.rid[r]].selection)))
            self.stage = Stage.czar

    def do_turn(self, ctx, serv, nick, dest, msg):
        # check and process player commands
        
        if not self.inited:
            return
        if self.stage == Stage.players:
            if nick in self.players.keys() and nick != self.czar:
                p = self.players[nick]
                if len(p.selection) < self.black_blanks:
                    try:
                        pick = p.hand[int(msg)-1]
                        if not pick:
                            serv.say(nick, 'You already picked that card. Pick a different one.')
                            return
                        p.selection += [pick]
                        p.hand[int(msg)-1] = ""
                    except ValueError, e:
                        return
                    except IndexError, e:
                        return
                    except:
                        return
                    
                    if len(p.selection) == self.black_blanks:
                        self.poll()
                    else:
                        serv.say(p.name, 'Pick next card (#%s): ' % (len(p.selection)+1))
        
        elif self.stage == Stage.czar:
            if nick == self.czar:
                p = None
                try:
                    p = self.players[self.rid[int(msg)-1]]
                except:
                    pass
                if not p:
                    return
                p.score += 1
                serv.broadcast("%s gains 1 point with: %s" % (p.name, ', '.join(p.selection)))
                self.next_round()

    def init(self, cmd, serv, nick, dest, msg):
        
        # %cards -> starts game
        if not msg:
            #reload cards
                
            self.players[nick] = Player(nick)
            serv.broadcast(JOIN_MSG % ', '.join(self.players))
            
            self.inited = True
            serv.on_msg.ensure(self.do_turn) # start watching all messages
        
        # end game explicitly
        if self.inited:
            if msg == "stop" or msg == "end":
                # determine winner
                try:
                    winners = sorted(self.players.values(), key=lambda x: x.score, reverse=True)
                    i = 1
                    for p in winners:
                        serv.say(dest, "%s) %s (%s points)" % (i, p.name, p.score))
                        i += 1
                except:
                    pass
                self.inited = False
                self.turn = -1
                self.players = {}
            elif msg == "score":
                try:
                    winners = sorted(self.players.values(), key=lambda x: x.score, reverse=True)
                    i = 1
                    for p in winners:
                        serv.say(dest, "%s) %s (%s points)" % (i, p.name, p.score))
                        i += 1
                except:
                    pass

    def next_round(self):
        
        # start round
        self.turn = self.turn + 1
        if self.turn >= len(self.players):
            self.turn = 0
        self.czar = self.players.items()[self.turn][0]

        # random pick black card
        serv.broadcast('%s is now card czar.' % self.czar)
        self.black = self.random_alg('black')
        self.black_blanks = max(1, self.black.count('_'))
        serv.broadcast(self.black)
        
        for p in self.players.values():
            p.selection = []
            count = HAND_SIZE - len(p.hand)
            for r in range(count):
                while True:
                    r = self.random_alg('white')
                    if r not in p.hand:
                        break
                p.hand += [r]
            if p.name != self.czar:
                hand = ""
                for r in range(len(p.hand)):
                    hand += '(%s) %s ' % (r+1, p.hand[r])
                multi = ' (one at a time)' if self.black_blanks>1 else ''
                serv.say(p.name, hand)
                serv.say(p.name, 'Pick a card%s: ' % multi)
        
        self.stage = Stage.players

    def go(self, cmd, serv, nick, dest, msg):
        
        if self.inited and self.stage == Stage.setup and self.players.items()[0][0] == nick:
            if len(self.players) >= MIN_PLAYERS:
                self.next_round()
            else:
                serv.broadcast('Not enough players to start.')

    def join(self, cmd, serv, nick, dest, msg):

        if not self.inited or self.stage != Stage.setup:
            return
        
        #if msg and nick in GODS:
        #    self.players[msg] = Player(msg)
        #else:
        self.players[nick] = Player(nick)
        
        for chan in CHANS:
            serv.broadcast(JOIN_MSG % ', '.join(self.players))
            if len(self.players) >= MIN_PLAYERS:
                serv.broadcast('When all players ready, %s must type %%go.' % self.players.items()[0][0])

g = Game()
serv.on_command.connect(g.init, "cards")
serv.on_command.connect(g.join, "join")
serv.on_command.connect(g.go, "go")

