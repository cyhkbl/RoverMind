from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("cmd_vel_topic", default_value="/cmd_vel"),
            DeclareLaunchArgument("speech_topic", default_value=""),
            DeclareLaunchArgument("sequence_file", default_value=""),
            DeclareLaunchArgument("publish_hz", default_value="20.0"),
            DeclareLaunchArgument("max_linear_speed", default_value="1.0"),
            DeclareLaunchArgument("max_angular_speed", default_value="1.0"),
            DeclareLaunchArgument("obstacle_distance", default_value="0.5"),
            Node(
                package="walk_talk_run_core",
                executable="sequence_runner",
                name="sequence_runner",
                output="screen",
                parameters=[
                    {
                        "cmd_vel_topic": LaunchConfiguration("cmd_vel_topic"),
                        "speech_topic": LaunchConfiguration("speech_topic"),
                        "sequence_file": LaunchConfiguration("sequence_file"),
                        "publish_hz": LaunchConfiguration("publish_hz"),
                        "max_linear_speed": LaunchConfiguration("max_linear_speed"),
                        "max_angular_speed": LaunchConfiguration("max_angular_speed"),
                    }
                ],
            ),
            Node(
                package="walk_talk_run_core",
                executable="obstacle_avoider",
                name="obstacle_avoider",
                output="screen",
                parameters=[
                    {
                        "obstacle_distance": LaunchConfiguration("obstacle_distance"),
                    }
                ],
            ),
        ]
    )
