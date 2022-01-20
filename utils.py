import csv
import math
import os
import re
import shutil
import struct
import subprocess
import threading
from datetime import datetime

import cv2
import numpy as np
from skimage.feature import local_binary_pattern


def read_bin(bin_path, tuple_size=(200, 200), low_endian=True):
    f = open(bin_path, "r")
    if low_endian:
        byte = np.fromfile(f, dtype=np.uint16)
    else:
        byte = np.fromfile(f, dtype='>u2')
    # if low_endian == False:
    #     for i in range(len(byte)):
    #         b = struct.pack('>H', byte[i])
    #         byte[i] = struct.unpack('H', b)[0]
    return byte.reshape(tuple_size)


def read_8bit_bin(bin_path, tuple_size=(200, 200)):
    if os.path.splitext(bin_path)[1] == '.png':
        img = cv2.imread(bin_path, 0)
        return img
    else:
        f = open(bin_path, "r")
        byte = np.fromfile(f, dtype=np.uint8)

        # if low_endian == False:
        #     for i in range(len(byte)):
        #         b = struct.pack('>H', byte[i])
        #         byte[i] = struct.unpack('H', b)[0]
        return byte.reshape(tuple_size)


def read_bin_flatten(bin_path, low_endian=True):
    f = open(bin_path, "r")
    byte = np.fromfile(f, dtype=np.uint16)

    if low_endian == False:
        for i in range(len(byte)):
            b = struct.pack('>H', byte[i])
            byte[i] = struct.unpack('H', b)[0]
    return byte


def convert_lbp(byte):
    radius = 1
    n_points = 15 * radius
    threshold = 300
    byte[byte < threshold] = 0
    lbp = local_binary_pattern(byte, n_points, radius)
    return lbp


def subtract(nd1, nd2):
    diff = np.subtract(nd1.astype(np.float32), nd2.astype(np.float32))
    min = np.min(diff)
    diff -= min
    return diff


def normalize_ndarray(nd):
    return (nd - np.min(nd)) / (np.max(nd) - np.min(nd))


def normalize_ndarray_set(nd, min, max):
    return (nd - min) / (max - min)


def get_circle_boundary(byte):
    norm1 = normalize_ndarray(byte) * 255
    norm1 = norm1.astype(np.uint8)
    _, norm1_c = cv2.threshold(norm1, 10, 255, cv2.THRESH_BINARY)
    _, contours, hierarchy = cv2.findContours(norm1_c, cv2.RETR_TREE,
                                              cv2.CHAIN_APPROX_SIMPLE)

    area_list = []
    for cnt in contours:
        area_list.append(cv2.contourArea(cnt))

    area_list = np.asarray(area_list)
    max_index = np.argmax(area_list)
    cnt = contours[max_index]
    (c_x, c_y), radius = cv2.minEnclosingCircle(cnt)
    return c_x, c_y, radius


def LPF_FWHM(byte, LPF):
    L = 0.5

    # # get center
    # c_x, c_y, radius = get_circle_boundary(byte)
    # c_x = 120
    # shift_y = (byte.shape[0] / 2 - c_x) * 2 * L / byte.shape[0]
    # shift_x = (byte.shape[1] / 2 - c_y) * 2 * L / byte.shape[1]
    shift_x = shift_y = 0

    x = np.linspace(-L + shift_x, L + shift_x, byte.shape[0])
    y = np.linspace(-L + shift_y, L + shift_y, byte.shape[1])
    [X1, Y1] = (np.meshgrid(x, y))
    X = X1.T
    Y = Y1.T

    def cart2pol(x, y):
        theta = np.arctan2(y, x)
        rho = np.hypot(x, y)
        return (theta, rho)

    [THETA, RHO] = cart2pol(X, Y)

    # RHO_ = normalize_ndarray(RHO) * 255
    # cv2.imshow('', RHO_.astype(np.uint8))
    # cv2.waitKey()

    # Apply localization kernel to the original image to reduce noise
    Image_orig_f = ((np.fft.fft2(byte)))
    expo = np.fft.fftshift(
        np.exp(-np.power((np.divide(RHO, math.sqrt((LPF ** 2) /
                                                   np.log(2)))), 2)))
    # expo = normalize_ndarray(expo) * 255
    # cv2.imshow('', expo.astype(np.uint8))
    # cv2.waitKey()

    Image_orig_filtered = np.real(
        np.fft.ifft2((np.multiply(Image_orig_f, expo))))
    return Image_orig_filtered


def find_bk_bins(bin_dir):
    pair_EtBk = []
    for root, dirs, files in os.walk(bin_dir, topdown=False):
        for name in files:
            pos = name.lower().find('_bkg.bin')
            if pos >= 0:
                et = int(name[0:pos])
                pair_EtBk.append((et, os.path.join(root, name)))
    return pair_EtBk


