import numpy as np
from PyQt5.QtWidgets import *

from UnSupClassifyWin import *

import numpy
import math
import random


# Class
class Pixel:
    """Pixel"""

    def __init__(self, initX: int, initY: int, initColor):
        self.x = initX
        self.y = initY
        self.color = initColor


class Cluster:
    """Cluster in Gray"""

    def __init__(self, initCenter):
        self.center = initCenter
        self.pixelList = []


class ClusterPair:
    """Cluster Pair"""

    def __init__(self, initClusterAIndex: int, initClusterBIndex: int, initDistance):
        self.clusterAIndex = initClusterAIndex
        self.clusterBIndex = initClusterBIndex
        self.distance = initDistance


# Functions

# RGB
def distanceBetween(colorA, colorB) -> float:
    aveR = float(int(colorA[0]) + int(colorB[0])) / 2
    dR = int(colorA[0]) - int(colorB[0])
    dG = int(colorA[1]) - int(colorB[1])
    dB = int(colorA[2]) - int(colorB[2])
    return math.sqrt((2 + aveR / 256) * (dR ** 2) + 4 * (dG ** 2) + (2 + (255 - aveR) / 256) * (dB ** 2))


def doISODATARGB(image_data, K: int, TN: int, TS: float, TC: int, L: int, I: int):
    imgArray = image_data
    imgX, imgY, band = imgArray.shape
    clusterList = []
    # Generate K cluster centers randomly
    for i in range(0, K):
        randomX = random.randint(0, imgX - 1)
        randomY = random.randint(0, imgY - 1)
        duplicated = False
        for cluster in clusterList:
            if (cluster.center[0] == imgArray[randomX, randomY, 0] and
                    cluster.center[1] == imgArray[randomX, randomY, 1] and
                    cluster.center[2] == imgArray[randomX, randomY, 2]):
                duplicated = True
                break
        if not duplicated:
            clusterList.append(Cluster(numpy.array([imgArray[randomX, randomY, 0],
                                                    imgArray[randomX, randomY, 1],
                                                    imgArray[randomX, randomY, 2]],
                                                   dtype=numpy.uint8)))

    # Iteration
    iterationCount = 0
    didAnythingInLastIteration = True
    while True:
        iterationCount += 1

        # Clear the pixel lists of all clusters
        for cluster in clusterList:
            cluster.pixelList.clear()
        print("------")
        print("Iteration: {0}".format(iterationCount))

        # Classify all pixels into clusters
        print("Classifying...", end='', flush=True)
        for row in range(0, imgX):
            for col in range(0, imgY):
                targetClusterIndex = 0
                targetClusterDistance = distanceBetween(imgArray[row, col], clusterList[0].center)
                # Classify
                for i in range(1, len(clusterList)):
                    currentDistance = distanceBetween(imgArray[row, col], clusterList[i].center)
                    if currentDistance < targetClusterDistance:
                        targetClusterDistance = currentDistance
                        targetClusterIndex = i
                clusterList[targetClusterIndex].pixelList.append(Pixel(row, col, imgArray[row, col]))
        print(" Finished.")

        # Check TN
        gotoNextIteration = False
        for i in range(len(clusterList) - 1, -1, -1):
            if len(clusterList[i].pixelList) < TN:
                # Re-classify
                clusterList.pop(i)
                gotoNextIteration = True
                break
        if gotoNextIteration:
            print("TN checking not passed.")
            continue
        print("TN checking passed.")

        # Recalculate the centers
        print("Recalculating the centers...", end='', flush=True)
        for cluster in clusterList:
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
                didAnythingInLastIteration = True
            cluster.center = numpy.array([aveR, aveG, aveB], dtype=numpy.uint8)
        print(" Finished.")
        if iterationCount > I:
            break
        if not didAnythingInLastIteration:
            print("More iteration is not necessary.")
            break

        # Calculate the average distance
        print("Preparing for Merging and Spliting...", end='', flush=True)
        aveDisctanceList = []
        sumDistanceAll = 0.0
        for cluster in clusterList:
            currentSumDistance = 0.0
            for pixel in cluster.pixelList:
                currentSumDistance += distanceBetween(pixel.color, cluster.center)
            aveDisctanceList.append(float(currentSumDistance) / len(cluster.pixelList))
            sumDistanceAll += currentSumDistance
        aveDistanceAll = float(sumDistanceAll) / (imgX * imgY)
        print(" Finished.")

        if (len(clusterList) <= K / 2) or not (iterationCount % 2 == 0 or len(clusterList) >= K * 2):
            # Split
            print("Split:", end='', flush=True)
            beforeCount = len(clusterList)
            for i in range(len(clusterList) - 1, -1, -1):
                currentSD = [0.0, 0.0, 0.0]
                for pixel in clusterList[i].pixelList:
                    currentSD[0] += (int(pixel.color[0]) - int(clusterList[i].center[0])) ** 2
                    currentSD[1] += (int(pixel.color[1]) - int(clusterList[i].center[1])) ** 2
                    currentSD[2] += (int(pixel.color[2]) - int(clusterList[i].center[2])) ** 2
                currentSD[0] = math.sqrt(currentSD[0] / len(clusterList[i].pixelList))
                currentSD[1] = math.sqrt(currentSD[1] / len(clusterList[i].pixelList))
                currentSD[2] = math.sqrt(currentSD[2] / len(clusterList[i].pixelList))
                # Find the max in SD of R, G and B
                maxSD = currentSD[0]
                for j in (1, 2):
                    maxSD = currentSD[j] if currentSD[j] > maxSD else maxSD
                if (maxSD > TS) and (
                        (aveDisctanceList[i] > aveDistanceAll and len(clusterList[i].pixelList) > 2 * (TN + 1)) or (
                        len(clusterList) < K / 2)):
                    gamma = 0.5 * maxSD
                    clusterList[i].center[0] += gamma
                    clusterList[i].center[1] += gamma
                    clusterList[i].center[2] += gamma
                    clusterList.append(Cluster(numpy.array([clusterList[i].center[0],
                                                            clusterList[i].center[1],
                                                            clusterList[i].center[2]],
                                                           dtype=numpy.uint8)))
                    clusterList[i].center[0] -= gamma * 2
                    clusterList[i].center[1] -= gamma * 2
                    clusterList[i].center[2] -= gamma * 2
                    clusterList.append(Cluster(numpy.array([clusterList[i].center[0],
                                                            clusterList[i].center[1],
                                                            clusterList[i].center[2]],
                                                           dtype=numpy.uint8)))
                    clusterList.pop(i)
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))
        elif (iterationCount % 2 == 0) or (len(clusterList) >= K * 2) or (iterationCount == I):
            # Merge
            print("Merge:", end='', flush=True)
            beforeCount = len(clusterList)
            didAnythingInLastIteration = False
            clusterPairList = []
            for i in range(0, len(clusterList)):
                for j in range(0, i):
                    currentDistance = distanceBetween(clusterList[i].center, clusterList[j].center)
                    if currentDistance < TC:
                        clusterPairList.append(ClusterPair(i, j, currentDistance))

            clusterPairListSorted = sorted(clusterPairList, key=lambda clusterPair: clusterPair.distance)
            newClusterCenterList = []
            mergedClusterIndexList = []
            mergedPairCount = 0
            for clusterPair in clusterPairListSorted:
                hasBeenMerged = False
                for index in mergedClusterIndexList:
                    if clusterPair.clusterAIndex == index or clusterPair.clusterBIndex == index:
                        hasBeenMerged = True
                        break
                if hasBeenMerged:
                    continue
                newCenterR = int((len(clusterList[clusterPair.clusterAIndex].pixelList) * float(
                    clusterList[clusterPair.clusterAIndex].center[0]) + len(
                    clusterList[clusterPair.clusterBIndex].pixelList) * float(
                    clusterList[clusterPair.clusterBIndex].center[0])) / (
                                         len(clusterList[clusterPair.clusterAIndex].pixelList) + len(
                                     clusterList[clusterPair.clusterBIndex].pixelList)))
                newCenterG = int((len(clusterList[clusterPair.clusterAIndex].pixelList) * float(
                    clusterList[clusterPair.clusterAIndex].center[1]) + len(
                    clusterList[clusterPair.clusterBIndex].pixelList) * float(
                    clusterList[clusterPair.clusterBIndex].center[1])) / (
                                         len(clusterList[clusterPair.clusterAIndex].pixelList) + len(
                                     clusterList[clusterPair.clusterBIndex].pixelList)))
                newCenterB = int((len(clusterList[clusterPair.clusterAIndex].pixelList) * float(
                    clusterList[clusterPair.clusterAIndex].center[2]) + len(
                    clusterList[clusterPair.clusterBIndex].pixelList) * float(
                    clusterList[clusterPair.clusterBIndex].center[2])) / (
                                         len(clusterList[clusterPair.clusterAIndex].pixelList) + len(
                                     clusterList[clusterPair.clusterBIndex].pixelList)))
                newClusterCenterList.append([newCenterR, newCenterG, newCenterB])
                mergedClusterIndexList.append(clusterPair.clusterAIndex)
                mergedClusterIndexList.append(clusterPair.clusterBIndex)
                mergedPairCount += 1
                if mergedPairCount > L:
                    break
            if len(mergedClusterIndexList) > 0:
                didAnythingInLastIteration = True
            mergedClusterIndexListSorted = sorted(mergedClusterIndexList, key=lambda clusterIndex: clusterIndex,
                                                  reverse=True)
            for index in mergedClusterIndexListSorted:
                clusterList.pop(index)
            for center in newClusterCenterList:
                clusterList.append(Cluster(numpy.array([center[0], center[1], center[2]], dtype=numpy.uint8)))
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))

    # Generate the new image martrix
    print("Over")
    print("Classified to {0} kinds.".format(len(clusterList)))
    newImgArray = numpy.zeros((imgX, imgY, 3), dtype=numpy.uint8)
    for cluster in clusterList:
        for pixel in cluster.pixelList:
            newImgArray[pixel.x, pixel.y, 0] = int(cluster.center[0])
            newImgArray[pixel.x, pixel.y, 1] = int(cluster.center[1])
            newImgArray[pixel.x, pixel.y, 2] = int(cluster.center[2])

    return newImgArray


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

        self.Classified_data = doISODATARGB(self.origin_data, self.argvK, self.argvTN, self.argvTS, self.argvTC,
                                            self.argvL, self.argvI)
