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

def visualise_pcds(dataset, poses, save_path = None):
    poses_list = defaultdict()
    pcds = []

    for _, _, files in os.walk(poses):
        for file in files:
            filename = poses/file
            try:
                f = open(filename, newline='')
            except OSError:
                print("Could not open/read file:", filename)
                sys.exit()
            with f:
                lines = f.readlines()
                matrix = [[round(float(el), 4) for el in row.split(" ")[0:7]] for row in lines]
                s = ''.join(filter(str.isdigit, file))
                pose_number = int(s) 
                poses_list[pose_number] = matrix

    for _, _, files in os.walk(dataset):
        for file in files:
            if file =='alidarPose.csv':
                continue 
            filepath = str(dataset/file)
            pcd_strange = o3d.io.read_point_cloud(filepath)
            pcd = o3d.geometry.PointCloud()
            pcd.points = pcd_strange.points
            # getting pose name from file
            s = ''.join(filter(str.isdigit, file))
            pose_number = int(s) 
            pcd = pcd.transform(poses_list[pose_number])
            # pcd = pcd.translate(poses_list[pose_number][0])
            # rotation = np.asarray(poses_list[pose_number][1].as_matrix())
            # pcd = pcd.rotate(rotation)
            pcd = pcd.paint_uniform_color([random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)])
            if save_path:
                new_pcd_filename = "full"+file
                save_filename = str(save_path/new_pcd_filename)
                o3d.io.write_point_cloud(save_filename, pcd)
            pcds.append(pcd)
    o3d.visualization.draw_geometries(pcds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default='/home/polosatik/voxel-slam/evaluation/hilti/clouds',
        help="path to the pointclouds",
    )
    parser.add_argument(
        "--original_poses",
        type=str,
        default= '/home/polosatik/voxel-slam/evaluation/hilti/poses',
        help="path to the file with poses before refinement",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default= '/home/polosatik/BALM/datas/hilti',
        help="path to the file with poses before refinement",
    )
    args = parser.parse_args()
    dataset = Path(args.dataset)
    poses_orig = Path(args.original_poses)
    save_path = Path(args.save_path)
   
    visualise_pcds(dataset=dataset, poses=poses_orig,save_path=save_path)
