import sys

import numpy as np
from PyQt5.Qt import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from osgeo import gdal

from MainWin import *


# 定义主窗口类，继承自MainWin
class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.MainView = MyMainView(self.MainView)
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

        if self.qim_data.dtype != np.uint8:  # 非8位无符号整型时
            self.qim_data = self.compress()
        del dataset

    def compress(self):
        """
        16位影像转8位
        """
        array_data = self.qim_data
        rows = self.im_height
        cols = self.im_width
        bands = self.im_bands

        compress_data = np.zeros((rows, cols, bands))

        for i in range(bands):
            band_max = np.max(array_data[:, :, i])
            band_min = np.min(array_data[:, :, i])
            compress_data[:, :, i] = ((array_data[:, :, i] - band_min) / band_max * 255)

        int_data = compress_data.astype('uint8')
        return int_data

    def show_img(self):
        """
        显示影像到MainView
        :return:
        """
        Band = np.array((int(self.SpBox_Red.value()) - 1, int(self.SpBox_Green.value()) - 1, \
                         int(self.SpBox_Blue.value()) - 1))
        show_img = self.qim_data[:, :, Band]
        height, width, bytesPerComponent = show_img.shape
        # size = QSize(self.MainView.size().width() - 10, self.MainView.size().height() - 10)
        bytesPerLine = bytesPerComponent * width
        self.QImg = QImage(show_img.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888)
        # self.pixmap = QPixmap.fromImage(self.QImg).scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # self.item = QGraphicsPixmapItem(self.pixmap)
        # self.scene = QGraphicsScene()  # 创建场景
        # self.scene.addItem(self.item)
        # self.MainView.setScene(self.scene)
        self.MainView.addLayer(self.QImg)
        # 连接信号与槽2
        self.SpBox_Ratio.textChanged.connect(self.MainView.changeRatio)
        self.MainView.ratioChanged.connect(self.SpBox_Ratio.setValue)


class MyMainView(QGraphicsView):
    # 信号
    ratioChanged = QtCore.pyqtSignal(float)

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
        self.pixmapItem = None

    def addLayer(self, image):
        """
        将外部的QImage放入scene
        :param image:
        :return:
        """
        if self.pixmapItem != None:
            originX = self.pixmapItem.x()
            originY = self.pixmapItem.y()
        else:
            originX, originY = 0, 0
        self.ratio = min(self.width() / image.width(), self.height() / image.height())
        self.pixmap = QPixmap.fromImage(image)
        self.pixmapItem = self.scene.addPixmap(self.pixmap)
        self.pixmapItem.setScale(self.ratio)
        self.pixmapItem.setPos(originX, originY)

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


# 程序主入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
