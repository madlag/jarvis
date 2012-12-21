from gevent import monkey;
monkey.patch_all()

import logging
import logging.config
import jarvis.utils.conf as conf
import frontend

#from stupeflix.conf import settings as dragon_settings
#import dragon.conf
#import dragon_front.conf


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


def main(**settings):
    """
    This function returns a Pyramid WSGI application.
    """
    listen()

    # Load dragon configuration
    conf.load("jarvis")

    # Setup logging
    #logging.config.dictConfig(jarvis.LOGGING)

    # Start the frontend greenlets and create the WSGI application
    _frontend = frontend.Frontend()
    _frontend.start(start_wsgi_server = True, forever = True)