def read_bins(bin_dir, width, height, RBS=False):
    img_list = []
    bk_list = []
    ipp_list = []
    bds_list = []
    file_list = []
    img = None
    bk = None
    ipp = None
    bds = None
    BK_et = 0
    need_bk = True
    low_endian = not RBS
    img_size = (height, width)

    for root, dirs, files in os.walk(bin_dir, topdown=False):
        for name in files:
            if os.path.splitext(name)[1] == '.bin':
                if RBS:
                    if root.find("image_raw") != -1:
                        img = read_bin(os.path.join(root, name), img_size, low_endian)

                        ipp_path = os.path.join(root, name).replace("image_raw", "image_bin")
                        ipp = read_8bit_bin(ipp_path, img_size)

                        bds_path = os.path.join(root, name).replace("image_raw", "image_bkg")
                        bds = read_bin(bds_path, img_size, low_endian)

                        # if img is None or bk is None or ipp is None or bds is None:
                        #     continue
                        if img is None or ipp is None or bds is None:
                            continue

                        img_list.append(img)
                        bk_list.append(bk)
                        ipp_list.append(ipp)
                        bds_list.append(bds)
                        file_list.append(os.path.join(root, name))
                    pass
                else:

                    if name.find("_Img16b_") != -1:

                        # # find et
                        # et = name[name.find("_et=") + 4: name.find("_hc=")]
                        #
                        # # # find bk
                        # # mi = name[name.find("mica=") + 5: name.find("mica=") + 7]
                        # #
                        # # if root.find("enroll") != -1 and mi == "00" and need_bk:
                        # #     bk_name = name.replace("Img16b", "Img16bBkg")
                        # #     bk = read_bin(os.path.join(root, bk_name), img_size)
                        # #     need_bk = False
                        # #     BK_et = et
                        # # elif need_bk == False and root.find("enroll") == -1:
                        # #     need_bk = True
                        # #
                        # # if BK_et != et or et == 0:
                        # #     continue

                        img = read_bin(os.path.join(root, name), img_size, low_endian)

                        ipp_name = name.replace("Img16b", "Img8b")
                        ipp = read_8bit_bin(os.path.join(root, ipp_name), img_size)

                        bds_name = name.replace("Img16b", "Img16bBkg")
                        bds = read_bin(os.path.join(root, bds_name), img_size, low_endian)

                        # if img is None or bk is None or ipp is None or bds is None:
                        #     continue
                        if img is None or ipp is None or bds is None:
                            continue

                        img_list.append(img)
                        bk_list.append(bk)
                        ipp_list.append(ipp)
                        bds_list.append(bds)
                        file_list.append(os.path.join(root, name))

    print("img_list size is {}".format(len(img_list)))
    return img_list, bk_list, ipp_list, bds_list, file_list


def read_bins_toCSV(bin_dir, out_path, RBS=False, GOOD=False):
    BK_et = 0
    need_bk = True
    count = 0
    img = None
    bk = None
    ipp = None
    bds = None
    pair_EtBk = find_bk_bins(bin_dir)

    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for root, dirs, files in os.walk(bin_dir, topdown=False):
            for name in files:
                # print(os.path.join(root, name))

                if os.path.splitext(name)[1] == '.bin':

                    if RBS:
                        if root.find("image_raw") != -1:
                            img = os.path.join(root, name)

                            ipp_root = root.replace("image_raw", "image_bin")
                            ipp_name = name.replace("bin", "png")
                            ipp = os.path.join(ipp_root, ipp_name)

                            bds_root = root.replace("image_raw", "image_bkg")
                            bds = os.path.join(bds_root, name)

                            bk = None
                            pos = name.lower().find('_et=')
                            if pair_EtBk is not [] and pos >= 0:
                                sEt = name.lower()[pos + 4:]
                                pos_end = sEt.find('_')
                                iEt = int(float(sEt[0:pos_end]) * 1000)
                                for et_, bk_ in pair_EtBk:
                                    if et_ == iEt:
                                        bk = bk_
                            if bk is None:
                                bk = img

                            if os.path.exists(img) is False or os.path.exists(
                                    ipp) is False or os.path.exists(bds) is False:
                                continue

                            writer.writerow([img, bk, ipp, bds])
                            count += 1
                    else:

                        if name.find("_Img16b_") != -1:

                            # find et
                            et = name[name.find("_et=") + 4: name.find("_hc=")]

                            # find mica
                            mi = name[name.find("mica=") + 5: name.find("mica=") + 7]

                            # find egp rl
                            egp = 100
                            rl = 0
                            if name.find("_egp=") >= 0 and name.find("_rl=") >= 0 and name.find("_CxCy=") >= 0:
                                egp = int(name[name.find("_egp=") + 5: name.find("_rl=")])
                                rl = int(name[name.find("_rl=") + 4: name.find("_CxCy")])

                            if GOOD and egp < 80 or rl > 0:
                                continue

                            if root.find("enroll") != -1 and mi == "00" and need_bk:
                                bk_name = name.replace("Img16b", "Img16bBkg")
                                bk = os.path.join(root, bk_name)
                                need_bk = False
                                BK_et = et
                            elif need_bk == False and root.find("enroll") == -1:
                                need_bk = True

                            if BK_et != et or et == 0:
                                continue

                            img = os.path.join(root, name)

                            ipp_name = name.replace("Img16b", "Img8b")
                            ipp = os.path.join(root, ipp_name)

                            bds_name = name.replace("Img16b", "Img16bBkg")
                            bds = os.path.join(root, bds_name)

                            if os.path.exists(img) is False or os.path.exists(bk) is False or os.path.exists(
                                    ipp) is False or os.path.exists(bds) is False:
                                continue

                            writer.writerow([img, bk, ipp, bds])
                            count += 1

    print("img_list size is {}".format(count))
    return


