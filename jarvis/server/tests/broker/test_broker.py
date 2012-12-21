from gevent import monkey;
monkey.patch_all()
import gevent

import os
import os.path as op
import unittest
import shutil

import mox
import jarvis.server.broker as broker
import jarvis.utils.conf as conf


this_dir = op.dirname(__file__)
data_dir = op.join(this_dir, "data")
tmp_dir = op.join(this_dir, "tmp")

class TestJarvisServerBroker(unittest.TestCase):
    def setUp(self):
        conf.load("jarvis", defaults = {"REDIS_DB":10})

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

    def tst_basic_subscribe(self, broker):
        sub = broker.subscriber()
        sub.subscribe("test_channel")
        for s in sub:
            return s
        
        
    def tst_basic_publish(self, broker):
        pub = broker.publisher()
        pub.publish("test_channel", {"a":"b"})
        return "OK"
    
    def test_basic(self):
        # TODO
        b = broker.Broker()
        
        sublet = gevent.Greenlet.spawn(self.tst_basic_subscribe, b)
        publet = gevent.Greenlet.spawn(self.tst_basic_publish, b)

        jobs = [sublet, publet]
        gevent.joinall(jobs, timeout=2)

        ret = [job.value for job in jobs]
        self.assertEquals(ret,  [('test_channel', {u'a': u'b'}), 'OK'])
        
    
    def tearDown(self):
        self.mox.UnsetStubs()
        
        try:
            shutil.rmtree(tmp_dir, True)
        except:
            pass

        
def main():
    prefix = "test_"
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJarvisServerBroker)
    suite = filter(lambda x : str(x).startswith(prefix), suite)
    suite = unittest.TestLoader().suiteClass(suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
#    testunit_result(result)

if __name__ == "__main__":
    main()
    
