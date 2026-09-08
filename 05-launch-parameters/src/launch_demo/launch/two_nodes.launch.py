"""第 05 课 · Launch ①：最基础的写法。

一次启动 talker 与 listener 两个节点。

运行:
    ros2 launch launch_demo two_nodes.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """每个 launch 文件都必须实现这个函数，返回 LaunchDescription。"""
    return LaunchDescription([
        Node(
            package='launch_demo',        # 功能包名
            executable='talker',          # 可执行文件名（setup.py 里注册的）
            name='talker',                # 运行时的节点名
            output='screen',              # 日志打印到终端
        ),
        Node(
            package='launch_demo',
            executable='listener',
            name='listener',
            output='screen',
        ),
    ])