def parse_genuines(gen_file):
    with open(gen_file, 'r') as file:
        all_lines = file.readlines()

    data = []
    for line in all_lines:
        if line[0:1] == "#":
            continue
        match = re.findall(r"\s*([0-9]+)\s*", line)
        if len(match) >= 23:
            info = dict()
            info['enroll'] = match[0] + match[1] + match[2]
            info['verify'] = match[3] + match[4] + match[5]
            info['match'] = match[6]
            info['score'] = match[11]
            data.append(info)
    return data


# egistec_200x200_cardo_2PX
# egistec_200x200_cardo_2PA
# egistec_200x200_cardo_2PA_NEW
# egistec_200x200_cardo_2PB
# egistec_200x200_cardo_2PB_CH1M30
# egistec_200x200_cardo_3PX
# egistec_200x200_cardo_3PC
# egistec_200x200_cardo_3PD
# egistec_200x200_cardo_3PDx
# egistec_193x193_cardo_3PA
# egistec_193x193_cardo_3PF
# egistec_120x33_cardo_525
# egistec_120x27_cardo_5XX
# egistec_120x25_cardo_528
# egistec_134x188_cardo_702_NEW
# egistec_134x188_cardo_702_INV
# egistec_134x188_cardo_702
# egistec_200x200_cardo_CH1ABY
# egistec_200x200_cardo_CH1AJA
# egistec_200x200_cardo_CH1AJB
# egistec_200x200_cardo_CH1AJA_demorie
# egistec_200x200_cardo_CH1AJB_demorie
# egistec_200x200_cardo_CH1LA
# egistec_200x200_cardo_CH1LA_NEW
# egistec_200x200_cardo_ET760
# egistec_142x142_cardo_ET760_CROP
# egistec_150x104_cardo_ET760_CROP2
# egistec_134x188_cardo_CH1M30
# egistec_134x188_cardo_CH1M30_INV
# egistec_132x120_cardo_CH1M30
# egistec_200x200_cardo_CH1E_SB
# egistec_200x200_cardo_CH1E_SV
# egistec_200x200_cardo_CH1E_H
# egistec_200x200_cardo_CH1B_H
# egistec_200x200_cardo_CH1J_SB
# egistec_200x200_cardo_CL1MH2
# egistec_134x188_cardo_CL1MH2
# egistec_134x188_cardo_CL1MH2_INV
# egistec_118x172_cardo_CL1WING
# egistec_134x188_cardo_CL1WING
# egistec_134x188_cardo_CL1WING_Latency
# egistec_200x200_cardo_CL1MH2_CLT3
# egistec_134x188_cardo_CL1MH2_C230
# egistec_200x200_cardo_CL1MH2V
# egistec_193x193_cardo_CL1TIME
# egistec_193x193_cardo_CL1CAY
# egistec_193x193_cardo_CL1CAY_pad
# egistec_200x200_cardo_CO1D151
# egistec_200x200_cardo_CO1A118
# egistec_200x200_cardo_3PG_CO1A118
# egistec_200x200_cardo_3PG_CH1JSC_H
# egistec_200x200_cardo_CS3ZE2
# egistec_200x200_cardo_CV1CPD1960
# egistec_200x200_cardo_CV1CTD2041
# egistec_200x200_cardo_3PG_CV1CPD1960
# egistec_150x150_cardo_ET901
# egistec_150x150_cardo_ET901_CL1V60
# egistec_175x175_cardo_EF9002
# egistec_175x175_cardo_EF9002_raw
# egistec_200x200_cardo_S3PG1
# egistec_200x200_cardo_S3PG2
# egistec_200x200_cardo_S3PG3
# egistec_200x200_cardo_S3PG3_Latency
# egistec_200x200_cardo_S3PG4
# egistec_200x200_cardo_S3PG5
# egistec_200x200_cardo_S3PG6
# egistec_200x200_cardo_S3PG6_new
# egistec_200x200_evo_S3PG6
# egistec_200x200_cardo_S3PG7
# egistec_200x200_cardo_S3PG7_new
# egistec_200x200_evo_S3PG7
# egistec_200x200_cardo_S3PG8
# egistec_200x200_cardo_S3PG8_new
# egistec_200x200_cardo_S2PB1
# egistec_200x200_cardo_S2PA4
# egistec_193x193_cardo_S3PF5
# egistec_193x193_cardo_S3PF2
# egistec_193x193_cardo_S3PA2
# egistec_193x193_cardo_S3PA2_Latency
# egistec_134x188_cardo_SXC210
# egistec_193x193_cardo_ET715_3PG
# egistec_215x175_cardo_EL721_3PI_CV1CTD2052
# egistec_215x175_evo_EL721_3PI_CV1CTD2052
# egistec_200x200_cardo_ET760_2
# egistec_200x200_cardo_ET760_2_IPP61e
# egistec_200x200_cardo_ET760_3
# egistec_215x175_cardo_EL721_3PI_S3PI1
# egistec_215x175_evo_EL721_3PI_S3PI1
# egistec_200x200_cardo_CH2NTH_B
# egistec_200x200_cardo_CH2NTH_V
# egistec_200x200_cardo_CH2NTH
# gen_0x0_eval_cardo
# gen_130x130_neo
# gen_130x130_neo_speed
# gen_192x192_spectral
# gen_192x192_minutiae
# gen_192x192_minutiae_speed_mem
# gen_80x64_cardo_capacitive
# gen_6x6_cardo_embedded_363dpi
# gen_6x6_cardo_embedded_508dpi
# gen_10x10_hybrid_embedded_254dpi
# gen_10x10_cardo_embedded_363dpi
# gen_8x8_hybrid_embedded_254dpi
# gen_8x8_hybrid_plus_embedded_254dpi
# gen_8x8_cardo_embedded_363dpi
# gen_fullsize_cardo_embedded_254dpi

