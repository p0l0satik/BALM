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

def visualise_pcds(dataset, poses):
    poses_list = defaultdict()
    pcds = []

    try:
        f = open(poses, newline='')
    except OSError:
        print("Could not open/read file:", poses)
        sys.exit()

    with f:
        reader = csv.reader(f)
        for n, row in enumerate(reader):
            row = [float(el) for el in row[:7]]
            # splitting row into translation[0:3] and rotation[3:7]             (row[:3], R.from_quat(row[3:]))
            poses_list[n] = (row[:3], R.from_quat(row[3:]))

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
            pcd = pcd.translate(poses_list[pose_number][0])
            rotation = np.asarray(poses_list[pose_number][1].as_matrix())
            pcd = pcd.rotate(rotation)
            pcd = pcd.paint_uniform_color([random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)])
            pcds.append(pcd)
    o3d.visualization.draw_geometries(pcds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default='/home/polosatik/BALM/datas/hilti',
        help="path to the pointclouds",
    )
    parser.add_argument(
        "--original_poses",
        type=str,
        default= '/home/polosatik/Desktop/balm_output_hilti/pose_start.csv',
        help="path to the file with poses before refinement",
    )
    parser.add_argument(
        "--refined_poses",
        type=str,
        default='/home/polosatik/Desktop/balm_output_hilti/pose_result.csv',
        help="path to the file with poses after refinement",
    )
    args = parser.parse_args()
    dataset = Path(args.dataset)
    poses_orig = Path(args.original_poses)
    poses_refined = Path(args.refined_poses)
   
    visualise_pcds(dataset=dataset, poses=poses_orig)
    visualise_pcds(dataset=dataset, poses=poses_refined)
