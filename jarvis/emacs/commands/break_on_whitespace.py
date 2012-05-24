from Pymacs import lisp

start, end = lisp.point(), lisp.mark(True)
words = lisp.buffer_substring(start, end).split()
lisp.delete_region(start, end)
lisp.insert('\n'.join(words))
