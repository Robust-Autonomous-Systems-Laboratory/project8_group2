#!/usr/bin/env bash
set -e

PROJECT_DIR="$HOME/robotics/project_8"
ROS_SETUP="/opt/ros/jazzy/local_setup.bash"
TB_SETUP="$HOME/robotics/scripts/turtlebot_connect.sh"
WS_SETUP="$PROJECT_DIR/install/local_setup.bash"

cd "$PROJECT_DIR"

run_term() {
  local title="$1"
  local cmd="$2"

  terminator -T "$title" -x bash -lc "
    cd $PROJECT_DIR
    source $ROS_SETUP
    source $TB_SETUP
    source $WS_SETUP
    $cmd
    exec bash
  " &
}

wait_for_node() {
  local node_name="$1"
  local timeout="${2:-30}"
  local count=0

  until ros2 node list | grep -q "^${node_name}$"; do
    sleep 1
    count=$((count + 1))
    if [ "$count" -ge "$timeout" ]; then
      echo "Timeout waiting for node: $node_name"
      ros2 node list || true
      exit 1
    fi
  done
}

echo "Starting TurtleBot3 Navigation2..."
run_term "nav2" \
"ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=False \
  map:=maps/map_eerc722.yaml \
  params_file:=config/nav2_params.yaml"

sleep 3

echo "Starting speed costmap filter info server..."
run_term "speed_filter_info" \
"ros2 run nav2_map_server costmap_filter_info_server \
  --ros-args \
  -r __node:=speed_costmap_filter_info_server \
  -p filter_info_topic:=/speed_costmap_filter_info \
  -p type:=1 \
  -p mask_topic:=/speed_filter_mask \
  -p base:=100.0 \
  -p multiplier:=-1.0 \
  -p use_sim_time:=False"

echo "Starting keepout mask server..."
run_term "keepout_mask" \
"ros2 run nav2_map_server map_server \
  --ros-args \
  -r __node:=keepout_filter_mask_server \
  -p yaml_filename:=$PROJECT_DIR/config/keepout_mask.yaml \
  -p topic_name:=/keepout_filter_mask \
  -p frame_id:=map \
  -p use_sim_time:=False"

echo "Starting speed mask server..."
run_term "speed_mask" \
"ros2 run nav2_map_server map_server \
  --ros-args \
  -r __node:=speed_filter_mask_server \
  -p yaml_filename:=$PROJECT_DIR/config/speed_mask.yaml \
  -p topic_name:=/speed_filter_mask \
  -p frame_id:=map \
  -p use_sim_time:=False"

echo "Starting keepout costmap filter info server..."
run_term "keepout_filter_info" \
"ros2 run nav2_map_server costmap_filter_info_server \
  --ros-args \
  -r __node:=keepout_costmap_filter_info_server \
  -p filter_info_topic:=/keepout_costmap_filter_info \
  -p type:=0 \
  -p mask_topic:=/keepout_filter_mask \
  -p base:=0.0 \
  -p multiplier:=1.0 \
  -p use_sim_time:=False"

echo "Waiting for nodes to start..."
source "$ROS_SETUP"
source "$TB_SETUP" 2>/dev/null || true
source "$WS_SETUP" 2>/dev/null || true

wait_for_node "/keepout_filter_mask_server" 30
wait_for_node "/speed_filter_mask_server" 30
wait_for_node "/keepout_costmap_filter_info_server" 30
wait_for_node "/speed_costmap_filter_info_server" 30

echo "Configuring and activating lifecycle nodes..."

ros2 lifecycle set /keepout_filter_mask_server configure
ros2 lifecycle set /keepout_filter_mask_server activate

ros2 lifecycle set /speed_filter_mask_server configure
ros2 lifecycle set /speed_filter_mask_server activate

ros2 lifecycle set /keepout_costmap_filter_info_server configure
ros2 lifecycle set /keepout_costmap_filter_info_server activate

ros2 lifecycle set /speed_costmap_filter_info_server configure
ros2 lifecycle set /speed_costmap_filter_info_server activate

echo "All navigation and filter nodes started."