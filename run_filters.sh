#!/usr/bin/env bash
set -e

cd ~/robotics/project_8

echo "Starting TurtleBot3 Navigation2..."
gnome-terminal -- bash -c '
cd ~/robotics/project_8
source /opt/ros/jazzy/local_setup.bash
source ../scripts/turtlebot_connect.sh
source install/local_setup.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=False \
  map:=maps/map_eerc722.yaml \
  params_file:=config/nav2_params.yaml
exec bash
'

sleep 3

echo "Starting speed costmap filter info server..."
gnome-terminal -- bash -c '
cd ~/robotics/project_8
source /opt/ros/jazzy/local_setup.bash
source ../scripts/turtlebot_connect.sh
source install/local_setup.bash
ros2 run nav2_map_server costmap_filter_info_server \
  --ros-args \
  -r __node:=speed_costmap_filter_info_server \
  -p filter_info_topic:=/speed_costmap_filter_info \
  -p type:=1 \
  -p mask_topic:=/speed_filter_mask \
  -p base:=100.0 \
  -p multiplier:=-1.0 \
  -p use_sim_time:=False
exec bash
'

echo "Starting keepout mask server..."
gnome-terminal -- bash -c '
cd ~/robotics/project_8
source /opt/ros/jazzy/local_setup.bash
source ../scripts/turtlebot_connect.sh
source install/local_setup.bash
ros2 run nav2_map_server map_server \
  --ros-args \
  -r __node:=keepout_filter_mask_server \
  -p yaml_filename:=/home/progress/robotics/project_8/config/keepout_mask.yaml \
  -p topic_name:=/keepout_filter_mask \
  -p frame_id:=map \
  -p use_sim_time:=False
exec bash
'

echo "Starting speed mask server..."
gnome-terminal -- bash -c '
cd ~/robotics/project_8
source /opt/ros/jazzy/local_setup.bash
source ../scripts/turtlebot_connect.sh
source install/local_setup.bash
ros2 run nav2_map_server map_server \
  --ros-args \
  -r __node:=speed_filter_mask_server \
  -p yaml_filename:=/home/progress/robotics/project_8/config/speed_mask.yaml \
  -p topic_name:=/speed_filter_mask \
  -p frame_id:=map \
  -p use_sim_time:=False
exec bash
'

echo "Starting keepout costmap filter info server..."
gnome-terminal -- bash -c '
cd ~/robotics/project_8
source /opt/ros/jazzy/local_setup.bash
source ../scripts/turtlebot_connect.sh
source install/local_setup.bash
ros2 run nav2_map_server costmap_filter_info_server \
  --ros-args \
  -r __node:=keepout_costmap_filter_info_server \
  -p filter_info_topic:=/keepout_costmap_filter_info \
  -p type:=0 \
  -p mask_topic:=/keepout_filter_mask \
  -p base:=0.0 \
  -p multiplier:=1.0 \
  -p use_sim_time:=False
exec bash
'

echo "Waiting for nodes to start..."
sleep 5

echo "Configuring and activating lifecycle nodes..."
source /opt/ros/jazzy/setup.bash
source ~/robotics/scripts/turtlebot_connect.sh 2>/dev/null || true
source ~/robotics/project_8/install/setup.bash 2>/dev/null || true

ros2 lifecycle set /keepout_filter_mask_server configure
ros2 lifecycle set /keepout_filter_mask_server activate

ros2 lifecycle set /speed_filter_mask_server configure
ros2 lifecycle set /speed_filter_mask_server activate

ros2 lifecycle set /keepout_costmap_filter_info_server configure
ros2 lifecycle set /keepout_costmap_filter_info_server activate

ros2 lifecycle set /speed_costmap_filter_info_server configure
ros2 lifecycle set /speed_costmap_filter_info_server activate

echo "All navigation and filter nodes started."
