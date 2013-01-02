import jarvis.utils.conf as conf
import os.path
import jarvis.client as client

conf.load("jarvis")

class Agent(object):
    def __init__(self):
        # Build the name parts
        parts = ["agents", self.__class__.__name__.lower()]
        # Build the name
        name = "_".join(parts)
        # Build the config file name
        subpath = os.path.join(*parts) + ".py"
        # Assemble the config pathes
        basepathes = ["/etc/jarvis", os.path.join(os.getenv("HOME"), ".jarvis.d", "conf")]
        pathes = []
        for p in basepathes:            
            pathes += [os.path.join(p, subpath)]

        # Load the conf
        conf.load(name, pathes = pathes)

        # Retrieve the object containing the conf
        self.conf = getattr(conf, name)

        self.client = client.Client()
        
        
        

