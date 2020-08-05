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
            info['score'] = match[13]
            data.append(info)
    return data


def parse_index(index_file):
    with open(index_file, 'r') as file:
        all_lines = file.readlines()

    data = []
    for line in all_lines:
        if line[0:1] == "#":
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

def combine_info(gen_data0, gen_data1, index_data0, index_data1):
    with open('gen_compare.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['enroll', 'verify', 'match', 'score', 'enroll1', 'verify1', 'match', 'score1', 'path', 'compare', 'same'])

        for info0 in gen_data0:
            verify_id = info0['verify']

            # find path
            path = find_path(index_data0, verify_id)

            # find other info
            info1 = find_gen_info(gen_data1, verify_id)

            if info1 is None:
                continue

            compare = int(info0['match']) - int(info1['match'])
            if info0['enroll'] == info1['enroll'] and info0['verify'] == info1['verify']:
                same = 1
            else:
                same = 0

            writer.writerow([info0['enroll'], info0['verify'], info0['match'], info0['score'], info1['enroll'], info1['verify'], info1['match'], info1['score'], path, compare, same])
    pass


def combine_info_list(gen_data0, gen_data1, gen_data2, gen_data3, gen_data4, gen_data5, gen_data6, index_data0):
    with open('gen_compare.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['enroll0', 'verify0', 'match0', 'score0',
                         'enroll1', 'verify1', 'match1', 'score1',
                         'enroll2', 'verify2', 'match2', 'score2',
                         'enroll3', 'verify3', 'match3', 'score3',
                         'enroll4', 'verify4', 'match4', 'score4',
                         'enroll5', 'verify5', 'match5', 'score5',
                         'enroll6', 'verify6', 'match6', 'score6', 'path'])

        for info0 in gen_data0:
            verify_id = info0['verify']

            # find path
            path = find_path(index_data0, verify_id)

            # find other info
            info1 = find_gen_info(gen_data1, verify_id)
            info2 = find_gen_info(gen_data2, verify_id)
            info3 = find_gen_info(gen_data3, verify_id)
            info4 = find_gen_info(gen_data4, verify_id)
            info5 = find_gen_info(gen_data5, verify_id)
            info6 = find_gen_info(gen_data6, verify_id)

            writer.writerow([
                info0['enroll'], info0['verify'], info0['match'], info0['score'],
                info1['enroll'], info1['verify'], info1['match'], info1['score'],
                info2['enroll'], info2['verify'], info2['match'], info2['score'],
                info3['enroll'], info3['verify'], info3['match'], info3['score'],
                info4['enroll'], info4['verify'], info4['match'], info4['score'],
                info5['enroll'], info5['verify'], info5['match'], info5['score'],
                info6['enroll'], info6['verify'], info6['match'], info6['score'],
                             path])
    pass

if __name__ == '__main__':
    # gen_file0 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\org_su\\genuines.txt"
    # gen_file1 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\6f_su\\genuines.txt"
    # gen_file2 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\L_su\\genuines.txt"
    # gen_file3 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\L1_su\\genuines.txt"
    # gen_file4 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\L2_su\\genuines.txt"
    # gen_file5 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\L10_su\\genuines.txt"
    # gen_file6 = "D:\\PB_bat\\2020_0520_R2213\\dec_egistec_200x200_cardo_S3PG5_100K_R120_DRY\\L20_su\\genuines.txt"
    #
    # gen_data0 = parse_genuines(gen_file0)
    # gen_data1 = parse_genuines(gen_file1)
    # gen_data2 = parse_genuines(gen_file2)
    # gen_data3 = parse_genuines(gen_file3)
    # gen_data4 = parse_genuines(gen_file4)
    # gen_data5 = parse_genuines(gen_file5)
    # gen_data6 = parse_genuines(gen_file6)
    #
    # index_file0 = "D:\\data\\partial\\a51\\20200424_ET713_3PG_A515G_36_NP_v159.901_dry_partial_test_5DB_IPP_org\\sunlight\\S3PG5_cleaned_index.fpdbindex"
    # index_data0 = parse_index(index_file0)
    #
    # combine_info_list(gen_data0, gen_data1, gen_data2, gen_data3, gen_data4, gen_data5, gen_data6, index_data0)

    gen_file0 = "D:/PB_bat/2020_0728_R2311/dec_egistec_200x200_cardo_S3PG6_100K_R120/wash_org/genuines.txt"
    gen_file1 = "D:/PB_bat/2020_0728_R2311/dec_egistec_200x200_cardo_S3PG6_100K_R120/wash_nor/genuines.txt"

    gen_data0 = parse_genuines(gen_file0)
    gen_data1 = parse_genuines(gen_file1)

    index_file0 = "D:/data/partial/a42/wash/20040604_IPP_org/i.fpdbindex"
    index_data0 = parse_index(index_file0)

    combine_info(gen_data0, gen_data1, index_data0, index_data0)
    pass