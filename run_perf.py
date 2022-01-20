import os
import argparse
from shutil import copyfile, rmtree
from utils import run_perf_single_pair

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("img_path0", help="directory to parse")
    parser.add_argument("img_path1", help="directory to parse")
    parser.add_argument("dpi", type=int, help="DPI", default=630)
    args = parser.parse_args()

    test_folder = os.path.join(os.path.dirname(__file__), "perf")
    if os.path.exists(test_folder):
        rmtree(test_folder, ignore_errors=True)
        os.mkdir(test_folder)

    img0 = os.path.basename(args.img_path0)
    img1 = os.path.basename(args.img_path1)
    copyfile(args.img_path0, os.path.join(test_folder, img0))
    copyfile(args.img_path1, os.path.join(test_folder, img1))
    # run_perf_single_pair(test_folder, "read_sys_file/perf/" + img0, "read_sys_file/perf/" + img1, args.dpi)
    run_perf_single_pair(test_folder, img0, img1, args.dpi)
