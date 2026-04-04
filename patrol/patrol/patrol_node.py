#!/usr/bin/env python3

import math
import time
import argparse
from typing import List, Optional, Tuple
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


class PatrolNode(Node):
    def __init__(self, cycles: int = 3):
        super().__init__('patrol_node')
        self.cycles = cycles
        self.latest_amcl_pose: Optional[PoseWithCovarianceStamped] = None

        self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        self.navigator = BasicNavigator()

    def amcl_callback(self, msg: PoseWithCovarianceStamped):
        self.latest_amcl_pose = msg

    def make_pose(self, x: float, y: float, yaw_deg: float) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        yaw = math.radians(yaw_deg)
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def get_latest_pose_xy(self) -> Optional[Tuple[float, float]]:
        if self.latest_amcl_pose is None:
            return None
        x = self.latest_amcl_pose.pose.pose.position.x
        y = self.latest_amcl_pose.pose.pose.position.y
        return (x, y)

    def wait_for_amcl_pose(self, timeout_sec: float = 10.0) -> Optional[Tuple[float, float]]:
        start = time.time()
        while time.time() - start < timeout_sec:
            rclpy.spin_once(self, timeout_sec=0.1)
            pose = self.get_latest_pose_xy()
            if pose is not None:
                return pose
        return None

    def distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def patrol_waypoints(self) -> List[PoseStamped]:
        
        return [
           # we might want to return a list of maybe 4 to 5 waypoints
        ]

    def wait_for_nav2_active(self):
        self.get_logger().info('Waiting for Nav2 to become active...')
        self.navigator.waitUntilNav2Active()
        self.get_logger().info('Nav2 is active.')

    def run_single_waypoint(self, waypoint_id: int, pose: PoseStamped) -> str:
        start_time = time.time()

        self.get_logger().info(
            f'Navigating to waypoint {waypoint_id}: '
            f'x={pose.pose.position.x:.2f}, y={pose.pose.position.y:.2f}'
        )

        self.navigator.goToPose(pose)

        while not self.navigator.isTaskComplete():
            rclpy.spin_once(self, timeout_sec=0.1)

        result = self.navigator.getResult()
        elapsed = time.time() - start_time

        if result == TaskResult.SUCCEEDED:
            status = 'SUCCEEDED'
        elif result == TaskResult.FAILED:
            status = 'FAILED'
        elif result == TaskResult.CANCELED:
            status = 'CANCELED'
        else:
            status = 'UNKNOWN'

        self.get_logger().info(
            f'Waypoint {waypoint_id} result: {status} | elapsed: {elapsed:.2f} s'
        )
        return status

    def run_patrol(self):
        self.wait_for_nav2_active()

        initial_pose = self.wait_for_amcl_pose(timeout_sec=10.0)
        if initial_pose is None:
            self.get_logger().error('Could not get initial /amcl_pose. Is AMCL running?')
            return

        self.get_logger().info(
            f'Initial AMCL pose received: x={initial_pose[0]:.3f}, y={initial_pose[1]:.3f}'
        )

        waypoints = self.patrol_waypoints()

        total_success = 0
        total_failed = 0

        #not the full code yet but will be, feel free to change anything here
        #i feel like we might need a loop somewhere in here 

        


def parse_args():
    parser = argparse.ArgumentParser(description='Autonomous patrol node for Nav2.')
    parser.add_argument(
        '--cycles',
        type=int,
        default=3,
        help='Number of patrol cycles to execute (default: 3)'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rclpy.init()

    node = PatrolNode(cycles=args.cycles)

    try:
        node.run_patrol()
    except KeyboardInterrupt:
        node.get_logger().info('Patrol interrupted by user.')
    finally:
        node.navigator.lifecycleShutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()