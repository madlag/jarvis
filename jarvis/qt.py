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
import config

class MyTextEdit(QtGui.QTextEdit):
    def __init__(self, text, father):
        super(MyTextEdit, self).__init__(text, father)
        self.setReadOnly(True)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.setFont(font)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
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

        self.rightBox = QtGui.QVBoxLayout(self)
        self.rightBox.setContentsMargins(0,0,0,0)
        self.rightBox.setSpacing(0)

        value = 100 if config.ASPECT_RATIO == 1.0 else 200
        self.error = self.createEditor("", WIDTH, value)
        self.debug = self.createEditor("", WIDTH, value)

        if self.osg_enable:
            self.osgView = self.createOSG(WIDTH, int(WIDTH * 1.0/config.ASPECT_RATIO))

        self.rightBox.addWidget(self.error)
        self.rightBox.addWidget(self.debug)
        if self.osg_enable:
            self.rightBox.addWidget(self.osgView, 0, Qt.AlignCenter)

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
