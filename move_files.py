import argparse
import os

files = []

angle_list = ['N05D', 'N10D', 'N15D', 'N20D', 'N25D', 'N30D', 'N35D', 'N40D', 'N45D', 'P00D', 'P05D', 'P10D', 'P15D', 'P20D', 'P25D', 'P30D', 'P35D', 'P40D', 'P45D']
weight_list = ['000g', '100g', '200g', '300g', '400g', '500g', '600g']
chart_list = ['BK', 'WK', 'CT']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory to parse", default=".")
    args = parser.parse_args()
    path = args.dir

    # angle
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:

            check_angle = False
            for angle_name in angle_list:
                if angle_name.find('N') >= 0:
                    angle_key = '-' + angle_name[1:4]
                # elif angle_name == 'P00D':
                #     angle_key = '_00D_'
                else:
                    angle_key = angle_name[1:4]

                check_angle = file.find(angle_key) >= 0
                if check_angle:
                    break

            check_weight = False
            for weight_name in weight_list:
                if weight_name == '000g':
                    check_weight = file.find('_0g_') >= 0 or file.find('_00g_') >= 0 or file.find('_000g_') >= 0
                else:
                    check_weight = file.find('_' + weight_name + '_') >= 0
                if check_weight:
                    break

            check_chart = False
            for chart_name in chart_list:
                check_chart = file.find(chart_name + '_') >= 0
                if check_chart:
                    break
            if chart_name is 'CT':
                chart_name = 'CTR'

            if check_angle and check_weight and check_chart:
                src = os.path.join(r, file)
                folder_dir = os.path.join(path, chart_name, 'image_raw', angle_name, weight_name)
                dst = os.path.join(folder_dir, file)
                if not os.path.exists(folder_dir):
                    os.makedirs(folder_dir)
                if os.path.exists(src) and os.path.exists(dst) is False:
                    os.rename(src, dst)
            else:
                print()
                pass
