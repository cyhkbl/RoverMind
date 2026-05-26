import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_sim = get_package_share_directory("walk_talk_run_sim")

    world_file = os.path.join(pkg_sim, "world", "indoor.sdf")
    urdf_file = os.path.join(pkg_sim, "urdf", "diff_drive.urdf.xacro")
    sequence_file = LaunchConfiguration("sequence_file")
    obstacle_distance = LaunchConfiguration("obstacle_distance")

    return LaunchDescription(
        [
            DeclareLaunchArgument("world", default_value=world_file),
            DeclareLaunchArgument(
                "sequence_file",
                default_value=os.path.join(pkg_sim, "config", "default_sequence_sim.json"),
            ),
            DeclareLaunchArgument("obstacle_distance", default_value="0.5"),
            # Gazebo
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("ros_gz_sim"),
                        "launch",
                        "gz_sim.launch.py",
                    )
                ),
                launch_arguments={"gz_args": f"-r {world_file}"}.items(),
            ),
            # Robot State Publisher (URDF)
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": open(urdf_file).read()}],
            ),
            # Spawn robot in Gazebo
            ExecuteProcess(
                cmd=[
                    "ros2", "run", "ros_gz_sim", "create",
                    "-topic", "/robot_description",
                    "-name", "walk_talk_run_robot",
                    "-x", "0", "-y", "0", "-z", "0.1",
                ],
                output="screen",
            ),
            # ros_gz_bridge: /cmd_vel (Twist)
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="bridge_cmd_vel",
                arguments=["/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist"],
                output="screen",
            ),
            # ros_gz_bridge: /odom (Odometry)
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="bridge_odom",
                arguments=["/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry"],
                output="screen",
            ),
            # ros_gz_bridge: /scan (LaserScan)
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="bridge_scan",
                arguments=[
                    "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
                ],
                output="screen",
                parameters=[{"use_sim_time": True}],
            ),
            # Sequence Runner
            Node(
                package="walk_talk_run_core",
                executable="sequence_runner",
                name="sequence_runner",
                output="screen",
                parameters=[
                    {
                        "sequence_file": sequence_file,
                        "max_linear_speed": 0.5,
                        "max_angular_speed": 1.0,
                    }
                ],
            ),
            # Obstacle Avoider
            Node(
                package="walk_talk_run_core",
                executable="obstacle_avoider",
                name="obstacle_avoider",
                output="screen",
                parameters=[
                    {"obstacle_distance": obstacle_distance}
                ],
            ),
        ]
    )
