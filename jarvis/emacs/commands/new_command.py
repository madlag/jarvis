from Pymacs import lisp
import os.path

d = os.path.dirname(os.path.abspath(__file__))
name = arg[0]
name = name.replace("-", "_")
filename = os.path.join(d, name + ".py")
f = open(filename, "w")

newcommand = """from Pymacs import lisp
# Sample code : break on whitespace
start, end = lisp.point(), lisp.mark(True)
words = lisp.buffer_substring(start, end).split()
lisp.delete_region(start, end)
lisp.insert('\\n'.join(words))
"""

f.write(newcommand)
f.close()

lisp.pymacs_load("jarvis.emacs", "j-")
lisp.find_file(filename)

