# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWin.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(858, 756)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.MainView = QtWidgets.QGraphicsView(self.centralwidget)
        self.MainView.setMinimumSize(QtCore.QSize(500, 500))
        self.MainView.setObjectName("MainView")
        self.horizontalLayout_2.addWidget(self.MainView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Btn_ReadImage = QtWidgets.QPushButton(self.centralwidget)
        self.Btn_ReadImage.setObjectName("Btn_ReadImage")
        self.verticalLayout.addWidget(self.Btn_ReadImage)
        self.LinEdit_ImageAddress = QtWidgets.QLineEdit(self.centralwidget)
        self.LinEdit_ImageAddress.setInputMask("")
        self.LinEdit_ImageAddress.setObjectName("LinEdit_ImageAddress")
        self.verticalLayout.addWidget(self.LinEdit_ImageAddress)
        self.Btn_ShowImage = QtWidgets.QPushButton(self.centralwidget)
        self.Btn_ShowImage.setObjectName("Btn_ShowImage")
        self.verticalLayout.addWidget(self.Btn_ShowImage)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Btn_ReadImage.setText(_translate("MainWindow", "读取图像"))
        self.LinEdit_ImageAddress.setText(_translate("MainWindow", "武汉.tif"))
        self.Btn_ShowImage.setText(_translate("MainWindow", "显示图像"))