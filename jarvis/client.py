import jarvis.utils.conf as conf

conf.load("jarvis", {"SERVER_ADDRESS":"127.0.0.1", "SERVER_PORT":9107})

class Client(object):
    def __init__(self):
        self.address = conf.jarvis.SERVER_ADDRESS
        self.port = conf.jarvis.SERVER_PORT
        
