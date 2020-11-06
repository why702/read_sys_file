import os
from shutil import move
from pathlib import Path
import argparse

DEBUG = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse")
    args = parser.parse_args()

    path = args.dir
    for r, ds, fs in os.walk(path):
        for d in ds:
            if d == 'st':
                src_folder = os.path.join(r, d)
                dst_folder = os.path.join(r, '45d')
                move(src_folder, dst_folder)
                print('{} => {}', src_folder, dst_folder)
                pass