def execute_perf(fpdbindex_path, org=False):
    key = "tst"
    now = datetime.now()
    dt_string = now.strftime("%Y%d%m_%H%M%S")
    if org:
        key = "org"
    else:
        key = key + "_" + dt_string

    output_perf = ".\\perf\\{}".format(key)
    if os.path.exists(output_perf) and org is False:
        shutil.rmtree(output_perf, ignore_errors=True)

    PERF_VERSION = 4012
    API = "mobile"
    ALGO = "egistec_215x175_evo_EL721_3PI_generic"
    # ALGO = "egistec_200x200_cardo_S3PG5"
    FAR = "1K"
    LATCENY = 0
    ENROLL_UPPER_BOUNDARY = 17
    ENROLL_LOWER_BOUNDARY = 1
    MAXTEMPLATESIZE = 1024000
    IMPROVEDRY = 0
    RADIUS = 120
    THREADS = 1
    PBexe_path = "N:\\PB_evtool\\BioMatchFramework_Egistec-R{}\\BMF\\bin\\x86_64-w64-mingw32\\PerfEval.exe".format(
        PERF_VERSION)

    perf_cmd = "{} -rs={} -n=perf -tp=image -api={} -skip -algo={} -ver_type=dec -far=1:{} -ms=allx -latency_adjustment={} -enr=1000of{}+g -enr_min={} -div=1000 -Cmaxtsize={} -ver_update=gen -scorefiles=1 -improve_dry={} -static_pattern_detect -performance_report -Agen.aperture.radius={} -threads={} \"{}\" > perf/perf_info.txt".format(
        PBexe_path, key, API, ALGO, FAR, LATCENY, ENROLL_UPPER_BOUNDARY, ENROLL_LOWER_BOUNDARY, MAXTEMPLATESIZE,
        IMPROVEDRY, RADIUS, THREADS, fpdbindex_path)
    # perf_cmd = "{} -skip -rs={} -n=test -improve_dry=94 -latency_adjustment=0 -algo=egistec_200x200_cardo_CH1AJA -tp=image -api=mobile -ver_type=dec -far=1:100K -ms=fvc2x:ogi -enr=1000of15+g -div=1000 -Cmaxtsize=1024000 -ver_update=gen -scorefiles=1 -static_pattern_detect -threads=4 -Agen.aperture.radius=120 -Agen.aperture.x=107 -Agen.aperture.y=87  \"{}\\i.fpdbindex\" > perf_info.txt".format(
    #     PBexe_path, key, test_folder)

    print('run\n{}'.format(perf_cmd))
    os.system(perf_cmd)

    # read genuines.txt
    genuines_path = output_perf + "\\genuines.txt"
    genuines_info = parse_genuines(genuines_path)
    return genuines_info


def run_perf_single_pair(test_folder, img_path0, img_path1, dpi):
    # test_folder = os.path.dirname(img_path0)
    # fpdbindex_path = os.path.join(test_folder, "i.fpdbindex")

    fpdbindex_path = os.path.join(test_folder, "i.fpdbindex")

    # write index file
    fp = open(fpdbindex_path, "w")
    fp.write(
        "# This file contains information about a fingerprint database.\n")
    fp.write(
        "# It is intended to help when iterating over all images of a database.\n"
    )
    fp.write("#\n")
    fp.write("#\n")
    fp.write("# Database attributes:\n")
    fp.write("## fingerIdsRegistered=0,1,2,3,4,5,6,7,8,9,10,11\n")
    fp.write("## fingerTypesRegistered=0\n")
    fp.write("## idFirstVerificationSample=1000\n")
    fp.write("## idPersonBottom=1\n")
    fp.write("## idPersonTop=66\n")
    fp.write("## idSampleBottom=0\n")
    fp.write("## idSampleTop=4000\n")
    fp.write("## itemType=png\n")
    fp.write("## locked=False\n")
    fp.write("## name=test\n")
    fp.write("## resolution={}\n".format(dpi))
    fp.write("# End of attributes\n")
    fp.write("# This file was generated by: MixedFingers\n")
    fp.write(
        "# The Python command that generated the fpdbindex can be found in the input file\n"
    )
    fp.write("#\n")
    fp.write("# Columns (tab separated):\n")
    fp.write("# Person ID (0 if unknown)\n")
    fp.write(
        "# 	Finger ID (= Finger Type if unspecified or 0 if unknown/unused)\n")
    fp.write("# 		Finger Type (according to ISO/IES 19794-2:2005 table 2)\n")
    fp.write(
        "# 			Sample ID (sometimes referred to as \"Attempt\" or \"Transaction\"\n"
    )
    fp.write("# 				Image file relative path\n")
    fp.write("#\n")
    fp.write("1\t5\t0\t0\t{}\n".format(img_path0))
    fp.write("1\t5\t0\t10000\t{}\n".format(img_path1))
    fp.close()

    genuines_info = execute_perf(fpdbindex_path)

    print(genuines_info)
    return


