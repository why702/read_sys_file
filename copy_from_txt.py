import os
import numpy as np
import matplotlib.pylab as plt
from itertools import zip_longest
import cv2
import re
import csv
from shutil import copyfile, SameFileError

DEBUG = True

def copy_files(txt_path, org_path, copy_path):
    txtfile = open(txt_path, 'r', newline='').readlines()

    for root, dirs, files in os.walk(org_path, topdown=False):
        for name in files:
            # print(os.path.join(root, name))

            if os.path.splitext(name)[1] != '.bin':
                continue

            for match_name in txtfile:
                if match_name == '\r\n':
                    continue
                match_name = match_name.replace('\r\n', '')
                if name.find(match_name) != -1:
                    dst = copy_path + "/" + os.path.basename(name)
                    try:
                        copyfile(os.path.join(root, name), dst)
                    except SameFileError:
                        # code when Exception occur
                        pass
                    else:
                        # code if the exception does not occur
                        pass
                    finally:
                        # code which is executed always
                        pass


if __name__ == '__main__':

    txt_path =  "E:/data/partial/190820/190820_ET713_3PC_MH2_hank_139966f7_Partial/19080502/1/1.txt"
    org_path =  "E:/data/partial/190820/190820_ET713_3PC_MH2_hank_139966f7_Partial/19080502/"
    copy_path = "E:/data/partial/190820/190820_ET713_3PC_MH2_hank_139966f7_Partial/19080502/1/"
    copy_files(txt_path, org_path, copy_path)










