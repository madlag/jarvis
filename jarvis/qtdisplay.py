import qt
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtOpenGL
import osg
import osgDB


class QTDisplay(QtCore.QObject):
    def __init__(self, mainloop):
        QtCore.QObject.__init__(self)
        self.app = QtGui.QApplication(sys.argv)
        glf = QtOpenGL.QGLFormat.defaultFormat()
        glf.setSampleBuffers(True)
        glf.setSamples(4)
        QtOpenGL.QGLFormat.setDefaultFormat(glf)

        self.jm = qt.JarvisMain()
#        self.jm.raise_()

        self.debug_available.connect(self.jm.debug_text)
        self.error_available.connect(self.jm.error_text)
        self.osg_available.connect(self.jm.setSceneData)
        self.set_loop_time.connect(self.jm.setLoopTime)
        self.run_command.connect(self.jm.run_command)

        mainloop.start()

        self.lastdebug = ""
        self.lasterror = ""

        self.debug = ""
        self.error = ""
        
    def start(self):
        pass
    
    def finish(self):
        pass

    def clear(self):
#        self.debug = ""
#        self.error = ""
        self.error_available.emit(None)
        self.debug_available.emit(None)

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        self.debug_available.emit(info)

#        print "DEBUGPRINT", info
#        self.debug += info

    def errorprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        self.error_available.emit(info)
#        self.error += info

    def setlooptime(self, loop_time):
        self.set_loop_time.emit(loop_time)

    def runcommand(self, fun):        
        self.jm.fun = fun
        self.run_command.emit()

    debug_available = QtCore.pyqtSignal(object)
    error_available = QtCore.pyqtSignal(object)
    osg_available = QtCore.pyqtSignal(object)
    set_loop_time = QtCore.pyqtSignal(object)
    run_command = QtCore.pyqtSignal()

    def validate(self):
        pass
#        if self.lastdebug != self.debug:
#            print "EMITTING"
#            self.jm.debug.setText(self.debug)
#        print "VALIDATE", self.debug
#        self.debug_available.emit(self.debug)
#        self.lastdebug = self.debug

#        if self.lasterror != self.error:
#        self.error_available.emit(self.error)
#        self.lasterror = self.error

    def osgprint(self, data):
        self.osg_available.emit(data)

    def get_osg_viewer(self):
        return self.jm.get_osg_viewer()

    def launch(self):
        sys.exit(self.app.exec_())