def run_perf_sum_score(test_folder, org=False):
    # write index file
    write_fpdboncex_cmd = "python ..\\..\\read_sys_file\\generate_4folder.py {} > {}\\i.fpdbindex".format(test_folder,
                                                                                                          test_folder)
    os.system(write_fpdboncex_cmd)

    fpdbindex_path = os.path.join(test_folder, "i.fpdbindex")
    genuines_info = execute_perf(fpdbindex_path, org)

    sum_score = 0
    score_array = []
    for info in genuines_info:
        sum_score += int(info['score'])
        score_array.append(int(info['score']))
    return sum_score, score_array


def runcmd(command):
    max_runs = 2
    run = 0
    while run < max_runs:
        try:
            ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8",
                                 timeout=5)
            if ret.returncode == 0:
                # print("success:", ret)
                return ret.stdout
            else:
                print("error:", ret)
                continue
        except subprocess.TimeoutExpired:
            continue
        finally:
            run += 1
    return False


def apply_perf_one(raw_e, raw_v, file_label):
    bin_e = raw_e.astype('uint8')
    bin_v = raw_v.astype('uint8')

    e_path = os.path.join(os.path.dirname(__file__), 'e_{}.bin'.format(file_label))
    v_path = os.path.join(os.path.dirname(__file__), 'v_{}.bin'.format(file_label))

    f_e = open(e_path, 'w+b')
    binary_format = bytearray(bin_e)
    f_e.write(binary_format)
    f_e.close()
    f_v = open(v_path, 'w+b')
    binary_format = bytearray(bin_v)
    f_v.write(binary_format)
    f_v.close()
    PBexe_path = os.path.join(os.path.dirname(__file__), 'PBexe.exe')
    stdout = runcmd('{} {} {}'.format(PBexe_path, e_path, v_path))  # match_score = 57133, rot = 0, dx = 0, dy = 0,
    match_score = -1
    if stdout:
        pos_str = stdout.find('match_score = ') + 14
        pos_end = stdout.find(', rot', pos_str)
        match_score = int(stdout[pos_str: pos_end])
    return match_score


def apply_perf(raw_e, raw_v):
    perf_result = []
    perf_score = 0
    for i in range(raw_e.shape[0]):
        match_score = apply_perf_one(raw_e[i], raw_v[i], "")
        perf_score += match_score
    # print('perf_score = {}'.format(perf_score))
    return perf_result


def apply_perf_thread(raw_e, raw_v, thread):
    def thread_job(data, label):
        data[2] = apply_perf_one(data[0], data[1], label)

    def multithread(data):
        all_thread = []
        for i in range(len(data)):
            thread = threading.Thread(target=thread_job, args=(data[i], str(i)))
            thread.start()
            all_thread.append(thread)
        for t in all_thread:
            t.join()

    perf_result = []
    perf_score = 0
    batch_size = raw_e.shape[0]
    for idx in range(0, batch_size, thread):
        thread_data = []
        if batch_size - idx < thread:
            thread = batch_size - idx
        for t in range(thread):
            thread_data.append(
                [raw_e[idx + t], raw_v[idx + t], 0])
        multithread(thread_data)

        for t in range(thread):
            perf_result.append(thread_data[t][2])
            perf_score += thread_data[t][2]
    # print('perf_score = {}'.format(perf_score))
    return perf_result


def apply_perf_BinPath(bin_e, bin_v):
    PBexe_path = os.path.join(os.path.dirname(__file__), 'PBexe.exe')
    stdout = runcmd('{} {} {}'.format(PBexe_path, bin_e, bin_v))  # match_score = 57133, rot = 0, dx = 0, dy = 0,
    match_score = -1
    if stdout:
        pos_str = stdout.find('match_score = ') + 14
        pos_end = stdout.find(', rot', pos_str)
        match_score = int(stdout[pos_str: pos_end])
    return match_score


