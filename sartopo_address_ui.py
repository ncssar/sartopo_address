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
        Dialog.resize(400, 300)
        self.addrField = QtWidgets.QLineEdit(Dialog)
        self.addrField.setGeometry(QtCore.QRect(104, 15, 267, 22))
        self.addrField.setObjectName("addrField")
        self.latField = QtWidgets.QLineEdit(Dialog)
        self.latField.setEnabled(False)
        self.latField.setGeometry(QtCore.QRect(105, 80, 113, 22))
        self.latField.setObjectName("latField")
        self.lonField = QtWidgets.QLineEdit(Dialog)
        self.lonField.setEnabled(False)
        self.lonField.setGeometry(QtCore.QRect(105, 115, 113, 22))
        self.lonField.setObjectName("lonField")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(36, 18, 53, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(41, 83, 53, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(39, 119, 64, 16))
        self.label_3.setObjectName("label_3")
        self.goButton = QtWidgets.QPushButton(Dialog)
        self.goButton.setGeometry(QtCore.QRect(103, 236, 93, 28))
        self.goButton.setObjectName("goButton")
        self.urlField = QtWidgets.QLineEdit(Dialog)
        self.urlField.setGeometry(QtCore.QRect(105, 181, 282, 22))
        self.urlField.setObjectName("urlField")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(39, 183, 64, 16))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Dialog)
        self.addrField.editingFinished.connect(Dialog.lookupFromAddrField)
        self.goButton.clicked.connect(Dialog.go)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Address"))
        self.label_2.setText(_translate("Dialog", "Latitude"))
        self.label_3.setText(_translate("Dialog", "Longitude"))
        self.goButton.setText(_translate("Dialog", "Go"))
        self.label_4.setText(_translate("Dialog", "URL"))
