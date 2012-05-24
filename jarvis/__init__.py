# Example package with a console entry point
import os
import argparse
import traceback
from lxml import etree
import sys

ml = None

TEST_MODULE_PATH="testmodule.txt"

def get_home():
    jarvis_home = os.getenv("JARVIS_HOME", "/tmp/jarvis")
    try:
        os.makedirs(jarvis_home)
    except OSError, e:
        if e.errno != 17:
            raise
        
    return jarvis_home


def run(modulename):
    global ml
    import qtdisplay
    import mainloop

    try:
        ml = mainloop.MainLoop(modulename)
        
        display = qtdisplay.QTDisplay(ml)
        print "TEST1", display
        ml.setdisplay(display)
        print "TEST2"

        display.launch()
        
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print traceback.format_exc(e)
    finally:
        display.finish()    
        

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--nogl", default=False, action="store_true", help="disable gl window")
    parser.add_argument("--module", metavar="NAME")

    args = parser.parse_args()
    run(args.module)

def debug(*args):
    try:
        global ml
        ml.display.debugprint(*args)
    except Exception, e:
        print traceback.format_exc(e)
        pass

def error(*args):
    try:
        global ml
        d = " ".join(map(lambda x: str(x), args))
#        d = d.split("\n")
#        d.reverse()
#        d = "\n".join(d)
        ml.display.errorprint(d)
    except Exception, e:
        print traceback.format_exc(e)
        pass

def debug_dir(object, filt = None):
    debug("debug_dir", object, filt)   
    for k in dir(object):        
        if filt == None or filt in k.lower():
            debug(k)    

def debug_xml(*args):
    debug(*(list(args[:-1]) + [etree.tostring(args[-1], pretty_print = True)]))

def show(osgdata):
    try:
        global ml
        ml.display.osgprint(osgdata)
    except Exception, e:
        print traceback.format_exc(e)
        pass

    return

def get_osg_viewer():
    global ml
    return ml.display.get_osg_viewer()

def setlooptime(loop_time):
    try:
        global ml
        ml.display.setlooptime(loop_time)
    except Exception, e:
        print traceback.format_exc(e)
        pass

    return

def testunit_result(result):
    for err in result.errors:
        print err
        error(err[1])
        break
    

if __name__ == "__main__":
    main()

