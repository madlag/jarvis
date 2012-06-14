from Pymacs import lisp
import os.path
import jarvis.emacs as emacs

def main():    
    d = emacs.get_user_dir("commands")
    name = arg[0]
    name = name.replace("-", "_")
    
    # Check if command already exists
    command_file_name = emacs.get_command_file(name)
    if command_file_name != None:
        lisp.message("Command already exists, opening %s" % command_file_name)
        lisp.find_file(command_file_name)
        return
    raise Exception("not found")
    
    filename = os.path.join(d, name + ".py")    
    f = open(filename, "w")

    newcommand = """if 'arg' in globals():
    from Pymacs import lisp
    import jarvis.emacs.utils as utils

    # Retrieve current buffer file name
    filename = lisp.buffer_file_name()

    # Sample code : break on whitespace
    start, end = lisp.point(), lisp.mark(True)
    words = lisp.buffer_substring(start, end).split()
    lisp.delete_region(start, end)
    lisp.insert('\\n'.join(words))"""

    f.write(newcommand)
    f.close()

    lisp.pymacs_load("jarvis.emacs", "j-")
    lisp.find_file(filename)

    
if "arg" in globals():
    main()
