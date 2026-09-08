"""第 06 课：在 RViz 里查看机器人模型。

启动三个节点：
    - robot_state_publisher：把 URDF + 关节状态 -> 发布完整 TF 树和 /robot_description
    - joint_state_publisher_gui：带滑块的关节状态发布器（拖动滑块轮子会转）
    - rviz2：可视化

运行:
    ros2 launch robot_description display.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('robot_description')
    xacro_file = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    rviz_config = os.path.join(pkg_share, 'rviz', 'urdf.rviz')

    gui_arg = DeclareLaunchArgument(
        'gui', default_value='true',
        description='是否启动关节状态滑块 GUI')

    # 用 xacro 命令把 .xacro 处理成最终 URDF 字符串
    robot_description = Command(['xacro ', xacro_file])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui')),
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
    )

    return LaunchDescription([gui_arg, robot_state_publisher, joint_state_publisher_gui, rviz])
