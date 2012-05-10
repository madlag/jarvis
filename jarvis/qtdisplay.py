import qt
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import osg
import osgDB


class QTDisplay(QtCore.QObject):
    def __init__(self, mainloop):
        QtCore.QObject.__init__(self)
        self.app = QtGui.QApplication(sys.argv)
        self.jm = qt.JarvisMain()
#        self.jm.raise_()

        # create a root node
        node = osg.Group()
        # open a file
        loadedmodel = osgDB.readNodeFile("/Users/lagunas/tmp/osgIphoneExampleGLES2/cow.osg")
        node.addChild(loadedmodel)

#        self.jm.osgView.viewer.setSceneData(node)

        self.debug_available.connect(self.jm.debug.setText)
        self.error_available.connect(self.jm.error.setText)
        self.osg_available.connect(self.jm.setSceneData)

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
        self.debug = ""
        self.error = ""
        #self.error_available.emit("")
        #self.debug_available.emit("")

    def debugprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        self.debug += info

    def errorprint(self, *args):
        info = " ".join(map(lambda x: str(x), args)) + "\n"
        self.error += info

    debug_available = QtCore.pyqtSignal(object)
    error_available = QtCore.pyqtSignal(object)
    osg_available = QtCore.pyqtSignal(object)

    def validate(self):
        if self.lastdebug != self.debug:
            self.debug_available.emit(self.debug)
        self.lastdebug = self.debug

        if self.lasterror != self.error:
            self.error_available.emit(self.error)
        self.lasterror = self.error

    def osgprint(self, data):
        self.osg_available.emit(data)

    def launch(self):
        sys.exit(self.app.exec_())

