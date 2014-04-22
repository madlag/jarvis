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
    def __init__(self, text_color, father):
        super(MyTextEdit, self).__init__("", father)
        self.setReadOnly(True)
        font = QtGui.QFont()
        font.setFamily("Monaco")
        self.setFont(font)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.setTextColor(QtGui.QColor(*text_color))

class ToolBar(QtGui.QWidget):
    def __init__(self, father):
        QtGui.QWidget.__init__(self)

        self.father = father
        self.aspect_ratio_btn = QtGui.QPushButton('square', self)
        self.aspect_ratio_btn.clicked.connect(self.aspect_ratio_btn_handle)
        self.toogle_aspect_ratio = True

        self.slider = QtGui.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self.slider_handle)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.aspect_ratio_btn)
        layout.addWidget(self.slider)

    def aspect_ratio_btn_handle(self):
        if self.toogle_aspect_ratio:
            config.ASPECT_RATIO = "square"
            self.father.update_aspect_ratio(config.ASPECT_RATIO)
            self.aspect_ratio_btn.setText("large")
        else:
            config.ASPECT_RATIO = "large"
            self.father.update_aspect_ratio(config.ASPECT_RATIO)
            self.aspect_ratio_btn.setText("square")
        self.toogle_aspect_ratio = not self.toogle_aspect_ratio

    def update_slider(self, delta):
        self.slider.setValue(int(delta * 100))

    def slider_handle(self):
        self.father.osgView.set_current_time(float(self.slider.value()) / 100.0)

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
        self.debugEditor.clear()
        self.errorEditor.clear()

    def finish(self):
        pass

    def display(self):
        print self.editor.toPlainText()

    def initUI(self, layout=None):
        self.setWindowTitle('Jarvis')

        self.rightBox = QtGui.QVBoxLayout(self)
        self.rightBox.setContentsMargins(0,0,0,0)
        self.rightBox.setSpacing(0)

        self.errorEditor = MyTextEdit((230, 20, 20), self)
        self.debugEditor = MyTextEdit((20, 20, 20),  self)

        self.rightBox.addWidget(self.errorEditor)
        self.rightBox.addWidget(self.debugEditor)
        if self.osg_enable:
            self.osgView = osgqt.PyQtOSGWidget(self)
            self.toolbar = ToolBar(self)
            self.rightBox.addWidget(self.osgView, 0, Qt.AlignCenter)
            self.rightBox.addWidget(self.toolbar)

        self.update_aspect_ratio(config.ASPECT_RATIO)

        self.filename = None
        self.show()

    def update_aspect_ratio(self, aspect_ratio):
        if aspect_ratio == "large":
            ratio = 16.0/9.0
        elif aspect_ratio == "square":
            ratio = 1.0
        else:
            raise Exception("Invalid aspect ratio " + ratio)
        screen = QtGui.QDesktopWidget().screenGeometry()
        width = screen.width() * config.WIDTH_RATIO
        self.setGeometry(
            screen.width() - width,
            0, width, screen.height()
        )

        WINDOW_BAR = 50
        height = (screen.height() - width / ratio) / 2.0 - WINDOW_BAR

        self.errorEditor.setMinimumWidth(width)
        self.errorEditor.setMinimumHeight(height)

        self.debugEditor.setMinimumWidth(width)
        self.debugEditor.setMinimumHeight(height)

        if self.osg_enable:
            self.osgView.setMinimumWidth(width)
            self.osgView.setMinimumHeight(width / ratio)

    def atomic_write(self, filename, text):
        f = open(filename + ".tmp", "w")
        f.write(text)
        f.close()
        shutil.move(filename + ".tmp", filename)

    def debugprint(self, *args):
        text = " ".join(map(lambda x: str(x), args))
        self.debugEditor.append(text)
        text = self.debugEditor.toPlainText()

        debug_file = jarvis.get_filename(jarvis.DEBUG_FILE)
        self.atomic_write(debug_file, text + "\n")

    def errorprint(self, *args):
        text = " ".join(map(lambda x: str(x), args))
        self.errorEditor.append(text)
        text = self.errorEditor.toPlainText()

        error_file = jarvis.get_filename(jarvis.ERROR_FILE)
        self.atomic_write(error_file, text + "\n")

    def reset(self):
        self.debugEditor.setText("")
        self.errorEditor.setText("")
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
