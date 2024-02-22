FROM ros:noetic

RUN apt-get update \
    &&  apt-get install -y \
        build-essential \
        cmake \
        git \
        libgtk2.0-dev \
        pkg-config \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev  \
        libgoogle-glog-dev \
        libatlas-base-dev \
        libeigen3-dev \
        libsuitesparse-dev


RUN git clone https://ceres-solver.googlesource.com/ceres-solver \
    &&  cd ceres-solver \
    &&  mkdir release \
    &&  cd release \
    &&  cmake .. \
    &&  make -j20 \
    &&  make test \
    &&  make install

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
      libeigen3-dev \
      libpcl-dev \
      cmake \
      ros-noetic-pcl-conversions \
      ros-noetic-pcl-ros \
      ros-noetic-rviz

RUN mkdir -p catkin_ws/src/BALM

ADD . /catkin_ws/src/BALM

WORKDIR /catkin_ws

RUN rm -rfd /src/BALM/BALM-old && . /opt/ros/noetic/setup.sh && catkin_make

ENTRYPOINT ["bash", "/catkin_ws/src/BALM/run.sh"]
