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
        for ctx, funcs in self.slots.items():
            if not limit_context or ctx in limit_context:
                for func in funcs:
                    if kwargs.get("include_context", False):
                        func(ctx, *args)
                        continue
                    func(*args)

class Server:
    def __init__(self, sock):
        self.sock = sock
        self.on_msg = Signal()
        self.on_data = Signal()
        self.on_command = Signal()
    def send(self, msg):
        self.sock.send(msg)

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

while True:
    
    buf = sock.recv(4096)

    serv.on_data.emit(serv, buf, include_context=True)
    
    if buf.find("PING") != -1:
        sock.send("PONG %s\r\n" % buf.split()[1]+"\n")
        if not logged_in:
            sock.send("PRIVMSG nickserv identify %s\n" % PASS)
            sock.send("JOIN %s\n" % CHAN)
            logged_in = True
            print "signed in"
    elif buf.find("PRIVMSG") != -1:
        #print buf.strip()
        buf = buf.replace("!",":").split(":")
        nick = buf[1]
        if len(buf[3]) <= 2:
            continue
        msg = ":".join(buf[3:])[:-2]
        dest = buf[2].split()[2]
        
        serv.on_msg.emit(serv, nick, dest, msg, include_context=True)
        
        if msg=="%":
            about("about", serv, nick, dest, msg)
            continue
        
        if msg and msg.startswith("%"):
            msg = msg[1:]
            msg = msg.strip()
            chop = msg.find(" ")
            if chop != -1:
                cmd = msg[chop:]
                msg = msg[:chop+1]
            else:
                cmd = msg
                msg = ""
            serv.on_command.emit(serv, nick, dest, msg,
                include_context=True, limit_context=[cmd])
            continue

#except:
#    print "bye"
    #s.send("PRIVMSG %s :bye" % CHAN)

