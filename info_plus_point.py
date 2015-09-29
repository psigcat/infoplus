import json
import time
from collections import OrderedDict

from qgis.gui import *
from qgis.core import *
from PyQt4.Qt import *

from ui.info_plus_dialog import InfoPlusDialog
from ui.records_display_widget import RecordsDisplayWidget
from template.records_display_widget_bridge import RecordsDisplayWidgetBridge 


class InfoPlusPoint(QgsMapTool):

    def __init__(self, canvas, action, settings):
        self.canvas = canvas
        self.active = False
        self.settings = settings
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
        
        self.recordsDisplayWidgetBridge = None
        self.newPage = None
        self.selectedLayerId = None
        self.selectedFeatureId = None
        self.defaultZoomScale = None
        
        self.loadInfoPlusPointSettings()
    
    def loadInfoPlusPointSettings(self):
        ''' Load plugin settings
        '''      
        # get initial Scale
        self.defaultZoomScale = self.settings.value('status/defaultZoomScale', 2500)

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
        
        # add listener to selected layer/record
        self.dlg.center_PButton.clicked.connect(self.doZoomCenterAction)
        self.dlg.zoom_PButton.clicked.connect(self.doZoomCenterAction)
        
        # Iterate over all layers
        self.layers = self.iface.mapCanvas().layers()
        self.processLayers()
        
        # Show dialog
        self.dlg.show()
    

    def doZoomCenterAction(self):
        ''' pan or zoom to the selected feature. Depend on sender
        '''
        if (not self.selectedLayerId) or (not self.selectedFeatureId):
            return
        
        # get current selected layer
        layer = QgsMapLayerRegistry.instance().mapLayer(self.selectedLayerId)
        if (not layer) or (not layer.isValid()):
            return
        
        # get feature with the specific featureId
        request = QgsFeatureRequest( self.selectedFeatureId )
        iterator = layer.getFeatures(request)
        try:
            feature = iterator.next()
        except:
            # no feature found
            return
        
        # depending on geometry do different actions
        geometry = feature.geometry()
        
        # skip if not valid
        if (geometry.type == QGis.UnknownGeometry) or (geometry.type == QGis.NoGeometry):
            return
        
        # distinguish if action have to be center or zoom
        centroid = geometry.centroid().asPoint()

        self.canvas.setCenter(centroid)
        if self.sender().objectName() == 'zoom_PButton':
            # scale of bbox depending on geom type
            if geometry.type == QGis.Point:
                self.iface.mapCanvas().zoomScale( float(self.defaultZoomScale) )
            else:
                self.canvas.setExtent( geometry.boundingBox() )
        
        self.canvas.refresh()

    
    def setSelectedRecord(self, layerId, featureId):
        ''' Set current selected Record and layer
        '''
        QgsLogger.debug("InfoPlusPoint.setSelectedRecord: Selected layerId = {} and record id {}".format(layerId, featureId), 3)

        self.selectedLayerId = layerId
        self.selectedFeatureId = int(featureId)
    
    def processLayers(self):
        
        # clean all toolBox elements if any, starting from the last
        # to avoid index invalidation 
        for index in range(self.dlg.tbMain.count() - 1, -1, -1):
            self.dlg.tbMain.removeItem(index)
        
        # create unique bridge for all web pages
        self.recordsDisplayWidgetBridge = RecordsDisplayWidgetBridge()
        self.recordsDisplayWidgetBridge.selectedRecord.connect(self.setSelectedRecord)
        
        # create and populate webpage
        for layer in self.layers:
            # If have any feature selected
            if layer.selectedFeatureCount() > 0:
                self.newPage = RecordsDisplayWidget(layer, self.recordsDisplayWidgetBridge, self.iface.mainWindow())
                self.newPage.setObjectName('page_' + layer.id())
                
                # set tab name witht the record count
                aux = layer.name()+" ("+str(layer.selectedFeatureCount())+")" 
                self.dlg.tbMain.addItem(self.newPage, aux)
    
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
    