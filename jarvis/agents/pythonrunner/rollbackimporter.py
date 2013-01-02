import sys
import __builtin__
import copy
import traceback

class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = []
        
    def _import(self, name, globals=None, locals=None, fromlist=[], level = -1):
        # Apply real import
        result = apply(self.realImport, (name, globals, locals, fromlist, level))

        if len(name) <= len(result.__name__):
           name = copy.copy(result.__name__)

        black_list = ["stashy", "unittest"] #, "sentry", "raven", "logging", "warnings"]
        
        for b in black_list:
            if b in name.lower():
                return result

        # Remember import in the right order
        if name not in self.previousModules:
            # Only remember once
            if name not in self.newModules:                            
                self.newModules += [name]
        return result

    def cleanup(self, display):
        for name in self.newModules:
            # Force reload when modname next imported
            try:
                reload(sys.modules[name])
            except TypeError:
                pass
            except Exception, e:
                display.errorprint("ERROR on ", traceback.format_exc(e), name)
#        self.newModules = []
                
    def uninstall(self):
        __builtin__.__import__ = self.realImport