def show_ndarray(img, name):
    img = np.float32(img)
    norm = (img - np.min(img)) / (np.max(img) - np.min(img)) * 255
    norm = cv2.normalize(src=img, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    cv2.imshow(name, norm)
    cv2.waitKey(1000)


def pattern_interpolation(img, strx, stry, endx, endy):
    for i in range(stry, endy, 30):
        for j in range(strx, endx, 30):
            for k in range(0, 9, 4):
                for l in range(0, 8, 7):
                    pos_x0 = j + k
                    pos_y0 = i + l
                    pos_x1 = j + k + 1
                    pos_y1 = i + l + 1
                    pos_x2 = j + k + 0
                    pos_y2 = i + l + 2
                    sum0 = (img[pos_y0 - 1, pos_x0 - 1] +
                            img[pos_y0 + 0, pos_x0 - 1] +
                            img[pos_y0 + 1, pos_x0 - 1] +
                            img[pos_y0 - 1, pos_x0 + 0] +
                            img[pos_y0 + 1, pos_x0 + 0] +
                            img[pos_y0 - 1, pos_x0 + 1] +
                            img[pos_y0 + 0, pos_x0 + 1]) / 7
                    sum1 = (img[pos_y1 + 0, pos_x1 - 1] +
                            img[pos_y1 - 1, pos_x1 + 0] +
                            img[pos_y1 + 1, pos_x1 + 0] +
                            img[pos_y1 - 1, pos_x1 + 1] +
                            img[pos_y1 + 0, pos_x1 + 1] +
                            img[pos_y1 + 1, pos_x1 + 1]) / 6
                    sum2 = (img[pos_y2 - 1, pos_x2 - 1] +
                            img[pos_y2 + 0, pos_x2 - 1] +
                            img[pos_y2 + 1, pos_x2 - 1] +
                            img[pos_y2 - 1, pos_x2 + 0] +
                            img[pos_y2 + 1, pos_x2 + 0] +
                            img[pos_y2 + 0, pos_x2 + 1] +
                            img[pos_y2 + 1, pos_x2 + 1]) / 7
                    img[pos_x0, pos_y0] = sum0
                    img[pos_x1, pos_y1] = sum1
                    img[pos_x2, pos_y2] = sum2


def mss_interpolation(img, width, height):
    pattern_interpolation(img, 16, 16, width - 20, height - 20)
    pattern_interpolation(img, 31, 31, width, height)
    # #721
    # pattern_interpolation(img, 12, 12, width - 20, height - 20)
    # pattern_interpolation(img, 27, 27, width - 20, height - 20)
    # pattern_interpolation(img, 12, 162, width - 20, 13)


def read_pngs(png_dir):
    img_list = []

    for root, dirs, files in os.walk(png_dir, topdown=False):
        for name in files:
            if os.path.splitext(name)[1] == '.png':
                img = cv2.imread(os.path.join(root, name))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
                img_list.append(img)

    print("img_list size is {}".format(len(img_list)))
    return img_list


def remap(data, repo):
    if data in repo:
        return repo[data]

    new_index = len(repo.keys()) + 1
    repo[data] = new_index
    return new_index


def get_index(path, ignore=[]):
    files = []
    ignore_count = 0
    err_count = 0
    user_et = {}

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if file[-3:] != 'png':
                continue
            if file.find("_Img8bmsk_") >= 0:
                continue
            if file.find("_0x8") >= 0:
                continue
            rp = "." + r.replace(path, '')
            files.append(os.path.join(rp, file))
            # files.append([os.path.join(r, file), int(file[0:2] + file[3:5] + file[6:8] + file[9:11] + file[12:14] + file[15:18])])
            # print(os.path.join(rp, file))

    if len(files) < 10:
        print("len(files) < 10")
        return
    # # change order
    # files.sort(key = lambda s: s[1])

    expr = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify|update)\\(st|45d|90d|135d)\\([0-9]+\\)*(\S+).png"
    )
    expr_partial = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify|update)\\(\S+)\\([0-9]+)\\(\S+).png")
    expr_simple_partial = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify|update)\\([0-9]+)\\(\S+).png")
    expr_enroll = re.compile(
        r"(\S+)\\(\d+)\\(enroll|verify|identify|update)\\(\S+).png")
    expr_simple = re.compile(r"(\S+)\\(enroll|verify|identify|update)\\(\S+).png")

    # no enroll/verify folder
    is_enroll = True
    expr_no_enroll = re.compile(r"(\S+)\\(\S+).png")

    all_entries = list()
    persons = dict()

    # print("Loading all entries.")
    for f in files:
        filename = f[2:]

        need_ignore = False
        if len(ignore) > 0:
            for i in range(len(ignore)):
                f_low = f.lower()
                k = ignore[i]
                b = f_low.find(k)
                if f_low.find(ignore[i]) >= 0:
                    need_ignore = True
                    break

        if need_ignore:
            ignore_count += 1
            continue
        # elif filename.find('mask') > 0 or filename.find(
        #         'msk') > 0 or filename.find('_T.png') > 0 or filename.find(
        #     '_RD_') > 0 or filename.find('_TRY_0_TRY_') > 0:
        #     err_count += 1
        #     continue
        elif filename.find('0x80') > 0 and filename.find('_0x08') < 0:
            err_count += 1
            continue

        m = expr.match(filename.lower())
        m_p = expr_partial.match(filename.lower())
        m_sp = expr_simple_partial.match(filename.lower())
        m_e = expr_enroll.match(filename.lower())
        m_s = expr_simple.match(filename.lower())
        m_ne = expr_no_enroll.match(filename.lower())

        if (m):
            # print(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
            person = m.group(1)
            finger = int(m.group(2))
            verify = m.group(3)
            quality = m.group(4)
            part = m.group(5)

            index_offset = 0
            if verify == "verify" or verify == "identify" or verify == "update":
                index_offset += 10000
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
            if verify == "verify" or verify == "identify" or verify == "update":
                index_offset += 10000
            if cond == "dry" or cond == "wash": index_offset += 200000
            if cond == "normal_on" or cond == "on" or cond == "normal":
                index_offset += 400000
            if cond == "normal_under" or cond == "under":
                index_offset += 600000
            if cond == "normal_walking" or cond == "walking" or cond == "walk" or cond == "normal_walk" or cond == "walk_on":
                index_offset += 800000
            if cond == "wet" or cond == "wet_on": index_offset += 1000000
            if cond == "lotion": index_offset += 1200000
            if cond == "normal_solar" or cond == "solar" or cond == "sunlight":
                index_offset += 1400000

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
            if verify == "verify" or verify == "identify" or verify == "update": index_offset += 10000

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
            if verify == "verify" or verify == "identify" or verify == "update":
                index_offset += 10000

            all_entries.append([person, finger, index_offset, filename])
        elif m_s:
            person = m_s.group(1)
            verify = m_s.group(2)
            index_offset = 0
            if verify == "verify" or verify == "identify" or verify == "update":
                index_offset += 10000

            all_entries.append([person, 0, index_offset, filename])
        elif m_ne:
            person = m_ne.group(1)
            index_offset = 0
            if is_enroll is False:
                index_offset += 10000

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

    if len(all_entries) <= 0:
        print("len(all_entries) <= 0")
        return

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

        if tmp_person == all_entries[i][0] and tmp_finger == all_entries[i][
            1] and all_entries[i][3].find("enroll") >= 0:
            enroll_count += 1

        if i + 1 < len(all_entries) and (
                (all_entries[i][3].find("enroll") >= 0
                 and all_entries[i + 1][3].find("enroll") < 0) or
                (tmp_person != all_entries[i + 1][0]
                 and tmp_finger != all_entries[i + 1][1])):
            if enroll_count != 17:
                print("#ERROR!\tperson {}\tfinger {}\tenroll_count {} != 17\n".
                      format(tmp_person, tmp_finger, enroll_count))
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
        if filename.rfind('_0x') > 0:
            sn = filename[filename.rfind('\\') + 1:filename.rfind('_0x')]
        else:
            sn = None

        # log = parse_file_name(filename)
        # if int(log.dict['irl']) > 0 and (filename.find('_0_') >= 0 or filename.find('_2_') >= 0):
        #     continue

        if sn is not None:
            if i is 0:
                if sn.find("_TRY_") >= 0:
                    break
                sn_past = sn
                try_count = 0
            elif sn_past != sn:
                sn_past = sn
                try_count = 0
            else:
                try_count += 1
        else:
            sn = filename[filename.rfind('\\') + 1:]
            if sn.find("_TRY_0_") >= 0:
                try_count = 0
            elif sn.find("_TRY_1_") >= 0:
                try_count = 1
            elif sn.find("_TRY_2_") >= 0:
                try_count = 2
            elif sn.find("_TRY_3_") >= 0:
                try_count = 3
            elif sn.find("_TRY_4_") >= 0:
                try_count = 4
            elif sn.find("_TRY_5_") >= 0:
                try_count = 5

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

        log = parse_file_name(filename)

        if sn is not None and offset > 0:
            if log.dict['egp'] == 'None' or int(log.dict['egp']) >= 80:
                output_update = "{0}\t{1}\t{2}\t{3}\t{4} : verify_count={5}".format(
                    remap(person, persons), finger, 0, offset + sample_counter,
                    filename, try_count)
            # elif int(log.dict['irl']) > 0 and (filename.find('_0_') >= 0 or filename.find('_2_') >= 0):
            #     pass  # work around
            else:
                output_update = "{0}\t{1}\t{2}\t{3}\t{4} : verify_count={5}".format(
                    remap(person, persons), finger, 0, offset + sample_counter,
                    filename, try_count)
        else:
            if log.dict['egp'] == 'None' or int(log.dict['egp']) >= 80:
                output_update = "{0}\t{1}\t{2}\t{3}\t{4}".format(
                    remap(person, persons), finger, 0, offset + sample_counter,
                    filename)
            # elif int(log.dict['irl']) > 0 and (filename.find('_0_') >= 0 or filename.find('_2_') >= 0):
            #     pass  # work around
            else:
                output_update = "{0}\t{1}\t{2}\t{3}\t{4}".format(
                    remap(person, persons), finger, 0, offset + sample_counter,
                    filename)

        output = "{0}\t{1}\t{2}\t{3}\t{4}".format(remap(person,
                                                        persons), finger, 0,
                                                  offset + sample_counter,
                                                  filename)
        sample_counter += 1
        output_list.append(output)
        output_update_list.append(output_update)

        # get user's et
        if log.dict['et'] is not 'None':
            user_et.setdefault(person, set()).add(log.dict['et'])

    return output_list, output_update_list, ignore_count, err_count, user_et


