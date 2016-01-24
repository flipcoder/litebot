def highfive(ctx, serv, nick, dest, msg):
    if msg=="\o":
        serv.say(dest, "o/")
    elif msg=="o/":
        serv.say(dest, "\o")
    elif msg=="o'":
        serv.say(dest, "'o")
    elif msg=="'o":
        serv.say(dest, "o'")

serv.on_msg.connect(highfive)

