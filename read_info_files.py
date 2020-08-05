import os
import numpy as np
import matplotlib.pylab as plt
from itertools import zip_longest
import cv2
import re
import csv
import argparse

def list_files(dir_path, csv_file):
    fieldnames = None

    with open('info.txt', 'w') as fp:
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                if name.find('info.txt') == -1:
                    continue

                file_path = os.path.join(root, name)
                print(file_path)

                f = open(file_path)
                fp.writelines(file_path + "\n")
                for line in f:
                    if (line.find('FRR') != -1 or line.find('FAR') != -1) and line.find('finger detect') == -1 and line.find('latent detect') == -1 and line.find('PAD') == -1:
                        fp.writelines(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse")
    args = parser.parse_args()

    path = args.dir
    csv_path = ""
    list_files(path, csv_path)
