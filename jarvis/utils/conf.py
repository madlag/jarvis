import copy
import traceback
import os
import os.path
import errno

# Reserved settings names
RESERVED_NAMES = (
)

class _DummyContainer(object):
    pass

class Conf:
    """This object is responsible for reading configuration files that are written in python."""
    def __init__(self, pathes, defaults):
        # The list of places to look for configuration
        self.pathes = pathes
        # Default values for configuration
        self.defaults = defaults
        # Bare container for configuration
        self.container = _DummyContainer()
        # Then read configuration
        self.read()

    def valid_key(self, key):
        """Check if configuration key is valid"""
        if key.startswith("__") and key.endswith("__"):
            return False
        else:
            return True
        
    def set_key_value(self, key, value):
        """Set a new key in configuration"""
        if self.valid_key(key):
            setattr(self.container, key, value)        

    def read(self):
        """Read the configuration files after reading the defaults"""
        for key,value in self.defaults.iteritems():
            self.set_key_value(key, value)

        # Enumerate the pathes
        for p in self.pathes:
            try:
                data = {}
                s = execfile(p, data)
                # Set the keys, values from this configuration file
                for key, value in data.iteritems():
                    self.set_key_value(key, value)            
            except IOError, e:
                # Raise 
                if e.errno != errno.ENOENT:
                    raise

    def __getattr__(self, key):
        if self.valid_key(key):
            return getattr(self.container, key)
        else:
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, key))

    def __hasattr__(self, key):
        if self.valid_key(key):
            return hasattr(self.container, key)
        else:
            return False            
    
def load(name, pathes = None, defaults = {}):
    if pathes == None:
        pathes = []
        pathes += ["/etc/%s/conf.py" % name]
        pathes +=  [os.path.join(os.getenv("HOME"), "." + name + ".d", "conf.py")]
    else:
        pathes = copy.deepcopy(pathes)
    globals()[name] = Conf(pathes, defaults = defaults)
    
