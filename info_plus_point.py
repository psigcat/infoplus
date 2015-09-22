import json
from collections import OrderedDict

from qgis.gui import *
from qgis.core import *
from PyQt4.Qt import *

from ui.info_plus_dialog import InfoPlusDialog
from ui.records_display_widget import RecordsDisplayWidget
from template.records_display_widget_bridge import RecordsDisplayWidgetBridge 


class InfoPlusPoint(QgsMapTool):

    def __init__(self, canvas, action):
        self.canvas = canvas
        self.active = False
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
        
        self.recordsDisplayWidgetBridge = None
        self.newPage = None
        self.selectedLayerId = None
        self.selectedFeatureId = None
    
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
        self.dlg.center_PButton.clicked.connect(self.centerSelectedFeature)
        self.dlg.zoom_PButton.clicked.connect(self.zoomSelectedFeature)
        
        # Iterate over all layers
        self.layers = self.iface.mapCanvas().layers()
        self.processLayers()
        
        # Show dialog
        self.dlg.show()
    
    def zoomSelectedFeature(self):
        ''' zoom to the selected feature
        '''
        if not self.selectedLayerId or not self.selectedFeatureId:
            return
        
        # for now... do nothing!
    
    def centerSelectedFeature(self):
        ''' pan to the selected feature
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
        
        # if point or line 
        if (geometry.type == QGis.Point) or (geometry.type == QGis.Line):
            centroid = geometry.centroid().asPoint()
            self.canvas.setCenter(centroid)
        else:
            bbox = geometry.boundingBox()
            self.canvas.setExtent(bbox)
        
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
        for i, layer in enumerate(self.layers):
            # If have any feature selected
            if layer.selectedFeatureCount() > 0:
                aux = layer.name()+" ("+str(layer.selectedFeatureCount())+")" 
                self.newPage = RecordsDisplayWidget(self.iface.mainWindow())
                self.newPage.setObjectName("page_"+str(i))
                self.processLayer_asAccordion(layer)
                self.dlg.tbMain.addItem(self.newPage, aux)
                
    def processLayer_asAccordion(self, layer):
        # Get selected features of current layers
        columns = [field.name() for field in layer.pendingFields().toList()]
        total = len(layer.selectedFeatures())
        features = {'name': 'Records',
                    'children': []}
        for i, feature in enumerate(layer.selectedFeatures()):
            print "Feature "+str(i)+ " of "+str(total)
            
            item = {'name': 'id: {}'.format(feature.id()),
                    'children': []} 
            
            # add records
            values = feature.attributes()
            namedValues = zip(columns, values)
            
            for key, value in namedValues:
                record = {'name': key,
                          'value': value if value != None else 'NULL'}
                item['children'].append(record)
                
            print item
            features['children'].append( item )
        
        if len(features) == 0:
            return
        
        self.processFeatures_asAccordion(layer.id(), features)
        
    def processFeatures_asAccordion(self, layerId, featuresDicts):
        ''' Push record in the webView
        '''
        if self.newPage:
            # first inject bridge object
            self.newPage.webView.page().mainFrame().addToJavaScriptWindowObject("recordsDisplayWidgetBridge", self.recordsDisplayWidgetBridge)
            
            # then render records
            jsonString = json.dumps(featuresDicts)
            
            JsCommand = "showRecords('%s', '%s')" % (layerId, jsonString)
            QgsLogger.debug(self.tr("display records with with JS command: %s" % JsCommand), 3)
            
            self.newPage.webView.page().mainFrame().evaluateJavaScript(JsCommand)
    
    def processLayer_asTable(self, layer):
        # Get selected features of current layers
        columns = [field.name() for field in layer.pendingFields().toList()]
        total = len(layer.selectedFeatures())
        featuresDicts = []
        for i, feature in enumerate(layer.selectedFeatures()):
            print "Feature "+str(i)+ " of "+str(total)
            
            items = [('featureId', feature.id())]
            values = feature.attributes()
            items.extend( zip(columns, values) )
            featureDict = OrderedDict(items)
            
            for key, value in featureDict.items():
                if value == None:
                    featureDict[key] = 'NULL'
            
            print featureDict
            featuresDicts.append( featureDict )
        
        if len(featuresDicts) == 0:
            return
        
        self.processFeatures(layer.id(), featuresDicts)
        
    def processFeatures_asTable(self, layerId, featuresDicts):
        ''' Push record in the webView
        '''
        if self.newPage:
            # first inject bridge object
            self.newPage.webView.page().mainFrame().addToJavaScriptWindowObject("recordsDisplayWidgetBridge", self.recordsDisplayWidgetBridge)
            
            # then render records
            jsonString = json.dumps(featuresDicts)
            
            JsCommand = "showRecords('%s', '%s')" % (layerId, jsonString)
            QgsLogger.debug(self.tr("display records with with JS command: %s" % JsCommand), 3)
            
            self.newPage.webView.page().mainFrame().evaluateJavaScript(JsCommand)
    
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
    