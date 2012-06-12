import os
import argparse
import traceback

ml = None

# This is the place where is stored the currently tested 'module.function' .
TEST_MODULE_PATH="testmodule.txt"

# This is the file where errors produced by calls to jarvis.command.error are written.
ERROR_FILE="error.txt"
DEBUG_FILE="debug.txt"

def get_home():
    jarvis_home = os.getenv("JARVIS_HOME", "/tmp/jarvis")
    try:
        os.makedirs(jarvis_home)
    except OSError, e:
        if e.errno != 17:
            raise
        
    return jarvis_home

def get_filename(key):
    error_file = os.path.join(get_home(), key)    
    return error_file

def run(modulename, layout=None):
    global ml
    import qtdisplay
    import mainloop

    try:
        ml = mainloop.MainLoop(modulename)

        display = qtdisplay.QTDisplay(ml, layout)
        ml.setdisplay(display)

        display.init()
        
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print traceback.format_exc(e)
    finally:
        display.destroy()
        

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--nogl", default=False, action="store_true", help="disable gl window")
    parser.add_argument("--module", metavar="NAME")
    parser.add_argument("--layout", metavar="LAYOUT", default=None)

    args = parser.parse_args()
    run(args.module, args.layout)

if __name__ == "__main__":
    main()

from commands import *

def coucou():
    a = 4
