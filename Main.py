import sys
import re
import numpy as np
from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from osgeo import gdal

from MainWin import *
from BandMathWin import *
from ReSampleWin import *
# from UnSupClassifyWin import *
from UnSupClassifyWindow import *
from SupCassifyWindow import *


# 定义主窗口类，继承自MainWin
class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.MainView = MyMainView(self.MainView)
        stretch_list = ["无拉伸", "2%线性拉伸"]
        self.ComBox_Stretch.addItems(stretch_list)
        # 初始化成员对象
        self.filename = self.LinEdit_ImageAddress.text()
        self.im_width = 0
        self.im_height = 0
        self.im_bands = 0
        self.im_geotrans = ''
        self.im_proj = ''
        self.qim_data = np.zeros((0, 0, 0))
        # 处理信号与槽的连接
        self.Btn_ReadImage.clicked.connect(self.read_img)
        self.Btn_ChooseFile.clicked.connect(self.openfile)

    def openfile(self):
        """
        选择要打开的文件路径
        """
        openfile_name = QFileDialog.getOpenFileName(self, '选择文件', './', 'All Files(*)')
        self.LinEdit_ImageAddress.setText(openfile_name[0])

    def read_img(self):
        """
        读取影像，如非8位无符号进行转换
        :return:
        """
        self.filename = self.LinEdit_ImageAddress.text()
        dataset = gdal.Open(self.filename)  # 打开文件
        self.im_width = dataset.RasterXSize  # 栅格矩阵的列数
        self.im_height = dataset.RasterYSize  # 栅格矩阵的行数
        self.im_bands = dataset.RasterCount  # 波段数
        self.im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵，左上像素的大地坐标和像素分辨率
        self.im_proj = dataset.GetProjection()  # 地图投影信息，字符串表示
        im_data = dataset.ReadAsArray(0, 0, self.im_width, self.im_height)
        self.qim_data = np.rollaxis(im_data, 0, 3)
        # 设置UI波段最大值
        self.SpBox_Red.setMaximum(self.im_bands)
        self.SpBox_Green.setMaximum(self.im_bands)
        self.SpBox_Blue.setMaximum(self.im_bands)
        del dataset
        self.Btn_ShowImage.clicked.connect(self.show_img)

    def show_img(self):
        """
        显示影像到MainView
        :return:
        """
        Band = np.array((int(self.SpBox_Red.value()) - 1, int(self.SpBox_Green.value()) - 1, \
                         int(self.SpBox_Blue.value()) - 1))
        show_data = self.qim_data[:, :, Band]
        self.MainView.showInput(show_data)
        # 连接信号与槽
        self.SpBox_Ratio.textChanged.connect(self.MainView.changeRatio)
        self.MainView.ratioChanged.connect(self.SpBox_Ratio.setValue)
        self.ComBox_Stretch.activated.connect(self.MainView.changeStretch)
        self.Btn_BandMath.clicked.connect(self.bandMath)
        self.Btn_ReSample.clicked.connect(self.reSample)
        self.Btn_UnSupClassify.clicked.connect(self.UnSupClassify)
        self.Btn_SupClassify.clicked.connect(self.SupClassify)

    def bandMath(self):
        """
        波段运算，打开窗口并将结果放入MainView
        :return:
        """
        BMW = BandMathWindow(self.qim_data)  # 创建波段运算窗口
        BMW.show()
        if BMW.exec_() == QDialog.Accepted:
            self.MainView.showInput(BMW.bandMathResult)

    def reSample(self):
        """
        重采样
        :return:重采样后影像矩阵
        """
        RSW = ReSampleWindow(self.qim_data)
        RSW.show()
        if RSW.exec_() == QDialog.Accepted:
            # 设置UI波段最大值
            Band = np.array((int(self.SpBox_Red.value()) - 1, int(self.SpBox_Green.value()) - 1,
                             int(self.SpBox_Blue.value()) - 1))
            show_data = RSW.resampleResult[:, :, Band]
            self.MainView.showInput(show_data)

    def UnSupClassify(self):
        """
        非监督分类
        :return:
        """
        Band = np.array((int(self.SpBox_Red.value()) - 1, int(self.SpBox_Green.value()) - 1,
                         int(self.SpBox_Blue.value()) - 1))
        USC = UnSupClassifyWindow(self.qim_data[:, :, Band])
        USC.show()
        if USC.exec_() == QDialog.Accepted:
            self.MainView.showInput(USC.Classified_data)

    def SupClassify(self):
        """
        监督分类
        :return:
        """
        # Band = np.array((int(self.SpBox_Red.value()) - 1, int(self.SpBox_Green.value()) - 1,
        #                  int(self.SpBox_Blue.value()) - 1))
        SC = SupClassifyWindow(self.filename, self.qim_data)
        SC.show()
        if SC.exec_() == QDialog.Accepted:
            self.MainView.showInput(SC.Classified_data)
            form = ConfMatForm(SC.label_dict, SC.Conf_mat)
            form.exec()
            # form.updateUi(SC.label_dict, SC.Conf_mat)


