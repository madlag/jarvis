from Pymacs import lisp

linenumber = lisp.line_number_at_pos()
point = lisp.point()
filename = lisp.buffer_file_name()


f = open("/tmp/log", "w")
f.write(filename + "\n")
f.write(str(point) + "\n")
f.write(str(linenumber)  + "\n")
f.close()

#words = lisp.buffer_substring(start, end).split()
#lisp.delete_region(start, end)
#lisp.insert('\n'.join(words))

