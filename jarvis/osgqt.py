#!/usr/bin/env python
#osgviewerQt4.py

__author__  = ["Rene Molenaar"]
__url__     = ("http://code.google.com/p/osgswig/")
__version__ = "1.0.0"
__doc__     = """ This example shows to use osgViewer.Viewer within PyQt4 ____Rene Molenaar 2008 
                  the basics functionality is present, but there are many 'missing features'
                  for example, mouse modifiers are not adapted, mouse wheel is not adapted and 
                  non-ascii keyboard input is not adapted.
              """

# general Python
import sys,os

import OpenGL.GL as GL

# import qtWidgets stuff
import PyQt4

# import OpenSceneGraph wrapper
import osg, osgDB, osgGA, osgViewer

from PyQt4 import QtOpenGL
from PyQt4 import Qt, QtGui, QtCore
import time

mouseButtonDictionary = {
    QtCore.Qt.LeftButton: 1,
    QtCore.Qt.MidButton: 2,
    QtCore.Qt.RightButton: 3,
    QtCore.Qt.NoButton: 0,
    }

class PyQtOSGWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent = 0, name = '' ,flags = 0):
        """constructor """
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.timer = Qt.QTimer()
        self.camera = None

    def initializeGL (self):
        """initializeGL the context and create the osgViewer, also set manipulator and event handler """
        self.gw = self.createContext()
        self.viewer = self.createViewer()
        #init the default eventhandler
#        self.viewer.setCameraManipulator(osgGA.TrackballManipulator())
        self.viewer.addEventHandler(osgViewer.StatsHandler())
        self.viewer.addEventHandler(osgViewer.HelpHandler())
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout ()"), self.updateGL)
        self.timer.start(0)

    def embedInContext (self):
        """create a osg.GraphicsWindow for a Qt.QWidget window"""
        gw = osgViewer.GraphicsWindowEmbedded(0,0,self.width(),self.height())
        return gw

    def createContext (self):
        """create a opengl context (currently WindowData classes are not wrapped so we can not inherrit the windowdata) """
        ds = osg.DisplaySettings_instance()
        if False:
            traits = osg.Traits()
            traits.readDISPLAY()
            if (traits.displayNum<0): traits.displayNum = 0

            traits.windowName = "osgViewerPyQt"
            traits.screenNum = 0
            traits.x = self.x()
            traits.y = self.y()
            traits.width = self.width()
            traits.height = self.height()
            traits.alpha = ds.getMinimumNumAlphaBits()
            traits.stencil = ds.getMinimumNumStencilBits()
            traits.windowDecoration = False
            traits.doubleBuffer = True
            traits.sampleBuffers = ds.getMultiSamples()
            traits.samples = ds.getNumMultiSamples()
        gw = osgViewer.GraphicsWindowEmbedded()
        return gw

    def createViewer(self):
        """create a osgViewer.Viewer and set the viewport, camera and previously created graphical context """
        viewer = osgViewer.Viewer()
        camera = viewer.getCamera()
        camera.setViewport(osg.Viewport(0,0, self.width(), self.height()))

        CAMERA_ANGLE = 45.0
        CAMERA_Z_TRANSLATE = 2.4142135623730949 #1.0 / math.tan(math.radians(CAMERA_ANGLE / 2.0))    
        cameraPosition = [0.0, 0.0, CAMERA_Z_TRANSLATE]

        camera.setProjectionMatrixAsPerspective(CAMERA_ANGLE,float(self.width())/float(self.height()), 1.0, 10000.0)

        eye = osg.Vec3d(cameraPosition[0], cameraPosition[1], cameraPosition[2])
        center = osg.Vec3d(0,0,0)
        up = osg.Vec3d(0,1,0)
        camera.setViewMatrixAsLookAt(eye, center, up)

        if not self.gw:
            raise Exception("GraphicsWindow not yet created")
        camera.setGraphicsContext(self.gw)
        self.camera = camera

        return viewer

    def createViewerNew(self):
        # Standard size
        size = (self.width(), self.height())
        screen_ratio = float(size[0]) / float(size[1])

        # Build the camera
        import math
        CAMERA_ANGLE = 45.0
        CAMERA_Z_TRANSLATE = 2.4142135623730949 #1.0 / math.tan(math.radians(CAMERA_ANGLE / 2.0))
    
        cameraPosition = [0.0, 0.0, CAMERA_Z_TRANSLATE]

        # Create the viewer
        viewer = osgViewer.Viewer()

