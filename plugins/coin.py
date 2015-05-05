import random

def coin_msg(ctx, serv, nick, dest, msg):
    r = random.randint(0,1)
    serv.send("PRIVMSG %s :%s\n" % (dest, "heads" if r else "tails"))
    return True
    
serv.on_command.connect(coin_msg, "coin")

