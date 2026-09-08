"""第 05 课 · Launch ③：用 YAML 文件集中管理参数。

运行:
    ros2 launch launch_demo with_yaml.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # get_package_share_directory: 定位本包安装后的 share 目录
    # （config/ 目录在 setup.py 里被安装到了那里）
    pkg_share = get_package_share_directory('launch_demo')
    params_file = os.path.join(pkg_share, 'config', 'talker_params.yaml')

    return LaunchDescription([
        Node(
            package='launch_demo',
            executable='talker',
            name='talker',
            output='screen',
            # parameters 可以直接给 YAML 文件路径
            parameters=[params_file],
        ),
        Node(
            package='launch_demo',
            executable='listener',
            name='listener',
            output='screen',
            parameters=[params_file],
        ),
    ])
