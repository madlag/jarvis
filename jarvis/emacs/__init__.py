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

def get_user_dir(n):
    ret = os.path.join(os.getenv("HOME"), ".jarvis.d", n)
    # Create the directory
    if not os.path.exists(ret):
        os.path.makedirs(ret)
    return ret

def get_dirs(n):
    subdirnames = []
    for d in [os.path.join(os.getenv("HOME"), ".jarvis.d"), dirname]:
        subdirname = os.path.join(d, n)
        if os.path.exists(subdirname) and os.path.isdir(subdirname):
            subdirnames += [subdirname]
    return subdirnames

def get_command_file(command_name, create = False):
    for commanddirname in commanddirnames:
        # Enumerate the commands
        full_file_name = os.path.join(commanddirname, command_name + ".py")
        if os.path.exists(full_file_name):
            return full_file_name

    return None

commanddirnames = get_dirs("commands")

for commanddirname in commanddirnames:
    # Enumerate the commands
    for f in os.listdir(commanddirname):
        if f.endswith(".py"):
            commandname = f[:-3]
            commandfilename = os.path.join(commanddirname, f)
            if commandname not in globals():
                globals()[commandname] = FunctionWrap(commandfilename)

snippetdirnames = get_dirs("snippets")

for snippetdirname in snippetdirnames:
    # Enumerate the snippets
    for f in os.listdir(snippetdirname):
        if not f.endswith('~'):
            commandname = f
            commandfilename = os.path.join(snippetdirname, f)
            if commandname not in globals():
                globals()[commandname] = SnippetWrap(commandfilename)
