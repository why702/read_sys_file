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

path = '.'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if r.find("verify\\50") > 0:
            src = os.path.join(r, file)
            r_dst = r.replace("verify\\50", "verify\\st")
            dst = os.path.join(r_dst, file)
            if not os.path.exists(r_dst):
                os.mkdir(r_dst)
            os.rename(src, dst)
