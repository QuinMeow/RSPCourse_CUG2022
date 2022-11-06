# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'BandMathWin.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BandMathWin(object):
    def setupUi(self, BandMathWin):
        BandMathWin.setObjectName("BandMathWin")
        BandMathWin.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(BandMathWin)
        self.gridLayout.setObjectName("gridLayout")
        self.LinEdit_Formula = QtWidgets.QLineEdit(BandMathWin)
        self.LinEdit_Formula.setObjectName("LinEdit_Formula")
        self.gridLayout.addWidget(self.LinEdit_Formula, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(BandMathWin)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(BandMathWin)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)

        self.retranslateUi(BandMathWin)
        self.buttonBox.accepted.connect(BandMathWin.accept)
        self.buttonBox.rejected.connect(BandMathWin.reject)
        QtCore.QMetaObject.connectSlotsByName(BandMathWin)

    def retranslateUi(self, BandMathWin):
        _translate = QtCore.QCoreApplication.translate
        BandMathWin.setWindowTitle(_translate("BandMathWin", "波段运算"))
        self.label.setText(_translate("BandMathWin", "波段运算表达式："))
