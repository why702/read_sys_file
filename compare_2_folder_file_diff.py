import os
import numpy as np
import matplotlib.pylab as plt
from itertools import zip_longest
import cv2
import re
import csv
import argparse
import util


def compare_png(folder0, folder1):
    # search bins
    ipp_list0 = util.read_pngs(folder0)
    ipp_list1 = util.read_pngs(folder1)

    for i in range(len(ipp_list0)):
        img0 = ipp_list0[i].astype(np.float)
        img1 = ipp_list1[i].astype(np.float)
        imgDiff = np.subtract(img0, img1)
        max_diff = np.max(np.abs(imgDiff))
        print("max_diff = {}".format(max_diff))
        cv2.normalize(imgDiff, imgDiff, 0, 1, cv2.NORM_MINMAX)
        cv2.imshow("",imgDiff)
        cv2.waitKey()
        cv2.normalize(imgDiff, imgDiff, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        cv2.imwrite("imgDiff.png",imgDiff)
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("index_path0", help="directory to parse")
    parser.add_argument("index_path1", help="directory to parse")
    args = parser.parse_args()

    index_file0 = args.index_path0
    index_file1 = args.index_path1

    compare_png(index_file0, index_file1)
    pass
