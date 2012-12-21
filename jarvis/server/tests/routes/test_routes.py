import os
import os.path as op
import unittest
import shutil
import redis

import mox
import jarvis.commands as commands

import urllib
import time
import json
import gevent
import logging
log = logging.getLogger('eventsource.client')

this_dir = op.dirname(__file__)
data_dir = op.join(this_dir, "data")
tmp_dir = op.join(this_dir, "tmp")

def debug(*args):
    commands.debug(*args)

class Event(object):
    """
    Contains a received event to be processed
    """
    def __init__(self):
        self.type = None
        self.name = None
        self.data = None
        self.id = None

    def __repr__(self):
        return "Event<%s,%s,%s,%s>" % (str(self.type),  str(self.id), str(self.name), str((self.data or "").replace('\n','\\n')))


class EventSourceClient(object):
    def __init__(self):
        self.logging = False

    def debug(self, *args):
        if not self.logging:
            return
        log.debug(*args)

    def info(self, *args):
        if not self.logging:
            return
        log.info(*args)

    def parse(self, message):
        """
        Acts on message reception
        :param message: string of an incoming message

        parse all the fields and builds an Event object that is passed to the callback function
        """
        self.debug("handle_stream(...)")
        
        event = Event()

        for line in message.strip('\n').split('\n'):
            if len(line) == 0:
                yield event
                event = Event()
                continue

            (field, value) = line.split(":",1)
            event.type = field
            if field == 'event':
                event.name = value.lstrip()
            elif field == 'data':
                value = value.lstrip()
                if event.data is None:
                    event.data = value
                else:
                    event.data = "%s\n%s" % (event.data, value)
            elif field == 'id':
                event.id = value.lstrip()
            elif field == 'retry':
                try:
                    self.retry_timeout = int(value)
                    self.info( "timeout reset: %s" % (value,) )
                except ValueError:
                    pass
            elif field == '':
                self.info( "received comment: %s" % (value,) )
            else:
                raise Exception("Unknown field !")
        if event.type != None:
            yield event

    
class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Refresh the temporary directory
        try:
            shutil.rmtree(tmp_dir, True)
        except:
            pass
        os.makedirs(tmp_dir)
        
        try:
            os.makedirs(data_dir)
        except:
            pass
        
        self.mox = mox.Mox()
        
    def data_file_name(self, filename):
        return op.join(data_dir, filename)
    
    def get_tst_file_name(self, filename):
        return op.join(tmp_dir, filename)

    def tst_basic_send(self, msg):
        gevent.sleep(1.0)
        msg = {"op":"set", "content":str(msg)}
        msg = urllib.urlencode(msg)
        a = urllib.urlopen("http://localhost:9017/state/update/a/", msg).read()
        print "GOT", a
    
    def st_basic_json(self):
        client = redis.Redis("127.0.0.1", 6379)
        client.delete("state-user-a")
        oldtime = str(time.time())
        msg = {"op":"set", "content":oldtime}
        msg = urllib.urlencode(msg)

        a = urllib.urlopen("http://localhost:9017/state/update/a/", msg).read()

        newtime = time.time() + 1
        sublet = gevent.Greenlet.spawn(self.tst_basic_send, newtime)
        
        r = urllib.urlopen("http://localhost:9017/state/stream/json/?count=2&ids=a,b").read()
        r = r.split("\n")

        sublet.join()
        
        self.assertTrue(len(r) == 3)
        for i, b in enumerate(r):
            if b == '':
                continue
            b = json.loads(b)
            self.assertTrue("time" in b)
            del b["time"]

            data = [oldtime, newtime][i]
                
            ref = {u'user': u'user', u'op': u'set', u'id': u'a', u'parameters': {u'content': unicode(data)}}
            self.assertTrue(b == ref)
    


    def test_basic_eventsource(self):
        client = redis.Redis("127.0.0.1", 6379)
        client.delete("state-user-a")
        oldtime = str(time.time())
        msg = {"op":"set", "content":oldtime}
        msg = urllib.urlencode(msg)

        a = urllib.urlopen("http://localhost:9017/state/update/a/", msg).read()
        
        msg = {"ids":"a,b", "count":"2"}
        msg = urllib.urlencode(msg)

        newtime = time.time() + 1
        sublet = gevent.Greenlet.spawn(self.tst_basic_send, newtime)
        
        r = urllib.urlopen("http://localhost:9017/state/stream/eventsource/", msg).read()
        msgs = []

        esc =  EventSourceClient()
        for m in esc.parse(r):
            if m.type == "data":
                msgs += [m]

        r = msgs
                                
        self.assertTrue(len(r) == 2)
        
        for i, b in enumerate(r):
            if b == '':
                continue
            b = json.loads(b.data)
            self.assertTrue("time" in b)
            del b["time"]

            data = [oldtime, newtime][i]
                
            ref = {u'user': u'user', u'op': u'set', u'id': u'a', u'parameters': {u'content': unicode(data)}}
            
            self.assertTrue(b == ref)
    

        
    def tearDown(self):
        self.mox.UnsetStubs()
        
        try:
            shutil.rmtree(tmp_dir, True)
        except:
            pass
        
def main():
    commands.add_watch_file(op.join(op.dirname(__file__), "../../views.py"))
    commands.add_watch_file(op.join(op.dirname(__file__), "../../state.py"))
    prefix = "test_basic_eventsource"
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRoutes)
    suite = filter(lambda x : str(x).startswith(prefix), suite)
    suite = unittest.TestLoader().suiteClass(suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    commands.testunit_result(result)

if __name__ == "__main__":
    main()

    
