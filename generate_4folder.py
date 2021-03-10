#!/usr/bin/env python3

#
# This scripts expects a directory layout similar to the following:
#
# (person) / (finger) / (enroll | verify) / (st | 45d) / filename
#
# All of these elements must be present. If person, for instance, is missing,
# parsing will fail.
#
#
# Example:
# 0063/0/enroll/st/filename.png
#
# Would be parsed as:
# 0063          person
# 0             finger
# enroll        part of the enrollment set
# st            straight verification or enrollment
# filename.png
#
#
# Usage:
# Just run it from the root directory and it will output the indexfile on stdout.
#
# cat header.fpdbindex > index.fpdbindex && python3 generate.py >> index.fpdbindex
#
#

__author__ = 'ulfh'

import os
import re
import argparse
import read_BMP


def remap(data, repo):
    if data in repo:
        return repo[data]

    new_index = len(repo.keys()) + 1
    repo[data] = new_index
    return new_index


def get_index(path, ignore = []):

    files = []
    ignore_count = 0
    err_count = 0

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            rp = "." + r.replace(path, '')
            files.append(os.path.join(rp, file))
            # files.append([os.path.join(r, file), int(file[0:2] + file[3:5] + file[6:8] + file[9:11] + file[12:14] + file[15:18])])
            # print(os.path.join(rp, file))

    # # change order
    # files.sort(key = lambda s: s[1])

    expr = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify)\\(st|45d|90d|135d)\\([0-9]+\\)*(\S+).png"
    )
    expr_partial = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify)\\(\S+)\\([0-9]+)\\(\S+).png"
    )
    expr_simple_partial = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify)\\([0-9]+)\\(\S+).png"
    )
    expr_enroll = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify)\\(\S+).png"
    )
    expr_simple = re.compile(
        r"(\S+)\\(enroll|verify|identify)\\(\S+).png"
    )

    all_entries = list()
    persons = dict()

    # print("Loading all entries.")
    for f in files:
        filename = f[2:]

        need_ignore = False
        if len(ignore) > 0:
            for i in range(len(ignore)):
                if f.find(ignore[i]) >= 0:
                    need_ignore = True
                    break

        if need_ignore:
            ignore_count += 1
            continue
        elif filename.find('mask') > 0 or filename.find('msk') > 0 or filename.find('_T.png') > 0 or filename.find('_RD_') > 0 or filename.find('_TRY_0_TRY_') > 0:
            err_count += 1
            continue
        elif filename.find('_0x800') > 0 or filename.find('_0x880') > 0:
            err_count += 1
            continue

        m = expr.match(filename.lower())
        m_p = expr_partial.match(filename.lower())
        m_sp = expr_simple_partial.match(filename.lower())
        m_e = expr_enroll.match(filename.lower())
        m_s = expr_simple.match(filename.lower())

        if (m):
            #print(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
            person = m.group(1)
            finger = int(m.group(2))
            verify = m.group(3)
            quality = m.group(4)
            part = m.group(5)

            index_offset = 0
            if verify == "verify" or verify == "identify": index_offset += 10000
            if quality == "45d": index_offset += 200000
            if quality == "90d": index_offset += 400000
            if quality == "135d": index_offset += 600000

            if part == "100\\": index_offset += 10000
            if part == "95\\": index_offset += 20000
            if part == "90\\": index_offset += 30000
            if part == "85\\": index_offset += 40000
            if part == "80\\": index_offset += 50000
            if part == "75\\": index_offset += 60000
            if part == "70\\": index_offset += 70000
            if part == "65\\": index_offset += 80000
            if part == "60\\": index_offset += 90000
            if part == "55\\": index_offset += 100000
            if part == "50\\": index_offset += 110000
            if part == "45\\": index_offset += 120000
            if part == "40\\": index_offset += 130000
            if part == "35\\": index_offset += 140000
            if part == "30\\": index_offset += 150000
            if part == "25\\": index_offset += 160000
            if part == "20\\": index_offset += 170000
            if part == "15\\": index_offset += 180000
            if part == "10\\": index_offset += 190000

            all_entries.append([person, finger, index_offset, filename])
        elif (m_p):
            person = m_p.group(1)
            finger = int(m_p.group(2))
            verify = m_p.group(3)
            cond = m_p.group(4)
            part = m_p.group(5)

            index_offset = 0
            if verify == "verify": index_offset += 10000

            if cond == "dry" or cond == "wash": index_offset += 200000
            if cond == "normal_on" or cond == "on" or cond == "normal": index_offset += 400000
            if cond == "normal_under" or cond == "under": index_offset += 600000
            if cond == "normal_walking" or cond == "walking" or cond == "walk" or cond == "normal_walk" or cond == "walk_on": index_offset += 800000
            if cond == "wet" or cond == "wet_on": index_offset += 1000000
            if cond == "lotion": index_offset += 1200000
            if cond == "normal_solar" or cond == "solar" or cond == "sunlight": index_offset += 1400000

            if part == "100": index_offset += 10000
            if part == "95": index_offset += 20000
            if part == "90": index_offset += 30000
            if part == "85": index_offset += 40000
            if part == "80": index_offset += 50000
            if part == "75": index_offset += 60000
            if part == "70": index_offset += 70000
            if part == "65": index_offset += 80000
            if part == "60": index_offset += 90000
            if part == "55": index_offset += 100000
            if part == "50": index_offset += 110000
            if part == "45": index_offset += 120000
            if part == "40": index_offset += 130000
            if part == "35": index_offset += 140000
            if part == "30": index_offset += 150000
            if part == "25": index_offset += 160000
            if part == "20": index_offset += 170000
            if part == "15": index_offset += 180000
            if part == "10": index_offset += 190000

            all_entries.append([person, finger, index_offset, filename])
        elif (m_sp):
            person = m_sp.group(1)
            finger = int(m_sp.group(2))
            verify = m_sp.group(3)
            part = m_sp.group(4)

            index_offset = 0
            if verify == "verify": index_offset += 10000

            if part == "100": index_offset += 10000
            if part == "95": index_offset += 20000
            if part == "90": index_offset += 30000
            if part == "85": index_offset += 40000
            if part == "80": index_offset += 50000
            if part == "75": index_offset += 60000
            if part == "70": index_offset += 70000
            if part == "65": index_offset += 80000
            if part == "60": index_offset += 90000
            if part == "55": index_offset += 100000
            if part == "50": index_offset += 110000
            if part == "45": index_offset += 120000
            if part == "40": index_offset += 130000
            if part == "35": index_offset += 140000
            if part == "30": index_offset += 150000
            if part == "25": index_offset += 160000
            if part == "20": index_offset += 170000
            if part == "15": index_offset += 180000
            if part == "10": index_offset += 190000

            all_entries.append([person, finger, index_offset, filename])
        elif (m_e):
            person = m_e.group(1)
            finger = int(m_e.group(2))
            verify = m_e.group(3)
            index_offset = 0
            if verify == "verify" or verify == "identify": index_offset += 10000

            all_entries.append([person, finger, index_offset, filename])
        elif m_s:
            person = m_s.group(1)
            verify = m_s.group(2)
            index_offset = 0
            if verify == "verify" or verify == "identify": index_offset += 10000

            all_entries.append([person, 0, index_offset, filename])


    # # inverse index
    # for i in range(len(all_entries)):
    #     index_file = list(all_entries[i])
    #     if index_file[1] != 5 and index_file[1] != 6:
    #         index_file[1] = index_file[1] + 7
    #     all_entries[i] = tuple(index_file)

    # # check repeatedly enrollment
    # expr_repeat_enroll = re.compile(
    #     r"(\S+)\\(\S+).png"
    # )

    # check enrollment numbers
    tmp_person = ""
    tmp_finger = -1
    # enroll_list = [] * 17
    enroll_count = 0
    for i in range(len(all_entries)):
        if all_entries[i][2] != 0:
            continue
        if tmp_person == "" or tmp_finger == -1:
            tmp_person = all_entries[i][0]
            tmp_finger = all_entries[i][1]

        if tmp_person == all_entries[i][0] and tmp_finger == all_entries[i][1] and all_entries[i][3].find(
                "enroll") >= 0:
            enroll_count += 1

        if i + 1 < len(all_entries) and ((all_entries[i][3].find("enroll") >= 0 and all_entries[i + 1][3].find("enroll") < 0) or (tmp_person != all_entries[i +1][0] and tmp_finger != all_entries[i+1][1])):
            if enroll_count != 17:
                print("#ERROR!\tperson {}\tfinger {}\tenroll_count {} != 17\n".format(tmp_person, tmp_finger, enroll_count))
                tmp_person = ""
                tmp_finger = -1
                enroll_count = 0
                pass
        # if all_entries[i][3].find("_c01_"): enroll_list[0] = all_entries[i][3]
        # elif all_entries[i][3].find("_c02_"): enroll_list[1] = all_entries[i][3]
        # elif all_entries[i][3].find("_c03_"): enroll_list[2] = all_entries[i][3]
        # elif all_entries[i][3].find("_c04_"): enroll_list[3] = all_entries[i][3]
        # elif all_entries[i][3].find("_c05_"): enroll_list[4] = all_entries[i][3]
        # elif all_entries[i][3].find("_c06_"): enroll_list[5] = all_entries[i][3]
        # elif all_entries[i][3].find("_c07_"): enroll_list[6] = all_entries[i][3]
        # elif all_entries[i][3].find("_c08_"): enroll_list[7] = all_entries[i][3]
        # elif all_entries[i][3].find("_c09_"): enroll_list[8] = all_entries[i][3]
        # elif all_entries[i][3].find("_c10_"): enroll_list[9] = all_entries[i][3]
        # elif all_entries[i][3].find("_c11_"): enroll_list[10] = all_entries[i][3]
        # elif all_entries[i][3].find("_c12_"): enroll_list[11] = all_entries[i][3]
        # elif all_entries[i][3].find("_c13_"): enroll_list[12] = all_entries[i][3]
        # elif all_entries[i][3].find("_c14_"): enroll_list[13] = all_entries[i][3]
        # elif all_entries[i][3].find("_c15_"): enroll_list[14] = all_entries[i][3]
        # elif all_entries[i][3].find("_c16_"): enroll_list[15] = all_entries[i][3]
        # elif all_entries[i][3].find("_c17_"): enroll_list[16] = all_entries[i][3]

    # print("Sorting all entries.")
    all_entries.sort()

    # get try_count
    sn_past = ""
    try_count = 0
    new_list = []
    for i in range(len(all_entries)):
        filename = all_entries[i][3]
        sn = filename[filename.rfind('\\') + 1 : filename.rfind('_0x')]

        # log = read_BMP.parse_file_name(filename)
        # if int(log.dict['irl']) > 0 and (filename.find('_0_') >= 0 or filename.find('_2_') >= 0):
        #     continue

        if i == 0:
            if sn.find("_TRY_") >= 0:
                break
            sn_past = sn
            try_count = 0
        elif sn_past != sn:
            sn_past = sn
            try_count = 0
        else:
            try_count += 1

        l = all_entries[i]
        l.append(try_count)
        new_list.append(l)

    # replace
    all_entries = new_list

    # print("Mapping and writing to stdout.")
    tri_key = all_entries[1][0:3]
    sample_counter = 0
    output_list = []
    output_update_list = []

    for person, finger, offset, filename, try_count in all_entries:
        new_tri_key = (person, finger, offset)

        # Check if a new finger or group. If so, reset sample counter.
        if tri_key != new_tri_key: sample_counter = 0
        tri_key = new_tri_key

        # # work around switch filename
        # if filename.find("_1_") >= 0 or filename.find("_3_") >= 0:
        #     filename = "20210122_Solar_10DB_ph3\\np\\" + filename
        # else:
        #     filename = "20210122_Solar_10DB_IPP\\np\\" + filename

        log = read_BMP.parse_file_name(filename)
        if log.dict['egp'] == 'None' or int(log.dict['egp']) >= 80:
            output_update = "{0}\t{1}\t{2}\t{3}\t{4} : verify_count={5}".format(
                remap(person, persons), finger, 0, offset + sample_counter,
                filename, try_count)
        # elif int(log.dict['irl']) > 0 and (filename.find('_0_') >= 0 or filename.find('_2_') >= 0):
        #     pass  # work around
        else:
            # output_update = "{0}\t{1}\t{2}\t{3}\t{4} : skip_dyn_update".format(
            #     remap(person, persons), finger, 0, offset + sample_counter,
            #     filename)
            output_update = "{0}\t{1}\t{2}\t{3}\t{4} : verify_count={5}".format(
                remap(person, persons), finger, 0, offset + sample_counter,
                filename, try_count)

        output = "{0}\t{1}\t{2}\t{3}\t{4}".format(remap(person,
                                                        persons), finger, 0,
                                                  offset + sample_counter,
                                                  filename)
        sample_counter += 1
        output_list.append(output)
        output_update_list.append(output_update)

    return output_list, output_update_list, ignore_count, err_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse", default=".")
    args = parser.parse_args()

    path = args.dir
    ignore = ["Img16b"]
    _, output_update_list, ignore_count, err_count = get_index(path, ignore)

    print("# This file contains information about a fingerprint database.")
    print(
        "# It is intended to help when iterating over all images of a database."
    )
    print("#")
    print("#")
    print("# Database attributes:")
    print("## fingerIdsRegistered=0,1,2,3,4,5,6,7,8,9,10,11\n")
    print("## fingerTypesRegistered=0")
    print("## idFirstVerificationSample=1000")
    print("## idPersonBottom=1")
    print("## idPersonTop=66")
    print("## idSampleBottom=0")
    print("## idSampleTop=4000")
    print("## itemType=png")
    print("## locked=False")
    print("## name=A42")
    print("## resolution=705")
    print("# End of attributes")
    print("# This file was generated by: MixedFingers")
    print(
        "# The Python command that generated the fpdbindex can be found in the input file"
    )
    print("#")
    print("# Columns (tab separated):")
    print("# Person ID (0 if unknown)")
    print("# 	Finger ID (= Finger Type if unspecified or 0 if unknown/unused)")
    print("# 		Finger Type (according to ISO/IES 19794-2:2005 table 2)")
    print(
        "# 			Sample ID (sometimes referred to as \"Attempt\" or \"Transaction\")"
    )
    print("# 				Image file relative path")
    print("#")
    for i in range(len(output_update_list)):

        if output_update_list[i].find("_TRY_") >= 0:
            try_num = int(output_update_list[i][output_update_list[i].find("_TRY_") +
                                5:output_update_list[i].find("_TRY_") + 6])
            if try_num >= 0:
                print(output_update_list[i] + " : verify_count={}".format(try_num))
        else:
            print(output_update_list[i])
        pass

    print("#len = {}".format(len(output_update_list)))
    print("#ignore_count = {}".format(ignore_count))
    print("#err_count = {}".format(err_count))
