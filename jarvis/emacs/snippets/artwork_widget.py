from jarvis import *
import stupeflix.artwork.kinetictypo.basic as basic
from lxml import etree

class Widget():
    @staticmethod
    def defaultDuration(xmlNode):
        return 5.0

    kind = "OSGWidget"
    def __init__(self, xmlNode):        
        self.xmlNode = xmlNode
        self.text = etree.tostring(self.xmlNode, method="text")
        self.duration  = float(self.xmlNode.get("duration"))
        self.startTimee  = float(self.xmlNode.get("startTime"))
    
    def osgNodeGet(self):
        b = basic.{{Class}}(self.text.strip())
        return b.osgNodeGet()
