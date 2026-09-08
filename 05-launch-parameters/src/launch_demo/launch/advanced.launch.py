"""第 05 课 · Launch ④：进阶 —— 命名空间 / 话题重映射 / include 组合。

运行:
    ros2 launch launch_demo advanced.launch.py

效果:
    - GroupAction + PushRosNamespace: 把一组节点放进 /demo 命名空间
    - remappings: talker 的 chatter 话题改名为 news（=> /demo/news）
    - IncludeLaunchDescription: 再 include two_nodes.launch.py，
      它的一对节点仍使用根命名空间的 /chatter

验证:
    ros2 topic list   # 应同时看到 /chatter 和 /demo/news
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    pkg_share = get_package_share_directory('launch_demo')

    # ---- 组合：把已有的 launch 文件整体包含进来 ----
    include_two_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'two_nodes.launch.py')
        ),
    )

    # ---- 分组：组内节点统一加命名空间 /demo ----
    demo_group = GroupAction([
        PushRosNamespace('demo'),
        Node(
            package='launch_demo',
            executable='talker',
            name='talker',
            output='screen',
            # 话题重映射：节点内部的 'chatter' -> 外部的 'news'
            # （再加上组命名空间，最终话题是 /demo/news）
            remappings=[('chatter', 'news')],
            parameters=[{'message': '来自 /demo 命名空间'}],
        ),
        Node(
            package='launch_demo',
            executable='listener',
            name='listener',
            output='screen',
            remappings=[('chatter', 'news')],
        ),
    ])

    return LaunchDescription([include_two_nodes, demo_group])
