from Pymacs import lisp
import jarvis.emacs.utils as utils
import os.path
import os

"""
Launch this command in a given task code buffer, it will create the test with it
"""


filename = lisp.buffer_file_name()
#filename = "/Users/lagunas/devel/task/stupeflix/lizard/tasks/video/render/base.py"
directory = filename[:-3]


BASE = os.path.join(os.getenv("HOME"), "devel", "task", "stupeflix", "lizard", "tasks")
print BASE
print directory
submodule =  directory[len(BASE) + 1:].split("/")

subdir = "_".join(submodule)

testdir = os.path.join(BASE, "tests", subdir)
try:
    os.mkdir(testdir)
except Exception, e:
    pass


testname = "test_" + subdir
testfilename = os.path.join(testdir, testname + ".py")

if os.path.exists(testfilename):
    raise Exception("Test %s already exists", testfilename)
else:
    f = open(testfilename, "w")

    taskmodule = ".".join(submodule)
    shorttaskmodule = submodule[-1]
    taskclassname = "".join(map(lambda x: x.capitalize(), submodule)) + "Task"
    TESTBASE = utils.load_snippet("lizard_task_test", taskmodule= taskmodule, shorttaskmodule = shorttaskmodule, TaskClassName = taskclassname)
    f.write(TESTBASE)
    f.close()

lisp.find_file(testfilename)
