# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfoPlus - A QGIS plugin
                              -------------------
        begin                : 2015-07-31
        git sha              : $Format:%H$
        copyright            : (C) 2015 by David Erill
        email                : daviderill79@gmail.com
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
from qgis.utils import active_plugins
from qgis.gui import (QgsMessageBar)
from qgis.core import (QgsGeometry, QgsPoint, QgsLogger)
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtWebKit

import resources_rc
from info_plus_point import InfoPlusPoint
from info_plus_rectangle import InfoPlusRectangle

import os.path
import sys  


class InfoPlus(QObject):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        super(InfoPlus, self).__init__()
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.pluginName = os.path.basename(self.plugin_dir)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'InfoPlus_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
        # load local settings of the plugin
        settingFile = os.path.join(self.plugin_dir, 'config', 'infoplus.config')
        self.settings = QSettings(settingFile, QSettings.IniFormat)
        self.settings.setIniCodec(sys.getfilesystemencoding())
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&infoplus')
        
        self.toolbar = self.iface.addToolBar(u'InfoPlus')
        self.toolbar.setObjectName(u'InfoPlus')
        
        # global settings for web componets
        self.initWebKitSettings()
    
    def initWebKitSettings(self):
        ''' Set global configuration for WebKit components
        '''
        # set webView setting
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.SpatialNavigationEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PrintElementBackgrounds, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, False)

        
    def createToolButton(self, parent, text):
        button = QToolButton(parent)
        button.setObjectName(text)
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        button.setPopupMode(QToolButton.MenuButtonPopup)
        parent.addWidget(button)
        return button

        
    def createAction(self, icon_path, text, callback):
        action = QAction(QIcon(icon_path), text, self.iface.mainWindow())
        # connect the action to the run method
        action.setCheckable(True)
        action.toggled.connect(callback)
        return action

        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        #icon_path = ':/plugins/InfoPlus/icon_infoplus.png'
        #self.add_action(icon_path, text=self.tr(u'Cercador avançat'), callback=self.run, parent=self.iface.mainWindow())

        # Create the dock widget and dock it but hide it waiting the ond of qgis loading
        #self.dlg = InfoPlusDialog(self.iface.mainWindow())
        
        # Create action that will start plugin configuration
        icon_path = ':/plugins/InfoPlus/icon_infoplus.png'
        self.actionPoint = self.createAction(icon_path, u"Multi Selection by point", self.runPoint)

        # Create action that will start plugin configuration
        icon_path2 = ':/plugins/InfoPlus/icon_infoplus2.png'        
        self.actionRectangle = self.createAction(icon_path2, u"Multiple Selection by Rectangle", self.runRectangle)   

        self.toolPoint = InfoPlusPoint(self.iface.mapCanvas(), self.actionPoint, self.settings) 
        self.toolRectangle = InfoPlusRectangle(self.iface.mapCanvas(), self.actionRectangle, self.settings) 
        self.toolPoint.setInterface(self.iface)
        self.toolRectangle.setInterface(self.iface)        
        
        # QToolButtons
        self.selectionButton = self.createToolButton(self.toolbar, u'MultipleSelectionButton')
        self.selectionButton.addAction(self.actionPoint)     
        self.selectionButton.addAction(self.actionRectangle)
        self.selectionButton.setDefaultAction(self.actionPoint)         
    
    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&infoplus'), action)
            self.iface.removeToolBarIcon(action)
            
        # Remove the plugin menu item and icon
        self.iface.mainWindow().removeToolBar(self.toolbar)      
        #del self.toolbar        

    
    def runPoint(self, b):
        self.actionRectangle.setChecked(False)
        self.selectionButton.setDefaultAction(self.selectionButton.sender())
        if b:
            self.iface.mapCanvas().setMapTool(self.toolPoint)
        else:
            self.iface.mapCanvas().unsetMapTool(self.toolPoint)

            
    def runRectangle(self, b):
        self.actionPoint.setChecked(False)
        self.selectionButton.setDefaultAction(self.selectionButton.sender())
        if b:
            self.iface.mapCanvas().setMapTool(self.toolRectangle)
        else:
            self.iface.mapCanvas().unsetMapTool(self.toolRectangle)
