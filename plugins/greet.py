import random

def response_event(ctx, serv, nick, dest, msg):
    msg = msg.lower()
    
    greeting_words = [
        "hi","hey","hello","yo","yoyo","greetings",
        "howdy","sup","wasup"
    ]
    for w in greeting_words:
        if msg == w or msg.startswith(w+" "):
            serv.send("PRIVMSG %s :%s\n" % (
                dest, random.choice(greeting_words)))
            break
    
    leaving_words = [
        "bye","cya","seeya","later","bai"
    ]
    for w in leaving_words:
        if msg == w or msg.startswith(w+" "):
            serv.send("PRIVMSG %s :%s %s\n" % (
                dest, random.choice(leaving_words), nick))
            break
        
    laughing_words = [
        "lol","hehe","haha","i don't get it","LOL","rofl",
        "lmfao","lmfao","jokes are funny","not funny"
    ]
    for w in laughing_words:
        if msg == w or msg.startswith(w+" ") or msg.endswith(" "+w):
            if random.random() > 0.75:
                serv.send("PRIVMSG %s :%s\n" % (
                    dest, random.choice(laughing_words)))
                break

    response = [
        ":)",
        "someone talking about me?"
    ]
    if NICK in msg:
        if msg.endswith("?"):
            serv.send("PRIVMSG %s ::(\n" % dest)
        else:
            reactions = [
                ";)", ":)","that's my name, don't wear it out"
            ]
            serv.send("PRIVMSG %s :%s\n" % (dest, random.choice(reactions)))
    
serv.on_msg.connect(response_event, "greet")

