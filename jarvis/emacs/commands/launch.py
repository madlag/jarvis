from Pymacs import lisp
import subprocess
import jarvis

module_name = open(jarvis.get_filename(jarvis.TEST_MODULE_PATH)).read()

lisp.compile("jarvis --module " + module_name)

