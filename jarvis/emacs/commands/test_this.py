from Pymacs import lisp
import jarvis.emacs.utils as utils

reload(utils)

# Retrieve current buffer file name
filename = lisp.buffer_file_name()

lisp.j_test_filename_function_set(filename + ":main")
