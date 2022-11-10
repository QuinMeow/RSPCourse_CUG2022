# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SupClassifyWin.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SupClassifyWin(object):
    def setupUi(self, SupClassifyWin):
        SupClassifyWin.setObjectName("SupClassifyWin")
        SupClassifyWin.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(SupClassifyWin)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(SupClassifyWin)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.LinEdit_ShpAddress = QtWidgets.QLineEdit(self.groupBox)
        self.LinEdit_ShpAddress.setObjectName("LinEdit_ShpAddress")
        self.horizontalLayout.addWidget(self.LinEdit_ShpAddress)
        self.Btn_ChooseFile = QtWidgets.QPushButton(self.groupBox)
        self.Btn_ChooseFile.setObjectName("Btn_ChooseFile")
        self.horizontalLayout.addWidget(self.Btn_ChooseFile)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(SupClassifyWin)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SupClassifyWin)
        self.buttonBox.accepted.connect(SupClassifyWin.accept)
        self.buttonBox.rejected.connect(SupClassifyWin.reject)
        QtCore.QMetaObject.connectSlotsByName(SupClassifyWin)

    def retranslateUi(self, SupClassifyWin):
        _translate = QtCore.QCoreApplication.translate
        SupClassifyWin.setWindowTitle(_translate("SupClassifyWin", "监督分类"))
        self.groupBox.setTitle(_translate("SupClassifyWin", "最大似然分类"))
        self.label.setText(_translate("SupClassifyWin", "矢量文件"))
        self.Btn_ChooseFile.setText(_translate("SupClassifyWin", "选择文件"))
