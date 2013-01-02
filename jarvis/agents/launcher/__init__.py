import jarvis.agents.base as base
from jarvis.commands import debug

class Launcher(base.Agent):
    def run(self):
        debug(self.conf.A)

def main():
    l = Launcher()
    l.run()
