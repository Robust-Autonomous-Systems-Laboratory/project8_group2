#!/usr/bin/env python3

import sys
import math
import time
import argparse
from typing import List, Optional, Tuple

import rclpy
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
        start_time = time.time()

        while time.time() - start_time < timeout_sec:
            rclpy.spin_once(self, timeout_sec=0.1)
            pose = self.get_latest_pose_xy()
            if pose is not None:
                return pose

        return None

    def distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def patrol_waypoints(self) -> List[Tuple[int, str, PoseStamped]]:
        """
        Replace these coordinates with your real map-frame waypoints from EERC 722.

        I included waypoint 1 again as the final waypoint so each patrol cycle
        returns near the start and you can compute loop-closure drift cleanly.
        """
        return [
            (1, 'Start corner / waypoint 1', self.make_pose(0.00, 0.00, 0.0)),
            (2, 'Hall approach near keepout zone', self.make_pose(1.00, 0.20, 0.0)),
            (3, 'Far side of room', self.make_pose(1.60, 1.00, 90.0)),
            (4, 'Opposite wall / turn point', self.make_pose(0.80, 1.70, 180.0)),
            (5, 'Return corridor through patrol loop', self.make_pose(-0.20, 1.00, -90.0)),
            (6, 'Loop closure back near waypoint 1', self.make_pose(0.00, 0.00, 0.0)),
        ]

    def wait_for_nav2_active(self):
        self.get_logger().info('Waiting for Nav2 to become active...')
        self.navigator.waitUntilNav2Active()
        self.get_logger().info('Nav2 is active.')

    def run_single_waypoint(self, waypoint_id: int, label: str, pose: PoseStamped) -> str:
        start_time = time.time()

        self.get_logger().info(
            f'Navigating to waypoint {waypoint_id} ({label}) | '
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
            self.get_logger().error('Could not get initial /amcl_pose. Make sure AMCL is running.')
            return

        self.get_logger().info(
            f'Initial AMCL pose received: x={initial_pose[0]:.3f}, y={initial_pose[1]:.3f}'
        )

        waypoints = self.patrol_waypoints()
        if len(waypoints) < 5:
            self.get_logger().error('You must define at least 5 patrol waypoints.')
            return

        total_success = 0
        total_failed = 0

        for cycle in range(1, self.cycles + 1):
            self.get_logger().info('=' * 60)
            self.get_logger().info(f'Starting patrol cycle {cycle}/{self.cycles}')
            self.get_logger().info('=' * 60)

            cycle_success = 0
            cycle_failed = 0
            cycle_start_pose: Optional[Tuple[float, float]] = None

            for index, (waypoint_id, label, pose) in enumerate(waypoints):
                status = self.run_single_waypoint(waypoint_id, label, pose)

                if status == 'SUCCEEDED':
                    cycle_success += 1
                    total_success += 1
                else:
                    cycle_failed += 1
                    total_failed += 1
                    self.get_logger().warn(
                        f'Waypoint {waypoint_id} did not succeed ({status}). '
                        f'Continuing to next waypoint.'
                    )

                # Record the start pose after reaching waypoint 1 successfully
                if index == 0 and status == 'SUCCEEDED':
                    time.sleep(0.5)
                    cycle_start_pose = self.wait_for_amcl_pose(timeout_sec=2.0)
                    if cycle_start_pose is not None:
                        self.get_logger().info(
                            f'Cycle {cycle} start pose at waypoint 1: '
                            f'x={cycle_start_pose[0]:.3f}, y={cycle_start_pose[1]:.3f}'
                        )
                    else:
                        self.get_logger().warn(
                            f'Cycle {cycle}: could not record start pose at waypoint 1.'
                        )

            # Record end pose after final waypoint, which should return near waypoint 1
            time.sleep(0.5)
            cycle_end_pose = self.wait_for_amcl_pose(timeout_sec=2.0)

            if cycle_start_pose is not None and cycle_end_pose is not None:
                drift = self.distance(cycle_start_pose, cycle_end_pose)
                self.get_logger().info(
                    f'Cycle {cycle} end pose: '
                    f'x={cycle_end_pose[0]:.3f}, y={cycle_end_pose[1]:.3f}'
                )
                self.get_logger().info(f'Cycle {cycle} drift: {drift:.3f} m')
            else:
                self.get_logger().warn(
                    f'Cycle {cycle} drift could not be computed because start or end pose was missing.'
                )

            self.get_logger().info(
                f'Cycle {cycle} summary | successes: {cycle_success} | failures: {cycle_failed}'
            )

        self.get_logger().info('=' * 60)
        self.get_logger().info(
            f'Patrol finished | total successes: {total_success} | total failures: {total_failed}'
        )
        self.get_logger().info('=' * 60)


def parse_args():
    parser = argparse.ArgumentParser(description='Autonomous patrol node for Nav2.')
    parser.add_argument(
        '--cycles',
        type=int,
        default=3,
        help='Number of patrol cycles to execute (default: 3)'
    )

    args, _ = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    rclpy.init(args=sys.argv)

    node = PatrolNode(cycles=args.cycles)

    try:
        node.run_patrol()
    except KeyboardInterrupt:
        node.get_logger().info('Patrol interrupted by user.')
    finally:
        try:
            node.navigator.lifecycleShutdown()
        except Exception:
            pass

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
