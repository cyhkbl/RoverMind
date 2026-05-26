#!/usr/bin/env python3
"""Closed-loop motion controller using odometry feedback."""

import math

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.publisher import Publisher


def normalize_angle(angle: float) -> float:
    """Normalize angle to [-pi, pi]."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class ClosedLoopController:
    """PID-based closed-loop controller for distance and rotation."""

    def __init__(
        self,
        node: Node,
        cmd_vel_pub: Publisher,
        max_linear_speed: float = 1.0,
        max_angular_speed: float = 1.0,
        linear_kp: float = 1.5,
        angular_kp: float = 2.0,
        distance_tolerance: float = 0.05,
        angle_tolerance: float = 0.05,
    ):
        self.node = node
        self.cmd_vel_pub = cmd_vel_pub
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed
        self.linear_kp = linear_kp
        self.angular_kp = angular_kp
        self.distance_tolerance = distance_tolerance
        self.angle_tolerance = angle_tolerance

        self._start_x: float | None = None
        self._start_y: float | None = None
        self._start_yaw: float | None = None
        self._current_x: float = 0.0
        self._current_y: float = 0.0
        self._current_yaw: float = 0.0
        self._odom_received: bool = False

        self.odom_sub = node.create_subscription(
            Odometry, "/odom", self._odom_callback, 10
        )

    def _odom_callback(self, msg: Odometry) -> None:
        self._current_x = msg.pose.pose.position.x
        self._current_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self._current_yaw = math.atan2(siny_cosp, cosy_cosp)
        self._odom_received = True

    def _set_start_pose(self) -> None:
        self._start_x = self._current_x
        self._start_y = self._current_y
        self._start_yaw = self._current_yaw

    def _distance_traveled(self) -> float:
        dx = self._current_x - self._start_x
        dy = self._current_y - self._start_y
        return math.sqrt(dx * dx + dy * dy)

    def _angle_turned(self) -> float:
        return normalize_angle(self._current_yaw - self._start_yaw)

    def _publish_vel(self, linear_x: float = 0.0, angular_z: float = 0.0) -> None:
        twist = Twist()
        twist.linear.x = max(-self.max_linear_speed, min(linear_x, self.max_linear_speed))
        twist.angular.z = max(-self.max_angular_speed, min(angular_z, self.max_angular_speed))
        self.cmd_vel_pub.publish(twist)

    def stop(self) -> None:
        self._publish_vel(0.0, 0.0)

    def move_distance(self, target_distance: float) -> bool:
        """Move forward/backward by target_distance meters. Returns True when done."""
        if not self._odom_received:
            self.node.get_logger().warn("No odom received yet, skipping move_distance")
            return True

        self._set_start_pose()
        traveled = self._distance_traveled()

        if traveled >= abs(target_distance) - self.distance_tolerance:
            self.stop()
            return True

        direction = 1.0 if target_distance >= 0.0 else -1.0
        error = abs(target_distance) - traveled
        speed = direction * min(self.linear_kp * error, self.max_linear_speed)
        self._publish_vel(linear_x=speed)
        return False

    def move_distance_step(self, target_distance: float) -> bool:
        """Check if move_distance is complete. Call in a loop."""
        if not self._odom_received:
            return True

        traveled = self._distance_traveled()
        if traveled >= abs(target_distance) - self.distance_tolerance:
            self.stop()
            return True

        direction = 1.0 if target_distance >= 0.0 else -1.0
        error = abs(target_distance) - traveled
        speed = direction * min(self.linear_kp * error, self.max_linear_speed)
        self._publish_vel(linear_x=speed)
        return False

    def rotate_angle(self, target_angle: float) -> bool:
        """Rotate by target_angle radians. Returns True when done."""
        if not self._odom_received:
            self.node.get_logger().warn("No odom received yet, skipping rotate_angle")
            return True

        self._set_start_pose()
        turned = self._angle_turned()

        if abs(turned - target_angle) < self.angle_tolerance:
            self.stop()
            return True

        error = normalize_angle(target_angle - turned)
        speed = min(self.angular_kp * error, self.max_angular_speed)
        speed = max(-self.max_angular_speed, speed)
        self._publish_vel(angular_z=speed)
        return False

    def rotate_angle_step(self, target_angle: float) -> bool:
        """Check if rotate_angle is complete. Call in a loop."""
        if not self._odom_received:
            return True

        turned = self._angle_turned()
        if abs(turned - target_angle) < self.angle_tolerance:
            self.stop()
            return True

        error = normalize_angle(target_angle - turned)
        speed = min(self.angular_kp * error, self.max_angular_speed)
        speed = max(-self.max_angular_speed, speed)
        self._publish_vel(angular_z=speed)
        return False
