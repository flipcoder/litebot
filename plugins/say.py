def say(cmd, serv, nick, dest, msg):
    serv.say(dest, msg)

serv.on_command.connect(say, "say")

