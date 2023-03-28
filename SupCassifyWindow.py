import os

from PyQt5.Qt import *
from PyQt5.QtWidgets import *

from SupClassifyWin import *

from osgeo import gdal, ogr
import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from shapely.geometry import mapping
from shapely.wkt import loads


def get_train_data(in_raster, in_shp, attr='CLASS_ID'):
    """获取训练数据集及其标签"""
    driver = ogr.GetDriverByName('ESRI Shapefile')
    data = driver.Open(in_shp, 0)
    layer = data.GetLayer(0)
    with rio.open(in_raster) as src:
        band_count = src.count
        X = np.array([], dtype=np.int16).reshape(band_count, 0)
        y = np.array([], dtype=np.int)
        feat = layer.GetNextFeature()
        while feat:
            LCtype = feat.GetField(attr)
            geom = feat.GetGeometryRef()
            geomWKT = geom.ExportToWkt()
            geo_feature = [mapping(loads(geomWKT))]
            clip_raster = mask(src, geo_feature, crop=True)[0]  # 提取roi
            clip_raster_nozero = clip_raster[:, ~np.all(clip_raster == 0, axis=0)]  # 提取非0像元
            y = np.append(y, [LCtype] * clip_raster_nozero.shape[1])
            X = np.hstack((X, clip_raster_nozero))
            feat = layer.GetNextFeature()
        layer.ResetReading()
    data.Destroy()
    return X, y


class SupClassifyWindow(QDialog, Ui_SupClassifyWin):
    def __init__(self, raster_addr, qim_data):
        super(SupClassifyWindow, self).__init__()
        self.setupUi(self)
        self.in_raster = raster_addr
        self.origin_data = qim_data
        self.origin_height, self.origin_width, self.bands = qim_data.shape
        self.Classified_data = np.zeros([self.origin_height, self.origin_width, 3])
        self.in_shp = self.LinEdit_ShpAddress.text()
        self.colorTable = np.array(
            [[255, 0, 0], [0, 255, 0], [0, 0, 255], [0, 255, 255], [255, 0, 255], [255, 255, 0], [47, 79, 79],
             [255, 215, 0], [255, 99, 71]],
            dtype=int)

        # 关联信号与槽
        self.buttonBox.accepted.connect(self.SupClassify)
        self.Btn_ChooseFile.clicked.connect(self.OpenShp)

    def OpenShp(self):
        openfile_name = QFileDialog.getOpenFileName(self, '选择文件', './', 'Shapefile(*.shp)')
        self.LinEdit_ShpAddress.setText(openfile_name[0])

    def SupClassify(self):
        self.in_shp = self.LinEdit_ShpAddress.text()
        train_X, train_y = get_train_data(self.in_raster, self.in_shp)
        class_num = len(np.unique(train_y))  # 待分类类别个数
        class_label = np.unique(train_y)  # 待分类类别标签
        u, c = [], []
        for i in class_label:
            label_index = np.argwhere(train_y == i)
            label_index = label_index.flatten()
            train_X_i = train_X[:, label_index]
            u_i = np.mean(train_X_i, axis=1)
            u_i = u_i.tolist()
            c_i = np.cov(train_X_i)
            u.append(u_i)
            c.append(c_i)
        # 假设协方差阵相同
        c_all = 0
        for i in range(class_num):
            c_all += c[i]
        # 计算每个类别的判别函数参量
        f = []
        for i in range(class_num):
            C_i = np.dot(np.linalg.inv(c_all), np.array(u[i]))  # size:(3,1)
            C_oi = -0.5 * np.dot(np.array(u[i]).reshape(1, -1), C_i)  # size:(1,1)
            f.append([C_i, C_oi])
        rs_data = np.zeros((class_num, self.origin_height, self.origin_width))  # 新建像元属于每个类别下的概率数
        sp_data = np.zeros((class_num, np.size(train_X, 1)))  # 对样本进行分类
        for i in range(class_num):
            rs_i = np.dot(self.origin_data, f[i][0])
            rs_i = rs_i + f[i][1]
            rs_data[i, :, :] = rs_i
            sp_i = np.dot(train_X.T, f[i][0])
            sp_i = sp_i + f[i][1]
            sp_data[i, :] = sp_i
        # 分类最大值index
        rs_index = np.argmax(rs_data, axis=0)  # 提取最大概率所属的类别索引
        sp_index = np.argmax(sp_data, axis=0)
        self.label_dict = dict(zip(np.array([i for i in range(class_num)]), class_label))
        sp_pred = np.vectorize(self.label_dict.get)(sp_index)
        for i in range(class_num):
            index = np.where(rs_index == i)
            self.Classified_data[index] = self.colorTable[i]
        self.Conf_mat = np.zeros((class_num, class_num), dtype=int)  # 混淆矩阵
        for i in range(class_num):
            label = class_label[i]
            label_index = np.argwhere(train_y == label)
            label_index = label_index.flatten()
            sp_pred_i = sp_pred[label_index]  # 某类样本实际分类情况
            for j in range(class_num):
                pred_label = class_label[j]
                self.Conf_mat[i][j] = np.size(np.argwhere(sp_pred_i == pred_label))


