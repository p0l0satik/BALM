import argparse
import sys
import csv
import os

from pathlib import Path


def extract_integer(filename):
    return int(filename.split(".")[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--poses",
        type=str,
        default="/home/polosatik/voxel-slam/evaluation/hilti/poses",
        help="path to the pointclouds",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default="/home/polosatik/mnt/hilti/14_short_balm",
        help="path to the file with poses before refinement",
    )

    args = parser.parse_args()

    poses = Path(args.poses)
    save_path = Path(args.save_path) / "alidarPose.csv"

    with open(save_path, mode="w") as saved_poses:
        saved_poses_csv = csv.writer(saved_poses, lineterminator=",\n")
        for _, _, files in os.walk(poses):
            for file in sorted(files, key=extract_integer):
                filename = poses / file
                with open(filename, newline="") as f:
                    lines = f.readlines()
                    matrix = [
                        [el.strip("\n") for el in row.split(" ")[0:7]] for row in lines
                    ]
                    matrix[3][3] = float("".join(filter(str.isdigit, file))) + 1
                    saved_poses_csv.writerows(matrix)