class MyMainView(QGraphicsView):
    # 信号
    ratioChanged = QtCore.pyqtSignal(float)  # 比例

    def __init__(self, graphicsView):
        super().__init__()
        self.graphicsView = graphicsView

        self.graphicsView.setStyleSheet("padding: 0px; border: 0px;")  # 内边距和边界去除
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 改变对齐方式

        self.graphicsView.setSceneRect(0, 0, self.graphicsView.viewport().width(),
                                       self.graphicsView.height())  # 设置图形场景大小和图形视图大小一致
        self.graphicsView.setScene(self.scene)

        self.scene.mousePressEvent = self.scene_mousePressEvent  # 接管图形场景的鼠标点击事件
        self.scene.mouseMoveEvent = self.scene_mouseMoveEvent  # 接管图形场景的鼠标移动事件
        self.scene.wheelEvent = self.scene_wheelEvent  # 接管图形场景的滑轮事件

        # self.size = QSize(self.size().width() - 10, self.size().height() - 10) #初始大小
        self.ratio = 1  # 缩放初始比例
        self.zoom_step = 0.1  # 缩放步长
        self.zoom_max = 10  # 缩放最大值
        self.zoom_min = 0.001  # 缩放最小值
        self.stretchType = 0  # 拉伸类型
        self.originData = None  # 原始影像
        self.IntData = None  # 8位无符号影像
        self.pixmapItem = None

    def showInput(self, origin_data):
        """
        读取外部并存储原始数据
        :param origin_data:
        :return:
        """
        self.originData = origin_data
        if self.originData.dtype != np.uint8:  # 非8位无符号整型时
            self.IntData = self.compress(self.originData)
        else:
            self.IntData = self.originData
        self.showStretch()

    def compress(self, originData):
        """
        16位影像转8位
        """

        array_data = originData
        rows, cols, bands = array_data.shape

        compress_data = np.zeros((rows, cols, bands))

        for i in range(bands):
            band_max = np.nanmax(array_data[:, :, i])  # 非nan最大最小值
            band_min = np.nanmin(array_data[:, :, i])
            compress_data[:, :, i] = ((array_data[:, :, i] - band_min) / band_max * 255)

        int_data = compress_data.astype('uint8')
        return int_data

    def showStretch(self):
        """
        将origin_data应用拉伸并转为pixmap放入scene
        :param :
        :return:
        """
        self.scene.clear()  # 清空场景

        if self.pixmapItem != None:
            originX = self.pixmapItem.x()
            originY = self.pixmapItem.y()
        else:
            originX, originY = 0, 0
        # 拉伸方式
        if self.stretchType == 0:
            show_data = self.IntData
        elif self.stretchType == 1:
            show_data = self.stretch_2p(self.IntData)

        height, width, bytesPerComponent = show_data.shape
        bytesPerLine = bytesPerComponent * width
        if bytesPerComponent == 3:
            image = QImage(show_data.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888)
        elif bytesPerComponent == 1:
            image = QImage(show_data.tobytes(), width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.ratio = min(self.width() / image.width(), self.height() / image.height())
        self.pixmap = QPixmap.fromImage(image)
        self.pixmapItem = self.scene.addPixmap(self.pixmap)
        self.pixmapItem.setScale(self.ratio)
        self.pixmapItem.setPos(originX, originY)

    def changeStretch(self, new_stretch):
        self.stretchType = new_stretch
        self.showStretch()

    def stretch_2p(self, show_data):

        height, width, bytesPerComponent = show_data.shape
        show_data_stretched = np.zeros((height, width, bytesPerComponent))
        for i in range(bytesPerComponent):
            p2 = np.percentile(show_data[:, :, i], 2)
            p98 = np.percentile(show_data[:, :, i], 98)
            r = (p98 - p2) / 255
            show_data_stretched[:, :, i] = (show_data[:, :, i]) / r + p2
            show_data_stretched[:, :, i] = np.where(show_data_stretched[:, :, i] < p2 / r + p2, p2 / r + p2,
                                                    show_data_stretched[:, :, i])
            show_data_stretched[:, :, i] = np.where(show_data_stretched[:, :, i] > p98 / r + p2, p98 / r + p2,
                                                    show_data_stretched[:, :, i])
        show_data_stretched = show_data_stretched.astype(np.uint8)
        return show_data_stretched

    def changeRatio(self, new_ratio_str):
        self.ratio = float(new_ratio_str)
        self.pixmapItem.setScale(self.ratio)

    def scene_mousePressEvent(self, event):
        if event.button() == Qt.MidButton:  # 中键按下
            self.preMousePosition = event.scenePos()  # 获取鼠标当前位置

    def scene_mouseMoveEvent(self, event):
        if event.buttons() == Qt.MidButton:
            self.MouseMove = event.scenePos() - self.preMousePosition  # 鼠标当前位置-先前位置=单次偏移量
            self.preMousePosition = event.scenePos()  # 更新当前鼠标在窗口上的位置，下次移动用
            self.pixmapItem.setPos(self.pixmapItem.pos() + self.MouseMove)  # 更新图元位置

    def scene_wheelEvent(self, event):
        angle = event.delta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
        if angle > 0:
            # print("滚轮上滚")
            self.ratio += self.zoom_step  # 缩放比例自加
            if self.ratio > self.zoom_max:
                self.ratio = self.zoom_max
            else:
                w = self.pixmap.size().width() * (self.ratio - self.zoom_step)
                h = self.pixmap.size().height() * (self.ratio - self.zoom_step)
                x1 = self.pixmapItem.pos().x()  # 图元左位置
                x2 = self.pixmapItem.pos().x() + w  # 图元右位置
                y1 = self.pixmapItem.pos().y()  # 图元上位置
                y2 = self.pixmapItem.pos().y() + h  # 图元下位置
                if x1 < event.scenePos().x() < x2 and y1 < event.scenePos().y() < y2:  # 判断鼠标悬停位置是否在图元中
                    # print('在内部')
                    self.pixmapItem.setScale(self.ratio)  # 缩放
                    self.ratioChanged.emit(self.ratio)
                    a1 = event.scenePos() - self.pixmapItem.pos()  # 鼠标与图元左上角的差值
                    a2 = self.ratio / (self.ratio - self.zoom_step) - 1  # 对应比例
                    delta = a1 * a2
                    self.pixmapItem.setPos(self.pixmapItem.pos() - delta)
                else:
                    # print('在外部')  # 以图元中心缩放
                    self.pixmapItem.setScale(self.ratio)  # 缩放
                    self.ratioChanged.emit(self.ratio)
                    delta_x = (self.pixmap.size().width() * self.zoom_step) / 2  # 图元偏移量
                    delta_y = (self.pixmap.size().height() * self.zoom_step) / 2
                    self.pixmapItem.setPos(self.pixmapItem.pos().x() - delta_x,
                                           self.pixmapItem.pos().y() - delta_y)  # 图元偏移

        else:
            # print("滚轮下滚")
            self.ratio -= self.zoom_step
            if self.ratio < self.zoom_step:
                self.ratio = self.zoom_min
            else:
                w = self.pixmap.size().width() * (self.ratio + self.zoom_step)
                h = self.pixmap.size().height() * (self.ratio + self.zoom_step)
                x1 = self.pixmapItem.pos().x()
                x2 = self.pixmapItem.pos().x() + w
                y1 = self.pixmapItem.pos().y()
                y2 = self.pixmapItem.pos().y() + h
                # print(x1, x2, y1, y2)
                if x1 < event.scenePos().x() < x2 and y1 < event.scenePos().y() < y2:
                    # print('在内部')
                    self.pixmapItem.setScale(self.ratio)  # 缩放
                    self.ratioChanged.emit(self.ratio)
                    a1 = event.scenePos() - self.pixmapItem.pos()  # 鼠标与图元左上角的差值
                    a2 = self.ratio / (self.ratio + self.zoom_step) - 1  # 对应比例
                    delta = a1 * a2
                    self.pixmapItem.setPos(self.pixmapItem.pos() - delta)

                else:
                    # print('在外部')
                    self.pixmapItem.setScale(self.ratio)
                    self.ratioChanged.emit(self.ratio)
                    delta_x = (self.pixmap.size().width() * self.zoom_step) / 2
                    delta_y = (self.pixmap.size().height() * self.zoom_step) / 2
                    self.pixmapItem.setPos(self.pixmapItem.pos().x() + delta_x, self.pixmapItem.pos().y() + delta_y)


# 栈的结构
class Stack(object):
    def __init__(self, stack, top):
        self.stack = stack
        self.top = top


# 波段运算类
class BandMathWindow(QDialog, Ui_BandMathWin):
    def __init__(self, qim_data):
        super(BandMathWindow, self).__init__()
        self.setupUi(self)
        self.origin_data = qim_data
        self.bandMathResult = qim_data
        self.buttonBox.accepted.connect(self.behindCalculation)

    # 中缀转后缀
    def middle2behind(self):
        formula = self.LinEdit_Formula.text()  # 从UI界面读取
        # 合并非符号
        formula = re.split(r'([\+\-\*\/\(\)])', formula)
        formula = list(filter(None, formula))
        behind = []
        s = Stack(stack=[], top=-1)
        # 遍历表达式
        for i in formula:
            if i == '+' or i == '-':  # 如果表达式元素为+或-
                if s.top > -1:  # 由于+或-的运算优先级最低，所以如果栈为非空，则从栈顶开始遍历栈符号，依次出栈，直到栈为空或者是遇到(
                    while s.top > -1 and s.stack[s.top] != '(':
                        behind.append(s.stack[s.top])
                        s.stack.pop()
                        s.top -= 1
                    # 将i入站
                    s.stack.append(i)
                    s.top += 1
                # 如果栈为空，直接入栈
                else:
                    s.stack.append(i)
                    s.top += 1
            # 如果表达式元素为*或/
            elif i == '*' or i == '/':
                if s.top > -1 and s.stack[s.top] != '(':  # 由于*或/的运算优先级较高，所以如果栈为非空，则从栈顶开始遍历栈内符号
                    while s.stack[s.top] == '*' and s.stack[s.top] == '/':  # 如果遇到*或者/，则依次出栈，直到栈为空或者是遇到(和+和-
                        behind.append(s.stack[s.top])
                        s.stack.pop()
                        s.top -= 1
                    s.stack.append(i)
                    s.top += 1
                else:
                    s.stack.append(i)
                    s.top += 1
            # 如果遇到(,则直接入栈，直到匹配到)后将栈中()内的符号全部出栈
            elif i == '(':
                s.stack.append(i)
                s.top += 1
            elif i == ')':
                while s.stack[s.top] != '(':
                    behind.append(s.stack[s.top])
                    s.stack.pop()
                    s.top -= 1
                s.stack.pop()
                s.top -= 1
            else:
                behind.append(i)

        # 把栈中剩余的符号出栈
        while s.top > -1:
            behind.append(s.stack[s.top])
            s.stack.pop()
            s.top -= 1
        return behind

    # 遍历后缀表达式，如果遇到数字，将其放入栈中，如果遇到符号，则取出栈中最顶上的两个数字进行计算，最顶上的那个数字是右项。运算完成之后将结果再存回栈中
    def behindCalculation(self):
        behind = self.middle2behind()
        result = Stack(stack=[], top=-1)
        # 转换内容
        r = np.array([0])
        cal_flag = False
        for i in behind:
            if i == "+":
                r = self.getData(result.stack[result.top - 1]) + self.getData(result.stack[result.top])
                cal_flag = True
                # r = int(result.stack[result.top - 1]) + int(result.stack[result.top])
            elif i == '-':
                r = self.getData(result.stack[result.top - 1]) - self.getData(result.stack[result.top])
                cal_flag = True
            elif i == '*':
                r = self.getData(result.stack[result.top - 1]) * self.getData(result.stack[result.top])
                cal_flag = True
            elif i == '/':
                r = self.getData(result.stack[result.top - 1]) / self.getData(result.stack[result.top])
                cal_flag = True
            else:
                result.stack.append(i)
                result.top += 1
            # 用这个条件来判断是否栈中取出了元素
            if cal_flag:
                # 将上次运算的两个元素出栈
                result.stack.pop()
                result.stack.pop()
                result.stack.append(r)
                result.top -= 1
                cal_flag = False
        finalResult = result.stack[0]
        print(finalResult)
        finalResult = finalResult[:, :, np.newaxis]
        self.bandMathResult = finalResult

    def getData(self, varName):
        """
        根据输入返回数据
        :param strName:
        :return:
        """

        if isinstance(varName, str):  # 判断类型是否是字符串
            if varName[0] in "bB":
                data = self.origin_data[:, :, int(varName[1:]) - 1]
                float_data = data.astype(np.float64)
                return float_data
            else:
                return float(varName)
        else:
            return varName


class ReSampleWindow(QDialog, Ui_ReSampleWin):
    def __init__(self, qim_data):
        super(ReSampleWindow, self).__init__()
        self.setupUi(self)
        self.origin_data = qim_data
        self.origin_height, self.origin_width, self.bands = qim_data.shape
        self.WidthRatio = 1.0
        self.HeightRatio = 1.0
        self.resampleResult = qim_data
        self.buttonBox.accepted.connect(self.ReSample)
        # 初始化窗口内数值
        self.Label_OWidth.setText(str(self.origin_width))
        self.Label_OHeight.setText(str(self.origin_height))
        self.LinEdit_TWidth.setText(str(self.origin_width))
        self.LinEdit_THeight.setText(str(self.origin_height))
        self.LinEdit_TWidthRatio.setText('1')
        self.LinEdit_THeightRatio.setText('1')
        self.LinEdit_TWidth.setValidator(QtGui.QIntValidator(0, 65535))
        self.LinEdit_THeight.setValidator(QtGui.QIntValidator(0, 65535))
        self.LinEdit_TWidthRatio.setValidator(QtGui.QDoubleValidator(0.0, 100.0, 2))
        self.LinEdit_THeightRatio.setValidator(QtGui.QDoubleValidator(0.0, 100.0, 2))
        # 比率变动时计算目标分辨率
        self.LinEdit_THeightRatio.textEdited.connect(self.calTargetResolution)
        self.LinEdit_TWidthRatio.textEdited.connect(self.calTargetResolution)
        # 目标分辨率变动时计算比例
        self.LinEdit_TWidth.textEdited.connect(self.calTargetRatio)
        self.LinEdit_THeight.textEdited.connect(self.calTargetRatio)

    def calTargetResolution(self):
        if self.LinEdit_TWidthRatio.text() != '' and self.LinEdit_THeightRatio.text() != '':
            self.WidthRatio = round(float(self.LinEdit_TWidthRatio.text()), 2)
            self.HeightRatio = round(float(self.LinEdit_THeightRatio.text()), 2)
            self.LinEdit_TWidth.setText(str(int(self.origin_width * self.WidthRatio)))
            self.LinEdit_THeight.setText(str(int(self.origin_height * self.HeightRatio)))

    def calTargetRatio(self):
        if self.LinEdit_TWidth.text() != '' and self.LinEdit_THeight.text() != '':
            self.WidthRatio = round(int(self.LinEdit_TWidth.text()) / self.origin_width, 2)
            self.HeightRatio = round(int(self.LinEdit_THeight.text()) / self.origin_height, 2)
            self.LinEdit_TWidthRatio.setText(str(self.WidthRatio))
            self.LinEdit_THeightRatio.setText(str(self.HeightRatio))

    def ReSample(self):
        TargetWidth = int(self.origin_width * self.WidthRatio)
        TargetHeight = int(self.origin_height * self.HeightRatio)
        self.resampleResult = np.zeros([TargetHeight, TargetWidth, self.bands])
        if self.rBtn_NN.isChecked():  # 最近邻
            for row in range(TargetHeight):
                srcRow = round(row / self.HeightRatio)
                for col in range(TargetWidth):
                    srcCol = round(col / self.WidthRatio)
                    # for band in range(self.bands):
                    #     self.resampleResult[row, col, band] = self.origin_data[srcRow, srcCol, band]
                    self.resampleResult[row, col, :] = self.origin_data[srcRow, srcCol, :]
        elif self.rBtn_Liner.isChecked():  # 双线性
            for row in range(TargetHeight):
                srcRow = row / self.HeightRatio
                n, i = np.modf(srcRow)  # 整数部分i，小数部分n
                i = int(i)
                for col in range(TargetWidth):
                    srcCol = col / self.WidthRatio
                    m, j = np.modf(srcCol)  # 整数部分j，小数部分m
                    j = int(j)
                    # for band in range(self.bands):
                    #     self.resampleResult[row, col, band] = \
                    #         self.origin_data[i, j, band] + self.origin_data[i + 1, j, band] * n + self.origin_data[
                    #             i, j + 1, band] * m + self.origin_data[i + 1, j + 1, band] * n * m
                    self.resampleResult[row, col, :] = self.origin_data[i, j, :] * (1 - n) * (1 - m) + \
                                                       self.origin_data[i + 1, j,:] * n * (1 - m) + \
                                                       self.origin_data[i, j + 1,:] * (1 - n) * m + \
                                                       self.origin_data[i + 1, j + 1,:] * n * m
        elif self.rBtn_Cube.isChecked():  # 双立方
            for row in range(TargetHeight):
                srcRow = row / self.HeightRatio
                v, i = np.modf(srcRow)  # 整数部分i，小数部分v
                A = np.array([self.BF(1 + v), self.BF(v), self.BF(1 - v), self.BF(2 - v)])
                i = int(i)
                for col in range(TargetWidth):
                    srcCol = col / self.WidthRatio
                    u, j = np.modf(srcCol)  # 整数部分j，小数部分u
                    C = np.array([self.BF(1 + u), self.BF(u), self.BF(1 - u), self.BF(2 - u)])
                    C = C.T
                    j = int(j)
                    for band in range(self.bands):
                        B = self.Get16Value(i, j, band)
                        self.resampleResult[row, col, band] = np.dot(np.dot(A, B), C)

    def BF(self, x):  # 双立方卷积公式
        if 0 <= abs(x) <= 1:
            return 1 - 2 * x ** 2 + abs(x) ** 3
        elif 1 < np.abs(x) <= 2:
            return 4 - 8 * abs(x) + 5 * x ** 2 - abs(x) ** 3

    def Get16Value(self, row, col, band):  # 获取4*4区域信息
        if 1 <= row <= self.origin_height - 3 and 1 <= col <= self.origin_width - 3:
            return self.origin_data[row - 1:row + 3, col - 1:col + 3, band]
        else:
            B = np.zeros([4, 4])
            for i in range(4):
                for j in range(4):
                    B[i, j] = self.GetValue(row - 1 + i, col - 1 + i, band)

        return B

    def GetValue(self, row, col, band):
        if row >= self.origin_height:
            row = self.origin_height - 1
        elif row <= 0:
            row = 0

        if col >= self.origin_width:
            col = self.origin_width - 1
        elif col <= 0:
            col = 0

        return self.origin_data[row, col, band]


# 程序主入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
