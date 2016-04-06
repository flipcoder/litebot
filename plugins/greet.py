import random,time

greeting_words = [
    "hi","hey","hello","yo","yoyo","greetings","hiya",
    "howdy","sup","wasup","whatsup","whats up","what's up"
]
leaving_words = [
    "bye","cya","seeya","bai"
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
    "It's a thankless job, but I've got a lot of Karma to burn off.",
    "Is your ass jealous of the amount of shit that just came out of your mouth?",
    "I'm not saying I hate you, but I would unplug your life support to charge my phone.",
    "What’s the difference between you and eggs? Eggs get laid and you don't.",
    "Roses are red, violets are blue, I have 5 fingers, the 3rd ones for you.",
    "Your birth certificate is an apology letter from the condom factory.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "If you are going to be two faced, at least make one of them pretty.",
    "I wasn't born with enough middle fingers to let you know how I feel about you.",
    "You must have been born on a highway because that's where most accidents happen.",
    "I’m jealous of all the people that haven't met you!",
    "You're so ugly, when your mom dropped you off at school she got a fine for littering.",
    "Two wrongs don't make a right, take your parents as an example.",
    "If laughter is the best medicine, your face must be curing the world.",
    "How many times do I have to flush to get rid of you?",
    "You shouldn't play hide and seek, no one would look for you."
]

last_greet = 0.0
last_part = 0.0
throttle = 5.0

def greet_msg(ctx, serv, nick, dest, msg):
    global last_greet
    global last_part
    msg = msg.lower()
    msg = msg.replace("?", " ").replace("!", " ").replace(".", " ")
    t = time.time()
    
    for w in greeting_words:
        if msg == w:
            if t - last_greet > throttle:
                last_greet = t
                serv.say(dest, random.choice(greeting_words))
            return True
        elif msg.startswith(w) or msg.endswith(w):
            if NICK in msg:
                if t - last_greet > throttle:
                    last_greet = t
                    serv.say(dest, nick+": "+random.choice(greeting_words))
                return True
        
    for w in leaving_words:
        if msg == w or msg.startswith(w+" ") or msg.endswith(" "+w):
            if t - last_part > throttle:
                last_part = t
                serv.say(dest, random.choice(leaving_words))
            return True
        
    #for w in laughing_words:
    #    if msg == w or msg.startswith(w+" ") or msg.endswith(" "+w):
    #        if random.random() > 0.50:
    #            serv.say(dest, random.choice(laughing_words))
    #        return True

    if NICK in msg:
        serv.say(dest, random.choice(reactions))
        return True

def greet_quit(ctx, serv):
    for chan in CHANS:
        serv.say(chan, random.choice(leaving_words))
    
serv.on_msg.connect(greet_msg, "greet")
serv.on_quit.connect(greet_quit, "greet")

