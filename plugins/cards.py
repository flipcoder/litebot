#!/usr/bin/env python2

import os
import json
import copy
import random
        
random.seed()

HAND_SIZE = 10
MIN_PLAYERS = 2
HISTORY_LEN = 100
MIN_PLAYERS = 2
HAND_SIZE = 10
JOIN_MSG = "Type %%join to join the game. Players: %s"
CARDS = {}
cards_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
   "plugins",
   "cards.json"
)
WILD_RATE = 0.08

with open(cards_file) as f:
    CARDS = json.loads(f.read())

class Stage:
    setup = 0 # players can join in, pre-deal
    players = 1 # players pick
    czar = 2 # czar picks

class Player:
    def __init__(self, name, game, **kwargs):
        self.name = name
        self.score = 0
        self.hand_size = HAND_SIZE
        self.hand = []
        self.selection = []
        self.cpu = kwargs.get('cpu', False)
        self.game = game
        self.fill()
    
    def __str__(self):
        return self.name

    # draw until hand is full
    def fill(self):
        count = self.hand_size - len(self.hand)
        for r in range(count):
            while True:
                r = self.game.random_alg('white')
                if r == 'WILDCARD' or r not in self.hand: # no dupes
                    break
            self.hand += [r]

    def show_hand(self, game):
        hand = ""
        for r in range(len(self.hand)):
            hand += '(%s) %s ' % (r+1, self.hand[r])
        multi = ' (one at a time)' if game.black_blanks>1 else ''
        serv.say(self.name, hand)
        serv.say(self.name, 'Pick card%s: ' % multi)

