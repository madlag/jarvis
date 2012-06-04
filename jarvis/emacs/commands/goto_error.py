from Pymacs import lisp
import jarvis

errorpath = jarvis.get_filename(jarvis.ERROR_FILE)
f = open(errorpath).read()

finalfilename = None
finalline = None

for l in f.split("\n"):
    if "File \"" in l:
        parts = l.split()
        filename = parts[1][1:-2]
        line = parts[3].strip(",")
        finalfilename = filename
        finalline = line

if finalfilename != None and finalline != None:
    lisp.find_file(finalfilename)
    lisp.goto_line(int(finalline))
