def log(ctx, serv, data):
    print data

serv.on_data.connect(log, "log")

