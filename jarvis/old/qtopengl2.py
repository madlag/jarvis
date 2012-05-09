'''
Created on Jul 7, 2009

@author: Stou Sandalski (stou@icapsid.net)
@license:  Public Domain
'''

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui
from PyQt4 import Qt
from PyQt4 import QtCore
from PyQt4.QtOpenGL import *
import osgViewer
from jarvis import *



class AdapterWidget(QGLWidget):
    '''
    Widget for drawing two spirals.
    '''
    
    def __init__(self, parent, shareWidget):
        QGLWidget.__init__(self, parent, shareWidget)

        self.setMinimumSize(500, 500)
        self.gw = osgViewer.GraphicsWindowEmbedded(0,0,self.width(),self.height());

    def resizeGL(width, height):
        self.gw.getEventQueue().windowResize(0, 0, width, height)
        self.gw.resized(0,0,width,height);



class ViewerQT(AdapterWidget, osgViewer.Viewer):
    def __init__(self, parent, shareWidget):
        AdapterWidget.__init__(self, parent, shareWidget)

        camera = self.getCamera()
        camera.setViewport(osg.Viewport(0, 0, self.width(), self.height()))
        
        camera.getProjectionMatrixAsPerspective(30.0, float(self.width())/float(height()), 1.0, 10000.0)
#            getCamera()->setGraphicsContext(getGraphicsWindow());

#            setThreadingModel(osgViewer::Viewer::SingleThreaded);

#            connect(&_timer, SIGNAL(timeout()), this, SLOT(updateGL()));
#            _timer.start(10);

"""
{
    public:

        ViewerQT(QWidget * parent = 0, const char * name = 0, const QGLWidget * shareWidget = 0, WindowFlags f = 0):
            AdapterWidget( parent, name, shareWidget, f )
        {
        }

        virtual void paintGL()
        {
            frame();
        }
    
    protected:

        QTimer _timer;
};
"""


# You don't need anything below this
class SpiralWidgetDemo(QtGui.QMainWindow):
    ''' Example class for using SpiralWidget'''
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        widget = AdapterWidget(None)
#        self.setCentralWidget(widget)

def main():
    widget = ViewerQT(None, None)
#    widget = QOSGWidget(None)
    
#    app = QtGui.QApplication(['Spiral Widget Demo'])
 #   window = SpiralWidgetDemo()
#    window.show()
#    app.exec_()
    
        
#if __name__ == '__main__':
#    main()
