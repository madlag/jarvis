import jarvis.client as client

class Display():
    def __init__(self):
        pass

    def init(self):
        pass

    def destroy(self):
        pass

    def reset(self):
        client.Client().update("debug", "set", "")
    
    def start(self):
        client.Client().update("debug", "set", "")

    def finish(self):
        pass

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        print "INFO", info

    def errorprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        print "INFO", info
