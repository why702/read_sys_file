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

def combine_info(gen_data0, gen_data1, index_data0, index_data1):
    with open('gen_compare.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['enroll0', 'verify0', 'match0', 'score0', 'path0', 'enroll1', 'verify1', 'match', 'score1', 'path1', 'compare', 'same', 'path'])

        for info0 in gen_data0:
            verify_id0 = info0['verify']

            # # find path
            # path = find_path(index_data0, verify_id)
            #
            # # # find other info
            # # info1 = find_gen_info(gen_data1, verify_id)
            # # if info1 is None:
            # #     continue

            # info1 = find_gen_info_sn(gen_data0, index_data0, verify_id, gen_data1, index_data1)
            # if info1 is None:
            #     continue

            # find path
            path0 = find_path(index_data0, verify_id0)
            path1 = ''
            info1 = None

            # find sn
            sn = ""
            if path0.rfind('_0x') > 0:
                sn = path0[path0.rfind('\\') + 1:path0.rfind('_0x')]
            else:
                sn = path0[path0.rfind('\\') + 1:path0.rfind('\\') + 26]

            if sn == '20200929_185505_637':
                print()

            # find id1
            verify_id1 = []
            verify_id1_path = []
            for idx in index_data1:
                if idx['path'].find(sn) >= 0:
                    verify_id1.append(idx['id'])
                    verify_id1_path.append(idx['path'])

            # find info1
            for info in gen_data1:
                for i in range(len(verify_id1)):
                    if info['verify'] == verify_id1[i]:
                        info1 = info
                        path1 = verify_id1_path[i]
                        break
            if info1 is None:
                continue

            compare = int(info0['match']) - int(info1['match'])
            if info0['enroll'] == info1['enroll'] and info0['verify'] == info1['verify']:
                same = 1
            else:
                same = 0

            writer.writerow([info0['enroll'], info0['verify'], info0['match'], info0['score'], path0, info1['enroll'], info1['verify'], info1['match'], info1['score'], path1, compare, same])
    pass


def analysis_info(gen_data0, index_data0, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(
        #     ['enroll', 'verify', 'match', 'score', 'path', 'person', 'finger', 'verify', 'quality', 'cond', 'part', 'fr'])
        writer.writerow(
            ['person', 'finger', '50', '75', '90', '100'])
        dicts=[]

        for info0 in gen_data0:
            verify_id = info0['verify']

            # find path
            path = find_path(index_data0, verify_id)

            m = expr.match(path.lower())
            m_p = expr_partial.match(path.lower())
            m_sp = expr_simple_partial.match(path.lower())
            m_e = expr_enroll.match(path.lower())

            person = ""
            finger = -1
            verify = ""
            quality = ""
            cond = ""
            part = ""

            if (m):
                person = m.group(1)
                finger = int(m.group(2))
                verify = m.group(3)
                quality = m.group(4)
                part = m.group(5)
            elif (m_p):
                person = m_p.group(1)
                finger = int(m_p.group(2))
                verify = m_p.group(3)
                cond = m_p.group(4)
                part = m_p.group(5)
            elif (m_sp):
                person = m_sp.group(1)
                finger = int(m_sp.group(2))
                verify = m_sp.group(3)
                part = m_sp.group(4)
            elif (m_e):
                person = m_e.group(1)
                finger = int(m_e.group(2))

            #replace
            person = person.replace("\\","")
            person = person.replace('np',"")
            person = person.replace("ipp","")
            person = person.replace("org","")
            person = person.replace("md1","")
            person = person.replace("md2","")
            person = person.replace("sdk","")
            person = person.replace("full","")
            person = person.replace("normal","")
            person = person.replace("_","")
            person = person.replace("pcopy","")
            person = person.replace("copy","")
            person = person.replace("md3","")

            fr = 1
            if info0['match'] == "1":
                fr = 0

            writer.writerow(
                [info0['enroll'], info0['verify'], info0['match'], info0['score'], path, person, finger, verify, quality, cond, part, fr])

        #     if part != '100':
        #         id = str(person) + "\t" + str(finger) + "\t0" + str(part)
        #     else:
        #         id = str(person) + "\t" + str(finger) + "\t" + str(part)
        #
        #     saved = 0
        #     for d in dicts:
        #         if d['id'] == id:
        #             d['sum'] += fr
        #             d['count'] += 1
        #             saved = 1
        #
        #     if saved == 0:
        #         dicts.append({'id': id, 'person': person, 'finger': finger, 'part': part, 'sum': fr, 'count': 1})
        #
        # dicts.sort(key=lambda k: k['id'])
        #
        # d50_sum = 0
        # d50_count = 0
        # d75_sum = 0
        # d75_count = 0
        # d90_sum = 0
        # d90_count = 0
        # d100_sum = 0
        # d100_count = 0
        # for i in range(0,len(dicts),4):
        #     d50 = dicts[i]['sum'] / dicts[i]['count']
        #     d75 = dicts[i+1]['sum'] / dicts[i+1]['count']
        #     d90 = dicts[i+2]['sum'] / dicts[i+2]['count']
        #     d100 = dicts[i+3]['sum'] / dicts[i+3]['count']
        #     writer.writerow([dicts[i]['person'], dicts[i]['finger'], d50, d75, d90, d100, dicts[i]['sum'], dicts[i]['count'], dicts[i+1]['sum'], dicts[i+1]['count'], dicts[i+2]['sum'], dicts[i+2]['count'], dicts[i+3]['sum'], dicts[i+3]['count']])
        #     d50_sum += dicts[i]['sum']
        #     d50_count += dicts[i]['count']
        #     d75_sum += dicts[i + 1]['sum']
        #     d75_count += dicts[i + 1]['count']
        #     d90_sum += dicts[i + 2]['sum']
        #     d90_count += dicts[i + 2]['count']
        #     d100_sum += dicts[i + 3]['sum']
        #     d100_count += dicts[i + 3]['count']
        #
        # writer.writerow(['person','finger', d50_sum / d50_count, d75_sum / d75_count, d90_sum / d90_count, d100_sum / d100_count])
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
    parser = argparse.ArgumentParser()
    parser.add_argument("gen_path0", help="directory to parse")
    parser.add_argument("gen_path1", help="directory to parse")
    parser.add_argument("index_path0", help="directory to parse")
    parser.add_argument("index_path1", help="directory to parse")
    args = parser.parse_args()

    gen_file0 = args.gen_path0
    gen_file1 = args.gen_path1
    index_file0 = args.index_path0
    index_file1 = args.index_path1

    gen_data0 = parse_genuines(gen_file0)
    gen_data1 = parse_genuines(gen_file1)
    index_data0 = parse_index(index_file0)
    index_data1 = parse_index(index_file1)

    combine_info(gen_data0, gen_data1, index_data0, index_data1)
    pass