import argparse
import os

def listdir_(path):
    for item in os.listdir(path):
        path_ = os.path.join(path, item)
        if item.find('raw') > 0:
            print(path_)
            break
        else:
            listdir_(path_)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse", default=".")
    args = parser.parse_args()
    path = args.dir

    listdir_(path)

