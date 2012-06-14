from Pymacs import lisp
import subprocess
import jarvis

test_filename_function = open(jarvis.get_filename(jarvis.TEST_FILENAME_FUNCTION)).read()

lisp.compile("jarvis --filename_function " + test_filename_function)

