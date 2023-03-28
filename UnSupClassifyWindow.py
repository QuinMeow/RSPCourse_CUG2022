import numpy as np
from PyQt5.QtWidgets import *

from UnSupClassifyWin import *

import numpy
import math
import random


# Class
class Pixel:
    """像素"""

    def __init__(self, initX: int, initY: int, initColor):
        self.x = initX
        self.y = initY
        self.color = initColor


class Cluster:
    """簇"""

    def __init__(self, initCenter):
        self.center = initCenter
        self.pixelList = []


class ClusterPair:
    """簇对"""

    def __init__(self, initClusterAIndex: int, initClusterBIndex: int, initDistance):
        self.clusterAIndex = initClusterAIndex
        self.clusterBIndex = initClusterBIndex
        self.distance = initDistance


def distanceBetween(colorA, colorB) -> float:
    """
    距离度量，优化欧氏距离
    :param colorA:
    :param colorB:
    :return:
    """
    aveR = float(int(colorA[0]) + int(colorB[0])) / 2
    dR = int(colorA[0]) - int(colorB[0])
    dG = int(colorA[1]) - int(colorB[1])
    dB = int(colorA[2]) - int(colorB[2])
    return math.sqrt((2 + aveR / 256) * (dR ** 2) + 4 * (dG ** 2) + (2 + (255 - aveR) / 256) * (dB ** 2))


