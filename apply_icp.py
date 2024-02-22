import csv
import open3d as o3d
import argparse
import numpy as np
import random

from pathlib import Path
from typing import List


def pairwise_registration(
    source: o3d.geometry.PointCloud,
    target: o3d.geometry.PointCloud,
    max_distance_coarse: float,
    max_distance_fine: float,
) -> np.ndarray:
    #  applying coarse alignment
    icp_coarse = o3d.pipelines.registration.registration_icp(
        source,
        target,
        max_distance_coarse,
        np.identity(4),
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
    )

    #  applying fine alignment
    icp_fine = o3d.pipelines.registration.registration_icp(
        source,
        target,
        max_distance_fine,
        icp_coarse.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
    )

    return icp_fine.transformation


def full_registration(
    pcds: List[o3d.geometry.PointCloud],
    max_distance_coarse: float,
    max_distance_fine: float,
) -> List[np.ndarray]:
    previous_tranform = np.identity(4)
    transform_matrixes = []
    result_poses = []

    # finding transforms from each pair of clouds
    for i in range(1, len(pcds)):
        transform = pairwise_registration(
            pcds[i], pcds[i - 1], max_distance_coarse, max_distance_fine
        )
        transform_matrixes.append(transform)

    # carefully applying transforms to align all clouds to the first one
    for i in range(1, len(pcds)):
        # applying all previous transforms + a transform between this specific pair
        # will align each cloud with the first one
        transform = previous_tranform @ transform_matrixes[i - 1]
        # saving transform matrix
        result_poses.append(transform)
        # applying for visualisation
        pcds[i].transform(transform)
        # saving current transform for next usage
        previous_tranform = transform

    return result_poses


def load_point_clouds(
    path: str, starting_cloud: int, number: int
) -> List[o3d.geometry.PointCloud]:
    pcds = []
    for i in range(number):
        filename = str(path / f"{starting_cloud+i}.pcd")
        pcd = o3d.io.read_point_cloud(str(filename))
        pcd = pcd.paint_uniform_color(
            [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
        )
        # downsampling and estimating normals for point to plane ICP
        pcd_down = pcd.voxel_down_sample(voxel_size=0.3)
        pcd_down.estimate_normals()
        pcds.append(pcd_down)
    return pcds


def save_poses(poses, filename: Path):
    with open(filename, mode="w") as saved_poses:
        saved_poses_csv = csv.writer(saved_poses, lineterminator=",\n")
        for pose in poses:
            pose_m = pose.tolist()
            saved_poses_csv.writerows(pose_m)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default="",
        help="path to the pointclouds",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default="",
        help="path where to save poses after alignment",
    )
    parser.add_argument(
        "--dataset_len",
        type=int,
        default=20,
        help="number of clouds we want to read",
    )
    parser.add_argument(
        "--first_cloud_number",
        type=int,
        default=0,
        help="number of cloud we want to start from (in case we want to process only part of the dataset)",
    )
    parser.add_argument(
        "--max_distance_coarse",
        type=float,
        default=2.0,
        help="maximum corresponding distance for initial step of ICP",
    )
    parser.add_argument(
        "--max_distance_fine",
        type=float,
        default=0.4,
        help="maximum corresponding distance for finetuning step of ICP",
    )
    parser.add_argument(
        "--visualise",
        type=bool,
        default=True,
    )

    args = parser.parse_args()
    dataset = Path(args.dataset)
    save_path = Path(args.save_path)

    # loading and preparing clouds
    pcds_down = load_point_clouds(dataset, args.first_cloud_number, args.dataset_len)

    if args.visualise:
        o3d.visualization.draw_geometries(pcds_down)

    # applying ICP
    result_poses = full_registration(
        pcds_down, args.max_distance_coarse, args.max_distance_fine
    )

    if args.visualise:
        o3d.visualization.draw_geometries(pcds_down)

    # saving result to a file
    save_poses(result_poses, save_path)
