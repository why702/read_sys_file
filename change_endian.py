import argparse
import os

import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse")
    parser.add_argument("--little", help="source file's endian", action="store_true")
    args = parser.parse_args()

    for r, d, f in os.walk(args.dir):
        for file in f:
            if file[-3:] != 'bin':
                continue
            path = os.path.join(r, file)
            f = open(path, "r")
            if args.little:  # low_endian
                bytes = np.fromfile(f, dtype=np.uint16)
            else:
                bytes = np.fromfile(f, dtype='>H')
                # byte = np.fromfile(f, dtype='>u2')
            f.close()

            if args.little:  # change to big endian
                path = path[0:-4] + "_b.bin"
            else:
                path = path[0:-4] + "_l.bin"

            f_w = open(path, 'wb')
            for b in bytes:
                byte_int = int(b)
                if args.little:  # change to big endian
                    byte = byte_int.to_bytes(2, byteorder='big')
                else:
                    byte = byte_int.to_bytes(2, byteorder='little')
                f_w.write(byte)
            f_w.close()
