def link(cmd, serv, nick, dest, msg):
    q = msg.replace(" ","+")
    serv.send("PRIVMSG %s :%s: http://lmgtfy.com/?q=%s\n" % (dest, nick, q))

serv.on_command.connect(link, "link")
