import subprocess

def w(cmd, serv, nick, dest, msg):
    try:
        msg = int(msg)
    except:
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
    except:
        return
    lines = msg.split('\n')
    lines = filter(lambda x: x, lines)
    serv.broadcast(' | '.join(lines))

serv.on_command.connect(w, "w")

