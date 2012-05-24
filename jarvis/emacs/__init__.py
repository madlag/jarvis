import os.path
from Pymacs import lisp
import jinja2
import jinja2.meta


#def simplify_on_whitespace():
#    start, end = lisp.point(), lisp.mark(True)
#    words = lisp.buffer_substring(start, end).split()
#    words = filter(lambda x : x != "", words)
#    lisp.delete_region(start, end)
#    lisp.insert('K'.join(words))


# Special class to wrap commandfilename
class FunctionWrap(object):
    def __init__(self, commandfilename):
        self.commandfilename = commandfilename
        self.interaction = self.interaction_()
        f = open("/tmp/log", "a")
        f.write(self.interaction)
        f.close()
        
    def __call__(self, *args, **kwargs):
        f = open("/tmp/log2", "a")
        f.write(str(args) + "\n")
        f.write(str(kwargs) + "\n")
        f.close()
        exec(open(self.commandfilename).read(), {"arg":args, "kwargs":kwargs, "__file__":self.commandfilename})

    def interaction_(self):
        try:
            return open(self.commandfilename[:-3] + ".spec").read()
        except:
            return ""
        
class SnippetWrap(FunctionWrap):
    def __init__(self, commandfilename):
        e = jinja2.Environment()
        s = open(commandfilename).read()
        ast = e.parse(s)
        self.variables = list(jinja2.meta.find_undeclared_variables(ast))
                
        super(SnippetWrap, self).__init__(commandfilename)
    
    def interaction_(self):
        s = ""
        for v in self.variables:
            s += "s%s:\n" % v
        return s

    def __call__(self, *args):
        s = open(self.commandfilename).read()
        template = jinja2.Template(s)

        kwargs = {}
        for i, a in enumerate(args):
            kwargs[self.variables[i]] = a
        
        s = template.render(**kwargs)
        lisp.insert(s)
    
# Build the commands directory
dirname = os.path.dirname(os.path.abspath(__file__))

commanddirname= os.path.join(dirname, "commands")

# Enumerate the commands 
for f in os.listdir(commanddirname):
    if f.endswith(".py"):
        commandname = f[:-3]
        commandfilename = os.path.join(commanddirname, f)
        globals()[commandname] = FunctionWrap(commandfilename)

snippetdirname = os.path.join(dirname, "snippets")

# Enumerate the snippets
for f in os.listdir(snippetdirname):
    if f.endswith(".py"):
        commandname = f[:-3]
        commandfilename = os.path.join(snippetdirname, f)
        globals()[commandname] = SnippetWrap(commandfilename)
