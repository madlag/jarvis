if 'arg' in globals():
    from Pymacs import lisp
    import jarvis.emacs.utils as utils
    import datetime
    import os

    filename = str(datetime.datetime.now())[:10]

    filename = os.path.join(os.getenv("HOME"), "doc","devel", "journal", filename + ".txt")
    lisp.find_file(filename)
