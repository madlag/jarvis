import compileall
import sys
import curses
import time
import traceback
import os
import threading
from PyQt4 import QtCore
import os.path
import copy
import __builtin__
import inspect

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

class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = []
#        print "PREVIOUS", self.previousModules
        
    def _import(self, name, globals=None, locals=None, fromlist=[], level = 0):
        # Apply real import
        result = apply(self.realImport, (name, globals, locals, fromlist))
        
        if len(name) <= len(result.__name__):
           name = copy.copy(result.__name__)
                       
        if "lxml" in name:
            print result.__file__
            return result

        # Remember import in the right order
        if name not in self.previousModules:
            # Only remember once
            if name not in self.newModules:                            
                self.newModules += [name]
        return result

    def cleanup(self):
        for name in self.newModules:
            # Force reload when modname next imported
            try:
                del sys.modules[name]
            except Exception, e:
                print "ERROR on ", traceback.format_exc(e)
        self.newModules = []
                
    def uninstall(self):
        __builtin__.__import__ = self.realImport

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
        self.filedates = {}
        self.module = None
#        self.rollbackImporter = None

        modName = self.module_function_name
        modNameParts = modName.split(".")
        self.module_name = ".".join(modNameParts[:-1])
        
        self.rollbackImporter = RollbackImporter()

    def setdisplay(self, display):
        self.display = display

    def checkreloadmodule(self, module):
        if not hasattr(module, "__file__"):
            return False
        
        filename = module.__file__

#        if "common" in filename:
#        print "checkreloadmodule", filename

        if filename.endswith(".pyc"):
            filename = filename[:-1]

        maxdate = None
        modified = False
        for suffix in ["", "c"]:
            filedate = os.path.getmtime(filename + suffix)
            if maxdate == None or maxdate < filedate:
                maxdate = filedate

            if filename in self.filedates:
                if filedate > self.filedates[filename]:
                    modified = True
            
        if maxdate != None:
            self.filedates[filename] = maxdate
                            
        return modified

    def loadMainModule(self):
        modName = self.module_function_name
        modNameParts = modName.split(".")
        mod = __import__(".".join(modNameParts[:-1]))
        for p in modNameParts[1:-1]:            
            mod = getattr(mod, p)
        self.module = mod
        reload(self.module)
        
    def singlePrepare(self):            
        modified = False
        self.daemon = True
        # Check if any file was modified since last run
        for mname, m in sys.modules.iteritems():
            if m != None:
                try:
                    checkreload = self.checkreloadmodule(m)
                    modified = modified or checkreload
                except OSError, e:
                    pass
                except Exception, e:                    
#                    pass
                    print e
                    print e.__class__.__name__

        return modified
        
    def singleRun(self):
        fun = getattr(self.module, self.module_function_name.split(".")[-1])
        fun() 

    def rel(self, modulename):
        try:
            del sys.modules[modulename]
            reload(sys.modules[modulename])
        except:
            pass

    def runloop(self):
        modified = self.singlePrepare()
        if self.module != None:
            if not modified:                
                return

        if self.rollbackImporter:
            self.rollbackImporter.cleanup()

        if False:
            self.rel("stupeflix.osgengine.osg")
            self.rel("stupeflix.osgengine.osgDB")
            self.rel("stupeflix.osgengine.osgStupeflix")
            self.rel("stupeflix.osgengine.common")
            self.rel("stupeflix.osgengine.shaders")
            self.rel("stupeflix.osgengine.filter")
            self.rel("stupeflix.osgengine.image")
            self.rel("stupeflix.osgengine.overlay")
            
        self.loadMainModule()
            
        self.display.clear()
        try:
            self.singleRun()
            self.display.errorprint("OK")                
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.display.errorprint("%s:%s\n" % (fname, exc_tb.tb_lineno) + traceback.format_exc(e) + "\n")

        self.display.validate()
                
    def run_(self):        
        while(not self.finished):
            try:
                self.runloop()
            except Exception, e:
                if self.display != None:
                    self.display.clear()
                    self.display.errorprint(traceback.format_exc(e))
                    self.display.validate()
            time.sleep(0.3)
                
                        
        
    def run(self):
        try:
            a = self.run_()
        except KeyboardInterrupt:
            pass
        except Exception, e:
            print e
        

