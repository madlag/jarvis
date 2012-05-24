from Pymacs import lisp
import imp
import inspect


# Find the buffer file name
filename = lisp.buffer_file_name()

# Load the module
f = imp.load_source("entrypoint", filename)


# Enumerate the classes in the module
for k in dir(f):
    
    # Find the task
    if k.endswith("Task") and k != "LizardTask":
        # Get the task class
        cl = getattr(f, k)
        # Build the parameters list
        parameters = []
        for k in cl.directory["input"]:
            parameters += [k["name"]]

        # Build the full string
        parameters = ", ".join(parameters)
        parameters = "    def run(self, " + parameters + "):"

        
        for i, l in enumerate(open(filename).readlines()):
            if "def run(self" in l:
                line = i + 1
                break
                    
        # Find the place where the run function is
#        line = inspect.getsourcelines(cl.run)[1]
        
        # Move to the line and select it 
        lisp.goto_line(line)
        lisp.end_of_line()
        beg = lisp.line_beginning_position()
        lisp.set_mark(beg)

        # Replace the line with the new one
        start, end = lisp.point(), lisp.mark(True)
        words = lisp.buffer_substring(start, end).split()
        lisp.delete_region(start, end)
        lisp.insert(parameters)
