import random

greeting_words = [
    "hi","hey","hello","yo","yoyo","greetings","hiya",
    "howdy","sup","wasup","whatsup","whats up","what's up"
]
leaving_words = [
    "bye","cya","seeya","later","bai"
]
laughing_words = [
    "lol","lolz","hehe","haha","i don't get it","rofl",
    "lmfao","lmfao","jokes are funny","not funny"
]
reactions = [
    "How about never? Is never good for you?",
    "You sound reasonable... Time to up the medication.",
    "I see you've set aside this special time to humiliate yourself in public.",
    "I don't work here. I'm a consultant.",
    "Ahhh... I see the screw-up fairy has visited us again",
    "I don't know what your problem is, but I'll bet it's hard to pronounce.",
    "I like you. You remind me of when I was young and stupid.",
    "You are validating my inherent mistrust of strangers.",
    "I'll try being nicer if you'll try being smarter.",
    "I'm out of my mind, but feel free to leave a message.",
    "I'm really easy to get along with once you people learn to worship me.",
    "It sounds like English, but I can't understand a word you're saying.",
    "I can see your point, but I still think you're full of it.",
    "What am I? Flypaper for freaks!?",
    "Any connection between your reality and mine is purely coincidental.",
    "I have plenty of talent and vision. I just don't give a damn.",
    "I'm already visualizing the duct tape over your mouth.",
    "Your teeth are brighter than you is.",
    "No, my powers can only be used for good.",
    "We're all refreshed and challenged by your unique point of view.",
    "The fact that no one understands you doesn't mean you're an artist.",
    "I will always cherish the initial misconceptions I had about you.",
    "Who me? I just wander from room to room.",
    "I'm not being rude. You're just insignificant.",
    "It's a thankless job, but I've got a lot of Karma to burn off."
]

def response_event(ctx, serv, nick, dest, msg):
    msg = msg.lower()
    msg = msg.replace("?", " ").replace("!", " ").replace(".", " ")
    
    for w in greeting_words:
        if msg == w:
            serv.send("PRIVMSG %s :%s\n" % (
                dest, random.choice(greeting_words)))
            return True
        elif msg.startswith(w) or msg.endswith(w):
            if NICK in msg:
                serv.send("PRIVMSG %s :%s %s\n" % (
                    dest, random.choice(greeting_words), nick))
                return True
        
    for w in leaving_words:
        if msg == w or msg.startswith(w+" ") or msg.endswith(" "+w):
            serv.send("PRIVMSG %s :%s\n" % (
                dest, random.choice(leaving_words)))
            return True
        
    for w in laughing_words:
        if msg == w or msg.startswith(w+" ") or msg.endswith(" "+w):
            if random.random() > 0.50:
                serv.send("PRIVMSG %s :%s\n" % (
                    dest, random.choice(laughing_words)))
            return True

    if NICK in msg:
        serv.send("PRIVMSG %s :%s\n" % (dest, random.choice(reactions)))
        return True

serv.on_msg.connect(response_event, "greet")