class LOG():
    def __init__(self):
        self.keywords = [
            # "et", "hc", "egp", "fk", "B", "Ba", "learn", "P", "ip", "rl", "irl", "rls", "sl", "mica", "702p", "dry", "sP", "isP"
            "et", "hc", "egp", "p",
            # "ip",
            "rl", "irl", "rls", "sl", "mica",
            # "dry", "sP", "isp", "q1", "q2", "q3",
            # "lcpr", "irg", "idt",
            "pLearn", "mr"
        ]
        self.dict = {}

    def update_dict(self, key, value):
        if key not in self.keywords:
            return False
        self.dict[key] = value
        return True

    def add_dict(self, key, value):
        self.dict[key] = value
        return True

    def add_dicts(self, keys, values):
        assert len(keys) == len(values)
        for i in range(len(keys)):
            self.dict[keys[i]] = values[i]
        return True


# def regax_keyword(keyword, text):
#     # 01-01-12-02-06-530_c01_p006_0x00000000_0_8bitImage_-999(0)_[0_0_0]_et=23.3_hc=6_mh=-1_mr=100_spp=100_sps=1_egp=93_fk=-3516_B=2_Ba=1_T=33_eq=-999_learn=00_M=384_Mc=915_MBc=716_ed=0_mlq=115_sd=81_md=0_er=1_R.bin
#     match = re.search(r"_{}=([0-9/-]*)".format(keyword), text)
#     if match:
#         return match.group(0).replace("_{}=".format(keyword), '')
#     else:
#         return 'None'

