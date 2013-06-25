import jarvis.utils.conf as conf
import urllib
import json

conf.load("jarvis", defaults = {"SERVER_ADDRESS":"127.0.0.1", "SERVER_PORT":9107})

class Client(object):
    def __init__(self):
        self.address = conf.jarvis.SERVER_ADDRESS
        self.port = conf.jarvis.SERVER_PORT
        
    def update(self, id, op, content):
        body = urllib.urlencode({"op":op, "content":content})
#        print "CONF JARVIS", dir(conf.jarvis)
        base_url = "http://%s:%s/state/update/" % (conf.jarvis.SERVER_ADDRESS, conf.jarvis.SERVER_PORT)
        response = urllib.urlopen(base_url + id + "/", body).read()
#        print "response=", response
        if response != "OK":
            raise Exception(response)

    def get(self, id):
        body = urllib.urlencode({"ids":id, "count":1})
        base_url = "http://%s:%s/state/stream/json/no_session/?%s" % (conf.jarvis.SERVER_ADDRESS, conf.jarvis.SERVER_PORT, body)
        result = urllib.urlopen(base_url).read()
        print "result='%s'" % result
        r = json.loads(result)
        return r["parameters"]["content"]
