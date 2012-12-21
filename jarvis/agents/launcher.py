import base
from jarvis.commands import debug

class Launcher(base.Service):
    def run(self):
        debug(self.conf.A)

def main():
    l = Launcher()
    l.run()
