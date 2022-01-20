import argparse
import sys
import utils
import numpy as np
import matplotlib.pyplot as plt
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir0", help="directory to parse")
    parser.add_argument("dir1", help="directory to parse")
    args = parser.parse_args()

    dir0 = args.dir0
    dir1 = args.dir1
    RBS = False
    img_list0, _, _, _, file_list0 = utils.read_bins(dir0, 215, 175, RBS)
    img_list1, _, _, _, file_list1 = utils.read_bins(dir1, 215, 175, RBS)
    if len(img_list0) != len(img_list1):
        print(file_list0)
        print(file_list1)
        sys.exit()

    img_max_list = list()
    for i in range(len(img_list0)):
        img0 = img_list0[i].astype(np.int)
        img1 = img_list1[i].astype(np.int)
        sub = np.abs(img0 - img1)
        sub_max = np.max(sub)
        np.savetxt("img0.csv", img0, delimiter=",")
        np.savetxt("img1.csv", img1, delimiter=",")
        np.savetxt("sub.csv", sub, delimiter=",")
        cv2.imshow("0",np.float32(img0) / np.max(img0))
        cv2.imshow("1",np.float32(img1) / np.max(img1))
        cv2.imshow("2",np.float32(sub) / sub_max)
        cv2.waitKey(1)
        img_max_list.append(sub_max)

    n, bins, patches = plt.hist(x=img_max_list, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    # plt.title('My Very Own Histogram')
    plt.text(23, 45, r'$\mu=15, b=3$')
    maxfreq = n.max()
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
    plt.show()
    pass
