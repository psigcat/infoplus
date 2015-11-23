import json
import time
import os
import subprocess
import platform

from qgis.gui import * # @UnusedWildImport
from qgis.core import * # @UnusedWildImport
from PyQt4.Qt import * # @UnusedWildImport
from PyQt4 import QtCore, QtGui

from ui.info_plus_dialog import InfoPlusDialog
from ui.records_display_widget import RecordsDisplayWidget


class InfoPlusRectangle(QgsMapTool):

    def __init__(self, canvas, action, settings):
        self.canvas = canvas
        self.active = False
        self.settings = settings
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
        self.defaultZoomScale = None
        self.currentHighlight = None
        self.loadInfoPlusPointSettings()

        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        mFillColor = QColor(254, 178, 76, 63);
        self.rubberBand.setColor(mFillColor)
        self.rubberBand.setWidth(1)
        self.reset()
        

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QGis.Polygon)
    
    
    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)
    
    
    def canvasReleaseEvent(self, e):
    
        # Remove selection of all layers
        self.clearCanvas()
        
        self.isEmittingPoint = False
        r = self.rectangle()
        layers = self.canvas.layers()
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                continue
            if r is not None:
                lRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, r)
                layer.select(lRect, False)
                
        self.rubberBand.hide()
        
        # Create new dialog
        self.dlg = InfoPlusDialog()
        
        # add listener to selected layer/record
        self.dlg.center_PButton.clicked.connect(self.doZoomCenterAction)
        self.dlg.zoom_PButton.clicked.connect(self.doZoomCenterAction)
        
        # Iterate over all layers
        self.layers = self.canvas.layers()
        self.processLayers()
        
        # Show dialog
        self.dlg.show()
            
    
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates( e.pos() )
        self.showRect(self.startPoint, self.endPoint)
    
    
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QGis.Polygon)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
        point1 = QgsPoint(startPoint.x(), startPoint.y())
        point2 = QgsPoint(startPoint.x(), endPoint.y())
        point3 = QgsPoint(endPoint.x(), endPoint.y())
        point4 = QgsPoint(endPoint.x(), startPoint.y())
    
        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)    # true to update canvas
        self.rubberBand.show()
    
    
    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None
    
        return QgsRectangle(self.startPoint, self.endPoint)
    
    
    def loadInfoPlusPointSettings(self):
        ''' Load plugin settings
        '''      
        self.defaultZoomScale = self.settings.value('status/defaultZoomScale', 2500)        
        self.highlightTime = int(self.settings.value('status/highlightTime', 1000))

        
    def doZoomCenterAction(self):
        ''' pan or zoom to the selected feature. Depend on sender
        '''
        # get current selection from current QToolBox
        currentPage = self.dlg.tbMain.currentWidget()
        (selectedLayerId, selectedFeatureId) = currentPage.getSelection()
        
        QgsLogger.debug("InfoPlusPoint.doZoomCenterAction: Selected layerId = {} and record id {}".format(selectedLayerId, selectedFeatureId), 3)
        
        # check if something is selected
        if (not selectedLayerId) or (not selectedFeatureId):
            return
        
        # get current selected layer
        layer = QgsMapLayerRegistry.instance().mapLayer(selectedLayerId)
        if (not layer) or (not layer.isValid()):
            return
        
        # get feature with the specific featureId
        iterator = layer.getFeatures(QgsFeatureRequest(selectedFeatureId))
        try:
            feature = iterator.next()
        except:
            # no feature found
            return
        
        # depending on geometry do different actions
        geometry = feature.geometry()
        
        # skip if not valid
        if (geometry.type() == QGis.UnknownGeometry) or (geometry.type() == QGis.NoGeometry):
            return
        
        # distinguish if action have to be center or zoom
        centroid = geometry.centroid().asPoint()

        self.canvas.setCenter(centroid)
        if self.sender().objectName() == 'zoom_PButton':
            # scale of bbox depending on geom type           
            if geometry.type() == QGis.Point:
                self.canvas.zoomScale(float(self.defaultZoomScale))                    
            else:
                self.canvas.setExtent(geometry.boundingBox())
        
        self.canvas.refresh()

    
    def processLayers(self):
        
        # clean all toolBox elements if any, starting from the last
        # to avoid index invalidation 
        for index in range(self.dlg.tbMain.count() - 1, -1, -1):
            self.dlg.tbMain.removeItem(index)
        
        # create and populate webpage
        for layer in self.layers:
            # If have any feature selected
            if layer.selectedFeatureCount() > 0:
                newPage = RecordsDisplayWidget(layer, self.iface.mainWindow())
                newPage.setObjectName('page_' + layer.id())
                
                # record listener to open PDF or link is cliked
                newPage.docClicked.connect(self.manageDocClicked)
                newPage.linkClicked.connect(self.manageLinkClicked)
                newPage.highlightRecord.connect(self.manageHighlight)
                
                # set tab name witht the record count
                aux = layer.name()+" ("+str(layer.selectedFeatureCount())+")" 
                self.dlg.tbMain.addItem(newPage, aux)
    

    def manageHighlight(self, layerId, featureId):
        ''' Hilight record that is currently under the mouse
        ''' 
        # check if something is selected
        if (not layerId) or (not featureId):
            return
        
        # get current selected layer
        layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        if (not layer) or (not layer.isValid()):
            return
        
        # get feature with the specific featureId
        iterator = layer.getFeatures(QgsFeatureRequest(int(featureId)))
        try:
            feature = iterator.next()
        except:
            # no feature found
            return
        
        # depending on geometry do different actions
        geometry = feature.geometry()
        
        # skip if not valid
        if (geometry.type() == QGis.UnknownGeometry) or (geometry.type() == QGis.NoGeometry):
            return
        
        # create Hilight
        self.currentHighlight = QgsHighlight(self.canvas, geometry, layer)
        
        # set standard style
        color = QtGui.QColor( self.settings.value( "/Map/highlight/color", QGis.DEFAULT_HIGHLIGHT_COLOR.name() ) )
        alpha = int( self.settings.value( "/Map/highlight/colorAlpha", QGis.DEFAULT_HIGHLIGHT_COLOR.alpha() ))
        buffer = float(self.settings.value( "/Map/highlight/buffer", QGis.DEFAULT_HIGHLIGHT_BUFFER_MM ))
        minWidth = float(self.settings.value( "/Map/highlight/minWidth", QGis.DEFAULT_HIGHLIGHT_MIN_WIDTH_MM ))
        
        self.currentHighlight.setColor( color ) # sets also fill with default alpha
        color.setAlpha( alpha )
        self.currentHighlight.setFillColor( color ) # sets fill with alpha
        self.currentHighlight.setBuffer( buffer )
        self.currentHighlight.setMinWidth( minWidth )
        self.currentHighlight.show()
        
        # remove highlight after a while
        QtCore.QTimer.singleShot(self.highlightTime, self._removeHighlight)
    
    
    def _removeHighlight(self):
        ''' remove current Highlight
        '''
        if self.currentHighlight:
            del self.currentHighlight
            self.currentHighlight = None
    
    
    def manageDocClicked(self, layerId, featureId, document):
        ''' Open a doc document that has been clicked
        '''
        # manage filepath if absolute or relaltive
        filepath = document
        if not os.path.isabs(filepath):
            filepath = os.path.join( os.path.dirname(__file__), filepath)
        
        # check if exist
        if not os.path.exists(filepath):
            self.iface.messageBar().pushWarning('', self.tr('File {} does not exist'.format(filepath)))
            return
        
        if not os.path.isfile(filepath):
            self.iface.messageBar().pushWarning('', self.tr('{} is not a file'.format(filepath)))
            return
                
        # then open
        self._openUri(filepath)
              
    
    def manageLinkClicked(self, layerId, featureId, link):
        ''' Open a link that has been clicked
        '''
        self._openUri(link)
    
    
    def _openUri(self, uri):
        ''' Usefult to open Uri using default desktop application
        '''
        platformName = platform.system().lower()
        if platformName.startswith('linux'):
            subprocess.call(('xdg-open', uri))
        elif platformName.startswith('win') or platformName.startswith('cygwin'):
            os.startfile(uri)
        elif platformName.startswith('darwin'):
            subprocess.call(('open', uri))
    
    
    def setInterface(self, iface):
        self.iface = iface
    
    
    def clearCanvas(self):
        # Remove selection of all layers
        layers = self.iface.mapCanvas().layers()
        for layer in layers:
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
        self.iface.mapCanvas().refresh()   
            
    
    def deactivate(self):
        self.rubberBand.hide()
        QgsMapTool.deactivate(self)
        

    def activate(self):
        QgsMapTool.activate(self)
    