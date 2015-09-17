# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'records_display_widget.ui'))

class RecordsDisplayWidget(QtGui.QWidget, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(RecordsDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        
        # att HTML template and JS code to the web view
        self.initWebView()
        
    def initWebView(self):
        ''' Init the webView with the record template and JS usefult to 
            show record table
        '''
        # get the upper directory of the current file that is in the "ui" directory
        pluginPath = os.path.dirname(os.path.dirname(__file__))
        webPage = os.path.join(pluginPath, "template", "index.html")
        self.webView.load(QtCore.QUrl.fromLocalFile(webPage))
        
