import sys
import qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtOpenGL

# Used to wrap calls to QTDisplay missing functions, to proxy it to the JarvisMain Qt Widget
class CallWrapper:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __call__(self, *args, **kwargs):
        self.parent.message(self.name, *args, **kwargs)
        
class QTDisplay(QtCore.QObject):
    """This class act as a proxy between the rest of the world and the actual qt widgets"""

    # Message signal handler : it's used to pass all messages to Qt widgets
    message_available = QtCore.pyqtSignal(object)
        
    def __init__(self, mainloop, layout=None):
        # Initialize this as as Qt object
        QtCore.QObject.__init__(self)
        # Create the application
        self.app = QtGui.QApplication(sys.argv)
        
        # Setup OpenGL to use multisampling for antialiasing
        glf = QtOpenGL.QGLFormat.defaultFormat()
        glf.setSampleBuffers(True)
        glf.setSamples(4)
        QtOpenGL.QGLFormat.setDefaultFormat(glf)

        # Create the main widget
        self.jarvismain = qt.JarvisMain(layout)
#        self.jm.raise_()

        # Connect the message to the main widget
        self.message_available.connect(self.jarvismain.message)

        # Start the loop once the Qt App was created
        mainloop.start()

    # Initalize : launch the app
    def init(self):
        sys.exit(self.app.exec_())

    # Destroy the app
    def destroy(self):
        pass

    # Get the inner osg viewer
    def getosgviewer(self):
        return self.jarvismain.getosgviewer()

    # For all other display function calls, act as a proxy to qt for calls
    def message(self, fun, *args, **kwargs):
        self.message_available.emit({"fun":fun, "args":args, "kwargs":kwargs})

    # Catch the missing function calls
    def __getattr__(self, name):
        return CallWrapper(self, name)
                
