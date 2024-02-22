#!/bin/bash

set -ex

source /catkin_ws/devel/setup.bash
mkdir -p /src/BALM/output
roslaunch balm2 benchmark_realworld.launch
