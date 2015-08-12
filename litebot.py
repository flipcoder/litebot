#!/usr/bin/env python2

import sys
import socket
import urllib
import string
import random

class Signal:
    def __init__(self):
        self.slots = {}
    def ensure(self, func, context=""):
        if context not in self.slots:
            self.connect(func, context)
            return
        if func not in self.slots[context]:
            self.connect(func, context)
    def connect(self, func, context=""):
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
    def send(self, msg):
        self.sock.send(msg)
    def say(self, dest, msg):
        if type(dest) == type([]):
            for chan in dest:
                self.sock.send("PRIVMSG %s :%s\n" % (chan, msg))
            return
        self.sock.send("PRIVMSG %s :%s\n" % (dest, msg))
    def broadcast(self, msg):
        self.say(CHANS, msg)

with open("config.py") as source:
    eval(compile(source.read(), "config.py", 'exec'))

buf = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv = Server(sock)
sock.connect((HOST, PORT))
sock.send("NICK %s\n" % NICK)
sock.send("USER %s %s %s :%s\n" % (IDENT, NICK, HOST, REALNAME))

for cmd in PLUGINS:
    print "loading %s plugin..." % cmd
    with open("plugins/%s.py" % cmd) as source:
        eval(compile(source.read(), "%s.py" % cmd, 'exec'))
    
#try:
#    with open("plugins/__init__.py") as source:
#        eval(compile(source.read(), "plugins.py", 'exec'))
#except:
#    sys.exit(1)

def about(cmd, serv, nick, dest, msg):
    serv.send("PRIVMSG %s :I am litebot (github.com/flipcoder/litebot)\n" % dest)
    serv.send("PRIVMSG %s :Commands (prefix with %%): %s\n" % (dest, ", ".join(sorted(serv.on_command.slots))))

logged_in = False
        
print "%s running" % NICK

try:
    while True:
        
        buf = sock.recv(4096)
        
        if buf.find("PING") != -1:
            sock.send("PONG %s\r\n" % buf.split()[1]+"\n")
            if not logged_in:
                sock.send("PRIVMSG nickserv identify %s\n" % PASS)
                for chan in CHANS:
                    sock.send("JOIN %s\n" % chan)
                logged_in = True
                print "signed in"
                serv.on_enter.emit(serv,
                    include_context=True, allow_break=True)
            continue
        
        serv.on_data.emit(serv, buf, include_context=True, allow_break=True)
        
        if buf.find("PRIVMSG") != -1:
            #print buf.strip()
            buf = buf.replace("!",":").split(":")
            nick = buf[1]
            if len(buf[3]) <= 2:
                continue
            msg = ":".join(buf[3:])[:-2]
            dest = buf[2].split()[2]
            
            serv.on_msg.emit(serv, nick, dest, msg,
                include_context=True, allow_break=True)
            
            if msg=="%" or msg=="%help":
                about("about", serv, nick, dest, msg)
                continue

            if msg and msg.startswith("%"):
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
except:
    serv.on_quit.emit(serv, include_context=True)
    raise

