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


# def read_tiff(path):
#     """读取栅格数据"""
#     # 参数类型检查
#     if isinstance(path, gdal.Dataset):
#         dataset = path
#     else:
#         dataset = gdal.Open(path)
#
#     if dataset:
#         im_width = dataset.RasterXSize  # 栅格矩阵的列数
#         im_height = dataset.RasterYSize  # 栅格矩阵的行数
#         im_bands = dataset.RasterCount  # 波段数
#         im_proj = dataset.GetProjection()  # 获取投影信息
#         im_geotrans = dataset.GetGeoTransform()  # 获取仿射矩阵信息
#         im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 获取数据
#         return im_data, im_width, im_height, im_bands, im_geotrans, im_proj


class SupClassifyWindow(QDialog, Ui_SupClassifyWin):
    def __init__(self, raster_addr, qim_data):
        super(SupClassifyWindow, self).__init__()
        self.setupUi(self)
        self.in_raster = raster_addr
        self.origin_data = qim_data
        self.origin_height, self.origin_width, self.bands = qim_data.shape
        self.Classified_data = np.zeros([self.origin_height, self.origin_width, 3])
        self.in_shp = self.LinEdit_ShpAddress.text()
        self.colorTable = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=int)

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
        bands = train_X.shape[0]  # 波段数
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
        # im_data, im_width, im_height, im_bands, im_geotrans, im_proj = self.qim_data  # 读取待分类栅格数据
        rs_data = np.zeros((class_num, self.origin_height, self.origin_width))  # 新建像元属于每个类别下的概率数据
        for i in range(class_num):
            # tmp_data = im_data.transpose(1, 2, 0)
            rs_i = np.dot(self.origin_data, f[i][0])
            rs_i = rs_i + f[i][1]
            rs_data[i, :, :] = rs_i
        # 分类最大值index
        rs_index = np.argmax(rs_data, axis=0)  # 提取最大概率所属的类别索引
        # 分类index 对应的 分类标签label
        label_dict = dict(zip(np.array([i for i in range(class_num)]), class_label))
        rs_label = np.vectorize(label_dict.get)(rs_index)
        for i in range(self.origin_height):
            for j in range(self.origin_width):
                self.Classified_data[i, j, :] = self.colorTable[rs_index[i, j], :]
