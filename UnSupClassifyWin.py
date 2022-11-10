# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UnSupClassifyWin.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UnSupClassifyWin(object):
    def setupUi(self, UnSupClassifyWin):
        UnSupClassifyWin.setObjectName("UnSupClassifyWin")
        UnSupClassifyWin.resize(496, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(UnSupClassifyWin)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(UnSupClassifyWin)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.SpBox_K = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_K.setMinimum(1)
        self.SpBox_K.setProperty("value", 3)
        self.SpBox_K.setObjectName("SpBox_K")
        self.gridLayout.addWidget(self.SpBox_K, 0, 2, 1, 1)
        self.SpBox_TN = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_TN.setMinimum(1)
        self.SpBox_TN.setProperty("value", 3)
        self.SpBox_TN.setObjectName("SpBox_TN")
        self.gridLayout.addWidget(self.SpBox_TN, 0, 4, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 3, 1, 1)
        self.SpBox_I = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_I.setProperty("value", 8)
        self.SpBox_I.setObjectName("SpBox_I")
        self.gridLayout.addWidget(self.SpBox_I, 2, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 1, 1, 1)
        self.SpBox_L = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_L.setProperty("value", 10)
        self.SpBox_L.setObjectName("SpBox_L")
        self.gridLayout.addWidget(self.SpBox_L, 2, 4, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.SpBox_TC = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_TC.setProperty("value", 40)
        self.SpBox_TC.setObjectName("SpBox_TC")
        self.gridLayout.addWidget(self.SpBox_TC, 1, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 1, 1, 1)
        self.SpBox_TS = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.SpBox_TS.setProperty("value", 4.0)
        self.SpBox_TS.setObjectName("SpBox_TS")
        self.gridLayout.addWidget(self.SpBox_TS, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(UnSupClassifyWin)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(UnSupClassifyWin)
        self.buttonBox.accepted.connect(UnSupClassifyWin.accept)
        self.buttonBox.rejected.connect(UnSupClassifyWin.reject)
        QtCore.QMetaObject.connectSlotsByName(UnSupClassifyWin)
        UnSupClassifyWin.setTabOrder(self.SpBox_K, self.SpBox_TN)
        UnSupClassifyWin.setTabOrder(self.SpBox_TN, self.SpBox_TC)
        UnSupClassifyWin.setTabOrder(self.SpBox_TC, self.SpBox_I)
        UnSupClassifyWin.setTabOrder(self.SpBox_I, self.SpBox_L)

    def retranslateUi(self, UnSupClassifyWin):
        _translate = QtCore.QCoreApplication.translate
        UnSupClassifyWin.setWindowTitle(_translate("UnSupClassifyWin", "非监督分类"))
        self.groupBox.setTitle(_translate("UnSupClassifyWin", "isodata分类"))
        self.label_5.setText(_translate("UnSupClassifyWin", "各类别间最小距离"))
        self.label_4.setText(_translate("UnSupClassifyWin", "各类别标准差"))
        self.label.setText(_translate("UnSupClassifyWin", "期望类别数"))
        self.label_3.setText(_translate("UnSupClassifyWin", "各类别最小样本数目"))
        self.label_2.setText(_translate("UnSupClassifyWin", "每次允许合并最大类别数"))
        self.label_6.setText(_translate("UnSupClassifyWin", "迭代次数上限"))
