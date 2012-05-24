from Pymacs import lisp
import os.path
import jarvis

testmodule = arg[0]
jarvis_home = jarvis.get_home()

testmodulefilename = os.path.join(jarvis_home, "testmodule.txt")

f=open(testmodulefilename, "w")
f.write(testmodule)
f.close()

