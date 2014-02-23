import operator

quote_answer = ""
quote_score = {}
def quote(cmd, serv, nick, dest, msg):
    global quote_answer

    try:
        QUOTE_PATH
    except:
        return
    
    linec = 0
    
    with open(QUOTE_PATH, "r") as f:
        for line in f:
            if line.strip():
                linec += 1
    
    r = random.randint(0,linec)
    
    i = 0
    with open(QUOTE_PATH, "r") as f:
        for line in f:
            if line.strip():
                if i == r:
                    s = line.find("<")
                    e = line.find(">")
                    if quote_answer:
                        serv.send("PRIVMSG %s :Last answer was %s!\n" % (dest, quote_answer))
                    quote_answer = line[s+2:e]
                    #print "answer: %s" % quote_answer # cheater!
                    if e != -1:
                        line = line[e+2:]
                        serv.send("PRIVMSG %s :Guess the quote: %s\n" % (dest, line))
                    else:
                        serv.send("PRIVMSG %s :meh...")
                    #print line
                    break
            i+=1
    
    serv.on_msg.ensure(quote_event)

def quote_show_score(ctx, serv, nick, dest, msg):
    #if msg == "quote":
    output = []
    sorted_score = sorted(quote_score.iteritems(), key=operator.itemgetter(1))
    for tup in sorted_score:
        output += ["%s: %s" % tup]
    if len(output) > 5:
        output = output[:5] + ["..."]
    sock.send("PRIVMSG %s :Score: %s\n" % (dest, " ,".join(output)))

def quote_event(ctx, serv, nick, dest, msg):
    global quote_answer
    global quote_score
    if msg and quote_answer and msg.lower() == quote_answer.lower():
        sock.send("PRIVMSG %s :Correct answer: %s! +1 points awarded to %s!\n" % (dest, quote_answer, nick))
        quote_score[nick] = quote_score.get(nick, 0) + 1
        quote_answer = ""
        quote("quote", serv, nick, dest, msg)

serv.on_command.connect(quote, "quote")
serv.on_command.connect(quote_show_score, "score")
serv.on_command.connect(quote_show_score, "points")

