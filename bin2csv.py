import argparse
import csv
import os

from utils import parse_files

DEBUG = True


def list_files(dir_path, csv_file):
    fieldnames = None

    with open('result.csv', 'w', newline='') as csvfile:
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                print(os.path.join(root, name))

                ext = os.path.splitext(name)[1]
                # if len(name) < 80:
                #     continue
                if os.path.splitext(name)[1] != '.bmp':
                    continue

                # elif name.find('8bitImage') == -1:
                #     continue

                log = parse_files(root, name)

                if fieldnames is None:
                    fieldnames = log.dict.keys()
                    writer = csv.writer(csvfile)
                    writer.writerow(fieldnames)

                d = log.dict['pLearn']
                if log.dict['pLearn'] == 'None':
                    egp = int(log.dict['egp'])
                    rl = int(log.dict['rl'])
                    irl = int(log.dict['irl'])
                    sl = int(log.dict['sl'])
                    rls = int(log.dict['rls'])
                    if egp < 80 or (rl > 2 and rls > 50) or (irl > 0 and rls > 70) or (rl > 2 and sl > 90) or (
                            irl > 0 and sl > 90) or (rl <= 2 and sl == 200):
                        pLearn = 0
                    else:
                        pLearn = 1
                    log.dict['pLearn'] = pLearn
                    pass

                writer.writerow(log.dict.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse")
    args = parser.parse_args()

    path = args.dir
    csv_path = ""
    list_files(path, csv_path)
