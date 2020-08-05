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
import zipfile

path = '.'

files = []
# r=root, d=directories, f = files
for folder in os.listdir(path):
    if folder.find(".") >= 0:
        continue
    zf = zipfile.ZipFile(folder + ".zip", "w")
    for dirname, subdirs, files in os.walk(folder):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()
    pass
