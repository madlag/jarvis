import jarvis.utils.conf as conf
import urllib

conf.load("jarvis", defaults = {"SERVER_ADDRESS":"127.0.0.1", "SERVER_PORT":9107})

class Client(object):
    def __init__(self):
        self.address = conf.jarvis.SERVER_ADDRESS
        self.port = conf.jarvis.SERVER_PORT
        

    def update(self, id, op, content):
        body = urllib.urlencode({"op":op, "content":content})
        print "CONF JARVIS", dir(conf.jarvis)
        base_url = "http://%s:%s/state/update/" % (conf.jarvis.SERVER_ADDRESS, conf.jarvis.SERVER_PORT)
        response = urllib.urlopen(base_url + id + "/", body).read()
        print "response=", response
        if response != "OK":
            raise Exception(response)
