import os
import argparse
import traceback

ml = None

# This is the place where is stored the currently tested 'filename:function' .
TEST_FILENAME_FUNCTION="test_filename_function.txt"

# This is the file where errors produced by calls to jarvis.command.error are written.
ERROR_FILE="error.txt"
DEBUG_FILE="debug.txt"
INSPECT_VAR_QUERY="inspect_var_query.txt"
INSPECT_VAR_QUERY_RESPONSE="inspect_var_query_response.txt"

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

def run(filename_function, layout=None):
    global ml
    import qtdisplay
    import mainloop

    try:
        ml = mainloop.MainLoop(filename_function)

        display = qtdisplay.QTDisplay(ml, layout)
        ml.setdisplay(display)

        display.init()

    except KeyboardInterrupt:
        pass
    except Exception, e:
        print traceback.format_exc(e)
    finally:
        display.destroy()



import code, traceback, signal

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal recieved : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--nogl", default=False, action="store_true", help="disable gl window")
    parser.add_argument("--filename_function", metavar="NAME")
    parser.add_argument("--layout", metavar="LAYOUT", default=None)

    args = parser.parse_args()
    run(args.filename_function, args.layout)

if __name__ == "__main__":
    listen()
    main()


