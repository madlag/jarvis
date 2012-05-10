# Example package with a console entry point
import sys

import mainloop
import sys
import traceback
import argparse
import qtdisplay
from PyQt4 import QtCore

ml = None

def main():

    try:
        global ml
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument("--nogl", default=False, action="store_true", help="disable gl window")
        parser.add_argument("--module", metavar="NAME")

        args = parser.parse_args()

        ml = mainloop.MainLoop(args.module)
        
        display = qtdisplay.QTDisplay(ml)

        ml.setdisplay(display)

        display.launch()

        
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print traceback.format_exc(e)
    finally:
        display.finish()    
        


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
        ml.display.errorprint(*args)
    except Exception, e:
        print traceback.format_exc(e)
        pass

def debug_dir(object, filt):
    debug("debug_dir", object, filt)   
    for k in dir(object):
        if filt in k.lower():
            debug(k)    

def show(osgdata):
    try:
        global ml
        ml.display.osgprint(osgdata)
    except Exception, e:
        print traceback.format_exc(e)
        pass

    return

def testunit_result(result):
    for err in result.errors:
        error(err[1])
        break
    

if __name__ == "__main__":
    main()
