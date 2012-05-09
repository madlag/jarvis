import osg
import osgGA
import osgDB
import osgViewer
import sys
import math
import OpenGL.GL as GL
import threading
from jarvis import *
import time

osg.Vec3 = osg.Vec3f
osg.Matrix = osg.Matrixd

debug_viewer = None

#threading.Thread
class DebugViewer():
    def __init__(self, width = 480, height = 270):
        self.width = width
        self.height = height
        self.viewer = None
        self.camera = None
        self.daemon = True

    @staticmethod
    def init(width = 480, height=270):
        global debug_viewer
        if debug_viewer == None:
            debug_viewer = DebugViewer(width, height)
            debug_viewer.viewerBuild()
            debug_viewer.set_data(debug_viewer.main2())
            
        return debug_viewer

    def main2(self):
        w = -16.0 / 9.0 * 2.0
        h = 1.0 * 2.0
        corner = osg.Vec3(-w/2.0,-h/2, 0)
        width = osg.Vec3(w,0,0)
        height = osg.Vec3(0,h,0)
        geom = osg.createTexturedQuadGeometry(corner, width, height, 0.0, 0.0, 1.0, 1.0)
        uv1 = osg.Vec2Array()
        uv1.push_back(osg.Vec2(0.0, 1.0))
        uv1.push_back(osg.Vec2(0.0, 0.0))
        uv1.push_back(osg.Vec2(1.0, 0.0))
        uv1.push_back(osg.Vec2(1.0, 1.0))
        geom.setTexCoordArray(1, uv1)

        geode = osg.Geode()
        geode.addDrawable(geom)

        image = osgDB.readImageFile("/Users/lagunas/devel/stupeflix/sandbox/png/lena.png")
        texture = osg.Texture2D(image)

        geom.getOrCreateStateSet().setTextureAttributeAndModes(0, texture)

        return geode


    def viewerBuild(self):
        if self.viewer != None:
            return

        # Standard size
        size = (self.width, self.height)
        screen_ratio = float(size[0]) / float(size[1])

        # Build the camera
        CAMERA_ANGLE = 45.0
        CAMERA_Z_TRANSLATE = 1.0 / math.tan(math.radians(CAMERA_ANGLE / 2.0))
    
        cameraPosition = [0.0, 0.0, CAMERA_Z_TRANSLATE]

        camera = osg.Camera()

        # Setup the viewport
        camera.setViewport(osg.Viewport(0,0,size[0], size[1]))
        camera.setReferenceFrame(osg.Transform.ABSOLUTE_RF)
        position = cameraPosition
        camera.setProjectionMatrixAsPerspective(CAMERA_ANGLE, screen_ratio, 0.1, 100.0)
        camera.getOrCreateStateSet().setAttributeAndModes(osg.BlendFunc(GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA))
        camera.getOrCreateStateSet().setMode(GL.GL_LIGHTING, False)
        material = osg.Material()
        color = osg.Vec4(1.0,1.0,1.0,1.0)
        material.setDiffuse(osg.Material.FRONT_AND_BACK, color)
        material.setAmbient(osg.Material.FRONT_AND_BACK, color)
        camera.getOrCreateStateSet().setAttributeAndModes(material)
        camera.setClearColor(osg.Vec4(0,0,0,0))
        camera.setClearMask(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        eye = osg.Vec3d(cameraPosition[0], cameraPosition[1], cameraPosition[2])
        center = osg.Vec3d(0,0,0)
        up = osg.Vec3d(0,1,0)
        camera.setViewMatrixAsLookAt(eye, center, up)


        # Create the viewer
        viewer = osgViewer.Viewer()
        viewer.setSceneData(camera)

        self.viewer = viewer
        self.camera = camera
        
        viewer.setUpViewInWindow(0,0, size[0], size[1])
        viewer.addEventHandler(osgViewer.HelpHandler());
        viewer.addEventHandler(osgViewer.StatsHandler());
        viewer.addEventHandler(osgViewer.ThreadingHandler())
        viewer.setThreadingModel(osgViewer.ViewerBase.SingleThreaded)
        
    def set_data(self, scene_data):
        if self.camera == None:
            return
        if self.camera.getNumChildren() == 1:
            self.camera.removeChild(0)
        if scene_data != None:
            self.camera.addChild(scene_data)

    def run(self):
        print dir(self.viewer)
        self.viewer.run()
        


