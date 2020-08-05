import os
import numpy as np
import matplotlib.pylab as plt
from itertools import zip_longest
import cv2
import re
import csv

DEBUG = True


class LOG():
    def __init__(self):
        self.keywords = [
            "et", "hc", "mh", "mr", "spp", "sps", "egp", "fk", "B", "Ba", "T",
            "eq", "learn", "M", "Mc", "MBc", "ed", "mlq", "sd", "md", "er", "_p"
        ]
        self.dict = {}

    def update_dict(self, key, value):
        if key not in self.keywords:
            return False
        self.dict[key] = value
        return True

    def add_dict(self, key, value):
        self.dict[key] = value
        return True

    def add_dicts(self, keys, values):
        assert len(keys) == len(values)
        for i in range(len(keys)):
            self.dict[keys[i]] = values[i]
        return True


def regax_keyword(keyword, text):
    # 01-01-12-02-06-530_c01_p006_0x00000000_0_8bitImage_-999(0)_[0_0_0]_et=23.3_hc=6_mh=-1_mr=100_spp=100_sps=1_egp=93_fk=-3516_B=2_Ba=1_T=33_eq=-999_learn=00_M=384_Mc=915_MBc=716_ed=0_mlq=115_sd=81_md=0_er=1_R.bin
    match = re.search(r"{}=([0-9-]*)".format(keyword), text)
    if match:
        return match.group(0).replace("{}=".format(keyword), '')
    else:
        return 'None'


def regax_serial_number(text):
    match = re.search(r"([a-z|A-Z|0-9-_]*)_0x", text)
    if match:
        return match.group(0).replace('_0x', '')
    else:
        return 'None'


def regax_3pairs(text):
    match = re.search(r"([[0-9-]*_[0-9-]*_[0-9-]*])", text)
    if match:
        value = match.group(0).replace('[', '').replace(']', '')
        return value.split('_')
    else:
        return ['None'] * 3


def regax_score(text):
    match = re.search(r"_([0-9-]*)/(([0-9-]*)/)_", text)
    if match:
        value = match.group(0).replace('_', '').replace(')', '')
        return value.split('(')
    else:
        return ['None'] * 2


def regax_RT(text):
    match = re.search(r"[a-z|A-Z].bin", text)
    if match:
        return match.group(0).replace('.bin', '')
    else:
        return 'None'


def regax_pass(text):
    match = re.search(r"pass_[0-9]|fail_[0-9]", text)
    if match:
        return match.group(0).split('_')
    else:
        return ['enroll', '0']


def parse_file_name(name):
    log = LOG()

    value = regax_serial_number(name)
    if log.add_dict("serial_number", value) == False:
        print('log.add_dict("serial_number", value) == False')
        return

    values = regax_pass(name)
    if log.add_dicts(['pass_mode', '?'], values) == False:
        print('log.add_dict([pass_mode, ?], value) == False')
        return

    values = regax_score(name)
    if log.add_dicts(['score', 'Q/N_mode'], values) == False:
        print('log.add_dicts([score, Q/N_mode], values) == False')
        return

    values = regax_3pairs(name)
    if log.add_dicts(['finger1', 'finger2', 'finger3'], values) == False:
        print('log.add_dicts([finger1, finger2, finger], values) == False')
        return

    for key in log.keywords:
        value = regax_keyword(key, name)
        if log.update_dict(key, value) == False:
            print('log.update_dict(key, value) == False')
            return

    # value = regax_RT(name)
    # if log.add_dict('RT_mode', value) == False:
    #     print('log.add_dict([RT mode], value) == False')
    #     return

    return log


def list_files(txt_path, csv_file):
    txtfile = open(txt_path, 'r', newline='').readlines()

    fieldnames = None
    with open('result.csv', 'w', newline='') as csvfile:
        for txt in txtfile:
            sp = txt.replace('/r/n', '').split('//')
            txt = sp[len(sp) - 1]

            log = parse_file_name(txt)

            if fieldnames is None:
                fieldnames = log.dict.keys()
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)

            writer.writerow(log.dict.values())


if __name__ == '__main__':

    path = 'E:/svn/texture-decomposition/file.txt'
    csv_path = ""
    list_files(path, csv_path)
