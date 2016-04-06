#!/usr/bin/env python2

import os
import sys
import socket
import urllib
import string
import random
import traceback
import time

class Signal:
    def __init__(self):
        self.slots = {}
        self.meta = {}
    def ensure(self, func, context=""):
        if context not in self.slots:
            self.connect(func, context)
            return
        if func not in self.slots[context]:
            self.connect(func, context)
    def connect(self, func, context="", hidden=False):
        if context:
            self.meta[context] = {
                'hidden':  hidden
            }
        if context not in self.slots:
            self.slots[context] = []
        self.slots[context] += [func]
    def clear(self):
        self.slots = {}
    def disconnect(self, context):
        del self.slots[context]
    def emit(self, *args, **kwargs):
        limit_context = kwargs.get("limit_context", None)
        brk = kwargs.get("allow_break", False)
        force_brk = kwargs.get("force_break", False)
        include_context = kwargs.get("include_context", False)
        for ctx, funcs in self.slots.items():
            if not limit_context or ctx in limit_context:
                for func in funcs:
                    r = None
                    if include_context:
                        r = func(ctx, *args)
                    else:
                        r = func(*args)
                    if brk and r:
                        return
                    if force_brk:
                        return
                    continue

class Server:
    def __init__(self, sock):
        self.sock = sock
        self.on_msg = Signal()
        self.on_data = Signal()
        self.on_command = Signal()
        self.on_enter = Signal()
        self.on_quit = Signal()
        self.test = not sock
        
    def send(self, msg):
        if self.test:
            print msg
        else:
            self.sock.send(msg)
    
    def say(self, dest, msg):
        if type(dest) == type([]):
            if TEST:
                print "(all) %s" % msg
            else:
                for chan in dest:
                    self.sock.send("PRIVMSG %s :%s\n" % (chan, msg))
            return
        if TEST:
            print "(%s) %s" % (dest,msg)
        else:
            self.sock.send("PRIVMSG %s :%s\n" % (dest, msg))
            
    def broadcast(self, msg):
        self.say(CHANS, msg)

    def about(self, cmd, nick, dest, msg, plugins):
        self.say(dest, "I am litebot (github.com/flipcoder/litebot)")
        cmds = filter(lambda x: not self.on_command.meta[x]['hidden'], sorted(self.on_command.slots))
        self.say(dest, "Plugins: %s" % (", ".join(plugins)))
        self.say(dest, "Commands (prefix with %%): %s" % (", ".join(cmds)))

def handle_error(serv, e, errors, GODS=[], ERROR_SPAM=100, logged_in=False):
    try:
        ec = errors[e]
        if ec < ERROR_SPAM:
            ec += 1
        elif ec == ERROR_SPAM:
            if logged_in:
                for god in GODS:
                    serv.say(god, "Bot is error spamming: " + e)
    except KeyError:
        print e
        errors[e] = 1
        if logged_in:
            for god in GODS:
                serv.say(god, e)


TEST = bool(set(["-t","--test"]) & set(sys.argv[1:]))

if __name__=='__main__':
    
    import readline
    
    PLUGINS = None
    RECONNECT = False
    ERROR_SPAM = 100
    IGNORE = []

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.py"
    )
    
    with open(config_path) as source:
        eval(compile(source.read(), config_path, 'exec'))

    reconnect = RECONNECT
    while reconnect:
        reconnect = RECONNECT
        errors = {}
        buf = ""

        sock = None
        if not TEST:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv = Server(sock)
        if not TEST:
            sock.connect((HOST, PORT))
            sock.send("NICK %s\n" % NICK)
            sock.send("USER %s %s %s :%s\n" % (IDENT, NICK, HOST, REALNAME))

        plugins_fn = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "plugins"
        )

        for p in PLUGINS[:]:
            try:
                with open(os.path.join(plugins_fn, p+".py")) as source:
                    eval(compile(source.read(), "%s.py" % p, 'exec'))
            except Exception:
                print >>sys.stderr, "Exception in plugin \"%s\":" % p
                print >>sys.stderr, traceback.format_exc()
                PLUGINS.remove(p)

        logged_in = False or TEST
        test_nick = 'user'

        #if TEST:
        #    print 'Test mode on %s.' % CHANS[0]

        while True:
            try:
                
                if not TEST:
                    
                    buf = sock.recv(4096)
                    if not buf:
                        raise EOFError
                    
                    # print "buf (hex): " + str(buf).encode("hex")
                    
                    if buf.find("PING") != -1:
                        sock.send("PONG %s\r\n" % buf.split()[1]+"\n")
                        if not logged_in:
                            time.sleep(1)
                            sock.send("PRIVMSG nickserv identify %s\n" % PASS)
                            for chan in CHANS:
                                sock.send("JOIN %s\n" % chan)
                            logged_in = True
                            #print "signed in"
                            serv.on_enter.emit(serv,
                                include_context=True, allow_break=True)
                        continue
                    
                    serv.on_data.emit(serv, buf, include_context=True, allow_break=True)
                
                if buf.find("PRIVMSG") != -1 or TEST:
                    if not TEST:
                        bang_idx = buf.find('!')
                        if bang_idx == -1:
                            continue
                        tokens = []
                        # print "buf: " + str(buf)
                        tokens += [buf[1:bang_idx]]
                        tokens += buf[bang_idx+1:].split(":")
                        # print 'tokens: ' + str(tokens)
                        # print str(buf)
                        
                        nick = tokens[0]
                        dest = tokens[1].split()[2]
                        msg = ':'.join(tokens[2:]).rstrip()
                        # print 'nick: %s, dest: %s, msg: %s' % (nick,dest,msg)
                    
                    if TEST:
                        dest = CHANS[0]
                        nick = test_nick
                        msg = raw_input('%s> ' % test_nick)
                    
                    ignore = nick in IGNORE
                    
                    if not TEST or msg:
                        if not ignore:
                            serv.on_msg.emit(serv, nick, dest, msg,
                                include_context=True, allow_break=True)
                    
                    if TEST:
                        if msg.startswith("/n ") or msg.startswith("/nick "):
                            test_nick = msg[msg.index(" ")+1:]
                            continue
                        elif msg.startswith("/n"):
                            test_nick = 'user'
                        
                    if msg=="%" or msg=="%help":
                        if not ignore:
                            serv.about("about", nick, dest, msg, PLUGINS)
                            continue

                    if msg and msg.startswith("%"):
                        if not ignore:
                            msg = msg[1:]
                            msg = msg.strip()
                            chop = msg.find(" ")
                            if chop != -1:
                                cmd = msg[:chop]
                                msg = msg[chop+1:]
                            else:
                                cmd = msg
                                msg = ""
                            serv.on_command.emit(serv, nick, dest, msg,
                                include_context=True, limit_context=[cmd], force_break=True
                            )
                            continue
            
            except EOFError, e:
                serv.on_quit.emit(serv, include_context=True)
                break # may reconnect depending on settings

            except Exception, e:
                print "Exception"
                handle_error(serv, e, errors, GODS, ERROR_SPAM, logged_in)