def doISODATA(image_data, K: int, TN: int, TS: float, TC: int, L: int, I: int):
    img_array = image_data
    imgX, imgY, band = img_array.shape
    cluster_list = []
    # 随机生成K个聚类中心
    for i in range(0, K):
        randomX = random.randint(0, imgX - 1)
        randomY = random.randint(0, imgY - 1)
        duplicated = False
        for cluster in cluster_list:
            if (cluster.center[0] == img_array[randomX, randomY, 0] and
                    cluster.center[1] == img_array[randomX, randomY, 1] and
                    cluster.center[2] == img_array[randomX, randomY, 2]):
                duplicated = True
                break
        if not duplicated:
            cluster_list.append(Cluster(numpy.array([img_array[randomX, randomY, 0],
                                                    img_array[randomX, randomY, 1],
                                                    img_array[randomX, randomY, 2]],
                                                   dtype=numpy.uint8)))

    # 迭代
    iteration_count = 0
    did_anything_in_last_iteration = True
    while True:
        iteration_count += 1

        # 清除簇中的所有像素
        for cluster in cluster_list:
            cluster.pixelList.clear()
        print("第{0}次迭代".format(iteration_count))

        # 逐像元分类
        for row in range(0, imgX):
            for col in range(0, imgY):
                target_cluster_index = 0
                target_cluster_distance = distanceBetween(img_array[row, col], cluster_list[0].center)
                # 分类
                for i in range(1, len(cluster_list)):
                    currentDistance = distanceBetween(img_array[row, col], cluster_list[i].center)
                    if currentDistance < target_cluster_distance:
                        target_cluster_distance = currentDistance
                        target_cluster_index = i
                cluster_list[target_cluster_index].pixelList.append(Pixel(row, col, img_array[row, col]))

        # 检查是否满足样本最小数目
        goto_next_iteration = False
        for i in range(len(cluster_list) - 1, -1, -1):
            if len(cluster_list[i].pixelList) < TN:
                # 重新分类
                cluster_list.pop(i)
                goto_next_iteration = True
                break
        if goto_next_iteration:
            continue

        # 重新计算聚类中心
        for cluster in cluster_list:
            sumR = 0.0
            sumG = 0.0
            sumB = 0.0
            for pixel in cluster.pixelList:
                sumR += int(pixel.color[0])
                sumG += int(pixel.color[1])
                sumB += int(pixel.color[2])
            aveR = round(sumR / len(cluster.pixelList))
            aveG = round(sumG / len(cluster.pixelList))
            aveB = round(sumB / len(cluster.pixelList))
            if (aveR != cluster.center[0] and
                    aveG != cluster.center[1] and
                    aveB != cluster.center[2]):
                did_anything_in_last_iteration = True
            cluster.center = numpy.array([aveR, aveG, aveB], dtype=numpy.uint8)
        if iteration_count > I:
            break
        if not did_anything_in_last_iteration:  # 中心无变化
            break

        # 计算平均距离
        ave_disctance_list = []
        sum_distance_all = 0.0
        for cluster in cluster_list:
            currentSumDistance = 0.0
            for pixel in cluster.pixelList:
                currentSumDistance += distanceBetween(pixel.color, cluster.center)
            ave_disctance_list.append(float(currentSumDistance) / len(cluster.pixelList))
            sum_distance_all += currentSumDistance
        ave_distance_all = float(sum_distance_all) / (imgX * imgY)

        if (len(cluster_list) <= K / 2) or not (iteration_count % 2 == 0 or len(cluster_list) >= K * 2):
            # 分裂
            print("分裂类:", end='', flush=True)
            for i in range(len(cluster_list) - 1, -1, -1):
                currentSD = [0.0, 0.0, 0.0]
                for pixel in cluster_list[i].pixelList:
                    currentSD[0] += (int(pixel.color[0]) - int(cluster_list[i].center[0])) ** 2
                    currentSD[1] += (int(pixel.color[1]) - int(cluster_list[i].center[1])) ** 2
                    currentSD[2] += (int(pixel.color[2]) - int(cluster_list[i].center[2])) ** 2
                currentSD[0] = math.sqrt(currentSD[0] / len(cluster_list[i].pixelList))
                currentSD[1] = math.sqrt(currentSD[1] / len(cluster_list[i].pixelList))
                currentSD[2] = math.sqrt(currentSD[2] / len(cluster_list[i].pixelList))
                # 查找SD中RGB的最大值
                maxSD = currentSD[0]
                for j in (1, 2):
                    maxSD = currentSD[j] if currentSD[j] > maxSD else maxSD
                if (maxSD > TS) and (
                        (ave_disctance_list[i] > ave_distance_all and len(cluster_list[i].pixelList) > 2 * (TN + 1)) or (
                        len(cluster_list) < K / 2)):
                    gamma = 0.5 * maxSD
                    cluster_list[i].center[0] += gamma
                    cluster_list[i].center[1] += gamma
                    cluster_list[i].center[2] += gamma
                    cluster_list.append(Cluster(numpy.array([cluster_list[i].center[0],
                                                            cluster_list[i].center[1],
                                                            cluster_list[i].center[2]],
                                                           dtype=numpy.uint8)))
                    cluster_list[i].center[0] -= gamma * 2
                    cluster_list[i].center[1] -= gamma * 2
                    cluster_list[i].center[2] -= gamma * 2
                    cluster_list.append(Cluster(numpy.array([cluster_list[i].center[0],
                                                            cluster_list[i].center[1],
                                                            cluster_list[i].center[2]],
                                                           dtype=numpy.uint8)))
                    cluster_list.pop(i)
        elif (iteration_count % 2 == 0) or (len(cluster_list) >= K * 2) or (iteration_count == I):
            # 合并
            print("合并类:", end='', flush=True)
            did_anything_in_last_iteration = False
            cluster_pair_list = []
            for i in range(0, len(cluster_list)):
                for j in range(0, i):
                    currentDistance = distanceBetween(cluster_list[i].center, cluster_list[j].center)
                    if currentDistance < TC:
                        cluster_pair_list.append(ClusterPair(i, j, currentDistance))

            cluster_pair_list_sorted = sorted(cluster_pair_list, key=lambda clusterPair: clusterPair.distance)
            new_cluster_center_list = []
            merged_cluster_index_list = []
            mergedPairCount = 0
            for clusterPair in cluster_pair_list_sorted:
                has_been_merged = False
                for index in merged_cluster_index_list:
                    if clusterPair.clusterAIndex == index or clusterPair.clusterBIndex == index:
                        has_been_merged = True
                        break
                if has_been_merged:
                    continue
                new_center_r = int((len(cluster_list[clusterPair.clusterAIndex].pixelList) * float(
                    cluster_list[clusterPair.clusterAIndex].center[0]) + len(
                    cluster_list[clusterPair.clusterBIndex].pixelList) * float(
                    cluster_list[clusterPair.clusterBIndex].center[0])) / (
                                         len(cluster_list[clusterPair.clusterAIndex].pixelList) + len(
                                     cluster_list[clusterPair.clusterBIndex].pixelList)))
                new_center_g = int((len(cluster_list[clusterPair.clusterAIndex].pixelList) * float(
                    cluster_list[clusterPair.clusterAIndex].center[1]) + len(
                    cluster_list[clusterPair.clusterBIndex].pixelList) * float(
                    cluster_list[clusterPair.clusterBIndex].center[1])) / (
                                         len(cluster_list[clusterPair.clusterAIndex].pixelList) + len(
                                     cluster_list[clusterPair.clusterBIndex].pixelList)))
                new_center_b = int((len(cluster_list[clusterPair.clusterAIndex].pixelList) * float(
                    cluster_list[clusterPair.clusterAIndex].center[2]) + len(
                    cluster_list[clusterPair.clusterBIndex].pixelList) * float(
                    cluster_list[clusterPair.clusterBIndex].center[2])) / (
                                         len(cluster_list[clusterPair.clusterAIndex].pixelList) + len(
                                     cluster_list[clusterPair.clusterBIndex].pixelList)))
                new_cluster_center_list.append([new_center_r, new_center_g, new_center_b])
                merged_cluster_index_list.append(clusterPair.clusterAIndex)
                merged_cluster_index_list.append(clusterPair.clusterBIndex)
                mergedPairCount += 1
                if mergedPairCount > L:
                    break
            if len(merged_cluster_index_list) > 0:
                did_anything_in_last_iteration = True
            merged_cluster_index_list_sorted = sorted(merged_cluster_index_list, key=lambda clusterIndex: clusterIndex,
                                                  reverse=True)
            for index in merged_cluster_index_list_sorted:
                cluster_list.pop(index)
            for center in new_cluster_center_list:
                cluster_list.append(Cluster(numpy.array([center[0], center[1], center[2]], dtype=numpy.uint8)))

    # 生成新影像
    print("聚类完成")
    print("聚类结果为{0}类".format(len(cluster_list)))
    new_img_array = numpy.zeros((imgX, imgY, 3), dtype=numpy.uint8)
    color_table = np.array(
        [[255, 0, 0], [0, 255, 0], [0, 0, 255], [0, 255, 255], [255, 0, 255], [255, 255, 0], [47, 79, 79],
         [255, 215, 0], [255, 99, 71]],
        dtype=int)
    kind = -1
    for cluster in cluster_list:
        kind += 1
        for pixel in cluster.pixelList:
            new_img_array[pixel.x, pixel.y, :] = color_table[kind, :]  # 根据颜色查找表赋予颜色

    return new_img_array


