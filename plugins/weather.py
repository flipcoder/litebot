import subprocess

def w(cmd, serv, nick, dest, msg):
    try:
        msg = int(msg)
    except:
        return
    try:
        msg = subprocess.check_output(['/usr/bin/python2','plugins/cliweather/cliweather', str(msg)])
    except:
        return
    lines = msg.split('\n')
    lines = filter(lambda x: x, lines)
    serv.broadcast(' | '.join(lines))

serv.on_command.connect(w, "w")

