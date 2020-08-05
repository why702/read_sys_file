import os
import numpy as np
import matplotlib.pylab as plt
from itertools import zip_longest
import cv2
import re
import csv
import argparse
import generate_4folder
import read_BMP

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir0", help="directory to parse")
    parser.add_argument("dir1", help="directory to parse")
    args = parser.parse_args()

    path0 = args.dir0
    path1 = args.dir1

    list0, _ = generate_4folder.get_index(path0)
    list1, _ = generate_4folder.get_index(path1)

    folder0 = os.path.abspath(path0).split('\\')
    folder0 = folder0[len(folder0) - 1]
    folder1 = os.path.abspath(path1).split('\\')
    folder1 = folder1[len(folder1) - 1]

    count = 0
    if len(list0) == len(list1):
        for i in range(len(list0)):
            log = read_BMP.parse_file_name(list0[i])

            info0, info1, info2, info3, info4 = list0[i].split('\t')
            info5, info6, info7, info8, info9 = list1[i].split('\t')

            if int(info3) < 1000: # enroll
                output0 = "{0}\t{1}\t{2}\t{3}\t{4}".format( info0, info1, info2, info3, folder0 + '\\' + info4)
                print(output0)
                count = 1000
            else:
                output0 = "{0}\t{1}\t{2}\t{3}\t{4}".format( info0, info1, info2, count, folder0 + '\\' + info4)
                count += 1
                output1 = "{0}\t{1}\t{2}\t{3}\t{4}".format( info0, info1, info2, count, folder1 + '\\' + info9)
                count += 1
                if int(log.dict['egp']) >= 80:
                    print(output0 + " : verify_count=0")
                    print(output1 + " : verify_count=1")
                else:
                    print(output0 + " : verify_count=0 : skip_dyn_update")
                    print(output1 + " : verify_count=1 : skip_dyn_update")
                    # print(output1 + " : verify_count=0")

    pass



