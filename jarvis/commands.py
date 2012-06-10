import jarvis
from lxml import etree
import os

ml = jarvis.ml

def set_test_module(test_module):
    """Set the module.function that jarvis watches for changes and then executes."""
    # Get the jarvis home directory
    jarvis_home = jarvis.get_home()

    # Find the file that holds the current module.function to test
    testmodulefilename = os.path.join(jarvis_home, jarvis.TEST_MODULE_PATH)

    # Write the file
    f=open(testmodulefilename, "w")
    f.write(test_module)
    f.close()

def error(*args):
    global ml
    if ml != None and ml.display != None:
        ml.display.errorprint(*args)
    
def debug(*args):
    global ml
    if ml != None and ml.display != None:
        ml.display.debugprint(*args)

def debug_dir(object, filt = None):
    debug("debug_dir", object, filt)   
    for k in dir(object):        
        if filt == None or filt in k.lower():
            debug(k)    

def debug_xml(*args):
    debug(*(list(args[:-1]) + [etree.tostring(args[-1], pretty_print = True)]))

def debug_osg(osgdata):
    global ml
    if ml != None and ml.display != None:
        ml.display.osgprint(osgdata)

def debug_osg_set_loop_time(loop_time):
    global ml
    if ml != None and ml.display != None:
        ml.display.setlooptime(loop_time)
        
def testunit_result(result):
    for err in result.errors:
        error(err[1])
    for err in result.failures:
        error(err[1])

def get_osg_viewer():
    global ml
    if ml != None and ml.display != None:
        return ml.display.getosgviewer()

def add_watch_file(filename):
    global ml
    if ml != None:
        return ml.add_watch_file(filename)

