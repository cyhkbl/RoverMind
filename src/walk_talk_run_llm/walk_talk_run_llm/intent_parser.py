#!/usr/bin/env python3
"""Intent parser node — listens to natural language commands, calls Claude API,
and publishes motion sequences as JSON."""

import json
import os

import rclpy
from anthropic import Anthropic
from rclpy.node import Node
from std_msgs.msg import String

SYSTEM_PROMPT = """You are a robot motion planner. Given a natural language command in Chinese or English,
output a JSON array of motion steps for a differential-drive robot.

Available step types:
1. {"type": "motion_distance", "distance": <meters>, "speed": <m/s 0.1-0.5>}
2. {"type": "motion_angle", "angle": <radians>, "speed": <rad/s 0.2-1.0>}
3. {"type": "speech", "text": "<text>", "pause_after_sec": <seconds>}
4. {"type": "pause", "duration": <seconds>}

Rules:
- Output ONLY valid JSON array, no markdown, no explanation.
- distance: positive = forward, negative = backward. Max 5m per step.
- angle: positive = counterclockwise (left), negative = clockwise (right).
- speed: always positive.
- Keep steps simple. Max 10 steps.
- If the command is ambiguous, make reasonable assumptions.
- Include a speech step after reaching each destination.

Example input: "go forward 2 meters then turn left 90 degrees"
Example output:
[{"type":"motion_distance","distance":2.0,"speed":0.3},{"type":"speech","text":"到达目标点","pause_after_sec":1.0},{"type":"motion_angle","angle":1.57,"speed":0.5}]
"""


class IntentParserNode(Node):
    def __init__(self):
        super().__init__("intent_parser")

        self.declare_parameter("input_topic", "/nl_command")
        self.declare_parameter("output_topic", "/parsed_sequence")
        self.declare_parameter("model", "claude-sonnet-4-20250514")
        self.declare_parameter("max_linear_speed", 0.5)
        self.declare_parameter("max_angular_speed", 1.0)

        input_topic = self.get_parameter("input_topic").value
        output_topic = self.get_parameter("output_topic").value
        self.model = self.get_parameter("model").value
        self.max_linear_speed = float(self.get_parameter("max_linear_speed").value)
        self.max_angular_speed = float(self.get_parameter("max_angular_speed").value)

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.get_logger().error(
                "ANTHROPIC_API_KEY not set! LLM intent parsing disabled."
            )
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

        self.input_sub = self.create_subscription(
            String, input_topic, self._command_callback, 10
        )
        self.output_pub = self.create_publisher(String, output_topic, 10)

        self.get_logger().info(
            f"IntentParser: listening on {input_topic}, publishing to {output_topic}, "
            f"model={self.model}"
        )

    def _command_callback(self, msg: String) -> None:
        command = msg.data.strip()
        if not command:
            return

        self.get_logger().info(f"Received command: {command}")

        if self.client is None:
            self.get_logger().error("Anthropic client not initialized")
            return

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": command}],
            )
            raw_text = response.content[0].text.strip()
            self.get_logger().debug(f"LLM raw response: {raw_text}")

            sequence = json.loads(raw_text)
            if not isinstance(sequence, list):
                raise ValueError("LLM did not return a JSON array")

            from walk_talk_run_core.sequence_model import validate_sequence

            validated = validate_sequence(
                sequence, self.max_linear_speed, self.max_angular_speed
            )

            output = String()
            output.data = json.dumps(validated, ensure_ascii=False)
            self.output_pub.publish(output)
            self.get_logger().info(
                f"Published parsed sequence with {len(validated)} steps"
            )

        except json.JSONDecodeError as e:
            self.get_logger().error(f"Failed to parse LLM response as JSON: {e}")
        except ValueError as e:
            self.get_logger().error(f"Sequence validation failed: {e}")
        except Exception as e:
            self.get_logger().error(f"LLM API call failed: {e}")


def main():
    rclpy.init()
    node = IntentParserNode()
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
