import sys

import numpy as np
from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from osgeo import gdal

from MainWin import *


# 定义主窗口类，继承自MainWin
class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        # 处理信号与槽的连接
        self.Btn_ReadImage.clicked.connect(self.read_img)
        self.Btn_ShowImage.clicked.connect(self.show_img)

    def read_img(self):
        filename = self.LinEdit_ImageAddress.text()
        dataset = gdal.Open(filename)  # 打开文件
        dy = gdal.GDT_Byte
        gdal.GetDataTypeSize(dy)
        self.im_width = dataset.RasterXSize  # 栅格矩阵的列数
        self.im_height = dataset.RasterYSize  # 栅格矩阵的行数
        self.im_bands = dataset.RasterCount  # 波段数
        self.im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵，左上角像素的大地坐标和像素分辨率
        self.im_proj = dataset.GetProjection()  # 地图投影信息，字符串表示
        im_data = dataset.ReadAsArray(0, 0, self.im_width, self.im_height)
        self.qim_data = np.rollaxis(im_data[0:3], 0, 3)
        del dataset

    def show_img(self):
        height, width, bytesPerComponent = self.qim_data.shape
        size = QSize(self.MainView.size().width() - 10, self.MainView.size().height() - 10)
        bytesPerLine = bytesPerComponent * width
        self.QImg = QImage(self.qim_data.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(self.QImg).scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.item = QGraphicsPixmapItem(self.pixmap)
        self.scene = QGraphicsScene()  # 创建场景
        self.scene.addItem(self.item)
        self.MainView.setScene(self.scene)


# 程序主入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    # myWin.read_img()
    # myWin.show_img()
    sys.exit(app.exec_())
