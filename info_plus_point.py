from qgis.gui import *
from qgis.core import *
from PyQt4.Qt import *
from ui.info_plus_dialog import InfoPlusDialog


class InfoPlusPoint(QgsMapTool):

    def __init__(self, canvas, action):
        self.canvas = canvas
        self.active = False
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
    
    
    def canvasPressEvent(self, e):
    
        p = self.toMapCoordinates(e.pos())      
        layers = self.canvas.layers()
        w = self.canvas.mapUnitsPerPixel() * 3
        rect = QgsRectangle(p.x()-w, p.y()-w, p.x()+w, p.y()+w)
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                continue
            lRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, rect)
            layer.select(lRect, False)
        
        # Remove selection of all layers
        #self.clear()
        
        # Create new dialog
        self.dlg = InfoPlusDialog()
        
        # Iterate over all layers
        self.layers = self.iface.mapCanvas().layers()
        self.processLayers()
        
        # Show dialog
        self.dlg.show()
        
    
    def processLayers(self):

        i = 0    
        self.dlg.tbMain.setCurrentIndex(i)    
        for layer in self.layers:
            # If have any feature selected
            if layer.selectedFeatureCount() > 0:
                aux = layer.name()+" ("+str(layer.selectedFeatureCount())+")" 
                if i > 1:
                    self.newPage = QWidget()
                    self.newPage.setObjectName("page_"+str(i))
                    self.dlg.tbMain.addItem(self.newPage, aux)
                self.dlg.tbMain.setItemText(i, aux)
                self.pageIndex = i
                self.processLayer(layer)
                i = i+1

                
    def processLayer(self, layer):
        
        # Get selected features of current layers
        i = 1
        total = layer.selectedFeatureCount()
        print ""
        for feature in layer.selectedFeatures():
            print "Feature "+str(i)+ " of "+str(total)
            self.processFeature(feature)
            i = i + 1
        
    
    def processFeature(self, feature):
        
        for field in feature.fields():
            msg = field.name()+" - "+str(feature[field.name()])
            print msg
        print "\n----------------------------------------\n"            
        #self.label = QtGui.QLabel(self.page_0)
        #self.label.setGeometry(QtCore.QRect(20, 20, 221, 16))
        #self.label.setObjectName(_fromUtf8("label"))
        #self.tbMain.addItem(self.page_0, _fromUtf8(""))            
    
    def setInterface(self, iface):
        self.iface = iface
    
    def clear(self):
        # Remove selection of all layers
        layers = self.iface.mapCanvas().layers()
        for layer in layers:
            print layer.name()
            layer.removeSelection()
            
    def deactivate(self):
        pass
        #if self is not None:
        #    QgsMapTool.deactivate(self)
        
    def activate(self):
        QgsMapTool.activate(self)
    