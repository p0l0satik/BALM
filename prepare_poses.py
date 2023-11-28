import open3d as o3d
import argparse
import sys
import csv
import os
import numpy as np
import random

from pathlib import Path
from scipy.spatial.transform import Rotation as R
from collections import defaultdict

def extract_integer(filename):
    return int(filename.split('.')[0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--poses",
        type=str,
        default='/home/polosatik/voxel-slam/evaluation/hilti/poses',
        help="path to the pointclouds",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default= '/home/polosatik/BALM/datas/hilti',
        help="path to the file with poses before refinement",
    )

    args = parser.parse_args()

    poses = Path(args.poses)
    save_path = Path(args.save_path)/"alidarPose.csv"

    try:
        saved_poses = open(save_path, mode='w')
    except OSError:
        print("Could not open/read file:", save_path)
        sys.exit()

    with saved_poses:
        saved_poses_csv = csv.writer(saved_poses, lineterminator=",\n")
        for _, _, files in os.walk(poses):
            for file in sorted(files, key=extract_integer):
                filename = poses/file
                try:
                    f = open(filename, newline='')
                except OSError:
                    print("Could not open/read file:", filename)
                    sys.exit()

                with f:
                    lines = f.readlines()
                    matrix = [[round(float(el), 10) for el in row.split(" ")[0:7]] for row in lines]
                    matrix[3][3] = float(''.join(filter(str.isdigit, file))) + 1
                    saved_poses_csv.writerows(matrix)


            