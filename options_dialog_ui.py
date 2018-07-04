# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'options_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_optionsDialog(object):
    def setupUi(self, optionsDialog):
        optionsDialog.setObjectName("optionsDialog")
        optionsDialog.resize(400, 140)
        self.locationCountLabel = QtWidgets.QLabel(optionsDialog)
        self.locationCountLabel.setGeometry(QtCore.QRect(46, 92, 181, 20))
        self.locationCountLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.locationCountLabel.setObjectName("locationCountLabel")
        self.reloadButton = QtWidgets.QPushButton(optionsDialog)
        self.reloadButton.setGeometry(QtCore.QRect(243, 86, 30, 30))
        self.reloadButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sartopo_address/reload-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reloadButton.setIcon(icon)
        self.reloadButton.setIconSize(QtCore.QSize(24, 24))
        self.reloadButton.setObjectName("reloadButton")
        self.locationFileField = QtWidgets.QLineEdit(optionsDialog)
        self.locationFileField.setGeometry(QtCore.QRect(15, 32, 297, 22))
        self.locationFileField.setObjectName("locationFileField")
        self.label = QtWidgets.QLabel(optionsDialog)
        self.label.setGeometry(QtCore.QRect(14, 16, 156, 16))
        self.label.setObjectName("label")
        self.browseButton = QtWidgets.QPushButton(optionsDialog)
        self.browseButton.setGeometry(QtCore.QRect(320, 29, 75, 28))
        self.browseButton.setObjectName("browseButton")
        self.closeButton = QtWidgets.QPushButton(optionsDialog)
        self.closeButton.setGeometry(QtCore.QRect(296, 87, 93, 28))
        self.closeButton.setObjectName("closeButton")

        self.retranslateUi(optionsDialog)
        self.reloadButton.clicked.connect(optionsDialog.reload)
        self.browseButton.clicked.connect(optionsDialog.browseForFile)
        self.closeButton.clicked.connect(optionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(optionsDialog)

    def retranslateUi(self, optionsDialog):
        _translate = QtCore.QCoreApplication.translate
        optionsDialog.setWindowTitle(_translate("optionsDialog", "Options"))
        self.locationCountLabel.setText(_translate("optionsDialog", "0 Locations loaded"))
        self.label.setText(_translate("optionsDialog", "Location Lookup File (.csv)"))
        self.browseButton.setText(_translate("optionsDialog", "Browse"))
        self.closeButton.setText(_translate("optionsDialog", "Close"))

import sartopo_address_rc
