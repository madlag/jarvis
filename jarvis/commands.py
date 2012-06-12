import jarvis
import inspect
from lxml import etree
import os

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
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.errorprint(*args)
    
def debug(*args):
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.debugprint(*args)

def debug_dir(object, filt = None):
    debug("debug_dir", object, filt)   
    for k in dir(object):        
        if filt == None or filt in k.lower():
            debug(k)    

def debug_xml(*args):
    debug(*(list(args[:-1]) + [etree.tostring(args[-1], pretty_print = True)]))

def debug_osg(osgdata):
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.osgprint(osgdata)

def debug_osg_set_loop_time(loop_time):
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.setlooptime(loop_time)
        
def testunit_result(result):
    for err in result.errors:
        error(err[1])
    for err in result.failures:
        error(err[1])

def get_osg_viewer():
    if jarvis.ml != None and jarvis.ml.display != None:
        return jarvis.ml.display.getosgviewer()

def add_watch_file(filename):
    if jarvis.ml != None:
        return jarvis.ml.add_watch_file(filename)

def replace_this(*args):
    if len(args) == 0:
        raise Exception("jarvis.commands.replace_this: Nothing to replace by")
    # Retrieve the calling frame
    frame = inspect.stack()[1]
    # Get the file name and the line_number
    file_name = frame[1]
    line_number = frame[2]
    # Split by line the source file
    lines = open(file_name).read().split("\n")
    # Retrieve the right line
    line = lines[line_number - 1]
    # Check that the source code is still matching
    inspect_line = frame[4][0][:-1]
    if line != inspect_line or "replace_this" not in line:
        raise Exception("jarvis.commands.replace_this: looks like the file changed before replace could occur.")

    for i,c in enumerate(inspect_line):
        if c != " ":
            break
    # Build the replacement line
    replacement = " " * i + args[0] % args[1:]
    # Replace the line
    lines[line_number - 1] = replacement
    # Rebuild the file content
    file_content = "\n".join(lines)
    # Write back the file
    file = open(file_name, "w")
    file.write(file_content)
    file.close()    
