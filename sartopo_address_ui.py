# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sartopo_address.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(404, 136)
        self.addrField = QtWidgets.QLineEdit(Dialog)
        self.addrField.setGeometry(QtCore.QRect(77, 13, 307, 22))
        self.addrField.setObjectName("addrField")
        self.latField = QtWidgets.QLineEdit(Dialog)
        self.latField.setEnabled(False)
        self.latField.setGeometry(QtCore.QRect(79, 39, 110, 22))
        self.latField.setObjectName("latField")
        self.lonField = QtWidgets.QLineEdit(Dialog)
        self.lonField.setEnabled(False)
        self.lonField.setGeometry(QtCore.QRect(79, 66, 111, 22))
        self.lonField.setObjectName("lonField")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(24, 14, 53, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(22, 43, 53, 16))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(9, 68, 64, 16))
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.goButton = QtWidgets.QPushButton(Dialog)
        self.goButton.setGeometry(QtCore.QRect(293, 96, 93, 28))
        self.goButton.setObjectName("goButton")
        self.urlField = QtWidgets.QLineEdit(Dialog)
        self.urlField.setGeometry(QtCore.QRect(47, 97, 234, 22))
        self.urlField.setObjectName("urlField")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(20, 98, 26, 16))
        self.label_4.setObjectName("label_4")
        self.locationCountLabel = QtWidgets.QLabel(Dialog)
        self.locationCountLabel.setGeometry(QtCore.QRect(170, 52, 176, 20))
        self.locationCountLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.locationCountLabel.setObjectName("locationCountLabel")
        self.optionsButton = QtWidgets.QPushButton(Dialog)
        self.optionsButton.setGeometry(QtCore.QRect(356, 46, 30, 30))
        self.optionsButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sartopo_address/options_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.optionsButton.setIcon(icon)
        self.optionsButton.setIconSize(QtCore.QSize(24, 24))
        self.optionsButton.setObjectName("optionsButton")

        self.retranslateUi(Dialog)
        self.addrField.editingFinished.connect(Dialog.lookupFromAddrField)
        self.goButton.clicked.connect(Dialog.go)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "SARTopo Offline Address Search"))
        self.label.setText(_translate("Dialog", "Address"))
        self.label_2.setText(_translate("Dialog", "Latitude"))
        self.label_3.setText(_translate("Dialog", "Longitude"))
        self.goButton.setText(_translate("Dialog", "Add Marker"))
        self.label_4.setText(_translate("Dialog", "URL"))
        self.locationCountLabel.setText(_translate("Dialog", "0 Locations loaded"))

import sartopo_address_rc
