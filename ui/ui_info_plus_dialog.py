# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/info_plus_dialog.ui'
#
# Created: Mon Aug 03 16:28:42 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_infoPlusDialog(object):
    def setupUi(self, infoPlusDialog):
        infoPlusDialog.setObjectName(_fromUtf8("infoPlusDialog"))
        infoPlusDialog.resize(365, 300)
        self.tbMain = QtGui.QToolBox(infoPlusDialog)
        self.tbMain.setGeometry(QtCore.QRect(20, 20, 331, 231))
        self.tbMain.setObjectName(_fromUtf8("tbMain"))
        self.page_0 = QtGui.QWidget()
        self.page_0.setGeometry(QtCore.QRect(0, 0, 331, 177))
        self.page_0.setObjectName(_fromUtf8("page_0"))
        self.label = QtGui.QLabel(self.page_0)
        self.label.setGeometry(QtCore.QRect(20, 20, 221, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.tbMain.addItem(self.page_0, _fromUtf8(""))
        self.page_1 = QtGui.QWidget()
        self.page_1.setGeometry(QtCore.QRect(0, 0, 331, 177))
        self.page_1.setObjectName(_fromUtf8("page_1"))
        self.tbMain.addItem(self.page_1, _fromUtf8(""))

        self.retranslateUi(infoPlusDialog)
        self.tbMain.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(infoPlusDialog)

    def retranslateUi(self, infoPlusDialog):
        infoPlusDialog.setWindowTitle(_translate("infoPlusDialog", "Dialog", None))
        self.label.setText(_translate("infoPlusDialog", "TextLabel", None))
        self.tbMain.setItemText(self.tbMain.indexOf(self.page_0), _translate("infoPlusDialog", "Nom capa 1", None))
        self.tbMain.setItemText(self.tbMain.indexOf(self.page_1), _translate("infoPlusDialog", "Capa 2", None))

