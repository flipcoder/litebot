def url_msg(ctx, serv, nick, dest, msg):
    import urllib2,ssl
    from BeautifulSoup import BeautifulSoup
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    tokens = msg.split(' ')
    for t in tokens:
        if t.startswith("http://") or t.startswith("https://"):
            txt = BeautifulSoup(
                urllib2.urlopen(t,context=ctx)
            ).find('title').text
            txt = BeautifulSoup(txt, convertEntities=BeautifulSoup.HTML_ENTITIES)
            serv.say(dest, txt)
            continue

serv.on_msg.connect(url_msg, "url")

