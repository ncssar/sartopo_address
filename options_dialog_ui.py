# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'options_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_optionsDialog(object):
    def setupUi(self, optionsDialog):
        optionsDialog.setObjectName("optionsDialog")
        optionsDialog.resize(400, 140)
        self.locationCountLabel = QtWidgets.QLabel(optionsDialog)
        self.locationCountLabel.setGeometry(QtCore.QRect(46, 110, 181, 20))
        self.locationCountLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.locationCountLabel.setObjectName("locationCountLabel")
        self.reloadButton = QtWidgets.QPushButton(optionsDialog)
        self.reloadButton.setGeometry(QtCore.QRect(243, 104, 30, 30))
        self.reloadButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sartopo_address/reload-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reloadButton.setIcon(icon)
        self.reloadButton.setIconSize(QtCore.QSize(24, 24))
        self.reloadButton.setObjectName("reloadButton")
        self.locationFileField = QtWidgets.QLineEdit(optionsDialog)
        self.locationFileField.setGeometry(QtCore.QRect(10, 74, 297, 26))
        self.locationFileField.setObjectName("locationFileField")
        self.label = QtWidgets.QLabel(optionsDialog)
        self.label.setGeometry(QtCore.QRect(9, 58, 160, 16))
        self.label.setObjectName("label")
        self.browseButton = QtWidgets.QPushButton(optionsDialog)
        self.browseButton.setGeometry(QtCore.QRect(317, 73, 75, 28))
        self.browseButton.setObjectName("browseButton")
        self.closeButton = QtWidgets.QPushButton(optionsDialog)
        self.closeButton.setGeometry(QtCore.QRect(299, 106, 93, 28))
        self.closeButton.setObjectName("closeButton")
        self.folderComboBox = STSFeatureComboBox(optionsDialog)
        self.folderComboBox.setGeometry(QtCore.QRect(243, 32, 148, 22))
        self.folderComboBox.setObjectName("folderComboBox")
        self.label_2 = QtWidgets.QLabel(optionsDialog)
        self.label_2.setGeometry(QtCore.QRect(9, 32, 233, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(optionsDialog)
        self.label_3.setGeometry(QtCore.QRect(9, 7, 95, 20))
        self.label_3.setObjectName("label_3")
        self.urlField = QtWidgets.QLineEdit(optionsDialog)
        self.urlField.setGeometry(QtCore.QRect(107, 6, 261, 22))
        self.urlField.setObjectName("urlField")
        self.linkIndicator = QtWidgets.QLineEdit(optionsDialog)
        self.linkIndicator.setEnabled(False)
        self.linkIndicator.setGeometry(QtCore.QRect(373, 8, 20, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.linkIndicator.setFont(font)
        self.linkIndicator.setObjectName("linkIndicator")

        self.retranslateUi(optionsDialog)
        self.reloadButton.clicked.connect(optionsDialog.reload)
        self.browseButton.clicked.connect(optionsDialog.browseForFile)
        self.closeButton.clicked.connect(optionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(optionsDialog)

    def retranslateUi(self, optionsDialog):
        _translate = QtCore.QCoreApplication.translate
        optionsDialog.setWindowTitle(_translate("optionsDialog", "Options"))
        self.locationCountLabel.setText(_translate("optionsDialog", "0 Locations loaded"))
        self.label.setText(_translate("optionsDialog", "Location Lookup File (.csv):"))
        self.browseButton.setText(_translate("optionsDialog", "Browse"))
        self.closeButton.setText(_translate("optionsDialog", "Close"))
        self.label_2.setText(_translate("optionsDialog", "Only list existing labels from fodler(s):"))
        self.label_3.setText(_translate("optionsDialog", "Saved map URL:"))

from  STSFeatureComboBox import STSFeatureComboBox
import sartopo_address_rc
