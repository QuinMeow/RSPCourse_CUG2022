import sys
import re
import numpy as np
from PyQt5.Qt import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from osgeo import gdal

from MainWin import *
from BandMathWin import *


# 定义主窗口类，继承自MainWin
class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.MainView = MyMainView(self.MainView)
        stretch_list = ["无拉伸", "2%线性拉伸"]
        self.ComBox_Stretch.addItems(stretch_list)
        # 初始化成员对象
        self.im_width = 0
        self.im_height = 0
        self.im_bands = 0
        self.im_geotrans = ''
        self.im_proj = ''
        self.qim_data = np.zeros((0, 0, 0))
        # 处理信号与槽的连接
        self.Btn_ReadImage.clicked.connect(self.read_img)
        self.Btn_ShowImage.clicked.connect(self.show_img)
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
        filename = self.LinEdit_ImageAddress.text()
        dataset = gdal.Open(filename)  # 打开文件
        self.im_width = dataset.RasterXSize  # 栅格矩阵的列数
        self.im_height = dataset.RasterYSize  # 栅格矩阵的行数
        self.im_bands = dataset.RasterCount  # 波段数
        self.im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵，左上角像素的大地坐标和像素分辨率
        self.im_proj = dataset.GetProjection()  # 地图投影信息，字符串表示
        im_data = dataset.ReadAsArray(0, 0, self.im_width, self.im_height)
        self.qim_data = np.rollaxis(im_data, 0, 3)
        # 设置UI波段最大值
        self.SpBox_Red.setMaximum(self.im_bands)
        self.SpBox_Green.setMaximum(self.im_bands)
        self.SpBox_Blue.setMaximum(self.im_bands)
        del dataset

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

    def bandMath(self):
        """
        波段运算，打开窗口并将结果放入MainView
        :return:
        """
        BMW = BandMathWindow(self.qim_data)  # 创建波段运算窗口
        BMW.show()
        if BMW.exec_() == QDialog.Accepted:
            self.MainView.showInput(BMW.bandMathResult)


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
        formula = self.LinEdit_Formula.text()
        # 合并非符号
        formula = re.split(r'([\+\-\*\/\(\)])', formula)
        formula = list(filter(None, formula))
        behind = []
        s = Stack(stack=[], top=-1)
        # 遍历表达式
        for i in formula:
            # 如果表达式元素为+或-，由于+或-的运算优先级最低，所以如果栈为非空，则从栈顶开始遍历栈符号，依次出栈，直到栈为空或者是遇到(
            if i == '+' or i == '-':
                if s.top > -1:
                    while s.top > -1 and s.stack[s.top] != '(':
                        behind.append(s.stack[s.top])
                        s.stack.pop()
                        s.top -= 1
                    # 将此时在表达式中遍历的这个符号入栈，也就是i
                    s.stack.append(i)
                    s.top += 1
                # 如果栈为空，直接入栈
                else:
                    s.stack.append(i)
                    s.top += 1
            # 如果表达式元素为*或/，由于*或/的运算优先级较高，所以如果栈为非空，则从栈顶开始遍历栈内符号，如果
            # 遇到*或者/，则依次出栈，直到栈为空或者是遇到(和+和-
            elif i == '*' or i == '/':
                if s.top > -1 and s.stack[s.top] != '(':
                    while s.stack[s.top] == '*' and s.stack[s.top] == '/':
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

    # 遍历后缀表达式，如果遇到数字，将其放入栈中，如果遇到符号，则取出栈中最顶上的两个数字进行
    # 计算，最顶上的那个数字是右项。运算完成之后将结果再存回栈中
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


# 程序主入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
