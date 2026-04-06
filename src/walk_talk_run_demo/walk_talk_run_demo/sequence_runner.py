#!/usr/bin/env python3

import signal
import sys
import time
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from walk_talk_run_demo.sequence_model import load_sequence, validate_sequence


GLOBAL_NODE = None


class SequenceRunnerNode(Node):
    def __init__(self):
        super().__init__("sequence_runner")

        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("speech_topic", "")
        self.declare_parameter("sequence_file", "")
        self.declare_parameter("publish_hz", 20.0)
        self.declare_parameter("max_linear_speed", 1.0)
        self.declare_parameter("max_angular_speed", 1.0)
        self.declare_parameter("stop_grace_period", 0.5)

        self.cmd_vel_topic = self.get_parameter("cmd_vel_topic").value
        self.speech_topic = self.get_parameter("speech_topic").value
        self.publish_hz = float(self.get_parameter("publish_hz").value)
        self.max_linear_speed = float(self.get_parameter("max_linear_speed").value)
        self.max_angular_speed = float(self.get_parameter("max_angular_speed").value)
        self.stop_grace_period = float(self.get_parameter("stop_grace_period").value)
        self.sequence_file = self._resolve_sequence_file(self.get_parameter("sequence_file").value)

        self.velocity = Twist()
        self.velocity_publisher = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.speech_publisher = None
        if self.speech_topic:
            self.speech_publisher = self.create_publisher(String, self.speech_topic, 10)

        timer_period = 1.0 / self.publish_hz
        self.timer = self.create_timer(timer_period, self._publish_velocity)
        self.sequence = self._load_sequence()

        self.get_logger().info(f"cmd_vel_topic={self.cmd_vel_topic}")
        self.get_logger().info(f"speech_topic={self.speech_topic or '<disabled>'}")
        self.get_logger().info(f"sequence_file={self.sequence_file}")

    def _resolve_sequence_file(self, configured_path):
        if configured_path:
            return configured_path

        share_dir = Path(get_package_share_directory("walk_talk_run_demo"))
        return str(share_dir / "config" / "default_sequence.json")

    def _load_sequence(self):
        raw_sequence = load_sequence(self.sequence_file)
        return validate_sequence(raw_sequence, self.max_linear_speed, self.max_angular_speed)

    def _publish_velocity(self):
        self.velocity_publisher.publish(self.velocity)

    def set_velocity(self, linear_x=0.0, linear_y=0.0, angular_z=0.0):
        self.velocity.linear.x = linear_x
        self.velocity.linear.y = linear_y
        self.velocity.angular.z = angular_z

    def stop(self):
        self.set_velocity()
        self.get_logger().info("Stop command published.")

    def _spin_for_duration(self, duration):
        start = self.get_clock().now()
        while (self.get_clock().now() - start).nanoseconds / 1e9 < duration:
            rclpy.spin_once(self, timeout_sec=0.05)
            time.sleep(0.001)

    def execute_sequence(self):
        for index, step in enumerate(self.sequence, start=1):
            step_type = step["type"]
            if step_type == "motion":
                self.get_logger().info(
                    f"Step {index}: motion "
                    f"linear_x={step['linear_x']:.2f}, "
                    f"linear_y={step['linear_y']:.2f}, "
                    f"angular_z={step['angular_z']:.2f}, "
                    f"duration={step['duration']:.2f}s"
                )
                self.set_velocity(step["linear_x"], step["linear_y"], step["angular_z"])
                self._spin_for_duration(step["duration"])
                self.stop()
                self._spin_for_duration(self.stop_grace_period)
                continue

            if step_type == "speech":
                text = step["text"]
                self.get_logger().info(f"Step {index}: speech {text}")
                if self.speech_publisher is not None:
                    message = String()
                    message.data = text
                    self.speech_publisher.publish(message)
                self._spin_for_duration(step["pause_after_sec"])
                continue

            if step_type == "pause":
                self.get_logger().info(f"Step {index}: pause {step['duration']:.2f}s")
                self.stop()
                self._spin_for_duration(step["duration"])
                continue

        self.stop()
        self.get_logger().info("Sequence finished.")


def signal_handler(sig, frame):
    del frame
    global GLOBAL_NODE
    if GLOBAL_NODE is not None:
        GLOBAL_NODE.stop()
        GLOBAL_NODE.get_logger().info(f"Received signal {sig}, shutting down.")
    if rclpy.ok():
        rclpy.shutdown()
    sys.exit(0)


def main():
    global GLOBAL_NODE
    rclpy.init()
    node = SequenceRunnerNode()
    GLOBAL_NODE = node

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        node.execute_sequence()
    except Exception as exc:
        node.get_logger().error(f"Execution failed: {exc}")
        raise
    finally:
        node.stop()
        time.sleep(0.2)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
