# -*- coding: utf-8 -*-
"""
/***************************************************************************
    A QGIS plugin for Road contamination modelling for EMSURE Project
                              -------------------
        begin                : 2015-04-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli (for EMSURE project)º
        email                : luipir@gmail.lcom
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import collections
import traceback
import json
from PyQt4 import QtCore
from qgis.core import QgsLogger

class RecordsDisplayWidgetBridge(QtCore.QObject):
    ''' Class used to receive statistic modification from JS and bridge to Python
    '''
    selectedRecord = QtCore.pyqtSignal(str, str)
    highlightRecord = QtCore.pyqtSignal(str, str)
    linkClicked = QtCore.pyqtSignal(str, str, str)
    docClicked = QtCore.pyqtSignal(str, str, str)

    def __init__(self):
        """Constructor."""
        super(RecordsDisplayWidgetBridge, self).__init__()
        
    @QtCore.pyqtSlot(str, str)
    def setSelctedRecord(self, layerId=None, featureId=None):
        '''
        slot emitted by JS to communicate the current Layer/featureId selected in the interface
        '''
        QgsLogger.debug("RecordsDisplayWidgetBridge.setSelctedRecord: Selected layerId = {} and record id {}".format(layerId, featureId), 3)
        
        if layerId and featureId:
            self.selectedRecord.emit(layerId, featureId)

    @QtCore.pyqtSlot(str, str)
    def setHilightRecord(self, layerId=None, featureId=None):
        '''
        slot emitted by JS to communicate the current Layer/featureId have to be highlighted
        '''
        QgsLogger.debug("RecordsDisplayWidgetBridge.setHilightRecord: on mouse over layerId = {} and record id {}".format(layerId, featureId), 3)
        
        if layerId and featureId:
            self.highlightRecord.emit(layerId, featureId)

    @QtCore.pyqtSlot(str, str, str)
    def notifyLinkClicked(self, layerId=None, featureId=None, link=None):
        '''
        slot emitted by JS to communicate that a hyperlink has been clicked.
        event return the Layer/featureId of the click and the web address clicked
        '''
        QgsLogger.debug("RecordsDisplayWidgetBridge.notifyClicked: Clicked hyperlnk = {} on layerId = {} and record id {}".format(link, layerId, featureId), 3)
        
        if layerId and featureId and link:
            self.linkClicked.emit(layerId, featureId, link)

    @QtCore.pyqtSlot(str, str, str)
    def notifyDocClicked(self, layerId=None, featureId=None, document=None):
        '''
        slot emitted by JS to communicate that a document has been clicked.
        event return the Layer/featureId of the click and the value of the document filename
        Does not care if document filename is relative or absolute... that's is managed by 
        listeners of this event
        '''
        QgsLogger.debug("RecordsDisplayWidgetBridge.notifyDocClicked: Clicked doc = {} on layerId = {} and record id {}".format(document, layerId, featureId), 3)
        
        if layerId and featureId and document:
            self.docClicked.emit(layerId, featureId, document)
