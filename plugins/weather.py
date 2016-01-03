import subprocess,json,traceback

saved_names = {}
weather_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
   "plugins",
   "weather.json"
)
with open(weather_file, 'a+') as f:
    try:
        saved_names = json.loads(f.read())
    except ValueError, e:
        saved_names = {}

def weather_save(serv):
    with open(weather_file, 'w') as f:
        f.write(json.dumps(saved_names, sort_keys=True, indent=4))

def w(cmd, serv, nick, dest, msg):
    try:
        if msg:
            msg = int(msg)
            saved_names[nick] = msg
            weather_save(serv)
        else:
            msg = int(saved_names[nick])
    except Exception, e:
        print traceback.format_exc()
        return
    try:
        plugins_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "plugins"
        )
        msg = subprocess.check_output([
            '/usr/bin/python2',
            os.path.join(plugins_path, 'cliweather/cliweather'),
            str(msg)
        ])
    except Exception, e:
        print traceback.format_exc()
        return
    lines = msg.split('\n')
    lines = filter(lambda x: x, lines)
    serv.broadcast(' | '.join(lines))

serv.on_command.connect(w, "w")

