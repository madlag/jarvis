import os
import os.path as op
import unittest
import shutil

import {{module}} as {{shortmodule}}
import urllib2
import mock 
import mox

this_dir = op.dirname(__file__)
data_dir = op.join(this_dir, "data")
tmp_dir = op.join(this_dir, "tmp")

class Test{{TestClassName}}(unittest.TestCase):
    def setUp(self):
        # Refresh the temporary directory
        try:
            shutil.rmtree(tmp_dir, True)
        except:
            pass
        os.makedirs(tmp_dir)
        self.mox = mox.Mox()
        
    def dataFilename(self, filename):
        return op.join(data_dir, filename)

    def fun_basic(self, filename, ref):
        self.mox.StubOutWithMock(urllib2, "urlopen")

        videoFileName = self.dataFilename(filename)
        videoFile = open(videoFileName)

        url = "http://stupeflix-tmp.s3.amazonaws.com/%s" % filename
        urllib2.urlopen(url, None).AndReturn(videoFile)

        # Activate mocks
        self.mox.ReplayAll()

        store_method = {{shortmodule}}.{{ClassName}}.store
        # Mock the store function
        {{shortmodule}}.{{ClassName}}.store = mock.Mock()
        Runner = {{shortmodule}}.{{ClassName}}(host="https://dummy.com", secret="dummy")
        taskRunner.debug = True
        taskRunner.path  = tmp_dir

        task = {"url":url, "video_br":"1024k"}
        ret = taskRunner.run(**task)
                      
        self.assertEqual(ret, ref)

        output = os.path.join(tmp_dir, 'out.tmp')
        convertInfo = (('out.mp4',), {'mimeType': 'video/mp4', 'filename': output})
        self.assertEqual({{shortmodule}}.{{ClassName}}.store.call_args, convertInfo)

        videoRefFilename = self.dataFilename("convert/%s.ref.mov" % filename)
        if not op.exists(videoRefFilename):                            
            shutil.copy(output, videoRefFilename)

        a = open(videoRefFilename).read()
        b = open(output).read()

        self.assertEqual(a,b)
        self.mox.VerifyAll()        

        # Reset the store function to its initial value
        {{shortmodule}}.{{ClassName}}.store = store_method


    def test_main(self):
        # TODO
        o = {{shortmodule}}.{{ClassName}}()
        
    def tearDown(self):
        self.mox.UnsetStubs()

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(Test{{TestClassName}})
    suite = filter(lambda x : str(x).startswith("test_"), suite)
    suite = unittest.TestLoader().suiteClass(suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    testunit_result(result)

    
if __name__=="__main__":
    main()
