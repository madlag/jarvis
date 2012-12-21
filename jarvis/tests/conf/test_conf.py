import os
import os.path as op
import unittest
import shutil

import mock 
import mox
import jarvis.utils.conf as conf
from jarvis.commands import *

this_dir = op.dirname(__file__)
data_dir = op.join(this_dir, "data")
tmp_dir = op.join(this_dir, "tmp")

class TestConf(unittest.TestCase):
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
    
    def get_test_file_name(self, filename):
        return op.join(tmp_dir, filename)

    def test_main(self):
        o = conf.Conf([self.data_file_name("serverconf.py")], {})
        self.assertTrue(o.a == "b")
        self.assertTrue(o.c == "bbbb")

    def test_load(self):
        conf.load("jarvis", pathes=[self.data_file_name("serverconf.py")])
        self.assertTrue(conf.jarvis.a ==  "b")
        self.assertTrue(conf.jarvis.c ==  "bbbb")

    def test_bad_load(self):
        with self.assertRaises(NameError):
            conf.load("jarvis", pathes= [self.data_file_name("serverconf_bad.py")])
        
    def tearDown(self):
        self.mox.UnsetStubs()
        
        try:
            shutil.rmtree(tmp_dir, True)
        except:
            pass

        
def main():
    prefix = "test_"
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConf)
    suite = filter(lambda x : str(x).startswith(prefix), suite)
    suite = unittest.TestLoader().suiteClass(suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    testunit_result(result)
