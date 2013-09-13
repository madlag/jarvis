import jarvis
import inspect
import os
import time
import jarvis.client as client

def set_test_filename_function(test_filename_function):
    """Set the module.function that jarvis watches for changes and then executes."""
    # Get the jarvis home directory
    jarvis_home = jarvis.get_home()

    # Find the file that holds the current module.function to test
    testmodulefilename = os.path.join(jarvis_home, jarvis.TEST_FILENAME_FUNCTION)

    # Write the file
    f=open(testmodulefilename, "w")
    f.write(test_filename_function)
    f.close()

start_time = time.time()
def delta_time_format():
    global start_time
    return str(time.time() - start_time)[:6] + "s"

def error(*args):
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.errorprint(delta_time_format(), *args)
    print " ".join(args)

def reset_start_time():
    global start_time
    start_time = time.time()

def display_reset():
    # TEMPORARY
    client.Client().update("debug", "set", "")

def debug(*args):
    msg = " ".join(map(lambda x : str(x), args))

    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.debugprint(delta_time_format(), *args)

#    print client.Client().update("debug", "append", msg + "<br/>")

def debug_dir(object, filt = None):
    debug("debug_dir", object, filt)
    for k in dir(object):
        if filt == None or filt in k.lower():
            debug(k)
def debug_xml(*args):
    import lxml
    debug(*(list(args[:-1]) + [lxml.etree.tostring(args[-1], pretty_print = True)]))

def debug_osg(osgdata):
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.osgprint(osgdata)

def debug_audio(audiodata, skip = 0.0):
    if jarvis.ml != None and jarvis.ml.display != None:
        jarvis.ml.display.audioemit(audiodata, skip)

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


MAX_INSPECT_ELAPSED = 10
def external_inspect_vars(file_name, line_number):
    filename = jarvis.get_filename(jarvis.INSPECT_VAR_QUERY)
    f = open(filename, "w")
    query = "%s %s" % (line_number, file_name)
    f.write(query)
    f.close()
    start = time.time()
    elapsed = 0
    while elapsed < MAX_INSPECT_ELAPSED:
        try:
            filename = jarvis.get_filename(jarvis.INSPECT_VAR_QUERY_RESPONSE)
            r = open(filename).read()
            if r.split("\n")[0] == query:
                return r
        except IOError:
            pass

        elapsed = time.time() - start


