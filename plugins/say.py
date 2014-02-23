def say(cmd, serv, nick, dest, msg):
    serv.send("PRIVMSG %s :%s\n" % (dest, msg))

serv.on_command.connect(say, "say")

