import os
import os.path
import sys
import time
import traceback
from PyQt4 import QtCore
import jarvis
import rollbackimporter
import imp
import errno
import tracer

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
        self.module = None

        self.rollbackImporter = rollbackimporter.RollbackImporter()
        self.watchfiles = {}
        # This flag says if last test was runned or not yet finished
        self.run_finished = True
        # Used to debug vars
        self.tracer = None
        self.file_dates = {}
        self.trace_file_white_list = {}
        # Set this flag to True to ask for a new run (True for the first run !)
        self.force_run = True

    def add_watch_file(self, filename):
        self.watchfiles[filename] = True

    def setdisplay(self, display):
        self.display = display

    def checkreloadfile(self, filename):
        modified = False
        try:
            filedate = os.path.getmtime(filename)
            self.watchfiles[filename] = True
            checkedfile = filename
        except OSError:
            return False, None

        old_file_date = self.file_dates.get(filename)

        if old_file_date != None and old_file_date != filedate:
            modified = True

        self.file_dates[filename] = filedate

        return modified, checkedfile

    def checkreloadmodule(self, module):
        checkedfiles = []
        if not hasattr(module, "__file__"):
            return False, []

        filename = module.__file__

        if filename == None:
            return False, []

        if filename.endswith(".pyc"):
            filename = filename[:-1]

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
        entry_point = self.get_test_filename()
        try:
            self.module = imp.load_source("__mainjarvismodule__", entry_point)
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise Exception("The entry_point %s does not exist.", entry_point)

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

        # Check if any file was modified since last run
        modules = sys.modules.values()

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
                    print traceback.format_exc(e)

        for filename in self.watchfiles:
            if filename not in fullcheckedfiles:
                checkreload, checkedfile = self.checkreloadfile(filename)
                if checkreload:
                    modified = True
                    break


        return modified

    def start_run(self):
        self.run_finished = False

    def finish_run(self):
        self.run_finished = True

    def runcommand(self):
        if self.module != None:
            try:
                self.last_run = time.time()
                fun = getattr(self.module, self.get_test_fun_name())
                self.tracer = tracer.Tracer(self.trace_file_white_list)
                self.tracer.install()
                fun()
                self.tracer.uninstall()
                # Reset trace so it is recomputed
                self.trace_file_date = None
            except Exception, e:
                print traceback.format_exc(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.display.errorprint("%s:%s\n" % (fname, exc_tb.tb_lineno) + traceback.format_exc(e) + "\n")
            finally:
                # We are sure we have run code that was up to date = self.new_check_timestamp
                self.finish_run()


    def inspect_vars(self, file, line):
        if self.tracer == None:
            return None
        else:
            return self.tracer.inspect(file, line)

    def singleRun(self):
        if self.display != None:
            self.display.runcommand(self.runcommand)


    def runloop(self):
        if not self.run_finished:
            return

        modified_force = self.force_run
        # Reset force_run
        self.force_run = False
        modified = modified_force

        module_changed = self.modulechanged()

        if module_changed:
            # The tested module changed, so we reset the set of files to be traced
            self.trace_file_white_list = {}
            self.display.reset()

        modified = modified or module_changed

        modified_single = self.singlePrepare()

        modified = modified or modified_single

        if not modified:
            self.finish_run()
            return

        self.loadMainModule()
        self.display.reset()

        self.start_run()

        self.display.start()

        if self.rollbackImporter:
            self.rollbackImporter.cleanup(self.display)

        self.singleRun()


    def trace_query_check_write(self, query_string, content):
        filename = jarvis.get_filename(jarvis.INSPECT_VAR_QUERY_RESPONSE)
        f = open(filename, "w")
        f.write(query_string + "\n")
        f.write(content + "\n")
        f.close()

    def trace_query_check(self):
        if self.tracer == None:
            return

        filename = jarvis.get_filename(jarvis.INSPECT_VAR_QUERY)

        # Check date of trace file, not to redo work for nothing
        if not os.path.exists(filename):
            return

        filedate = os.path.getmtime(filename)
        if hasattr(self, "trace_file_date") and filedate == self.trace_file_date:
            return

        try:
            query_string = open(filename).read()
            query = query_string.split()
            line = query[0]
            file = query[1]
        except:
            return None

        if not self.tracer.istracing(file):
            self.trace_file_white_list[file] = True
            # Force a new run !!
            self.force_run = True
            return

        ret = self.tracer.inspect(file, int(line))
        if ret == None:
            self.trace_query_check_write(query_string, "Function was not executed")
            return

        # The check was successful, so we can set the date
        self.trace_file_date = filedate

        new_ret = []
        for time,d in ret:
            new_ret += [[time, {}]]
            for k,v in d.iteritems():
                new_ret[-1][1][k] = [v[0], str(v[1])]
        ret = new_ret

        self.trace_query_check_write(query_string, str(ret))
#        self.trace_query.inspect_all()

    def run_(self):
        while(not self.finished):

            try:
                 self.runloop()
            except:
                self.finish_run()
                print traceback.format_exc()
                if self.display != None:
                    self.display.start()
                    self.display.errorprint(traceback.format_exc())
                    self.display.finish()

            try:
                self.trace_query_check()
            except:
                print traceback.format_exc()

            time.sleep(0.1)

    def run(self):
        # Write the current module name to disk
        testmodulepath = os.path.join(jarvis.get_home(), jarvis.TEST_FILENAME_FUNCTION)
        if self.filename_function != None:
            f = open(testmodulepath, "w")
            f.write(self.filename_function)
            f.close()

        try:
            self.run_()
        except KeyboardInterrupt:
            pass
        except Exception, e:
            print traceback.format_exc(e)
