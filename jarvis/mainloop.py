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
        
    def _import(self, name, globals=None, locals=None, fromlist=[], level = -1):
        # Apply real import
        result = apply(self.realImport, (name, globals, locals, fromlist))

#        print "name = ", name, result.__name__
        if len(name) <= len(result.__name__):
           name = copy.copy(result.__name__)

        black_list = ["streaming_httplib2", "stashy", "numpy", "sys", "lxml", "htmlrenderer"]
        black_list = ["stashy"]
        
        for b in black_list:
            if b in name:
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
                reload(sys.modules[name])
            except Exception, e:
                pass
#                print "ERROR on ", traceback.format_exc(e), name
#        self.newModules = []
                
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
        self.debug_window.clear()

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
        self.watchfiles = {}
        # This flag says if last test was runned or not yet finished
        self.run_finished = True

    def setdisplay(self, display):
        self.display = display

    def checkreloadfile(self, filename):
#        debug = "test_" in filename

        modified = False
        try:
            filedate = os.path.getmtime(filename)
            self.watchfiles[filename] = True
            checkedfile = filename
        except OSError:
            return False, None

        lastdate = self.filedates.get(filename)

#        if debug:
#            print "lastdate", lastdate, "filedate", filedate
            
        if lastdate == None:
            lastdate = filedate
        elif lastdate < filedate:
            lastdate = filedate
            modified = True
#            print "MODIFIED"
            
        self.filedates[filename] = lastdate            

        return modified, checkedfile


    def checkreloadmodule(self, module):
        checkedfiles = []
        if not hasattr(module, "__file__"):
            return False, []
        
        filename = module.__file__

        if filename == None:
            return False, []
#        if "common" in filename:
#        print "checkreloadmodule", filename

        if filename.endswith(".pyc"):
            filename = filename[:-1]

#        if "test_" in filename:
#            print "HERE !!"

        modified = False
        for suffix in [""]:
            localModified, checkedfile = self.checkreloadfile(filename + suffix)
            modified = modified or localModified
            if checkedfile != None:
                checkedfiles += [checkedfile]
                            
        return modified, checkedfiles

    def loadMainModule(self):
        modName = self.module_function_name
        modNameParts = modName.split(".")
        mod = __import__(".".join(modNameParts[:-1]))

#        print "FOUND", "test_" in sys.modules.keys()
        for p in modNameParts[1:-1]:            
            mod = getattr(mod, p)
        self.module = mod
#        reload(self.module)
        
    def singlePrepare(self):            
        modified = False
        self.daemon = True
        # Check if any file was modified since last run

        modules = sys.modules.values()

#        print "is there", "test_" in sys.modules.keys()
#        print "\n".join(sys.modules.keys())
        fullcheckedfiles = {}
                
        for m in modules:
            if m != None:
                try:
                    checkreload, checkedfiles = self.checkreloadmodule(m)
                    for filename in checkedfiles:
                        fullcheckedfiles[filename] = True
                    modified = modified or checkreload
                    if modified:
                        break
                except Exception, e:                    
#                    pass
                    print traceback.format_exc(e)
                    print e.__class__.__name__

        for filename in self.watchfiles:
#            if "test_" in filename:
#                print filename, filename in fullcheckedfiles
            
            if filename not in fullcheckedfiles:
                checkreload, checkedfile = self.checkreloadfile(filename)
                if checkreload:
                    modified = True
                    break
                    

        return modified

    def runcommand(self):
        fun = getattr(self.module, self.module_function_name.split(".")[-1])
        fun()
        self.run_finished = True
        
    def singleRun(self):
        if self.display != None:
            self.display.runcommand(self.runcommand)

    def runloop(self):
        if not self.run_finished:
            return

        if self.module == None:
            first = True
        else:
            first = False
            
        self.loadMainModule()

        modified = self.singlePrepare()
        
        if not first:
            if not modified:                
                return

        self.run_finished = False
        
        if self.rollbackImporter:
            self.rollbackImporter.cleanup()


        self.display.clear()
        try:
            self.singleRun()
            self.display.errorprint("")                
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
            time.sleep(2.0)
                                                
    def run(self):
        try:
            a = self.run_()
        except KeyboardInterrupt:
            pass
        except Exception, e:
            print e
        


