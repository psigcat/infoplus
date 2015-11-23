# -*- coding: utf-8 -*-
import os
import json

from PyQt4 import QtCore, QtGui, uic
from qgis.core import QgsLogger

from template.records_display_widget_bridge import RecordsDisplayWidgetBridge 

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'records_display_widget.ui'))


class RecordsDisplayWidget(QtGui.QWidget, FORM_CLASS):
    
    # signal emitted quen the webView is compleated loaded
    ready = QtCore.pyqtSignal(bool)
    docClicked = QtCore.pyqtSignal(str, str, str)    
    linkClicked = QtCore.pyqtSignal(str, str, str)
    highlightRecord = QtCore.pyqtSignal(str, str)
    
    def __init__(self, layer, parent):
        """Constructor."""
        super(RecordsDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        
        # status flags
        self._layer = layer
        self._selectedLayerId = None
        self._selectedFeatureId = None
        self._ready = False
        self._recordsDisplayWidgetBridge = RecordsDisplayWidgetBridge()
        self._recordsDisplayWidgetBridge.selectedRecord.connect(self._setSelectedRecord)
        self._recordsDisplayWidgetBridge.docClicked.connect(self._docClicked)
        self._recordsDisplayWidgetBridge.linkClicked.connect(self._linkClicked)
        self._recordsDisplayWidgetBridge.highlightRecord.connect(self._highlightRecord)
       
        # att HTML template and JS code to the web view
        self.initWebView()
        
        
    def initWebView(self):
        ''' Init the webView with the record template and JS usefult to 
            show record table
        '''
        # check status of webView loading
        self.webView.loadStarted.connect(self._setNotReady)
        self.webView.loadFinished.connect(self._initWebContent)
        
        # get the upper directory of the current file that is in the "ui" directory
        pluginPath = os.path.dirname(os.path.dirname(__file__))
        webPage = os.path.join(pluginPath, "template", "index.html")
        
        self.webView.load(QtCore.QUrl.fromLocalFile(webPage))
    
    
    def setName(self, name):
        self.name = name
        
        
    def setRemoveSelection(self, removeSelection):
        self.removeSelection = removeSelection        
        
        
    def isReady(self):
        ''' Status of the loaded webView
        '''
        return self._ready
    
    
    def _setNotReady(self):
        ''' Set that current webPage is not ready to be managed
        '''
        self._ready = False
    
    
    def _initWebContent(self, success):
        ''' Set status of page loading
        '''
        if not success:
            return
        
        # first inject bridge object
        self.webView.page().mainFrame().addToJavaScriptWindowObject("recordsDisplayWidgetBridge", self._recordsDisplayWidgetBridge)
        
        # wait a while before loading records
        QtCore.QTimer.singleShot(300, self._displayRecords)
        
        
    def _displayRecords(self):
        ''' after a while show records... this give time that the bridge is available in JS
        '''
        if self._layer.selectedFeatureCount():
            # then prepare selected records in structure usefut for accordion visualization
            featuresDict = self._prepareFeatures_asAccordion()
            
            # prepare js command to execute in the page
            jsonString = json.dumps(featuresDict)
            
            JsCommand = "showRecords('%s', %s)" % (self._layer.id(), jsonString) # <<< jsonString is automatically converted in javascript obj during evaluate
            QgsLogger.debug(self.tr("display records with with JS command: %s" % JsCommand), 3)
            
            # show records
            self.webView.page().mainFrame().evaluateJavaScript(JsCommand)
        
        else:
            QgsLogger.debug(self.tr("No features selected to display for layer: %s" % self._layer.id()), 1)

        # then we can say that the load is completed
        self._ready = True
        
        # Check if we want to remove selection of this layer
        if self.removeSelection:
            self._layer.removeSelection()      
        
        # notify it is ready
        self.ready.emit(self._ready)
    
    
    def _prepareFeatures_asAccordion(self):
        ''' Prepare selected records in a structure useful for accordion visualization
        '''
        # Get selected features of current layers
        columns = [field.name() for field in self._layer.pendingFields().toList()]
        featuresDict = {'name': self.name, 'children': []}
        for i, feature in enumerate(self._layer.selectedFeatures()):
            item = {'name': feature.id(), 'children': []} 
            
            # add records
            values = feature.attributes()
            namedValues = zip(columns, values)
            
            for key, value in namedValues:
                record = {'name': key, 'value': value if value != None else 'NULL'}
                item['children'].append(record)
                
            featuresDict['children'].append( item )
        
        return featuresDict


    def _setSelectedRecord(self, layerId, featureId):
        ''' Set current selected Record and layer
        '''
        QgsLogger.debug("RecordsDisplayWidget._setSelectedRecord: Selected layerId = {} and record id {}".format(layerId, featureId), 3)

        self._selectedLayerId = layerId
        self._selectedFeatureId = int(featureId)
    
    
    def _highlightRecord(self, layerId, featureId):
        ''' Set current hilighted Record and layer
        '''
        QgsLogger.debug("RecordsDisplayWidget._highlightRecord: on mouse over layerId = {} and record id {}".format(layerId, featureId), 3)
        
        if layerId and featureId:
            self.highlightRecord.emit(layerId, featureId)
    
    
    def _docClicked(self, layerId, featureId, document):
        ''' re emit signal that a document has been clicked
        '''
        self.docClicked.emit(layerId, featureId, document)
    
    
    def _linkClicked(self, layerId, featureId, link):
        ''' re emit signal that a link document has been clicked
        '''
        self.linkClicked.emit(layerId, featureId, link)
    
    
    def getSelection(self):
        ''' return current selection touple (that can be none,none if no selection)
        '''
        return self._selectedLayerId, self._selectedFeatureId
    
    