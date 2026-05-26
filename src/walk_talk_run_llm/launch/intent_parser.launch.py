from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("input_topic", default_value="/nl_command"),
            DeclareLaunchArgument("output_topic", default_value="/parsed_sequence"),
            DeclareLaunchArgument("model", default_value="claude-sonnet-4-20250514"),
            Node(
                package="walk_talk_run_llm",
                executable="intent_parser",
                name="intent_parser",
                output="screen",
                parameters=[
                    {
                        "input_topic": LaunchConfiguration("input_topic"),
                        "output_topic": LaunchConfiguration("output_topic"),
                        "model": LaunchConfiguration("model"),
                    }
                ],
            ),
        ]
    )
