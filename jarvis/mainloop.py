import compileall
import sys
import curses
import time
import traceback
import os
import threading
from PyQt4 import QtCore

class Display():
    def __init__(self):
        pass

    def start(self):
        pass
    
    def finish(self):
        pass

    def clear(self):
        pass

    def validate(self):
        pass

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        print "INFO", info

    def errorprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        print "INFO", info


class CursesDisplay():
    def __init__(self):
        pass
    
    def start(self):
        self.stdscr = curses.initscr()
        
        begin_x = 0
        begin_y = 0
        height = 25
        width = 0
        self.status_window = curses.newwin(height, width, begin_y, begin_x)
        begin_y += height
        height = 100
        self.debug_window = curses.newwin(height, width, begin_y, begin_x)
            
    def finish(self):
        curses.nocbreak()
        self.status_window.keypad(0)
        curses.echo()
        curses.endwin()

    def clear(self):
        self.status_window.clear()
        self.status_window.addstr(0,0, "OK")
        self.debug_window.clear()
        self.debug_window.addstr(0,0, "")

    def validate(self):
        self.status_window.refresh()
        self.debug_window.refresh()

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        self.status_window.clear()
        self.debug_window.addstr(info)

    def errorprint(self, *args):        
        error = " ".join(map(lambda x: str(x), args)) + "\n"
        self.status_window.clear()
        self.status_window.addstr(error)

class MainLoop(QtCore.QThread):
    def __init__(self, module, display = None):
        QtCore.QThread.__init__(self)

        self.module_function_name = module
        self.finished = False
        self.display = display
        

    def setdisplay(self, display):
        self.display = display
        
    def single(self):
        modName = self.module_function_name
        modNameParts = modName.split(".")
        mod = __import__(".".join(modNameParts[:-1]))
        for p in modNameParts[1:-1]:
            mod = getattr(mod, p)
        self.module = mod
        self.daemon = True


        reload(self.module)
        fun = getattr(self.module, self.module_function_name.split(".")[-1])
        fun()            
    
    def run_(self):        
        while(not self.finished):
#            if self.viewer != None:
#                self.viewer.frameAtTime(0.0)

            self.display.clear()
            try:
                self.single()
                self.display.errorprint("OK")                
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.display.errorprint("%s:%s\n" % (fname, exc_tb.tb_lineno) + traceback.format_exc(e) + "\n")

            self.display.validate()
                
            time.sleep(0.3)
                        
        
    def run(self):
        try:
            a = self.run_()
        except KeyboardInterrupt:
            pass
        except Exception, e:
            self.display.debugprint(e)
            time.sleep(10)
        finally:
            self.display.finish()
        

