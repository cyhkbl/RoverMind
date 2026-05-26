#!/usr/bin/env python3
"""Obstacle avoidance node — subscribes to /scan and pauses motion when obstacles are close."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


class ObstacleAvoiderNode(Node):
    """Monitors laser scan and publishes obstacle state."""

    def __init__(self):
        super().__init__("obstacle_avoider")

        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("obstacle_distance", 0.5)
        self.declare_parameter("obstacle_topic", "/obstacle_detected")

        scan_topic = self.get_parameter("scan_topic").value
        self.obstacle_distance = float(self.get_parameter("obstacle_distance").value)
        obstacle_topic = self.get_parameter("obstacle_topic").value

        self.obstacle_pub = self.create_publisher(Bool, obstacle_topic, 10)
        self.scan_sub = self.create_subscription(LaserScan, scan_topic, self._scan_callback, 10)

        self.get_logger().info(
            f"ObstacleAvoider: listening on {scan_topic}, "
            f"threshold={self.obstacle_distance}m, publishing to {obstacle_topic}"
        )

    def _scan_callback(self, msg: LaserScan) -> None:
        min_range = min(r for r in msg.ranges if r > msg.range_min)
        detected = Bool()
        detected.data = min_range < self.obstacle_distance
        self.obstacle_pub.publish(detected)

        if detected.data:
            self.get_logger().warn(
                f"Obstacle detected at {min_range:.2f}m (threshold={self.obstacle_distance}m)"
            )


def main():
    rclpy.init()
    node = ObstacleAvoiderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
