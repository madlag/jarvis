from Pymacs import lisp
import jarvis.emacs.utils as utils

reload(utils)

# Retrieve current buffer file name
filename = lisp.buffer_file_name()

module_name = utils.find_module_name(filename) + ".main"

lisp.j_test_module_current_set(module_name)
