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


def get_index(path):

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            rp = "." + r.replace(path, '')
            files.append(os.path.join(rp, file))
            # if file.find('.png') <= 0:
            #     continue
            # files.append([os.path.join(r, file), int(file[0:2] + file[3:5] + file[6:8] + file[9:11] + file[12:14] + file[15:18])])

    # # change order
    # files.sort(key = lambda s: s[1])

    expr = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify)\\(st|45d|90d|135d)\\([0-9]+\\)*(\S+).png"
    )

    all_entries = list()
    persons = dict()

    # print("Loading all entries.")
    for f in files:
        filename = f[2:]

        if filename.find('mask') > 0 or filename.find('_0x800') > 0:
            continue

        m = expr.match(filename)
        if (m):
            #print(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
            person = m.group(1)
            finger = int(m.group(2))
            verify = m.group(3)
            quality = m.group(4)
            part = m.group(5)
            filename = m.group(0)

            index_offset = 0
            if verify == "verify": index_offset += 1000
            if quality == "45d": index_offset += 20000
            if quality == "90d": index_offset += 40000
            if quality == "135d": index_offset += 60000

            if part == "100\\": index_offset += 1000
            if part == "95\\": index_offset += 2000
            if part == "90\\": index_offset += 3000
            if part == "85\\": index_offset += 4000
            if part == "80\\": index_offset += 5000
            if part == "75\\": index_offset += 6000
            if part == "70\\": index_offset += 7000
            if part == "65\\": index_offset += 8000
            if part == "60\\": index_offset += 9000
            if part == "55\\": index_offset += 10000
            if part == "50\\": index_offset += 11000
            if part == "45\\": index_offset += 12000
            if part == "40\\": index_offset += 13000
            if part == "35\\": index_offset += 14000
            if part == "30\\": index_offset += 15000
            if part == "25\\": index_offset += 16000
            if part == "20\\": index_offset += 17000
            if part == "15\\": index_offset += 18000
            if part == "10\\": index_offset += 19000

            all_entries.append((person, finger, index_offset, filename))

    # print("Sorting all entries.")
    all_entries.sort()

    # print("Mapping and writing to stdout.")
    tri_key = all_entries[1][0:3]
    sample_counter = 0
    output_list = []
    output_update_list = []

    for person, finger, offset, filename in all_entries:
        new_tri_key = (person, finger, offset)

        # Check if a new finger or group. If so, reset sample counter.
        if tri_key != new_tri_key: sample_counter = 0
        tri_key = new_tri_key

        log = read_BMP.parse_file_name(filename)
        if log.dict['egp'] == 'None':
            output_update = "{0}\t{1}\t{2}\t{3}\t{4}".format(
                remap(person, persons), finger, 0, offset + sample_counter,
                filename)
        elif int(log.dict['egp']) >= 80:
            output_update = "{0}\t{1}\t{2}\t{3}\t{4}".format(
                remap(person, persons), finger, 0, offset + sample_counter,
                filename)
        else:
            output_update = "{0}\t{1}\t{2}\t{3}\t{4} : skip_dyn_update".format(
                remap(person, persons), finger, 0, offset + sample_counter,
                filename)

        output = "{0}\t{1}\t{2}\t{3}\t{4}".format(remap(person,
                                                        persons), finger, 0,
                                                  offset + sample_counter,
                                                  filename)
        sample_counter += 1
        output_list.append(output)
        output_update_list.append(output_update)

    return output_list, output_update_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse", default=".")
    args = parser.parse_args()

    path = args.dir
    _, output_update_list = get_index(path)

    print("# This file contains information about a fingerprint database.")
    print(
        "# It is intended to help when iterating over all images of a database."
    )
    print("#")
    print("#")
    print("# Database attributes:")
    print("## fingerIdsRegistered=0,5,6")
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
        "# The Python command that generated the fpdbindex can be found in the input file ="
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
        print(output_update_list[i])