class RegaxClass():
    def regax_keyword(self, keyword, text):
        # 01-01-12-02-06-530_c01_p006_0x00000000_0_8bitImage_-999(0)_[0_0_0]_et=23.3_hc=6_mh=-1_mr=100_spp=100_sps=1_egp=93_fk=-3516_B=2_Ba=1_T=33_eq=-999_learn=00_M=384_Mc=915_MBc=716_ed=0_mlq=115_sd=81_md=0_er=1_R.bin
        match = re.findall(r"_{}=([0-9-.]*)".format(keyword), text)
        if len(match) == 3:
            value = "{}".format(match[2].replace("_{}=".format(keyword), ''))
            return value
        elif len(match) == 2:
            value = "{}".format(match[1].replace("_{}=".format(keyword), ''))
            return value
            # # value = "{},{}".format(match[0].replace("_{}=".format(keyword), ''),  match[1].replace("_{}=".format(keyword), ''))
            # diff = int(match[0].replace("_{}=".format(keyword), '')) -int(match[1].replace("_{}=".format(keyword), ''))
            # return abs(diff)
        elif len(match) == 1:
            return match[0].replace("_{}=".format(keyword), '')
        else:
            return 'None'

    def regax_serial_number(self, text):
        match = re.search(r"([a-z|A-Z|0-9/-_]*)_0x", text)
        if match:
            return match.group(0).replace('_0x', '')
        else:
            return 'None'

    def regax_3pairs(self, text):
        match = re.search(r"/[([0-9/-]*_[0-9/-]*_[0-9/-]*)/]", text)
        if match:
            value = match.group(0).replace('[', '').replace(']', '')
            return value.split('_')
        else:
            return ['None'] * 3

    def regax_score(self, text):
        match = re.search(r"_([0-9/-]*)/(([0-9/-]*)/)_", text)
        if match:
            value = match.group(0).replace('_', '').replace(')', '')
            return value.split('(')
        else:
            return ['None'] * 2

    def regax_RT(self, text):
        match = re.search(r"[a-z|A-Z].bin", text)
        if match:
            return match.group(0).replace('.bin', '')
        else:
            return 'None'

    def regax_pass(self, text):
        match = re.search(r"pass_[0-9]|fail_[0-9]", text)
        if match:
            return match.group(0).split('_')
        else:
            return ['enroll', '0']


def parse_files(root, name):
    log = LOG()
    rex = RegaxClass()

    # value = rex.regax_serial_number(name)
    # if log.add_dict("serial_number", value) == False:
    #     print('log.add_dict("serial_number", value) == False')
    #     return

    # serial_number
    log.add_dict("serial_number", name)

    values = rex.regax_pass(name)
    if log.add_dicts(['pass_mode', '?'], values) == False:
        print('log.add_dict([pass_mode, ?], value) == False')
        return

    # values = rex.regax_score(name)
    # if log.add_dicts(['score', 'Q/N_mode'], values) == False:
    #     print('log.add_dicts([score, Q/N_mode], values) == False')
    #     return

    # values = rex.regax_3pairs(name)
    # if log.add_dicts(['finger1', 'finger2', 'finger3'], values) == False:
    #     print('log.add_dicts([finger1, finger2, finger], values) == False')
    #     return

    for key in log.keywords:
        value = rex.regax_keyword(key, name)
        if log.update_dict(key, value) == False:
            print('log.update_dict(key, value) == False')
            return

    # value = regax_RT(name)
    # if log.add_dict('RT_mode', value) == False:
    #     print('log.add_dict([RT mode], value) == False')
    #     return

    if log.add_dict('folder', root) == False:
        print('log.add_dict(folder, root) == False')
        return

    return log


def parse_file_name(name):
    log = LOG()
    rex = RegaxClass()

    # serial_number
    log.add_dict("serial_number", name)

    values = rex.regax_pass(name)
    if log.add_dicts(['pass_mode', '?'], values) == False:
        print('log.add_dict([pass_mode, ?], value) == False')
        return

    for key in log.keywords:
        value = rex.regax_keyword(key, name)
        if log.update_dict(key, value) == False:
            print('log.update_dict(key, value) == False')
            return

    return log


if __name__ == '__main__':
    pass