class ConfMatForm(QDialog):

    def __init__(self, label_dict, Conf_mat, parent=None):
        super(ConfMatForm, self).__init__(parent)
        self.table = QTableWidget()
        self.browser = QTextBrowser()
        # self.lineedit = QLineEdit("Type an expression and press Enter")
        # self.lineedit.selectAll()
        layout = QVBoxLayout()  # 垂直盒式布局
        layout.addWidget(self.table)
        layout.addWidget(self.browser)
        # layout.addWidget(self.lineedit)
        # layout = QGridLayout() #网格布局
        # layout.addWidget(self.browser，0, 0)
        # layout.addWidget(self.lineedit，0, 0)
        self.setLayout(layout)
        # self.lineedit.setFocus()
        # self.connect(self.lineedit, SIGNAL("returnPressed()"), self.updateUi)  # 信号绑定到槽，按回车后执行槽函数
        self.setWindowTitle("混淆矩阵")
        self.updateUi(label_dict, Conf_mat)

    def updateUi(self, label_dict, Conf_mat):
        self.table.setRowCount(np.size(Conf_mat, 0) + 1)
        self.table.setColumnCount(np.size(Conf_mat, 1) + 1)
        listE = list(label_dict.values())
        listE.append('Total')
        self.table.setHorizontalHeaderLabels(listE)
        self.table.setVerticalHeaderLabels(listE)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i in range(np.size(Conf_mat, 0)):
            for j in range(np.size(Conf_mat, 1)):
                newItem = QTableWidgetItem(str(Conf_mat[i][j]))
                self.table.setItem(i, j, newItem)
            newItem = QTableWidgetItem(str(np.sum(Conf_mat[i][:])))
            self.table.setItem(i, j + 1, newItem)
        for j in range(np.size(Conf_mat, 1)):
            newItem = QTableWidgetItem(str(np.sum(Conf_mat[:][j])))
            self.table.setItem(i + 1, j, newItem)
        newItem = QTableWidgetItem(str(np.sum(Conf_mat)))
        self.table.setItem(i + 1, j + 1, newItem)

        # 各种分类精度
        self.browser.clear()
        pixelSum = np.sum(Conf_mat)
        pixelDiagSum = np.sum(np.diag(Conf_mat))
        OvrAcc = pixelDiagSum / pixelSum
        self.browser.append("总体分类精度 = (%s/%s)  %s" % (pixelDiagSum, pixelSum, OvrAcc))
        Pe = 0
        for i in range(np.size(Conf_mat, 0)):
            Pe += np.sum(Conf_mat[i][:]) * np.sum(Conf_mat[:][i])
        Kappa = (pixelSum * pixelDiagSum - Pe) / (pixelSum * pixelSum - Pe)
        self.browser.append("Kappa系数 = %s" % (Kappa))
