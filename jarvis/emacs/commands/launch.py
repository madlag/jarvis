from Pymacs import lisp
import jarvis

try:
    test_filename_function = open(jarvis.get_filename(jarvis.TEST_FILENAME_FUNCTION)).read()
except:
    test_filename_function = None

if test_filename_function not in [None, ""]:
    lisp.set_frame_size(lisp.selected_frame(), 164, 62)

    lisp.compile("jarvis --filename_function " + test_filename_function)
else:
    lisp.compile("jarvis")


