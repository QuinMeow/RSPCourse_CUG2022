# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWin.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(511, 398)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.SpBox_Ratio = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.SpBox_Ratio.setDecimals(3)
        self.SpBox_Ratio.setMinimum(0.001)
        self.SpBox_Ratio.setMaximum(10.0)
        self.SpBox_Ratio.setSingleStep(0.1)
        self.SpBox_Ratio.setObjectName("SpBox_Ratio")
        self.horizontalLayout.addWidget(self.SpBox_Ratio)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.ComBox_Stretch = QtWidgets.QComboBox(self.centralwidget)
        self.ComBox_Stretch.setObjectName("ComBox_Stretch")
        self.horizontalLayout.addWidget(self.ComBox_Stretch)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.MainView = QtWidgets.QGraphicsView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MainView.sizePolicy().hasHeightForWidth())
        self.MainView.setSizePolicy(sizePolicy)
        self.MainView.setMinimumSize(QtCore.QSize(200, 200))
        self.MainView.setObjectName("MainView")
        self.verticalLayout_4.addWidget(self.MainView)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.LinEdit_ImageAddress = QtWidgets.QLineEdit(self.groupBox_2)
        self.LinEdit_ImageAddress.setInputMask("")
        self.LinEdit_ImageAddress.setObjectName("LinEdit_ImageAddress")
        self.horizontalLayout_3.addWidget(self.LinEdit_ImageAddress)
        self.Btn_ChooseFile = QtWidgets.QPushButton(self.groupBox_2)
        self.Btn_ChooseFile.setObjectName("Btn_ChooseFile")
        self.horizontalLayout_3.addWidget(self.Btn_ChooseFile)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.Btn_ReadImage = QtWidgets.QPushButton(self.groupBox_2)
        self.Btn_ReadImage.setObjectName("Btn_ReadImage")
        self.verticalLayout_3.addWidget(self.Btn_ReadImage)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.SpBox_Red = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_Red.setMinimum(1)
        self.SpBox_Red.setProperty("value", 3)
        self.SpBox_Red.setObjectName("SpBox_Red")
        self.horizontalLayout_4.addWidget(self.SpBox_Red)
        self.SpBox_Green = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_Green.setFrame(True)
        self.SpBox_Green.setMinimum(1)
        self.SpBox_Green.setProperty("value", 2)
        self.SpBox_Green.setObjectName("SpBox_Green")
        self.horizontalLayout_4.addWidget(self.SpBox_Green)
        self.SpBox_Blue = QtWidgets.QSpinBox(self.groupBox)
        self.SpBox_Blue.setMinimum(1)
        self.SpBox_Blue.setProperty("value", 1)
        self.SpBox_Blue.setObjectName("SpBox_Blue")
        self.horizontalLayout_4.addWidget(self.SpBox_Blue)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.Btn_ShowImage = QtWidgets.QPushButton(self.groupBox)
        self.Btn_ShowImage.setObjectName("Btn_ShowImage")
        self.verticalLayout_2.addWidget(self.Btn_ShowImage)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 511, 18))
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
        self.label_4.setText(_translate("MainWindow", "显示比例"))
        self.label_5.setText(_translate("MainWindow", "线性拉伸"))
        self.groupBox_2.setTitle(_translate("MainWindow", "文件打开"))
        self.LinEdit_ImageAddress.setText(_translate("MainWindow", "武汉.tif"))
        self.Btn_ChooseFile.setText(_translate("MainWindow", "选择文件"))
        self.Btn_ReadImage.setText(_translate("MainWindow", "读取图像"))
        self.groupBox.setTitle(_translate("MainWindow", "波段选择"))
        self.label.setText(_translate("MainWindow", "红"))
        self.label_2.setText(_translate("MainWindow", "绿"))
        self.label_3.setText(_translate("MainWindow", "蓝"))
        self.Btn_ShowImage.setText(_translate("MainWindow", "显示图像"))
