import os
import os.path as op
import unittest
import shutil

import stupeflix.lizard.tasks.{{taskmodule}} as {{shorttaskmodule}}
import urllib2
import mock 
import mox

this_dir = op.dirname(__file__)
data_dir = op.join(this_dir, "data")
tmp_dir = op.join(this_dir, "tmp")

class Test{{TaskClassName}}(unittest.TestCase):
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

        store_method = {{shorttaskmodule}}.{{TaskClassName}}.store
        # Mock the store function
        {{shorttaskmodule}}.{{TaskClassName}}.store = mock.Mock()
        taskRunner = {{shorttaskmodule}}.{{TaskClassName}}(host="https://dummy.com", secret="dummy")
        taskRunner.debug = True
        taskRunner.path  = tmp_dir

        taskRunner.taskInfo = {"task":{"video_br":str(video_br)}}
        ret = taskRunner.run(url)
                      
        self.assertEqual(ret, ref)

        output = os.path.join(tmp_dir, 'out.tmp')
        convertInfo = (('out.mp4',), {'mimeType': 'video/mp4', 'filename': output})
        self.assertEqual({{shorttaskmodule}}.{{TaskClassName}}.store.call_args, convertInfo)

        videoRefFilename = self.dataFilename("convert/%s.ref.mov" % filename)
        if not op.exists(videoRefFilename):                            
            shutil.copy(output, videoRefFilename)

        a = open(videoRefFilename).read()
        b = open(output).read()

        self.assertEqual(a,b)
        self.mox.VerifyAll()        

        # Reset the store function to its initial value
        {{shorttaskmodule}}.{{TaskClassName}}.store = store_method
        
    def tearDown(self):
        self.mox.UnsetStubs()



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(Test{{TaskClassName}})
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print result

    
if __name__=="__main__":
    main()
