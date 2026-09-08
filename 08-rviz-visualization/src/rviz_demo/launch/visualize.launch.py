"""第 08 课：一键启动 Marker / 点云演示 + RViz。

运行:
    ros2 launch rviz_demo visualize.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    rviz_config = os.path.join(
        get_package_share_directory('rviz_demo'), 'rviz', 'visualize.rviz')

    return LaunchDescription([
        Node(
            package='rviz_demo',
            executable='marker_demo',
            output='screen',
        ),
        Node(
            package='rviz_demo',
            executable='pointcloud_demo',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
        ),
    ])
