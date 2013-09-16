import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
import os.path
import codecs
import osgqt
import osgDB
import osg
import shutil
import jarvis
import traceback

class MyTextEdit(QtGui.QTextEdit):
    def __init__(self, text, father):
        super(MyTextEdit, self).__init__(text, father)
#        self.setFontPointSize(20)
#    def keyPressEvent(self, event):
#        print event

class JarvisMain(QtGui.QWidget):

    def __init__(self, layout=None):
        self.osg_enable = True
        super(JarvisMain, self).__init__()

        self.initUI(layout)

    def message(self, object):
        try:
            fun_name = object["fun"]
            args = object.get("args", [])
            kwargs = object.get("kwargs", {})
            getattr(self, fun_name)(*args, **kwargs)
        except:
            print traceback.format_exc()
            pass

    def start(self):
        self.debug.clear()
        self.error.clear()

    def finish(self):
        pass

    def display(self):
        print self.editor.toPlainText()

#    def wheelEvent(self, event):
#        print self.editor.setFocus(False)

#    def keyPressEvent(self, event):
#         print event

    def createEditor(self, text, width, height):
        editor = MyTextEdit(text, self)
        editor.setMinimumWidth(width)
        editor.setMinimumHeight(height)
        return editor

    def createOSG(self, width, height):
        osgWidget = osgqt.PyQtOSGWidget(self)
        osgWidget.setMinimumWidth(width)
        osgWidget.setMinimumHeight(height)
        return osgWidget

    def parse_layout(self, layout):
        ret = {}
        f = open(layout)
        for line in f:
            parts = line.split("=")
            ret[parts[0]] = int(parts[1])
        return ret

    def initUI(self, layout=None):
        self.setWindowTitle('Jarvis')

        if layout is not None:
            layout = self.parse_layout(layout)
        else:
            layout = {}

        WIDTH=480
        HEIGHT=1024
        self.setGeometry(1680 - WIDTH, 0, WIDTH, 1050)

#        self.setWindowIcon(QtGui.QIcon('web.png'))

        text = ""
#        for i in range(10):
#            text += '<b>Text%d</b><br/>' % i

        self.topBox = QtGui.QHBoxLayout(self)
        self.topBox.setContentsMargins(0,0,0,0)
        self.topBox.setSpacing(0)
        self.topBox.setGeometry(QtCore.QRect(0, 0, WIDTH, HEIGHT))

#        self.editor = self.createEditor(text, 300, 600)
#        self.editor.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#        self.topBox.addWidget(self.editor)

        self.rightBox = QtGui.QVBoxLayout()
        self.rightBox.setSpacing(0)
        self.topBox.addLayout(self.rightBox)


        self.error = self.createEditor("", WIDTH, 200)
        self.debug = self.createEditor("", WIDTH, 200)

        if self.osg_enable:
            self.osgView = self.createOSG(WIDTH, int(WIDTH * 9 / 16.0))

        self.rightBox.addWidget(self.error, 0, Qt.AlignRight)
        self.rightBox.addWidget(self.debug, 0, Qt.AlignRight)
        if self.osg_enable:
            self.rightBox.addWidget(self.osgView, 0, Qt.AlignRight)

#        editor.textChanged.connect(self.display)
#        editor.wheelEvent.connect(self.wheelEvent)
#        self.editor.setFocus()
        self.filename = None
        self.show()

    def atomic_write(self, filename, text):
        f = open(filename + ".tmp", "w")
        f.write(text)
        f.close()
        shutil.move(filename + ".tmp", filename)

    def debugprint(self, *args):
        text = " ".join(map(lambda x: str(x), args))
        self.debug.append(text)
        text = self.debug.toPlainText()

        debug_file = jarvis.get_filename(jarvis.DEBUG_FILE)
        self.atomic_write(debug_file, text + "\n")

    def errorprint(self, *args):
        text = " ".join(map(lambda x: str(x), args))
        self.error.append(text)
        text = self.error.toPlainText()

        error_file = jarvis.get_filename(jarvis.ERROR_FILE)
        self.atomic_write(error_file, text + "\n")

    def reset(self):
        self.debug.setText("")
        self.error.setText("")
        self.osgView.resetSceneData(None)

    def osgprint(self, data):
        self.osgView.setSceneData(data)

    def audioemit(self, data, skip = 0.0):
        self.osgView.setAudioData(data, skip)

    def setlooptime(self, loopTime):
        self.osgView.setLoopTime(loopTime)

    def runcommand(self, fun):
        fun()

    def getosgviewer(self):
        return self.osgView.getosgviewer()

    def file_dialog(self):
        fd = QtGui.QFileDialog(self)
        filename = fd.getOpenFileName()
        if os.path.isfile(filename):
            text = open(filename).read()
            self.editor.setText(text)
            self.filename = filename

            s = codecs.open(self.filename,'w','utf-8')
            s.write(unicode(self.ui.editor_window.toPlainText()))
            s.close()
