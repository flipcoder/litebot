import time
throttle = 5.0
last_t = 0

def jealous(ctx, serv, nick, dest, msg):
    global last_t
    if msg.startswith("!") and msg[1] != "!"
        t = time.time()
        if t - last_t > throttle:
            last_t = t
            serv.say(dest, ":'(")
        
serv.on_msg.connect(jealous)

