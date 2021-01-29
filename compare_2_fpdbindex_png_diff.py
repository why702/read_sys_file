import os
import numpy as np
import matplotlib.pylab as plt
from itertools import zip_longest
import cv2
import re
import csv
import argparse

def parse_genuines(gen_file):
    with open(gen_file, 'r') as file:
        all_lines = file.readlines()

    data = []
    for line in all_lines:
        if line[0:1] == "#":
            continue
        match = re.findall(r"\s*([0-9]+)\s*", line)
        if len(match) >= 23:
            info = dict()
            info['enroll'] = match[0] + match[1] + match[2]
            info['verify'] = match[3] + match[4] + match[5]
            info['match'] = match[6]
            info['score'] = match[11]
            data.append(info)
    return data


def parse_index(index_file):
    with open(index_file, 'r') as file:
        all_lines = file.readlines()

    data = []
    for line in all_lines:
        if line[0:1] == "#":
            continue
        if line[0:6] == "ERROR!":
            continue
        match = re.findall(r"\s*([0-9a-zA-Z\\\-\_\=\[\]\.]+)\s*", line)
        if len(match) >= 5:
            info = dict()
            info['id'] = match[0] + match[1] + match[3]
            info['path'] = match[4]
            data.append(info)
    return data

def find_path(index_data, id):
    for info in index_data:
        if info['id'] == id:
            return info['path']

def find_gen_info(gen_data, id):
    for info in gen_data:
        if info['verify'] == id:
            return info

def find_gen_info_sn(gen_data, index_data, id, gen_data1, index_data1):
    # find path
    path = find_path(index_data, id)

    #find sn
    sn = path[path.rfind('\\') + 1:path.rfind('_00000000_')]

    id1 = ''
    for idx in index_data1:
        if idx['path'].find(sn) >= 0:
            id1 = idx['id']
            break

    for info in gen_data:
        if info['verify'] == id1:
            return info


expr = re.compile(
    r"(\S+)\\(\d+)\\(enroll|verify|identify)\\(st|45d|90d|135d)\\([0-9]+\\)*(\S+).png"
)
expr_partial = re.compile(
    r"(\S+)\\(\d+)\\(enroll|verify)\\(\S+)\\([0-9]+)\\(\S+).png"
)
expr_simple_partial = re.compile(
    r"(\S+)\\(\d+)\\(enroll|verify)\\([0-9]+)\\(\S+).png"
)
expr_enroll = re.compile(
    r"(\S+)\\(\d+)\\(enroll)\\(\S+).png"
)

def compare_png(index_file0, index_file1):
    index_dir0 = os.path.dirname(index_file0)
    index_dir1 = os.path.dirname(index_file1)
    index_data0 = parse_index(index_file0)
    index_data1 = parse_index(index_file1)
    for f0 in index_data0:
        png_path0 = os.path.join(index_dir0,f0['path'])

        # find sn
        sn = ""
        if png_path0.rfind('_0x') > 0:
            sn = png_path0[png_path0.rfind('\\') + 1:png_path0.rfind('_0x')]
        else:
            sn = png_path0[png_path0.rfind('\\') + 1:png_path0.rfind('\\') + 26]

        if sn == '20200929_185505_637':
            print()

        # find png_path1
        png_path1 = ""
        for f1 in index_data1:
            if f1['path'].find(sn) >= 0:
                png_path1 = os.path.join(index_dir1,f1['path'])
                break


        max_diff = 0
        if png_path1 is not "":

            img0 = cv2.imread(png_path0, cv2.IMREAD_GRAYSCALE).astype('float32')
            img1 = cv2.imread(png_path1, cv2.IMREAD_GRAYSCALE).astype('float32')
            imgDiff = np.subtract(img0, img1)
            max_diff = np.max(np.abs(imgDiff))
            print("{}\nmax_diff = {}".format(png_path0, max_diff))
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