class UnSupClassifyWindow(QDialog, Ui_UnSupClassifyWin):
    def __init__(self, qim_data):
        super(UnSupClassifyWindow, self).__init__()
        self.setupUi(self)
        self.origin_data = qim_data
        if self.origin_data.dtype != np.uint8:  # 非8位无符号整型时
            self.origin_data = self.compress(self.origin_data)
        self.origin_height, self.origin_width, self.bands = qim_data.shape
        self.Classified_data = np.zeros([self.origin_height, self.origin_width, 3])
        self.buttonBox.accepted.connect(self.USC)
        self.argvK = self.SpBox_K.value()
        self.argvTN = self.SpBox_TN.value()
        self.argvTS = self.SpBox_TS.value()
        self.argvTC = self.SpBox_TC.value()
        self.argvL = self.SpBox_L.value()
        self.argvI = self.SpBox_I.value()

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

    def USC(self):
        self.argvK = self.SpBox_K.value()
        self.argvTN = self.SpBox_TN.value()
        self.argvTS = self.SpBox_TS.value()
        self.argvTC = self.SpBox_TC.value()
        self.argvL = self.SpBox_L.value()
        self.argvI = self.SpBox_I.value()

        self.Classified_data = doISODATA(self.origin_data, self.argvK, self.argvTN, self.argvTS, self.argvTC,
                                         self.argvL, self.argvI)
