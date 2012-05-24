import curses

class CursesDisplay():
    def __init__(self):
        self.stdscr = curses.initscr()
        
        begin_x = 0
        begin_y = 0
        height = 25
        width = 0
        self.status_window = curses.newwin(height, width, begin_y, begin_x)
        begin_y += height
        height = 100
        self.debug_window = curses.newwin(height, width, begin_y, begin_x)
            
    def end(self):
        curses.nocbreak()
        self.status_window.keypad(0)
        curses.echo()
        curses.endwin()

    def clear(self):
        self.status_window.clear()
        self.debug_window.clear()

    def finish(self):
        self.status_window.refresh()
        self.debug_window.refresh()

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        self.status_window.clear()
        self.debug_window.addstr(info)

    def errorprint(self, *args):        
        error = " ".join(map(lambda x: str(x), args)) + "\n"
        self.status_window.clear()
        self.status_window.addstr(error)

