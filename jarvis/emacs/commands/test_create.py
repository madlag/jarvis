from Pymacs import lisp
import jarvis.emacs.utils as utils
import os.path
import os

reload(utils)

"""
Launch this command in a given  code buffer, it will create the test with it
"""

# Retrieve current buffer file name
filename = lisp.buffer_file_name()

# Find the test path
test_path = utils.find_tests_path(filename)

# Find the module_name
module_name = utils.find_module_name(filename)

# If not found, ask the user for a directory
if test_path == None:
    test_path = os.path.join(os.path.dirname(filename), "tests")
    test_path = lisp.read_file_name("Where should I create the 'tests' directory ?", test_path)

# Find the point where tests and current file names diverge
BASE = os.path.abspath(os.path.join(test_path, ".."))

# Try to infer the small name for the module and so the test file name
if filename.startswith(BASE):
    parts = filename[len(BASE) + 1:-3].split("/")
    testfilename = os.path.join(test_path, "_".join(parts), "test_" + "_".join(parts) + ".py")
else:
    testfilename = lisp.read_file_name("Where should I create this test ?", os.path.join(test_path, "test.py") )

# Create the test directory
try:
    os.makedirs(os.path.dirname(testfilename))
except OSError, e:
    # Directory exists ?
    if e.errno != 17:
        raise


utils.create_init_files(testfilename)
            
# Test if the test file name exists
if os.path.exists(testfilename) and False:
    lisp.message("Test %s already exists" % testfilename)
else:
    # Find the snippets that starts with test_ and finish by _create.py

    snippetdirnames = utils.get_snippet_dir_names()
    tests = []
    for snippetdirname in snippetdirnames:    
        tests += [t for t in os.listdir(snippetdirname)]
        
    tests = filter(lambda x: x.startswith("test_") and x.endswith("_create.py"), tests)
    tests = map(lambda x:x[5:-10], tests)

    # Ask for the kind of test to create
    testtypename = lisp.completing_read("What kind of test do you want to create ?", tests)
    if testtypename == None or len(testtypename) == 0:
        testtypename = "simple"

    # Create the test filename
    f = open(testfilename, "w")

    # Find the variable names 
    module = module_name
    shortmodule = module_name.split(".")[-1]
    testclassname = "".join(map(lambda x: x.capitalize(), module_name.split(".")))

    class_names = utils.find_class_names(filename)

    if len(class_names) != 1:
        # Ask for the kind of test to create
        class_name = lisp.completing_read("For which class do you want to create a test ?", class_names)
    else:
        class_name = class_names[0]

    # Run the snippet
    TESTBASE = utils.load_snippet("test_%s_create" % testtypename, module= module, shortmodule = shortmodule, ClassName = class_name, TestClassName = testclassname)
    # Write it into the file
    f.write(TESTBASE)
    f.close()

lisp.find_file(testfilename)

lisp.j_test_filename_function_set(testfilename + ":main")
