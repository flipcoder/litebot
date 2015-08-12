def say(cmd, serv, nick, dest, msg):
    serv.broadcast(msg)

serv.on_command.connect(say, "say")