class Game:
    
    def random_balanced_sets(self, deck, wild=True):

        i = 0
        max_retries = 10
        if deck not in self.history:
            self.history[deck] = []

        if wild and deck=='white' and random.random() < WILD_RATE:
            return "WILDCARD"
        
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
        
        self.random_alg = self.random_balanced_sets
        self.reset()

    def reset(self):
        
        self.players = {}
        self.host = None
        self.inited = False
        #turn = -1 # who is czar?
        self.black = "" # current black card text
        self.black_blanks = 1
        self.czar = ""
        self.cards = CARDS
        self.rid = []
        self.history = {}
        
        self.stage = Stage.setup

    def restart(self):
        
        self.reset()
        
        self.players[NICK] = Player(NICK, self, cpu=True) # cpu player
                
        self.players[nick] = Player(nick, self)
        serv.broadcast(JOIN_MSG % ', '.join(self.players))
        self.host = self.players[nick]
        
        self.inited = True
        serv.on_msg.ensure(self.do_turn) # start watching all messages

    # determine winner
    def scores(self):
        
        try:
            winners = sorted(self.players.values(), key=lambda x: x.score, reverse=True)
            i = 1
            for p in winners:
                serv.say(dest, "%s) %s (%s points)" % (i, p.name, p.score))
                i += 1
        except:
            pass
    
    def poll(self):
        
        if self.stage == Stage.players:
            for p in self.players.values():
                if not p.cpu and p.name != self.czar:
                    if len(p.selection) < self.black_blanks:
                        return # someone not ready
                    elif p.selection and p.selection[-1]=="WILDCARD":
                        return # someone not ready
            
            # remove all the blank placeholder cards used to prevent IDs from changing during multiselection
            for p in self.players.values():
                p.hand = filter(lambda card: card, p.hand)
            
                # have cpus randomly pick an answer now, instead of maintaining a hand
                if p.cpu:
                    p.selection = []
                    for x in xrange(self.black_blanks):
                        p.selection += [self.random_alg('white', wild=False)]
            
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
                
                if p.selection and p.selection[-1] == "WILDCARD":
                    p.selection[-1] = msg
                    if len(p.selection) == self.black_blanks:
                        self.poll()
                    else:
                        serv.say(p.name, 'Pick next card (#%s): ' % (len(p.selection)+1))
                elif len(p.selection) < self.black_blanks:
                    pick = None
                    try:
                        pick = p.hand[int(msg)-1]
                    except ValueError, e:
                        return
                    except IndexError, e:
                        return
                    except:
                        return
                    
                    if not pick: # previously picked cards are blanked
                        serv.say(nick, 'You already picked that card. Pick a different one.')
                        return
                    p.selection += [pick]
                    p.last_answer = pick
                    p.hand[int(msg)-1] = "" # blank cards to avoid repick and preserve offsets
                    
                    if p.selection and p.selection[-1] == "WILDCARD":
                        serv.say(p.name, "You have chosen wildcard. Enter card text:")
                    elif len(p.selection) == self.black_blanks:
                        self.poll()
                    else:
                        serv.say(p.name, 'Pick next card (#%s): ' % (len(p.selection)+1))
                elif len(p.selection) == self.black_blanks:
                    pick = None
                    try:
                        pick = p.hand[int(msg)-1]
                    except ValueError, e:
                        return
                    except IndexError, e:
                        return
                    except:
                        return
                    if not pick: # previously picked cards are blanked
                        serv.say(nick, 'You already picked that card.')
                        return

                    p.selection[-1] = pick
                    for c in p.hand: # put back in last answer
                        if c == "":
                            c = p.last_answer
                            break
                    p.last_answer = pick
                    p.hand[int(msg)-1] = ""
                    
                    if p.selection and p.selection[-1] == "WILDCARD":
                        serv.say(p.name, "You have chosen wildcard. Enter card text:")
        
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
                
                if not p.cpu:
                    serv.broadcast("%s gains 1 point with: %s" % (p.name, ', '.join(p.selection)))
                else:
                    serv.broadcast("Beaten by a robot. Humanity must suffer the consequences.")
                    #if random.randint(0,1):
                    #    self.players[self.czar].score -= 1
                    #    serv.broadcast("%s was attacked by a robot (-1 point)." % self.czar)
                    #else:
                    #    random_player = random.choice(filter(lambda p: not p.cpu, self.players.values()))
                    #    random_player.score -= 1
                    #    serv.broadcast("%s was attacked by a robot (-1 point)." % random_player.name)
                
                self.next_round()

    def init(self, cmd, serv, nick, dest, msg):
        
        if self.inited:
            if msg == "stop" or msg == "end" or msg == "reset":
                self.scores()
                self.reset()
            elif msg == "score":
                self.scores()
            # elif msg.startswith("kick "):
            #     user = msg[msg.index(" ")+1:]
            #     if self.czar == user:
            #         next_turn()
            #     if user in self.players:
            #         p = self.players[user]
            #         serv.broadcast("Kicked %s (score: %s) " % (p.name,p.score))
            #         del self.players[user]
        else:
            if not msg:
                self.restart()

    def next_turn(self):
        while True:
            if self.czar == '':
                # first turn
                self.czar = self.host.name
            else:
                turn = list(self.players.keys()).index(self.czar)
                turn += 1
                if turn >= len(self.players):
                    turn = 0
                self.czar = self.players.items()[turn][0]
                print self.czar
                if not self.players[self.czar].cpu:
                    # cpu players are never czars
                    return
        
    def next_round(self):
        
        self.next_turn()

        # random pick black card
        serv.broadcast('%s is now card czar.' % self.czar)
        self.black = self.random_alg('black')
        self.black_blanks = max(1, self.black.count('_'))

        serv.broadcast(self.black)
        
        for p in self.players.values():
            if p.cpu: continue
            p.selection = []
            p.fill()
            if p.name != self.czar:
                serv.say(p.name, self.black)
                p.show_hand(self)
            else:
                serv.say(p.name, "You're now czar.  Wait until other players have selected cards.")
        
        self.stage = Stage.players

    def go(self, cmd, serv, nick, dest, msg):
        
        if self.inited and self.stage == Stage.setup and nick == self.host.name:
            if len(self.players) >= MIN_PLAYERS:
                self.next_round()
            else:
                serv.broadcast('Not enough players to start.')

    def join(self, cmd, serv, nick, dest, msg):

        if not self.inited:
            return
        
        if TEST and msg:
            self.players[msg] = Player(msg, self)
        else:
            self.players[nick] = Player(nick, self)
        
        if self.stage == Stage.setup:
            for chan in CHANS: 
                serv.broadcast(JOIN_MSG % ', '.join(self.players))
                if len(self.players) >= MIN_PLAYERS:
                    serv.broadcast('When all players ready, %s must type %%go.' % self.host.name)
        elif self.stage == Stage.players:
            serv.say(nick, self.black)
            self.players[nick].show_hand(self)

g = Game()
serv.on_command.connect(g.init, "cards")
serv.on_command.connect(g.join, "join", hidden=True)
serv.on_command.connect(g.go, "go", hidden=True)

