def highfive(ctx, serv, nick, dest, msg):
    if msg=="\o":
        serv.send("PRIVMSG %s :o/\n" % dest)

serv.on_msg.connect(highfive)
