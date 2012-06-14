import os
import os.path
import sys
import time
import traceback
from PyQt4 import QtCore
import jarvis
import rollbackimporter
import imp

class Display():
    def __init__(self):
        pass

    def init(self):
        pass

    def destroy(self):
        pass

    def start(self):
        pass
    
    def finish(self):
        pass

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        print "INFO", info

    def errorprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        print "INFO", info

        
class MainLoop(QtCore.QThread):
    def __init__(self, filename_function, display = None):
        QtCore.QThread.__init__(self)

        self.filename_function = filename_function
        self.finished = False
        self.display = display
        self.filedates = {}
        self.module = None
        
        self.rollbackImporter = rollbackimporter.RollbackImporter()
        self.watchfiles = {}
        # This flag says if last test was runned or not yet finished
        self.run_finished = True

    def add_watch_file(self, filename):
        self.watchfiles[filename] = True

    def setdisplay(self, display):
        self.display = display

    def checkreloadfile(self, filename):
#        debug = "lizard" in filename
#        if debug:
#            print filename
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

    def get_test_filename(self):
        parts = self.filename_function.split(":")
        return parts[0]
    
    def get_test_fun_name(self):
        parts = self.filename_function.split(":")
        filename = parts[0]
        if len(parts) > 1:
            function_name = parts[1]
        else:
            function_name = "main"
        return function_name
        
    def loadMainModule(self):            
        mod = imp.load_source("__module__" + str(time.time()).replace(".", "_"), self.get_test_filename())

        self.module = mod

    def modulechanged(self):
        # Check that main module has not changed
        test_filename_function_path = os.path.join(jarvis.get_home(), jarvis.TEST_FILENAME_FUNCTION)
        
        test_filename_function = open(test_filename_function_path).read()
        if test_filename_function != self.filename_function:
            self.filename_function = test_filename_function
            return True
        return False

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
        fun = getattr(self.module, self.get_test_fun_name())
        try:
            fun()
        except Exception, e:
            print traceback.format_exc(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.display.errorprint("%s:%s\n" % (fname, exc_tb.tb_lineno) + traceback.format_exc(e) + "\n")
        finally:
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

        modified = self.modulechanged()
            
        self.loadMainModule()

        modified = modified or self.singlePrepare()
        
        if not first:
            if not modified:                
                return

        self.run_finished = False

        self.display.start()

        if self.rollbackImporter:
            self.rollbackImporter.cleanup(self.display)


        self.singleRun()
                
    def run_(self):
        while(not self.finished):
            try:
                self.runloop()
            except Exception, e:
                print traceback.format_exc(e)
                if self.display != None:
                    self.display.start()
                    self.display.errorprint(traceback.format_exc(e))
                    self.display.finish()
            time.sleep(0.5)
                                                
    def run(self):
        # Write the current module name to disk
        testmodulepath = os.path.join(jarvis.get_home(), jarvis.TEST_FILENAME_FUNCTION)
        f = open(testmodulepath, "w")
        f.write(self.filename_function)
        f.close()        

        try:
            self.run_()
        except KeyboardInterrupt:
            pass
        except Exception, e:
            print traceback.format_exc(e)
        


