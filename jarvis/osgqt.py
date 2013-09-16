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
import osgUtil
import jarvis

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
        self.timer.setInterval(40)
        self.camera = None
        self.startTime = time.time()
        self.loopTime = 10.0
        self.mousePressed = False
        self.current_mouse_time = 0
        self.audio = None

    def initializeGL (self):
        """initializeGL the context and create the osgViewer, also set manipulator and event handler """
        self.gw = self.createContext()
        self.viewer = self.createViewer()
        #init the default eventhandler
#        self.viewer.setCameraManipulator(osgGA.TrackballManipulator())
        self.viewer.addEventHandler(osgViewer.StatsHandler())
        self.viewer.addEventHandler(osgViewer.HelpHandler())
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout ()"), self.updateGL)
        self.timer.start(40)

    def setLoopTime(self, loopTime):
        self.loopTime = loopTime

    def embedInContext (self):
        """create a osg.GraphicsWindow for a Qt.QWidget window"""
        gw = osgViewer.GraphicsWindowEmbedded(0,0,self.width(),self.height())
        return gw

    def createContext (self):
        """create a opengl context (currently WindowData classes are not wrapped so we can not inherrit the windowdata) """
        ds = osg.DisplaySettings_instance()
        if False:
            traits = osg.GraphicsContext.Traits()
            print traits
            traits.readDISPLAY()
            if (traits.displayNum<0): traits.displayNum = 0

            traits.windowName = "osgViewerPyQt"
            traits.screenNum = 0
            traits.x = self.x()
            traits.y = self.y()
            traits.width = self.width()
            traits.height = self.height()
            traits.alpha = 8 #ds.getMinimumNumAlphaBits()
            traits.stencil = 8 #ds.getMinimumNumStencilBits()
            traits.windowDecoration = False
            traits.doubleBuffer = True
            traits.sampleBuffers = 4 #ds.getMultiSamples()
            traits.samples = 4 #ds.getNumMultiSamples()
        gw = osgViewer.GraphicsWindowEmbedded()
        return gw

    def createViewer(self):
        """create a osgViewer.Viewer and set the viewport, camera and previously created graphical context """
        viewer = osgViewer.Viewer()
        self.resetCamera(viewer)
        return viewer

    def resetCamera(self, viewer):

        camera = viewer.getCamera()
        camera.setComputeNearFarMode(False)
#        camera = osg.Camera()
        camera.setViewport(osg.Viewport(0,0, self.width(), self.height()))
