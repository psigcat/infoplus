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

    def __init__(self):
        """Constructor."""
        super(RecordsDisplayWidgetBridge, self).__init__()
        
    @QtCore.pyqtSlot(str, str)
    def setSelctedRecord(self, layerId=None, cat=None):
        '''
        slot emitted by JS to communicate the current Layer/cat selected in the interface
        '''
        QgsLogger.debug("RecordsDisplayWidgetBridge.setSelctedRecord: Selected layerId = {} and record cat {}".format(layerId, cat), 3)
        
        if layerId and cat:
            self.selectedRecord.emit(layerId, cat)
