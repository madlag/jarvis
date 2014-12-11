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

# import OpenSceneGraph wrapper
import osg, osgDB, osgGA, osgViewer

from PySide import QtOpenGL
from PySide import QtCore
import time
import osgUtil
import jarvis
import config
from fpscalculator import FPSCalculator
from soundplayer import SoundPlayer

UPDATE_MASK=3
VISIBLE_CULL_MASK=1

mouseButtonDictionary = {
    QtCore.Qt.LeftButton: 1,
    QtCore.Qt.MidButton: 2,
    QtCore.Qt.RightButton: 3,
    QtCore.Qt.NoButton: 0,
    }

viewerFactory = osgViewer.Viewer

def setViewerFactory(factory):
    global viewerFactory
    viewerFactory = factory

class PyQtOSGWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent = 0, name = '' ,flags = 0):
        """constructor """
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000.0 / config.FPS_RENDERING) # in milliseconds
        self.camera = None
        self.startTime = 0.0
        self.loopTime = 10.0
        self.is_paused = False
        self.still_frame = True
        self.current_time = 0
        self.audio = None
        self.fps_calculator = FPSCalculator(start_time=self.startTime, smoothness=30)

    def initializeGL (self):
        """initializeGL the context and create the osgViewer, also set manipulator and event handler """
        self.gw = self.createContext()
        self.viewer = None

        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout ()"), self.updateGL)

    def setLoopTime(self, loopTime):
        self.loopTime = loopTime
        if self.audio is not None:
            self.audio.set_loop_time(start_time=self.audio_skip, end_time=self.audio_skip + self.loopTime)

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
        global viewerFactory
        viewer = viewerFactory()
        #init the default eventhandler
#        self.viewer.setCameraManipulator(osgGA.TrackballManipulator())
        viewer.addEventHandler(osgViewer.StatsHandler())
        viewer.addEventHandler(osgViewer.HelpHandler())
        viewer.getUpdateVisitor().setTraversalMask(UPDATE_MASK)
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

        camera.setCullMask(VISIBLE_CULL_MASK)

        if not self.gw:
            raise Exception("GraphicsWindow not yet created")

        self.camera = camera

#        viewer.getCamera().setViewport(osg.Viewport(0,0, self.width(), self.height()))
 #       viewer.getCamera().addChild(camera)
        camera.setGraphicsContext(self.gw)

    def heightForWidth(self, w):
        return w / config.ASPECT_RATIO

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

        camera.setProjectionMatrixAsPerspective(CAMERA_ANGLE,float(self.width())/float(self.height()), 0.1, 10000.0)

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
        corner = osg.Vec3(-config.ASPECT_RATIO, -1.0, 0)
        width = osg.Vec3(2 * config.ASPECT_RATIO, 0, 0)
        height = osg.Vec3(0, 2 * 1.0, 0)
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

    def resetSceneData(self, data):
        self.timer.stop()
        if self.viewer == None:
            return
        self.viewer.setSceneData(None)
        
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

    def setSceneData(self, data):
        if data != None:
            if self.viewer == None:
                self.viewer = self.createViewer()
            data = self.build_wrapping_node(data)
            self.viewer.setSceneData(data)

        # ready to render
        self.fps_calculator.reset(self.startTime)
        self.still_frame = False
        self.timer.start()

    def setAudioData(self, data, skip=0.0):
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None
        self.audio_data = data
        self.audio_skip = float(skip)
        self.audio = SoundPlayer(input_file_name=data, tmp_dir=jarvis.get_home(), start=False, loop_nb=0, frames_per_buffer=1024, blocking=False)
        self.audio.set_loop_time(start_time=self.audio_skip, end_time=self.audio_skip + self.loopTime)        
        self.audio.set_time(self.audio_skip + self.current_time, compensate_buffer=False)

    def getosgviewer(self):
        return self.viewer

    def resizeGL( self, w, h ):
        if self.viewer == None:
            return 
        self.gw.resized(0,0,w,h)
        self.resetCamera(self.viewer)

    def paintGL(self):
        if self.viewer == None:
            return

        frame_time = time.time()

        if self.audio is not None :
            if self.is_paused or self.still_frame:
                self.audio.pause()
            else:
                self.audio.play(blocking=False)
            audio_time = self.audio.get_time() - self.audio_skip
            # self.current_time = self.align_time(audio_time)
            self.current_time = audio_time
        else:
            if self.is_paused or self.still_frame:
                self.startTime = frame_time - self.current_time
            else:                
                self.current_time = frame_time - self.startTime
                if self.current_time >= self.loopTime:
                    self.startTime = frame_time
                    self.current_time = 0.0

        fps = self.fps_calculator.get(frame_time)
        self.parent.toolbar.update_time_info(self.current_time, self.loopTime, fps)
        
        self.viewer.frameAtTime(self.current_time)

    def align_time(self, t):
        return min(self.loopTime, max(0.0, round(t * config.FPS_UI) / config.FPS_UI))

    def update_time(self, from_ratio=None, from_delta=None):
        if from_ratio is not None:
            self.current_time = self.align_time(self.loopTime * from_ratio)
            self.startTime = time.time() - self.current_time

        elif from_delta is not None:
            self.current_time = self.align_time(self.current_time + from_delta)
            self.startTime = time.time() - self.current_time

        if self.audio is not None:
            self.audio.set_time(self.audio_skip + self.current_time, compensate_buffer=False)

    def pause(self):
        self.is_paused = True

    def play(self):
        self.is_paused = False
        
    def mousePressEvent( self, event ):
        """put the qt event in the osg event queue"""
        self.still_frame = True
        button = mouseButtonDictionary.get(event.button(), 0)
        self.update_time(from_ratio=float(event.x()) / float(self.width()))
        self.gw.getEventQueue().mouseButtonPress(event.x(), event.y(), button)

    def mouseMoveEvent(self, event):
        """put the qt event in the osg event queue"""
        self.update_time(from_ratio=float(event.x()) / float(self.width()))
        self.gw.getEventQueue().mouseMotion(event.x(), event.y())

    def mouseReleaseEvent( self, event ):
        """put the qt event in the osg event queue"""
        button = mouseButtonDictionary.get(event.button(), 0)
        self.gw.getEventQueue().mouseButtonRelease(event.x(), event.y(), button)
        self.still_frame = False

    def getGraphicsWindow(self):
        """returns the osg graphicswindow created by osgViewer """
        return self.gw