#        camera.setReferenceFrame(osg.Transform.ABSOLUTE_RF)
        CAMERA_ANGLE = 45.0
        CAMERA_Z_TRANSLATE = 2.4142135623730949 #1.0 / math.tan(math.radians(CAMERA_ANGLE / 2.0))
        cameraPosition = [0.0, 0.0, CAMERA_Z_TRANSLATE]

        camera.setProjectionMatrixAsPerspective(CAMERA_ANGLE,float(self.width())/float(self.height()), 0.1, 100.0)

        eye = osg.Vec3d(cameraPosition[0], cameraPosition[1], cameraPosition[2])
        center = osg.Vec3d(0,0,0)
        up = osg.Vec3d(0,1,0)
        camera.setViewMatrixAsLookAt(eye, center, up)

        camera.getOrCreateStateSet().setAttributeAndModes(osg.BlendFunc(GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA))
        camera.getOrCreateStateSet().setMode(GL.GL_DEPTH_TEST, False)
        camera.getOrCreateStateSet().setMode(GL.GL_DEPTH_WRITEMASK, False)
        camera.getOrCreateStateSet().setMode(GL.GL_LIGHTING, False)
        material = osg.Material()
        color = osg.Vec4(1.0,1.0,1.0,1.0)
        material.setDiffuse(osg.Material.FRONT_AND_BACK, color)
        material.setAmbient(osg.Material.FRONT_AND_BACK, color)
        camera.getOrCreateStateSet().setAttributeAndModes(material)
        camera.setClearColor(osg.Vec4(0,0,0,0))
        camera.setClearMask(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        camera.setComputeNearFarMode(False)

        if not self.gw:
            raise Exception("GraphicsWindow not yet created")

        self.camera = camera

#        viewer.getCamera().setViewport(osg.Viewport(0,0, self.width(), self.height()))
 #       viewer.getCamera().addChild(camera)
        camera.setGraphicsContext(self.gw)

    def heightForWidth(self, w):
        ret = int(w * 9.0 / 16.0)
        return ret

    def texture_build(self):
        texture = osg.Texture2D()
        texture.setTextureSize(self.width(), self.height())
        texture.setInternalFormat(GL.GL_RGBA)
        texture.setResizeNonPowerOfTwoHint(False)

        # bug detected here, if I enable mipmap osg seems to use the view buffer to
        # do something. If I disable the mipmap it works.
        # you can view the issue with test_09_gaussian_filter.py
        #texture.setFilter(osg.Texture.MIN_FILTER, osg.Texture.LINEAR_MIPMAP_LINEAR)
        texture.setFilter(osg.Texture.MIN_FILTER, osg.Texture.LINEAR)
        texture.setFilter(osg.Texture.MAG_FILTER, osg.Texture.LINEAR)
        return texture

    def camera_build(self):
        texture = self.texture_build()

        camera = osg.Camera()
        camera.setViewport(osg.Viewport(0,0, self.width(), self.height()))
        camera.setReferenceFrame(osg.Transform.ABSOLUTE_RF)
        camera.setRenderOrder(osg.Camera.PRE_RENDER)
        camera.setRenderTargetImplementation(osg.Camera.FRAME_BUFFER_OBJECT)
        camera.attach(osg.Camera.COLOR_BUFFER, texture, 0, 0, False, 0, 0)

        CAMERA_ANGLE = 45.0
        CAMERA_Z_TRANSLATE = 2.4142135623730949 #1.0 / math.tan(math.radians(CAMERA_ANGLE / 2.0))
        cameraPosition = [0.0, 0.0, CAMERA_Z_TRANSLATE]

        camera.setProjectionMatrixAsPerspective(CAMERA_ANGLE,float(self.width())/float(self.height()), 1.0, 10000.0)

        eye = osg.Vec3d(cameraPosition[0], cameraPosition[1], cameraPosition[2])
        center = osg.Vec3d(0,0,0)
        up = osg.Vec3d(0,1,0)
        camera.setViewMatrixAsLookAt(eye, center, up)

        camera.getOrCreateStateSet().setAttributeAndModes(osg.BlendFunc(GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA))
        camera.getOrCreateStateSet().setMode(GL.GL_DEPTH_TEST, False)
        camera.getOrCreateStateSet().setMode(GL.GL_DEPTH_WRITEMASK, False)
        camera.getOrCreateStateSet().setMode(GL.GL_LIGHTING, False)
        material = osg.Material()
        color = osg.Vec4(1.0,1.0,1.0,1.0)
        material.setDiffuse(osg.Material.FRONT_AND_BACK, color)
        material.setAmbient(osg.Material.FRONT_AND_BACK, color)
        camera.getOrCreateStateSet().setAttributeAndModes(material)
        camera.setClearColor(osg.Vec4(0,0,0,0))
        camera.setClearMask(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)


        return camera, texture

    def quad_create(self, texture):
        stateset = osg.StateSet()
        stateset.setTextureAttributeAndModes(0, texture)

        w = 16.0 / 9.0
        h = 1.0
        corner = osg.Vec3(-w,-h, 0)
        width = osg.Vec3(2 * w,0,0)
        height = osg.Vec3(0,2 * h,0)

        geom = osg.createTexturedQuadGeometry(corner, width, height, 0.0, 0.0, 1.0, 1.0)
        geom.setStateSet(stateset)

        geode = osg.Geode()
        geode.addDrawable(geom)
        return geode


    def build_wrapping_node(self, data):
        grp = osg.Group()
        camera,texture = self.camera_build()

        grp.addChild(camera)
        camera.addChild(data)

        quad = self.quad_create(texture)
        grp.addChild(quad)

        grp.getOrCreateStateSet().setMode(GL.GL_LIGHTING, False)
        return grp

    def get_current_time(self):
        if self.mousePressed:
            return self.current_mouse_time
        else:
            return time.time() - self.startTime

    def resetSceneData(self, data):
        self.viewer.setSceneData(None)
        self.audioStop()
        self.audio = None

    def setSceneData(self, data):
        start = time.time()
#        self.startTime = time.time()
        if data  != None:
            data = self.build_wrapping_node(data)
            self.viewer.setSceneData(data)
        end = time.time()
        self.startTime += end - start

    def audioPlay(self):
        if self.audio != None:
            self.audio.play()

    def audioStop(self):
        if self.audio != None:
            self.audio.stop()

    def buildAudioTmpFile(self, data, skip):
        import wavehelper
        if isinstance(data, basestring):
            data = wavehelper.WaveReader(data)
        if hasattr(data, "read"):
            outputFileName = jarvis.get_filename("audiotmpfile.wav")
            ws = wavehelper.WaveSink(data, outputFileName, self.loopTime, skip = skip)
            ws.run()
            return outputFileName

    def setAudioData(self, data, skip = 0.0):
        if self.audio != None:
            self.audioStop()
            self.audio = None
        fname = self.buildAudioTmpFile(data, skip)
        self.audio = QtGui.QSound(fname)
        self.audioPlay()

    def getosgviewer(self):
        return self.viewer

    def resizeGL( self, w, h ):
        self.gw.resized(0,0,w,h)
        self.resetCamera(self.viewer)

    def paintGL (self):
        t = self.get_current_time()
        if t >= self.loopTime:
            self.startTime = time.time()
            t = 0.0
            if self.audio != None:
                self.audioStop()
                self.audioPlay()

        self.viewer.frameAtTime(t)

    def set_time_from_mouse(self, position):
        self.current_mouse_time = self.loopTime * float(position) / float(self.width())
        self.startTime = time.time() - self.current_mouse_time

    def mousePressEvent( self, event ):
        """put the qt event in the osg event queue"""
        button = mouseButtonDictionary.get(event.button(), 0)
        self.mousePressed = True
        self.set_time_from_mouse(event.x())
        self.gw.getEventQueue().mouseButtonPress(event.x(), event.y(), button)
        self.audioStop()

    def mouseReleaseEvent( self, event ):
        """put the qt event in the osg event queue"""
        button = mouseButtonDictionary.get(event.button(), 0)
        self.mousePressed = False
        self.gw.getEventQueue().mouseButtonRelease(event.x(), event.y(), button)

    def mouseMoveEvent(self, event):
        """put the qt event in the osg event queue"""
        self.set_time_from_mouse(event.x())
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

