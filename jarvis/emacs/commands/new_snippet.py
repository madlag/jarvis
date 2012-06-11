from Pymacs import lisp
import os.path
import jarvis.emacs as emacs

def main():
    d = emacs.get_user_dir("snippets")
    name = arg[0]
    name = name.replace("-", "_")
    filename = os.path.join(d, name)

    start, end = lisp.point(), lisp.mark(True)

    if end != None:
        txt = lisp.buffer_substring(start, end)
    else:
        txt = "This is your new snippet. Next time, set the mark so I can copy / paste it into your snippet"
                
    f = open(filename, "w")
    f.write(txt)
    f.close()

    lisp.pymacs_load("jarvis.emacs", "j-")
    lisp.find_file(filename)
    
if "arg" in globals():
    main()
