from Pymacs import lisp
import os.path

def main():
    d = os.path.dirname(os.path.abspath(__file__))
    name = arg[0]
    name = name.replace("-", "_")
    filename = os.path.join(d, "..", "snippets", name)

    start, end = lisp.point(), lisp.mark(True)
    txt = lisp.buffer_substring(start, end)
    
    f = open(filename, "w")
    f.write(txt)
    f.close()

    lisp.pymacs_load("jarvis.emacs", "j-")
    lisp.find_file(filename)
    
if "arg" in globals():
    main()
