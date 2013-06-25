import jarvis.agents.base as base
import webdisplay
import mainloop
import time

class PythonRunner(base.Agent):
    def run(self):
        
        ml = mainloop.MainLoop()
        display = webdisplay.Display()
        ml.setdisplay(display)
        display.init()

        while(True):
            test_filename_function = self.client.get("test_filename_function")
            ml.run_once(test_filename_function)
            time.sleep(0.1)

def main():
    l = PythonRunner()
    l.run()