#        viewer.setSceneData(camera)

        camera = viewer.getCamera()

        # Setup the viewport
        camera.setViewport(osg.Viewport(0,0,size[0], size[1]))
        camera.setReferenceFrame(osg.Transform.ABSOLUTE_RF)
        position = cameraPosition
        camera.setProjectionMatrixAsPerspective(CAMERA_ANGLE, screen_ratio, 0.1, 100.0)
#        camera.getOrCreateStateSet().setAttributeAndModes(osg.BlendFunc(GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA))
#        camera.getOrCreateStateSet().setMode(GL.GL_LIGHTING, False)
        material = osg.Material()
        color = osg.Vec4(1.0,1.0,1.0,1.0)
        material.setDiffuse(osg.Material.FRONT_AND_BACK, color)
        material.setAmbient(osg.Material.FRONT_AND_BACK, color)
        camera.getOrCreateStateSet().setAttributeAndModes(material)
        camera.setClearColor(osg.Vec4(0,0,0,0))
#        camera.setClearMask(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        eye = osg.Vec3d(cameraPosition[0], cameraPosition[1], cameraPosition[2])
        center = osg.Vec3d(0,0,0)
        up = osg.Vec3d(0,1,0)
        camera.setViewMatrixAsLookAt(eye, center, up)

        self.camera = camera
        
        if not self.gw:
            raise Exception("GraphicsWindow not yet created")

        viewer.getCamera().setGraphicsContext(self.gw)        

#        viewer.setUpViewInWindow(0,0, size[0], size[1])
#        viewer.addEventHandler(osgViewer.HelpHandler());
#        viewer.addEventHandler(osgViewer.StatsHandler());
#        viewer.addEventHandler(osgViewer.ThreadingHandler())
#        viewer.setThreadingModel(osgViewer.ViewerBase.SingleThreaded)

        return viewer

    def setSceneData(self, data):
        print "setSceneData"
        if self.camera == None:
            return
        if self.camera.getNumChildren() == 1:
            self.camera.removeChild(0)
        if scene_data != None:
            self.camera.addChild(scene_data)

    
    def resizeGL( self, w, h ):
        print "GL resized ", w, h
        self.gw.resized(0,0,w,h)

    def paintGL (self):
        self.viewer.frame()

    def mousePressEvent( self, event ):
        """put the qt event in the osg event queue"""
        button = mouseButtonDictionary.get(event.button(), 0)
        self.gw.getEventQueue().mouseButtonPress(event.x(), event.y(), button)

    def mouseReleaseEvent( self, event ):
        """put the qt event in the osg event queue"""
        button = mouseButtonDictionary.get(event.button(), 0)
        self.gw.getEventQueue().mouseButtonRelease(event.x(), event.y(), button)

    def mouseMoveEvent(self, event):
        """put the qt event in the osg event queue"""
        self.gw.getEventQueue().mouseMotion(event.x(), event.y())

    def keyPressEvent(self, event):
        """ translate the qt event to an osg event (currently only ascii values) """
        print "key pressed", event.text()
        self.gw.getEventQueue().keyPress( ord(event.text().toAscii().data()) ) #

    def keyReleaseEvent(self, event):
        """ translate the qt event to an osg event (currently only ascii values) """
        print "key released", event.text()
        self.gw.getEventQueue().keyRelease( ord(event.text().toAscii().data()) )

    def timerEvent(self, timerevent):
        """periodically called (each cycle) calls updateGL (which will trigger paintGL)"""
        self.updateGL()

    def getGraphicsWindow(self):
        """returns the osg graphicswindow created by osgViewer """
        return self.gw 


if  __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()

    #show the mainwindow
    mainwindow.show()

    time.sleep(10)
    # create a root node
    node = osg.Group()
    # open a file
    loadedmodel = osgDB.readNodeFile("/Users/lagunas/tmp/osgIphoneExampleGLES2/cow.osg")
    node.addChild(loadedmodel)
    mainwindow.setSceneData(node)

    #execute the application
    sys.exit(app.exec_())
