import os.path
import jinja2

dirname = os.path.dirname(os.path.abspath(__file__))
snippetdirname = os.path.join(dirname, "snippets")

def load_snippet(commandname, **kwargs):
    commandfilename = os.path.join(snippetdirname, commandname + ".py")    
    s = open(commandfilename).read()
    
    template = jinja2.Template(s)
    
    s = template.render(**kwargs)

    return s
