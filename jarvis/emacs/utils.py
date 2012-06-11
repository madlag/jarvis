import os.path
import jinja2
import imp
import time
import jarvis.emacs as emacs

dirname = os.path.dirname(os.path.abspath(__file__))
snippetdirnames = []

snippetdirnames = emacs.get_dirs("snippets")

def get_snippet_dir_names():
    return snippetdirnames
    
def load_snippet(commandname, **kwargs):
    for snippetdirname in snippetdirnames:        
        commandfilename = os.path.join(snippetdirname, commandname + ".py")
        if os.path.exists(commandfilename):
            break
    s = open(commandfilename).read()
    
    template = jinja2.Template(s)
    
    s = template.render(**kwargs)

    return s


# Find the "tests" directory
def find_tests_path(filename):
    new_directory = filename
    test_path = None
    while(True):
        old_directory = new_directory
        test_path_try = os.path.join(new_directory, "tests")
        if os.path.exists(test_path_try) and os.path.isdir(test_path_try):
            test_path = test_path_try
            break

        new_directory = os.path.abspath(os.path.join(new_directory, ".."))

        if new_directory == old_directory:
            break
    return test_path


def find_module_name(filename):
    basename = os.path.basename(filename) 
    if basename == "__init__.py":
        module_name = []
    else:
        module_name = [basename[:-3]]

    current_dir = os.path.dirname(filename)
        
    while(True):
        old_current_dir = current_dir
        initfile = os.path.join(current_dir, "__init__.py")
        if os.path.exists(initfile):
            module_name = [os.path.basename(current_dir)] + module_name            
        else:
            break

        current_dir = os.path.abspath(os.path.join(current_dir, ".."))

        if current_dir == old_current_dir:
            break
    return ".".join(module_name)

def load_module_by_filename(filename):
    return imp.load_source("entrypoint" + str(time.time()).replace(".", "_"), filename)

def create_init_files(filename):
    current_dir = os.path.dirname(filename)
        
    while(True):
        old_current_dir = current_dir
        initfile = os.path.join(current_dir, "__init__.py")
        if os.path.exists(initfile):
            break
        else:
            f = open(initfile, "w")
            f.close()

        current_dir = os.path.abspath(os.path.join(current_dir, ".."))

        if current_dir == old_current_dir:
            break

def module_load_source(filename):
    import imp
    name = "entrypoint" + str(time.time()).replace(".", "_")

    pyc_filename = filename + "c"
    if os.path.exists(pyc_filename) and filename.endswith(".py"):
        os.remove(pyc_filename)

    mod = imp.load_source(name, filename)
    return mod
        
def find_class_names(filename):
    import inspect
    
    class_names = []
    # Load the module
    f = module_load_source(filename) 

    # Enumerate the classes in the module
    for k in dir(f):
        # Get the task class
        cl = getattr(f, k)
        if inspect.isclass(cl):
            class_names  += [cl.__name__]

    return class_names
