import open3d as o3d
import argparse
import sys
import csv
import os
from pathlib import Path
from collections import defaultdict


def visualise_pcds(dataset, poses, save_path=None):
    poses_list = defaultdict()
    for _, _, files in os.walk(poses):
        for file in files:
            filename = poses / file
            with open(filename, newline="") as f:
                lines = f.readlines()
                matrix = [
                    [round(float(el), 4) for el in row.split(" ")[0:7]] for row in lines
                ]
                s = "".join(filter(str.isdigit, file))
                pose_number = int(s)
                poses_list[pose_number] = matrix

    poses = Path(save_path) / "alidarPose.csv"
    with open(poses, mode="w") as save_poses:
        saved_poses_csv = csv.writer(save_poses, lineterminator=",\n")
        matrix = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
        for _, _, files in os.walk(dataset):
            for file in files:
                filepath = str(dataset / file)
                pcd_strange = o3d.io.read_point_cloud(filepath)
                pcd = o3d.geometry.PointCloud()
                pcd.points = pcd_strange.points
                # getting pose name from file
                s = "".join(filter(str.isdigit, file))
                pose_number = int(s)
                # transform
                pcd = pcd.transform(poses_list[pose_number])

                # saving pcd
                new_pcd_filename = "full" + file
                save_filename = str(save_path / new_pcd_filename)
                o3d.io.write_point_cloud(save_filename, pcd)

                # saving matrix of ones to poses
                matrix[3][3] = float(pose_number)
                saved_poses_csv.writerows(matrix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default="/home/polosatik/voxel-slam/evaluation/hilti/clouds",
        help="path to the pointclouds",
    )
    parser.add_argument(
        "--original_poses",
        type=str,
        default="/home/polosatik/voxel-slam/evaluation/hilti/poses",
        help="path to the file with poses before refinement",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default="/home/polosatik/mnt/hilti/14_short_balm",
        help="path to the file with poses before refinement",
    )
    args = parser.parse_args()
    dataset = Path(args.dataset)
    poses_orig = Path(args.original_poses)
    save_path = Path(args.save_path)

    visualise_pcds(dataset=dataset, poses=poses_orig, save_path=save_path)
